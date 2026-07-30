#!/usr/bin/env python3
"""Render scenario 04's two diagrams to PNG.

The repo's existing diagram-*.png files were authored as small HTML fragments and
screenshotted with headless Chrome using the md_to_pdf.py palette; no generator
was committed. This is that generator for scenario 04.

Usage:  python3 scripts/make_s4_diagrams.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_to_pdf import find_chrome  # noqa: E402

OUT = (Path(__file__).resolve().parent.parent
       / "04-clonesystems-seuxdr-siem" / "docs" / "screenshots")

BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
       background: #fff; color: #1a1d22; padding: 22px 26px; }
h2 { font-size: 15pt; color: #0b2a4a; margin-bottom: 3px; }
.sub { font-size: 9.5pt; color: #666; margin-bottom: 16px; }
.row { display: flex; gap: 14px; align-items: stretch; }
.vm { flex: 1; border: 1px solid #c9c9c9; border-radius: 6px; background: #faf6ec;
      padding: 12px 14px; }
.vm.cf { background: #eef4f6; border-color: #1d6f7a; }
.vm.tgt { background: #f5efe1; }
.vm h3 { font-size: 11pt; color: #0b2a4a; margin-bottom: 2px; }
.vm .role { font-size: 8.5pt; color: #777; margin-bottom: 9px; }
.svc { font-size: 9pt; margin: 3px 0; display: flex; justify-content: space-between;
       border-bottom: 1px dotted #cfc9bb; padding-bottom: 2px; }
.svc .p { font-family: "SF Mono", Menlo, Consolas, monospace; color: #1d6f7a; }
.arrow { display: flex; flex-direction: column; justify-content: center;
         align-items: center; font-size: 8pt; color: #666; min-width: 96px; }
.arrow .line { font-size: 15pt; color: #999; line-height: 1; }
.note { margin-top: 14px; font-size: 8.8pt; color: #555; background: #f5efe1;
        border-left: 3px solid #1d6f7a; padding: 7px 11px; border-radius: 3px; }
.warn { border-left-color: #a8323a; background: #fbeeee; }
"""

TOPOLOGY = """
<h2>Scenario 04 &mdash; range topology</h2>
<div class="sub">The assessment is source-side. Only the live demonstration needs VM2 and VM3.</div>
<div class="row">
  <div class="vm cf">
    <h3>VM1 &mdash; CyberFort</h3>
    <div class="role">compliance platform &middot; hosted or range-local</div>
    <div class="svc"><span>Frontend</span><span class="p">:5173</span></div>
    <div class="svc"><span>Backend</span><span class="p">:8000</span></div>
    <div class="svc"><span>Semgrep &middot; OSV &middot; Syft</span><span class="p">:8012-8013</span></div>
    <div class="svc"><span>Nmap &middot; ZAP</span><span class="p">:8010-8011</span></div>
  </div>
  <div class="arrow"><div>source archive<br>or GitHub URL</div><div class="line">&#8594;</div>
    <div>no network path<br>to VM2 required</div></div>
  <div class="vm tgt">
    <h3>VM2 &mdash; SEUXDR target</h3>
    <div class="role">32 GB RAM &middot; amd64 &middot; GPU optional</div>
    <div class="svc"><span>Front end (nginx)</span><span class="p">:8080</span></div>
    <div class="svc"><span>Manager API + agent WS</span><span class="p">:8443</span></div>
    <div class="svc"><span>Agent enrolment (mTLS)</span><span class="p">:8081</span></div>
    <div class="svc"><span>Ollama phi4:14b</span><span class="p">:11434</span></div>
    <div class="svc"><span>Wazuh 4.11 + OpenSearch</span><span class="p">internal</span></div>
  </div>
  <div class="arrow"><div>mTLS enrolment<br>TLS + WebSocket</div><div class="line">&#8592;</div>
    <div>remediation<br>commands</div></div>
  <div class="vm">
    <h3>VM3 &mdash; endpoints</h3>
    <div class="role">throwaway hosts only</div>
    <div class="svc"><span>SEUXDR agent</span><span class="p">Windows</span></div>
    <div class="svc"><span>SEUXDR agent</span><span class="p">Linux</span></div>
    <div class="svc"><span>SEUXDR agent</span><span class="p">macOS</span></div>
    <div class="svc"><span>attack simulations</span><span class="p">11 scripts</span></div>
  </div>
</div>
<div class="note">Two deployable modes on VM2. <b>00a95ad</b> is the baseline product with a
completely unauthenticated API; <b>cra/remediation-sprint-1</b> is the remediated one. Running the
same assessment against both is the exercise.</div>
<div class="note warn">The agent executes <b>rm -f</b>, <b>process kill</b> and host firewall
changes as root. Enrol throwaway endpoints only, on an isolated subnet.</div>
"""

HIERARCHY_CSS = """
.tree { display: flex; gap: 12px; }
.col { flex: 1; border: 1px solid #c9c9c9; border-radius: 6px; overflow: hidden; }
.col header { background: #0b2a4a; color: #fff; padding: 7px 11px; font-size: 10pt;
              font-weight: 600; display: flex; justify-content: space-between; }
.col header .n { background: rgba(255,255,255,.18); border-radius: 9px;
                 padding: 0 8px; font-size: 9pt; }
.col.big header { background: #1d6f7a; }
.col ul { list-style: none; padding: 8px 11px; }
.col li { font-size: 8.8pt; padding: 2.5px 0; border-bottom: 1px dotted #ddd;
          display: flex; gap: 7px; }
.col li:last-child { border-bottom: 0; }
.col li .id { font-family: "SF Mono", Menlo, Consolas, monospace; color: #0b2a4a;
              font-weight: 600; min-width: 26px; }
.foot { margin-top: 13px; display: flex; gap: 12px; }
.pill { flex: 1; border: 1px solid #c9c9c9; border-radius: 6px; padding: 9px 12px;
        background: #f5efe1; font-size: 9pt; }
.pill b { color: #0b2a4a; font-size: 11pt; }
"""

HIERARCHY = """
<h2>Scenario 04 &mdash; the CRA as CyberFort models it</h2>
<div class="sub">30 objectives at asset scope, across six chapters, plus a 52-question
conformity questionnaire. This is the tree the trainee grades.</div>
<div class="tree">
  <div class="col big">
    <header><span>ANNEX I &mdash; essential requirements</span><span class="n">13</span></header>
    <ul>
      <li><span class="id">1</span><span>Appropriate cybersecurity based on risks</span></li>
      <li><span class="id">2</span><span>No known exploitable vulnerabilities</span></li>
      <li><span class="id">3a</span><span>Secure by default, resettable</span></li>
      <li><span class="id">3b</span><span>Protection from unauthorised access</span></li>
      <li><span class="id">3c</span><span>Confidentiality through encryption</span></li>
      <li><span class="id">3d</span><span>Integrity of data and commands</span></li>
      <li><span class="id">3e</span><span>Data minimisation</span></li>
      <li><span class="id">3f</span><span>Availability and DoS resilience</span></li>
      <li><span class="id">3g</span><span>Limit impact on other services</span></li>
      <li><span class="id">3h</span><span>Limit attack surfaces</span></li>
      <li><span class="id">3i</span><span>Reduce impact of an incident</span></li>
      <li><span class="id">3j</span><span>Security-event recording</span></li>
      <li><span class="id">3k</span><span>Vulnerabilities addressable by update</span></li>
    </ul>
  </div>
  <div class="col big">
    <header><span>Vulnerability Handling</span><span class="n">8</span></header>
    <ul>
      <li><span class="id">1</span><span>Identify and document components (SBOM)</span></li>
      <li><span class="id">2</span><span>Remediate without delay</span></li>
      <li><span class="id">3</span><span>Effective and regular testing</span></li>
      <li><span class="id">4</span><span>Publicly disclose fixed vulnerabilities</span></li>
      <li><span class="id">5</span><span>Coordinated disclosure policy</span></li>
      <li><span class="id">6</span><span>Contact address for reports</span></li>
      <li><span class="id">7</span><span>Secure update distribution</span></li>
      <li><span class="id">8</span><span>Disseminate free, with advisories</span></li>
    </ul>
  </div>
  <div class="col">
    <header><span>Chapters</span><span class="n">9</span></header>
    <ul>
      <li><span class="id">I</span><span>Art. 1&ndash;2 scope and applicability</span></li>
      <li><span class="id">I</span><span>Art. 6 + Annex I essential requirements</span></li>
      <li><span class="id">II</span><span>Art. 13 manufacturer obligations</span></li>
      <li><span class="id">II</span><span>Art. 14 reporting to ENISA</span></li>
      <li><span class="id">II</span><span>Art. 25 internal processes</span></li>
      <li><span class="id">II</span><span>Art. 26 user guidance</span></li>
      <li><span class="id">III</span><span>Art. 28 conformity and the DoC</span></li>
      <li><span class="id">V</span><span>Art. 52/54 market surveillance</span></li>
      <li><span class="id">V</span><span>Art. 70 evaluation and review</span></li>
    </ul>
  </div>
</div>
<div class="foot">
  <div class="pill"><b>52</b> conformity questions &mdash; the product-level questionnaire
    the trainee answers, paginated ten per page.</div>
  <div class="pill"><b>Annex III Class I</b> &mdash; SIEM systems. Article 32(2) requires a
    notified body; Module A self-declaration is not available.</div>
  <div class="pill"><b>2 &rarr; 21</b> of 30 compliant &mdash; the manufacturer's claim the
    trainee is there to verify.</div>
</div>
"""


def render(name, body, extra_css, width, height):
    html = (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{BASE_CSS}{extra_css}</style></head><body>{body}</body></html>")
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w",
                                     encoding="utf-8") as fh:
        fh.write(html)
        src = Path(fh.name)
    out = OUT / f"{name}.png"
    try:
        subprocess.run([find_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
                        "--hide-scrollbars", f"--window-size={width},{height}",
                        f"--screenshot={out}", f"file://{src}"],
                       check=True, capture_output=True)
    finally:
        src.unlink(missing_ok=True)
    print(f"  {out.name}  ({out.stat().st_size / 1024:.1f} KB)")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    render("diagram-topology", TOPOLOGY, "", 1380, 300)
    render("diagram-cra-hierarchy", HIERARCHY, HIERARCHY_CSS, 1380, 560)


if __name__ == "__main__":
    main()
