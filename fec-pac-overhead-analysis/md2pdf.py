"""Minimal Markdown -> styled HTML for the memo, then print to PDF via Chromium.
Handles: #..#### headings, pipe tables, ** bold, * italic, `code`, --- rules,
- bullet lists, blank-line paragraphs. Good enough for MEMO.md; not a full parser.
"""
import html
import re
import subprocess
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "MEMO.md"
HTML = SRC.rsplit(".", 1)[0] + ".html"
PDF = SRC.rsplit(".", 1)[0] + ".pdf"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


lines = open(SRC).read().split("\n")
out, i = [], 0
while i < len(lines):
    ln = lines[i]
    m = re.match(r"^(#{1,6})\s+(.*)", ln)
    if m:
        lvl = len(m.group(1))
        out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
        i += 1
        continue
    if re.match(r"^---+\s*$", ln):
        out.append("<hr>")
        i += 1
        continue
    # table: header row, separator row, then body
    if "|" in ln and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]):
        head = cells(ln)
        i += 2
        body = []
        while i < len(lines) and "|" in lines[i] and lines[i].strip():
            body.append(cells(lines[i]))
            i += 1
        th = "".join(f"<th>{inline(c)}</th>" for c in head)
        rows = ""
        for r in body:
            rows += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
        out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>")
        continue
    if re.match(r"^\s*[-*]\s+", ln):
        items = []
        while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
            items.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>")
            i += 1
        out.append("<ul>" + "".join(items) + "</ul>")
        continue
    if ln.strip() == "":
        i += 1
        continue
    # paragraph (gather until blank)
    para = [ln]
    i += 1
    while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|---+\s*$|\s*[-*]\s+)", lines[i]) and "|" not in lines[i]:
        para.append(lines[i])
        i += 1
    out.append("<p>" + inline(" ".join(para)) + "</p>")

CSS = """
@page { size: Letter; margin: 0.75in; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.45 -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
       color: #1a1a1a; max-width: 100%; }
h1 { font-size: 19pt; margin: 0 0 4pt; letter-spacing:-.01em; }
h2 { font-size: 14pt; margin: 20pt 0 6pt; border-bottom: 2px solid #222; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin: 15pt 0 4pt; color:#111; }
h4 { font-size: 10.5pt; margin: 10pt 0 3pt; }
p { margin: 5pt 0; }
strong { color:#000; }
em { color:#333; }
code { font: 9pt 'SF Mono', Consolas, monospace; background:#f2f2f2; padding:1px 4px; border-radius:3px; }
hr { border:none; border-top:1px solid #ccc; margin:14pt 0; }
table { border-collapse: collapse; width:100%; margin:8pt 0; font-size:9pt; page-break-inside:avoid; }
th { background:#222; color:#fff; text-align:left; padding:5pt 7pt; font-weight:600; }
td { padding:4pt 7pt; border-bottom:1px solid #e2e2e2; vertical-align:top; }
tbody tr:nth-child(even){ background:#f8f8f8; }
td:first-child, th:first-child { white-space:nowrap; }
ul { margin:5pt 0 5pt 0; padding-left:18pt; }
li { margin:3pt 0; }
h3 { page-break-after: avoid; }
table { page-break-inside: auto; }
"""

doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(out)}</body></html>"
open(HTML, "w").write(doc)
print(f"-> {HTML}")

subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                "--no-pdf-header-footer", f"--print-to-pdf={PDF}",
                f"file://{__import__('os').path.abspath(HTML)}"],
               check=True, capture_output=True)
print(f"-> {PDF}")
