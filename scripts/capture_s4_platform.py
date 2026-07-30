"""Walk the CyberFort platform for scenario 04 and screenshot every runbook step.

Usage:
    CF_USER=... CF_PASS=... python3 scripts/capture_s4_platform.py

Writes to 04-clonesystems-seuxdr-siem/docs/screenshots/. Note that the CRA Technical
File pages and the EU Declaration of Conformity resolve only through in-app sidebar
navigation - entering their URLs directly redirects to /home - so those are captured
by clicking the sidebar (see capture_s4_technical_file.py behaviour inline below).
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE = "https://access.cyber-fort.eu"
EMAIL = os.environ["CF_USER"]
PW = os.environ["CF_PASS"]
REPO = Path(__file__).resolve().parent.parent
SHOTS = REPO / "04-clonesystems-seuxdr-siem" / "docs" / "screenshots"
TXT = Path("pagetext/tf")
SHOTS.mkdir(parents=True, exist_ok=True)
TXT.mkdir(parents=True, exist_ok=True)

def shot(page, name, full=True):
    page.screenshot(path=str(SHOTS/f"{name}.png"), full_page=full); print(f"  shot {name}")

def save(page, name):
    m=page.query_selector("main") or page.query_selector("body")
    t=m.inner_text(); (TXT/f"{name}.txt").write_text(t, encoding="utf-8")
    print(f"  txt {name} ({len(t)})"); return t

def go(page, route, name=None, settle=2800, full=True, txt=None):
    page.goto(f"{BASE}{route}", wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(settle)
    if txt: save(page, txt)
    if name: shot(page, name, full=full)
    print(f"  [{route}] -> {page.url}")

def pick(page, label, value):
    sel=page.locator(f"label:has-text('{label}')").locator("..").locator(".ant-select").first
    sel.scroll_into_view_if_needed(); sel.click(); page.wait_for_timeout(400)
    page.keyboard.type(value, delay=15); page.wait_for_timeout(700)
    try: page.locator(f".ant-select-item-option:has-text('{value}')").first.click(timeout=3000)
    except Exception: page.keyboard.press("Enter")
    page.wait_for_timeout(400)

with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":900}, ignore_https_errors=True)
    page=ctx.new_page()
    # step 0
    page.goto(f"{BASE}/login", wait_until="domcontentloaded"); page.wait_for_timeout(1200)
    shot(page, "step0-01-login-page", full=False)
    page.fill('input[placeholder*="mail" i]', EMAIL); page.fill('input[type=password]', PW)
    page.wait_for_timeout(400); shot(page, "step0-02-login-filled", full=False)
    page.click('button[type=submit]')
    for _ in range(60):
        page.wait_for_timeout(500)
        if "/login" not in page.url: break
    page.wait_for_load_state("networkidle", timeout=20000); page.wait_for_timeout(1800)
    shot(page, "step0-03-dashboard", full=False)

    # step 1 — asset / classification
    go(page, "/assets", "step1-01-assets-list", full=False)
    try:
        page.click('button:has-text("Add Asset")', timeout=6000); page.wait_for_timeout(1600)
        shot(page, "step1-02-add-asset-modal-blank")
        try: page.fill('input[placeholder="Enter asset name"]', "SEUXDR")
        except Exception: pass
        try: page.fill('input[placeholder="Enter version"]', "3.4")
        except Exception: pass
        for lbl, val in [("Asset Type","Software Product"),("Status","Active"),
                         ("Economic Operator","Manufacturer")]:
            try: pick(page, lbl, val)
            except Exception as e: print("   pick fail", lbl, str(e)[:70])
        try: pick(page, "Criticality", "Security information and event management")
        except Exception as e: print("   criticality fail", str(e)[:70])
        page.wait_for_timeout(600); shot(page, "step1-03-add-asset-modal-filled")
        page.keyboard.press("Escape"); page.wait_for_timeout(800)
        page.keyboard.press("Escape"); page.wait_for_timeout(500)
    except Exception as e:
        print("  add-asset modal failed:", str(e)[:150])
    # step 2 — frameworks
    for r in ["/frameworks","/manage_frameworks","/frameworks_configuration"]:
        page.goto(f"{BASE}{r}", wait_until="networkidle", timeout=45000); page.wait_for_timeout(2200)
        print(f"  probe {r} -> {page.url}")
        if "notfound" not in page.url and page.url.rstrip('/').endswith(r.strip('/')):
            shot(page, "step2-01-manage-frameworks"); break

    # step 3-5 security tools
    go(page, "/sbom_generator",  "step3-01-sbom-generator",  txt="sbom_generator")
    go(page, "/dependency_check","step4-01-dependency-check", txt="dependency_check")
    go(page, "/code_analysis",   "step4-02-code-analysis",    txt="code_analysis")
    go(page, "/security_scanners","step4-03-security-scanners", txt="security_scanners")
    go(page, "/scan_findings",   "step5-01-scan-findings",    txt="scan_findings")
    go(page, "/vex",             "step5-02-vex-statements",   txt="vex")

    # step 6 — CRA technical file
    tf = [("/sbom_management","step6-01-tf-sbom-management","tf_sbom"),
          ("/secure_sdlc_evidence","step6-02-tf-secure-sdlc","tf_sdlc"),
          ("/security_design_documentation","step6-03-tf-security-design","tf_design"),
          ("/patch_support_policy","step6-04-tf-patch-support","tf_patch"),
          ("/vulnerability_disclosure_policy","step6-05-tf-vuln-disclosure","tf_vd"),
          ("/dependency_policy","step6-06-tf-dependency-policy","tf_dep"),
          ("/evidence","step6-07-evidence-library","tf_evidence")]
    for r, s, t in tf: go(page, r, s, txt=t)

    # step 7 assessments
    go(page, "/assessments", "step7-01-assessments-overview", full=False)
    try:
        page.get_by_text("Wazuh SIEM CRA Conformity Assessment", exact=False).first.click(timeout=10000)
        page.wait_for_timeout(5000); shot(page, "step7-02-conformity-questions")
    except Exception as e: print("  q open failed", str(e)[:120])

    # step 8 objectives
    page.goto(f"{BASE}/objectives_checklist", wait_until="networkidle"); page.wait_for_timeout(2500)
    try:
        pick(page, "Select Framework", "CRA"); page.wait_for_timeout(2500)
        pick(page, "Scope Type", "Asset"); page.wait_for_timeout(1500)
        for lbl in ["Select Asset / Product","Asset / Product","Asset"]:
            try: pick(page, lbl, "SEUXDR"); break
            except Exception: pass
        page.wait_for_timeout(3500)
    except Exception as e: print("  objectives pick failed", str(e)[:120])
    shot(page, "step8-01-objectives-cra-seuxdr")

    # step 9 gap + chain
    page.goto(f"{BASE}/gap_analysis", wait_until="networkidle"); page.wait_for_timeout(2500)
    try:
        page.locator(".ant-select").first.click(); page.wait_for_timeout(500)
        page.keyboard.type("CRA", delay=20); page.wait_for_timeout(700)
        page.locator(".ant-select-item-option:has-text('CRA')").first.click(timeout=3000)
        page.wait_for_timeout(4000)
    except Exception: pass
    shot(page, "step9-01-gap-analysis-cra")
    go(page, "/compliance_chain_map", "step9-02-compliance-chain-map")
    go(page, "/compliance_chain_links", "step9-03-compliance-chain-links")

    # step 10 DoC + CE
    go(page, "/eu_declaration_of_conformity", "step10-01-eu-declaration-of-conformity", txt="doc")
    page.goto(f"{BASE}/home", wait_until="networkidle"); page.wait_for_timeout(1200)
    try:
        page.get_by_text("Assets / Products", exact=True).first.click(timeout=6000); page.wait_for_timeout(800)
        page.get_by_text("CE Marking Checklist", exact=True).first.click(timeout=6000)
        page.wait_for_load_state("networkidle"); page.wait_for_timeout(3000)
        save(page, "ce_marking"); shot(page, "step10-02-ce-marking-checklist")
    except Exception as e: print("  CE failed", str(e)[:120])

    # step 11 risks
    go(page, "/risk_registration", "step11-01-risk-register", txt="risks")
    b.close()
    print("done")
