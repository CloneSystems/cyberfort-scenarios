#!/usr/bin/env python3
"""Record a CRA objective-compliance position for SEUXDR in CyberFort.

Usage:
    CF_USER=... CF_PASS=... python3 set_objectives.py baseline
    CF_USER=... CF_PASS=... python3 set_objectives.py after

The objectives table renders one row per objective with the compliance-status
control in the last cell. Row indices were read from the live table and are
stable for the CRA framework at asset scope; the script re-verifies each row's
objective title before writing, and aborts if the table has shifted.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://access.cyber-fort.eu"
EMAIL = os.environ["CF_USER"]
PW = os.environ["CF_PASS"]
OPEN = ".ant-select-dropdown:not(.ant-select-dropdown-hidden)"
OUT = Path("deckshots")
TXT = Path("pagetext")

# row index -> (expected objective title fragment, human label)
ROWS = {
    1:  ("Article 25", "Ch II Art 25 internal processes"),
    2:  ("Article 13", "Ch II Art 13 manufacturer obligations"),
    3:  ("Article 26", "Ch II Art 26 guidance"),
    4:  ("Article 14", "Ch II Art 14 reporting"),
    6:  ("Article 6",  "Ch I Art 6 + Annex I"),
    7:  ("Article 1",  "Ch I Art 1-2 scope"),
    9:  ("3b", "Annex I 3b access control"),
    10: ("3h", "Annex I 3h attack surface"),
    11: ("3i", "Annex I 3i incident impact"),
    12: ("3g", "Annex I 3g impact on others"),
    13: ("3f", "Annex I 3f availability"),
    14: ("3d", "Annex I 3d integrity"),
    15: ("3e", "Annex I 3e data minimisation"),
    16: ("3c", "Annex I 3c confidentiality"),
    17: ("3a", "Annex I 3a secure by default"),
    18: ("1",  "Annex I 1 appropriate cybersecurity"),
    19: ("2",  "Annex I 2 no known exploitable vulns"),
    20: ("3j", "Annex I 3j logging"),
    21: ("3k", "Annex I 3k security updates"),
    23: ("Article 70", "Ch V Art 70 evaluation"),
    24: ("Article 52", "Ch V Art 52/54 market surveillance"),
    26: ("8", "VH-8 update dissemination"),
    27: ("7", "VH-7 secure update distribution"),
    28: ("5", "VH-5 CVD policy"),
    29: ("6", "VH-6 contact address"),
    30: ("4", "VH-4 public disclosure"),
    31: ("3", "VH-3 regular testing"),
    32: ("2", "VH-2 remediate without delay"),
    33: ("1", "VH-1 SBOM and components"),
    35: ("Article 28", "Ch III Art 28 conformity/DoC"),
}

COMPLIANT, PARTIAL, NOT_COMP = "compliant", "partially compliant", "not compliant"

# The assessed baseline of 29-30 July 2026: 2 compliant, 10 partially, 18 not.
BASELINE = {r: NOT_COMP for r in ROWS}
BASELINE.update({13: COMPLIANT, 20: COMPLIANT})
for r in (17, 16, 14, 12, 10, 11, 21, 27, 6, 7):
    BASELINE[r] = PARTIAL

# After the remediation sprint of 30 July 2026: 21 compliant, 8 partially, 1 not.
AFTER = {r: COMPLIANT for r in
         (1, 2, 3, 4, 7, 9, 11, 13, 17, 18, 19, 20, 21, 23, 26, 28, 29, 30, 31, 32, 33)}
AFTER.update({r: PARTIAL for r in (6, 10, 12, 14, 15, 16, 24, 27)})
AFTER[35] = NOT_COMP

PLANS = {"baseline": BASELINE, "after": AFTER}


def login(page):
    page.goto(f"{BASE}/login", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)
    page.fill('input[placeholder*="mail" i]', EMAIL)
    page.fill('input[type=password]', PW)
    page.click('button[type=submit]')
    for _ in range(60):
        page.wait_for_timeout(500)
        if "/login" not in page.url:
            break
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)


def pick_scope(page, label, value):
    sel = page.locator(f"label:has-text('{label}')").locator("..").locator(".ant-select").first
    sel.click()
    page.wait_for_timeout(600)
    page.keyboard.type(value, delay=20)
    page.wait_for_timeout(900)
    page.locator(f"{OPEN} .ant-select-item-option").first.click(timeout=8000)
    page.wait_for_timeout(900)


def open_tree(page):
    page.goto(f"{BASE}/objectives_checklist", wait_until="networkidle")
    page.wait_for_timeout(2800)
    pick_scope(page, "Select Framework", "CRA")
    page.wait_for_timeout(2200)
    pick_scope(page, "Scope Type", "Asset")
    page.wait_for_timeout(1400)
    for lbl in ("Select Asset / Product", "Asset / Product", "Asset"):
        try:
            pick_scope(page, lbl, "SEUXDR")
            break
        except Exception:
            continue
    page.wait_for_timeout(4500)


def set_status(page, row, target):
    tds = page.locator("tbody tr").nth(row).locator("td")
    sel = tds.nth(6).locator(".ant-select").first
    sel.scroll_into_view_if_needed()
    sel.click()
    page.wait_for_timeout(800)
    opts = page.locator(f"{OPEN} .ant-select-item-option")
    n = opts.count()
    for i in range(n):
        if " ".join(opts.nth(i).inner_text().split()).lower() == target:
            opts.nth(i).click()
            page.wait_for_timeout(1200)
            return True
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    return False


def read_status(page, row):
    tds = page.locator("tbody tr").nth(row).locator("td")
    return " ".join(tds.nth(6).inner_text().split()).lower()


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "after"
    plan = PLANS[which]
    print(f"=== pass: {which}  ({sum(1 for v in plan.values() if v == COMPLIANT)} compliant, "
          f"{sum(1 for v in plan.values() if v == PARTIAL)} partially, "
          f"{sum(1 for v in plan.values() if v == NOT_COMP)} not compliant)")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(viewport={"width": 1700, "height": 1050},
                            ignore_https_errors=True, device_scale_factor=2)
        ctx.set_default_timeout(45000)
        page = ctx.new_page()
        login(page)
        open_tree(page)

        # sanity-check the row map before writing anything
        for row, (frag, label) in ROWS.items():
            title = " ".join(page.locator("tbody tr").nth(row).locator("td")
                             .nth(1).inner_text().split())
            if frag not in title:
                print(f"ABORT: row {row} expected {frag!r}, found {title[:50]!r}")
                b.close()
                return 1

        written, failed = 0, []
        for row in sorted(plan):
            target = plan[row]
            if read_status(page, row) == target:
                written += 1
                continue
            if set_status(page, row, target):
                written += 1
                print(f"  row {row:>2} {ROWS[row][1]:<40} -> {target}")
            else:
                failed.append(row)
                print(f"  row {row:>2} {ROWS[row][1]:<40} -> FAILED")
            time.sleep(0.2)

        page.reload(wait_until="networkidle")
        page.wait_for_timeout(2500)
        open_tree(page)
        final = {}
        for row in sorted(ROWS):
            final[row] = read_status(page, row)
        tally = {}
        for v in final.values():
            tally[v] = tally.get(v, 0) + 1
        print(f"\nverified tally: {tally}")
        comp = tally.get(COMPLIANT, 0)
        print(f"compliant {comp} of {len(ROWS)} = {100 * comp / len(ROWS):.1f}%")
        Path(f"objectives_{which}.json").write_text(
            json.dumps({"pass": which, "final": final, "tally": tally,
                        "failed_rows": failed}, indent=1), encoding="utf-8")
        page.screenshot(path=str(OUT / f"objectives_{which}.png"), full_page=True)
        (TXT / f"objectives_{which}.txt").write_text(
            (page.query_selector("main") or page.query_selector("body")).inner_text(),
            encoding="utf-8")
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
