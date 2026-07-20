#!/usr/bin/env python3
"""Render markdown files to PDF via headless Chrome.

Usage:  python3 md_to_pdf.py file1.md file2.md ...
Outputs:  file1.pdf, file2.pdf in the same directory as the source.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CSS = """
@page {
  size: A4;
  margin: 18mm 16mm;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1a1d22;
  line-height: 1.45;
  font-size: 10.5pt;
}
h1, h2, h3, h4 {
  color: #0b2a4a;
  page-break-after: avoid;
}
h1 { font-size: 22pt; border-bottom: 2px solid #0b2a4a; padding-bottom: 4px; margin-top: 0; }
h2 { font-size: 15pt; border-bottom: 1px solid #c9c9c9; padding-bottom: 3px; margin-top: 22px; }
h3 { font-size: 12pt; margin-top: 16px; }
h4 { font-size: 11pt; margin-top: 14px; color: #1d6f7a; }
p  { margin: 6px 0; }
ul, ol { margin: 6px 0 6px 22px; padding: 0; }
li { margin: 2px 0; }
hr {
  border: 0; border-top: 1px solid #c9c9c9;
  margin: 18px 0;
}
code {
  font-family: "SF Mono", Menlo, Consolas, monospace;
  background: #f0eadb;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 0.88em;
}
pre {
  background: #f6f3ea;
  border: 1px solid #e0d8c5;
  border-radius: 4px;
  padding: 8px 12px;
  overflow-x: auto;
  page-break-inside: avoid;
  font-size: 0.85em;
}
pre code { background: transparent; padding: 0; border-radius: 0; }
blockquote {
  border-left: 3px solid #1d6f7a;
  margin: 8px 0; padding: 4px 12px;
  background: #f5efe1; color: #333;
  page-break-inside: avoid;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 9.5pt;
  page-break-inside: auto;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th, td {
  border: 1px solid #c9c9c9;
  padding: 5px 8px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #0b2a4a;
  color: #fff;
  font-weight: 600;
}
tr:nth-child(even) td { background: #faf6ec; }
a { color: #1d6f7a; }
strong { color: #0b2a4a; }

img {
  max-width: 100%;
  border: 1px solid #c9c9c9;
  border-radius: 4px;
  margin: 8px 0;
  page-break-inside: avoid;
  display: block;
}
em.caption {
  display: block;
  font-size: 0.85em;
  color: #555;
  text-align: center;
  margin-top: -2px;
  margin-bottom: 12px;
}
"""

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <base href="{base_href}">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def md_to_pdf(md_path: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "attr_list", "def_list", "sane_lists"],
    )
    html_full = HTML_TEMPLATE.format(
        title=md_path.stem,
        css=CSS,
        body=html_body,
        base_href=f"file://{md_path.parent}/",
    )

    with tempfile.NamedTemporaryFile(
        suffix=".html", delete=False, mode="w", encoding="utf-8"
    ) as fh:
        fh.write(html_full)
        html_path = Path(fh.name)

    pdf_path = md_path.with_suffix(".pdf")

    try:
        subprocess.run(
            [
                "google-chrome",
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                f"--print-to-pdf={pdf_path}",
                "--no-pdf-header-footer",
                "--virtual-time-budget=2000",
                f"file://{html_path}",
            ],
            check=True,
            capture_output=True,
        )
    finally:
        html_path.unlink(missing_ok=True)

    return pdf_path


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    for arg in argv:
        src = Path(arg).expanduser().resolve()
        if not src.is_file():
            print(f"skip (not a file): {src}")
            continue
        out = md_to_pdf(src)
        size_kb = out.stat().st_size / 1024
        print(f"  {src.name:36s} -> {out.name}  ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
