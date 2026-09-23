#!/usr/bin/env python3
"""Figures for difficulty-is-an-information-gap.md.

    python3 scripts/information-gap-figures.py            # snapshot the ledger, then render
    python3 scripts/information-gap-figures.py --render   # render from the committed snapshot

The snapshot needs the research repo (RESEARCH_REPO, default ../open_swe_traces_research).
Rendering needs only docs/data/information-gap-snapshot.json. Every colour is a CSS variable
from src/styles.css, so one SVG serves both themes.
"""
import collections, datetime, glob, json, os, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
RESEARCH = os.environ.get("RESEARCH_REPO", os.path.join(os.path.dirname(SITE), "open_swe_traces_research"))
SNAPSHOT = os.path.join(SITE, "docs/data/information-gap-snapshot.json")
OUT = os.path.join(SITE, "src/_includes/figures/information-gap")

# The authoring census lives outside the trial ledger; restate it here when it moves.
AUTHORED = 591

# The ledger numbers the bug report rung 0 and keeps an unused partial-description rung 1.
# The post numbers the bug report L1, so every label goes through post_level.
LEVELS = ["0", "2", "3", "4", "5", "6"]
LEVEL_NAME = {"0": "bug report", "2": "full description",
              "3": "test names", "4": "signatures", "5": "one test", "6": "all tests"}


def post_level(rung):
    return "1" if rung == "0" else rung
MODEL = {"composer": "Composer", "devin": "Devin", "grok": "Grok"}
MODEL_COLOR = {"composer": "var(--chart-1)", "devin": "var(--chart-2)", "grok": "var(--chart-3)"}

CURVE_GROUPS = [
    ("Composer and Devin: Devin needs less", ("composer", "devin"),
     ["gin-clientip", "client-go-memdbstaging", "ipqueue", "archive", "defval", "rootval"]),
    ("Composer and Devin: Composer needs less", ("composer", "devin"),
     ["advrefs", "helm-searchindex", "namescope"]),
    ("Composer and Devin: same level", ("composer", "devin"), ["httperrexpr"]),
    ("Composer and Grok: the top of the ladder", ("composer", "grok"),
     ["httpmux", "httpencoding", "exprhash"]),
]
# The cut keeps exported signatures, and nearly every task has one hidden test file, so on
# most tasks L4 is the L3 task and L6 is the L5 task. Charts read them as one step.
STEPS = [("L1", ("0",), "bug report"), ("L2", ("2",), "full description"),
         ("L3–4", ("3", "4"), "test names"), ("L5–6", ("5", "6"), "the test file")]
DISPLAY = {"client-go-memdbstaging": "memdbstaging"}


# ---------------------------------------------------------------- snapshot

GRADE_STEPS = ["L1", "L2", "L3–4", "L5–6", "none"]
GRADE_OF = {"0": 0, "2": 1, "3": 2, "4": 2, "5": 3, "6": 3}


def grade(rungs):
    """The first step a model passed, 4 when it failed through the test file, None if unfinished."""
    passed = sorted(GRADE_OF[r] for r, v in rungs.items() if r in GRADE_OF and v and max(v) > 0)
    if passed:
        return passed[0]
    return 4 if rungs.get("5") or rungs.get("6") else None


def joint_grades(bys):
    """Composer's grade against Devin's on every task both models graded, and Kendall's tau-b."""
    pairs = []
    for d in bys.values():
        if "composer" in d and "devin" in d:
            c, v = grade(d["composer"]), grade(d["devin"])
            if c is not None and v is not None:
                pairs.append((c, v))
    cells = collections.Counter(f"{c}-{v}" for c, v in pairs)
    conc = disc = tie_c = tie_v = 0
    for i, (a, b) in enumerate(pairs):
        for c, v in pairs[i + 1:]:
            s = (a - c) * (b - v)
            conc += s > 0
            disc += s < 0
            tie_c += a == c
            tie_v += b == v
    n0 = len(pairs) * (len(pairs) - 1) / 2
    tau = (conc - disc) / ((n0 - tie_c) * (n0 - tie_v)) ** 0.5 if pairs else 0.0
    return {"cells": dict(cells), "n": len(pairs), "tau_b": round(tau, 2)}


def snapshot():
    sys.path.insert(0, os.path.join(RESEARCH, "scripts/ops"))
    os.chdir(RESEARCH)
    import trial_ledger as T

    s = T.summary()
    certs = T.certificates()
    bys = T.ledger_by_solver()

    first_pass = collections.Counter(str(v["rung"]) for v in certs.values())
    first_pass["0"] = len(s["too_easy"])

    runs = collections.defaultdict(collections.Counter)
    for t in T.trials():
        if t["reward"] is None or t["errored"]:
            continue
        runs[t["rung"]][T.solver_of(t["model"])] += 1

    agree = collections.Counter()
    for d in bys.values():
        c, v = d.get("composer", {}).get("0"), d.get("devin", {}).get("0")
        if c and v:
            agree[f"{'pass' if max(c) > 0 else 'fail'}-{'pass' if max(v) > 0 else 'fail'}"] += 1

    joint = joint_grades(bys)

    curves = {}
    for _, models, bases in CURVE_GROUPS:
        for b in bases:
            curves[b] = {m: {r: [sum(1 for x in v if x > 0), len(v)] for r, v in rr.items() if v}
                         for m, rr in bys[b].items() if m in models}

    snap = {
        "date": datetime.date.today().isoformat(),
        "funnel": {"authored": AUTHORED, "trialled": s["units"],
                   "decided": len(certs) + len(s["too_easy"]) + len(s["nonflip"]),
                   "certified": len(certs), "too_easy": len(s["too_easy"]),
                   "unresolved": len(s["nonflip"])},
        "first_pass": dict(first_pass),
        "unresolved": s["nonflip"],
        "runs": {r: dict(c) for r, c in sorted(runs.items())},
        "l0_agreement": dict(agree),
        "curves": curves,
        "joint": joint,
        "words": prompt_words(),
    }
    os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
    with open(SNAPSHOT, "w") as f:
        json.dump(snap, f, indent=1, sort_keys=True)
    return snap


def prompt_words():
    """Median prompt length at the bug report, and the median per-task increase at each level above.

    Levels are compared within a task, never across the population at each level: the
    upper levels are only staged for tasks that failed lower down, whose descriptions run
    longer, so population medians mix the two effects."""
    boiler = [re.compile(r"Work in `/app`\..*?work only from the repository\.", re.S),
              re.compile(r"IMPORTANT: This repository is fully self-contained\..*?test output\.", re.S)]

    def words(text):
        for b in boiler:
            text = b.sub("", text)
        return len(text.split())

    latest = collections.defaultdict(dict)
    for f in glob.glob(os.path.join(RESEARCH, "experiments/dose_response/*/*/instruction.md")):
        m = re.match(r"(.+)-L(\d)$", os.path.basename(os.path.dirname(f)))
        if not m:
            continue
        base, rung = m.groups()
        t = os.path.getmtime(f)
        if base not in latest[rung] or latest[rung][base][1] < t:
            latest[rung][base] = (words(open(f).read()), t)

    w = {r: {b: v[0] for b, v in d.items()} for r, d in latest.items()}
    out = {"L0": statistics.median(w["0"].values()), "n0": len(w["0"])}
    for lo, hi in zip(LEVELS, LEVELS[1:]):
        both = [b for b in w[lo] if b in w[hi]]
        out[f"d{hi}"] = statistics.median(w[hi][b] - w[lo][b] for b in both)
        out[f"n{hi}"] = len(both)
    out["gin-clientip"] = [w["0"]["gin-clientip"], w["2"]["gin-clientip"]]
    return out


# ---------------------------------------------------------------- svg helpers

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def num(n):
    return f"{n:,}" if isinstance(n, int) else f"{n:g}"


def text(x, y, s, size=20, fill="var(--text)", anchor="start", weight=400, mono=False, extra=""):
    fam = "var(--font-mono)" if mono else "var(--font-sans)"
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    w = f' font-weight="{weight}"' if weight != 400 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}"{a} fill="{fill}" font-size="{size}"{w} '
            f'font-family="{fam}"{extra}>{esc(s)}</text>')


def rect(x, y, w, h, fill, title=None, rx=3, extra=""):
    t = f"<title>{esc(title)}</title>" if title else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{h:.1f}" '
            f'rx="{min(rx, w / 2, h / 2):.1f}" fill="{fill}"{extra}>{t}</rect>')


def line(x1, y1, x2, y2, stroke="var(--line)", width=1, extra=""):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{extra}/>')


def svg(h, label, body, anim=None):
    a = f' data-anim="{anim}"' if anim else ""
    return (f'<svg viewBox="0 0 720 {h:.0f}" role="img"{a} aria-label="{esc(label)}">\n'
            + "\n".join(body) + "\n</svg>\n")


def level_label(x, y, r, size=20, name=True):
    out = [text(x, y, f"L{post_level(r)}", size, weight=700, mono=True)]
    if name:
        out.append(text(x + 38, y, LEVEL_NAME[r], size - 2, "var(--text-2)"))
    return out


# ---------------------------------------------------------------- figures

def fig_prompt_words(s):
    """Typical prompt length at each level. The prompt stops growing after L3."""
    w = s["words"]
    x0, scale, row, bh = 230, 300 / 600, 46, 22
    body = []
    for t in (0, 200, 400, 600):
        x = x0 + t * scale
        body.append(line(x, 18, x, 18 + row * 6, "var(--line)"))
        body.append(text(x, 18 + row * 6 + 26, num(t), 16, "var(--text-3)", "middle", mono=True))
    total = 0
    notes = {"4": "+ stubs, already in place", "5": "+ the test file", "6": "+ any other test files"}
    for i, r in enumerate(LEVELS):
        y = 24 + i * row
        total += w["L0"] if r == "0" else w[f"d{r}"]
        body += level_label(0, y + bh - 5, r)
        body.append(rect(x0, y, total * scale, bh, "var(--chart-1)", f"L{post_level(r)}: about {num(total)} words"))
        end = x0 + total * scale + 10
        body.append(text(end, y + bh - 4, num(total), 19, weight=700, mono=True))
        if r in notes:
            body.append(text(end + 50, y + bh - 5, notes[r], 16, "var(--chart-2)"))
    body.append(text(x0 + 150, 18 + row * 6 + 54, "words in the prompt", 17, "var(--text-2)", "middle"))
    label = (f"Prompt length by level. The bug report is about {num(w['L0'])} words, the full "
             f"description about {num(w['L0'] + w['d2'])}, and test names add {num(w['d3'])}. "
             f"Above L3 the prompt stays the same and the levels add files to the repository.")
    return svg(18 + row * 6 + 66, label, body, "x")


def fig_funnel(s):
    f = s["funnel"]
    rows = [("authored", f["authored"], None),
            ("trialled", f["trialled"], f"{num(f['authored'] - f['trialled'])} not yet run"),
            ("graded", f["decided"], f"{num(f['trialled'] - f['decided'])} still without a verdict")]
    x0, scale, row, bh = 130, 380 / f["authored"], 56, 34
    body = []
    for i, (name, n, note) in enumerate(rows):
        y = 16 + i * row
        body.append(text(x0 - 16, y + bh - 10, name, 20, anchor="end"))
        body.append(rect(x0, y, n * scale, bh, "var(--chart-1)", f"{name}: {num(n)}",
                         extra=f' fill-opacity="{(0.3, 0.6, 1)[i]}"'))
        end = x0 + n * scale + 10
        body.append(text(end, y + bh - 9, num(n), 21, weight=700, mono=True))
        if note:
            body.append(text(end + 12 + 11.5 * len(num(n)), y + bh - 10, note, 16, "var(--text-3)"))
    label = (f"{num(f['authored'])} tasks authored, {num(f['trialled'])} trialled, "
             f"{num(f['decided'])} graded on the ladder.")
    return svg(16 + row * len(rows) - 6, label, body, "x")


def fig_first_pass(s):
    """Where each graded task first passed, for the model that graded it."""
    fp = s["first_pass"]
    rows = [(name, lvls, desc, sum(fp.get(r, 0) for r in lvls)) for name, lvls, desc in STEPS]
    rows.append(("none", (), "no level yet", len(s["unresolved"])))
    peak = max(r[3] for r in rows)
    x0, scale, row, bh = 250, 300 / peak, 42, 24
    body = []
    for i, (name, lvls, desc, n) in enumerate(rows):
        y = 12 + i * row
        body.append(text(0, y + bh - 5, name, 20, "var(--text)" if lvls else "var(--text-2)", weight=700, mono=True))
        body.append(text(76, y + bh - 5, desc, 18, "var(--text-2)"))
        fill = f"var(--lvl-{post_level(lvls[-1])})" if lvls else "var(--text-3)"
        body.append(rect(x0, y, max(n * scale, 2), bh, fill, f"{name}: {n}"))
        body.append(text(x0 + max(n * scale, 2) + 10, y + bh - 4, num(n), 19, weight=700, mono=True))
    cert = sum(r[3] for r in rows[1:4])
    bx, top, bot = 640, 12 + row + 2, 12 + row * 3 + bh - 2
    body.append(f'<path d="M{bx - 8} {top} H{bx} V{bot} H{bx - 8}" fill="none" '
                f'stroke="var(--text-2)" stroke-width="1.5"/>')
    body.append(text(bx + 10, (top + bot) / 2 + 2, num(cert), 20, weight=700, mono=True))
    body.append(text(bx + 10, (top + bot) / 2 + 22, "certified", 15, "var(--text-2)"))
    label = "Lowest level each graded task passed at. " + ", ".join(f"{r[0]} {r[3]}" for r in rows) + "."
    return svg(12 + row * len(rows) - 4, label, body, "x")


def glyph(x, y, color, passed, tip):
    t = f"<title>{esc(tip)}</title>"
    if passed:
        return f'<circle cx="{x}" cy="{y}" r="8.5" fill="{color}">{t}</circle>'
    return (f'<circle cx="{x}" cy="{y}" r="7.5" fill="var(--bg)" stroke="{color}" '
            f'stroke-width="2">{t}</circle>')


def fig_curves(s):
    """One lane per model per task. The tinted track runs from the bug report to the first
    pass: how much information the model needed."""
    cols = [310 + i * 112 for i in range(len(STEPS))]
    end_x = cols[-1]
    lane, gap, head = 28, 14, 38
    body = [text(x, 22, name, 17, "var(--text-2)", "middle", 700, True) for x, (name, _, _) in zip(cols, STEPS)]
    body += [glyph(8, 16, "var(--text-2)", True, "passed"), text(22, 21, "passed", 15, "var(--text-2)"),
             glyph(96, 16, "var(--text-2)", False, "failed"), text(110, 21, "failed", 15, "var(--text-2)")]
    y = 44
    for gi, (group, models, bases) in enumerate(CURVE_GROUPS):
        y += 10 if gi else 0
        body.append(text(0, y + 20, group.upper(), 13, "var(--text-3)", weight=600,
                         extra=' letter-spacing="0.08em"'))
        body.append(line(0, y + 30, 720, y + 30))
        y += head
        for b in bases:
            present = [m for m in models if m in s["curves"][b]]
            for li, m in enumerate(present):
                cy = y + li * lane + lane / 2
                d = s["curves"][b][m]
                color = MODEL_COLOR[m]
                if li == 0:
                    body.append(text(0, cy + 6, DISPLAY.get(b, b), 17, weight=600, mono=True))
                body.append(text(262, cy + 6, MODEL[m], 16, color, "end", 600))
                body.append(line(cols[0], cy, end_x, cy, "var(--line)", 2))
                cells = []
                for (name, lvls, _), x in zip(STEPS, cols):
                    got = [d[r] for r in lvls if r in d]
                    cells.append((x, name, sum(g[0] for g in got), sum(g[1] for g in got)))
                ran = [c for c in cells if c[3]]
                first = next((c for c in cells if c[2]), None)
                reach = first or ran[-1]
                if reach[0] > cols[0]:
                    body.append(line(cols[0], cy, reach[0], cy, color, 8,
                                     ' stroke-opacity="0.22" stroke-linecap="round"'))
                for x, name, p, n in cells:
                    if not n:
                        body.append(f'<circle cx="{x}" cy="{cy}" r="2" fill="var(--text-3)" fill-opacity="0.6"/>')
                    else:
                        body.append(glyph(x, cy, color, p > 0, f"{MODEL[m]} on {b}, {name}: {p} of {n} passed"))
                if not first:
                    body.append(text(end_x + 20, cy + 5, "none", 15, "var(--text-3)"))
            y += len(present) * lane + gap
    label = ("Ladder results for thirteen tasks run by two models. On six, Devin passes at a lower "
             "level than Composer, and on three Composer passes lower than Devin. On httperrexpr both "
             "pass at L2. With the test file in the tree, Grok passes httpmux and httpencoding in one "
             "run of two and Composer in none. Nobody passes exprhash.")
    return svg(y + 2, label, body)


def fig_l0_agreement(s):
    a = s["l0_agreement"]
    get = lambda c, d: a.get(f"{c}-{d}", 0)
    total = sum(a.values())
    x0, y0, cell = 250, 64, 150
    peak = max(a.values())
    body = [text(x0 + cell / 2, 26, "Devin passed", 17, "var(--chart-2)", "middle", 600),
            text(x0 + cell * 1.5, 26, "Devin failed", 17, "var(--chart-2)", "middle", 600),
            text(x0 + cell, 48, "on the bug report", 15, "var(--text-3)", "middle")]
    for ri, c in enumerate(("pass", "fail")):
        cy = y0 + ri * cell + cell / 2
        body.append(text(x0 - 18, cy - 2, f"Composer {'passed' if c == 'pass' else 'failed'}", 17,
                         "var(--chart-1)", "end", 600))
        body.append(text(x0 - 18, cy + 18, "on the bug report", 15, "var(--text-3)", "end"))
        for ci, d in enumerate(("pass", "fail")):
            n = get(c, d)
            cx = x0 + ci * cell + cell / 2
            body.append(rect(x0 + ci * cell, y0 + ri * cell, cell, cell, "none", rx=0,
                             extra=' stroke="var(--line)" stroke-width="1.5"'))
            side = (cell - 62) * (n / peak) ** 0.5
            agree = c == d
            fill = "var(--chart-1)" if agree else "var(--chart-2)"
            if n:
                body.append(rect(cx - side / 2, cy - side / 2 - 16, side, side, fill,
                                 f"Composer {c}, Devin {d}: {n}", rx=2))
            body.append(text(cx, y0 + (ri + 1) * cell - 12, num(n), 20,
                             "var(--text)" if n else "var(--text-3)", "middle", 700, True))
    nx = x0 + 2 * cell + 26
    body.append(text(nx, y0 + 22, f"{num(total)} tasks", 20, weight=700))
    body.append(text(nx, y0 + 46, "screened by both", 16, "var(--text-2)"))
    body.append(text(nx, y0 + cell + 52, f"{num(get('fail', 'pass'))} disagreements,", 16, "var(--text-2)"))
    body.append(text(nx, y0 + cell + 74, f"Devin passed all {num(get('fail', 'pass'))}", 16, "var(--text-2)"))
    label = (f"{total} tasks screened at the bug report by Composer and Devin. Both failed "
             f"{get('fail', 'fail')}, both passed {get('pass', 'pass')}, only Devin passed "
             f"{get('fail', 'pass')}, only Composer passed {get('pass', 'fail')}.")
    return svg(y0 + 2 * cell + 8, label, body)


def fig_joint(s):
    j = s["joint"]
    get = lambda c, v: j["cells"].get(f"{c}-{v}", 0)
    n = len(GRADE_STEPS)
    x0, y0, cell = 170, 70, 100
    peak = max(j["cells"].values())
    body = [text(x0 + n * cell / 2, 22, "Devin's first pass", 17, "var(--chart-2)", "middle", 600)]
    for i, name in enumerate(GRADE_STEPS):
        body.append(text(x0 + i * cell + cell / 2, 52, name, 16, "var(--text-2)", "middle", 600, True))
        body.append(text(x0 - 16, y0 + i * cell + cell / 2 + 6, name, 16, "var(--text-2)", "end", 600, True))
    body.append(text(20, y0 + n * cell / 2 - 10, "Composer's", 17, "var(--chart-1)", weight=600))
    body.append(text(20, y0 + n * cell / 2 + 12, "first pass", 17, "var(--chart-1)", weight=600))
    for ci in range(n):
        for vi in range(n):
            k = get(ci, vi)
            x, y = x0 + vi * cell, y0 + ci * cell
            same = ci == vi
            body.append(rect(x, y, cell, cell, "var(--bg-2)" if same else "none", rx=0,
                             extra=' stroke="var(--line)" stroke-width="1.5"'))
            if k:
                side = (cell - 34) * (k / peak) ** 0.5
                who = "same level" if same else ("Devin needs less" if vi < ci else "Composer needs less")
                body.append(rect(x + cell / 2 - side / 2, y + cell / 2 - side / 2 - 8, side, side,
                                 "var(--chart-1)" if same else "var(--chart-2)",
                                 f"Composer {GRADE_STEPS[ci]}, Devin {GRADE_STEPS[vi]}: {k} ({who})", rx=2,
                                 extra="" if same or vi < ci else ' fill-opacity="0.45"'))
            body.append(text(x + cell / 2, y + cell - 10, num(k), 17,
                             "var(--text)" if k else "var(--text-3)", "middle", 700, True))
    same = sum(get(i, i) for i in range(n))
    lower_d = sum(get(c, v) for c in range(n) for v in range(n) if v < c)
    lower_c = sum(get(c, v) for c in range(n) for v in range(n) if c < v)
    label = (f"Where Composer and Devin first pass, on the {j['n']} tasks both graded. The same level "
             f"on {same}. Devin passes lower on {lower_d} and Composer lower on {lower_c}. "
             f"Kendall's tau-b between the two grades is {j['tau_b']}.")
    return svg(y0 + n * cell + 8, label, body)


def fig_runs(s):
    runs = s["runs"]
    lv = sorted(r for r in runs if r in LEVELS)
    totals = {r: sum(runs[r].values()) for r in lv}
    base, top = 250, 40
    scale = (base - top) / max(totals.values())
    bw, step, x0 = 64, 104, 84
    body = [line(40, base, 700, base, "var(--line)", 1.5)]
    for i, r in enumerate(lv):
        x = x0 + i * step
        y = base
        for m in ("composer", "devin", "grok"):
            n = runs[r].get(m, 0)
            if not n:
                continue
            h = n * scale
            body.append(rect(x, y - h, bw, h, MODEL_COLOR[m], f"L{post_level(r)}, {MODEL[m]}: {n} runs", rx=0))
            y -= h
        body.append(text(x + bw / 2, y - 10, num(totals[r]), 19, anchor="middle", weight=700, mono=True))
        key = r in ("0", "2")
        body.append(text(x + bw / 2, base + 30, f"L{post_level(r)}", 20, "var(--text)" if key else "var(--text-2)",
                         "middle", 700, True))
    for lx, m in ((450, "composer"), (560, "devin"), (640, "grok")):
        body.append(rect(lx, 10, 14, 14, MODEL_COLOR[m], rx=2))
        body.append(text(lx + 20, 22, MODEL[m], 16, "var(--text-2)"))
    above = sum(totals[r] for r in lv if r not in ("0", "2"))
    label = (f"Runs with a verdict per level, stacked by model. L1 {totals.get('0', 0)}, "
             f"L2 {totals.get('2', 0)}, L3 to L6 {above} together.")
    return svg(base + 44, label, body, "y")


def fig_runs_per_cert(_s):
    rows = [("parallel, no gate", 9.0, False), ("sequential, no gate", 7.7, False),
            ("sequential, gated", 3.2, True)]
    x0, scale, row, bh = 230, 400 / 9.0, 54, 32
    body = []
    for i, (name, v, key) in enumerate(rows):
        y = 16 + i * row
        body.append(text(x0 - 16, y + bh - 9, name, 20, anchor="end"))
        body.append(rect(x0, y, v * scale, bh, "var(--chart-1)", f"{name}: {v}",
                         extra="" if key else ' fill-opacity="0.35"'))
        body.append(text(x0 + v * scale + 10, y + bh - 8, f"{v:.1f}", 21, weight=700, mono=True))
    fx = x0 + 2 * scale
    body.append(line(fx, 6, fx, 16 + row * 3 - 8, "var(--chart-2)", 2, ' stroke-dasharray="4 4"'))
    body.append(text(fx + 8, 16 + row * 3 + 12, "floor of 2", 16, "var(--chart-2)"))
    body.append(text(x0 + 200, 16 + row * 3 + 40, "runs per certificate", 17, "var(--text-2)", "middle"))
    label = "Runs needed per certificate: parallel with no gate 9.0, sequential with no gate 7.7, sequential with a gate 3.2, against a floor of 2."
    return svg(16 + row * 3 + 50, label, body, "x")


FIGURES = {
    "prompt-words": fig_prompt_words,
    "funnel": fig_funnel,
    "first-pass": fig_first_pass,
    "curves": fig_curves,
    "bug-report-agreement": fig_l0_agreement,
    "joint-grades": fig_joint,
    "runs-per-level": fig_runs,
    "runs-per-certificate": fig_runs_per_cert,
}


def render(s):
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FIGURES.items():
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(fn(s))
    print(f"rendered {len(FIGURES)} figures from the {s['date']} snapshot into {os.path.relpath(OUT, SITE)}")


if __name__ == "__main__":
    if "--render" in sys.argv:
        render(json.load(open(SNAPSHOT)))
    else:
        render(snapshot())
