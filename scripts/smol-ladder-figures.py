#!/usr/bin/env python3
"""Figures for knowledge-vs-execution-qwen3-5-2b-data-agent.md.

    uv run --project ../smol-ladder python3 scripts/smol-ladder-figures.py --snapshot
    python3 scripts/smol-ladder-figures.py --render

The snapshot needs the research repo (RESEARCH_REPO, default ../smol-ladder) and its run trees, and
runs inside that repo's environment. Rendering needs only docs/data/smol-ladder-snapshot.json and
borrows the SVG helpers of information-gap-figures.py, so the two posts' charts share one look:
every colour is a CSS variable from src/styles.css and one SVG serves both themes.
"""
import importlib.util
from pathlib import Path
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
RESEARCH = os.environ.get("RESEARCH_REPO", os.path.join(os.path.dirname(SITE), "smol-ladder"))
SNAPSHOT = os.path.join(SITE, "docs/data/smol-ladder-snapshot.json")
OUT = os.path.join(SITE, "src/_includes/figures/smol-ladder")

RUNGS = [("L1", "amd2-{m}", "L1"), ("L1+control", "amd3-{m}", "L1+control"),
         ("L2", "amd3-{m}", "L2"), ("L3", "amd3-{m}", "L3"), ("L4", "amd3-{m}", "L4")]
RUNG_NAME = {"L1": "question", "L1+control": "+ rules", "L2": "+ columns",
             "L3": "+ method", "L4": "+ program"}
TICK_MAIN = {"L1+control": "L1"}
def disp(rung):
    """Display name: the post calls the L1+control run the rules variant."""
    return "L1 + rules" if rung == "L1+control" else rung
MODELS = {"base": "amd2-base", "A": "amd2-a", "B1": "amd3-b4", "B2": "amd3-b5"}
SAMPLED = {"base": "amd3s-base", "A": "amd3s-a", "B": "amd3s-b4"}


# ---------------------------------------------------------------- snapshot (research env)

def snapshot():
    sys.path.insert(0, RESEARCH)
    os.chdir(RESEARCH)
    from smol_ladder import report_runs as R           # noqa: E402
    from smol_ladder.tasks import load_split            # noqa: E402
    import glob, collections                            # noqa: E401,E402

    rows = {r["task_id"]: r for r in load_split("test")}

    def trim(m):
        keep = ("pass_rate", "ci95", "wrote_any_answer", "ended_in_repeat_loop", "stop_reasons", "by_tier")
        out = {k: m[k] for k in keep}
        for k, v in m.items():
            if k.startswith("vs_"):
                out[k] = v
        return out

    out = {"date": date.today().isoformat(), "l1_greedy": {}, "l1_sampled": {}, "ladder": {}, "anatomy": {},
           "rescue": {}}
    rep = R.report(MODELS, "L1", "base")
    out["l1_greedy"] = {"common_tasks": rep["common_tasks"], "models": {k: trim(v) for k, v in rep["models"].items()}}
    rep = R.report(SAMPLED, "L1", "base")
    out["l1_sampled"] = {"common_tasks": rep["common_tasks"], "models": {k: trim(v) for k, v in rep["models"].items()}}
    for rung, pat, name in RUNGS:
        rep = R.report({"base": pat.format(m="base"), "A": pat.format(m="a")}, name, "base")
        out["ladder"][rung] = {"common_tasks": rep["common_tasks"], "models": {k: trim(v) for k, v in rep["models"].items()}}

    # Paired against L1 for the base model: tasks kept, gained and lost at each higher rung.
    passes = {}
    for rung, pat, name in RUNGS:
        passes[rung] = {t: R.mean(d["passes"]) >= 1 for t, d in R.load_run(pat.format(m="base"), name).items()}
    for rung in list(passes)[1:]:
        c = set(passes["L1"]) & set(passes[rung])
        out["rescue"][rung] = {"n": len(c),
                               "kept": sum(passes["L1"][t] and passes[rung][t] for t in c),
                               "gained": sum(passes[rung][t] and not passes["L1"][t] for t in c),
                               "lost": sum(passes["L1"][t] and not passes[rung][t] for t in c),
                               "p": R.sign_test(sum(passes[rung][t] and not passes["L1"][t] for t in c),
                                                sum(passes["L1"][t] and not passes[rung][t] for t in c))}

    # How the base model's episodes end at L1, L3 and L4.
    def num(s):
        try:
            return float(str(s).replace(",", "").replace("%", ""))
        except ValueError:
            return None

    def variants(g):
        g = str(g).strip()
        v = {g}
        try:
            x = float(g.replace(",", ""))
            for d in range(5):
                v.add(f"{x:.{d}f}")
            if x == int(x):
                v.add(str(int(x)))
        except ValueError:
            pass
        return {a for a in v if len(a) >= 2}

    for rung, pat, name in RUNGS:
        if rung not in ("L1", "L3", "L4"):
            continue
        tag = pat.format(m="base")
        C = collections.Counter()
        onscreen = unanswered = n = 0
        tiers = collections.defaultdict(lambda: [0, 0])
        for f in glob.glob(f"data/runs/{tag}/test/*/{R.rung_dir(name)}/result.json"):
            r = json.load(open(f))
            if r.get("stop_reason") == "error" or r.get("skipped"):
                continue
            n += 1
            tier = rows[r["task_id"]].get("difficulty_tier") or "?"
            tiers[tier][0] += 1
            if r["reward"] >= 1:
                C["correct"] += 1
                tiers[tier][1] += 1
                continue
            cmds = R.commands_of(Path(f).with_name("transcript.json"))
            t = json.load(open(os.path.join(os.path.dirname(f), "transcript.json")))
            outs = [str(x.get("content")) for x in (t if isinstance(t, list) else t.get("messages") or []) if x.get("role") == "tool"]
            pred = (r.get("prediction") or "").strip()
            gold = rows[r["task_id"]]["answer"]
            if pred:
                g, p = num(gold), num(pred)
                if (g is None) != (p is None):
                    C["wrong kind of answer"] += 1
                else:
                    C["wrong answer"] += 1
            else:
                unanswered += 1
                loop = len(cmds) >= 4 and len(set(cmds[-4:])) == 1
                C["ran out of context" if r["stop_reason"] == "context_exhausted" else "repeat loop" if loop else "wandered 16 turns"] += 1
                pats = [re.compile(r"(?<![\w.])" + re.escape(v) + r"(?![\w.]*\d)") for v in variants(gold)]
                onscreen += any(p.search(o) for o in outs for p in pats)
        out["anatomy"][rung] = {"n": n, "ends": dict(C), "unanswered": unanswered, "value_on_screen": onscreen,
                                "by_tier": {k: {"n": v[0], "correct": v[1]} for k, v in sorted(tiers.items())}}
    with open(SNAPSHOT, "w") as f:
        json.dump(out, f, indent=1)
    print("snapshot written to", os.path.relpath(SNAPSHOT, SITE))
    return out


# ---------------------------------------------------------------- render

def helpers():
    spec = importlib.util.spec_from_file_location("ig", os.path.join(HERE, "information-gap-figures.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = None   # the borrowed helper module, set in render()
MODEL_COLOR = {"base": "var(--text-3)", "A": "var(--chart-1)", "B": "var(--chart-2)", "B1": "var(--chart-2)",
               "B2": "var(--chart-2)"}
MODEL_NAME = {"base": "base", "A": "A (SmolDataEnvs-sft)", "B": "B (our trajectories)",
              "B1": "B, seed 1", "B2": "B"}


def pct(x):
    return f"{100 * x:.0f}%"


def whisker(x, y0, y1, color):
    return [H.line(x, y0, x, y1, color, 1.5), H.line(x - 5, y0, x + 5, y0, color, 1.5), H.line(x - 5, y1, x + 5, y1, color, 1.5)]


def fig_ladder(s):
    """Base and A at each rung: pass rate with its 95% interval."""
    rungs = list(RUNGS)
    x0, x1, top, bottom = 70, 690, 50, 320
    sy = lambda v: bottom - (bottom - top) * v / 0.8
    body = []
    for v in (0, 0.2, 0.4, 0.6, 0.8):
        body.append(H.line(x0, sy(v), x1, sy(v)))
        body.append(H.text(x0 - 10, sy(v) + 5, pct(v), 14, "var(--text-3)", "end", mono=True))
    gw = (x1 - x0) / len(rungs)
    bw = 36
    label = []
    for i, (rung, _, _) in enumerate(rungs):
        d = s["ladder"][rung]["models"]
        cx = x0 + gw * (i + 0.5)
        for j, m in enumerate(("base", "A")):
            x = cx - bw - 6 + j * (bw + 12)
            v = d[m]["pass_rate"]
            lo, hi = d[m]["ci95"]
            body.append(H.rect(x, sy(v), bw, bottom - sy(v), MODEL_COLOR[m],
                               f"{MODEL_NAME[m]} at {disp(rung)}: {pct(v)} [{pct(lo)}, {pct(hi)}]"))
            body += whisker(x + bw / 2, sy(hi), sy(lo), "var(--text)")
            body.append(H.text(x + bw / 2, sy(hi) - 7, pct(v), 13, "var(--text-2)", "middle", mono=True))
            label.append(f"{MODEL_NAME[m]} {disp(rung)} {pct(v)}")
        body.append(H.text(cx, bottom + 22, TICK_MAIN.get(rung, rung), 15, "var(--text)", "middle", 700, mono=True))
        body.append(H.text(cx, bottom + 40, RUNG_NAME[rung], 13, "var(--text-2)", "middle"))
    body.append(H.line(x0, bottom, x1, bottom, "var(--text-3)", 1.5))
    body.extend(H.y_axis(x0, top, bottom, "pass rate"))
    body.append(H.text((x0 + x1) / 2, bottom + 60, "rung", 15, "var(--text-2)", "middle"))
    lx = x0 + 10
    for m in ("base", "A"):
        body.append(H.rect(lx, 8, 14, 14, MODEL_COLOR[m]))
        body.append(H.text(lx + 20, 20, MODEL_NAME[m], 14, "var(--text-2)"))
        lx += 60 + 9 * len(MODEL_NAME[m])
    body.append(H.text(x0, bottom + 80, "Whiskers are 95% bootstrap intervals over tasks; L1 on 250 tasks, the rest on the 213 with a verified reference.", 12, "var(--text-3)"))
    return H.svg(bottom + 94, "Pass rate by rung for the base model and A. " + "; ".join(label), body)


def fig_sft(s):
    """L1 at temperature 0 (four models) and sampled (three): pass rate with its interval."""
    panels = [("Temperature 0, one attempt, 250 tasks", s["l1_greedy"]["models"], ["base", "A", "B2"]),
              ("Sampled, 4 attempts per task, 60 tasks", s["l1_sampled"]["models"], ["base", "A", "B"])]
    top, bottom = 48, 250
    sy = lambda v: bottom - (bottom - top) * v / 0.4
    body, label = [], []
    for p, (title, d, models) in enumerate(panels):
        x0 = 70 + p * 340
        x1 = x0 + 300
        body.append(H.text(x0, 22, title, 15, "var(--text-2)"))
        for v in (0, 0.1, 0.2, 0.3, 0.4):
            body.append(H.line(x0, sy(v), x1, sy(v)))
            if p == 0:
                body.append(H.text(x0 - 10, sy(v) + 5, pct(v), 14, "var(--text-3)", "end", mono=True))
        gw = (x1 - x0) / len(models)
        for i, m in enumerate(models):
            v, (lo, hi) = d[m]["pass_rate"], d[m]["ci95"]
            x = x0 + gw * i + gw / 2 - 22
            body.append(H.rect(x, sy(v), 44, bottom - sy(v), MODEL_COLOR[m], f"{MODEL_NAME[m]}: {pct(v)} [{pct(lo)}, {pct(hi)}]"))
            body += whisker(x + 22, sy(min(hi, 0.4)), sy(lo), "var(--text)")
            body.append(H.text(x + 22, sy(min(hi, 0.4)) - 7, pct(v), 13, "var(--text-2)", "middle", mono=True))
            body.append(H.text(x + 22, bottom + 20, MODEL_NAME[m].split(" (")[0], 14, "var(--text)", "middle", 700 if m == "base" else 400))
            label.append(f"{title}: {MODEL_NAME[m]} {pct(v)}")
        body.append(H.line(x0, bottom, x1, bottom, "var(--text-3)", 1.5))
        body.append(H.text(x0 + 150, bottom + 38, "model", 15, "var(--text-2)", "middle"))
    body.extend(H.y_axis(70, top, bottom, "pass rate"))
    body.append(H.text(70, bottom + 56, "A: 4,439 SmolDataEnvs-sft trajectories. B: our 1,897 from the same harness. Whiskers are 95% intervals.", 12, "var(--text-3)"))
    return H.svg(bottom + 70, "L1 pass rate by model. " + "; ".join(label), body)


ENDS = [("correct", "correct", "var(--chart-1)"), ("wrong kind of answer", "wrong format", "var(--chart-2)"),
        ("wrong answer", "wrong answer", "color-mix(in srgb, var(--chart-2) 55%, var(--bg))"),
        ("repeat loop", "loops", "var(--text-3)"),
        ("wandered 16 turns", "wandered 16 turns", "color-mix(in srgb, var(--text-3) 60%, var(--bg))"),
        ("ran out of context", "ran out of context", "color-mix(in srgb, var(--text-3) 35%, var(--bg))")]


def fig_failures(s):
    """How the base model's episodes end at L1, L3 and L4, as one stacked bar per rung."""
    x0, x1 = 150, 690
    top, rh, bh = 30, 64, 30
    body, label = [], []
    for i, rung in enumerate(("L1", "L3", "L4")):
        a = s["anatomy"][rung]
        y = top + i * rh
        body.append(H.text(x0 - 12, y + bh / 2 + 5, f"{rung} {RUNG_NAME[rung]}", 14, "var(--text)", "end", 700))
        x = x0
        parts = []
        for key, label_, color in ENDS:
            c = a["ends"].get(key, 0)
            w = (x1 - x0) * c / a["n"]
            body.append(H.rect(x, y, w, bh, color, f"{rung}: {c} of {a['n']} episodes, {label_}", rx=2))
            if w > 34:
                body.append(H.text(x + w / 2, y + bh / 2 + 5, str(c), 13, "var(--bg)" if key == "correct" else "var(--text)", "middle", mono=True))
            parts.append(f"{label_} {c}")
            x += w
        label.append(f"{rung}: " + ", ".join(parts))
    body.append(H.text((x0 + x1) / 2, top + 3 * rh - 10, "share of episodes", 15, "var(--text-2)", "middle"))
    body.append(H.rotated(20, (top + top + 2 * rh + bh) / 2, "rung"))
    y = top + 3 * rh + 4
    for k, (key, label_, color) in enumerate(ENDS):
        lx = x0 + (k % 3) * 180
        ly = y + (k // 3) * 20
        body.append(H.rect(lx, ly, 12, 12, color, rx=2))
        body.append(H.text(lx + 17, ly + 11, label_, 12, "var(--text-2)"))
    a = s["anatomy"]
    body.append(H.text(x0, y + 58, "Of the unanswered episodes, the correct value had already been printed in", 12, "var(--text-3)"))
    body.append(H.text(x0, y + 74, f"{a['L1']['value_on_screen']} of {a['L1']['unanswered']} at L1, {a['L3']['value_on_screen']} of {a['L3']['unanswered']} at L3 and {a['L4']['value_on_screen']} of {a['L4']['unanswered']} at L4.", 12, "var(--text-3)"))
    return H.svg(y + 88, "How the base model's episodes end at L1, L3 and L4. " + "; ".join(label), body)


def fig_gained_lost(s):
    """Against L1, the tasks each rung gains and loses for the base model: diverging bars."""
    rungs = [r for r in s["rescue"]]
    mid, top, rh, bh = 360, 30, 48, 26
    scale = 2.1
    body, label = [], []
    for i, rung in enumerate(rungs):
        d = s["rescue"][rung]
        y = top + i * rh
        body.append(H.text(230, y + bh / 2 + 5, f"{TICK_MAIN.get(rung, rung)} {RUNG_NAME[rung]}", 14, "var(--text)", "end", 700))
        body.append(H.rect(mid - d["lost"] * scale, y, d["lost"] * scale, bh, "var(--chart-2)", f"{disp(rung)}: {d['lost']} tasks solved at L1 and lost here", rx=2))
        body.append(H.rect(mid, y, d["gained"] * scale, bh, "var(--chart-1)", f"{disp(rung)}: {d['gained']} tasks failed at L1 and gained here", rx=2))
        body.append(H.text(mid - d["lost"] * scale - 8, y + bh / 2 + 5, f"{d['lost']}", 14, "var(--text-2)", "end", mono=True))
        body.append(H.text(mid + d["gained"] * scale + 8, y + bh / 2 + 5, f"{d['gained']}", 14, "var(--text-2)", mono=True))
        p = d["p"]
        body.append(H.text(690, y + bh / 2 + 5, f"p = {p:.3f}" if p >= 0.001 else "p < 0.001", 13, "var(--text-3)", "end", mono=True))
        label.append(f"{disp(rung)}: gained {d['gained']}, lost {d['lost']}, kept {d['kept']}, p {p:.3f}")
    body.append(H.line(mid, top - 8, mid, top + len(rungs) * rh, "var(--text-3)", 1.5))
    body.append(H.text(mid - 8, top - 14, "lost", 13, "var(--chart-2)", "end"))
    body.append(H.text(mid + 8, top - 14, "gained", 13, "var(--chart-1)"))
    body.append(H.text(mid, top + len(rungs) * rh + 6, "tasks", 15, "var(--text-2)", "middle"))
    body.append(H.rotated(100, (top + top + (len(rungs) - 1) * rh + bh) / 2, "rung"))
    body.append(H.text(60, top + len(rungs) * rh + 22, "Tasks, paired against the same model at L1 (250 for the rules, 213 for L2 to L4).", 12, "var(--text-3)"))
    body.append(H.text(60, top + len(rungs) * rh + 38, "The sign test asks whether gains outnumber losses beyond what a coin would give.", 12, "var(--text-3)"))
    return H.svg(top + len(rungs) * rh + 52, "Tasks gained and lost against L1 by the base model at each rung. " + "; ".join(label), body)


def fig_tiers(s):
    """Base pass rate by difficulty tier at L1, L3 and L4."""
    tiers = ["easy", "medium", "hard"]
    rungs = ["L1", "L3", "L4"]
    shade = {"L1": "color-mix(in srgb, var(--chart-1) 35%, var(--bg))", "L3": "color-mix(in srgb, var(--chart-1) 65%, var(--bg))", "L4": "var(--chart-1)"}
    x0, x1, top, bottom = 70, 690, 30, 260
    sy = lambda v: bottom - (bottom - top) * v / 0.8
    body, label = [], []
    for v in (0, 0.2, 0.4, 0.6, 0.8):
        body.append(H.line(x0, sy(v), x1, sy(v)))
        body.append(H.text(x0 - 10, sy(v) + 5, pct(v), 14, "var(--text-3)", "end", mono=True))
    gw = (x1 - x0) / 3
    bw = 44
    for i, tier in enumerate(tiers):
        cx = x0 + gw * (i + 0.5)
        for j, rung in enumerate(rungs):
            t = s["anatomy"][rung]["by_tier"][tier]
            v = t["correct"] / t["n"]
            x = cx - 1.5 * bw - 8 + j * (bw + 8)
            body.append(H.rect(x, sy(v), bw, bottom - sy(v), shade[rung], f"{tier} at {rung}: {t['correct']} of {t['n']}"))
            body.append(H.text(x + bw / 2, sy(v) - 8, pct(v), 13, "var(--text-2)", "middle", mono=True))
            body.append(H.text(x + bw / 2, bottom + 18, rung, 12, "var(--text-3)", "middle", mono=True))
            label.append(f"{tier} {rung} {pct(v)}")
        n = s["anatomy"]["L1"]["by_tier"][tier]["n"]
        body.append(H.text(cx, bottom + 40, f"{tier} ({n} tasks at L1)", 15, "var(--text)", "middle", 700))
    body.append(H.line(x0, bottom, x1, bottom, "var(--text-3)", 1.5))
    body.extend(H.y_axis(x0, top, bottom, "pass rate"))
    body.append(H.text((x0 + x1) / 2, bottom + 58, "difficulty tier", 15, "var(--text-2)", "middle"))
    return H.svg(bottom + 72, "Base model pass rate by difficulty tier at L1, L3 and L4. " + "; ".join(label), body)


FIGURES = {"ladder": fig_ladder, "sft-l1": fig_sft, "failures": fig_failures, "gained-lost": fig_gained_lost, "tiers": fig_tiers}
TITLES = {"ladder": "Pass Rate by Rung: Base Model and A", "sft-l1": "Fine-Tuning at L1",
          "failures": "How the Base Model's Episodes End", "gained-lost": "Tasks Gained and Lost Against L1",
          "tiers": "Difficulty by Tier as Information Is Added"}


def render(s):
    global H
    H = helpers()
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FIGURES.items():
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(H.with_title(fn(s), TITLES[name]))
    print(f"rendered {len(FIGURES)} figures from the {s['date']} snapshot into {os.path.relpath(OUT, SITE)}")


if __name__ == "__main__":
    if "--snapshot" in sys.argv:
        snapshot()
    else:
        render(json.load(open(SNAPSHOT)))
