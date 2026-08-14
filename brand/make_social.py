#!/usr/bin/env python3
"""Profile pictures and banners for every platform, from one design.

    python brand/make_social.py

Writes into ``brand/social/``. Each platform gets the size it actually wants,
cut from the same drawing rather than a stretched export, because a banner
scaled to fit is the first thing that reads as amateur.

Design, in one line: the product's own instrument look — near-black ground,
a faint measurement grid, and a single amber oscilloscope trace that starts
flat, becomes speech, and settles again. Cyan is reserved for the claim that
matters ("on-device"), exactly as in the app.

Two variants of every banner:

    -brand    amber trace. The permanent identity.
    -launch   the trace runs saffron → white → green, for Independence Day.
              A nod, not a flag: the Flag Code is explicit about the tricolour
              itself, and a waveform that happens to carry those colours says
              "made here" without appropriating the flag for marketing.

Everything is drawn at 3× and downsampled, which is what keeps the curve and
the type crisp at 256 px.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "social")

SS = 3                                  # supersampling factor

INK = (9, 12, 18)
INK_2 = (14, 18, 32)
AMBER = (255, 180, 61)
AMBER_D = (224, 138, 23)
CYAN = (56, 225, 206)
PAPER = (234, 238, 244)
MUTED = (126, 138, 160)

SAFFRON = (255, 153, 51)
WHITE = (255, 255, 255)
GREEN = (19, 136, 8)

FONTS = r"C:\Windows\Fonts"
F_DISPLAY = os.path.join(FONTS, "segoeuib.ttf")
F_BODY = os.path.join(FONTS, "segoeui.ttf")
F_MONO = os.path.join(FONTS, "consolab.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def tricolour(t):
    """saffron → white → green across the width."""
    return lerp(SAFFRON, WHITE, t / 0.5) if t < 0.5 else lerp(WHITE, GREEN, (t - 0.5) / 0.5)


# --------------------------------------------------------------------------
def wave_points(width, mid, span, phase=0.0, swell=True):
    """The trace: flat at the edges, speech in the middle.

    Deterministic — no RNG — so a re-run produces the identical asset and a
    banner can be regenerated without silently changing.
    """
    pts = []
    step = max(1, width // 900)
    for x in range(0, width + step, step):
        u = min(1.0, x / width)
        # max(0, …): the loop can overshoot the width by one step, and a
        # negative base raised to a fractional power is a complex number.
        env = max(0.0, math.sin(u * math.pi)) ** 1.6 if swell else 1.0
        y = (math.sin(u * 22 + phase) * 0.55
             + math.sin(u * 51 - phase * 1.7) * 0.28
             + math.sin(u * 97 + phase * 0.6) * 0.17)
        # ints, not floats: Pillow 12 rejects float coordinates in draw.line
        pts.append((int(x), int(mid + y * span * env)))
    return pts


def draw_trace(img, pts, colour=None, gradient=False, width=6, glow=22):
    """Polyline with a soft glow underneath, drawn on its own layer."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if gradient:
        for i in range(len(pts) - 1):
            t = pts[i][0] / img.size[0]
            d.line([pts[i], pts[i + 1]], fill=tricolour(t) + (255,), width=width)
    else:
        d.line(pts, fill=(colour or AMBER) + (255,), width=width, joint="curve")

    if glow:
        blur = layer.filter(ImageFilter.GaussianBlur(glow))
        img.alpha_composite(Image.blend(Image.new("RGBA", img.size, (0, 0, 0, 0)), blur, 0.85))
    img.alpha_composite(layer)


def draw_grid(img, spacing, alpha=16, fade=True):
    """A faint measurement grid, faded out towards the edges."""
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, w, spacing):
        d.line([(x, 0), (x, h)], fill=(255, 255, 255, alpha), width=1)
    for y in range(0, h, spacing):
        d.line([(0, y), (w, y)], fill=(255, 255, 255, alpha), width=1)
    if fade:
        mask = Image.new("L", img.size, 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([-w * 0.15, -h * 1.2, w * 1.15, h * 2.2], fill=200)
        mask = mask.filter(ImageFilter.GaussianBlur(w // 12))
        layer.putalpha(Image.composite(layer.getchannel("A"),
                                       Image.new("L", img.size, 0), mask))
    img.alpha_composite(layer)


def ground(size):
    """Ink background with a soft top-centre lift, like the site's hero."""
    w, h = size
    img = Image.new("RGBA", size, INK + (255,))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([-w * 0.25, -h * 1.6, w * 1.25, h * 1.1], fill=INK_2 + (255,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(min(w, h) // 6)))
    return img


def mark(size, tile=True, round_tile=False):
    """The product mark: amber tile, dark oscilloscope trace.

    ``round_tile`` swaps the squircle for a circle, so the mark can sit inside
    a ring without its corners poking through it.
    """
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tile and round_tile:
        d.ellipse([s * 0.02, s * 0.02, s * 0.98, s * 0.98], fill=AMBER)
    elif tile:
        d.rounded_rectangle([s * 0.03, s * 0.03, s * 0.97, s * 0.97],
                            radius=s * 0.25, fill=AMBER)
    # The same seven-segment trace as assets/mark.svg, drawn to scale.
    path = [(0.19, 0.50), (0.28, 0.50), (0.33, 0.39), (0.39, 0.61),
            (0.45, 0.25), (0.52, 0.75), (0.58, 0.37), (0.63, 0.53),
            (0.67, 0.47), (0.81, 0.47)]
    d.line([(x * s, y * s) for x, y in path], fill=(11, 15, 24, 255),
           width=int(s * 0.055), joint="curve")
    return img.resize((size, size), Image.LANCZOS)


def chips(d, x, y, items, f, pad=None, gap=None):
    """Row of outlined mono chips. Returns the x it ended at."""
    pad = pad or int(f.size * 0.85)
    gap = gap or int(f.size * 0.9)
    for text in items:
        w = d.textlength(text, font=f)
        h = f.size * 1.05
        d.rounded_rectangle([x, y, x + w + pad * 2, y + h + pad],
                            radius=(h + pad) / 2, outline=CYAN + (150,), width=max(1, SS))
        d.text((x + pad, y + pad * 0.45), text, font=f, fill=CYAN)
        x += w + pad * 2 + gap
    return x


# --------------------------------------------------------------------------
def banner(size, launch=False, tagline=None, safe_left=0, compact=False):
    """Three zones that never overlap: identity top-left, claims bottom-right,
    and the trace as a signal floor beneath both.

    The first cut put the chips at the same height as the wordmark and ran the
    tagline through the loudest part of the wave. Everything here is placed
    from measured text widths rather than guessed offsets.
    """
    w, h = size[0] * SS, size[1] * SS
    img = ground((w, h))
    draw_grid(img, spacing=int(h / 6), alpha=14)

    # ---- the trace, low and wide: a floor, not a backdrop for type ---------
    mid = int(h * (0.86 if not compact else 0.80))
    span = h * (0.11 if not compact else 0.13)
    pts = wave_points(w, mid, span, phase=1.1)
    draw_trace(img, pts, gradient=launch, width=max(3, int(h * 0.014)),
               glow=int(h * 0.045))

    d = ImageDraw.Draw(img)
    left = int(safe_left * SS) + int(w * 0.04)

    # ---- identity, top-left -----------------------------------------------
    m = int(h * (0.34 if compact else 0.30))
    top = int(h * (0.16 if compact else 0.14))
    img.alpha_composite(mark(m), (left, top))

    f_name = font(F_DISPLAY, int(h * (0.34 if compact else 0.30)))
    tx = left + m + int(h * 0.09)
    ty = top + int(m * 0.5) - int(f_name.size * 0.62)
    d.text((tx, ty), "Vlocalhost", font=f_name, fill=PAPER)
    nw = d.textlength("Vlocalhost", font=f_name)
    d.text((tx + nw, ty), ".AI", font=f_name, fill=AMBER)

    if tagline:
        f_tag = font(F_MONO, int(h * (0.10 if compact else 0.085)))
        d.text((tx + int(h * 0.01), top + m + int(h * 0.04)), tagline,
               font=f_tag, fill=MUTED)

    # ---- claims, bottom-right, clear of the avatar cut-out -----------------
    if not compact:
        f_chip = font(F_MONO, int(h * 0.058))
        items = ["ON-DEVICE", "0 BYTES UPLOADED", "OPEN SOURCE"]
        pad, gap = int(f_chip.size * 0.85), int(f_chip.size * 0.9)
        total = sum(d.textlength(t, font=f_chip) + pad * 2 + gap for t in items) - gap
        chips(d, int(w - total - w * 0.04), int(h * 0.60), items, f_chip,
              pad=pad, gap=gap)
        f_url = font(F_MONO, int(h * 0.05))
        url = "antigravitysoham-eng.github.io/vlocalhost-ai"
        d.text((w - d.textlength(url, font=f_url) - w * 0.04, int(h * 0.79)),
               url, font=f_url, fill=MUTED)

    return img.resize(size, Image.LANCZOS).convert("RGB")


def profile(size, launch=False):
    """Square avatar. The tile is the logo; at 64 px nothing else survives.

    The launch variant adds one thin tricolour ring. Colour runs with the
    *angle*, not the radius — colouring by radius (the first attempt) draws a
    fat rainbow donut that eats the mark and reads as clip art.
    """
    s = size * SS
    img = Image.new("RGBA", (s, s), INK + (255,))
    if launch:
        d = ImageDraw.Draw(img)
        ring = max(2, int(s * 0.035))
        inset = int(s * 0.02)
        box = [inset, inset, s - inset, s - inset]
        radius = (s - inset * 2) / 2.0
        cx = cy = s / 2.0
        for a in range(0, 360, 2):
            # Colour by height, not by angle. Running the gradient round the
            # circumference puts saffron and green on opposite *sides*, which
            # reads as neither — the flag stacks top to bottom, so the ring
            # should too: saffron across the top, white at the waist, green
            # along the bottom.
            mid = math.radians(a + 1)
            y = cy + math.sin(mid) * radius
            t = min(1.0, max(0.0, (y - (cy - radius)) / (radius * 2)))
            d.arc(box, a, a + 3, fill=tricolour(t) + (255,), width=ring)
    inner = int(s * (0.855 if launch else 0.94))
    img.alpha_composite(mark(inner, round_tile=launch),
                        ((s - inner) // 2, (s - inner) // 2))
    return img.resize((size, size), Image.LANCZOS).convert("RGB")


def square_card(size, launch=True):
    """A 1080 post card for Instagram."""
    w = h = size * SS
    img = ground((w, h))
    draw_grid(img, spacing=int(h / 12), alpha=14)
    pts = wave_points(w, int(h * 0.52), h * 0.10, phase=0.6)
    draw_trace(img, pts, gradient=launch, width=int(h * 0.008), glow=int(h * 0.03))

    d = ImageDraw.Draw(img)
    m = int(h * 0.15)
    img.alpha_composite(mark(m), ((w - m) // 2, int(h * 0.16)))

    f_name = font(F_DISPLAY, int(h * 0.085))
    f_line = font(F_DISPLAY, int(h * 0.052))
    f_tag = font(F_MONO, int(h * 0.026))

    def centre(text, f, y, fill):
        d.text(((w - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)

    centre("Vlocalhost.AI", f_name, int(h * 0.335), PAPER)
    centre("Meeting notes that never", f_line, int(h * 0.60), PAPER)
    centre("leave your machine.", f_line, int(h * 0.665), AMBER)
    centre("MADE IN INDIA  ·  ON-DEVICE  ·  FREE", f_tag, int(h * 0.79), CYAN)
    centre("link in bio  ·  windows today", f_tag, int(h * 0.855), MUTED)
    return img.resize((size, size), Image.LANCZOS).convert("RGB")


TAG = "meeting notes that never leave your machine"
TAG_LAUNCH = "made in india  ·  your voice stays yours"


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []

    # profile pictures — every platform wants a different square
    for name, px in (("x", 400), ("instagram", 320), ("reddit", 256),
                     ("linkedin", 300), ("master", 1024)):
        for variant, launch in (("brand", False), ("launch", True)):
            p = os.path.join(OUT, f"pfp-{name}-{variant}.png")
            profile(px, launch).save(p)
            made.append(p)

    # banners, each at its platform's real size and safe area
    specs = [
        ("x-header", (1500, 500), 0, False),          # avatar overlaps lower-left
        ("linkedin-page-cover", (1128, 191), 200, True),
        ("linkedin-personal-cover", (1584, 396), 0, False),
        ("reddit-banner", (1920, 384), 0, True),
        ("youtube-channel-art", (2048, 512), 0, False),
    ]
    for name, size, safe, compact in specs:
        for variant, launch in (("brand", False), ("launch", True)):
            tag = TAG_LAUNCH if launch else TAG
            p = os.path.join(OUT, f"{name}-{variant}.png")
            banner(size, launch=launch, tagline=tag, safe_left=safe,
                   compact=compact).save(p, quality=95)
            made.append(p)

    p = os.path.join(OUT, "instagram-launch-card.png")
    square_card(1080).save(p, quality=95)
    made.append(p)

    for path in made:
        kb = os.path.getsize(path) / 1024
        print(f"  {os.path.relpath(path, HERE):48s} {kb:6.0f} KB")
    print(f"\n{len(made)} files in brand/social/")


if __name__ == "__main__":
    main()
