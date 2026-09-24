---
title: "The Information Ladder: Measuring Model Capabilities"
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
description: "Each coding task gets six prompts, from a bug report to the hidden tests, and a model is certified at the first one it passes. We use the ladder to certify 242 synthetic Go tasks across nine repositories and compare Composer 2.5 and SWE-2."
series: Evals
series_index: 3
hero: /assets/images/information-gap-hero.png
hero_dark: /assets/images/information-gap-hero.dark.png
---

<!-- vale House.FirstPerson = NO -->
<!-- vale Google.Headings = NO -->

## Intro

What makes a coding task difficult? One answer is how much information the solver has. If an agent
can look the answer up, the task is trivial. We build on that idea with an information ladder, creating 6
prompts for one task that gradually reveal more information to the solver: from a bug report
that names only the symptom (L1), to a full description of every behavior the tests check (L2),
up to the hidden tests themselves. The ladder gives each
task a second dimension, so we can mark the point where it goes from unsolvable to solvable and
certify a model's capability there. We test the approach on 591 Go tasks from 9 open-source
repositories, grading 411 of them over 1,608 runs and certifying 242.

- **59% hit rate: hard at L1, solvable higher up.** Of the 411 graded tasks, 242 are hits, and we
  certified 81% of them at L2, once the solver had the full description. The remaining 169 (41%)
  passed the bug report and are too easy.
- **Information replaces search.** A passing run makes 24–32% fewer reads and searches
  than the failed run one level below it.
- **Models differ in capabilities.** Composer 2.5 and SWE-2, the models behind Cursor and Devin,
  need different amounts of information on 32 of the 73 tasks both graded, and differ most where
  the full description runs long.
- **Grading drives the cost.** Agents authored all 591 tasks for $409 (3.1 billion tokens), and 93% passed
  validation on the first try. Grading took $990 (4.9 billion tokens), for about $1.4k in total at API
  token prices.

## The Information Ladder

### Six Levels of Information

The ladder follows Blackwell's theorem from decision theory. By Blackwell's theorem, one source of
information is more informative than another exactly when every decision maker does at least as well
with it. Each level contains everything in the one below, so a solver that uses everything it reads
can only gain by climbing.

The ladder holds the task fixed and changes only what the solver sees. The code, the hidden tests,
and the answer key stay the same at every level, and each level adds information to the one below:
words in the prompt up to L4, then test code in the repository at L5 and L6. A model's grade on a
task is the first level it passes, and a task that fails at L1 and passes higher up is certified at
that level.

Take `httpmux`, from [goa's HTTP package](https://github.com/goadesign/goa/tree/v3/http), whose
task removes the router, 109 lines of `http/mux.go`. An agent writes the bug report the way a user
files an issue. A separate agent writes the full description after reading the answer key and the
hidden tests, so it spells out every behavior they check.

| Level | The solver gets | For `httpmux` |
|---|---|---|
| L1 bug report | The symptom and a command to reproduce it | 75 words, opening "Registering a route, serving a request, reading path variables, or resolving the matched pattern panics." |
| L2 full description | Every behavior the tests check, one line per assertion, with worked examples | 567 words, such as "`{*name}` captures the whole remainder" |
| L3 test names | L2 plus the names of the hidden tests | `TestDetail01_WildcardForms` through `TestDetail10_WildcardNameClass` |
| L4 signatures | L3 plus the exported signatures as stubs | Nothing new, because the cut already left them |
| L5 one test | L4 plus one hidden test file in the repository | `mux_hidden_test.go`, 431 lines |
| L6 all tests | Every hidden test in the repository | Nothing new, because that was the only file |

Figure 1 below shows that the full description carries most of the ladder's added words, which is
also the step where most tasks become solvable, 89% of graded tasks by L2. From L5 the information changes kind,
from prose to test code, so the charts group the levels into 4 steps: L1, L2, L3–4, and L5–6.

<figure class="fig-inline">
{% include "figures/information-gap/prompt-words.svg" %}
<figcaption><strong>Figure 1:</strong> What each level adds, in medians. Prompt words (blue) grow through the test names. Test code (orange) is zero until L5, because the hidden tests stay outside the solver's container until then.</figcaption>
</figure>

### Information Replaces Search

For every task a model failed and later passed higher up, 209 for Composer and 69 for SWE-2, we
compare its first passing run with the failed run just below it. The passing run takes 15% fewer
tool calls for Composer and 17% fewer for SWE-2. Nearly the whole saving is exploration: read and
search calls fall by 24% and 32%, while test runs hold level. The information does searching the
model would otherwise have done. Failed runs also run longer, 73 calls against 54 for Composer and
76 against 63 for SWE-2, so a call budget could stop a likely miss early.

<figure class="fig-inline">
{% include "figures/information-gap/trace-flips.svg" %}
<figcaption><strong>Figure 2:</strong> Same task, same model: the failed run just below the first passing level, and that passing run. The calls both models drop are reads and searches.</figcaption>
</figure>

### Task Certification

When a model fails a benchmark task, the failure is ambiguous: the task may be hard, or its prompt
may leave out something no solver could guess. The information ladder removes the ambiguity by
bounding the model's capability between 2 levels, the highest one it fails and the first one it
passes, and that bound certifies the task. Most certificates take 2 runs. Failing at L1 shows the
task is hard for that model from a bug report alone, and passing at L2 shows it is solvable from a
description that names no file, line, or function to edit. If L2 fails too, the model keeps
climbing, and the certificate records the first level it passes.

How do we know a certificate is sound? A certificate at L2 claims the full description made the
task solvable, which holds only if the hidden tests are fair and the description is true. 4
checks guard that before any grading:

1. **Blind tests.** The hidden tests come from a list of behaviors and the public API, never the
   answer key, and check thousands of seeded random inputs, so any correct implementation passes.
2. **Execution gates.** In the task's Docker image, the answer key must pass, the cut repository
   must fail, and a fake fix that hardcodes the test inputs must fail.
3. **A description drawn from the tests.** The full description is written from the hidden tests,
   one line per assertion, and every line must hold for the answer key.
4. **A derivability judge.** A separate judge agent reads each line using only what the solver can
   see and drops any line no solver could work out, like the value of an internal constant.

### Comparing Model Capabilities

A solve rate says whether a model passed. The ladder says how much information it needed, so holding
the task fixed and changing the model compares capability in a unit a solve rate cannot see.
Composer 2.5 screened most tasks, and SWE-2 climbed tasks Composer had already screened.

The two models differ more than their solve rates suggest. We say the models agree on a task when
both first pass at the same level. On the 73 tasks both graded, they agree on 41, and their grades
are only weakly correlated (0.29 on a scale where 1 means the models rank every task the same way).
Where both earned a certificate, on 36 tasks, they need the same level on 23, SWE-2 needs less on
10, and Composer needs less on 3. A task that is hard for one model is only loosely hard for the
other.

<figure class="fig-inline">
{% include "figures/information-gap/curves.svg" %}
<figcaption><strong>Figure 3:</strong> Each lane is one model on one task. The tint runs from the bug report to the first pass, so its length is how much information that model needed. A filled dot is a pass and a ring is a fail.</figcaption>
</figure>

Figure 3 shows what that looks like on single tasks. On `archive` and `defval`, both models fail the
bug report, which a solve rate scores as a tie, yet SWE-2 passes from the full description while
Composer needs the test file. The widest gap is `ipqueue`, where SWE-2 passes straight from the bug
report and Composer needs the test file. The gap also runs the other way: on `advrefs` Composer
passes at L2 while SWE-2 needs the test file. On `httperrexpr` the models tie at L2, and `httpmux`
falls to Composer only once the test file is in the tree.

Description length appears to predict where the models disagree. They agree on 67% of tasks with a
short full description, 75% with a middling one, and only 25% with a long one (Figure 4). Where they
disagree, the median description runs 716 words, and where they agree, 532. A longer description
gives a model more to use but also more to miss, and the two models handle that differently.

<figure class="fig-inline">
{% include "figures/information-gap/agreement-by-length.svg" %}
<figcaption><strong>Figure 4:</strong> Composer and SWE-2 grades on the 72 of those 73 tasks with a recorded description length, split into thirds by the length of the full description. The models agree on 67% of tasks with a short description, 75% with a middling one, and 25% with a long one.</figcaption>
</figure>

## The Factory

### Building a Task

Agents build each task and Docker checks it by execution, with no person in the loop.

1. **Cut.** An agent removes one self-contained behavior from a Go repository, keeps it as the
   answer key, and writes the bug report and a list of behaviors to restore.
2. **Write blind tests.** A second agent writes one hidden test per behavior from the list and the
   public API, never the removed code, so the tests check what a caller can see.
3. **Validate.** Docker builds the task and rejects any task a correct solver could fail or a
   wrong one could pass. The answer key must pass and the cut repository fail, a fake fix that
   hardcodes the test inputs must fail, and the answer key may never change a test file.
4. **Describe.** A third agent reads the answer key and the tests and writes the full description,
   one line per assertion. A judge then drops any line no solver could work out.
5. **Grade.** The task runs at L1, then at L2, and climbs the ladder only if L2 fails.

### Yield and Headroom

Agents authored the 591 tasks over 3 days, and validation passed 93% of them on the first try. Each
authored task yields a family of prompts without further authoring, because every level of the
ladder comes from the same cut. The 9 repositories still have room to spare, since the answer keys
change only about 14% of their source files, and adding a repository takes a base image and a
validation pass.

### Keeping the Grade Honest

A pass should mean the model fixed the code. During a run the container reaches only the model
vendor's API, the grader runs with no network, and the repository ships without its git history.
Below L5 the hidden tests stay outside the container, and at L5 and L6 the grader checks the test
file's sha256, so an edited copy scores zero. We audited 123k tool calls and found 1 web fetch of the
file under test, and that pass counts as no verdict. Another 55 passing runs also edited a test
file, and none of those edits can change what the hidden tests check. A zero counts only if the tests ran and
failed, and a separate check caught 69 verdicts on 13 tasks whose tests never compiled. Those ran
again once their tasks passed validation, and 5 tasks left the dataset.

## The Synthetic Dataset

### The Graded Tasks

The tasks come from 9 Go repositories: client-go, kops, helm, go-git, go-github, goa, gin, bbolt,
and nats-server. The median answer key adds 100 lines, and about 12% touch 2 or more files.

<figure class="fig-inline">
{% include "figures/information-gap/funnel.svg" %}
<figcaption><strong>Figure 5:</strong> 591 tasks authored and 411 graded on the ladder. The rest never ran, or ran without reaching a verdict.</figcaption>
</figure>

### Cost and What It Limited

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
never ran. Measuring every task at every level 3 times by both models would take about 12
times the runs of Stage 1, and that gap is compute, not method.

<figure class="fig-inline">
{% include "figures/information-gap/runs-per-level.svg" %}
<figcaption><strong>Figure 6:</strong> Runs with a verdict at each ladder step, stacked by model. The upper steps and the second model are where the budget ran out.</figcaption>
</figure>

### What These Data Can and Cannot Show

Most levels ran once per task per model, so one run cannot separate a model that needs the
information from one that got lucky, and part of the disagreement between models may be noise.
Selection shapes the comparison, since Composer screened 374 of the 432 tasks that ran and most
tasks SWE-2 saw were ones Composer had failed. The levels of a family nest by design, so a training or
evaluation split should keep each family on one side. The answer keys are upstream code from
widely used repositories, and our next check is a probe for memorized functions. The ladder also
assumes a model uses everything it reads, and a model can miss a line or get lost in a longer
prompt. On 26 tasks where a model passed a level and also ran higher up, it failed a higher level on
5. 4 of those rest on a single passing run, but `helm-repindex` passed 6 of 31 runs from the full
description and none of 21 once the test names were added.

## Related Work and Conclusion

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
search a model would otherwise do. 4 lessons carry to any task factory: put the difficulty in
the prompt, run 2 prompts, keep the test writer away from the answer key, and build the guards
before the generator.

Stage 1 is small because of its budget, and 3 questions come next. Does the cut work outside
Go, which we test in Stage 2 with a second language? Does the disagreement between models survive 3
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
