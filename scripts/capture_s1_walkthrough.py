"""Walk through Scenario 01 — PortPilot Maritime — in the live CyberFort
platform and screenshot every step.

Usage:
    CF_USER=...  CF_PASS=...  python3 capture_s1_walkthrough.py
"""

import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUT = "/home/mike/cyberfort/cyber-range-scenarios/01-portpilot-maritime/docs/screenshots"
HOST = "https://access.cyber-fort.eu"
USER = os.environ["CF_USER"]
PASSWORD = os.environ["CF_PASS"]


# ---------- helpers ----------
def shot(page, name, full=False):
    path = f"{OUT}/{name}.png"
    page.screenshot(path=path, full_page=full)
    print(f"  📸 {name}.png")


def safe_click(page, selector, label="", timeout=5000):
    try:
        page.click(selector, timeout=timeout)
        return True
    except PWTimeout:
        print(f"  ⚠ click {label or selector!r} timed out")
        return False
    except Exception as e:
        print(f"  ⚠ click {label or selector!r} error: {e}")
        return False


def safe_fill(page, selector, value, label="", timeout=5000):
    try:
        page.fill(selector, value, timeout=timeout)
        return True
    except Exception as e:
        print(f"  ⚠ fill {label or selector!r}: {e}")
        return False


def pick_antd_option(page, label_text, option_text):
    """Pick an option from an Ant Design Select identified by its label."""
    # Click the select (the visible chooser sits after the label)
    select = page.locator(f"label:has-text('{label_text}')").locator("..") \
                  .locator(".ant-select").first
    select.scroll_into_view_if_needed()
    select.click()
    page.wait_for_timeout(400)
    # Type to filter then pick
    try:
        page.keyboard.type(option_text, delay=20)
        page.wait_for_timeout(400)
    except Exception:
        pass
    # Click the option
    opt = page.locator(f".ant-select-item-option:has-text('{option_text}')").first
    try:
        opt.click(timeout=3000)
    except Exception:
        # Fallback: press Enter
        page.keyboard.press("Enter")
    page.wait_for_timeout(300)


# ---------- flows ----------
def login(page):
    print("[login]")
    page.goto(f"{HOST}/login", wait_until="domcontentloaded")
    page.wait_for_timeout(800)
    shot(page, "step0-01-login-page")
    page.fill('input[placeholder*="mail" i]', USER)
    page.fill('input[type="password"]', PASSWORD)
    page.wait_for_timeout(400)
    shot(page, "step0-02-login-filled")
    page.click('button[type="submit"]')
    for _ in range(60):
        page.wait_for_timeout(500)
        if "/login" not in page.url:
            break
    page.wait_for_load_state("networkidle", timeout=20000)
    page.wait_for_timeout(800)
    shot(page, "step0-03-dashboard")


def step1_register_asset(page):
    print("\n[step 1] register PortPilot as a product")
    page.goto(f"{HOST}/assets", wait_until="networkidle")
    page.wait_for_timeout(1200)
    shot(page, "step1-01-assets-list")

    # Open the modal
    safe_click(page, 'button:has-text("Add Asset")', "Add Asset")
    page.wait_for_timeout(1200)
    shot(page, "step1-02-add-asset-modal-blank", full=True)

    # Fill fields
    safe_fill(page, 'input[placeholder="Enter asset name"]', "PortPilot")
    safe_fill(page, 'input[placeholder="Enter version"]', "0.9.2")

    # Asset Type — pick something plausible
    try:
        pick_antd_option(page, "Asset Type", "SAAS Product")
    except Exception:
        try:
            pick_antd_option(page, "Asset Type", "Application")
        except Exception:
            print("  ⚠ could not pick asset type")

    # Status
    try:
        pick_antd_option(page, "Status", "Active")
    except Exception:
        pass

    # Economic Operator
    try:
        pick_antd_option(page, "Economic Operator", "Manufacturer")
    except Exception:
        pass

    # Criticality — pick the first option
    try:
        select = page.locator("label:has-text('Criticality')").locator("..").locator(".ant-select").first
        select.click()
        page.wait_for_timeout(400)
        page.locator(".ant-select-item-option").first.click()
        page.wait_for_timeout(300)
    except Exception:
        pass

    # IP / URL
    safe_fill(
        page,
        'input[placeholder*="192.168" i]',
        "10.10.20.30",
    )

    # Description
    descs = page.locator('textarea')
    try:
        descs.nth(1).fill(
            "In-house Flask vessel and cargo-manifest manager for Larnaca port operations. "
            "Trains operators on the PortPilot cyber-range scenario."
        )
    except Exception:
        pass

    page.wait_for_timeout(500)
    shot(page, "step1-03-add-asset-modal-filled", full=True)

    # Save
    saved = safe_click(page, 'button:has-text("Save")', "Save asset")
    if not saved:
        saved = safe_click(page, 'button:has-text("Create")', "Create asset")
    if not saved:
        saved = safe_click(page, 'button:has-text("Submit")', "Submit asset")
    page.wait_for_timeout(2500)
    # Close any leftover modals
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)
    page.goto(f"{HOST}/assets", wait_until="networkidle")
    page.wait_for_timeout(1200)
    shot(page, "step1-04-assets-list-with-portpilot")


def step2_security_tools_overview(page):
    print("\n[step 2-5] Security Tools — capture each scanner page")
    # Expand sidebar Security Tools
    safe_click(page, 'text=Security Tools', "Security Tools sidebar")
    page.wait_for_timeout(600)
    # Security Scanners (Nmap)
    safe_click(page, 'text=Security Scanners', "Security Scanners")
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(1500)
    shot(page, "step2-01-security-scanners", full=True)
    # Code Analysis (Semgrep)
    safe_click(page, 'text=Code Analysis', "Code Analysis")
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(1500)
    shot(page, "step4-01-code-analysis", full=True)
    # Dependency Check (OSV)
    safe_click(page, 'text=Dependency Check', "Dependency Check")
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(1500)
    shot(page, "step5-01-dependency-check", full=True)
    # Scan Findings overview
    safe_click(page, 'text=Scan Findings', "Scan Findings")
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(1500)
    shot(page, "step5-02-scan-findings", full=True)


def step_register_a_risk(page, title, likelihood, impact, description, screenshot_name):
    """Open the Add Risk form, fill it, save it, return."""
    page.goto(f"{HOST}/risk_registration", wait_until="networkidle")
    page.wait_for_timeout(1200)
    # Click the dashboard "Add New Risk" button (top-right or in the
    # Quick Actions card)
    clicked = False
    for sel in [
        'button:has-text("Add New Risk")',
        'a:has-text("Add New Risk")',
        'text="Add New Risk"',
    ]:
        try:
            loc = page.locator(sel).first
            loc.scroll_into_view_if_needed()
            loc.click(timeout=3000)
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        print(f"  ⚠ could not open Add Risk for {title}")
        return
    page.wait_for_timeout(1500)
    shot(page, f"{screenshot_name}-form-blank", full=True)

    # Try a generic fill: first text input → title; first textarea → description
    try:
        page.locator("input[type='text']").first.fill(title)
    except Exception:
        pass
    try:
        page.locator("textarea").first.fill(description)
    except Exception:
        pass
    page.wait_for_timeout(400)
    shot(page, f"{screenshot_name}-form-filled", full=True)
    # Save
    for sel in ['button:has-text("Save")', 'button:has-text("Create")',
                'button:has-text("Submit")', 'button:has-text("Add")']:
        try:
            page.click(sel, timeout=2500)
            break
        except Exception:
            continue
    page.wait_for_timeout(1500)
    page.keyboard.press("Escape")


def step6_assessment(page):
    print("\n[step 6] open CRA assessment")
    page.goto(f"{HOST}/assessments", wait_until="networkidle")
    page.wait_for_timeout(1500)
    shot(page, "step6-01-assessments-overview", full=True)

    # New Assessment
    safe_click(page, 'button:has-text("+ New Assessment")', "+ New Assessment")
    page.wait_for_timeout(1500)
    shot(page, "step6-02-new-assessment-form", full=True)

    # Pick Framework = CRA (often default), Assessment Type = Conformity,
    # Scope = some default, then Create
    try:
        pick_antd_option(page, "Framework", "CRA")
    except Exception:
        pass
    try:
        pick_antd_option(page, "Assessment Type", "Conformity")
    except Exception:
        pass
    try:
        pick_antd_option(page, "Scope Type", "Asset")
    except Exception:
        try:
            pick_antd_option(page, "Scope Type", "Product")
        except Exception:
            pass

    # Assessment Name
    try:
        page.locator('input[placeholder*="name" i]').last.fill("PortPilot CRA Conformity")
    except Exception:
        try:
            page.locator('input[type="text"]').last.fill("PortPilot CRA Conformity")
        except Exception:
            pass
    page.wait_for_timeout(400)
    shot(page, "step6-03-new-assessment-filled", full=True)

    safe_click(page, 'button:has-text("Create")', "Create assessment")
    page.wait_for_timeout(2500)
    shot(page, "step6-04-assessment-created", full=True)

    # If we're on the questions page, scroll and screenshot
    page.wait_for_timeout(1500)
    shot(page, "step6-05-questions-top", full=True)
    try:
        page.evaluate("window.scrollBy(0, 600)")
    except Exception:
        pass
    page.wait_for_timeout(500)
    shot(page, "step6-06-questions-scrolled", full=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  ignore_https_errors=True)
        page = ctx.new_page()

        login(page)
        step1_register_asset(page)
        step2_security_tools_overview(page)

        # Six risk entries replicating the scanner findings.
        risks = [
            ("PostgreSQL exposed on public network interface",
             "PG bound to 0.0.0.0:5432 in docker-compose; weak password 'PortPilot2024!'. "
             "Discovered via Nmap; CRA Annex I 3a, 3h.",
             "step2-02-risk-pg-exposed"),
            ("SQL injection auth bypass on /login",
             "Username field concatenated into SQL. Payload \"admin' OR '1'='1' --\" "
             "yields admin session. Discovered via ZAP; CRA Annex I 3b, 2.",
             "step3-01-risk-sqli"),
            ("Reflected XSS on /vessels search",
             "vessels() route uses Markup() over user input; <script>alert(1)</script> "
             "executes. CRA Annex I 3d, 2.",
             "step3-02-risk-xss"),
            ("Broken access control on /admin/manifests",
             "/admin/manifests has no auth check; returns CLASSIFIED cargo manifests. "
             "CRA Annex I 3b, 3c.",
             "step3-03-risk-broken-access"),
            ("Hardcoded credentials in source",
             "config.py contains DB password and billing API key in plaintext. "
             "Found by Semgrep. CRA Annex I 3d.",
             "step4-02-risk-hardcoded-secret"),
            ("Multiple outdated dependencies",
             "Flask 2.0.1, Werkzeug 2.0.1, Jinja2 3.0.0, requests 2.25.0 have "
             "known CVEs (OSV). CRA Annex I 2, 3k; Vuln-Handling 1.",
             "step5-03-risk-osv-deps"),
        ]
        for title, desc, fname in risks:
            print(f"\n[risk] {title}")
            step_register_a_risk(page, title, "High", "High", desc, fname)

        # After all risks, screenshot the risk list
        page.goto(f"{HOST}/risk_registration", wait_until="networkidle")
        page.wait_for_timeout(1200)
        # Click View Risk List
        try:
            page.click('text=View Risk List', timeout=4000)
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_timeout(1500)
        except Exception:
            pass
        shot(page, "step5-04-risk-register-with-findings", full=True)

        step6_assessment(page)

        # Logout/end
        browser.close()
        print("\n✅ walkthrough complete")


if __name__ == "__main__":
    main()
