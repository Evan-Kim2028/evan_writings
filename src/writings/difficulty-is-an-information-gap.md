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
description: "Stage 1: Go, nine repositories, 591 tasks. The information ladder sets what a prompt withholds, and the factory uses it to build a synthetic dataset."
series: Evals
series_index: 3
hero: /assets/images/information-gap-hero.png
hero_dark: /assets/images/information-gap-hero.dark.png
---

## Summary

Difficulty is an information gap.

A coding task is hard when the prompt leaves out something the solver needs and cannot work out
from what remains. Widen the gap and the task gets harder. Close it and the task gets solved. The
ladder sets the width, one level at a time.

The factory below is built around that ladder. Cut a working behavior out of a real Go repository. Have a
second agent write hidden tests from a written specification, never from the code. Then run the
same model twice. The first run gets only a bug report. The second gets a full description of every
behavior those tests check. Keep the task when the first fails and the second passes.

Those two runs are how a task enters the synthetic dataset. The failure shows the task is hard.
The pass shows it is solvable as written. One prompt cannot show both, and every comparable generation pipeline uses one prompt.

Stage 1 is Go, nine repositories, self-funded: 591 tasks authored and 238 certified so far.

## The information gap

### The ladder

A generated coding task can fail two ways that look identical from the outside. It can be too easy,
in which case it separates no two models. Or it can be underspecified, where the prompt never
carried enough for anyone to solve it, so every model fails and the failure says nothing about
ability. Both show up as a number in a results table, and a solve rate cannot tell them apart. Most
pipelines carry no other instrument.

Both failures are about information. A task is too easy when the prompt plus what the repository
still shows already contains the answer. It is underspecified when the two together leave out
something nobody could derive. The ladder therefore makes information the thing to set and measure.

Each level contains the one below it and adds one kind of information about the removed behavior.
Nothing above the level is visible.

A certificate uses two of them. The task fails the bug report and passes the full description.
From the next level up, the levels hand over the tests, and a certified task never sees a test
name.

| Level | Name | What it adds over the level below |
|---|---|---|
| L0 | Bug report | The symptom, and how to reproduce it. The implementation is gone. |
| L1 | Partial description | Every requirement but one, in prose. |
| L2 | Full description | Every behavior the hidden tests check, one line per assertion. |
| L3 | Test names | The names of the hidden tests, and a one-line summary of each. |
| L4 | Signatures | The exported function signatures, as empty stubs. |
| L5 | One test | The full body of one hidden test file. |
| L6 | All tests | Every test in the tree. |

The rings are even steps. They show containment, not an amount. Blackwell's theorem is why the
containment matters: an agent with the richer prompt can ignore what was added, so the richer
prompt is at least as useful. A pass on the full description leaves the bug report undecided, so
both runs are made.

From the bug report to the full description, the levels change the prose.

The ladder builds a task when the levels are written for it. The same ladder edits a task that
already exists: remove what a level added, or add the next level, and leave the tests fixed.
Mapping the names onto Terminal-Bench by instruction content, without that edit, puts almost
every task at L1, a goal plus unstated requirements plus hidden tests. A benchmark that does not
vary information cannot be used to study information.

### Why the prompt has to carry it

If the gap sets difficulty, everything the repository still shows is part of the gap. Three leaks
account for most of what has to be closed.

**Call sites.** Cut a function out of a dependency, leave its callers intact, and the call sites
specify the contract. Argument shapes, call order, and what the caller asserts afterward are enough
to reconstruct it. Nineteen of 23 such tasks were solved from the bug report alone. Obscurity does
not help, because reconstruction from usage needs no recall: a round aimed at behavior no model
could have memorized came in at 12 of 14.

**Tests in the tree.** A complete test suite is a specification. Every task that kept its
in-tree tests was solved, 36 of 36 for one model and 26 of 26 for another.

**Test names.** Before a check caught it, hidden test names handed over the name of the removed
function on every task.

The same principle explains why structural complexity does not create difficulty. A generator with eight knobs sets exactly that: call hops, edit sites, decoy locations, cross-module placement,
test sparsity, guard tests, interface removal. Twenty-five tasks, up to seven functions deleted
across four files. A frontier model passed all 25, and the knobs moved solve time from 1.34 minutes
to 7.57 without moving the outcome. Rearranging code does not remove information. It moves the
information somewhere less convenient.

### The certificate

A task earns a place in the synthetic dataset on two runs by one model. The first
gives it only a bug report, and it fails. The second gives it a full description of every behavior
the hidden tests check, and it passes.

The L0 failure shows the task is hard. Not hard in the abstract. Hard for a named model at a named
amount of information, which is the only kind of hard that means anything.

The L2 pass shows the task is fair. Somebody did it, from a prompt naming no file, no line number,
no symbol, and no diff. One prompt cannot give you that second claim. A single failing run is
ambiguous between a hard task and an impossible one, and re-running it does not help, because both
readings predict the same failure.

### The inversion test

The ladder could still be a story imposed after the fact. Tasks at low levels might fail for reasons that
have nothing to do with information. Here is the test that separates the two readings.

Take eight tasks a model passes at L2. Hold the code, the tests, the repository, and the model
fixed. Invert one line of the written description so it states the opposite of what the removed
code did.

Seven of the eight flipped to failing, each on exactly the property that was inverted.

One sentence of prose moved and the outcome moved with it. The description carries the task. Two
findings from the same audit back this up: 40% of the first batch described the removed code
incorrectly, and all seven tasks investigated that failed at both L0 and L2 turned out to have a
defective description rather than being impossible.

A level is therefore a claim about what a competent programmer could work out from what they were
handed. If the prose is wrong, the level is a lie, and the run measures the prose instead of the
model’s ability.

### When the ladder runs out

Three tasks failed every rung. Composer 2.5 took the bug report, the full description, the test
names, the signatures, a restored test, and finally every test in the tree, and failed all six
levels on `exprhash`, `httpencoding` and `httpmux`.

That repeats the ambiguity the certificate removes, at the other end of the ladder. Failing at L6
reads equally as a task at the edge of what a model can do and as a task nobody can do, and
re-running the same model separates neither reading, for the same reason a repeated L0 failure
does not. A second prompt cannot settle it either, because no wider prompt exists. L6 hands over
the entire suite.

The second claim therefore has to come from a second model. Grok 4.7 ran the complete ladder on
all three, measuring every level rather than inferring it from the one below.

| Task | Composer 2.5 | Grok 4.7 |
|---|---|---|
| `httpencoding` | fails L0 through L6 | fails L0 through L5, **passes L6** |
| `httpmux` | fails L0 through L6 | fails L0 through L5, **passes L6** |
| `exprhash` | fails L0 through L6 | fails L0 through L6 |

Two of the three are solvable, and now carry a certificate saying so. Both Grok certificates bind
at L6 over a recorded L5 failure, so neither rests on a skipped rung. Composer failed both tasks
with every test in front of it.

`exprhash` did not resolve, and it is not a broken task. Its answer key restores the removed code
and passes the hidden suite, the A1 check every task clears before it reaches a trial at all. It
is solvable by construction. Two frontier models, six levels each, 28 trials between them, and
neither wrote it.

Three things follow. A task can be hard for one frontier model and tractable for another at the
same level, which is the per-model claim the certificate makes, measured at the point where the
gap between models is widest. The ladder has a top, and a task can sit above it for a given model,
so a dataset that reports only "failed" at its highest level is reporting two different facts under
one word. And a second model does for an exhausted ladder what a second prompt does for a single
failing run: it is the instrument that separates hard from impossible when the first instrument has
run out of range.

### How other pipelines set difficulty

| Method | How difficulty is set | Evidence it is hard | Prompt proven |
|---|---|---|---|
| SWE-bench, SWE-Gym | inherited from the issue | reviewer judgment | ✗ |
| SWE-smith | not set; follows the injected bug | ✗ | ✗ |
| R2E-Gym | inherited from the commit | ✗ | ✗ |
| ProgramDistill | how many behaviors are restored together | authored depth | ✗ |
| CodeMidas | screening model drops always-pass and always-fail | the screening model failed it | ✗ |
| This work | what the prompt withholds, L0 against L2 | one model failed the bug report | ✓ the same model passed the full description |

The first three inherit difficulty from something a human already made, so it belongs to the pool
rather than to any one task. The last three set it per task.

CodeMidas is the closest relative, and the only other row that starts from source code alone
(Ye et al., [arXiv:2609.22068](https://arxiv.org/abs/2609.22068), Table 1). It keeps 5,545 tasks
across 23 languages, forty times this dataset, so the two differ somewhere other than scale. Every row above the last
can show that a model failed a task. Only a second prompt that passes separates a hard task from an
underspecified one. CodeMidas also builds its tests by running the original code, so its tests come
from the answer. These come from a written specification of it.

## The factory

### Four steps, three agents

These four steps are how the ladder gets built.

**The cut.** An agent reads a Go repository and removes one self-contained behavior. Public
signatures stay, so tests can still call them. The removed code becomes the answer key. The same
agent writes a bug report and a list of behaviors a solver should restore.

**Blind tests.** A second agent writes one hidden test per listed behavior. It sees the behavior
list, the public API, and the repository with the hole in it. It never sees the removed code. Tests
may only call exported functions.

**Execution checks.** Build the task in Docker and prove four things. The cut repository fails the
suite. Restoring the answer key makes it pass. A fake fix that hardcodes the test inputs still
fails. The answer key never touches a test file.

**The description.** A third agent reads the answer key and the tests together and writes the full
description, one line per assertion. Then one run at L0 and one at L2.

Keeping the first two agents apart is what makes the rest work. Suppose the agent that removed the
code also wrote the tests. Those tests would describe the implementation that is gone rather than
the behavior a caller can see, and a solver who writes different but correct code would fail for no
good reason.

### One task, two prompts

`gin-clientip` is a certified task. The cut removes gin’s request-introspection helpers: client IP
resolution behind proxies, scheme detection, content-type parsing, websocket detection. Composer
2.5 failed it at L0, then passed it at L2 three times out of three.

The entire L0 prompt, minus the no-network boilerplate:

> **Bug report.** Client-IP and request introspection are broken: behind a proxy the reported
> client address is the proxy itself or empty, forwarded-IP headers are ignored or the wrong entry
> of a multi-IP list is chosen, the request content type still carries its parameters, websocket
> upgrade requests are not detected, and the URL scheme ignores forwarded-proto headers.
>
> Expected: the helpers honor trusted proxies and forwarded headers per the documented precedence.
> Got: the helpers panic or return raw values. Reproduce with `go test -count=1 .`

A competent Go programmer can tell what broke. They cannot tell what the documented precedence is,
because the documentation left with the code.

L2 keeps that bug report word for word and puts a contract above it. One clause of five:

> **ClientIP precedence.** Validation walks the joined header list right-to-left, trimming spaces,
> and returns the first entry from the right that either is the leftmost entry or is not itself a
> trusted proxy. An unparsable entry invalidates the whole header.

Then worked examples, so no clause rests on prose alone:

> Remote `1.2.3.4:5678` trusted, `X-Forwarded-For: 9.9.9.9, 8.8.8.8` with `8.8.8.8`
> also trusted, gives `9.9.9.9`. With `8.8.8.8` untrusted it gives `8.8.8.8`.

168 words become 668. Not one of the extra 500 names a file, a line number, or a function to edit.
Every one states behavior a caller can observe. The model fails on 168 words and passes on 668.

<figure class="fig-inline">
<svg viewBox="0 0 720 460" role="img" data-anim="x" aria-label="Prompt length in words at each level. L0 is 101 words. L2 is 450. L4 to L6 fall back to about 324.">
<line x1="150" y1="24" x2="150" y2="400" stroke="var(--line)" stroke-width="1"/>
<text x="150" y="432" text-anchor="middle" fill="var(--text)" font-size="22" font-family="var(--font-mono)">0</text>
<line x1="280" y1="24" x2="280" y2="400" stroke="var(--line)" stroke-width="1"/>
<text x="280" y="432" text-anchor="middle" fill="var(--text)" font-size="22" font-family="var(--font-mono)">200</text>
<line x1="410" y1="24" x2="410" y2="400" stroke="var(--line)" stroke-width="1"/>
<text x="410" y="432" text-anchor="middle" fill="var(--text)" font-size="22" font-family="var(--font-mono)">400</text>
<line x1="540" y1="24" x2="540" y2="400" stroke="var(--line)" stroke-width="1"/>
<text x="540" y="432" text-anchor="middle" fill="var(--text)" font-size="22" font-family="var(--font-mono)">600</text>
<line x1="670" y1="24" x2="670" y2="400" stroke="var(--line)" stroke-width="1"/>
<text x="670" y="432" text-anchor="middle" fill="var(--text)" font-size="22" font-family="var(--font-mono)">800</text>
<text x="128" y="54" text-anchor="end" fill="var(--text)" font-size="24" font-weight="700" font-family="var(--font-mono)">L0</text>
<rect x="203.3" y="33.0" width="24.1" height="26" rx="4" fill="var(--lvl-0)" fill-opacity="0.45"><title>L0</title></rect>
<circle cx="215.7" cy="46" r="7" fill="var(--lvl-0)"/>
<text x="239.4" y="54" fill="var(--text)" font-size="24" font-weight="700" font-family="var(--font-mono)">101</text>
<text x="128" y="104" text-anchor="end" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">L1</text>
<rect x="289.8" y="83.0" width="111.1" height="26" rx="4" fill="var(--lvl-1)" fill-opacity="0.45"><title>L1</title></rect>
<circle cx="310.6" cy="96" r="7" fill="var(--lvl-1)"/>
<text x="412.9" y="104" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">247</text>
<text x="128" y="154" text-anchor="end" fill="var(--text)" font-size="24" font-weight="700" font-family="var(--font-mono)">L2</text>
<rect x="325.5" y="133.0" width="252.9" height="26" rx="4" fill="var(--lvl-2)" fill-opacity="0.45"><title>L2</title></rect>
<circle cx="442.5" cy="146" r="7" fill="var(--lvl-2)"/>
<text x="590.4" y="154" fill="var(--text)" font-size="24" font-weight="700" font-family="var(--font-mono)">450</text>
<text x="128" y="204" text-anchor="end" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">L3</text>
<rect x="337.2" y="183.0" width="308.1" height="26" rx="4" fill="var(--lvl-3)" fill-opacity="0.45"><title>L3</title></rect>
<circle cx="492.6" cy="196" r="7" fill="var(--lvl-3)"/>
<text x="657.3" y="204" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">527</text>
<text x="128" y="254" text-anchor="end" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">L4</text>
<rect x="319.0" y="233.0" width="176.2" height="26" rx="4" fill="var(--lvl-4)" fill-opacity="0.45"><title>L4</title></rect>
<circle cx="360.6" cy="246" r="7" fill="var(--lvl-4)"/>
<text x="507.2" y="254" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">324</text>
<text x="128" y="304" text-anchor="end" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">L5</text>
<rect x="328.1" y="283.0" width="195.6" height="26" rx="4" fill="var(--lvl-5)" fill-opacity="0.45"><title>L5</title></rect>
<circle cx="367.1" cy="296" r="7" fill="var(--lvl-5)"/>
<text x="535.8" y="304" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">334</text>
<text x="128" y="354" text-anchor="end" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">L6</text>
<rect x="327.5" y="333.0" width="64.3" height="26" rx="4" fill="var(--lvl-6)" fill-opacity="0.45"><title>L6</title></rect>
<circle cx="360.6" cy="346" r="7" fill="var(--lvl-6)"/>
<text x="403.8" y="354" fill="var(--text-2)" font-size="24" font-weight="500" font-family="var(--font-mono)">324</text>
<line x1="150" y1="400" x2="670" y2="400" stroke="var(--line)" stroke-width="1.5"/>
<text x="410" y="458" text-anchor="middle" fill="var(--text-2)" font-size="20" font-family="var(--font-sans)">words in the prompt</text>
</svg>
<figcaption>Above L3 the prompt stops growing. Those levels add test files to the repository rather than prose to the prompt. The bug report is 101 words and barely varies. The full description is 450 and varies with how much behavior was cut.</figcaption>
</figure>

### What the checks reject

**The answer key must pass the tests.** Two tasks shipped where it did not. Both were unsolvable,
and invisible until something ran them.

**A fake fix must fail.** One task passed with a hardcoded special case, so its tests were not
checking behavior at all.

**Every behavior must be derivable.** A judge reads each line of the behavior list and asks whether
a solver could work out the answer from what they can see. Some answers are arbitrary, like an
internal constant. Such a line becomes an assertion no solver can satisfy at any level. One pass
over 170 tasks dropped or weakened 245 of 1,560 lines.

**No network.** The container has no egress, and any run where the agent used a web tool is thrown
out. 15 of 30 runs from one model were disqualified this way, against 0 of 32 from another.
Agent-side web tools run on the vendor’s servers and cannot be blocked from inside the container.

## The synthetic dataset

### What a task contains

The synthetic dataset is the set of tasks the ladder kept.

238 certified tasks so far, cut from nine Go repositories: client-go, kops, helm, go-git,
go-github, goa, gin, bbolt, and nats-server. Kubernetes tooling, version control, API design,
storage, HTTP services, and messaging.

Each task ships as a Docker environment plus five artifacts. The repository with the behavior
removed. A bug report, which is the L0 prompt. A written description of every behavior the tests
check, which is the L2 prompt. A hidden test suite that only calls exported functions. And the
answer key, the code that was cut.

These are not toy edits. The median answer key is 127 lines, most fall between 80 and 320, and a
quarter touch two or more files.

Every task carries the model that certified it, and a certificate now requires one model to do
both halves: the same model fails L0 and passes the level that certifies it. An earlier count
labelled 15 tasks where one model failed L0 and a different one passed L2 as a weaker kind of
certificate. That category is gone. Inspecting the six that were left, four were two halves that
never joined, with no single model doing both, and the other two were complete certificates that
pooling had misreported by three levels each, because taking the lowest passing level across models
lets the stronger one erase the weaker one's difficulty. That is the quantity the ladder exists to
measure, so the pooled view was retired rather than kept alongside.

Only two tasks carry a curve climbed independently by two models, which is the population that can
separate a task's difficulty from a model's. That count stays small for a plain reason: a second
curve costs a second full climb. A further 17 tasks pass L0 for one model while another model holds
a certificate on them, so difficulty at the bug report is already model-dependent.

### What the filter removed

<figure class="fig-inline">
<svg viewBox="0 0 720 250" role="img" data-anim="x" aria-label="Funnel: 591 authored, 436 trialled, 411 decided, 238 certified.">
<text x="168" y="54" text-anchor="end" fill="var(--text)" font-size="22" font-family="var(--font-sans)">authored</text>
<rect x="184" y="28" width="460.0" height="36" rx="4" fill="var(--chart-1)" opacity="1"><title>authored: 591</title></rect>
<text x="656.0" y="54" fill="var(--text)" font-size="24" font-weight="700" font-family="var(--font-mono)">591</text>
<text x="168" y="110" text-anchor="end" fill="var(--text)" font-size="22" font-family="var(--font-sans)">trialled</text>
<rect x="184" y="84" width="339.4" height="36" rx="4" fill="var(--chart-1)" opacity="0.34"><title>trialled: 436</title></rect>
<text x="535.4" y="110" fill="var(--text)" font-size="24" font-weight="700" font-family="var(--font-mono)">436</text>
<text x="168" y="166" text-anchor="end" fill="var(--text)" font-size="22" font-family="var(--font-sans)">decided</text>
<rect x="184" y="140" width="319.9" height="36" rx="4" fill="var(--chart-1)" opacity="0.34"><title>decided: 411</title></rect>
<text x="515.9" y="166" fill="var(--text)" font-size="24" font-weight="700" font-family="var(--font-mono)">411</text>
<text x="168" y="222" text-anchor="end" fill="var(--text)" font-size="22" font-family="var(--font-sans)">certified</text>
<rect x="184" y="196" width="185.2" height="36" rx="4" fill="var(--chart-1)" opacity="1"><title>certified: 238</title></rect>
<text x="381.2" y="222" fill="var(--text)" font-size="24" font-weight="700" font-family="var(--font-mono)">238</text>
</svg>

<figcaption>591 authored tasks produce 238 certificates.</figcaption>
</figure>

<figure class="fig-inline">
<svg viewBox="0 0 720 380" role="img" data-anim="x" aria-label="411 decided tasks on two planes. 172 passed the bug report. 238 failed it and passed a higher level. 1 failed every level.">
<rect x="164.0" y="90.9" width="117.9" height="118.0" fill="none" stroke="var(--text-3)" stroke-width="1.2" stroke-dasharray="3 3.5"/>
<polygon points="34.0,214.0 156.9,214.0 163.9,213.7 41.0,213.7" fill="var(--bg-2)" stroke="var(--line)" stroke-width="1"/>
<polygon points="421.9,208.9 552.0,208.9 559.0,208.6 428.9,208.6" fill="var(--chart-1)" fill-opacity="0.14" stroke="var(--text-3)" stroke-width="1"/>
<polygon points="293.9,214.0 424.0,214.0 431.0,213.7 300.9,213.7" fill="var(--bg-2)" stroke="var(--line)" stroke-width="1"/>
<polygon points="689.0,208.9 720.1,208.9 727.1,208.6 696.0,208.6" fill="var(--chart-1)" fill-opacity="0.14" stroke="var(--text-3)" stroke-width="1"/>
<polygon points="561.0,214.0 592.1,214.0 599.1,213.7 568.0,213.7" fill="var(--bg-2)" stroke="var(--line)" stroke-width="1"/>
<polygon points="303.3,213.7 427.6,213.7 548.6,90.9 424.3,90.9" fill="var(--chart-1)" fill-opacity="0.28" stroke="none"/>
<polygon points="570.4,213.7 595.7,213.7 716.7,208.9 691.4,208.9" fill="var(--chart-mute)" fill-opacity="0.5" stroke="none"/>
<polygon points="43.3,213.7 160.6,213.7 160.6,95.7 43.3,95.7" fill="var(--chart-1)"/>
<polygon points="303.2,213.7 427.7,213.7 427.7,208.7 303.2,208.7" fill="var(--chart-mute)"/>
<polygon points="424.2,208.9 548.7,208.9 548.7,90.9 424.2,90.9" fill="var(--chart-1)"/>
<polygon points="570.3,213.7 595.8,213.7 595.8,208.7 570.3,208.7" fill="var(--chart-mute)"/>
<polygon points="691.3,208.9 716.8,208.9 716.8,203.9 691.3,203.9" fill="var(--chart-mute)"/>
<line x1="31.0" y1="213.7" x2="31.0" y2="89.7" stroke="var(--text)" stroke-width="1"/>
<line x1="31.0" y1="89.7" x2="27.5" y2="95.7" stroke="var(--text)" stroke-width="1"/>
<line x1="31.0" y1="89.7" x2="34.5" y2="95.7" stroke="var(--text)" stroke-width="1"/>
<text x="24.0" y="154.7" fill="var(--text)" text-anchor="middle" font-family="var(--font-sans)" font-size="18" font-weight="700" transform="rotate(-90 24.0 154.7)">Outcome</text>
<text x="49.0" y="110.7" fill="var(--bg)" font-family="var(--font-sans)" font-size="20" font-weight="700">pass</text>
<text x="102.0" y="204.0" fill="var(--bg)" text-anchor="middle" font-family="var(--font-sans)" font-size="18" font-weight="600">bug report</text>
<text x="304.9" y="200.7" fill="var(--text-2)" font-family="var(--font-sans)" font-size="20" font-weight="700">fail</text>
<text x="222.9" y="126.9" fill="var(--text)" text-anchor="middle" font-family="var(--font-mono)" font-size="22" font-weight="700">L2</text>
<text x="222.9" y="144.9" fill="var(--text-2)" text-anchor="middle" font-family="var(--font-sans)" font-size="20">empty</text>
<text x="486.4" y="82.9" fill="var(--text)" text-anchor="middle" font-family="var(--font-mono)" font-size="12">L2</text>
<text x="95.0" y="262.0" fill="var(--text)" text-anchor="middle" font-family="var(--font-mono)" font-size="28" font-weight="700">172</text>
<text x="130.0" y="292.0" fill="var(--text-2)" text-anchor="middle" font-family="var(--font-sans)" font-size="20">Passed the bug report.</text>
<text x="358.4" y="262.0" fill="var(--text)" text-anchor="middle" font-family="var(--font-mono)" font-size="28" font-weight="700">238</text>
<text x="358.4" y="292.0" fill="var(--text-2)" text-anchor="middle" font-family="var(--font-sans)" font-size="20">Failed, then passed.</text>
<text x="576.0" y="262.0" fill="var(--text)" text-anchor="middle" font-family="var(--font-mono)" font-size="28" font-weight="700">1</text>
<text x="576.0" y="292.0" fill="var(--text-2)" text-anchor="middle" font-family="var(--font-sans)" font-size="20">Failed both.</text>
<line x1="295.9" y1="328.0" x2="589.1" y2="328.0" stroke="var(--text)" stroke-width="1"/>
<line x1="295.9" y1="328.0" x2="295.9" y2="320.0" stroke="var(--text)" stroke-width="1"/>
<line x1="589.1" y1="328.0" x2="589.1" y2="320.0" stroke="var(--text)" stroke-width="1"/>
<text x="442.5" y="352.0" fill="var(--text)" text-anchor="middle" font-family="var(--font-sans)" font-size="20" font-weight="600">168 failures on the bug report alone</text>
</svg>
<figcaption>411 decided tasks. Height is the outcome. Depth is the prompt. On the bug report, the 238 and the 1 are one pile of 239 failures. The higher levels lift the 238. Block proportions are from the earlier snapshot and are due a redraw.</figcaption>
</figure>

Of the 411 decided tasks, 172 were solved from the bug report by every model that tried, and never
reached the certificate. Nearly half of what a careful pipeline authors is already solvable from a
symptom report. Any generator shipping unscreened tasks is shipping a lot of freebies and cannot
tell you which ones.

The tasks that failed both prompts have almost all resolved, and the ladder is what resolved them.
That bucket stood at 29 while the levels over the full description still had few measurements.
Climbing them left exactly one task, `exprhash`, that no model has passed at any level. Of the
earlier 29, every one audited turned out to carry a defective description rather than an impossible
task, and the rest certified once a higher level supplied what the prose had left out.

Roughly one authored task in four survives to the dataset. The screen and the certificate each
remove about as much as the other.

### Why it cannot be contaminated

Across 1,545 task files there are zero references to issues, pull requests, or CVEs. The answer
keys are 102,586 added lines against 638 non-stub deletions, because restoring removed code is
almost entirely addition. No task in this dataset can sit in any model's training data, because
none of them existed until the cut was made.

That separates the dataset from anything mined out of GitHub history, where the fix a model is
asked to produce may already be in its weights.

### What it cost to produce

Three models did the work, and they bill and report differently, so the totals need stating per
model rather than as one figure.

Composer 2.5 ran most of the ladder trials. Devin and Grok both authored tasks and ran trials, and
Grok 4.7 ran the complete ladder on the three tasks under "When the ladder runs out."

| Model | Runs or sessions | Input | Cache read | Output | Cost |
|---|---:|---:|---:|---:|---:|
| Composer 2.5 | 1,439 runs | 3,005M | 2,931M | 21.9M | $678.23 |
| Devin swe-2-max | 151 sessions | 162M | 3,270M | 22.7M | $452 |
| Grok 4.7 | 22 runs | 79.4M | 66.4M | 1.47M | $23.69 |
| Grok 4.6 | 26 runs | 10.6M | 9.8M | 0.19M | $2.57 |

The Composer and Grok rows come from the trial ledger at the date above. The Devin row is the
earlier export and is due a refresh: it bills in Agent Compute Units rather than tokens, so its
cost is not derivable from the repository, and the repository's own per-model counts disagree with
the token split below. Treat the Devin row as the ACU-based figure it is.

Those rows do not sum, and the reason is the next paragraph. Composer and Grok processed 3.12
billion tokens between them, cache reads included, because their cached count sits inside their
input count. Devin processed a further 3.45 billion, because its cache reads are counted on top of
its input. **The run so far is 6.57 billion tokens for $1,156**, and 6.28 billion of those tokens are
cache reads, so most of the bill is a model re-reading a repository it has already seen.

Devin's share needs a pricing basis, because it bills in Agent Compute Units rather than tokens.
Priced at the SWE-2 promotional rate of $0.75 per million input, $0.075 per million cache read and
$3.75 per million output, its 151 sessions come to $452. Its 185.5 ACUs at the $2.25 list rate
come to $417, so the two ways of pricing the same work agree within 8%. That agreement is the
strongest available check that the token counts are right. At the full SWE-2 rate the same work
would have been $1,808.

The two vendors count caching differently, and the difference is large enough to change the
headline. Composer and Grok report cached tokens as a subset of input, which a least-squares fit
of cost against the three counts confirms: treating cache as additive prices a cached token at
negative money. Devin reports 3,270M cache against 162M input, twenty times larger, so there it
has to be a separate count. Anyone re-deriving these numbers from the repository will hit that
discrepancy, so it is worth naming rather than smoothing over.

The two profiles differ in another way. Output is 0.74% of input for Composer and Grok, and 14%
for Devin. One is almost entirely a reading bill; the other writes far more per token read.

Spending concentrates on the two levels the certificate needs.

| Level | Runs | Input | Cost | Cache hit | $/run |
|---|---:|---:|---:|---:|---:|
| L0, the screen | 541 | 907.6M | $198.10 | 97.4% | $0.37 |
| L2, the certificate | 834 | 1,046.5M | $225.08 | 97.1% | $0.27 |
| Other levels | 113 | 441.0M | $96.80 | 98.2% | $0.86 |

<figure class="fig-inline">
<svg viewBox="0 0 720 360" role="img" data-anim="y" aria-label="Runs per information level. L0 has 541 runs and L2 has 834. The other five levels together have 113.">
<rect x="70" y="152.7" width="70" height="97.3" rx="4" fill="var(--chart-2)" opacity="1"><title>L0: 541 runs</title></rect>
<text x="105.0" y="140.7" text-anchor="middle" fill="var(--text)" font-size="22" font-weight="700" font-family="var(--font-mono)">541</text>
<text x="105.0" y="282" text-anchor="middle" fill="var(--chart-2)" font-size="24" font-weight="700" font-family="var(--font-mono)">L0</text>
<rect x="158" y="246.0" width="70" height="4.0" rx="4" fill="var(--chart-mute)" opacity="0.55"><title>L1: 16 runs</title></rect>
<text x="193.0" y="234.0" text-anchor="middle" fill="var(--text)" font-size="22" font-weight="700" font-family="var(--font-mono)">16</text>
<text x="193.0" y="282" text-anchor="middle" fill="var(--text-2)" font-size="24" font-weight="700" font-family="var(--font-mono)">L1</text>
<rect x="246" y="100.0" width="70" height="150.0" rx="4" fill="var(--chart-1)" opacity="1"><title>L2: 834 runs</title></rect>
<text x="281.0" y="88.0" text-anchor="middle" fill="var(--text)" font-size="22" font-weight="700" font-family="var(--font-mono)">834</text>
<text x="281.0" y="282" text-anchor="middle" fill="var(--chart-1)" font-size="24" font-weight="700" font-family="var(--font-mono)">L2</text>
<rect x="334" y="245.7" width="70" height="4.3" rx="4" fill="var(--chart-mute)" opacity="0.55"><title>L3: 24 runs</title></rect>
<text x="369.0" y="233.7" text-anchor="middle" fill="var(--text)" font-size="22" font-weight="700" font-family="var(--font-mono)">24</text>
<text x="369.0" y="282" text-anchor="middle" fill="var(--text-2)" font-size="24" font-weight="700" font-family="var(--font-mono)">L3</text>
<rect x="422" y="246.0" width="70" height="4.0" rx="4" fill="var(--chart-mute)" opacity="0.55"><title>L4: 12 runs</title></rect>
<text x="457.0" y="234.0" text-anchor="middle" fill="var(--text)" font-size="22" font-weight="700" font-family="var(--font-mono)">12</text>
<text x="457.0" y="282" text-anchor="middle" fill="var(--text-2)" font-size="24" font-weight="700" font-family="var(--font-mono)">L4</text>
<rect x="510" y="243.5" width="70" height="6.5" rx="4" fill="var(--chart-mute)" opacity="0.55"><title>L5: 36 runs</title></rect>
<text x="545.0" y="231.5" text-anchor="middle" fill="var(--text)" font-size="22" font-weight="700" font-family="var(--font-mono)">36</text>
<text x="545.0" y="282" text-anchor="middle" fill="var(--text-2)" font-size="24" font-weight="700" font-family="var(--font-mono)">L5</text>
<rect x="598" y="245.5" width="70" height="4.5" rx="4" fill="var(--chart-mute)" opacity="0.55"><title>L6: 25 runs</title></rect>
<text x="633.0" y="233.5" text-anchor="middle" fill="var(--text)" font-size="22" font-weight="700" font-family="var(--font-mono)">25</text>
<text x="633.0" y="282" text-anchor="middle" fill="var(--text-2)" font-size="24" font-weight="700" font-family="var(--font-mono)">L6</text>
<line x1="56" y1="250" x2="690" y2="250" stroke="var(--line)" stroke-width="1.5"/>
<text x="360" y="330" text-anchor="middle" fill="var(--text)" font-size="20" font-family="var(--font-sans)">L0 and L2 carry 92% of the runs</text>
</svg>
<figcaption>Runs per level across all three models, 1,488 runs whose level is recorded. L0 and L2 take 1,375 of them. L1 and L3 through L6 share 113, which is why the shape of the curve between them stays unmeasured.</figcaption>
</figure>

The levels above L2 cost more than twice as much per run, $0.86 against $0.27 to $0.37, because
their prompts carry test names and test bodies. Climbing the ladder costs money on both ends, in
prompt size and in runs.

238 certificates from 1,685 trials is 7.1 trials each, against a floor of two, and $4.86 apiece.
Both numbers roughly halved as the guards landed, which is the one place in this work where a gate
beat a generator outright. The remainder still goes to trials past the deciding pair: re-running L2
after repairing a description, re-running L0, and climbing the levels above.

<figure class="fig-inline">
<svg viewBox="0 0 720 280" role="img" data-anim="x" aria-label="Runs needed per certificate: parallel with no gate 9.0, sequential with no gate 7.7, sequential with a gate 3.2, against a floor of 2.">
<text x="264" y="52" text-anchor="end" fill="var(--text)" font-size="22" font-family="var(--font-sans)">parallel, no gate</text>
<rect x="280" y="24" width="340.0" height="40" rx="4" fill="var(--chart-mute)" opacity="0.6"><title>parallel, no gate: 9.0</title></rect>
<text x="632.0" y="52" fill="var(--text)" font-size="26" font-weight="700" font-family="var(--font-mono)">9.0</text>
<text x="264" y="124" text-anchor="end" fill="var(--text)" font-size="22" font-family="var(--font-sans)">sequential, no gate</text>
<rect x="280" y="96" width="290.9" height="40" rx="4" fill="var(--chart-mute)" opacity="0.6"><title>sequential, no gate: 7.7</title></rect>
<text x="582.9" y="124" fill="var(--text)" font-size="26" font-weight="700" font-family="var(--font-mono)">7.7</text>
<text x="264" y="196" text-anchor="end" fill="var(--text)" font-size="22" font-family="var(--font-sans)">sequential, gated</text>
<rect x="280" y="168" width="120.9" height="40" rx="4" fill="var(--chart-1)" opacity="1"><title>sequential, gated: 3.2</title></rect>
<text x="412.9" y="196" fill="var(--text)" font-size="26" font-weight="700" font-family="var(--font-mono)">3.2</text>
<line x1="355.6" y1="12" x2="355.6" y2="232" stroke="var(--chart-2)" stroke-width="2"/>
<text x="363.6" y="228" fill="var(--chart-2)" font-size="20" font-family="var(--font-sans)">floor of 2</text>
<text x="470" y="266" text-anchor="middle" fill="var(--text)" font-size="20" font-family="var(--font-sans)">runs per certificate</text>
</svg>
<figcaption>Runs spent per certificate under three schedules. Refusing a run whose outcome is already determined is worth about 4×. Running trials in sequence, on its own, is worth almost nothing.</figcaption>
</figure>

Authoring is the part these figures cover worst. Devin's ledger folds authoring, verification and
trials into one account total, so the split between building a task and measuring it cannot be
recovered from the data as it stands. An earlier, partial measurement put authoring near $1.25 per
task, which is small against the trial bill but should be read as an estimate.

Re-measuring what you already know is what makes a task factory expensive. Generating tasks is the
cheap half. That $1,156 is one researcher's bill. The chart is the cut still available on a bill
like it.

## Conclusion and future work

Stage 1 is Go, nine repositories, in-repo cuts, and one model for roughly three runs in four. Those are budget
choices, not findings. This is self-funded, so the dataset is small and deep instead of broad. It is
enough to show the method works, not enough to claim it generalizes.

A solve rate belongs to the model that produced it, and so does a certificate. Difficulty is a relation
between a task, a model, and an amount of information, and what this work adds is a way to set the third term.

Four results here should hold for anyone building a task factory. Put the difficulty in the prompt,
because whatever you leave in the repository specifies what you took out. Use two prompts, because
a failing run alone cannot distinguish a hard task from a broken one. Keep the test writer away
from the answer key. Budget for the guards before the generator, because a gate that refuses a
redundant run beat every generation improvement in this work.

Stage 2 runs the same factory in a second language, which is the test of whether the cut mechanic
survives outside Go. The cut, the blind tests, and the certificate stay.

Two items that were future work here have started returning numbers. A held-out model screening
the dataset answers whether a certificate means anything to a model that took no part in producing
it; 42 certified tasks have now been re-screened at L0 by the solver that did not certify them,
and the answer so far is that it depends on the repository rather than the dataset. Eight of ten
`go-github` tasks were solved from the bug report alone by the second model against three of
thirty-two everywhere else, which is a property of that repository's issues naming the fields its
code turns on, not a property of the method. That rate is also one-directional: one model was the
first screener in 41 of the 42 pairs, so it measures what the second model rescues from the first
and not the reverse.

Filling in the test names, the signatures and the tests gives the dose-response curve above the
full description. The three tasks in "When the ladder runs out" have that curve complete for two
models, every level measured, and 79% of certified tasks bind at the full description with 16% at
a restored test, so the information does not arrive smoothly. Per-repository yield still needs an
instrumented unit-to-repository map before it can be claimed at all.

---

*Code and trial ledger:
[open_swe_traces_research](https://github.com/Evan-Kim2028/open_swe_traces_research). Counts are a
2026-09-22 snapshot of a run still in progress, derived from `trial_ledger.py` and `roots.py`.
Earlier in this series: [Terminal-Bench Task: Lakehouse Schema Contract
Drift](/writings/terminal-bench-task-lakehouse-schema-contract-drift/) and [Four Verifiable
Properties of a Useful Agent Task](/writings/four-verifiable-properties-of-a-useful-agent-task/).*
