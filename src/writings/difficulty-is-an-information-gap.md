---
title: "Building a Synthetic SWE Factory: The Information Ladder"
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
description: "A coding task is hard because of what its prompt leaves out. The information ladder sets that one level at a time and grades tasks and models on one scale. Stage 1: Go, nine repositories, 591 tasks."
series: Evals
series_index: 3
hero: /assets/images/information-gap-hero.png
hero_dark: /assets/images/information-gap-hero.dark.png
---

## Summary

Most generators make a coding task harder by working on the code: more files, deeper call chains,
more behavior removed at once. That tends to move the answer somewhere less convenient. A task is
hard because of what its prompt leaves out, and a factory can set that directly. Hold the code, the
tests, and the model fixed, change only how much the prompt says about the missing behavior, and
the same model goes from failing to passing. The information ladder is that dial, six prompts for
one task, each telling the solver more. Agents build each task and execution checks it, so no step
needs a person, and the factory scales with compute instead of reviewers. This post describes a
factory built on the ladder and what its first 591 Go tasks show.

- **The prompt sets the difficulty.** Composer fails `gin-clientip` from a 96-word bug report and
  passes it three runs in three from a 596-word description of the same behavior. Across the
  dataset, 41% of graded tasks fall to the bug report and 89% once the full description arrives.
- **Information replaces search.** On the same task, the passing run makes a quarter to a third
  fewer reads and searches than the failed run just below it, and runs the tests just as often.
- **Two prompts separate a hard task from a broken one.** The factory certifies a task only when
  one model fails the bug report and passes the full description. None of the comparable pipelines
  reports that second run.
- **Structure leaks the answer.** One frontier model solved all 25 tasks built with up to seven
  functions deleted across four files. Callers or tests left in the repository gave the answer away
  almost every time.
- **The same ladder grades models.** Composer and Devin both fail `archive` from the bug report,
  and the ladder puts them two steps apart. On the 76 tasks both graded, they land on the same level
  for 41, and they part ways most often where the description runs long.
- **Money sets the limit.** Stage 1 graded 412 tasks with 7.9 billion tokens, worth $1.4k at API
  prices. Measuring every task at every level with both models would cost about $15k.

## The information ladder

### Six prompts for one task

A task starts from a working Go repository. An agent cuts out one behavior, keeps it as the answer
key, and leaves the exported functions behind as stubs that panic, so the package still builds. The
solver passes when a hidden test suite passes, and the ladder changes only what the solver sees.

Take `httpmux`, from goa's HTTP package. Its cut removes the router: route registration, `{name}`
and `{*name}` wildcards, middleware order, and matching a request to its pattern. The answer key is
109 lines of `http/mux.go`, and the hidden suite is ten tests in one file.

| Level | The solver gets | For `httpmux` |
|---|---|---|
| L1 bug report | The symptom and a command to reproduce it | 75 words, opening "Registering a route, serving a request, reading path variables, or resolving the matched pattern panics." |
| L2 full description | Every behavior the tests check, one line per assertion, with worked examples | 567 words, such as "`{*name}` captures the whole remainder" and "pattern `/users/{id}` with request `/users` gives nil vars" |
| L3 test names | L2 plus the names of the hidden tests | `TestDetail01_WildcardForms` through `TestDetail10_WildcardNameClass` |
| L4 signatures | L3 plus the exported signatures as stubs | Nothing new, because the cut already left them |
| L5 one test | L4 plus one hidden test file in the repository | `mux_hidden_test.go`, 431 lines, now in the tree |
| L6 all tests | Every hidden test in the repository | Nothing new, because that was the only file |

Each level contains the one below, so a solver given more can always ignore the extra, and a task
passed at one level is solvable at every level above it. That is Blackwell's ordering of
experiments, and the rings in the figure at the top draw it. Up to L3 the ladder changes the
prompt, and from L4 on it changes the repository. Two levels rarely add anything here. The cut
already keeps the signatures, and most tasks keep their hidden tests in one file, so L4 usually
repeats L3 and L6 repeats L5. The same model gave the same verdict at L3 and L4 on 53 of the 58
tasks run at both. The charts use the four real steps: bug report, full description, test names,
and the test file.

One cut therefore yields a task family: the same code, answer key, and hidden tests, prompted at up
to six levels. Authoring pays for the cut once, and each level after it comes nearly free, which is
how the factory multiplies graded tasks without multiplying the agent work behind them. The levels
nest by design, so they share far more than separate tasks would, and this post counts families
and calls each one a task.

<figure class="fig-inline">
{% include "figures/information-gap/prompt-words.svg" %}
<figcaption>Typical prompt length at each level: the median bug report, plus the median words each level adds over tasks built at both, leaving out the no-network paragraph every prompt shares. The prompt grows through L3. Above that it holds steady, and each level adds files to the repository instead.</figcaption>
</figure>

### Where the difficulty lives

If the prompt sets the difficulty, anything left in the repository counts as prompt. Callers give a
removed function away through argument shapes, call order, and what they check afterward. Of 23
tasks cut with their callers in place, models solved 19 from the bug report, and 12 of 14 even when
the cut picked behavior no model could have memorized. In-tree tests act as a specification, and
models solved every task that kept them, 36 of 36 for one model and 26 of 26 for another. Structural
complexity fails for the same reason. A generator with eight knobs, including call hops, decoys,
cross-module placement, and interface removal, made 25 tasks with up to seven functions deleted
across four files, and a frontier model solved all 25. The knobs moved solve time from 1.3 minutes
to 7.6 and left the outcome where it was, because rearranging code only moves information
somewhere less convenient.

The prompt, by contrast, moves the outcome directly. Of the 412 graded tasks, models solved 169
from the bug report. The other 242 failed it and passed higher up, and 197 of those passed as soon
as the full description arrived, with the code, the tests, and the model unchanged. Another 11
needed the test names and 34 the test file. One task, `exprhash`, has beaten two models at every
level. Read as a gradient, the share of tasks solved climbs from 41% at the bug report to 89% at
the full description, then to 92% and nearly all. Both models trace the same curve. Each solves
about 38% of its tasks from the bug report, and the full description lifts Composer to 85% and
Devin to 91%. Nearly the whole gradient sits in that one step.

<figure class="fig-inline">
{% include "figures/information-gap/information-gradient.svg" %}
<figcaption>The information gradient: the share of graded tasks solved by each ladder step, counting a task as solved from its first passing level up. The solid line is every task at the level its grading model first passed it, and the dashed lines are each model's own grades. Each model climbs only after failing lower down, so the curve shows how much information each task needed.</figcaption>
</figure>

### What the information does

The trial traces show what the extra information changes in the work. Take every task a model
failed and later passed higher up, 207 for Composer and 73 for Devin, and compare its first passing
run with the failed run just below it on the same task. The passing run takes fewer tool calls, 58
against 68 for Composer and 57 against 68 for Devin, and nearly the whole saving is exploration.
Composer's read and search calls fall from 50 to 38 and Devin's from 43 to 30, a quarter to a third
fewer, while test runs hold level at 8 and 9. For Devin the exploring share of its calls drops too,
from 64% to 56%. The information does searching the model would otherwise have done.

<figure class="fig-inline">
{% include "figures/information-gap/trace-flips.svg" %}
<figcaption>Same task, same model: the failed run just below the first passing level, and that passing run. Both models pass with fewer calls, and the calls they drop are reads and searches.</figcaption>
</figure>

Across 1,646 graded Composer and Devin runs, the two models work much alike: a median of 62 tool
calls, about two thirds of them reading and searching and one in seven running the tests. Devin
takes 18 minutes a run to Composer's 3. Composer's failed runs take more calls than its passed
runs, 73 against 54, so a long Composer run signals a likely miss that a budget could cut short.
Devin's failed and passed runs look the same, 63 calls against 62.

Failure changes shape as the ladder rises. At the bug report and the full description, Composer's
failed runs are its long ones, 69 and 70 calls against 52 and 51 for passes, with more edits, as it
rewrites code that keeps failing. Higher up the order flips for both models, and failures become
the short runs. With the test file in the tree Composer fails in 44 calls and passes in 71, and
Devin's failures are the shorter runs from the full description on.

<figure class="fig-inline">
{% include "figures/information-gap/trace-steps.svg" %}
<figcaption>Median tool calls per run at each ladder step. Solid lines and filled dots are passed runs, dashed lines and rings are failed runs. Each step holds different tasks, since only a task that fails lower down climbs, and above L2 each point rests on few runs, down to 5.</figcaption>
</figure>

## Task certification

A failing task is ambiguous. It may be hard, or its prompt may be missing something nobody could
guess, and both score zero on every rerun. A certificate settles it with two runs by one model.
Failing at L1 shows the task is hard for that model from a bug report alone. Passing at L2 shows the
task is solvable from a description that names no file, line, or function to edit. If L2 fails
too, the model keeps climbing, and the certificate records the first level it passes. "Hard at L1"
describes a model, so every certificate names its model. An earlier version took the lowest passing
level across all models, which let the stronger model erase the weaker one's difficulty and put two
certificates three levels too low.

The certificate depends on each description saying what it claims, and an inversion test checks
that. On eight tasks a model had passed at L2, the audit flipped one line of the description to
state the opposite of the removed code and kept everything else fixed. Seven of the eight then
failed, each on the flipped property. The same audit found that 40% of the first batch described
the removed code wrongly, and all seven investigated tasks that failed at both L1 and L2 had a
defective description. When the prose is wrong, the run measures the prose.

## Grading models

Follow one model up one task, and its first passing level grades the task. Hold the task and change
the model, and the gap between their levels compares the models in information instead of points.
Composer ran most trials, including the cheap L1 screen that finds tasks solvable from the bug
report. Most of Devin's climbs began on tasks Composer had already graded. Grok had one narrow
job: a third model sent to the top of the ladder, to test whether any model could solve the three
tasks Composer failed at every level. The budget allowed about one run per level, so each gap
below is a single observation.

<figure class="fig-inline">
{% include "figures/information-gap/curves.svg" %}
<figcaption>Each lane is one model on one task. The tint runs from the bug report to the first pass, so its length is how much information that model needed. A filled dot is a pass at that step and a ring is a fail.</figcaption>
</figure>

On `archive` and `defval`, Composer and Devin both fail the bug report, which a solve rate scores
as a tie. Devin then passes from the full description, and Composer needs the test file. On
`ipqueue` Devin needs only the bug report. The gap runs the other way too. On `advrefs` Composer
passes from the full description and Devin needs the test file, and on `helm-dlmanager` Composer
passes at L2 in three runs of three while Devin fails every level. On `httperrexpr` both pass at
L2, a difficulty that belongs to the task.

At the top, Composer failed `httpmux`, `httpencoding`, and `exprhash` at every level, test file
included. With no wider prompt left, only a second model can show those tasks are solvable. Grok
passed `httpmux` and `httpencoding` with the test file in one run of two, which certifies both as
solvable, and Devin passed `httpencoding` once every hidden test was in the tree. The answer key for
`exprhash` passes its suite, so the task is solvable by construction, yet 28 runs from two models
have missed it.

Forty tasks carry independent certificates from two models, and those are the tasks that can
separate a task's difficulty from a model's. Composer and Devin share 39 of them. Both need the same
level on 23, so there the difficulty belongs to the task. Devin needs less on 11 and Composer on 5.
The pattern holds across every task both models graded, including the ones one of them solved from
the bug report.

<figure class="fig-inline">
{% include "figures/information-gap/joint-grades.svg" %}
<figcaption>Where each model first passes, on the 76 tasks both graded. The shaded diagonal is the same level for both. Below it Devin passes lower, and above it Composer does. The top row sits nearly empty because Composer screened first and its L1 passes rarely went on to Devin.</figcaption>
</figure>

The two models land on the same level for 41 of the 76. Devin passes lower on 29 and Composer on
6, and selection drives that lean, since tasks reached Devin after Composer failed them. The two
grades also rank the tasks differently. Kendall's tau-b between them is 0.23, so a task that is hard
for one model is only loosely hard for the other, and a difficulty grade means little without the
model that earned it.

The length of the full description predicts the disagreement. A larger answer key makes a task
harder for both models and moves them together, while a longer description pulls them apart. On the
tasks the models disagree about, the median description runs 716 words, against 526 where they
agree, and the gap holds with answer-key size held fixed and on the tasks both failed from the bug
report. These tasks leave open which model comes out ahead on a long description.

<figure class="fig-inline">
{% include "figures/information-gap/agreement-by-length.svg" %}
<figcaption>Composer and Devin grades on the 75 tasks both graded that have a recorded description, split into thirds by the length of the full description. The models agree on about seven in ten tasks with a short or middling description and on one in five with a long one.</figcaption>
</figure>

The bug report alone separates models too. Of 78 tasks both screened at L1, they agree on 59, and
on the other 19 Devin passed where Composer failed. The repository matters as much as the model.
Devin screened 36 tasks Composer had certified and solved 17 of them from the bug report: all 8 from
`go-github`, whose issues name the fields the code turns on, and 9 of the 28 everywhere else.

## The factory

The factory runs without a person in the loop. Agents cut, test, and describe each task, and Docker
checks it by execution. People design the checks and audit samples.

### Building a task

Three agents and a Docker harness build each task.

1. **Cut.** An agent removes one self-contained behavior from a Go repository. Public signatures
   stay as stubs, and the removed code becomes the answer key. The same agent writes the bug report
   and a list of behaviors a solver must restore.
2. **Write blind tests.** A second agent writes one hidden test per listed behavior. It sees the
   list, the public API, and the cut repository, never the removed code, and its tests may only
   call exported functions.
3. **Validate.** Docker builds the task and runs the checks below.
4. **Describe.** A third agent reads the answer key and the tests together and writes the full
   description, one line per assertion.
5. **Grade.** The task runs at L1, then at L2, and climbs the ladder only if L2 fails.

Step 2 keeps the test writer blind so the tests check behavior a caller can see. The agent that
removed the code would test the missing implementation and fail a correct solver who wrote it
differently.

### Task validation

Validation rejects any task a correct solver could fail or a wrong one could pass. Each check exists
because a bad task once got through without it.

- **The answer key passes and the cut repository fails.** Two tasks once shipped with an answer key
  that failed its own tests.
- **A fake fix fails.** A patch that hardcodes the test inputs must fail. One task accepted a
  special case, so its tests checked nothing.
- **The answer key never touches a test file.**
- **Every behavior is derivable.** A judge drops lines no solver could work out, like the value of
  an internal constant. One pass over 170 tasks dropped or weakened 245 of 1.6k lines.

### Keeping the grade honest

A pass should mean the model fixed the code. Three defenses close the other routes, and three
audits check what got through anyway.

- **A sealed container.** During a run the container reaches only the model vendor's own API hosts,
  and the grader runs with no network at all. The repository ships without its git history, so no
  old commit holds the fix. None of the 1.1k staged repositories carries a `.git` directory or a
  copy of the answer key.
- **Tests the agent cannot see or edit.** Below L5 the hidden tests stay outside the container
  until the agent stops. One staged copy leaked its test into the repository at L2, and all three
  runs on it failed anyway. At L5 and L6 the agent reads the test file, so the grader checks its
  sha256 before and after installing it, and an edited copy scores zero. The grade runs only the
  named hidden tests.
- **Web tools, audited.** Agent-side web tools run on vendor servers, beyond the container's
  reach, so the only defense is reading every trajectory. Across 1.8k runs and 123k tool calls,
  one agent used one: Composer fetched the upstream copy of the file under test for
  `helm-depresolver` at L3, then passed. That pass counts as no verdict.
- **Test edits, audited.** 55 passing runs also edited a test file, nearly always to bring
  the package's existing tests in line with the fix. None added an `init` or `TestMain` function,
  and Go refuses a second definition of the code under test, so a test file cannot change what the
  hidden tests check.
- **Harness failures, audited.** A zero counts only if the tests ran and failed. Sorting every
  verdict by what the grader printed turned up one real harness bug. A renaming pass, run after
  validation to disguise the source repositories, changed Go module paths and user-facing strings
  in three repositories without touching their hidden tests. On 13 tasks the tests could
  no longer compile, or the cut repository no longer held the bug, whatever the agent wrote.
  69 verdicts from those trees count as no verdict. Every task that had seemed to beat a
  model at every level was one of them. Rewriting the import paths restored 8 of the 13, which passed validation
  again and run their voided cells again. The other 5 need their cut rebuilt and count as no
  verdict until then.

## The synthetic dataset

### The graded tasks

The tasks come from nine Go repositories: client-go, kops, helm, go-git, go-github, goa, gin, bbolt,
and nats-server. They cover Kubernetes tooling, version control, API design, storage, HTTP
services, and messaging. The median answer key adds 100 lines, the middle half add between 50 and
190, and one in eight touches two or more files.

<figure class="fig-inline">
{% include "figures/information-gap/funnel.svg" %}
<figcaption>591 tasks authored and 412 graded on the ladder. The rest never ran, or ran without reaching a verdict.</figcaption>
</figure>

The bucket that failed every level held 29 tasks before the upper levels had runs. Every audited
one had a defective description, the rest certified once a higher level supplied what the prose
left out, and only `exprhash` remains.

### Cost and what it limited

Stage 1 processed 7.9 billion tokens, worth about $1.4k at API prices. One researcher drew them from
subscriptions and promotional plans, so the dollar figures here value the tokens at those prices.
The factory could author tasks and the harness could run them faster than those allowances could
pay for the runs, and the budget shaped the dataset more than any design choice did.

| Work | Runs or sessions | Tokens | Cost |
|---|---:|---:|---:|
| Composer 2.5, grading | 1,439 runs | 3.0B | $678 |
| Devin SWE-2, grading | 295 sessions | 1.7B | $276 |
| Devin SWE-2, authoring | 213 sessions | 3.0B | $378 |
| Grok 4.7 and 4.6, top-of-ladder probe and authoring | 21 runs, 24 sessions | 0.2B | $55 |
| **Stage 1** | | **7.9B** | **$1.4k** |

Almost all of it paid for reading. Cache reads made up 95% of the tokens, a model re-reading a
repository it had already loaded. Building a task was cheap, about $0.69 per authored task.
Grading cost far more, at 7.0 runs and $4.04 per certificate, and a run above L2 cost twice an L2
run, $0.78 against $0.38, because only harder tasks reach those levels and the solver has a test
file to read. The factory made tasks faster than the budget could grade them, so 159 of the 591
authored tasks never ran and 20 more ran without reaching a verdict.

<figure class="fig-inline">
{% include "figures/information-gap/runs-per-level.svg" %}
<figcaption>Runs with a verdict at each ladder step, stacked by model. The upper steps and the second models are where the budget ran out.</figcaption>
</figure>

The one saving that worked was refusing runs whose outcome the ledger already held, which cut the
runs per certificate about fourfold.

<figure class="fig-inline">
{% include "figures/information-gap/runs-per-certificate.svg" %}
<figcaption>Runs spent per certificate under three schedules, in a controlled comparison on 229 tasks at L1 and L2. Gating is worth about 4×, and running trials in sequence, on its own, is worth almost nothing. The whole run's 7.0 runs per certificate is higher because it also pays for climbs above L2 and second-model screens.</figcaption>
</figure>

Money sets the limit. At Stage 1's prices, $0.47 a Composer run and $0.94 a Devin run, the
measurements this budget could not buy are easy to price. Three repeat runs on 50 tasks at L1 and
L2 from both models, about $420, would show how often a grade changes on a rerun. Both models
climbing the same 100 tasks, about $570, would remove the selection in the model comparison.
Measuring everything, every authored task at every level three times by both models, takes about
21k runs and 83 billion tokens. That is $15k at these prices, eleven times Stage 1. The factory
already authors the tasks and the harness already runs every cell, so what stands between Stage 1
and a fully measured dataset is compute bought at scale, a bill beyond one researcher.

Two caveats on the tokens. Composer and Grok count cached tokens inside their input and Devin
counts them on top, so each total follows its vendor's convention. Devin bills in Agent Compute
Units. Its counts here come exact, request by request, from its own session logs, priced at the
SWE-2 promotional rate, which matched the compute-unit bill within 8% when both were available.
The table counts building and grading tasks only. It leaves out the agents that ran and analyzed the
pipeline, about $45 of Grok among them, since not every tool logged that work.

### What these data can and cannot show

- **Most levels ran once per task per model.** One run cannot separate a model that needs the
  information from one that got lucky. The levels that repeat a task act as reruns and show how
  much that matters. The same model gave the same verdict at L3 and L4 on 53 of 58 tasks, but at
  L5 and L6 on only 10 of 16, where Grok's one pass in two on `httpmux` falls. Noise grows near the
  top of the ladder, and part of the disagreement between models may be noise too.
- **Selection shapes the model comparison.** Composer screened 374 of the 432 tasks that ran, and
  most tasks Devin saw were ones Composer had failed, so Devin's lean toward lower grades partly
  reflects which tasks it got.
- **The second model is thin.** A Devin run cost about twice a Composer run and drew on a fixed
  allowance of compute units, so only 136 tasks have its L1 screen and 40 have two independent
  climbs. Composer and Devin carried the dataset, and Grok ran only as a probe on the three tasks
  at the top. Of the 169 tasks solved from the bug report, Composer graded 132 and Devin 36, and
  both solved one.
- **Tasks cluster.** The levels of a family nest by design, and tasks from one repository share its
  code and conventions. A training or evaluation split should keep each family, and where it can
  each repository, on one side.
- **The design limits memorization but cannot rule it out.** The answer keys are upstream code from
  widely used repositories. No task file references an issue, pull request, or CVE, so nothing in
  the prompt names the code to recall. The answer keys add 59k lines and delete 5.5k, most of them
  the panicking stubs, which leaves behavior to rebuild from a description. A direct probe, asking a
  model for each function from its name alone, is the next check.

## Related work and conclusion

| Method | How difficulty is set | Evidence it is hard | Evidence the prompt suffices |
|---|---|---|---|
| SWE-bench, SWE-Gym | inherited from the issue | reviewer judgment | not reported |
| SWE-smith | follows the injected bug | not reported | not reported |
| R2E-Gym | inherited from the commit | not reported | not reported |
| ProgramDistill | how many behaviors a solver restores together | authored depth | not reported |
| CodeMidas | screening model drops always-pass and always-fail | the screening model failed it | not reported |
| This work | what the prompt withholds, L1 against L2 | one model failed the bug report | the same model passed the full description |

The first three inherit difficulty from an issue, a bug, or a commit, so it belongs to the pool
and to no single task. The last three set it per task, and only this work reports a second prompt
that separates a hard task from an underspecified one. Benchmarks hold the prompt fixed, and read
by instruction content almost every Terminal-Bench task sits between L1 and L2. CodeMidas is the
closest relative and the only other method that starts from source code alone (Ye et al.,
[arXiv:2609.22068](https://arxiv.org/abs/2609.22068), Table 1). It keeps 5.5k tasks across 23
languages, forty times this dataset, but builds its tests by running the original code, so its
tests come from the answer. These come from a written specification of it.

Difficulty is a relation between a task, a model, and an amount of information. The ladder sets the
information and reads off the other two, and the traces show the information standing in for the
search a model would otherwise do. Four lessons carry to any task factory: put the difficulty in
the prompt, run two prompts, keep the test writer away from the answer key, and build the guards
before the generator.

Stage 1 is small because of its budget, with one language, nine repositories, and mostly one model.
Three questions come next.

- **Does the cut work outside Go?** Stage 2 runs the same factory in a second language.
- **Does model disagreement survive a rerun?** Composer and Devin agree on 41 of 76 tasks and rank
  them only loosely alike, parting chiefly on long descriptions. Three repeat runs per level would
  show how much of that is noise.
- **What does the curve above L2 look like?** 81% of certificates bind at the full description and
  14% only once the test file is in the tree. Composer's certificates bind at the full description
  76% of the time and Devin's 84%, and a second model climbing the same tasks would show whether the
  models or the selection drive that gap.

---

*Code and trial ledger:
[open_swe_traces_research](https://github.com/Evan-Kim2028/open_swe_traces_research). Counts are a
2026-09-23 snapshot of the finished Stage 1 run, derived from `trial_ledger.py` and `roots.py`.
Figures regenerate from the ledger with `scripts/information-gap-figures.py`. Earlier in this
series: [Terminal-Bench Task: Lakehouse Schema Contract
Drift](/writings/terminal-bench-task-lakehouse-schema-contract-drift/) and [Four Verifiable
Properties of a Useful Agent Task](/writings/four-verifiable-properties-of-a-useful-agent-task/).*
