#!/usr/bin/env python3
"""Hero for what-a-2b-agent-is-missing.md, rendered to PNG in both themes.

    python3 scripts/smol-ladder-hero.py

Needs google-chrome on PATH. Writes src/assets/images/smol-ladder-hero{,.dark}.png. The drawing is
the post's finding in one glance: the same 2B model climbing from the question to the program, and
the last third, which is control.
"""
import os, subprocess, tempfile

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 900

RUNGS = [("L1", "question", 0.240), ("L2", "+ columns", 0.235), ("L3", "+ method", 0.347), ("L4", "+ program", 0.685)]

THEMES = {
    "light": {"bg": "#fbfbf9", "text": "#1a1a1a", "text2": "#4b4b4b", "text3": "#8a8a85", "line": "#d9d7d0",
              "bar": "#1f5fbf", "rest": "#e9e7e0", "fail": "#b6541e"},
    "dark": {"bg": "#0f1013", "text": "#e8e6e1", "text2": "#b3b0a8", "text3": "#6f6d68", "line": "#2a2c33",
             "bar": "#4a8fe0", "rest": "#1c1e25", "fail": "#d9752f"},
}


def hero(t):
    c = THEMES[t]
    out = [f'<rect width="{W}" height="{H}" fill="{c["bg"]}"/>']
    out.append(f'<text x="{W / 2}" y="92" text-anchor="middle" fill="{c["text"]}" font-family="Fira Sans" '
               f'font-size="52" font-weight="700">What a 2B Data Agent Is Missing</text>')
    out.append(f'<text x="{W / 2}" y="146" text-anchor="middle" fill="{c["text2"]}" font-family="Fira Sans" '
               f'font-size="30">the same model, the same 213 tasks, one more piece of the solution each rung</text>')
    x0, x1 = 300, 1340
    top, row, bh = 230, 150, 78
    for k, (rung, name, v) in enumerate(RUNGS):
        y = top + k * row
        out.append(f'<text x="{x0 - 30}" y="{y + bh / 2 + 2}" text-anchor="end" fill="{c["text"]}" '
                   f'font-family="Fira Mono" font-size="36" font-weight="500">{rung}</text>')
        out.append(f'<text x="{x0 - 30}" y="{y + bh / 2 + 40}" text-anchor="end" fill="{c["text3"]}" '
                   f'font-family="Fira Sans" font-size="26">{name}</text>')
        out.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{bh}" rx="8" fill="{c["rest"]}"/>')
        w = (x1 - x0) * v
        out.append(f'<rect x="{x0}" y="{y}" width="{w:.0f}" height="{bh}" rx="8" fill="{c["bar"]}"/>')
        out.append(f'<text x="{x0 + w + 22:.0f}" y="{y + bh / 2 + 14}" fill="{c["text"]}" font-family="Fira Mono" '
                   f'font-size="40" font-weight="500">{100 * v:.0f}%</text>')
    # The last third: control, the part training can reach.
    y = top + 3 * row
    bx = x0 + (x1 - x0) * RUNGS[-1][2] + 150
    out.append(f'<path d="M{bx} {y - 10} V{y - 34} H{x1} V{y - 10}" fill="none" stroke="{c["fail"]}" stroke-width="4"/>')
    out.append(f'<text x="{(bx + x1) / 2:.0f}" y="{y - 50}" text-anchor="middle" fill="{c["fail"]}" '
               f'font-family="Fira Sans" font-size="28" font-weight="600">left for training: control</text>')
    out.append(f'<text x="{W / 2}" y="{H - 48}" text-anchor="middle" fill="{c["text3"]}" font-family="Fira Sans" '
               f'font-size="26">Qwen3.5-2B, SmolDataEnvs test split, temperature 0</text>')
    return (f'<!DOCTYPE html><html><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(out) + '</svg></body></html>')


if __name__ == "__main__":
    for t, suffix in (("light", ""), ("dark", ".dark")):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(hero(t))
        png = os.path.join(SITE, f"src/assets/images/smol-ladder-hero{suffix}.png")
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={W},{H}", f"--screenshot={png}", "file://" + f.name],
                       check=True, capture_output=True)
        os.unlink(f.name)
        print("wrote", os.path.relpath(png, SITE))
