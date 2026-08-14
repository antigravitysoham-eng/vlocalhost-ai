#!/usr/bin/env python3
"""Generate the Vlocalhost.AI installation guide PDF.

    python tools/make_install_guide.py

Writes install/vlocalhost-installation-guide.pdf, which the install page links
to. Keep this script as the source of truth — editing the PDF by hand means the
next regeneration silently discards the change.
"""

import os
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether,
                                PageBreak, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "install", "vlocalhost-installation-guide.pdf")

VERSION = "1.1.1"
SITE = "https://antigravitysoham-eng.github.io/vlocalhost-ai/"
SUPPORT = SITE + "support/"
RELEASES = "https://github.com/antigravitysoham-eng/vlocalhost-core/releases/latest"

# Brand, adapted for paper: dark ink on white, amber for emphasis, teal for
# "this is fine" notes. The app's cyan is too light to read on white.
INK = colors.HexColor("#0E1219")
BODY = colors.HexColor("#3A4354")
MUTED = colors.HexColor("#6B7688")
AMBER = colors.HexColor("#9A6100")
TEAL = colors.HexColor("#0B7268")
RED = colors.HexColor("#B23A26")
RULE = colors.HexColor("#D9DFE8")
PANEL = colors.HexColor("#F4F6FA")
CODEBG = colors.HexColor("#EEF1F6")

styles = getSampleStyleSheet()


def S(name, **kw):
    base = kw.pop("parent", styles["BodyText"])
    return ParagraphStyle(name, parent=base, **kw)


TITLE = S("t", fontName="Helvetica-Bold", fontSize=30, leading=34,
          textColor=INK, spaceAfter=6)
SUB = S("s", fontName="Helvetica", fontSize=12.5, leading=18,
        textColor=MUTED, spaceAfter=18)
H1 = S("h1", fontName="Helvetica-Bold", fontSize=19, leading=23,
       textColor=INK, spaceBefore=20, spaceAfter=9, keepWithNext=1)
H2 = S("h2", fontName="Helvetica-Bold", fontSize=13.5, leading=17,
       textColor=INK, spaceBefore=15, spaceAfter=6, keepWithNext=1)
H3 = S("h3", fontName="Helvetica-Bold", fontSize=11, leading=14,
       textColor=AMBER, spaceBefore=11, spaceAfter=4, keepWithNext=1)
P = S("p", fontName="Helvetica", fontSize=10, leading=15, textColor=BODY,
      spaceAfter=7, alignment=TA_LEFT)
LI = S("li", parent=P, leftIndent=13, bulletIndent=3, spaceAfter=4)
STEP = S("step", fontName="Helvetica", fontSize=10, leading=15, textColor=BODY,
         leftIndent=17, bulletIndent=0, spaceAfter=6)
CODE = S("code", fontName="Courier", fontSize=8.8, leading=13,
         textColor=INK, backColor=CODEBG, borderPadding=(6, 7, 6, 7),
         leftIndent=2, spaceBefore=3, spaceAfter=9)
NOTE = S("note", fontName="Helvetica-Oblique", fontSize=9.5, leading=14,
         textColor=TEAL, leftIndent=10, spaceAfter=8)
WARN = S("warn", fontName="Helvetica", fontSize=9.5, leading=14,
         textColor=RED, leftIndent=10, spaceAfter=8)
SMALL = S("small", fontName="Helvetica", fontSize=8.5, leading=12,
          textColor=MUTED, spaceAfter=5)


def bullets(items, style=LI):
    return [Paragraph(t, style, bulletText="\u2022") for t in items]


def steps(items):
    return [Paragraph(t, STEP, bulletText=f"{i}.")
            for i, t in enumerate(items, 1)]


def table(rows, widths, header=True):
    t = Table(rows, colWidths=widths, hAlign="LEFT")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.6),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("TEXTCOLOR", (0, 0), (-1, -1), BODY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]
    if header:
        style += [
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (-1, 0), INK),
            ("BACKGROUND", (0, 0), (-1, 0), PANEL),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, RULE),
        ]
    t.setStyle(TableStyle(style))
    return t


def problem(title, cause, fix):
    """One troubleshooting entry, kept on a single page."""
    block = [Paragraph(title, H3), Paragraph(cause, P)]
    block += fix if isinstance(fix, list) else [Paragraph(fix, P)]
    return KeepTogether(block)


def section(title, first):
    """A heading glued to whatever follows it.

    ``keepWithNext`` on the style is not enough here: the next flowable is a
    KeepTogether, and reportlab will happily break between the two, leaving a
    heading stranded alone at the foot of a page.
    """
    return KeepTogether([Paragraph(title, H2), first])


# ---------------------------------------------------------------------------
def decorate(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(20 * mm, 12 * mm,
                          f"Vlocalhost.AI {VERSION} \u2014 Installation Guide")
        canvas.drawRightString(w - 20 * mm, 12 * mm, str(doc.page))
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(20 * mm, 15.5 * mm, w - 20 * mm, 15.5 * mm)
    else:
        # A single amber rule on the cover, echoing the app's one accent.
        canvas.setStrokeColor(colors.HexColor("#FFB43D"))
        canvas.setLineWidth(3)
        canvas.line(20 * mm, h - 42 * mm, 62 * mm, h - 42 * mm)
    canvas.restoreState()


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=20 * mm, bottomMargin=20 * mm,
                          title=f"Vlocalhost.AI {VERSION} — Installation Guide",
                          author="Vlocalhost", subject="Installation and troubleshooting")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id="body")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame],
                                       onPage=decorate)])

    F = []           # flowables

    # ---------------------------------------------------------------- cover
    F += [Spacer(1, 26 * mm)]
    F += [Paragraph("Vlocalhost.AI", TITLE)]
    F += [Paragraph("Installation Guide", S("t2", parent=TITLE, fontSize=21,
                                            leading=25, textColor=AMBER))]
    F += [Spacer(1, 6 * mm)]
    F += [Paragraph(
        "Meeting notes that never leave your machine. This guide covers "
        "Windows, macOS and Linux, what to do when something goes wrong, and "
        "how to set up the optional summary model.", SUB)]
    F += [Spacer(1, 4 * mm)]
    F += [table([
        ["Version", VERSION],
        ["Updated", date.today().strftime("%d %B %Y")],
        ["Download", RELEASES],
        ["Support", SUPPORT],
        ["Licence", "AGPL-3.0 \u2014 free forever, source open"],
    ], [32 * mm, 128 * mm], header=False)]

    F += [Spacer(1, 10 * mm)]
    F += [Paragraph("What you need", H2)]
    F += bullets([
        "<b>Nothing but the download.</b> The installer carries its own Python "
        "and every library it needs. You do not need to install Python, pip, "
        "or anything else first.",
        "<b>About 400 MB of free disk space</b>, plus ~150 MB the first time "
        "you record, when the speech model downloads.",
        "<b>A microphone.</b> Any built-in one is fine.",
        "<b>Optional: Ollama</b>, only if you want written summaries. Without "
        "it you still get a complete, timestamped transcript of every meeting.",
    ])
    F += [Paragraph(
        "No account, no sign-in, no internet connection after the download. "
        "Audio and transcripts never leave your computer.", NOTE)]

    F += [PageBreak()]

    # -------------------------------------------------------------- windows
    F += [Paragraph("Windows", H1)]
    F += [Paragraph("Windows 10 or 11, 64-bit.", SMALL)]

    F += [Paragraph("Install", H2)]
    F += steps([
        f'Download <b>vlocalhost-{VERSION}-windows-x64-setup.exe</b> from '
        f'the downloads page.',
        "Double-click it.",
        "<b>Windows will show a blue \u201cWindows protected your PC\u201d "
        "screen.</b> This is expected \u2014 see the note below. Click "
        "<b>More info</b>, then <b>Run anyway</b>.",
        "Choose where to install it. The default is inside your user folder "
        "and needs no administrator rights. You can pick any drive \u2014 "
        "<font face='Courier'>D:\\Apps\\Vlocalhost</font> is fine.",
        "Leave <b>Create a desktop shortcut</b> ticked if you want one.",
        "Click <b>Install</b>, then <b>Finish</b>. The app opens and asks you "
        "two setup questions.",
    ])
    F += [Paragraph(
        "<b>Why the warning appears.</b> Windows shows that screen for any "
        "program without a paid code-signing certificate. It is not a virus "
        "warning and says nothing about the file's contents. Vlocalhost is "
        "open source \u2014 you can read every line of what the installer "
        "puts on your machine. A signed build is planned.", WARN)]
    F += [Paragraph(
        "The installer needs no administrator password, so it works on a "
        "locked-down work laptop.", NOTE)]

    F += [Paragraph("Uninstall", H2)]
    F += [Paragraph(
        "<b>Settings \u2192 Apps \u2192 Installed apps \u2192 Vlocalhost.AI "
        "\u2192 Uninstall</b>, or use the shortcut in the Start menu folder. "
        "Your meeting notes and settings are deliberately kept. To remove "
        "those too, delete this folder afterwards:", P)]
    F += [Paragraph("%LOCALAPPDATA%\\Vlocalhost", CODE)]

    F += [Paragraph("Or: the portable ZIP", H2)]
    F += [Paragraph(
        f"Every release also ships <b>vlocalhost-{VERSION}-windows-x64.zip</b>: the "
        "same build with no installer. Take this one if a virus scanner refuses "
        "the .exe, if Chrome reports \u201cVirus scan failed\u201d, or if you simply "
        "want nothing written outside a single folder.", P)]
    F += steps([
        "Unpack the .zip anywhere you can write. Keep the path short \u2014 a "
        "folder buried deeper than about 140 characters cannot unpack cleanly, "
        "because the files inside are already long.",
        "Open the folder and run <b>Vlocalhost.cmd</b>.",
        "That is the whole install. Nothing is written outside this folder.",
    ])
    F += [Paragraph(
        "<b>No desktop icon?</b> Correct \u2014 the ZIP deliberately touches nothing "
        "outside its own folder. The app can still make one. Run this once from "
        "the unpacked folder:", P)]
    F += [Paragraph("runtime\\pythonw.exe app\\vlocalhost.py --install-shortcut", CODE)]
    F += [Paragraph(
        "It adds Vlocalhost.AI to your desktop and Start menu, pointing at the "
        "copy you unpacked, and finds the real desktop folder even when OneDrive "
        "has moved it.", NOTE)]

    F += [Paragraph("Removing the portable version", H2)]
    F += [Paragraph(
        "There is no uninstaller and no Add/Remove Programs entry \u2014 that is "
        "what portable means. Removing it is one step, or three if you made "
        "shortcuts:", P)]
    F += steps([
        "Delete the folder you unpacked. The program is gone.",
        "If you created shortcuts, remove them with "
        "<font face='Courier'>runtime\\pythonw.exe app\\vlocalhost.py "
        "--remove-shortcut</font> before deleting the folder \u2014 or delete the "
        "two .lnk files by hand afterwards.",
        "Notes and settings survive on purpose, in the folders listed under "
        "\u201cWhere your files live\u201d. Delete those only if you want the "
        "meetings gone too.",
    ])

    F += [PageBreak()]

    # ---------------------------------------------------------------- macOS
    F += [Paragraph("macOS", H1)]
    F += [Paragraph("<b>Coming soon.</b> Apple silicon and Intel builds are being packaged and tested. Everything below is how it will work; the download is not on the releases page yet. Today, both platforms run from source: see the README in the repository.", WARN)]
    F += [Paragraph("macOS 12 Monterey or newer.", SMALL)]

    F += [Paragraph("Pick the right build", H2)]
    F += [Paragraph(
        "Click the Apple menu \u2192 <b>About This Mac</b> and look at the "
        "chip:", P)]
    F += [table([
        ["Your Mac says", "Download"],
        ["Apple M1 / M2 / M3 / M4", f"vlocalhost-{VERSION}-macos-arm64.dmg"],
        ["Intel", f"vlocalhost-{VERSION}-macos-x64.dmg"],
    ], [55 * mm, 105 * mm])]

    F += [Paragraph("Install", H2)]
    F += steps([
        "Download the .dmg and double-click it.",
        "Drag <b>Vlocalhost</b> onto the <b>Applications</b> folder in the "
        "window that opens.",
        "Eject the disk image, then open <b>Vlocalhost</b> from Applications "
        "or Launchpad.",
        "<b>macOS will refuse the first launch</b> \u2014 see below.",
        "The first time you record, macOS asks for <b>microphone "
        "permission</b>. Allow it, or the app records silence.",
    ])

    F += [Paragraph("\u201cApple could not verify Vlocalhost\u201d", H2)]
    F += [Paragraph(
        "macOS blocks apps that have not been notarised by Apple, which "
        "requires a paid developer account. Until that is in place, open it "
        "manually once:", P)]
    F += steps([
        "Try to open the app. Dismiss the warning.",
        "Open <b>System Settings \u2192 Privacy &amp; Security</b>.",
        "Scroll down. There is a line naming Vlocalhost with an "
        "<b>Open Anyway</b> button. Click it.",
        "Confirm. macOS remembers, so you only do this once.",
    ])
    F += [Paragraph(
        "On older macOS the shortcut is to right-click the app and choose "
        "<b>Open</b>. That no longer works on macOS 15 and later \u2014 use "
        "System Settings.", NOTE)]

    F += [Paragraph("Recording the other people on a call", H2)]
    F += [Paragraph(
        "macOS has no built-in way to capture what your speakers are playing, "
        "so out of the box Vlocalhost records only your microphone. To capture "
        "the far end, install <b>BlackHole</b> (free, open source), route your "
        "output through it, then choose it in <b>Settings \u2192 What to "
        "listen to</b>. Windows and Linux need no such step.", P)]

    F += [Paragraph("Uninstall", H2)]
    F += [Paragraph("Drag <b>Vlocalhost</b> from Applications to the Bin. To "
                    "remove notes and settings as well:", P)]
    F += [Paragraph("~/Library/Application Support/Vlocalhost", CODE)]

    F += [PageBreak()]

    # ---------------------------------------------------------------- Linux
    F += [Paragraph("Linux", H1)]
    F += [Paragraph("<b>Coming soon.</b> The Linux archive is being packaged and tested. Everything below is how it will work; the download is not on the releases page yet. Today, both platforms run from source: see the README in the repository.", WARN)]
    F += [Paragraph("64-bit, glibc 2.35 or newer "
                    "(Ubuntu 22.04+, Debian 12+, Fedora 36+).", SMALL)]

    F += [Paragraph("Install", H2)]
    F += [Paragraph(
        "Unpack the archive into your home folder and run the install script "
        "inside it. It installs for your user only, needs no root, and adds "
        "Vlocalhost.AI to the applications menu. The exact commands are "
        "published with the build, once the build has been tested on each "
        "distribution named above.", P)]
    F += [Paragraph(
        "The microphone needs <b>libportaudio2</b>. The script names the "
        "package for your distribution rather than guessing.", NOTE)]
    F += [Paragraph("Notes and settings are kept, in "
                    "<font face='Courier'>~/.local/share/vlocalhost</font>.", P)]

    F += [PageBreak()]

    # ------------------------------------------------------------ first run
    F += [Paragraph("First run", H1)]
    F += [Paragraph(
        "The first time it opens, Vlocalhost asks two questions. Both can be "
        "changed later in <b>Settings \u2192 Models</b>, and the whole wizard "
        "can be re-run from <b>Settings \u2192 Run setup again</b>.", P)]

    F += [Paragraph("1. How accurate should transcription be?", H2)]
    F += [table([
        ["Profile", "Model", "Memory", "Best for"],
        ["Light", "tiny", "~250 MB", "Old or low-power machines, 2 cores"],
        ["Balanced", "base", "~350 MB",
         "The default. Keeps up with live speech"],
        ["Accurate", "small", "~735 MB",
         "4+ fast cores; noticeably better on Indian languages"],
    ], [26 * mm, 22 * mm, 24 * mm, 88 * mm])]
    F += [Paragraph(
        "You can also point it at your own model folder. The model downloads "
        "once, the first time you record \u2014 expect a wait of a minute or "
        "two on that first recording only.", P)]

    F += [Paragraph("2. Do you want written summaries?", H2)]
    F += [Paragraph(
        "Summaries are written by a second model running locally through "
        "<b>Ollama</b>. This is entirely optional:", P)]
    F += bullets([
        "<b>Skip it</b> and you still get a complete timestamped transcript of "
        "every meeting, saved as a .txt file. Nothing else is lost.",
        "<b>Set it up</b> and you additionally get a Markdown file with a "
        "summary, key points, decisions and action items.",
    ])
    F += [Paragraph(
        "If Ollama is not installed, get it from <b>ollama.com</b>, then "
        "return to Settings and press <b>Run setup again</b>. The wizard "
        "detects it and offers to download the summary model (about 2 GB).", P)]

    F += [Paragraph("Where your files go", H1)]
    F += [table([
        ["", "Notes and settings"],
        ["Windows", "%LOCALAPPDATA%\\Vlocalhost"],
        ["macOS", "~/Library/Application Support/Vlocalhost"],
        ["Linux", "~/.local/share/vlocalhost"],
    ], [26 * mm, 134 * mm])]
    F += [Paragraph(
        "These are deliberately outside the program folder, so updating, "
        "reinstalling or uninstalling never touches your meetings. "
        "Not sure? The app will tell you:", P)]
    F += [Paragraph("Vlocalhost --paths", CODE)]

    F += [PageBreak()]

    # ------------------------------------------------------- troubleshooting
    F += [Paragraph("Troubleshooting", H1)]
    F += [Paragraph("If your problem is not here, the support page has a form "
                    "and a way to send a diagnostic report: " + SUPPORT, P)]

    F += [section("Installing", problem(
        "Chrome: \u201cFailed \u2014 Virus scan failed\u201d",
        "Not a detection. Chrome hands the finished file to Windows to scan, "
        "and that call failed.",
        [Paragraph("Usually a third-party antivirus, a managed work laptop, or a "
                   "Defender service that is not running. Press <b>Retry</b> in "
                   "Downloads first. If it fails again, take the portable ZIP "
                   "instead \u2014 same build, no installer \u2014 or verify the file "
                   "against the SHA-256 published beside every download and keep "
                   "it.", P)]))]
    F += [problem(
        "The installer stops part-way and rolls back",
        "The folder you chose is too deep.",
        [Paragraph("Windows limits a path to 260 characters, and the files inside "
                   "the bundle are already long. An install folder beyond roughly "
                   "140 characters cannot fit. Nothing is left behind \u2014 install "
                   "again somewhere shorter, such as the default.", P)])]
    F += [problem(
        "Windows: \u201cWindows protected your PC\u201d",
        "Expected. The installer is not code-signed yet.",
        [Paragraph("Click <b>More info</b> \u2192 <b>Run anyway</b>. If the "
                   "button is missing, your workplace may block unsigned "
                   "installers \u2014 ask IT, or install from source.", P)])]
    F += [problem(
        "Windows: antivirus removed the installer",
        "Some scanners flag any unsigned installer that unpacks an "
        "interpreter.",
        [Paragraph("Restore it from quarantine and add an exclusion, or verify "
                   "the download first: each release publishes a SHA-256 "
                   "checksum, and the .sha256 file next to the download should "
                   "match what you compute locally.", P)])]
    F += [problem(
        "macOS: \u201cVlocalhost is damaged and can't be opened\u201d",
        "Misleading message. It almost always means the quarantine flag is "
        "set, not that the file is corrupt.",
        [Paragraph("Use System Settings \u2192 Privacy &amp; Security \u2192 "
                   "Open Anyway, as described in the macOS section. If that "
                   "does not appear, clear the flag directly:", P),
         Paragraph("xattr -dr com.apple.quarantine /Applications/Vlocalhost.app",
                   CODE)])]
    F += [problem(
        "macOS: the app closes instantly",
        "Usually the wrong build \u2014 an Intel bundle on Apple silicon or "
        "the reverse.",
        [Paragraph("Check the chip under Apple menu \u2192 About This Mac and "
                   "download the matching .dmg.", P)])]
    F += [problem(
        "Linux: <font face='Courier'>./install.sh: Permission denied</font>",
        "The extracted script lost its executable bit.",
        [Paragraph("bash install.sh", CODE)])]
    F += [problem(
        "Linux: <font face='Courier'>version `GLIBC_2.35' not found</font>",
        "Your distribution is older than the build.",
        [Paragraph("Install from source instead \u2014 the repository README "
                   "covers it, and it works on much older systems.", P)])]

    F += [section("Starting", problem(
        "Nothing happens when I click the icon",
        "The window failed to open and the error went nowhere, because the "
        "shortcut deliberately runs without a console.",
        [Paragraph("Run it from a terminal to see the reason:", P),
         Paragraph(
             "Windows:  \"%LOCALAPPDATA%\\Programs\\Vlocalhost\\runtime\\"
             "python.exe\" \\<br/>"
             "          \"%LOCALAPPDATA%\\Programs\\Vlocalhost\\app\\"
             "vlocalhost.py\"<br/><br/>"
             "Linux:    ~/.local/opt/vlocalhost/runtime/bin/python3 \\<br/>"
             "          ~/.local/opt/vlocalhost/app/vlocalhost.py", CODE)]))]
    F += [problem(
        "It opens in a terminal instead of a window",
        "The graphical toolkit could not start, so it fell back.",
        [Paragraph("On Linux this usually means no display is available over "
                   "SSH. The terminal mode is fully functional \u2014 press "
                   "Ctrl+C to stop and save.", P)])]

    F += [section("Recording", problem(
        "The transcript is empty, or every line is silence",
        "The microphone is muted, denied, or the wrong device.",
        [Paragraph("Check the operating system's microphone permission first "
                   "(macOS: System Settings \u2192 Privacy &amp; Security "
                   "\u2192 Microphone; Windows: Settings \u2192 Privacy "
                   "\u2192 Microphone). Then confirm the device:", P),
         Paragraph("Vlocalhost --devices", CODE)]))]
    F += [problem(
        "I can hear the other people but they are not transcribed",
        "A microphone only carries your half of a call.",
        [Paragraph("Set <b>Settings \u2192 What to listen to</b> to "
                   "<b>Both</b>. On macOS this additionally needs BlackHole "
                   "\u2014 see the macOS section.", P)])]
    F += [problem(
        "The transcript lags behind the meeting",
        "The model is too large for the machine.",
        [Paragraph("Switch to the <b>Light</b> profile in Settings \u2192 "
                   "Performance, or press <b>Benchmark this machine</b> to "
                   "measure what your hardware can actually keep up with.",
                   P)])]
    F += [problem(
        "Hindi (or another language) comes out as nonsense English",
        "An English-only model was selected.",
        [Paragraph("Models ending in <font face='Courier'>.en</font> are "
                   "English only, and they hallucinate rather than fail. "
                   "Choose a model without the suffix. The app blocks the "
                   "combination where it can.", P)])]

    F += [section("Summaries", problem(
        "The transcript saved but there is no notes file",
        "Ollama was not reachable when the recording stopped.",
        [Paragraph("The transcript is never lost to this \u2014 it is written "
                   "first, on purpose. Check the server is running by opening "
                   "this in a browser; you should see a short JSON response, "
                   "not an error:", P),
         Paragraph("http://localhost:11434/api/tags", CODE),
         Paragraph("Then <b>Settings \u2192 Models \u2192 Re-check Ollama</b>.",
                   P)]))]
    F += [problem(
        "Settings says the model is not installed, but I installed it",
        "Ollama names models with a tag, so <font face='Courier'>llama3.2"
        "</font> and <font face='Courier'>llama3.2:latest</font> are different "
        "strings.",
        [Paragraph("Press <b>List\u2026</b> next to the summarisation box. It "
                   "reads the models straight off the server, so you pick a "
                   "name that certainly exists rather than typing one.", P)])]

    F += [Paragraph("Getting help", H2)]
    F += [Paragraph(
        "Write a diagnostic report and attach it to your message. It lists "
        "your settings, versions and recent log lines \u2014 <b>no meeting "
        "audio, transcripts or notes.</b> Read it before sending; it is a "
        "plain text file.", P)]
    F += [Paragraph("Vlocalhost --diagnose", CODE)]
    F += [Paragraph(f"Support: {SUPPORT}<br/>"
                    f"Source and issues: "
                    f"https://github.com/antigravitysoham-eng/vlocalhost-core",
                    P)]

    doc.build(F)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path} ({os.path.getsize(path) / 1024:.0f} KB)")
