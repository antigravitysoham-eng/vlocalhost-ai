#!/usr/bin/env python3
"""Render the installation guide to PDF and to HTML.

    python tools/make_install_guide.py

Writes:
    install/vlocalhost-installation-guide.pdf   ships inside the download
    install/guide/index.html                    the online guide

Both come from ``guide_content.py``. Edit that, never these outputs.

On pagination: the previous version forced a page break between every section,
which left pages carrying three lines of text. Sections now flow, and a break
happens only when a heading would otherwise land within ``ROOM`` of the foot of
the page. That is the difference between a document and a stack of covers.
"""

import html as html_mod
import os
import re
import shutil
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable,
                                Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle)

import guide_content as G

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF_OUT = os.path.join(ROOT, "install", "vlocalhost-installation-guide.pdf")
HTML_DIR = os.path.join(ROOT, "install", "guide")
HTML_OUT = os.path.join(HTML_DIR, "index.html")

# A heading needs at least this much page beneath it, or it starts the next one.
ROOM = 46 * mm

# Brand, adapted for paper. The app's cyan is too light on white, so notes take
# the darker teal; amber stays, because it is the one accent the product has.
INK = colors.HexColor("#0E1219")
BODY = colors.HexColor("#3A4354")
MUTED = colors.HexColor("#6B7688")
AMBER = colors.HexColor("#9A6100")
AMBER_HI = colors.HexColor("#FFB43D")     # screen amber, for the dark cover
TEAL = colors.HexColor("#0B7268")
RED = colors.HexColor("#B23A26")
RULE = colors.HexColor("#D9DFE8")
PANEL = colors.HexColor("#F4F6FA")
CODEBG = colors.HexColor("#EEF1F6")
COVER_BG = colors.HexColor("#090C12")     # the site's background, exactly

styles = getSampleStyleSheet()


def S(name, **kw):
    base = kw.pop("parent", styles["BodyText"])
    return ParagraphStyle(name, parent=base, **kw)


H1 = S("h1", fontName="Helvetica-Bold", fontSize=20, leading=24,
       textColor=INK, spaceBefore=2, spaceAfter=3)
STAND = S("stand", fontName="Helvetica", fontSize=10.5, leading=15,
          textColor=MUTED, spaceAfter=12)
H2 = S("h2", fontName="Helvetica-Bold", fontSize=13, leading=16.5,
       textColor=INK, spaceBefore=15, spaceAfter=5, keepWithNext=1)
H3 = S("h3", fontName="Helvetica-Bold", fontSize=10.5, leading=13.5,
       textColor=AMBER, spaceBefore=10, spaceAfter=3, keepWithNext=1)
P_ = S("p", fontName="Helvetica", fontSize=10, leading=15, textColor=BODY,
       spaceAfter=7, alignment=TA_LEFT)
LEAD_ = S("lead", fontName="Helvetica", fontSize=11, leading=16.5,
          textColor=INK, spaceAfter=9)
LI = S("li", parent=P_, leftIndent=13, bulletIndent=3, spaceAfter=4)
STEP = S("step", parent=P_, leftIndent=17, bulletIndent=0, spaceAfter=6)
CODE_ = S("code", fontName="Courier", fontSize=8.6, leading=12.5,
          textColor=INK, backColor=CODEBG, borderPadding=(6, 7, 6, 7),
          borderColor=RULE, borderWidth=0.4, leftIndent=2,
          spaceBefore=3, spaceAfter=9)
NOTE_ = S("note", fontName="Helvetica-Oblique", fontSize=9.5, leading=14,
          textColor=TEAL, leftIndent=10, spaceAfter=8)
WARN_ = S("warn", fontName="Helvetica", fontSize=9.5, leading=14,
          textColor=RED, leftIndent=10, spaceAfter=8)


def pdf_markup(text):
    """Our two tags, in the dialect reportlab speaks."""
    return re.sub(r"<code>(.*?)</code>",
                  r"<font face='Courier' size='9'>\1</font>", text,
                  flags=re.S)


class Bookmark(Flowable):
    """A zero-height marker that puts a section in the PDF sidebar.

    Readers open a 10-page manual and look for the navigation pane; without
    outline entries there is nothing in it.
    """

    def __init__(self, title, key):
        Flowable.__init__(self)
        self.title, self.key = title, key
        self.width = self.height = 0

    def draw(self):
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.title, self.key, level=0, closed=False)


class Rule(Flowable):
    """The amber rule that opens every section — the one brand mark on paper."""

    def __init__(self, width, thickness=2.4, colour=AMBER, length=26 * mm):
        Flowable.__init__(self)
        self.width, self.height = width, thickness
        self.thickness, self.colour, self.length = thickness, colour, length

    def draw(self):
        self.canv.setStrokeColor(self.colour)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.length, 0)


def table(head, rows, widths_mm):
    data = ([head] if head else []) + rows
    data = [[Paragraph(pdf_markup(str(c)), P_) if len(str(c)) > 34 else str(c)
             for c in row] for row in data]
    t = Table(data, colWidths=[w * mm for w in widths_mm], hAlign="LEFT")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.8),
        ("LEADING", (0, 0), (-1, -1), 12.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), BODY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]
    if head:
        style += [
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (-1, 0), INK),
            ("BACKGROUND", (0, 0), (-1, 0), PANEL),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, RULE),
        ]
    else:
        style += [("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                  ("TEXTCOLOR", (0, 0), (0, -1), INK)]
    t.setStyle(TableStyle(style))
    return t


def render_blocks(blocks):
    """One guide section's blocks, as reportlab flowables."""
    out = []
    for kind, payload in blocks:
        if kind == "p":
            out.append(Paragraph(pdf_markup(payload), P_))
        elif kind == "lead":
            out.append(Paragraph(pdf_markup(payload), LEAD_))
        elif kind == "h2":
            # Bind a subheading to what follows it; a stranded heading at the
            # foot of a page is the other half of the whitespace problem.
            out.append(CondPageBreak(30 * mm))
            out.append(Paragraph(pdf_markup(payload), H2))
        elif kind == "steps":
            out += [Paragraph(pdf_markup(t), STEP, bulletText=f"{i}.")
                    for i, t in enumerate(payload, 1)]
        elif kind == "bullets":
            out += [Paragraph(pdf_markup(t), LI, bulletText="•")
                    for t in payload]
        elif kind == "code":
            out.append(Paragraph(html_mod.escape(payload), CODE_))
        elif kind == "note":
            out.append(Paragraph(pdf_markup(payload), NOTE_))
        elif kind == "warn":
            out.append(Paragraph(pdf_markup(payload), WARN_))
        elif kind == "table":
            head, rows, widths = payload
            out.append(table(head, rows, widths))
            out.append(Spacer(1, 7))
        elif kind == "problem":
            title, cause, body = payload
            block = [Paragraph(pdf_markup(title), H3),
                     Paragraph(pdf_markup(cause), P_)]
            block += render_blocks(body)
            out.append(KeepTogether(block))
    return out


def cover(canvas, doc):
    w, h = A4
    canvas.saveState()
    band = 62 * mm
    canvas.setFillColor(COVER_BG)
    canvas.rect(0, h - band, w, band, stroke=0, fill=1)

    # The waveform from the site's nav, drawn rather than embedded so the PDF
    # carries no external asset.
    canvas.setStrokeColor(AMBER_HI)
    canvas.setLineWidth(2.2)
    canvas.setLineCap(1)
    x0, y0, u = 20 * mm, h - 26 * mm, 2.6
    pts = [(0, 0), (3, 0), (5, 7), (8, -8), (11, 3), (13, -2), (15, 2), (20, 2)]
    path = canvas.beginPath()
    path.moveTo(x0, y0)
    for dx, dy in pts[1:]:
        path.lineTo(x0 + dx * u, y0 + dy * u)
    canvas.drawPath(path, stroke=1, fill=0)

    # Measure rather than guess: a fixed offset here put the amber "AI" on top
    # of the wordmark.
    canvas.setFont("Helvetica-Bold", 13)
    word_x = x0 + 24 * u
    canvas.setFillColor(colors.white)
    canvas.drawString(word_x, y0 - 4, "Vlocalhost")
    canvas.setFillColor(AMBER_HI)
    canvas.drawString(word_x + canvas.stringWidth("Vlocalhost ", "Helvetica-Bold", 13),
                      y0 - 4, "AI")

    canvas.setFillColor(colors.HexColor("#7E8AA0"))
    canvas.setFont("Helvetica", 9)
    canvas.drawString(20 * mm, h - 42 * mm, G.TAGLINE.upper())

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 27)
    canvas.drawString(20 * mm, h - 55 * mm, "Installation Guide")
    canvas.restoreState()


def page(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 12 * mm,
                      f"Vlocalhost.AI {G.VERSION} — Installation Guide")
    canvas.drawRightString(w - 20 * mm, 12 * mm, str(doc.page))
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(20 * mm, 15.5 * mm, w - 20 * mm, 15.5 * mm)
    # A brand tick, kept in the top-right corner: sitting at the left margin it
    # lined up directly above the first heading and read as a section rule.
    canvas.setStrokeColor(AMBER)
    canvas.setLineWidth(2)
    canvas.line(w - 20 * mm - 9 * mm, h - 13 * mm, w - 20 * mm, h - 13 * mm)
    canvas.restoreState()


def build_pdf():
    doc = BaseDocTemplate(
        PDF_OUT, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=22 * mm, bottomMargin=22 * mm,
        title=f"Vlocalhost.AI {G.VERSION} — Installation Guide",
        author="Vlocalhost.AI", subject="Installation, first run and troubleshooting",
        keywords="vlocalhost, install, meeting notes, local, privacy")

    # The cover frame stops clear of the dark band rather than starting under
    # the top margin, so the blurb sits a measured distance below it.
    frame_cover = Frame(doc.leftMargin, doc.bottomMargin, doc.width,
                        doc.height - 52 * mm, id="cover")
    frame_body = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                       id="body")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame_cover], onPage=cover),
        PageTemplate(id="body", frames=[frame_body], onPage=page),
    ])

    F = [Paragraph(G.BLURB, S("blurb", fontName="Helvetica", fontSize=11.5,
                               leading=17, textColor=MUTED, spaceAfter=14))]
    F += [table(None, [
        ["Version", G.VERSION],
        ["Updated", date.today().strftime("%d %B %Y")],
        ["Download", G.RELEASES],
        ["Online guide", G.GUIDE_URL],
        ["Support", G.SUPPORT],
        ["Licence", "AGPL-3.0 — free forever, source open"],
    ], [32, 128])]
    F += [Spacer(1, 9 * mm)]
    F += [Paragraph("Contents", S("ctitle", fontName="Helvetica-Bold",
                                  fontSize=11, textColor=INK, spaceAfter=6))]
    F += [table(None, [[str(i), s[1], s[2]]
                       for i, s in enumerate(G.SECTIONS, 1)],
                [8, 40, 112])]

    F += [NextPageTemplate("body"), PageBreak()]

    for anchor, title, stand, blocks in G.SECTIONS:
        F += [CondPageBreak(ROOM),
              Bookmark(title, anchor),
              Rule(doc.width),
              Spacer(1, 7),
              Paragraph(title, H1),
              Paragraph(stand, STAND)]
        F += render_blocks(blocks)
        F += [Spacer(1, 6 * mm)]

    doc.build(F)
    return PDF_OUT


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
CSS = """
:root{
  --bg:#E5E8EE;--panel:#EDEFF4;--ink:#0B0F18;--muted:#55617A;--faint:#97A1B4;
  --line:rgba(12,22,45,.14);--hair:rgba(12,22,45,.07);--amber:#A85F0C;
  --amber-d:#7F4708;--cyan:#0B8577;--glass:rgba(12,22,45,.025);
  --warn:#B23A26;
  --f-body:system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  --f-display:'Helvetica Neue',Helvetica,Arial,system-ui,sans-serif;
  --f-mono:ui-monospace,'Cascadia Code','SF Mono','JetBrains Mono',Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#090C12;--panel:#0E121A;--ink:#EAEEF4;--muted:#7E8AA0;--faint:#4B5468;
  --line:rgba(255,255,255,.10);--hair:rgba(255,255,255,.055);--amber:#FFB43D;
  --amber-d:#E08A17;--cyan:#38E1CE;--glass:rgba(255,255,255,.03);--warn:#FF8A6B;
}}
:root[data-theme="dark"]{
  --bg:#090C12;--panel:#0E121A;--ink:#EAEEF4;--muted:#7E8AA0;--faint:#4B5468;
  --line:rgba(255,255,255,.10);--hair:rgba(255,255,255,.055);--amber:#FFB43D;
  --amber-d:#E08A17;--cyan:#38E1CE;--glass:rgba(255,255,255,.03);--warn:#FF8A6B;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-body);
  font-size:16px;line-height:1.62;-webkit-font-smoothing:antialiased}
a{color:var(--amber);text-decoration:none;border-bottom:1px solid var(--line)}
a:hover{border-bottom-color:var(--amber)}
a:focus-visible{outline:2px solid var(--amber);outline-offset:3px;border-radius:2px}
.nav{border-bottom:1px solid var(--hair);position:sticky;top:0;background:var(--bg);z-index:20}
.nav-in{max-width:1120px;margin:0 auto;padding:13px 22px;display:flex;
  align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.brand{display:inline-flex;align-items:center;gap:9px;color:var(--ink);
  font-weight:600;border:none;letter-spacing:-.01em}
.brand svg{width:19px;height:19px;color:var(--amber)}
.brand small{color:var(--amber);font-weight:700}
.dl{font-family:var(--f-mono);font-size:11.5px;letter-spacing:.09em;
  text-transform:uppercase;background:var(--amber);color:var(--bg);
  border-radius:9px;padding:10px 16px;border:none;font-weight:600}
.dl:hover{background:var(--amber-d);border:none}
.shell{max-width:1120px;margin:0 auto;padding:0 22px;display:grid;
  grid-template-columns:212px minmax(0,1fr);gap:46px;align-items:start}
@media (max-width:900px){.shell{grid-template-columns:1fr;gap:0}}
.toc{position:sticky;top:74px;padding:40px 0 40px;font-size:14px}
@media (max-width:900px){.toc{position:static;padding:26px 0 0;
  border-bottom:1px solid var(--hair)}}
.toc p{font-family:var(--f-mono);font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--faint);margin:0 0 12px}
.toc ol{list-style:none;margin:0;padding:0;counter-reset:t}
.toc li{counter-increment:t;margin-bottom:2px}
.toc a{display:block;padding:5px 0;color:var(--muted);border:none}
.toc a:hover,.toc a:focus-visible{color:var(--amber)}
.toc a::before{content:counter(t,decimal-leading-zero);font-family:var(--f-mono);
  font-size:10px;color:var(--faint);margin-right:9px}
main{padding:40px 0 56px;min-width:0}
.hero{padding-bottom:30px;margin-bottom:8px;border-bottom:1px solid var(--hair)}
.eyebrow{font-family:var(--f-mono);font-size:10.5px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--amber);margin:0 0 16px}
h1{font-family:var(--f-display);font-size:clamp(32px,5.4vw,46px);line-height:1.05;
  letter-spacing:-.03em;font-weight:700;margin:0 0 16px;text-wrap:balance}
.blurb{font-size:18px;color:var(--muted);max-width:56ch;margin:0 0 22px}
.meta{font-family:var(--f-mono);font-size:11.5px;color:var(--faint);
  display:flex;gap:18px;flex-wrap:wrap}
section{scroll-margin-top:76px;padding-top:46px}
h2.sec{font-family:var(--f-display);font-size:clamp(24px,3.2vw,31px);
  letter-spacing:-.024em;font-weight:700;margin:0 0 6px;line-height:1.15}
h2.sec::before{content:"";display:block;width:26px;height:3px;
  background:var(--amber);border-radius:2px;margin-bottom:16px}
.stand{color:var(--muted);margin:0 0 20px;max-width:60ch}
h3{font-family:var(--f-display);font-size:18px;font-weight:650;
  letter-spacing:-.012em;margin:30px 0 8px;text-wrap:balance}
h4{font-family:var(--f-display);font-size:15.5px;font-weight:650;color:var(--amber);
  margin:24px 0 5px}
p{margin:0 0 13px;max-width:68ch}
p.lead{font-size:17.5px;color:var(--ink);max-width:60ch;margin-bottom:16px}
ul,ol{margin:0 0 15px;padding-left:22px;max-width:66ch}
li{margin-bottom:6px;padding-left:3px}
li::marker{color:var(--faint)}
code{font-family:var(--f-mono);font-size:.86em;background:var(--glass);
  border:1px solid var(--hair);border-radius:4px;padding:1.5px 5px;
  overflow-wrap:anywhere}
pre{font-family:var(--f-mono);font-size:13px;line-height:1.6;background:var(--glass);
  border:1px solid var(--line);border-radius:10px;padding:14px 16px;
  overflow-x:auto;margin:0 0 15px;max-width:68ch}
pre code{background:none;border:none;padding:0;font-size:inherit}
.note,.warn{border-left:2px solid var(--cyan);padding:2px 0 2px 15px;
  margin:0 0 15px;max-width:64ch;font-size:15px;color:var(--muted)}
.warn{border-left-color:var(--warn)}
.warn b,.note b{color:var(--ink)}
.t-scroll{overflow-x:auto;margin:0 0 18px}
table{border-collapse:collapse;width:100%;min-width:420px;font-size:14.5px}
th,td{text-align:left;padding:10px 14px 10px 0;border-bottom:1px solid var(--hair);
  vertical-align:top}
th{font-family:var(--f-mono);font-size:10.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--faint);font-weight:500;
  border-bottom-color:var(--line)}
tbody td:first-child{color:var(--ink);font-weight:600}
.prob{border:1px solid var(--line);border-radius:12px;padding:18px 20px 6px;
  margin:0 0 12px;background:var(--panel)}
.prob h4{margin-top:0}
.prob .cause{color:var(--muted);font-size:14.5px;margin-bottom:11px}
footer{border-top:1px solid var(--hair);margin-top:44px;padding:24px 0 0;
  font-family:var(--f-mono);font-size:11.5px;color:var(--faint);line-height:1.8}
@media print{.nav,.toc{display:none}.shell{grid-template-columns:1fr}}
"""

MARK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" aria-hidden="true">'
        '<path d="M2 12h3l2-7 3 15 3-11 2 5 2-2h5"/></svg>')


def h(text):
    """Guide markup is already the HTML we want — only bare & needs care."""
    return re.sub(r"&(?![a-zA-Z]+;|#\d+;)", "&amp;", text)


def html_blocks(blocks, out):
    for kind, payload in blocks:
        if kind == "p":
            out.append(f"<p>{h(payload)}</p>")
        elif kind == "lead":
            out.append(f'<p class="lead">{h(payload)}</p>')
        elif kind == "h2":
            out.append(f"<h3>{h(payload)}</h3>")
        elif kind == "steps":
            out.append("<ol>" + "".join(f"<li>{h(t)}</li>" for t in payload)
                       + "</ol>")
        elif kind == "bullets":
            out.append("<ul>" + "".join(f"<li>{h(t)}</li>" for t in payload)
                       + "</ul>")
        elif kind == "code":
            out.append("<pre><code>"
                       + html_mod.escape(payload) + "</code></pre>")
        elif kind == "note":
            out.append(f'<p class="note">{h(payload)}</p>')
        elif kind == "warn":
            out.append(f'<p class="warn">{h(payload)}</p>')
        elif kind == "table":
            head, rows, _ = payload
            t = ['<div class="t-scroll"><table>']
            if head:
                t.append("<thead><tr>"
                         + "".join(f"<th>{h(str(c))}</th>" for c in head)
                         + "</tr></thead>")
            t.append("<tbody>")
            for row in rows:
                cells = []
                for c in row:
                    c = str(c)
                    if c.startswith("http"):
                        c = f'<a href="{c}">{c}</a>'
                    cells.append(f"<td>{h(c)}</td>")
                t.append("<tr>" + "".join(cells) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
        elif kind == "problem":
            title, cause, body = payload
            out.append('<div class="prob">')
            out.append(f"<h4>{h(title)}</h4>")
            out.append(f'<p class="cause">{h(cause)}</p>')
            html_blocks(body, out)
            out.append("</div>")


def build_html():
    os.makedirs(HTML_DIR, exist_ok=True)
    updated = date.today().strftime("%d %B %Y")
    pdf_name = os.path.basename(PDF_OUT)

    toc = "".join(f'<li><a href="#{a}">{t}</a></li>'
                  for a, t, _, _ in G.SECTIONS)

    body = []
    for anchor, title, stand, blocks in G.SECTIONS:
        body.append(f'<section id="{anchor}">')
        body.append(f'<h2 class="sec">{h(title)}</h2>')
        body.append(f'<p class="stand">{h(stand)}</p>')
        html_blocks(blocks, body)
        body.append("</section>")

    page_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Installation Guide — Vlocalhost.AI</title>
<meta name="description" content="{h(G.BLURB)}">
<link rel="icon" href="../../assets/favicon.svg">
<style>{CSS}</style>
</head>
<body>

<nav class="nav">
  <div class="nav-in">
    <a class="brand" href="../../">{MARK} Vlocalhost <small>AI</small></a>
    <a class="dl" href="../{pdf_name}" download>Download PDF</a>
  </div>
</nav>

<div class="shell">
  <aside class="toc">
    <p>Contents</p>
    <ol>{toc}</ol>
  </aside>

  <main>
    <div class="hero">
      <p class="eyebrow">Vlocalhost.AI {G.VERSION}</p>
      <h1>Installation Guide</h1>
      <p class="blurb">{h(G.BLURB)}</p>
      <div class="meta">
        <span>Updated {updated}</span>
        <span>AGPL-3.0</span>
        <span><a href="{G.RELEASES}">Downloads</a></span>
        <span><a href="{G.SUPPORT}">Support</a></span>
      </div>
    </div>

    {''.join(body)}

    <footer>
      This page and the PDF are generated from one source — edits belong in
      <code>tools/guide_content.py</code>.<br>
      A copy of the PDF ships inside every download, and opens from
      Settings &rarr; Installation guide.
    </footer>
  </main>
</div>

</body>
</html>
"""
    with open(HTML_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(page_html)
    return HTML_OUT


def main():
    pdf = build_pdf()
    page_out = build_html()
    print(f"wrote {pdf} ({os.path.getsize(pdf) / 1024:.0f} KB)")
    print(f"wrote {page_out} ({os.path.getsize(page_out) / 1024:.0f} KB)")

    # Core ships the same PDF inside the download. Copy it when that checkout
    # is beside this one, so the two cannot drift silently.
    core_docs = os.path.join(os.path.dirname(ROOT), "Meeting Notes Agent",
                             "core", "docs")
    if os.path.isdir(core_docs):
        dest = os.path.join(core_docs, os.path.basename(PDF_OUT))
        shutil.copy2(pdf, dest)
        print(f"copied to {dest}")


if __name__ == "__main__":
    main()
