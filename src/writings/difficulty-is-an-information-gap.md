---
title: "Building a Synthetic SWE Factory: The Information Ladder"
date: "2026-09-22"
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

Generated coding tasks are usually made harder by working on the code: more files, deeper call
chains, more behavior removed at once. That turns out not to work. A task is hard because of what
its prompt leaves out, and a factory can set that directly. Hold the code, the tests, and the model
fixed, change only how much the prompt says about the missing behavior, and the same model goes from
failing to passing. The information ladder is that dial, six prompts for one task, each telling the
solver more. Agents build each task and execution checks it, so no step needs a person, and the
factory scales with compute instead of reviewers. This post describes a factory built on the ladder and what its first 591 Go tasks show.

- **The prompt sets the difficulty.** Composer fails `gin-clientip` from a 96-word bug report and
  passes it three runs in three from a 596-word description of the same behavior. Inverting one line
  of a working description made seven of eight passing tasks fail, each on the inverted line.
- **Two prompts separate a hard task from a broken one.** A failing task might be hard or
  impossible, and rerunning it cannot tell which. A task is certified only when one model fails the
  bug report and passes the full description. None of the comparable pipelines reports that second
  run.
- **Complex code is not hard code.** One frontier model solved all 25 tasks built with up to seven
  functions deleted across four files. Callers or tests left in the repository gave the answer away almost
  every time.
- **The same ladder grades models.** Composer and Devin both fail `archive` from the bug report, so
  a solve rate calls them equal, and the ladder puts them two steps apart. Across 39 tasks both
  models climbed, they need the same level on 23, Devin needs less on 11, and Composer needs less
  on 5. At the top, Composer fails two tasks with the hidden tests in front of it, and Grok solves
  each in one of two runs.
- **Every task gets a grade.** Of 415 graded tasks, 172 are solved from the bug report, 242 are
  certified higher up, and one has beaten two models at every level. Stage 1 cost $1.2k.

## The information ladder

### Six prompts for one task

A task starts from a working Go repository. An agent cuts out one behavior, keeps it as the answer
key, and leaves the exported functions behind as stubs that panic, so the package still builds. The
solver passes when a hidden test suite passes, and the ladder changes only what the solver is shown.

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
already keeps the signatures, so L4 matched L3 on 44 of 49 tasks built at both, and 443 of 448
tasks have one hidden test file, so L6 is L5. The charts use the four real steps: bug report, full
description, test names, and the test file.

<figure class="fig-inline">
{% include "figures/information-gap/prompt-words.svg" %}
<figcaption>Typical prompt length at each level: the median bug report, plus the median words each level adds over tasks built at both, not counting the no-network paragraph every prompt shares. The prompt grows through L3. Above that it stays the same, and each level adds files to the repository instead.</figcaption>
</figure>

If the prompt sets the difficulty, anything left in the repository counts as prompt. Callers give a
removed function away through argument shapes, call order, and what they check afterward. Of 23
tasks cut with their callers in place, 19 were solved from the bug report, and 12 of 14 were solved
even when the behavior was chosen so no model could have memorized it. In-tree tests are a
specification, and every task that kept them was solved, 36 of 36 for one model and 26 of 26 for
another. Structural complexity fails for the same reason. A generator with eight knobs, including
call hops, decoys, cross-module placement, and interface removal, made 25 tasks with up to seven
functions deleted across four files, and a frontier model solved all 25. The knobs moved solve time
from 1.3 minutes to 7.6 and never moved the outcome, because rearranging code only moves
information somewhere less convenient.

### The certificate

A failing task is ambiguous. It may be hard, or its prompt may be missing something nobody could
guess, and both score zero on every rerun. A certificate settles it with two runs by one model.
Failing at L1 shows the task is hard for that model from a bug report alone. Passing at L2 shows it
is solvable from a description that names no file, line, or function to edit. If L2 fails too, the
model keeps climbing, and the certificate records the first level it passes.

That depends on each description saying what it claims, and an inversion test checks it. On eight
tasks a model had passed at L2, one line of the description was flipped to state the opposite of
the removed code, with everything else fixed. Seven of the eight then failed, each on the flipped
property. The same audit found that 40% of the first batch described the removed code wrongly, and
all seven investigated tasks that failed at both L1 and L2 had a defective description. When the
prose is wrong, the run measures the prose.

### Grading models

Follow one model up one task, and its first passing level grades the task. Hold the task and change
the model, and the gap between their levels compares the models in information instead of points.
Composer ran most trials, including the cheap L1 screen that finds tasks solvable from the bug
report. Devin climbed tasks Composer had already graded, and Grok ran the three tasks where
Composer ran out of ladder. The Devin climbs test the first thing any difficulty scale owes a
reader, that it separates models the way existing benchmarks do. The budget allowed about one run
per level, so each gap below is a single observation, not an estimate.

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
solvable, and Devin passed `httpencoding` once every hidden test was in the tree. `exprhash` is solvable by construction, since its answer key passes the suite, yet 28 runs from two
models have not solved it.

The bug report alone separates models too. Composer and Devin both screened 78 tasks at L1.

<figure class="fig-inline">
{% include "figures/information-gap/bug-report-agreement.svg" %}
<figcaption>Tasks both models screened at the bug report. Composer screened first on most of them, and tasks it passed rarely went on to Devin, which is why the top row is nearly empty.</figcaption>
</figure>

They agree on 59. On the other 19, Devin passed where Composer failed, a one-sided split because
these tasks reached Devin after Composer failed them. "Hard at L1" is a statement about a model, so
every certificate names its model. An earlier version took the lowest passing level across all
models, which let the stronger model erase the weaker one's difficulty and put two certificates
three levels too low. Forty tasks now carry independent certificates from two models, and those
are the tasks that can separate a task's difficulty from a model's. Composer and Devin share 39 of
them. Both need the same level on 23, so there the difficulty belongs to the task. Devin needs
less on 11 and Composer on 5.

## The factory

The factory is built to run without a person in the loop. Agents cut, test, and describe each
task, and Docker checks it by execution. People design the checks and audit samples.

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

Step 2 is blind so the tests check behavior a caller can see. Tests from the agent that removed
the code would test the missing implementation, and fail a correct solver who wrote it differently.

### Task validation

Validation rejects any task a correct solver could fail or a wrong one could pass. Each check exists
because a bad task once got through without it.

- **The answer key passes and the cut repository fails.** Two tasks once shipped with an answer key
  that failed its own tests.
- **A fake fix fails.** A patch that hardcodes the test inputs must not pass. One task accepted a
  special case, so its tests checked nothing.
- **The answer key never touches a test file.**
- **Every behavior is derivable.** A judge drops lines no solver could work out, like the value of
  an internal constant. One pass over 170 tasks dropped or weakened 245 of 1.6k lines.
- **No network.** Agent-side web tools run on vendor servers, out of the container's reach, so any
  run that used one is thrown out. That disqualified 15 of 30 runs from one model and none of 32
  from another.

### Other pipelines

| Method | How difficulty is set | Evidence it is hard | Evidence the prompt suffices |
|---|---|---|---|
| SWE-bench, SWE-Gym | inherited from the issue | reviewer judgment | not reported |
| SWE-smith | not set; follows the injected bug | not reported | not reported |
| R2E-Gym | inherited from the commit | not reported | not reported |
| ProgramDistill | how many behaviors are restored together | authored depth | not reported |
| CodeMidas | screening model drops always-pass and always-fail | the screening model failed it | not reported |
| This work | what the prompt withholds, L1 against L2 | one model failed the bug report | the same model passed the full description |

The first three inherit difficulty from an issue, a bug, or a commit, so it belongs to the pool
and not to any one task. The last three set it per task, and only this work reports a second prompt
that separates a hard task from an underspecified one. Benchmarks hold the prompt fixed, and read
by instruction content almost every Terminal-Bench task sits between L1 and L2. CodeMidas is the
closest relative and the only other method that starts from source code alone (Ye et al.,
[arXiv:2609.22068](https://arxiv.org/abs/2609.22068), Table 1). It keeps 5.5k tasks across 23
languages, forty times this dataset, but builds its tests by running the original code, so its
tests come from the answer. These come from a written specification of it.

## The synthetic dataset

### The graded tasks

The tasks come from nine Go repositories: client-go, kops, helm, go-git, go-github, goa, gin, bbolt,
and nats-server. They cover Kubernetes tooling, version control, API design, storage, HTTP
services, and messaging. The median answer key is 127 lines, most fall between 80 and 320, and a
quarter touch two or more files.

<figure class="fig-inline">
{% include "figures/information-gap/funnel.svg" %}
<figcaption>591 tasks authored. 415 have been graded on the ladder. The rest never ran, or ran without reaching a verdict.</figcaption>
</figure>

<figure class="fig-inline">
{% include "figures/information-gap/first-pass.svg" %}
<figcaption>The lowest level at which each graded task was passed, by the model that graded it. L4 and L6 are merged into the step below, since on most tasks they are the same task.</figcaption>
</figure>

The 172 tasks solved from the bug report sit at the easy end, a gap of zero for the model that
tried them and possibly more for a weaker one. The 242 certified tasks sit higher, 197 at the full
description, 11 at the test names, and 34 at the test file. The bucket that failed every level held
29 tasks before the upper levels were measured. Every audited one had a defective description, the
rest certified once a higher level supplied what the prose left out, and only `exprhash` remains.

The tasks are new, but their answer keys are upstream code from widely used repositories, so a
model may have seen a removed function in training, and memorization cannot be ruled out. Two
things limit it. No task file references an issue, pull request, or CVE, so nothing in the prompt
names the code to recall. And the answer keys are 103k added lines against 638 non-stub
deletions, behavior to rebuild instead of a known diff to replay. A direct probe, asking a model for
each function from its name alone and comparing the output with the answer key, would measure
what is left, and it is the next check.

### Cost and what it limited

Stage 1 cost $1.2k, paid by one researcher, and the budget shaped the dataset more than any design
choice did.

| Model | Runs or sessions | Cost | Share | Per run |
|---|---:|---:|---:|---:|
| Composer 2.5 | 1.4k runs | $678 | 59% | $0.47 |
| Devin swe-2-max | 151 sessions | $452 | 39% | $2.99 |
| Grok 4.7 and 4.6 | 48 runs | $26 | 2% | $0.55 |

Almost all of it paid for reading. Of 6.6 billion tokens, 6.3 billion were cache reads, a model re-reading a
repository it had already loaded. Most of the bill went to the two runs every certificate needs.
The levels above L2 cost $0.96 a run, more than three times an L2 run, because only harder tasks
reach them and the solver has a test file to read.

| Level | Runs | Cost | Per run |
|---|---:|---:|---:|
| L1, the screen | 541 | $198 | $0.37 |
| L2, the certificate | 834 | $225 | $0.27 |
| Levels above L2 | 97 | $93 | $0.96 |

Authoring was cheap, near $1.25 a task in an earlier, incomplete measurement. Grading was not, at
7.0 runs and $4.80 per certificate, so the factory made tasks faster than the budget could grade
them. That gap sets the dataset's limits.

- **155 of the 591 authored tasks never ran**, and 21 more ran without reaching a verdict.
- **Most grades are Composer's.** It was the cheapest per run, so it screened 374 of the 436 tasks that
  ran and carried most climbs above L2.
- **The second model is thin.** Devin costs about six times as much per run, so only 136 tasks have
  its L1 screen and 40 have two independent climbs. Grok ran only the three tasks at the top.
- **Most levels ran once per task per model.** One run cannot separate a model that needs the
  information from one that got lucky, and Grok's one pass in two on `httpmux` is that case.
- **The 172 tasks solved from the bug report carry one model's grade.** Composer graded 132,
  Devin 36, and Grok 3, and only one was solved from the bug report by two models.

At Stage 1 prices, about $2.2k would buy the two measurements this budget could not. Three repeat
runs on 50 tasks at L1 and L2, from both models, would show how often a grade changes on a rerun.
Both models climbing the same random 100 tasks would remove the selection in the model comparison,
since Devin now mostly sees tasks Composer failed. A second model climbing all 415 graded tasks
would cost about $4.3k.

<figure class="fig-inline">
{% include "figures/information-gap/runs-per-level.svg" %}
<figcaption>Runs with a verdict at each level, stacked by model. The upper levels and the second models are where the budget ran out.</figcaption>
</figure>

The one saving that worked was refusing runs whose outcome was already known, which cut the runs
per certificate about fourfold.

<figure class="fig-inline">
{% include "figures/information-gap/runs-per-certificate.svg" %}
<figcaption>Runs spent per certificate under three schedules. Gating is worth about 4×. Running trials in sequence, on its own, is worth almost nothing.</figcaption>
</figure>

Two caveats on the tokens. Composer and Grok count cached tokens inside their input and Devin
counts them on top, so each total follows its vendor's convention. Devin also bills in Agent
Compute Units, and its tokens at the SWE-2 promotional rate ($452) and its 185.5 ACUs at the $2.25
list rate ($417) agree within 8%. The Devin figures come from an earlier export.

## Conclusion and future work

Difficulty is a relation between a task, a model, and an amount of information. The ladder sets the
information and reads off the other two. Four lessons carry to any task factory: put the difficulty
in the prompt, run two prompts, keep the test writer away from the answer key, and build the guards
before the generator.

Stage 1 is small because of its budget, with one language, nine repositories, and mostly one model.
Three questions come next.

- **Does the cut work outside Go?** Stage 2 runs the same factory in a second language.
- **Does a certificate transfer?** A second model has screened 75 certified tasks at L1, and so far
  the answer depends on the repository. It solved eight of ten `go-github` tasks from the bug
  report, whose issues name the fields the code turns on, and nine of 65 everywhere else.
- **What does the curve above L2 look like?** 81% of certificates bind at the full description and
  14% only once the test file is in the tree. With both models on the ladder, Composer's
  certificates bind at the full description 76% of the time and Devin's 84%.

---

*Code and trial ledger:
[open_swe_traces_research](https://github.com/Evan-Kim2028/open_swe_traces_research). Counts are a
2026-09-23 snapshot of the finished Stage 1 run, derived from `trial_ledger.py` and `roots.py`.
Figures regenerate from the ledger with `scripts/information-gap-figures.py`. Earlier in this
series: [Terminal-Bench Task: Lakehouse Schema Contract
Drift](/writings/terminal-bench-task-lakehouse-schema-contract-drift/) and [Four Verifiable
Properties of a Useful Agent Task](/writings/four-verifiable-properties-of-a-useful-agent-task/).*
