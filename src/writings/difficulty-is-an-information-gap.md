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

Most task generators make a coding task harder by working on the code, with more files, deeper call
chains, and more behavior removed at once, which only moves the answer somewhere less convenient.
A task is hard because of what its prompt leaves out, and a factory can set that directly. Hold the
code, the tests, and the model fixed, change only how much the prompt says about the missing
behavior, and the same model goes from failing to passing. The information ladder is that dial:
six prompts for one task, each telling the solver more. Agents build each task and execution checks
it, so the factory scales with compute instead of reviewers. This post describes a factory built on
the ladder and what its first 591 Go tasks show.

- **The prompt sets the difficulty.** Composer fails `gin-clientip` from a 96-word bug report and
  passes it three runs in three from a 596-word description of the same behavior. Across the
  dataset, 41% of graded tasks fall to the bug report and 89% once the full description arrives.
- **Information replaces search.** On the same task, the passing run makes a quarter to a third
  fewer reads and searches than the failed run just below it, and runs the tests just as often.
- **Two prompts separate a hard task from a broken one.** The factory certifies a task only when
  one model fails the bug report and passes the full description, a second run none of the
  comparable pipelines reports.
- **Structure leaks the answer.** A frontier model solved all 25 tasks built with up to seven
  functions deleted across four files, because callers or tests left in the repository gave the
  answer away.
- **The same ladder grades models.** Composer and Devin both fail `archive` from the bug report,
  and the ladder puts them two steps apart. On the 73 tasks both graded, they land on the same level
  for 41 and part ways most often where the description runs long.
- **Money, not authoring, sets the limit.** Agents authored all 591 tasks in three days without a
  person in the loop, 93% of them passed validation on the first try, and their answer keys change
  only about one in seven source files in nine repositories. Grading 411 of them took 7.9 billion
  tokens, worth $1.4k at API prices.

## The information ladder

### Six prompts for one task

A task starts from a working Go repository. An agent cuts out one behavior, keeps it as the answer
key, and leaves the exported functions behind as stubs that panic, so the package still builds. The
solver passes when a hidden test suite passes, and the ladder changes only what the solver sees.
Take `httpmux`, from goa's HTTP package. Its cut removes the router, and the answer key is 109
lines of `http/mux.go` checked by ten hidden tests in one file.

| Level | The solver gets | For `httpmux` |
|---|---|---|
| L1 bug report | The symptom and a command to reproduce it | 75 words, opening "Registering a route, serving a request, reading path variables, or resolving the matched pattern panics." |
| L2 full description | Every behavior the tests check, one line per assertion, with worked examples | 567 words, such as "`{*name}` captures the whole remainder" and "pattern `/users/{id}` with request `/users` gives nil vars" |
| L3 test names | L2 plus the names of the hidden tests | `TestDetail01_WildcardForms` through `TestDetail10_WildcardNameClass` |
| L4 signatures | L3 plus the exported signatures as stubs | Nothing new, because the cut already left them |
| L5 one test | L4 plus one hidden test file in the repository | `mux_hidden_test.go`, 431 lines, now in the tree |
| L6 all tests | Every hidden test in the repository | Nothing new, because that was the only file |

Each level contains the one below, so a task passed at one level is solvable at every level above
it, which is Blackwell's ordering of experiments and what the rings at the top draw. Up to L3 the
ladder adds words to the prompt, and from L5 on it adds test code to the repository. L4 and L6
rarely add anything, because the cut already keeps the signatures and most tasks keep their hidden
tests in one file, and the same model gave the same verdict at L3 and L4 on 42 of the 47 tasks run
at both. The charts therefore use four steps: bug report, full description, test names, and the
test file. One cut yields the whole family of levels, and this post counts each family as one task.

<figure class="fig-inline">
{% include "figures/information-gap/prompt-words.svg" %}
<figcaption>What each level adds. Left, the median words in the prompt, leaving out the no-network paragraph every prompt shares: the prompt grows through the test names and then holds steady. Right, the median lines of hidden test code in the repository, which appear only at L5 and L6.</figcaption>
</figure>

### Where the difficulty lives

If the prompt sets the difficulty, anything left in the repository counts as prompt. Callers give a
removed function away through argument shapes, call order, and what they check afterward: of 23
tasks cut with their callers in place, models solved 19 from the bug report. In-tree tests act as a
specification, and models solved every task that kept them, 36 of 36 for one model and 26 of 26 for
another. A generator with eight structural knobs, including call hops, decoys, and interface
removal, made 25 tasks with up to seven functions deleted across four files, and a frontier model
solved all 25. The knobs moved solve time from 1.3 minutes to 7.6 and left the outcome unchanged,
because rearranging code only moves information somewhere less convenient.

The prompt, by contrast, moves the outcome directly. Of the 411 graded tasks, models solved 169
from the bug report. The other 242 failed it and passed higher up, and 197 of those passed as soon
as the full description arrived, with the code, the tests, and the model unchanged. Another 10
needed the test names and 35 the test file, and no graded task beat every level. Read as a
gradient, the share of tasks solved climbs from 41% at the bug report to 89% at the full
description, then to 92% and all of them. Both models trace the same curve, solving about two in
five of their tasks from the bug report and 85% and 93% once the full description arrives.

<figure class="fig-inline">
{% include "figures/information-gap/information-gradient.svg" %}
<figcaption>The information gradient: the share of graded tasks solved by each ladder step, counting a task as solved from its first passing level up. The solid line is every task at the level its grading model first passed it, and the dashed lines are each model's own grades.</figcaption>
</figure>

### What the information does

The trial traces show what the extra information changes in the work. For every task a model failed
and later passed higher up, 209 for Composer and 69 for Devin, compare its first passing run with
the failed run just below it. The passing run takes fewer tool calls, 58 against 68 for Composer and
57 against 69 for Devin, and nearly the whole saving is exploration. Read and search calls fall
from 50 to 38 for Composer and from 44 to 30 for Devin, while test runs hold level. The information
does searching the model would otherwise have done.

<figure class="fig-inline">
{% include "figures/information-gap/trace-flips.svg" %}
<figcaption>Same task, same model: the failed run just below the first passing level, and that passing run. Both models pass with fewer calls, and the calls they drop are reads and searches.</figcaption>
</figure>

Across 1,607 graded runs the two models work much alike, with a median of 62 to 65 tool calls, two
thirds of them reading and searching, although Devin takes 19 minutes a run to Composer's 3. Failed
runs take more calls than passed ones, 73 against 54 for Composer and 76 against 63 for Devin, so a long run signals a likely miss that a budget could
cut short. With the test file in the tree almost nothing fails, and Composer passed 109 of its 113
runs there.

<figure class="fig-inline">
{% include "figures/information-gap/trace-steps.svg" %}
<figcaption>Median tool calls per run at each ladder step, for passed runs (solid) and failed runs (dashed). Each step holds different tasks, since only a task that fails lower down climbs, and a point needs at least five runs behind it.</figcaption>
</figure>

## Task certification

A failing task is ambiguous. It may be hard, or its prompt may be missing something nobody could
guess, and both score zero on every rerun. A certificate settles it with two runs by one model:
failing at L1 shows the task is hard for that model from a bug report alone, and passing at L2
shows it is solvable from a description that names no file, line, or function to edit. If L2 fails
too, the model keeps climbing, and the certificate records the first level it passes. Every
certificate names its model, because a stronger model would otherwise erase a weaker one's
difficulty.

The certificate depends on each description saying what it claims, and an inversion test checks
that. On eight tasks a model had passed at L2, the audit flipped one line of the description to
state the opposite of the removed code. Seven of the eight then failed, each on the flipped
property. The same audit found that 40% of the first batch described the removed code wrongly, and
every investigated task that failed at both L1 and L2 had a defective description.

## Grading models

Follow one model up one task, and its first passing level grades the task. Hold the task and change
the model, and the gap between their levels compares the models in information instead of points.
Composer ran most trials, including the L1 screen, and most of Devin's climbs began on tasks
Composer had already graded. Grok ran only as a third model at the top of the ladder. The budget
allowed about one run per level, so each gap below is a single observation.

<figure class="fig-inline">
{% include "figures/information-gap/curves.svg" %}
<figcaption>Each lane is one model on one task. The tint runs from the bug report to the first pass, so its length is how much information that model needed. A filled dot is a pass at that step and a ring is a fail.</figcaption>
</figure>

On `archive` and `defval`, Composer and Devin both fail the bug report, which a solve rate scores
as a tie, yet Devin then passes from the full description while Composer needs the test file. On
`ipqueue` Devin needs only the bug report, and on `advrefs` the gap runs the other way. On
`httperrexpr` both pass at L2, a difficulty that belongs to the task. At the top of the ladder sit
`httpmux` and `exprhash`, the hardest tasks in the dataset. Composer fails both through the test
names and passes both only once the test file is in the tree. Grok, run as a third model at the top,
also passes `httpmux` with the test file, and Devin, given a single run with the test file, passes
`exprhash`.

Thirty-six tasks carry independent certificates from both Composer and Devin. Both need the same
level on 23, where the difficulty belongs to the task, Devin needs less on 10, and Composer on 3.
Across all 73 tasks both graded, they land on the same level for 41, and Kendall's tau-b between
their grades is 0.29, so a task that is hard for one model is only loosely hard for the other.
Selection explains part of Devin's lean toward lower grades, since tasks reached Devin after
Composer failed them.

The length of the full description predicts the disagreement. A larger answer key makes a task
harder for both models and moves them together, while a longer description pulls them apart. On the
tasks the models disagree about, the median description runs 716 words, against 532 where they
agree, and the gap holds with answer-key size held fixed and on the tasks both failed from the bug
report.

<figure class="fig-inline">
{% include "figures/information-gap/agreement-by-length.svg" %}
<figcaption>Composer and Devin grades on the 72 tasks both graded that have a recorded description, split into thirds by the length of the full description. The models agree on about seven in ten tasks with a short or middling description and on about one in four with a long one.</figcaption>
</figure>

The repository matters as much as the model. Of the 33 tasks Composer had certified, Devin solved 18
from the bug report alone, including all 8 from `go-github`, whose issues name the fields the code
turns on.

## The factory

The factory runs without a person in the loop. Agents cut, test, and describe each task, Docker
checks it by execution, and people design the checks and audit samples.

### Building a task

1. **Cut.** An agent removes one self-contained behavior from a Go repository. Public signatures
   stay as stubs, and the removed code becomes the answer key. The same agent writes the bug report
   and a list of behaviors a solver must restore.
2. **Write blind tests.** A second agent writes one hidden test per listed behavior from the list,
   the public API, and the cut repository, never the removed code. Blind tests check behavior a
   caller can see, where the agent that removed the code would test its own implementation and fail
   a correct solver who wrote it differently.
3. **Validate.** Docker builds the task and runs the checks below.
4. **Describe.** A third agent reads the answer key and the tests together and writes the full
   description, one line per assertion.
5. **Grade.** The task runs at L1, then at L2, and climbs the ladder only if L2 fails.

### Task validation

Validation rejects any task a correct solver could fail or a wrong one could pass, and each check
exists because a bad task once got through without it.

- **The answer key passes and the cut repository fails.** Two tasks once shipped with an answer key
  that failed its own tests.
- **A fake fix fails.** A patch that hardcodes the test inputs must fail, since one task once
  accepted a special case and checked nothing.
- **The answer key never touches a test file.**
- **Every behavior is derivable.** A judge drops lines no solver could work out, like the value of
  an internal constant. One pass over 170 tasks dropped or weakened 245 of 1.6k lines.

### Yield and headroom

Agents authored the 591 tasks over three days, and validation passed 93% of them on the first
try. Each authored task yields a family of graded prompts without further authoring, because every
level of the ladder comes from the same cut. The nine repositories still have room to spare, since
the answer keys change only about one in seven of their source files. Adding a repository takes a
base image and a validation pass, and the cut, the blind tests, and the description carry over to
any language with a test runner.

### Keeping the grade honest

A pass should mean the model fixed the code. Two defenses close the other routes, and three audits
check what got through anyway.

- **A sealed container.** During a run the container reaches only the model vendor's own API hosts,
  the grader runs with no network, and the repository ships without its git history or the answer
  key.
- **Tests the agent cannot see or edit.** Below L5 the hidden tests stay outside the container
  until the agent stops. At L5 and L6 the agent reads the test file, so the grader checks its sha256
  before and after installing it, and an edited copy scores zero.
- **Web tools, audited.** Agent-side web tools run on vendor servers, beyond the container's
  reach, so the audit reads every trajectory. Across 1.8k runs and 123k tool calls, one agent used one,
  fetching the upstream copy of the file under test, and that pass counts as no verdict.
- **Test edits, audited.** 55 passing runs also edited a test file, nearly always to bring the
  package's existing tests in line with the fix, and none of those edits can change what the hidden
  tests check.
- **Harness failures, audited.** A zero counts only if the tests ran and failed. A run whose tests
  never compiled counts as no verdict and runs again once the task passes validation anew. The check
  caught 69 such verdicts on 13 tasks, and five of those tasks left the dataset until their cut is
  rebuilt.

## The synthetic dataset

### The graded tasks

The tasks come from nine Go repositories: client-go, kops, helm, go-git, go-github, goa, gin, bbolt,
and nats-server. They cover Kubernetes tooling, version control, API design, storage, HTTP
services, and messaging. The median answer key adds 100 lines, the middle half add between 50 and
190, and one in eight touches two or more files.

<figure class="fig-inline">
{% include "figures/information-gap/funnel.svg" %}
<figcaption>591 tasks authored and 411 graded on the ladder. The rest never ran, or ran without reaching a verdict.</figcaption>
</figure>

### Cost and what it limited

Stage 1 processed 7.9 billion tokens, worth about $1.4k at API prices. One researcher drew them from
subscriptions and promotional plans, so the dollar figures value the tokens at those prices, each
vendor counts tokens its own way, and Devin's come request by request from its session logs.

| Work | Runs or sessions | Tokens | Cost |
|---|---:|---:|---:|
| Composer 2.5, grading | 1,447 runs | 3.0B | $682 |
| Devin SWE-2, grading | 304 sessions | 1.8B | $284 |
| Devin SWE-2, authoring | 213 sessions | 3.0B | $378 |
| Grok 4.7 and 4.6, top-of-ladder probe and authoring | 21 runs, 24 sessions | 0.2B | $55 |
| **Stage 1** | | **7.9B** | **$1.4k** |

Almost all of it paid for reading, since cache reads made up 95% of the tokens. Building a task was
cheap, and grading cost far more, at 6.7 runs per certificate. The factory made tasks faster than
the budget could grade them, so 159 of the 591 authored tasks never ran and 21 more ran without
reaching a verdict. Refusing runs whose outcome the ledger already held was the one saving that
worked, and it cut the runs per certificate about fourfold.

<figure class="fig-inline">
{% include "figures/information-gap/runs-per-level.svg" %}
<figcaption>Runs with a verdict at each ladder step, stacked by model. The upper steps and the second models are where the budget ran out.</figcaption>
</figure>

Measuring everything, every authored task at every level three times by both models, would take
about 21k runs, twelve times as many as Stage 1. The factory already authors the tasks and the harness already
runs every cell, so what stands between Stage 1 and a fully measured dataset is compute bought at
scale.

### What these data can and cannot show

- **Most levels ran once per task per model.** One run cannot separate a model that needs the
  information from one that got lucky. The same model gave the same verdict at L3 and L4 on 42 of
  47 tasks and at L5 and L6 on 7 of 8, but those pairs differ slightly and cannot stand in for true
  reruns, and part of the disagreement between models may be noise.
- **Selection shapes the model comparison.** Composer screened 374 of the 432 tasks that ran, and
  most tasks Devin saw were ones Composer had failed.
- **The second model is thin.** Only 133 tasks have Devin's L1 screen and 36 have two independent
  climbs, and Grok ran only as a probe at the top of the ladder.
- **Tasks cluster.** The levels of a family nest by design, and tasks from one repository share its
  code, so a training or evaluation split should keep each family, and where it can each
  repository, on one side.
- **The design limits memorization but cannot rule it out.** The answer keys are upstream code from
  widely used repositories, although no task file names an issue, pull request, or CVE to recall. A
  direct probe, asking a model for each function from its name alone, is the next check.

## Related work and conclusion

| Method | How difficulty is set | Evidence it is hard | Evidence the prompt suffices |
|---|---|---|---|
| SWE-bench, SWE-Gym | inherited from the issue | reviewer judgment | not reported |
| SWE-smith | follows the injected bug | not reported | not reported |
| R2E-Gym | inherited from the commit | not reported | not reported |
| ProgramDistill | how many behaviors a solver restores together | authored depth | not reported |
| CodeMidas | screening model drops always-pass and always-fail | the screening model failed it | not reported |
| This work | what the prompt withholds, L1 against L2 | one model failed the bug report | the same model passed the full description |

The first three inherit difficulty from an issue, a bug, or a commit, so it belongs to the pool and
to no single task. The last three set it per task, and only this work reports a second prompt that
separates a hard task from an underspecified one. Benchmarks hold the prompt fixed, and read by
instruction content almost every Terminal-Bench task sits between L1 and L2. CodeMidas is the
closest relative and the only other method that starts from source code alone (Ye et al.,
[arXiv:2609.22068](https://arxiv.org/abs/2609.22068), Table 1). It keeps 5.5k tasks across 23
languages, but builds its tests by running the original code, so its tests come from the answer,
where these come from a written specification of it.

Difficulty is a relation between a task, a model, and an amount of information. The ladder sets the
information and reads off the other two, and the traces show the information standing in for the
search a model would otherwise do. Four lessons carry to any task factory: put the difficulty in
the prompt, run two prompts, keep the test writer away from the answer key, and build the guards
before the generator.

Stage 1 is small because of its budget, and three questions come next. Does the cut work outside
Go, which Stage 2 tests in a second language? Does the disagreement between models survive three
repeat runs per level? And does a second model climbing the same tasks change where certificates
bind, now 81% at the full description and 14% at the test file?

---

*Code and trial ledger:
[open_swe_traces_research](https://github.com/Evan-Kim2028/open_swe_traces_research). Counts are a
2026-09-23 snapshot of the finished Stage 1 run, derived from `trial_ledger.py` and `roots.py`.
Figures regenerate from the ledger with `scripts/information-gap-figures.py`. Earlier in this
series: [Terminal-Bench Task: Lakehouse Schema Contract
Drift](/writings/terminal-bench-task-lakehouse-schema-contract-drift/) and [Four Verifiable
Properties of a Useful Agent Task](/writings/four-verifiable-properties-of-a-useful-agent-task/).*
