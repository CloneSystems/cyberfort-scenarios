"""Capture SmartGrid Meter Admin app screenshots for Scenario 02."""

import os
from playwright.sync_api import sync_playwright

OUT = "/home/mike/cyberfort/cyber-range-scenarios/02-smartgrid-meter-energy/docs/screenshots/app"
HOST = "http://localhost:8080"


def shot(page, name, full=False):
    page.screenshot(path=f"{OUT}/{name}.png", full_page=full)
    print(f"  📸 {name}.png")


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1100, "height": 700}, ignore_https_errors=True)
        page = ctx.new_page()

        # 1. Login page
        print("[1] login page")
        page.goto(f"{HOST}/login", wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        shot(page, "smartgrid-01-login-page")

        # 2. Default creds entered
        print("[2] default creds entered")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin")
        page.wait_for_timeout(300)
        shot(page, "smartgrid-02-default-creds")

        # 3. Dashboard with telemetry (might need to wait for MQTT samples)
        print("[3] dashboard")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_timeout(7000)  # wait for telemetry from 3 meters
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(2000)
        shot(page, "smartgrid-03-dashboard-telemetry")

        # 4. Click "Read Modbus #1" link to view registers
        print("[4] modbus registers via web UI")
        try:
            page.click('a:has-text("Read Modbus #1")', timeout=4000)
            page.wait_for_load_state("networkidle", timeout=10000)
            page.wait_for_timeout(1000)
        except Exception as e:
            print("  retry via direct URL")
            page.goto(f"{HOST}/meter/1/registers", wait_until="networkidle")
            page.wait_for_timeout(1000)
        shot(page, "smartgrid-04-modbus-registers")

        # 5. Firmware upload — upload a python file (arbitrary type)
        print("[5] firmware upload arbitrary file")
        page.goto(f"{HOST}/firmware", wait_until="networkidle")
        page.wait_for_timeout(500)
        # write a payload file
        with open("/tmp/rogue.py", "w") as f:
            f.write('print("rce — this is a Python script saved by the firmware endpoint")\n')
        page.set_input_files('input[type="file"]', "/tmp/rogue.py")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_timeout(800)
        shot(page, "smartgrid-05-firmware-upload-rce")

        b.close()
        print("\n✅ smartgrid screenshots done")


if __name__ == "__main__":
    main()
