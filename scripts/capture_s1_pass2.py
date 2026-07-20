"""Second pass — fix the screenshots that the first pass got wrong:
   * Security Tools sub-pages (direct URLs)
   * Risk Add form filled with all required fields
   * Risk register list with PortPilot risks visible
   * CRA assessment created against PortPilot, question page opened
"""

import os
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUT = "/home/mike/cyberfort/cyber-range-scenarios/01-portpilot-maritime/docs/screenshots"
HOST = "https://access.cyber-fort.eu"
USER = os.environ["CF_USER"]
PASSWORD = os.environ["CF_PASS"]


def shot(page, name, full=False):
    path = f"{OUT}/{name}.png"
    page.screenshot(path=path, full_page=full)
    print(f"  📸 {name}.png")


def login(page):
    page.goto(f"{HOST}/login", wait_until="domcontentloaded")
    page.wait_for_timeout(800)
    page.fill('input[placeholder*="mail" i]', USER)
    page.fill('input[type="password"]', PASSWORD)
    page.click('button[type="submit"]')
    for _ in range(60):
        page.wait_for_timeout(500)
        if "/login" not in page.url:
            break
    page.wait_for_load_state("networkidle", timeout=20000)


def pick_select_after_label(page, label_text, option_text):
    """Pick an Ant Design Select that sits right after a label with the given text."""
    select = page.locator(f"label:has-text('{label_text}')").locator("..").locator(".ant-select").first
    select.scroll_into_view_if_needed()
    select.click()
    page.wait_for_timeout(300)
    page.keyboard.type(option_text, delay=15)
    page.wait_for_timeout(400)
    opt = page.locator(f".ant-select-item-option:has-text('{option_text}')").first
    try:
        opt.click(timeout=2500)
    except Exception:
        page.keyboard.press("Enter")
    page.wait_for_timeout(300)


def pick_first_option(page, label_text):
    select = page.locator(f"label:has-text('{label_text}')").locator("..").locator(".ant-select").first
    select.scroll_into_view_if_needed()
    select.click()
    page.wait_for_timeout(400)
    page.locator(".ant-select-item-option").first.click()
    page.wait_for_timeout(300)


def fill_input_after_label(page, label_text, value):
    inp = page.locator(f"label:has-text('{label_text}')").locator("..").locator("input, textarea").first
    inp.scroll_into_view_if_needed()
    inp.fill(value)
    page.wait_for_timeout(200)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  ignore_https_errors=True)
        page = ctx.new_page()

        login(page)

        # --- Step 2: Security Scanners (Nmap + ZAP) ---
        print("\n[step 2] Security Scanners")
        page.goto(f"{HOST}/security_scanners", wait_until="networkidle")
        page.wait_for_timeout(1500)
        shot(page, "step2-01-security-scanners", full=True)

        # --- Step 4: Code Analysis (Semgrep) ---
        print("\n[step 4] Code Analysis")
        page.goto(f"{HOST}/code_analysis", wait_until="networkidle")
        page.wait_for_timeout(1500)
        shot(page, "step4-01-code-analysis", full=True)

        # --- Step 5: Dependency Check (OSV) ---
        print("\n[step 5] Dependency Check")
        page.goto(f"{HOST}/dependency_check", wait_until="networkidle")
        page.wait_for_timeout(1500)
        shot(page, "step5-01-dependency-check", full=True)

        # --- Step 5b: Scan Findings (aggregated) ---
        print("\n[step 5b] Scan Findings")
        page.goto(f"{HOST}/scan_findings", wait_until="networkidle")
        page.wait_for_timeout(1500)
        shot(page, "step5-02-scan-findings", full=True)

        # --- Add ONE fully-filled Risk for the PG-exposed finding ---
        print("\n[step 2.5] Risk Register: Add the exposed-PG risk fully filled")
        page.goto(f"{HOST}/risk_registration", wait_until="networkidle")
        page.wait_for_timeout(1500)

        # Click the "Add New Risk" via the Quick Action — but the previous
        # run failed because there are two of these. Try the visible one
        # under Quick Actions.
        try:
            # The Quick Action button
            page.locator('button:has-text("Add New Risk"), a:has-text("Add New Risk")').first.click(timeout=4000)
        except Exception:
            # Try via direct text and force
            page.locator('text="Add New Risk"').first.click(force=True, timeout=4000)
        page.wait_for_timeout(1500)
        shot(page, "step2-02-risk-form-blank", full=True)

        # Fill mandatory fields
        try:
            page.locator('input[placeholder*="ORG-RSK" i]').fill("PORTPILOT-RSK-01")
        except Exception:
            page.locator('input[type="text"]').first.fill("PORTPILOT-RSK-01")

        try:
            pick_select_after_label(page, "Asset Category", "SAAS")
        except Exception:
            try:
                pick_first_option(page, "Asset Category")
            except Exception:
                pass

        try:
            pick_select_after_label(page, "Status (Treatment)", "Reduce")
        except Exception:
            try:
                pick_first_option(page, "Status (Treatment)")
            except Exception:
                pass

        try:
            pick_select_after_label(page, "Likelihood", "High")
        except Exception:
            try:
                pick_first_option(page, "Likelihood")
            except Exception:
                pass

        try:
            pick_select_after_label(page, "Severity", "High")
        except Exception:
            try:
                pick_first_option(page, "Severity")
            except Exception:
                pass

        try:
            pick_select_after_label(page, "Residual Risk", "Medium")
        except Exception:
            try:
                pick_first_option(page, "Residual Risk")
            except Exception:
                pass

        # Risk Category — it's a text input that doubles as a combobox
        try:
            cat = page.locator("input[placeholder*='risk category' i]").first
            cat.scroll_into_view_if_needed()
            cat.fill("Network / Infrastructure")
        except Exception:
            pass

        try:
            fill_input_after_label(
                page, "Description",
                "PortPilot ships docker-compose with PostgreSQL bound to 0.0.0.0:5432 "
                "and the default weak password 'PortPilot2024!'. Discovered via Nmap. "
                "CRA Annex I objectives 3a (secure by default), 3h (limit attack surfaces)."
            )
        except Exception:
            pass

        try:
            fill_input_after_label(
                page, "Potential Impact",
                "Customer-database compromise; full read/write to cargo manifests; "
                "GDPR Article 32 violation."
            )
        except Exception:
            pass

        try:
            fill_input_after_label(
                page, "Controls",
                "Remove ports:5432 mapping; rotate to strong password loaded from env; "
                "introduce network segmentation."
            )
        except Exception:
            pass

        page.wait_for_timeout(500)
        shot(page, "step2-02-risk-form-filled", full=True)

        # Save
        try:
            page.click('button:has-text("Save Risk")', timeout=4000)
            page.wait_for_timeout(2500)
        except Exception:
            try:
                page.click('button:has-text("Save")', timeout=2000)
                page.wait_for_timeout(2500)
            except Exception:
                pass

        # Close any toast / modal residue
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)

        # Risk Register list (Risk Registry tab)
        page.goto(f"{HOST}/risk_registration", wait_until="networkidle")
        page.wait_for_timeout(1500)
        try:
            page.click("text=Risk Registry", timeout=4000)
            page.wait_for_load_state("networkidle", timeout=10000)
            page.wait_for_timeout(1500)
        except Exception:
            pass
        shot(page, "step5-04-risk-register-with-findings", full=True)

        # --- Step 6: Create CRA assessment with PortPilot scope ---
        print("\n[step 6] CRA assessment for PortPilot")
        page.goto(f"{HOST}/assessments", wait_until="networkidle")
        page.wait_for_timeout(1500)
        shot(page, "step6-01-assessments-overview", full=True)

        try:
            page.click('button:has-text("+ New Assessment")', timeout=4000)
        except Exception:
            try:
                page.click('text="+ New Assessment"', timeout=4000)
            except Exception:
                pass
        page.wait_for_timeout(1500)

        try:
            pick_select_after_label(page, "Framework", "CRA")
        except Exception:
            pass
        try:
            pick_select_after_label(page, "Assessment Type", "Conformity")
        except Exception:
            pass
        try:
            pick_select_after_label(page, "Scope Type", "Asset")
        except Exception:
            pass
        try:
            pick_select_after_label(page, "Asset", "PortPilot")
        except Exception:
            try:
                # The label might say "Asset / Product"
                pick_select_after_label(page, "Asset / Product", "PortPilot")
            except Exception:
                pass

        try:
            fill_input_after_label(page, "Assessment Name", "PortPilot CRA Conformity")
        except Exception:
            page.locator('input[type="text"]').last.fill("PortPilot CRA Conformity")

        page.wait_for_timeout(600)
        shot(page, "step6-03-new-assessment-filled", full=True)

        try:
            page.click('button:has-text("Create")', timeout=4000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        shot(page, "step6-04-assessment-created", full=True)

        # If we got navigated to the assessment, capture the questions
        page.wait_for_timeout(1500)
        shot(page, "step6-05-questions-top", full=True)
        try:
            page.evaluate("window.scrollBy(0, 700)")
        except Exception:
            pass
        page.wait_for_timeout(500)
        shot(page, "step6-06-questions-scrolled", full=True)

        # --- Try answering one question (radio Not compliant) ---
        try:
            # Click the first "No" / "Not compliant" radio
            radio = page.locator('label:has-text("Not Compliant"), label:has-text("No"), input[value="not_compliant"]').first
            radio.scroll_into_view_if_needed()
            radio.click(timeout=3000)
            page.wait_for_timeout(500)
            shot(page, "step6-07-question-answered", full=True)
        except Exception as e:
            print("could not click answer radio:", e)

        browser.close()
        print("\n✅ second pass complete")


if __name__ == "__main__":
    main()
