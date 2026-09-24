---
title: "The Information Ladder: Difficulty as an Information Gap"
date: "2026-09-23"
collection: data
lede: true
tags:
  - writing
  - data
  - evals
  - benchmarks
  - agents
  - coding-agents
source_url: https://github.com/Evan-Kim2028/open_swe_traces_research
source_platform: github
slug: difficulty-is-an-information-gap
description: "A synthetic coding-task factory that sets difficulty by what the prompt withholds, certifies each task with two runs, and grades tasks and models on one scale. Stage 1: 591 Go tasks from nine repositories."
series: Evals
series_index: 3
hero: /assets/images/information-gap-hero.png
hero_dark: /assets/images/information-gap-hero.dark.png
---

<!-- vale House.FirstPerson = NO -->

## Intro

What makes a coding task difficult? One answer is how much information the solver has. If an agent
can look the answer up, the task is trivial. We build on that idea with an information ladder, creating six
prompts for one task that gradually reveal more information to the solver. The ladder gives each
task a second dimension, so we can mark the point where it goes from unsolvable to solvable and
certify a model's capability there. We test the approach on 591 Go tasks, with 1,610 graded runs and
242 certified tasks.

- **Three in five tasks are hard enough to keep.** Of the 411 graded tasks, 169 (41%) fell to the
  bug report and are too easy. The other 242 failed it and became solvable higher up the ladder,
  81% of them from the full description alone.
- **Information replaces search.** A passing run makes a quarter to a third fewer reads and searches
  than the failed run one level below it.
- **Models disagree on what is hard.** Composer and Devin land on the same level for 41 of the 73
  tasks both graded, and they agree least where the full description runs long.
- **The factory runs without people.** Agents authored 591 tasks in three days, 93% passed
  validation on the first try, and Stage 1 cost $1.4k.

## The information ladder

### Six prompts for one task

A task starts from a working Go repository. An agent cuts out one behavior, keeps it as the answer
key, and leaves the exported functions behind as stubs that panic. The solver passes when a hidden
test suite passes, and the ladder changes only what the solver sees. Take `httpmux`, from goa's
HTTP package, whose cut removes the router: its answer key is 109 lines of `http/mux.go`, checked
by ten hidden tests in one file. The agent that makes the cut also writes the bug report, the way a
user files an issue. A separate agent writes the full description after reading the answer key and
the hidden tests, so it spells out every behavior they check.

| Level | The solver gets | For `httpmux` |
|---|---|---|
| L1 bug report | The symptom and a command to reproduce it | 75 words, opening "Registering a route, serving a request, reading path variables, or resolving the matched pattern panics." |
| L2 full description | Every behavior the tests check, one line per assertion, with worked examples | 567 words, such as "`{*name}` captures the whole remainder" |
| L3 test names | L2 plus the names of the hidden tests | `TestDetail01_WildcardForms` through `TestDetail10_WildcardNameClass` |
| L4 signatures | L3 plus the exported signatures as stubs | Nothing new, because the cut already left them |
| L5 one test | L4 plus one hidden test file in the repository | `mux_hidden_test.go`, 431 lines |
| L6 all tests | Every hidden test in the repository | Nothing new, because that was the only file |

Each level contains the one below, so a task passed at one level is solvable at every level above
it. Up to L3 the ladder adds words to the prompt, and from L5 on it adds test code to the
repository. L4 and L6 rarely add anything, and the same model gave the same verdict at L3 and L4 on
42 of the 47 tasks run at both, so the charts use four steps. One cut yields every level, and we
count each such family as one task.

<figure class="fig-inline">
{% include "figures/information-gap/prompt-words.svg" %}
<figcaption>What each level adds, in medians over the staged tasks. Blue bars read against the bottom axis: words in the prompt grow through the test names and then hold steady. Orange bars read against the top axis: lines of hidden test code in the repository appear only at L5 and L6.</figcaption>
</figure>

### Where the difficulty lives

Anything the solver can read counts as information, including what the cut leaves in the
repository. Of 23 tasks cut
with their callers in place, models solved 19 from the bug report, and models solved every task that
kept its in-tree tests, 36 of 36 for one model and 26 of 26 for another. A generator with eight structural knobs, including call hops, decoys, and
interface removal, made 25 tasks with up to seven functions deleted across four files, and a
frontier model solved all 25. The knobs moved solve time from 1.3 minutes to 7.6 and left the
outcome unchanged, because rearranging code only moves information somewhere less convenient.

The prompt, by contrast, moves the outcome directly. Of the 411 graded tasks, models solved 169
from the bug report. The other 242 failed it and passed higher up, and 197 of those passed as soon
as the full description arrived, with the code, the tests, and the model unchanged. Another 10
needed the test names and 35 the test file. The graded set holds only tasks that passed somewhere
on the ladder, so the curve below reaches 100% by construction. What it shows is where tasks
become solvable: 41% at the bug report, 89% by the full description, and 92% by the test names.
Both models trace the same curve, solving about two in five of their tasks from the bug report and
85% and 93% by the full description.

<figure class="fig-inline">
{% include "figures/information-gap/information-gradient.svg" %}
<figcaption>The information gradient: the share of graded tasks solved by each ladder step, counting a task as solved from its first passing level up. Graded tasks are ones that passed at some level, so every line ends at 100%. The solid line is every task, and the dashed lines are each model's own grades.</figcaption>
</figure>

### What the information does

For every task a model failed and later passed higher up, 209 for Composer and 69 for Devin, we
compare its first passing run with the failed run just below it. The passing run takes fewer tool calls, 58
against 68 for Composer and 57 against 69 for Devin, and nearly the whole saving is exploration:
read and search calls fall by a quarter to a third, while test runs hold level. The information does
searching the model would otherwise have done.

<figure class="fig-inline">
{% include "figures/information-gap/trace-flips.svg" %}
<figcaption>Same task, same model: the failed run just below the first passing level, and that passing run. The calls both models drop are reads and searches.</figcaption>
</figure>

Across 1,608 graded runs the two models work much alike, with a median of 62 to 65 tool calls, two
thirds of them reading and searching, although Devin takes 19 minutes a run to Composer's 3. Failed runs take more calls than passed ones, 73 against 54
for Composer and 76 against 63 for Devin, so a long run signals a likely miss that a budget could
cut short. With the test file in the tree almost nothing fails, and Composer passed 109 of its 113
runs there.

<figure class="fig-inline">
{% include "figures/information-gap/trace-steps.svg" %}
<figcaption>Median tool calls per run at each ladder step, for passed runs (solid) and failed runs (dashed). Each step holds different tasks, and a point needs at least five runs behind it.</figcaption>
</figure>

## Task certification

A failing task is ambiguous: it may be hard, or its prompt may be missing something nobody could
guess. A certificate settles it with two runs by one model. Failing at L1 shows the task is hard for
that model from a bug report alone, and passing at L2 shows it is solvable from a description that
names no file, line, or function to edit. If L2 fails too, the model keeps climbing, and the
certificate records the first level it passes. Every certificate names its model, because a
stronger model would otherwise erase a weaker one's difficulty.

The certificate depends on each description saying what it claims. On eight tasks a model had
passed at L2, we flipped one line of the description to state the opposite of the removed code,
and seven of the eight then failed on the flipped property. The same audit found that 40% of
the first batch described the removed code wrongly, and every investigated task that failed at both
L1 and L2 had a defective description.

## Grading models

When we follow one model up one task, its first passing level grades the task. When we hold the
task and change the model, the gap between their levels compares the models in information instead
of points.
Composer ran most trials, Devin climbed tasks Composer had screened, and Grok ran only as a third
model at the top. Each gap below rests on about one run per level.

<figure class="fig-inline">
{% include "figures/information-gap/curves.svg" %}
<figcaption>Each lane is one model on one task. The tint runs from the bug report to the first pass, so its length is how much information that model needed. A filled dot is a pass and a ring is a fail.</figcaption>
</figure>

On `archive` and `defval`, both models fail the bug report, which a solve rate scores as a tie, yet
Devin then passes from the full description while Composer needs the test file. On `advrefs` the gap
runs the other way, and on `httperrexpr` both pass at L2. The hardest tasks, `httpmux` and
`exprhash`, fall to Composer only once the test file is in the tree, and Grok and Devin each pass
one of them there too.

Thirty-six tasks carry independent certificates from both models. Both need the same level on 23,
Devin needs less on 10, and Composer on 3, partly because tasks reached Devin after Composer failed
them. Across all 73 tasks both graded, the models land on the same level for 41, and Kendall's
tau-b between their grades is 0.29, so a task that is hard for one model is only loosely hard for
the other.

The length of the full description predicts where they disagree. On the tasks the models disagree
about, the median description runs 716 words, against 532 where they agree, and the gap holds with
answer-key size held fixed and on the tasks both failed from the bug report.

<figure class="fig-inline">
{% include "figures/information-gap/agreement-by-length.svg" %}
<figcaption>Composer and Devin grades on the 72 of those 73 tasks with a recorded description length, split into thirds by the length of the full description. The models agree on about seven in ten tasks with a short or middling description and on one in four with a long one.</figcaption>
</figure>

The repository matters as much as the model. Of the 33 tasks Composer had certified, Devin solved 18
from the bug report alone, including all 8 from `go-github`, whose issues name the fields the code
turns on.

## The factory

### Building a task

Agents build each task and Docker checks it by execution, with no person in the loop.

1. **Cut.** An agent removes one self-contained behavior from a Go repository, keeps it as the
   answer key, and writes the bug report and a list of behaviors to restore.
2. **Write blind tests.** A second agent writes one hidden test per behavior from the list and the
   public API, never the removed code, so the tests check what a caller can see.
3. **Validate.** Docker builds the task and runs the checks below.
4. **Describe.** A third agent reads the answer key and the tests and writes the full description,
   one line per assertion.
5. **Grade.** The task runs at L1, then at L2, and climbs the ladder only if L2 fails.

### Task validation

Validation rejects any task a correct solver could fail or a wrong one could pass. The answer key
must pass and the cut repository fail, a fake fix that hardcodes the test inputs must fail, and the
answer key may never change a test file. A judge also drops description lines no solver could work
out, like the value of an internal constant.

### Yield and headroom

Agents authored the 591 tasks over three days, and validation passed 93% of them on the first
try. Each authored task yields a family of prompts without further authoring, because every
level of the ladder comes from the same cut. The nine repositories still have room to spare, since
the answer keys change only about one in seven of their source files, and adding a repository takes
a base image and a validation pass.

### Keeping the grade honest

A pass should mean the model fixed the code. During a run the container reaches only the model
vendor's API, the grader runs with no network, and the repository ships without its git history.
Below L5 the hidden tests stay outside the container, and at L5 and L6 the grader checks the test
file's sha256, so an edited copy scores zero. We audited 123k tool calls and found one web fetch of the
file under test, and that pass counts as no verdict. Another 55 passing runs also edited a test
file, and none of those edits can change what the hidden tests check. A zero counts only if the tests ran and
failed, and a separate check caught 69 verdicts on 13 tasks whose tests never compiled. Those ran
again once their tasks passed validation, and five tasks left the dataset.

## The synthetic dataset

### The graded tasks

The tasks come from nine Go repositories: client-go, kops, helm, go-git, go-github, goa, gin, bbolt,
and nats-server. The median answer key adds 100 lines, and one in eight touches two or more files.

<figure class="fig-inline">
{% include "figures/information-gap/funnel.svg" %}
<figcaption>591 tasks authored and 411 graded on the ladder. The rest never ran, or ran without reaching a verdict.</figcaption>
</figure>

### Cost and what it limited

Stage 1 used 7.9 billion tokens, worth about $1.4k at API prices, drawn from one researcher's
subscriptions. The Devin rows use its SWE-2 promotional rate, 75% off list.

| Work | Runs or sessions | Tokens | Cost |
|---|---:|---:|---:|
| Composer 2.5, grading | 1,447 runs | 3.0B | $682 |
| Devin SWE-2, grading | 304 sessions | 1.8B | $284 |
| Devin SWE-2, authoring | 213 sessions | 3.0B | $378 |
| Grok, top-of-ladder probe and authoring | 21 runs, 24 sessions | 0.2B | $55 |
| **Stage 1** | | **7.9B** | **$1.4k** |

The factory made tasks faster than the budget could grade them, so 159 of the 591 authored tasks
never ran. Measuring every task at every level three times by both models would take about twelve
times the runs of Stage 1, and that gap is compute, not method.

<figure class="fig-inline">
{% include "figures/information-gap/runs-per-level.svg" %}
<figcaption>Runs with a verdict at each ladder step, stacked by model. The upper steps and the second model are where the budget ran out.</figcaption>
</figure>

### What these data can and cannot show

Most levels ran once per task per model, so one run cannot separate a model that needs the
information from one that got lucky, and part of the disagreement between models may be noise.
Selection shapes the comparison, since Composer screened 374 of the 432 tasks that ran and most
tasks Devin saw were ones Composer had failed. The levels of a family nest by design, so a training or
evaluation split should keep each family on one side. The answer keys are upstream code from
widely used repositories, and our next check is a probe for memorized functions.

## Related work and conclusion

| Method | How difficulty is set | Evidence it is hard | Evidence the prompt suffices |
|---|---|---|---|
| SWE-bench, SWE-Gym | inherited from the issue | reviewer judgment | not reported |
| SWE-smith | follows the injected bug | not reported | not reported |
| R2E-Gym | inherited from the commit | not reported | not reported |
| ProgramDistill | how many behaviors a solver restores together | authored depth | not reported |
| CodeMidas | screening model drops always-pass and always-fail | the screening model failed it | not reported |
| This work | what the prompt withholds, L1 against L2 | one model failed the bug report | the same model passed the full description |

Only our work reports a second prompt that separates a hard task from an underspecified one. The
closest relative, CodeMidas (Ye et al., [arXiv:2609.22068](https://arxiv.org/abs/2609.22068)),
also starts from source code alone but builds its tests by running the original code, so its tests
come from the answer, where these come from a written specification of it.

Difficulty is a relation between a task, a model, and an amount of information. The ladder sets the
information and reads off the other two, and the traces show the information standing in for the
search a model would otherwise do. Four lessons carry to any task factory: put the difficulty in
the prompt, run two prompts, keep the test writer away from the answer key, and build the guards
before the generator.

Stage 1 is small because of its budget, and three questions come next. Does the cut work outside
Go, which we test in Stage 2 with a second language? Does the disagreement between models survive three
repeat runs per level? And does a second model climbing the same tasks change where certificates
bind, now 81% at the full description and 14% at the test file?

---

*Code and trial ledger:
[open_swe_traces_research](https://github.com/Evan-Kim2028/open_swe_traces_research). Counts are a
2026-09-23 snapshot of the finished Stage 1 run, derived from `openswe_traces.reports.paper_numbers`.
Figures regenerate from the ledger with `scripts/information-gap-figures.py`. Earlier in this
series: [Terminal-Bench Task: Lakehouse Schema Contract
Drift](/writings/terminal-bench-task-lakehouse-schema-contract-drift/) and [Four Verifiable
Properties of a Useful Agent Task](/writings/four-verifiable-properties-of-a-useful-agent-task/).*
