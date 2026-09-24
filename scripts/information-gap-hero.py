#!/usr/bin/env python3
"""Hero for difficulty-is-an-information-gap.md, rendered to PNG in both themes.

    python3 scripts/information-gap-hero.py

Needs google-chrome on PATH. Writes src/assets/images/information-gap-hero{,.dark}.png.
"""
import math, os, subprocess, tempfile

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 900

LEVELS = ["bug report", "full description", "test names", "signatures", "one hidden test", "all tests"]

THEMES = {
    "light": {"bg": "#fbfbf9", "text": "#1a1a1a", "text2": "#4b4b4b", "text3": "#8a8a85",
              "pass": "#1f5fbf", "fail": "#b6541e",
              "ramp": ["#1a4b9c", "#2566c7", "#3d80d8", "#5896e0", "#78ade9", "#9cc4f0"],
              "code": ["#ffffff"] * 4 + ["#0f2a55"] * 2},
    "dark": {"bg": "#0f1013", "text": "#e8e6e1", "text2": "#b3b0a8", "text3": "#6f6d68",
             "pass": "#7aa7ff", "fail": "#f19a5b",
             "ramp": ["#e2edfe", "#bbd1f8", "#95b4ec", "#7196da", "#5479bd", "#3b5e98"],
             "code": ["#0f1013"] * 4 + ["#ffffff"] * 2},
}


def hero(t):
    c = THEMES[t]
    cx, bottom, R = 620, 832, 392
    step = R / len(LEVELS)
    radii = [step * (k + 1) for k in range(len(LEVELS))]
    band = [bottom - (radii[k] + (radii[k - 1] if k else 0)) for k in range(len(LEVELS))]
    band[0] = bottom - radii[0]
    label_x = 1090

    out = [f'<rect width="{W}" height="{H}" fill="{c["bg"]}"/>']
    for k in reversed(range(len(LEVELS))):
        out.append(f'<circle cx="{cx}" cy="{bottom - radii[k]:.1f}" r="{radii[k]:.1f}" '
                   f'fill="{c["ramp"][k]}" stroke="{c["bg"]}" stroke-width="3"/>')

    outer_cy = bottom - R
    for k, name in enumerate(LEVELS):
        y = band[k]
        exit_x = cx + math.sqrt(max(R * R - (y - outer_cy) ** 2, 0))
        out.append(f'<text x="{cx}" y="{y + 10:.1f}" text-anchor="middle" fill="{c["code"][k]}" '
                   f'font-family="Fira Mono" font-size="30" font-weight="500">L{k + 1}</text>')
        out.append(f'<line x1="{exit_x + 14:.1f}" y1="{y:.1f}" x2="{label_x - 22}" y2="{y:.1f}" '
                   f'stroke="{c["text3"]}" stroke-width="2"/>')
        out.append(f'<circle cx="{label_x - 22}" cy="{y:.1f}" r="4" fill="{c["text3"]}"/>')
        key = k in (0, 1)
        out.append(f'<text x="{label_x}" y="{y + 11:.1f}" fill="{c["text"] if key else c["text2"]}" '
                   f'font-family="Fira Sans" font-size="36" font-weight="{600 if key else 400}">{name}</text>')

    tag_x = label_x + 320
    for k, word, color in ((0, "fails", c["fail"]), (1, "passes", c["pass"])):
        y = band[k]
        out.append(f'<text x="{tag_x}" y="{y + 10:.1f}" fill="{color}" font-family="Fira Sans" '
                   f'font-size="28" font-weight="600">{word}</text>')
    top, bot = band[1] - 8, band[0] + 8
    bx = tag_x - 22
    out.append(f'<path d="M{bx + 10} {top:.1f} H{bx} V{bot:.1f} H{bx + 10}" fill="none" '
               f'stroke="{c["text3"]}" stroke-width="2"/>')
    out.append(f'<text x="{tag_x}" y="{(top + bot) / 2 + 10:.1f}" fill="{c["text3"]}" '
               f'font-family="Fira Sans" font-size="24">certificate</text>')

    ax = 96
    y_top, y_bot = band[-1], band[0]
    out.append(f'<line x1="{ax}" y1="{y_bot:.1f}" x2="{ax}" y2="{y_top + 16:.1f}" '
               f'stroke="{c["text3"]}" stroke-width="2.5"/>')
    out.append(f'<path d="M{ax - 10} {y_top + 22:.1f} L{ax} {y_top:.1f} L{ax + 10} {y_top + 22:.1f}" '
               f'fill="none" stroke="{c["text3"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    for y, words in ((y_top, ("more information", "easier")), (y_bot, ("less information", "harder"))):
        out.append(f'<text x="{ax + 26}" y="{y + 2:.1f}" fill="{c["text2"]}" font-family="Fira Sans" '
                   f'font-size="26" font-weight="500">{words[0]}</text>')
        out.append(f'<text x="{ax + 26}" y="{y + 34:.1f}" fill="{c["text3"]}" font-family="Fira Sans" '
                   f'font-size="24">{words[1]}</text>')
    # Shrink the drawing to make room for the title across the top.
    bg, body = out[0], "".join(out[1:])
    title = (f'<text x="{W / 2}" y="68" text-anchor="middle" fill="{c["text"]}" font-family="Fira Sans" '
             f'font-size="50" font-weight="700">The Information Ladder</text>')
    return (f'<!DOCTYPE html><html><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + bg + title
            + f'<g transform="translate(88 96) scale(0.89)">{body}</g></svg></body></html>')


if __name__ == "__main__":
    for t, suffix in (("light", ""), ("dark", ".dark")):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(hero(t))
        png = os.path.join(SITE, f"src/assets/images/information-gap-hero{suffix}.png")
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={W},{H}", f"--screenshot={png}", "file://" + f.name],
                       check=True, capture_output=True)
        os.unlink(f.name)
        print("wrote", os.path.relpath(png, SITE))
