#!/usr/bin/env python3
"""The installation guide, written once.

This module holds the guide as data. ``make_install_guide.py`` renders it twice
— to a PDF that ships inside the download, and to an HTML page on the site — so
the two can never drift. Editing either output by hand means the next
regeneration silently discards the change; edit this file instead.

Inline markup is deliberately tiny: ``<b>`` for emphasis and ``<code>`` for
anything the reader types or a path they look for. Both renderers understand
those two and nothing else, which keeps a wording change from becoming a
layout change.
"""

VERSION = "1.1.1"
SITE = "https://antigravitysoham-eng.github.io/vlocalhost-ai/"
SUPPORT = SITE + "support/"
GUIDE_URL = SITE + "install/guide/"
RELEASES = "https://github.com/antigravitysoham-eng/vlocalhost-core/releases/latest"
REPO = "https://github.com/antigravitysoham-eng/vlocalhost-core"

TAGLINE = "Your Voice Hosted Locally"
BLURB = ("Meeting notes that never leave your machine. Windows, macOS and "
         "Linux — installing, first run, and what to do when something "
         "goes wrong.")


# --- block constructors ----------------------------------------------------
# Each returns a plain tuple so the renderers can switch on the first element
# and nothing has to import anything from the other renderer.

def P(text):                 return ("p", text)
def H2(text):                return ("h2", text)
def LEAD(text):              return ("lead", text)
def STEPS(items):            return ("steps", items)
def BULLETS(items):          return ("bullets", items)
def CODE(text):              return ("code", text)
def NOTE(text):              return ("note", text)
def WARN(text):              return ("warn", text)
def TABLE(head, rows, widths): return ("table", (head, rows, widths))
def PROBLEM(title, cause, body): return ("problem", (title, cause, body))


# --- the guide -------------------------------------------------------------
# (anchor, title, standfirst, blocks)

SECTIONS = [

 ("before-you-start", "Before you start", "What the download needs from you.", [
    LEAD("Less than you would expect. The installer carries its own Python and "
         "every library it needs, so there is nothing to install first."),
    TABLE(None, [
        ["Disk space", "About 400 MB, plus ~150 MB the first time you record, "
                       "when the speech model downloads."],
        ["Microphone", "Any built-in one is fine."],
        ["Internet", "For the download only. Nothing is sent afterwards."],
        ["Account", "None. There is no sign-in."],
        ["Ollama", "Optional — only if you want written summaries as well as "
                   "transcripts."],
    ], [30, 130]),
    NOTE("Audio and transcripts never leave your computer. Without Ollama you "
         "still get a complete, timestamped transcript of every meeting."),
 ]),

 ("windows", "Windows", "Windows 10 or 11, 64-bit.", [
    H2("Install"),
    STEPS([
        f"Download <code>vlocalhost-{VERSION}-windows-x64-setup.exe</code> "
        "from the downloads page.",
        "Double-click it.",
        "<b>Windows will show a blue “Windows protected your PC” screen.</b> "
        "This is expected — see the note below. Click <b>More info</b>, then "
        "<b>Run anyway</b>.",
        "Choose where to install it. The default sits inside your user folder "
        "and needs no administrator rights. Any drive works — "
        "<code>D:\\Apps\\Vlocalhost</code> is fine.",
        "Leave <b>Create a desktop shortcut</b> ticked if you want one.",
        "Click <b>Install</b>, then <b>Finish</b>. The app opens and asks two "
        "setup questions.",
    ]),
    WARN("<b>Why the warning appears.</b> Windows shows that screen for any "
         "program without a paid code-signing certificate. It is not a virus "
         "warning and says nothing about the file's contents. Vlocalhost is "
         "open source — you can read every line of what the installer puts on "
         "your machine. A signed build is planned."),
    NOTE("The installer needs no administrator password, so it works on a "
         "locked-down work laptop."),

    H2("Or: the portable ZIP"),
    P(f"Every release also ships <code>vlocalhost-{VERSION}-windows-x64.zip</code>: "
      "the same build with no installer. Take this one if a virus scanner "
      "refuses the .exe, if Chrome reports “Virus scan failed”, or if you want "
      "nothing written outside a single folder."),
    STEPS([
        "Unpack the .zip anywhere you can write. Keep the path short — a "
        "folder buried deeper than about 140 characters cannot unpack "
        "cleanly, because the files inside are already long.",
        "Open the folder and run <code>Vlocalhost.cmd</code>.",
        "That is the whole install. Nothing is written outside this folder.",
    ]),
    P("<b>No desktop icon?</b> Correct — the ZIP deliberately touches nothing "
      "outside its own folder. A helper in the folder does it for you:"),
    CODE("Create desktop shortcut.cmd"),
    NOTE("It adds Vlocalhost.AI to your desktop and Start menu, pointing at "
         "the copy you unpacked, and finds the real desktop folder even when "
         "OneDrive has moved it."),

    H2("Uninstall"),
    P("<b>Settings → Apps → Installed apps → Vlocalhost.AI → Uninstall</b>, or "
      "use the shortcut in the Start menu folder. Your meeting notes and "
      "settings are deliberately kept. To remove those too, delete this "
      "folder afterwards:"),
    CODE("%LOCALAPPDATA%\\Vlocalhost"),
    P("The portable ZIP has no uninstaller — that is what portable means. "
      "Delete the folder you unpacked, and run <code>Remove desktop "
      "shortcut.cmd</code> first if you made shortcuts."),
 ]),

 ("macos", "macOS", "macOS 12 Monterey or newer.", [
    WARN("<b>Coming soon.</b> The Apple silicon and Intel builds are packaged "
         "and tested but not yet published to the releases page. Everything "
         "below is how it will work. Today, macOS runs from source — see the "
         "README in the repository."),

    H2("Pick the right build"),
    P("Apple menu → <b>About This Mac</b>, and look at the chip:"),
    TABLE(["Your Mac says", "Download"], [
        ["Apple M1 / M2 / M3 / M4", f"vlocalhost-{VERSION}-macos-arm64.dmg"],
        ["Intel", f"vlocalhost-{VERSION}-macos-x64.dmg"],
    ], [55, 105]),

    H2("Install"),
    STEPS([
        "Download the .dmg and double-click it.",
        "Drag <b>Vlocalhost</b> onto the <b>Applications</b> folder in the "
        "window that opens.",
        "Eject the disk image, then open <b>Vlocalhost</b> from Applications "
        "or Launchpad.",
        "<b>macOS will refuse the first launch</b> — see below.",
        "The first time you record, macOS asks for <b>microphone "
        "permission</b>. Allow it, or the app records silence.",
    ]),

    H2("“Apple could not verify Vlocalhost”"),
    P("macOS blocks apps that have not been notarised by Apple, which requires "
      "a paid developer account. Until that is in place, open it manually "
      "once:"),
    STEPS([
        "Try to open the app. Dismiss the warning.",
        "Open <b>System Settings → Privacy &amp; Security</b>.",
        "Scroll down. There is a line naming Vlocalhost with an "
        "<b>Open Anyway</b> button. Click it.",
        "Confirm. macOS remembers, so you only do this once.",
    ]),
    NOTE("On older macOS the shortcut was to right-click the app and choose "
         "<b>Open</b>. That no longer works on macOS 15 and later — use "
         "System Settings."),

    H2("Recording the other people on a call"),
    P("macOS has no built-in way to capture what your speakers are playing, so "
      "out of the box Vlocalhost records only your microphone. To capture the "
      "far end, install <b>BlackHole</b> (free, open source), route your "
      "output through it, then choose it in <b>Settings → What to listen "
      "to</b>. Windows and Linux need no such step."),

    H2("Uninstall"),
    P("Drag <b>Vlocalhost</b> from Applications to the Bin. To remove notes "
      "and settings as well:"),
    CODE("~/Library/Application Support/Vlocalhost"),
 ]),

 ("linux", "Linux",
  "64-bit, glibc 2.35 or newer (Ubuntu 22.04+, Debian 12+, Fedora 36+).", [
    WARN("<b>Coming soon.</b> The Linux archive is packaged but not yet "
         "published to the releases page. Today, Linux runs from source — see "
         "the README in the repository."),
    P("Unpack the archive into your home folder and run the install script "
      "inside it. It installs for your user only, needs no root, and adds "
      "Vlocalhost.AI to the applications menu. The exact commands ship with "
      "the build, once that build has been tested on each distribution named "
      "above."),
    NOTE("The microphone needs <b>libportaudio2</b>. The script names the "
         "package for your distribution rather than guessing."),
    P("Notes and settings are kept in <code>~/.local/share/vlocalhost</code>."),
 ]),

 ("first-run", "First run", "Two questions, both changeable later.", [
    P("The first time it opens, Vlocalhost asks two questions. Both can be "
      "changed in <b>Settings → Models</b>, and the whole wizard can be re-run "
      "from <b>Settings → Run setup again</b>."),

    H2("1. How accurate should transcription be?"),
    TABLE(["Profile", "Model", "Memory", "Best for"], [
        ["Light", "tiny", "~250 MB", "Old or low-power machines, 2 cores"],
        ["Balanced", "base", "~350 MB", "The default. Keeps up with live speech"],
        ["Accurate", "small", "~735 MB",
         "4+ fast cores; noticeably better on Indian languages"],
    ], [26, 22, 24, 88]),
    P("You can also point it at your own model folder. The model downloads "
      "once, the first time you record — expect a wait of a minute or two on "
      "that recording only."),

    H2("2. Do you want written summaries?"),
    P("Summaries are written by a second model running locally through "
      "<b>Ollama</b>. This is entirely optional:"),
    BULLETS([
        "<b>Skip it</b> and you still get a complete timestamped transcript of "
        "every meeting, saved as a .txt file. Nothing else is lost.",
        "<b>Set it up</b> and you additionally get a Markdown file with a "
        "summary, key points, decisions and action items.",
    ]),
    P("If Ollama is not installed, get it from <b>ollama.com</b>, then return "
      "to Settings and press <b>Run setup again</b>. The wizard detects it and "
      "offers to download the summary model (about 2 GB)."),

    H2("Where your files live"),
    TABLE(None, [
        ["Windows", "%LOCALAPPDATA%\\Vlocalhost"],
        ["macOS", "~/Library/Application Support/Vlocalhost"],
        ["Linux", "~/.local/share/vlocalhost"],
    ], [26, 134]),
    P("These sit deliberately outside the program folder, so updating, "
      "reinstalling or uninstalling never touches your meetings. Not sure? "
      "The app will tell you:"),
    CODE("Vlocalhost --paths"),
 ]),

 ("troubleshooting", "Troubleshooting",
  "The failures people actually hit, and what each one means.", [
    H2("Installing"),
    PROBLEM("Chrome: “Failed — Virus scan failed”",
            "Not a detection. Chrome hands the finished file to Windows to "
            "scan, and that call failed.",
            [P("Usually a third-party antivirus, a managed work laptop, or a "
               "Defender service that is not running. Press <b>Retry</b> in "
               "Downloads first. If it fails again, take the portable ZIP "
               "instead — same build, no installer — or verify the file "
               "against the SHA-256 published beside every download.")]),
    PROBLEM("The installer stops part-way and rolls back",
            "The folder you chose is too deep.",
            [P("Windows limits a path to 260 characters, and the files inside "
               "the bundle are already long. An install folder beyond roughly "
               "140 characters cannot fit. Nothing is left behind — install "
               "again somewhere shorter, such as the default.")]),
    PROBLEM("Windows: antivirus removed the installer",
            "Some scanners flag any unsigned installer that unpacks an "
            "interpreter.",
            [P("Restore it from quarantine and add an exclusion, or verify the "
               "download first: each release publishes a SHA-256 checksum, and "
               "the .sha256 file next to the download should match what you "
               "compute locally.")]),
    PROBLEM("macOS: “Vlocalhost is damaged and can't be opened”",
            "Misleading message. It almost always means the quarantine flag "
            "is set, not that the file is corrupt.",
            [P("Use System Settings → Privacy &amp; Security → Open Anyway, as "
               "described in the macOS section. If that does not appear, clear "
               "the flag directly:"),
             CODE("xattr -dr com.apple.quarantine /Applications/Vlocalhost.app")]),
    PROBLEM("macOS: the app closes instantly",
            "Usually the wrong build — an Intel bundle on Apple silicon, or "
            "the reverse.",
            [P("Check the chip under Apple menu → About This Mac and download "
               "the matching .dmg.")]),
    PROBLEM("Linux: <code>version `GLIBC_2.35' not found</code>",
            "Your distribution is older than the build.",
            [P("Install from source instead — the repository README covers it, "
               "and it works on much older systems.")]),

    H2("Starting"),
    PROBLEM("Nothing happens when I click the icon",
            "The window failed to open and the error went nowhere, because "
            "the shortcut deliberately runs without a console.",
            [P("Run it from a terminal to see the reason:"),
             CODE("\"%LOCALAPPDATA%\\Programs\\Vlocalhost\\runtime\\python.exe\" "
                  "\"%LOCALAPPDATA%\\Programs\\Vlocalhost\\app\\vlocalhost.py\"")]),
    PROBLEM("It opens in a terminal instead of a window",
            "The graphical toolkit could not start, so it fell back.",
            [P("On Linux this usually means no display is available over SSH. "
               "The terminal mode is fully functional — press Ctrl+C to stop "
               "and save.")]),

    H2("Recording"),
    PROBLEM("The transcript is empty, or every line is silence",
            "The microphone is muted, denied, or the wrong device.",
            [P("Check the operating system's microphone permission first "
               "(macOS: System Settings → Privacy &amp; Security → Microphone; "
               "Windows: Settings → Privacy → Microphone). Then confirm the "
               "device:"),
             CODE("Vlocalhost --devices")]),
    PROBLEM("I can hear the other people but they are not transcribed",
            "A microphone only carries your half of a call.",
            [P("Set <b>Settings → What to listen to</b> to <b>Both</b>. On "
               "macOS this additionally needs BlackHole — see the macOS "
               "section.")]),
    PROBLEM("The transcript lags behind the meeting",
            "The model is too large for the machine.",
            [P("Switch to the <b>Light</b> profile in Settings → Performance, "
               "or press <b>Benchmark this machine</b> to measure what your "
               "hardware can actually keep up with.")]),
    PROBLEM("Hindi (or another language) comes out as nonsense English",
            "An English-only model was selected.",
            [P("Models ending in <code>.en</code> are English only, and they "
               "hallucinate rather than fail. Choose a model without the "
               "suffix. The app blocks the combination where it can.")]),

    H2("Summaries"),
    PROBLEM("The transcript saved but there is no notes file",
            "Ollama was not reachable when the recording stopped.",
            [P("The transcript is never lost to this — it is written first, on "
               "purpose. Check the server is running by opening this in a "
               "browser; you should see a short JSON response, not an error:"),
             CODE("http://localhost:11434/api/tags"),
             P("Then <b>Settings → Models → Re-check Ollama</b>.")]),
    PROBLEM("Settings says the model is not installed, but I installed it",
            "Ollama names models with a tag, so <code>llama3.2</code> and "
            "<code>llama3.2:latest</code> are different strings.",
            [P("Press <b>List…</b> next to the summarisation box. It reads the "
               "models straight off the server, so you pick a name that "
               "certainly exists rather than typing one.")]),
 ]),

 ("help", "Getting help", "What to send, and where.", [
    P("Write a diagnostic report and attach it to your message. It lists your "
      "settings, versions and recent log lines — <b>no meeting audio, "
      "transcripts or notes.</b> Read it before sending; it is a plain text "
      "file."),
    CODE("Vlocalhost --diagnose"),
    TABLE(None, [
        ["Support", SUPPORT],
        ["Downloads", RELEASES],
        ["Source and issues", REPO],
    ], [34, 126]),
 ]),
]
