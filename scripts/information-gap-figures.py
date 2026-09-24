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
LEVEL_NAME = {"0": "Bug report", "2": "Full description",
              "3": "Test names", "4": "Signatures", "5": "One test", "6": "All tests"}


def post_level(rung):
    return "1" if rung == "0" else rung
MODEL = {"composer": "Composer", "devin": "SWE-2", "grok": "Grok"}
MODEL_COLOR = {"composer": "var(--chart-1)", "devin": "var(--chart-2)", "grok": "var(--chart-3)"}

CURVE_GROUPS = [
    ("go-git", ("composer", "devin"), ["archive", "advrefs"]),
    ("goa", ("composer", "devin"), ["defval", "httperrexpr", "httpmux"]),
    ("nats-server", ("composer", "devin"), ["ipqueue"]),
]
# The tasks Grok ran on as a top-of-ladder probe; its pilot elsewhere is left out.
GROK_PROBE = {"httpmux", "httpencoding", "exprhash"}
# A lane beyond the group's models, where the text relies on it.
CURVE_EXTRA = {}
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


def information_gradient(bys, first_pass, graded):
    """Share of graded tasks solved by each ladder step, cumulative: all tasks at the level
    their grading model first passed, and each model's own grades. A task passed at one
    level counts as solved at every level above it, the ladder's nesting."""
    def cumulative(counts, n):
        out, run = [], 0
        for step in range(4):
            run += counts.get(step, 0)
            out.append(round(100 * run / n, 1))
        return out

    pooled = collections.Counter()
    for rung, n in first_pass.items():
        if rung in GRADE_OF:
            pooled[GRADE_OF[rung]] += n
    out = {"all": {"n": graded, "share": cumulative(pooled, graded)}}
    for m in ("composer", "devin"):
        grades = [grade(d[m]) for d in bys.values() if m in d]
        grades = [g for g in grades if g is not None]
        out[m] = {"n": len(grades), "share": cumulative(collections.Counter(grades), len(grades))}
    return out


def joint_grades(bys):
    """Composer's grade against SWE-2's on every task both models graded, and Kendall's tau-b."""
    pairs, bases = [], []
    for base, d in bys.items():
        if "composer" in d and "devin" in d:
            c, v = grade(d["composer"]), grade(d["devin"])
            if c is not None and v is not None:
                pairs.append((c, v))
                bases.append(base)
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
    return {"cells": dict(cells), "n": len(pairs), "tau_b": round(tau, 2),
            "by_length": by_description_length(bases, pairs)}


def trace_lengths():
    """Tool calls per graded trial, quartiles by model and verdict, from the research repo's
    trace reader (openswe_traces.analysis.traces --rows). It runs in its own process because
    the ledger import above has already bound openswe_traces to the research checkout's src;
    RESEARCH_SRC points it at another copy of the package."""
    import subprocess
    src = os.environ.get("RESEARCH_SRC", os.path.join(RESEARCH, "src"))
    out = subprocess.run([sys.executable, "-m", "openswe_traces.analysis.traces", "--rows"],
                         cwd=RESEARCH, env={**os.environ, "PYTHONPATH": src},
                         capture_output=True, text=True, check=True).stdout

    rows = [json.loads(line) for line in out.splitlines() if line.strip()]
    groups = collections.defaultdict(list)
    minutes = collections.defaultdict(list)
    for r in rows:
        key = f"{r['model']}-{'pass' if r['passed'] else 'fail'}"
        groups[key].append(r["calls"])
        if r["minutes"] is not None:
            minutes[r["model"]].append(r["minutes"])
    out = {}
    for key, xs in groups.items():
        q = statistics.quantiles(xs, n=4)
        out[key] = {"n": len(xs), "q1": q[0], "median": statistics.median(xs), "q3": q[2]}
    out["minutes"] = {m: round(statistics.median(v), 1) for m, v in minutes.items()}
    out["by_step"] = trace_steps(rows)
    out["flips"] = trace_flips(rows)
    return out


TRACE_STEP = {"0": "L1", "2": "L2", "3": "L3–4", "4": "L3–4", "5": "L5–6", "6": "L5–6"}


def trace_steps(rows):
    """Median tool calls for passed and failed runs at each ladder step, per model."""
    g = collections.defaultdict(list)
    for r in rows:
        g[(r["model"], TRACE_STEP[r["rung"]], "pass" if r["passed"] else "fail")].append(r["calls"])
    return {f"{m}|{s}|{v}": {"n": len(xs), "median": statistics.median(xs)} for (m, s, v), xs in g.items()}


def trace_flips(rows):
    """Same model and task: the failed run just below the first pass, against that pass."""
    fam = collections.defaultdict(list)
    for r in rows:
        fam[(r["model"], r["base"])].append(r)
    pairs = collections.defaultdict(list)
    for (m, _), g in fam.items():
        passes = [r for r in g if r["passed"]]
        if not passes:
            continue
        p = min(passes, key=lambda r: int(r["rung"]))
        lower = [r for r in g if not r["passed"] and int(r["rung"]) < int(p["rung"])]
        if lower:
            pairs[m].append((max(lower, key=lambda r: int(r["rung"])), p))
    explore = lambda r: (r["read"] + r["search"]) / r["calls"]
    return {m: {"tasks": len(ps),
                "calls": [statistics.median(f["calls"] for f, _ in ps), statistics.median(p["calls"] for _, p in ps)],
                "explore_calls": [statistics.median(f["read"] + f["search"] for f, _ in ps),
                                  statistics.median(p["read"] + p["search"] for _, p in ps)],
                "explore": [round(statistics.median(explore(f) for f, _ in ps), 3),
                            round(statistics.median(explore(p) for _, p in ps), 3)]}
            for m, ps in pairs.items()}


def by_description_length(bases, pairs):
    """Agreement by full-description (L2) length, in thirds of the jointly graded tasks.

    Lengths come from the features the pipeline recorded when it staged each unit."""
    words = {}
    for line in open(os.path.join(RESEARCH, "outputs/unit_features.jsonl")):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("rung") == "2" and r.get("instr_words"):
            words[r["base"]] = r["instr_words"]
    have = sorted((words[b], c, v) for b, (c, v) in zip(bases, pairs) if b in words)
    third = len(have) // 3
    groups = [have[:third], have[third:2 * third], have[2 * third:]]
    return [{"from": g[0][0], "to": g[-1][0], "same": sum(c == v for _, c, v in g),
             "devin_lower": sum(v < c for _, c, v in g), "composer_lower": sum(c < v for _, c, v in g)}
            for g in groups]


def snapshot():
    sys.path.insert(0, os.path.join(RESEARCH, "scripts/ops"))
    os.chdir(RESEARCH)
    import trial_ledger as T

    # Grok is in the post only as the top-of-ladder probe. Its other trials were a pilot
    # from wiring up its harness, so every count here leaves them out. The ledger's own
    # functions all read trials(), so scoping that one function scopes them all.
    all_trials = T.trials

    def probe_scoped(jobs_dir=T.JOBS):
        for t in all_trials(jobs_dir):
            if T.solver_of(t["model"]) == "grok" and t["base"] not in GROK_PROBE:
                continue
            yield t

    T.trials = probe_scoped

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
    gradient = information_gradient(bys, first_pass, len(certs) + len(s["too_easy"]) + len(s["nonflip"]))
    traces = trace_lengths()

    curves = {}
    for _, models, bases in CURVE_GROUPS:
        for b in bases:
            curves[b] = {m: {r: [sum(1 for x in v if x > 0), len(v)] for r, v in rr.items() if v}
                         for m, rr in bys[b].items() if m in models + CURVE_EXTRA.get(b, ())}

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
        "gradient": gradient,
        "traces": traces,
        "words": prompt_words(),
        "repo_lines": repo_lines(),
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


def repo_lines():
    """Median lines of hidden test code sitting in the repository at each level: none through
    L4 (the stubs were already there), one hidden test file at L5, every hidden test at L6.
    Counted from the staged task's own tree, newest copy per task."""
    latest = collections.defaultdict(dict)
    for d in glob.glob(os.path.join(RESEARCH, "experiments/dose_response/*/*-L[56]/")):
        m = re.match(r"(.+)-L([56])$", os.path.basename(d.rstrip("/")))
        hid = os.path.join(d, "tests/hidden")
        if not m or not os.path.isdir(hid):
            continue
        base, rung = m.groups()
        n = 0
        for f in glob.glob(os.path.join(hid, "**/*_test.go"), recursive=True):
            shown = os.path.join(d, "environment/src", os.path.relpath(f, hid))
            if os.path.exists(shown):
                n += sum(1 for _ in open(shown, errors="replace"))
        t = os.path.getmtime(d)
        if n and (base not in latest[rung] or latest[rung][base][1] < t):
            latest[rung][base] = (n, t)
    out = {r: 0 for r in ("0", "2", "3", "4")}
    for r in ("5", "6"):
        out[r] = statistics.median(v[0] for v in latest[r].values())
        out["n" + r] = len(latest[r])
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

def rotated(x, y, s, size=15, fill="var(--text-2)"):
    """A y-axis title, reading bottom to top."""
    return text(x, y, s, size, fill, "middle", extra=f' transform="rotate(-90 {x:.1f} {y:.1f})"')


def x_axis(x0, x1, y, ticks, sx, fmt, title, tick_size=14):
    """Baseline, tick labels under it, and a title centred below."""
    out = [line(x0, y, x1, y, "var(--text-3)", 1.5)]
    for t in ticks:
        out.append(line(sx(t), y, sx(t), y + 5, "var(--text-3)", 1.5))
        out.append(text(sx(t), y + 22, fmt(t), tick_size, "var(--text-3)", "middle", mono=True))
    out.append(text((x0 + x1) / 2, y + 46, title, 15, "var(--text-2)", "middle"))
    return out


def y_axis(x, y0, y1, title, title_x=None):
    """Vertical axis line from y0 (top) to y1 (bottom) and a rotated title."""
    return [line(x, y0, x, y1, "var(--text-3)", 1.5),
            rotated(title_x if title_x is not None else x - 56, (y0 + y1) / 2, title)]


def fig_prompt_words(s):
    """What each level adds, as one grouped bar chart with two x axes: words in the prompt
    (bottom axis, blue) and lines of hidden test code in the repository (top axis, orange)."""
    w, lines = s["words"], s["repo_lines"]
    x0, width = 200, 400
    top, row, bh = 78, 50, 16
    y_end = top + row * 6
    wmax, lmax = 600, 500
    sxw = lambda v: x0 + width * v / wmax
    sxl = lambda v: x0 + width * v / lmax
    body = []
    for t in (0, 150, 300, 450, 600):
        body.append(line(sxw(t), top - 8, sxw(t), y_end, "var(--line)"))
    # top axis: lines of test code
    body.append(line(x0, top - 8, x0 + width, top - 8, "var(--chart-2)", 1.5))
    for t in (0, 125, 250, 375, 500):
        body.append(line(sxl(t), top - 13, sxl(t), top - 8, "var(--chart-2)", 1.5))
        body.append(text(sxl(t), top - 20, num(t), 14, "var(--chart-2)", "middle", mono=True))
    body.append(text(x0 + width / 2, top - 44, "Lines of Test Code in the Repository", 15, "var(--chart-2)", "middle", 600))
    total = 0
    for i, r in enumerate(LEVELS):
        y = top + i * row + 6
        total += w["L0"] if r == "0" else w[f"d{r}"]
        body += level_label(0, y + bh + 4, r, 17)
        body.append(rect(x0, y, sxw(total) - x0, bh, "var(--chart-1)",
                         f"L{post_level(r)}: about {num(round(total))} words in the prompt"))
        body.append(text(sxw(total) + 8, y + bh - 3, num(round(total)), 14, "var(--chart-1)", weight=700, mono=True))
        n = lines[r]
        y2 = y + bh + 2
        if n:
            body.append(rect(x0, y2, sxl(n) - x0, bh, "var(--chart-2)",
                             f"L{post_level(r)}: about {num(round(n))} lines of test code in the repository"))
            body.append(text(sxl(n) + 8, y2 + bh - 3, num(round(n)), 14, "var(--chart-2)", weight=700, mono=True))
        else:
            body.append(text(x0 + 8, y2 + bh - 3, "0", 13, "var(--text-3)", mono=True))
    # bottom axis: words in the prompt; y axis: ladder level
    body.append(line(x0, top - 8, x0, y_end, "var(--text-3)", 1.5))
    body.append(line(x0, y_end, x0 + width, y_end, "var(--chart-1)", 1.5))
    for t in (0, 150, 300, 450, 600):
        body.append(line(sxw(t), y_end, sxw(t), y_end + 5, "var(--chart-1)", 1.5))
        body.append(text(sxw(t), y_end + 22, num(t), 14, "var(--chart-1)", "middle", mono=True))
    body.append(text(x0 + width / 2, y_end + 46, "Words in the Prompt", 15, "var(--chart-1)", "middle", 600))
    label = (f"What each level adds, one pair of bars per level. Words in the prompt grow from about "
             f"{num(round(w['L0']))} at the bug report to about {num(round(w['L0'] + w['d2'] + w['d3']))} with "
             f"the test names and then hold steady. Lines of hidden test code in the repository are zero "
             f"through L4, about {num(round(lines['5']))} at L5, and about {num(round(lines['6']))} at L6.")
    return svg(y_end + 58, label, body, "x")


def fig_funnel(s):
    f = s["funnel"]
    rows = [("Authored", f["authored"], None),
            ("Trialled", f["trialled"], f"{num(f['authored'] - f['trialled'])} never ran"),
            ("Graded", f["decided"], f"{num(f['trialled'] - f['decided'])} no verdict")]
    x0, width, row, bh, top = 130, 380, 50, 30, 12
    sx = lambda v: x0 + width * v / 600
    body = []
    for i, (name, n, note) in enumerate(rows):
        y = top + i * row
        body.append(text(x0 - 14, y + bh - 9, name, 18, anchor="end"))
        body.append(rect(x0, y, sx(n) - x0, bh, "var(--chart-1)", f"{name}: {num(n)}",
                         extra=f' fill-opacity="{(0.3, 0.6, 1)[i]}"'))
        end = sx(n) + 10
        body.append(text(end, y + bh - 8, num(n), 19, weight=700, mono=True))
        if note:
            body.append(text(end + 12 + 10.5 * len(num(n)), y + bh - 9, note, 15, "var(--text-3)"))
    y_end = top + row * len(rows) - 8
    body.append(line(x0, top - 4, x0, y_end, "var(--text-3)", 1.5))
    body += x_axis(x0, x0 + width, y_end, (0, 200, 400, 600), sx, num, "tasks")
    label = (f"{num(f['authored'])} tasks authored, {num(f['trialled'])} trialled, "
             f"{num(f['decided'])} graded on the ladder.")
    return svg(y_end + 56, label, body, "x")


# Graded and certified tasks per source repository, from the ledger joined to each task's
# Harbor base image (ladder-base:<repo>). Four graded tasks with no recorded image, all too
# easy, are left out, so the rows sum to 407 graded rather than 411.
REPO_YIELD = [("kops", 70, 56), ("go-git", 68, 50), ("goa", 35, 26), ("nats-server", 29, 21),
              ("client-go", 21, 14), ("bbolt", 52, 29), ("helm", 26, 13), ("gin", 40, 16),
              ("go-github", 66, 17)]


def fig_repos(s):
    x0, width, row, bh, top = 150, 360, 40, 24, 44
    sx = lambda v: x0 + width * v / 80
    body = [rect(x0, 6, 16, 16, "var(--chart-1)"), text(x0 + 24, 20, "Certified", 15, "var(--text-2)"),
            rect(x0 + 120, 6, 16, 16, "var(--chart-1)", extra=' fill-opacity="0.3"'),
            text(x0 + 144, 20, "Too easy (passed the bug report)", 15, "var(--text-2)")]
    for i, (repo, graded, cert) in enumerate(REPO_YIELD):
        y = top + i * row
        body.append(text(x0 - 14, y + bh - 7, repo, 16, anchor="end", weight=600, mono=True))
        body.append(rect(x0, y, sx(cert) - x0, bh, "var(--chart-1)", f"{repo}: {cert} certified", rx=0))
        body.append(rect(sx(cert), y, sx(graded) - sx(cert), bh, "var(--chart-1)",
                         f"{repo}: {graded - cert} too easy", rx=0, extra=' fill-opacity="0.3"'))
        body.append(text(sx(graded) + 10, y + bh - 7, f"{cert}/{graded}", 15, "var(--text-2)", mono=True))
        body.append(text(x0 + width + 150, y + bh - 7, f"{round(100 * cert / graded)}%", 17,
                         weight=700, anchor="end", mono=True))
    y_end = top + row * len(REPO_YIELD) - 8
    body.append(text(x0 + width + 150, top - 10, "% Certified", 14, "var(--text-3)", "end"))
    body.append(line(x0, top - 4, x0, y_end, "var(--text-3)", 1.5))
    body += x_axis(x0, x0 + width, y_end, (0, 20, 40, 60, 80), sx, num, "Graded Tasks")
    label = ("Certified and too-easy tasks per repository: "
             + ", ".join(f"{r} {c}/{g}" for r, g, c in REPO_YIELD) + ".")
    return svg(y_end + 56, label, body, "x")


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
    body = [text((cols[0] + cols[-1]) / 2, 16, "Ladder Step", 15, "var(--text-2)", "middle")]
    body += [text(x, 40, name, 17, "var(--text-2)", "middle", 700, True) for x, (name, _, _) in zip(cols, STEPS)]
    body += [glyph(8, 34, "var(--text-2)", True, "passed"), text(22, 39, "Passed", 15, "var(--text-2)"),
             glyph(96, 34, "var(--text-2)", False, "failed"), text(110, 39, "Failed", 15, "var(--text-2)")]
    body.append(line(cols[0] - 30, 50, end_x + 30, 50, "var(--text-3)", 1.5))
    y = 62
    for gi, (group, models, bases) in enumerate(CURVE_GROUPS):
        y += 10 if gi else 0
        body.append(text(0, y + 20, group.upper(), 13, "var(--text-3)", weight=600,
                         extra=' letter-spacing="0.08em"'))
        body.append(line(0, y + 30, 720, y + 30))
        y += head
        for b in bases:
            present = [m for m in models + CURVE_EXTRA.get(b, ()) if m in s["curves"][b]]
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
    body.append(line(cols[0] - 30, 50, cols[0] - 30, y - gap, "var(--text-3)", 1.5))
    label = ("Ladder results for six tasks, one lane per model, by ladder step. On archive, defval and "
             "ipqueue SWE-2 passes at a lower level than Composer, and on advrefs Composer passes lower. "
             "On httperrexpr both pass at L2. On httpmux Composer fails through the test "
             "names and passes once the test file is in the tree.")
    return svg(y + 2, label, body, "r")


def fig_gradient(s):
    g = s["gradient"]
    words = s["words"]
    steps = [("L1", "Bug report", f"{words['L0']:.0f} words"),
             ("L2", "Full description", f"+{words['d2']:.0f} words"),
             ("L3–4", "Test names", f"+{words['d3']:.0f} words"),
             ("L5–6", "Test file", "+ a test file")]
    x0, x1, y0, h = 120, 570, 36, 280
    xs = [x0 + 30 + i * (x1 - x0 - 60) / 3 for i in range(4)]
    sy = lambda v: y0 + h - h * v / 100
    body = []
    for tick in range(0, 101, 25):
        body.append(line(x0, sy(tick), x1, sy(tick), "var(--line)", 1))
        body.append(text(x0 - 10, sy(tick) + 5, f"{tick}%", 14, "var(--text-3)", "end", mono=True))
    body += [line(x0, y0 - 8, x0, y0 + h, "var(--text-3)", 1.5), line(x0, y0 + h, x1, y0 + h, "var(--text-3)", 1.5),
             rotated(34, y0 + h / 2, "Share of Graded Tasks Solved")]
    for x, (lv, name, add) in zip(xs, steps):
        body.append(text(x, y0 + h + 26, lv, 17, "var(--text)", "middle", 700, True))
        body.append(text(x, y0 + h + 46, name, 14, "var(--text-2)", "middle"))
        body.append(text(x, y0 + h + 64, add, 13, "var(--text-3)", "middle", mono=True))
    body.append(text((x0 + x1) / 2, y0 + h + 92, "Ladder Step", 15, "var(--text-2)", "middle"))
    lines = (("all", "All tasks", "var(--text)", 3.5, ""),
             ("composer", "Composer", MODEL_COLOR["composer"], 2.5, ' stroke-dasharray="6 5"'),
             ("devin", "SWE-2", MODEL_COLOR["devin"], 2.5, ' stroke-dasharray="6 5"'))
    for key, name, color, width, dash in lines:
        pts = [(x, sy(v)) for x, v in zip(xs, g[key]["share"])]
        body.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" '
                    f'stroke="{color}" stroke-width="{width}"{dash}/>')
        for (x, y), v in zip(pts, g[key]["share"]):
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 if key == "all" else 4}" fill="{color}">'
                        f'<title>{esc(name)}: {v}% solved</title></circle>')
    a = g["all"]["share"]
    for x, v in zip(xs, a):
        shown = f"{v:.1f}%" if 99.5 <= v < 100 else f"{v:.0f}%"
        body.append(text(x, sy(v) - 14, shown, 16, weight=700, anchor="middle", mono=True))
    jump = a[1] - a[0]
    body.append(text((xs[0] + xs[1]) / 2 + 30, sy((a[0] + a[1]) / 2) + 30, f"+{jump:.0f} points", 16,
                     "var(--text-2)", weight=700))
    ly = sy(a[0]) + 44
    for i, (key, name, color, _, dash) in enumerate(lines):
        yy = ly + i * 22
        body.append(f'<line x1="{x1 - 150}" y1="{yy - 5}" x2="{x1 - 124}" y2="{yy - 5}" stroke="{color}" '
                    f'stroke-width="3"{dash}/>')
        body.append(text(x1 - 116, yy, f"{name} ({g[key]['n']})", 15, "var(--text-2)"))
    label = ("Share of graded tasks solved by each ladder step. All tasks: "
             + ", ".join(f"{lv} {v}%" for (lv, _, _), v in zip(steps, a))
             + f". Composer: {', '.join(f'{v}%' for v in g['composer']['share'])}. "
             + f"SWE-2: {', '.join(f'{v}%' for v in g['devin']['share'])}.")
    return svg(y0 + h + 104, label, body)


def fig_length(s):
    rows = s["joint"]["by_length"]
    names = ["Shortest third", "Middle third", "Longest third"]
    x0, bar, gap, width, top = 230, 40, 22, 330, 14
    sx = lambda v: x0 + width * v / 100
    body = []
    parts = (("same", "Same level", "var(--chart-1)", ""),
             ("devin_lower", "SWE-2 needs less", "var(--chart-2)", ""),
             ("composer_lower", "Composer needs less", "var(--chart-2)", ' fill-opacity="0.45"'))
    for i, (r, name) in enumerate(zip(rows, names)):
        y = top + i * (bar + gap)
        total = r["same"] + r["devin_lower"] + r["composer_lower"]
        body.append(text(x0 - 16, y + 18, name, 17, anchor="end", weight=600))
        body.append(text(x0 - 16, y + 37, f"{r['from']}–{r['to']} words", 14, "var(--text-3)", "end"))
        x = x0
        for key, label, color, extra in parts:
            w = width * r[key] / total
            if w:
                body.append(rect(x, y, w, bar, color, f"{name}: {label} {r[key]} of {total}", rx=0, extra=extra))
            x += w
        body.append(text(x0 + width + 12, y + 27, f"{round(100 * r['same'] / total)}% agree", 16,
                         weight=700, mono=True))
    y_end = top + 3 * (bar + gap) - gap + 6
    body.append(line(x0, top - 4, x0, y_end, "var(--text-3)", 1.5))
    body.append(rotated(24, (top + y_end) / 2, "Full Description Length"))
    body += x_axis(x0, x0 + width, y_end, (0, 50, 100), sx, lambda v: f"{v}%", "Share of Tasks Both Models Graded")
    ly = y_end + 78
    lx = x0
    for key, label, color, extra in parts:
        body.append(rect(lx, ly - 12, 14, 14, color, rx=2, extra=extra))
        body.append(text(lx + 20, ly, label, 15, "var(--text-2)"))
        lx += 150
    label = ("Agreement between Composer and SWE-2 by length of the full description, in thirds of the "
             + ", ".join(f"{n}: {r['same']} of {r['same'] + r['devin_lower'] + r['composer_lower']} agree"
                         for n, r in zip(names, rows)) + ".")
    return svg(ly + 14, label, body, "x")


MIN_RUNS = 5


def fig_trace_steps(s):
    """Median tool calls at each step; a point needs MIN_RUNS runs behind it."""
    d = s["traces"]["by_step"]
    steps = ["L1", "L2", "L3–4", "L5–6"]
    x0, x1, y0, h, top = 120, 560, 60, 240, 100
    xs = {st: x0 + 40 + i * (x1 - x0 - 80) / (len(steps) - 1) for i, st in enumerate(steps)}
    sy = lambda v: y0 + h - h * v / top
    body = []
    for tick in range(0, top + 1, 25):
        body.append(line(x0, sy(tick), x1, sy(tick), "var(--line)", 1))
        body.append(text(x0 - 10, sy(tick) + 5, str(tick), 14, "var(--text-3)", "end", mono=True))
    body += [line(x0, y0 - 8, x0, y0 + h, "var(--text-3)", 1.5), line(x0, y0 + h, x1, y0 + h, "var(--text-3)", 1.5),
             rotated(40, y0 + h / 2, "Median Tool Calls per Run")]
    for st in steps:
        body.append(text(xs[st], y0 + h + 26, st, 16, "var(--text-2)", "middle", 600, True))
    body.append(text((x0 + x1) / 2, y0 + h + 52, "Ladder Step", 15, "var(--text-2)", "middle"))
    series = (("composer", "pass"), ("composer", "fail"), ("devin", "pass"), ("devin", "fail"))
    for m, v in series:
        pts = [(xs[st], sy(d[k]["median"]), d[k]["n"]) for st in steps
               for k in [f"{m}|{st}|{v}"] if k in d and d[k]["n"] >= MIN_RUNS]
        dash = "" if v == "pass" else ' stroke-dasharray="6 5"'
        body.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)}" fill="none" '
                    f'stroke="{MODEL_COLOR[m]}" stroke-width="3"{dash}/>')
        for x, y, n in pts:
            body.append(glyph(x, y, MODEL_COLOR[m], v == "pass", f"{MODEL[m]} {v}ed, {n} runs"))
    # legend across the top
    lx = 60
    for m, v in series:
        dash = "" if v == "pass" else ' stroke-dasharray="6 5"'
        body.append(f'<line x1="{lx}" y1="18" x2="{lx + 30}" y2="18" stroke="{MODEL_COLOR[m]}" stroke-width="3"{dash}/>')
        body.append(glyph(lx + 15, 18, MODEL_COLOR[m], v == "pass", ""))
        body.append(text(lx + 40, 23, f"{MODEL[m]} {'passed' if v == 'pass' else 'failed'}", 14, "var(--text-2)"))
        lx += 165
    label = ("Median tool calls per run at each ladder step, for passed and failed runs of each model, "
             f"leaving out any point with fewer than {MIN_RUNS} runs. Failed runs take more calls than "
             "passed runs at the bug report and the full description for both models.")
    return svg(y0 + h + 64, label, body)


def fig_trace_flips(s):
    f = s["traces"]["flips"]
    rows = [("composer", "calls", "Tool Calls"), ("devin", "calls", "Tool Calls"),
            ("composer", "explore_calls", "Read and Search Calls"),
            ("devin", "explore_calls", "Read and Search Calls")]
    full = {"composer": "Composer 2.5", "devin": "SWE-2"}
    x0, width, row, top = 250, 400, 52, 46
    lo, hi = 20, 80
    sx = lambda v: x0 + width * (v - lo) / (hi - lo)
    body = []
    ys = []
    for i, (m, k, name) in enumerate(rows):
        y = top + i * row + (14 if i >= 2 else 0)
        ys.append(y)
        a, b = f[m][k]
        fmt = lambda v: f"{v:.0f}"
        body.append(text(x0 - 16, y - 3, name, 16, MODEL_COLOR[m], "end", 600))
        body.append(text(x0 - 16, y + 16, f"({full[m]})", 15, MODEL_COLOR[m], "end"))
        body.append(line(x0, y, x0 + width, y, "var(--line)", 1))
        body.append(line(sx(a), y, sx(b), y, MODEL_COLOR[m], 4))
        # Arrowhead at the midpoint, pointing from the failed run toward the pass.
        mid, d = (sx(a) + sx(b)) / 2, (1 if b > a else -1)
        tip = mid + 6 * d
        body.append(f'<polygon points="{tip:.1f},{y} {tip - 12 * d:.1f},{y - 7} {tip - 12 * d:.1f},{y + 7}" '
                    f'fill="{MODEL_COLOR[m]}"/>')
        body.append(glyph(sx(a), y, MODEL_COLOR[m], False, f"failed run: {fmt(a)}"))
        body.append(glyph(sx(b), y, MODEL_COLOR[m], True, f"passing run: {fmt(b)}"))
        below = abs(sx(a) - sx(b)) < 44
        body.append(text(sx(a), y + (28 if below else -16), fmt(a), 15, "var(--text-2)", "middle", mono=True))
        body.append(text(sx(b), y - 16, fmt(b), 15, weight=700, anchor="middle", mono=True))
        body.append(text(max(sx(a), sx(b)) + 26, y + 5, f"{100 * (b - a) / a:+.0f}%".replace("-", "−"),
                         16, MODEL_COLOR[m], weight=700, mono=True))
    y_end = ys[-1] + 26
    body.append(line(x0, top - 30, x0, y_end, "var(--text-3)", 1.5))
    body += x_axis(x0, x0 + width, y_end, (20, 40, 60, 80), sx, lambda v: str(v), "Median Calls per Run")
    ly = y_end + 76
    body.append(glyph(x0, ly, "var(--text-2)", False, "failed"))
    body.append(text(x0 + 14, ly + 5, "Failed trial below first pass", 15, "var(--text-2)"))
    body.append(glyph(x0, ly + 26, "var(--text-2)", True, "passed"))
    body.append(text(x0 + 14, ly + 31, "First passing trial", 15, "var(--text-2)"))
    label = (f"Same task, same model. Composer ({f['composer']['tasks']} tasks) goes from "
             f"{f['composer']['calls'][0]:.0f} calls on its failed run to {f['composer']['calls'][1]:.0f} on its pass, "
             f"and SWE-2 ({f['devin']['tasks']} tasks) from {f['devin']['calls'][0]:.0f} to {f['devin']['calls'][1]:.0f}. "
             f"Read and search calls fall from {f['composer']['explore_calls'][0]:.0f} to "
             f"{f['composer']['explore_calls'][1]:.0f} for Composer and from {f['devin']['explore_calls'][0]:.0f} "
             f"to {f['devin']['explore_calls'][1]:.0f} for SWE-2.")
    return svg(ly + 44, label, body, "r")


def fig_runs(s):
    raw = s["runs"]
    runs = {}
    for name, rungs, _ in STEPS:
        runs[name] = collections.Counter()
        for r in rungs:
            runs[name].update(raw.get(r, {}))
    lv = [name for name, _, _ in STEPS]
    totals = {r: sum(runs[r].values()) for r in lv}
    base, top = 270, 50
    ymax = 800
    sy = lambda v: base - (base - top) * v / ymax
    bw, step, x0 = 88, 140, 150
    body = []
    for t in range(0, ymax + 1, 200):
        body.append(line(110, sy(t), 700, sy(t), "var(--line)", 1))
        body.append(text(100, sy(t) + 5, num(t), 14, "var(--text-3)", "end", mono=True))
    body += [line(110, top - 8, 110, base, "var(--text-3)", 1.5), line(110, base, 700, base, "var(--text-3)", 1.5),
             rotated(30, (top + base) / 2, "Runs with a Verdict")]
    for i, r in enumerate(lv):
        x = x0 + i * step
        y = base
        for m in ("composer", "devin"):
            n = runs[r].get(m, 0)
            if not n:
                continue
            h = base - sy(n)
            body.append(rect(x, y - h, bw, h, MODEL_COLOR[m], f"{r}, {MODEL[m]}: {n} runs", rx=0))
            y -= h
        body.append(text(x + bw / 2, y - 10, num(totals[r]), 18, anchor="middle", weight=700, mono=True))
        body.append(text(x + bw / 2, base + 26, r, 18, "var(--text)", "middle", 700, True))
    body.append(text((110 + 700) / 2, base + 52, "Ladder Step", 15, "var(--text-2)", "middle"))
    for lx, m in ((450, "composer"), (560, "devin")):
        body.append(rect(lx, 10, 14, 14, MODEL_COLOR[m], rx=2))
        body.append(text(lx + 20, 22, MODEL[m], 16, "var(--text-2)"))
    label = ("Runs with a verdict per ladder step, stacked by model. "
             + ", ".join(f"{r} {totals[r]}" for r in lv) + ".")
    return svg(base + 64, label, body, "y")


def fig_runs_per_cert(_s):
    rows = [("parallel, no gate", 9.0, False), ("sequential, no gate", 7.7, False),
            ("sequential, gated", 3.2, True)]
    x0, width, row, bh, top = 230, 400, 50, 30, 14
    sx = lambda v: x0 + width * v / 10
    body = []
    for i, (name, v, key) in enumerate(rows):
        y = top + i * row
        body.append(text(x0 - 16, y + bh - 9, name, 18, anchor="end"))
        body.append(rect(x0, y, sx(v) - x0, bh, "var(--chart-1)", f"{name}: {v}",
                         extra="" if key else ' fill-opacity="0.35"'))
        body.append(text(sx(v) + 10, y + bh - 8, f"{v:.1f}", 19, weight=700, mono=True))
    y_end = top + row * 3 - 8
    fx = sx(2)
    body.append(line(fx, top - 6, fx, y_end, "var(--chart-2)", 2, ' stroke-dasharray="4 4"'))
    body.append(text(fx + 6, top - 10 + 4, "floor of 2", 14, "var(--chart-2)"))
    body.append(line(x0, top - 6, x0, y_end, "var(--text-3)", 1.5))
    body.append(rotated(26, (top + y_end) / 2, "schedule"))
    body += x_axis(x0, x0 + width, y_end, (0, 2, 4, 6, 8, 10), sx, lambda v: str(v), "runs per certificate")
    label = "Runs needed per certificate: parallel with no gate 9.0, sequential with no gate 7.7, sequential with a gate 3.2, against a floor of 2."
    return svg(y_end + 56, label, body, "x")


FIGURES = {
    "prompt-words": fig_prompt_words,
    "funnel": fig_funnel,
    "repo-yield": fig_repos,
    "information-gradient": fig_gradient,
    "curves": fig_curves,
    "agreement-by-length": fig_length,
    "trace-steps": fig_trace_steps,
    "trace-flips": fig_trace_flips,
    "runs-per-level": fig_runs,
}


TITLES = {
    "prompt-words": "What Each Level Adds",
    "funnel": "From Authored to Graded Tasks",
    "repo-yield": "Certified Tasks by Repository",
    "information-gradient": "Share of Tasks Solved by Level",
    "curves": "First Passing Level by Task and Model",
    "agreement-by-length": "Model Agreement by Description Length",
    "trace-steps": "Tool Calls per Run by Level",
    "trace-flips": "Tool Calls Before and After the First Pass",
    "runs-per-level": "Graded Runs per Level",
}
TITLE_H = 44


def with_title(markup, title):
    """Put a chart title above the drawing: grow the viewBox and shift the body down."""
    head, rest = markup.split(">", 1)
    h = float(re.search(r'viewBox="0 0 720 ([\d.]+)"', head).group(1))
    head = head.replace(f'viewBox="0 0 720 {h:.0f}"', f'viewBox="0 0 720 {h + TITLE_H:.0f}"')
    body, tail = rest.rsplit("</svg>", 1)
    return (f'{head}>\n{text(360, 24, title, 19, anchor="middle", weight=700)}\n'
            f'<g transform="translate(0 {TITLE_H})">{body}</g>\n</svg>{tail}')


def render(s):
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FIGURES.items():
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(with_title(fn(s), TITLES[name]))
    print(f"rendered {len(FIGURES)} figures from the {s['date']} snapshot into {os.path.relpath(OUT, SITE)}")


if __name__ == "__main__":
    if "--render" in sys.argv:
        render(json.load(open(SNAPSHOT)))
    else:
        render(snapshot())
