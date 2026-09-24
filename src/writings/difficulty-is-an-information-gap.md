---
title: "The Information Ladder: Measuring Model Capabilities"
date: "2026-09-23"
collection: data
lede: false
table_highlight: true
tags:
  - writing
  - data
  - evals
  - benchmarks
  - agents
  - harbor
  - synthetic-tasks
source_url: https://github.com/Evan-Kim2028/open_swe_traces_research
source_platform: github
slug: difficulty-is-an-information-gap
description: "We build LadderBench, 591 synthetic Go tasks from 9 repositories, and use the information ladder to certify 242 of them and compare Composer 2.5 and SWE-2. Each level reveals more to the solver, so the first level a model passes shows how much information it needed."
series: Evals
series_index: 3
hero: /assets/images/information-gap-hero.png
hero_dark: /assets/images/information-gap-hero.dark.png
---

<!-- vale House.FirstPerson = NO -->
<!-- vale Google.Headings = NO -->
<!-- vale Google.Slang = NO -->

## TL;DR

- **The prompt decides whether a task is solvable.** 59% of graded tasks fail from a bug report and
  become solvable with more information, 81% of them once the model gets the full description.
- **Solve rates hide real differences between models.** On 32 of 73 shared tasks, Composer 2.5 and
  SWE-2 need different amounts of information, and on tasks with long descriptions they agree only
  25% of the time.
- **Information replaces search.** When extra information turns a failure into a pass, the model
  makes 24–32% fewer reads and searches.

## Intro

What makes a coding task difficult? One answer is how much information the solver has. If an agent
can look the answer up, the task is trivial. We build on that idea with an information ladder,
creating 6 prompts for one task that gradually reveal more information to the solver: from a bug
report that names only the symptom (L1), to a full description of every behavior the tests check
(L2), up to the hidden tests themselves.

The ladder gives each task a second dimension, so we can mark the point where it goes from
unsolvable to solvable and certify a model's capability there. We generate LadderBench, a dataset of
591 synthetic Go tasks from 9 open-source repositories, and grade 411 of them over 1,608 trials in
[Harbor](https://github.com/harbor-framework/harbor), certifying 242.

### Related Work

Existing coding benchmarks and task generators treat difficulty as a property of the task. They
inherit it from a real issue or commit, set it by the size of an injected bug or the number of
features removed, or keep the tasks a screening model fails. Each gives the solver a single prompt,
so a failed task could be hard or just underspecified, and the result cannot tell which.

We treat difficulty as a relation between a task, a model, and an amount of information. The
information ladder gives each task 6 prompts, each containing everything in the one below, which is
the setting of [Blackwell's comparison of
experiments](https://en.wikipedia.org/wiki/Blackwell%27s_informativeness_theorem) from decision
theory. That ordering turns pass or fail into a measurement: the first level a model passes is how
much information it needed, and a task that fails from the bug report (L1) but passes from the full
description (L2) is shown to be both hard and solvable.

The closest relative, CodeMidas, also builds tasks from source code alone. Its agents write
behavioral specifications, ground the tests in running the original code, and filter tasks by how
often repeated solution attempts pass. Our tests are written blind, without the original code, and
instead of filtering tasks by pass rate, **the ladder measures how much information each model needs
to solve the task successfully.**

| Work | Source | Difficulty set by | Prompts | Hard vs. underspecified |
|---|---|---|:-:|:-:|
| **Information Ladder (ours)** | Source code | Prompt information | **6** | **Yes** |
| [SWE-bench](https://arxiv.org/abs/2310.06770) | GitHub issues | The issue | 1 | No |
| [SWE-Gym](https://arxiv.org/abs/2412.21139) | GitHub issues | The issue | 1 | No |
| [R2E-Gym](https://arxiv.org/abs/2504.07164) | Commits | The commit | 1 | No |
| [SWE-smith](https://arxiv.org/abs/2504.21798) | Injected bugs | The bug | 1 | No |
| [ProgramDistill](https://arxiv.org/abs/2609.18805) | Web app features | Features removed | 1 | No |
| [CodeMidas](https://arxiv.org/abs/2609.22068) | Source code | Rollout filtering | 1 | No |

## The Information Ladder

### Six Levels of Information

The ladder follows [Blackwell's
theorem](https://en.wikipedia.org/wiki/Blackwell%27s_informativeness_theorem) from decision theory:
one source of information is more informative than another exactly when every decision maker does at
least as well with it. Each level contains everything in the one below, so a solver that uses
everything it reads can only gain by climbing.

The ladder holds the task fixed and changes only what the solver sees. The code, the hidden tests,
and the answer key (the code removed to make the task) stay the same at every level. Each level adds
information to the one below: words in the prompt through L4, then test code in the repository at L5
and L6. A model's grade on a task is the first level it passes, and a task that fails at L1 and
passes higher up is certified at that level.

Take `httpmux`, from [goa's HTTP package](https://github.com/goadesign/goa/tree/v3/http), where an
agent cuts out the router, 109 lines of `http/mux.go`, and keeps it as the answer key. The same
agent writes the bug report the way a user files an issue. A separate agent writes the full
description after reading the answer key and the hidden tests, so it spells out every behavior they
check.

| Level | The solver gets | For `httpmux` |
|---|---|---|
| L1 bug report | The symptom and a command to reproduce it | 75 words, opening "Registering a route, serving a request, reading path variables, or resolving the matched pattern panics." |
| L2 full description | Every behavior the tests check, one line per assertion, with worked examples | 567 words, such as "`{*name}` captures the whole remainder" |
| L3 test names | L2 plus the names of the hidden tests | `TestDetail01_WildcardForms` through `TestDetail10_WildcardNameClass` |
| L4 signatures | L3 plus the exported signatures as stubs | Nothing new, because the cut already left them |
| L5 one test | L4 plus one hidden test file in the repository | `mux_hidden_test.go`, 431 lines |
| L6 all tests | Every hidden test in the repository | Nothing new, because that was the only file |

Figure 1 below shows that the full description carries most of the ladder's added words, the same
step where most tasks become solvable (89% of graded tasks by L2). From L5 the information changes
kind, from prose to test code, so the charts group the levels into 4 steps: L1, L2, L3–4, and L5–6.

<figure class="fig-inline">
{% include "figures/information-gap/prompt-words.svg" %}
<figcaption><strong>Figure 1:</strong> What each level adds, in medians. Prompt words (blue) grow through the test names. Test code (orange) is zero until L5, because the hidden tests stay outside the solver's container until then.</figcaption>
</figure>

### Task Certification

When a model fails a benchmark task, the failure is ambiguous: the task may be hard, or its prompt
may leave out something no solver could guess. The information ladder removes the ambiguity by
bounding the model's capability between 2 levels, the highest one it fails and the first one it
passes, and that bound certifies the task. Most certificates take 2 trials. Failing at L1 shows the
task is hard for that model from a bug report alone, and passing at L2 shows it is solvable from a
description that names no file, line, or function to edit. If L2 fails too, the model keeps
climbing, and the certificate records the first level it passes.

How do we know a certificate is sound? A certificate at L2 claims the full description made the task
solvable, which holds only if the hidden tests are fair and the description is true. The factory
(Section 4.1) guards both before any grading. A model check drops behaviors no solver could derive,
the tests are written blind from the public API, the description is derived from the tests, and
Docker proves that the answer key passes while the cut repository and a hardcoded fake fix fail.

## The Factory

### Agentic Task Generation

Three agents build each task, with model checks between them and a Docker gate at the end. Every
task ships as a [Harbor](https://github.com/harbor-framework/harbor) task: a Dockerfile, the hidden
tests, and a config that lets the solver reach only its model vendor's API and runs the grader with
no network. Harbor builds the container and runs every graded trial.

1. **Cut.** The first agent removes one self-contained behavior from a Go repository, keeps it as
   the answer key, and writes the bug report, a list of behaviors to restore, and a fake fix that
   hardcodes the test inputs.
2. **Screen.** A model check reads each behavior on the list using only what the solver can see
   and drops any behavior no solver could work out, like the value of an internal constant.
3. **Write blind tests.** The second agent writes one hidden test per behavior. It sees the behavior
   list and the public API but never the removed code, and the tests check thousands of seeded
   random inputs, so any correct implementation passes.
4. **Describe.** The third agent reads the answer key and the tests and writes the full description,
   one line per assertion. A second model check compares the description against the tests and flags
   any line that is missing or contradicts them.
5. **Validate.** The task's Docker image must reject any task a correct solver could fail or a wrong
   one could pass. The answer key must pass, the cut repository must fail, and the fake fix must
   fail. The answer key may never edit a test file.

Our initial research with the factory covers Go only. Agents authored the 591 tasks in LadderBench,
and 93% passed validation on the first try. Of the 591, 432 ran and 411 reached a verdict. The
median answer key adds 100 lines, and about 12% touch 2 or more files.

Each cut can yield 6 prompts, one per level, with no further authoring, so the 591 cuts support up
to 3,546 prompts. Figure 2 shows the yield of the 407 graded tasks with a recorded repository. Every
repository produced certified tasks, and the answer keys change only about 14% of the repositories'
source files, so the budget (Section 4.3) set the limit rather than the repositories.

<figure class="fig-inline">
{% include "figures/information-gap/repo-yield.svg" %}
<figcaption><strong>Figure 2:</strong> Graded tasks per repository. Solid bars are certified tasks, which failed the bug report and passed higher up. Faded bars are too easy, having passed the bug report. The right column is the share of each repository's graded tasks that certified.</figcaption>
</figure>

### Trial Integrity

A pass should mean the model fixed the code. Harbor enforces most of that, and audits of the traces
check the rest.

1. **Isolation.** During a trial the container reaches only the model vendor's API, the grader runs
   with no network, and the repository ships without its git history.
2. **Protected tests.** Below L5 the hidden tests stay outside the container. At L5 and L6 the
   grader checks the test file's sha256, so an edited copy scores zero.
3. **Trace audit.** We audited 123k tool calls and found 1 web fetch of the file under test, and
   that pass counts as no verdict. Another 55 passing trials edited a test file, and none of those
   edits can change what the hidden tests check.
4. **Real zeros.** A zero counts only if the tests ran and failed. A separate check caught 69
   verdicts on 13 tasks whose tests never compiled. Those tasks ran again once they passed
   validation, and 5 left LadderBench.

### Cost Limitations

All of this work drew on one researcher's subscriptions rather than metered API billing and used up
most of that allowance, so the budget was exhausted all the same. The table prices the same usage at
API rates to show its scale: 7.9 billion tokens, about $1.4k, with SWE-2 at its promotional rate of
75% off list.

| Work | Trials or sessions | Tokens | Cost at API prices |
|---|---:|---:|---:|
| Composer 2.5, grading | 1,447 trials | 3.0B | $682 |
| SWE-2 (Devin), grading | 304 sessions | 1.8B | $284 |
| SWE-2 (Devin), authoring | 213 sessions | 3.0B | $378 |
| Grok, authoring and a pilot | 21 trials, 24 sessions | 0.2B | $55 |
| **Total** | | **7.9B** | **$1.4k** |

The factory made tasks faster than the subscriptions could grade them, so 159 of the 591 authored
tasks never ran. Measuring every task at every level 3 times with both models would take about 12
times the trials made here, so the limit is compute, not method.

## Results

The results come from the 411 graded tasks. The first subsection shows what the added information
does inside a trial, and the second uses the ladder to compare the two models.

### Information Replaces Search

For every task a model failed and later passed higher up, 209 for Composer and 69 for SWE-2, we
compare its first passing trial with the failed trial just below it. The passing trial takes 15%
fewer tool calls for Composer and 17% fewer for SWE-2. Nearly the whole saving is exploration: read
and search calls fall by 24% and 32%, while the number of test runs stays flat. The added
information does the searching the model would otherwise have done. Failed trials are also longer,
73 calls against 54 for Composer and 76 against 63 for SWE-2, so a call budget could stop a likely
miss early.

<figure class="fig-inline">
{% include "figures/information-gap/trace-flips.svg" %}
<figcaption><strong>Figure 3:</strong> Same task, same model: the failed trial just below the first passing level, and that passing trial. The calls both models drop are reads and searches.</figcaption>
</figure>

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
<figcaption><strong>Figure 4:</strong> Each lane is one model on one task. The tint runs from the bug report to the first pass, so its length is how much information that model needed. A filled dot is a pass and a ring is a fail.</figcaption>
</figure>

Figure 4 shows what that looks like on single tasks. On `archive` and `defval`, both models fail the
bug report, which a solve rate scores as a tie, yet SWE-2 passes from the full description while
Composer needs the test file. The widest gap is `ipqueue`, where SWE-2 passes straight from the bug
report and Composer needs the test file. The gap also runs the other way: on `advrefs` Composer
passes at L2 while SWE-2 needs the test file. On `httperrexpr` the models tie at L2, and `httpmux`
falls to Composer only once the test file is in the tree.

Description length appears to predict where the models disagree. They agree on 67% of tasks with a
short full description, 75% with a middling one, and only 25% with a long one (Figure 5). Where they
disagree, the median description runs 716 words, and where they agree, 532. A longer description
gives a model more to use but also more to miss, and the two models handle that differently.

<figure class="fig-inline">
{% include "figures/information-gap/agreement-by-length.svg" %}
<figcaption><strong>Figure 5:</strong> Composer and SWE-2 grades on the 72 of the 73 tasks both models graded that have a recorded description length, split into thirds by the length of the full description. The models agree on 67% of tasks with a short description, 75% with a middling one, and 25% with a long one.</figcaption>
</figure>

## Conclusion

Difficulty is a relation between a task, a model, and an amount of information. The ladder sets the
information and reads off the other two, and the traces show the information standing in for the
search a model would otherwise do. 4 lessons carry to any task factory: put the difficulty in the
prompt, run 2 prompts, keep the test writer away from the answer key, and build the validation
checks before the generator.

These results have 3 main limitations. Most levels ran once per task per model, so a single trial
cannot separate a model that needs the information from one that got lucky, and part of the
disagreement between models may be noise. The two models also did not climb the same tasks: Composer
screened 374 of the 432 tasks that ran, and SWE-2 mostly received tasks Composer had already failed
at L1, so part of the gap between them may come from which tasks each one saw. Finally, the levels
of a task nest by design, so a training or evaluation split should keep all of a task's levels on
one side.

The information ladder also opens several research directions. The framework is not specific to Go
and should generalize to any language with a test suite, starting with a second language next.
Repeat trials at each level would show how stable a certificate is, and having several models climb
the same random tasks would place their capabilities on one scale. Every level comes from one task,
so the ladder can also test whether a pass comes from reasoning or from memorized upstream code, and
it could serve as a training curriculum that withholds more information as a model improves.

---

*Code, trial data, and figure scripts:
[open_swe_traces_research](https://github.com/Evan-Kim2028/open_swe_traces_research). Earlier in this
series: [Terminal-Bench Task: Lakehouse Schema Contract
Drift](/writings/terminal-bench-task-lakehouse-schema-contract-drift/) and [Four Verifiable
Properties of a Useful Agent Task](/writings/four-verifiable-properties-of-a-useful-agent-task/).*
