---
title: "Building a Synthetic SWE Factory: Difficulty Is an Information Gap"
date: "2026-09-21"
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
description: "Stage 1: Go, nine repositories, 527 tasks. A coding task is hard because of what its prompt leaves out, and that gap can be set on purpose and measured."
series: Evals
series_index: 3
hero: /assets/images/information-gap-hero.png
hero_dark: /assets/images/information-gap-hero.dark.png
---

## Summary

Difficulty is an information gap.

A coding task is hard when the prompt leaves out something the solver needs and cannot work out
from what remains. Widen the gap and the task gets harder. Close it and the task gets solved. The
width is a dial, and turning it is the only reliable way to build a task at a chosen
difficulty.

The factory below is built around that dial. Cut a working behavior out of a real Go repository. Have a
second agent write hidden tests from a written specification, never from the code. Then run the
same model twice. The first run gets only a bug report. The second gets a full description of every
behavior those tests check. Keep the task when the first fails and the second passes.

Those two runs are the product. The failure shows the task is hard. The pass shows it is solvable
as written. One prompt cannot show both, and every comparable generation pipeline uses one prompt.

Stage 1 is Go, nine repositories, self-funded: 527 tasks authored and 139 certified so far.

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

Each level adds exactly one kind of information about the removed behavior. Nothing above the
level is visible. Seven levels, because that is how many distinct kinds of help a solver can
actually use, ordered from the least specific to the most.

<figure class="fig-inline">
<svg viewBox="0 0 720 452" role="img" aria-label="Seven nested circles tangent at the bottom. L0 at the core is the bug report and is marked fails. Each larger circle contains the one inside it and adds one kind of information, out to L6, every test. L2, the full description, is marked passes, and the band between L0 and L2 is labelled the gap.">
<circle cx="330" cy="208" r="196" fill="var(--chart-mute)" fill-opacity="0.16" stroke="var(--line)" stroke-width="1.5" stroke-opacity="0.55"><title>L6: all tests</title></circle>
<circle cx="330" cy="236" r="168" fill="var(--chart-mute)" fill-opacity="0.16" stroke="var(--line)" stroke-width="1.5" stroke-opacity="0.55"><title>L5: one hidden test</title></circle>
<circle cx="330" cy="264" r="140" fill="var(--chart-mute)" fill-opacity="0.16" stroke="var(--line)" stroke-width="1.5" stroke-opacity="0.55"><title>L4: signatures</title></circle>
<circle cx="330" cy="292" r="112" fill="var(--chart-mute)" fill-opacity="0.16" stroke="var(--line)" stroke-width="1.5" stroke-opacity="0.55"><title>L3: test names</title></circle>
<circle cx="330" cy="320" r="84" fill="var(--chart-1)" fill-opacity="0.9" stroke="var(--chart-1)" stroke-width="1.5" stroke-opacity="0.55"><title>L2: full description</title></circle>
<circle cx="330" cy="348" r="56" fill="var(--chart-mute)" fill-opacity="0.16" stroke="var(--line)" stroke-width="1.5" stroke-opacity="0.55"><title>L1: partial description</title></circle>
<circle cx="330" cy="376" r="28" fill="var(--chart-2)" fill-opacity="1" stroke="var(--chart-2)" stroke-width="1.5" stroke-opacity="0.55"><title>L0: bug report</title></circle>
<text x="330" y="365" text-anchor="middle" fill="var(--bg)" font-size="12.5" font-weight="700" font-family="var(--font-mono)">L0</text>
<text x="330" y="381" text-anchor="middle" fill="var(--bg)" font-size="11.5" fill-opacity="0.85" font-family="var(--font-sans)">bug report</text>
<text x="330" y="309" text-anchor="middle" fill="var(--bg)" font-size="12.5" font-weight="500" font-family="var(--font-mono)">L1</text>
<text x="330" y="325" text-anchor="middle" fill="var(--bg)" font-size="11.5" fill-opacity="0.85" font-family="var(--font-sans)">partial description</text>
<text x="330" y="253" text-anchor="middle" fill="var(--bg)" font-size="12.5" font-weight="700" font-family="var(--font-mono)">L2</text>
<text x="330" y="269" text-anchor="middle" fill="var(--bg)" font-size="11.5" fill-opacity="0.85" font-family="var(--font-sans)">full description</text>
<text x="330" y="197" text-anchor="middle" fill="var(--text-2)" font-size="12.5" font-weight="500" font-family="var(--font-mono)">L3</text>
<text x="330" y="213" text-anchor="middle" fill="var(--text-3)" font-size="11.5" fill-opacity="1" font-family="var(--font-sans)">test names</text>
<text x="330" y="141" text-anchor="middle" fill="var(--text-2)" font-size="12.5" font-weight="500" font-family="var(--font-mono)">L4</text>
<text x="330" y="157" text-anchor="middle" fill="var(--text-3)" font-size="11.5" fill-opacity="1" font-family="var(--font-sans)">signatures</text>
<text x="330" y="85" text-anchor="middle" fill="var(--text-2)" font-size="12.5" font-weight="500" font-family="var(--font-mono)">L5</text>
<text x="330" y="101" text-anchor="middle" fill="var(--text-3)" font-size="11.5" fill-opacity="1" font-family="var(--font-sans)">one hidden test</text>
<text x="330" y="29" text-anchor="middle" fill="var(--text-2)" font-size="12.5" font-weight="500" font-family="var(--font-mono)">L6</text>
<text x="330" y="45" text-anchor="middle" fill="var(--text-3)" font-size="11.5" fill-opacity="1" font-family="var(--font-sans)">all tests</text>
<text x="330" y="288" text-anchor="middle" fill="var(--bg)" font-size="11.5" font-weight="700" letter-spacing="0.08em" font-family="var(--font-sans)">PASSES</text>
<text x="330" y="430" text-anchor="middle" fill="var(--chart-2)" font-size="11.5" font-weight="700" letter-spacing="0.08em" font-family="var(--font-sans)">L0 FAILS</text>
<line x1="246" y1="318" x2="150" y2="318" stroke="var(--text-2)" stroke-width="1.5"/>
<circle cx="246" cy="318" r="3" fill="var(--text-2)"/>
<text x="142" y="315" text-anchor="end" fill="var(--text)" font-size="13" font-weight="700" font-family="var(--font-sans)">the gap</text>
<text x="142" y="332" text-anchor="end" fill="var(--text-3)" font-size="12" font-family="var(--font-sans)">what L2 adds</text>
</svg>
<figcaption>Each level contains the one inside it and adds one kind of information about the removed behavior. A certificate is a failure at L0, the core, and a pass at L2. The band between them is the difficulty. Ring sizes are even steps; they show containment, not an amount.</figcaption>
</figure>

| Level | Name | What it adds over the level below |
|---|---|---|
| L0 | Bug report | The symptom, and how to reproduce it. The implementation is gone. |
| L1 | Partial description | Every requirement but one, in prose. |
| L2 | Full description | Every behavior the hidden tests check, one line per assertion. |
| L3 | Test names | The names of the hidden tests, and a one-line summary of each. |
| L4 | Signatures | The exported function signatures, as empty stubs. |
| L5 | One test | The full body of one hidden test file. |
| L6 | All tests | Every test in the tree. |

The order matters more than the count. L0 through L2 vary how the behavior is described, and L3
through L6 start handing over the tests themselves. The certificate lives entirely in the first
group, so a certified task never sees a test name.

These levels build tasks. They do not read existing ones. Mapping them onto Terminal-Bench by
instruction content puts almost every task at L1, a goal plus unstated requirements plus hidden
tests. A benchmark that does not vary information cannot be used to study information.

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

A task earns a place in the bank, the set kept and shipped, on two runs by one model. The first
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
across 23 languages, forty times this bank, so the two differ somewhere other than scale. Every row above the last
can show that a model failed a task. Only a second prompt that passes separates a hard task from an
underspecified one. CodeMidas also builds its tests by running the original code, so its tests come
from the answer. These come from a written specification of it.

## The factory

### Four steps, three agents

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

139 certified tasks so far, cut from nine Go repositories: client-go, kops, helm, go-git,
go-github, goa, gin, bbolt, and nats-server. Kubernetes tooling, version control, API design,
storage, HTTP services, and messaging.

Each task ships as a Docker environment plus five artifacts. The repository with the behavior
removed. A bug report, which is the L0 prompt. A written description of every behavior the tests
check, which is the L2 prompt. A hidden test suite that only calls exported functions. And the
answer key, the code that was cut.

These are not toy edits. The median answer key is 127 lines, most fall between 80 and 320, and a
quarter touch two or more files.

Every task also carries the model that certified it. 124 of the 139 had the same model fail L0 and
pass L2, which is the clean claim. The other 15 failed L0 on one model and passed L2 on another,
which might be an information gap or a capability gap, so they are labelled separately rather than
pooled.

### What the filter removed

<figure class="fig-inline">
<svg viewBox="0 0 720 300" role="img" data-anim="x" aria-label="Funnel: 527 authored, 339 trialled, 299 decided, 139 certified. The 299 decided split into 131 solved from the bug report, 139 certified, and 29 that failed both prompts.">
<text style="--d:1" x="112" y="36" text-anchor="end" fill="var(--text-2)" font-size="13" font-family="var(--font-sans)">authored</text>
<rect style="--d:1" x="124" y="20" width="528" height="22" rx="3" fill="var(--chart-1)" opacity="0.34"><title>authored: 527</title></rect>
<text style="--d:2" x="662" y="36" fill="var(--text)" font-size="13" font-weight="600" font-family="var(--font-mono)">527</text>
<text style="--d:3" x="112" y="70" text-anchor="end" fill="var(--text-2)" font-size="13" font-family="var(--font-sans)">trialled</text>
<rect style="--d:2" x="124" y="54" width="340" height="22" rx="3" fill="var(--chart-1)" opacity="0.34"><title>trialled: 339</title></rect>
<text style="--d:4" x="474" y="70" fill="var(--text)" font-size="13" font-weight="600" font-family="var(--font-mono)">339</text>
<text style="--d:5" x="112" y="104" text-anchor="end" fill="var(--text-2)" font-size="13" font-family="var(--font-sans)">decided</text>
<rect style="--d:3" x="124" y="88" width="300" height="22" rx="3" fill="var(--chart-1)" opacity="0.34"><title>decided: 299</title></rect>
<text style="--d:6" x="434" y="104" fill="var(--text)" font-size="13" font-weight="600" font-family="var(--font-mono)">299</text>
<text style="--d:7" x="112" y="138" text-anchor="end" fill="var(--text-2)" font-size="13" font-family="var(--font-sans)">certified</text>
<rect style="--d:4" x="124" y="122" width="139" height="22" rx="3" fill="var(--chart-1)" opacity="1"><title>certified: 139</title></rect>
<text style="--d:8" x="273" y="138" fill="var(--text)" font-size="13" font-weight="600" font-family="var(--font-mono)">139</text>
<line x1="124" y1="176" x2="652" y2="176" stroke="var(--line)" stroke-width="1"/>
<text style="--d:9" x="124" y="202" fill="var(--text-3)" font-size="12" font-family="var(--font-sans)">the 299 decided tasks</text>
<rect style="--d:5" x="124" y="214" width="229" height="34" rx="3" fill="var(--chart-2)"><title>solved from the bug report alone: 131</title></rect>
<text style="--d:10" x="238" y="236" text-anchor="middle" fill="var(--bg)" font-size="13" font-weight="600" font-family="var(--font-mono)">131</text>
<text style="--d:11" x="238" y="268" text-anchor="middle" fill="var(--text-2)" font-size="12" font-family="var(--font-sans)">solved from the</text>
<text style="--d:12" x="238" y="282" text-anchor="middle" fill="var(--text-2)" font-size="12" font-family="var(--font-sans)">bug report alone</text>
<rect style="--d:6" x="355" y="214" width="243" height="34" rx="3" fill="var(--chart-1)"><title>failed L0, passed L2 certified: 139</title></rect>
<text style="--d:13" x="476" y="236" text-anchor="middle" fill="var(--bg)" font-size="13" font-weight="600" font-family="var(--font-mono)">139</text>
<text style="--d:14" x="476" y="268" text-anchor="middle" fill="var(--text-2)" font-size="12" font-family="var(--font-sans)">failed L0, passed L2</text>
<text style="--d:15" x="476" y="282" text-anchor="middle" fill="var(--text-2)" font-size="12" font-family="var(--font-sans)">certified</text>
<rect style="--d:7" x="600" y="214" width="50" height="34" rx="3" fill="var(--chart-mute)"><title>failed both: 29</title></rect>
<text style="--d:16" x="625" y="236" text-anchor="middle" fill="var(--text)" font-size="13" font-weight="600" font-family="var(--font-mono)">29</text>
<text style="--d:17" x="625" y="268" text-anchor="middle" fill="var(--text-2)" font-size="12" font-family="var(--font-sans)">failed</text>
<text style="--d:18" x="625" y="282" text-anchor="middle" fill="var(--text-2)" font-size="12" font-family="var(--font-sans)">both</text>
</svg>
<figcaption>527 authored tasks produce 139 certificates. The screen and the certificate remove about as much as each other: 131 tasks were never hard, and 29 failed both prompts.</figcaption>
</figure>

Of the 299 decided tasks, 131 were solved from the bug report alone and never reached the
certificate. Nearly half of what a careful pipeline authors is already solvable from a symptom
report. Any generator shipping unscreened tasks is shipping a lot of freebies and cannot tell you
which ones. The 29 that failed both prompts came out too, and every one audited turned out to be a
defective description rather than an impossible task.

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

Composer 2.5 ran most of the ladder trials. Devin and Grok both authored tasks and ran trials.

| Model | Runs or sessions | Input | Cache read | Output | Cost |
|---|---:|---:|---:|---:|---:|
| Composer 2.5 | 1,233 runs | 2,302M | 2,244M | 16.8M | $520.13 |
| Devin swe-2-max | 151 sessions | 162M | 3,270M | 22.7M | $452 |
| Grok 4.6 | 27 runs | 10.6M | 9.8M | 0.19M | $2.57 |

Those rows do not sum, and the reason is the next paragraph. Composer and Grok processed 2.33
billion tokens between them, cache reads included, because their cached count sits inside their
input count. Devin processed a further 3.45 billion, because its cache reads are counted on top of
its input. **The run so far is 5.78 billion tokens for $975**, and 5.5 billion of those tokens are cache
reads, so most of the bill is a model re-reading a repository it has already seen.

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
<svg viewBox="0 0 720 286" role="img" data-anim="y" aria-label="Runs per information level across all three models. L0 has 541 runs and L2 has 834. The other five levels together have 113.">
<rect style="--d:1" x="110" y="118" width="56" height="106" rx="3" fill="var(--chart-2)" opacity="1"><title>L0: 541 runs</title></rect>
<text style="--d:1" x="138" y="110" text-anchor="middle" fill="var(--text)" font-size="12" font-weight="600" font-family="var(--font-mono)">541</text>
<text style="--d:2" x="138" y="244" text-anchor="middle" fill="var(--chart-2)" font-size="13" font-family="var(--font-mono)">L0</text>
<rect style="--d:2" x="194" y="221" width="56" height="3" rx="3" fill="var(--chart-mute)" opacity="0.55"><title>L1: 16 runs</title></rect>
<text style="--d:3" x="222" y="213" text-anchor="middle" fill="var(--text)" font-size="12" font-weight="600" font-family="var(--font-mono)">16</text>
<text style="--d:4" x="222" y="244" text-anchor="middle" fill="var(--text-3)" font-size="13" font-family="var(--font-mono)">L1</text>
<rect style="--d:3" x="278" y="60" width="56" height="164" rx="3" fill="var(--chart-1)" opacity="1"><title>L2: 834 runs</title></rect>
<text style="--d:5" x="306" y="52" text-anchor="middle" fill="var(--text)" font-size="12" font-weight="600" font-family="var(--font-mono)">834</text>
<text style="--d:6" x="306" y="244" text-anchor="middle" fill="var(--chart-1)" font-size="13" font-family="var(--font-mono)">L2</text>
<rect style="--d:4" x="362" y="219" width="56" height="5" rx="3" fill="var(--chart-mute)" opacity="0.55"><title>L3: 24 runs</title></rect>
<text style="--d:7" x="390" y="211" text-anchor="middle" fill="var(--text)" font-size="12" font-weight="600" font-family="var(--font-mono)">24</text>
<text style="--d:8" x="390" y="244" text-anchor="middle" fill="var(--text-3)" font-size="13" font-family="var(--font-mono)">L3</text>
<rect style="--d:5" x="446" y="221" width="56" height="3" rx="3" fill="var(--chart-mute)" opacity="0.55"><title>L4: 12 runs</title></rect>
<text style="--d:9" x="474" y="213" text-anchor="middle" fill="var(--text)" font-size="12" font-weight="600" font-family="var(--font-mono)">12</text>
<text style="--d:10" x="474" y="244" text-anchor="middle" fill="var(--text-3)" font-size="13" font-family="var(--font-mono)">L4</text>
<rect style="--d:6" x="530" y="217" width="56" height="7" rx="3" fill="var(--chart-mute)" opacity="0.55"><title>L5: 36 runs</title></rect>
<text style="--d:11" x="558" y="209" text-anchor="middle" fill="var(--text)" font-size="12" font-weight="600" font-family="var(--font-mono)">36</text>
<text style="--d:12" x="558" y="244" text-anchor="middle" fill="var(--text-3)" font-size="13" font-family="var(--font-mono)">L5</text>
<rect style="--d:7" x="614" y="219" width="56" height="5" rx="3" fill="var(--chart-mute)" opacity="0.55"><title>L6: 25 runs</title></rect>
<text style="--d:13" x="642" y="211" text-anchor="middle" fill="var(--text)" font-size="12" font-weight="600" font-family="var(--font-mono)">25</text>
<text style="--d:14" x="642" y="244" text-anchor="middle" fill="var(--text-3)" font-size="13" font-family="var(--font-mono)">L6</text>
<line x1="96" y1="224" x2="700" y2="224" stroke="var(--line)" stroke-width="1.5"/>
<text style="--d:15" x="398" y="262" text-anchor="middle" fill="var(--text-3)" font-size="12" font-family="var(--font-sans)">the deciding pair carries 92% of the runs; the rest of the ladder is thinly sampled</text>
</svg>
<figcaption>Runs per level across all three models, 1,488 runs whose level is recorded. L0 and L2 take 1,375 of them. L1 and L3 through L6 share 113, which is why the shape of the curve between them stays unmeasured.</figcaption>
</figure>

The levels above L2 cost more than twice as much per run, $0.86 against $0.27 to $0.37, because
their prompts carry test names and test bodies. Climbing the ladder costs money on both ends, in
prompt size and in runs.

139 certificates from 1,872 runs is 13.5 runs each, against a floor of two, and $7.01 apiece. Most of the spend therefore went to runs past the deciding pair: re-running L2 after
repairing a description, re-running L0, and exploring other levels. Almost none of it produced new
information.

<figure class="fig-inline">
<svg viewBox="0 0 720 236" role="img" data-anim="x" aria-label="Runs needed per certificate: parallel with no gate 9.0, sequential with no gate 7.7, sequential with a gate 3.2, against a floor of 2.">
<text style="--d:1" x="248" y="49" text-anchor="end" fill="var(--text-2)" font-size="13" font-family="var(--font-sans)">parallel, no gate</text>
<rect style="--d:1" x="262" y="28" width="378" height="30" rx="3" fill="var(--chart-mute)" opacity="0.6"><title>parallel, no gate: 9.0 runs per certificate</title></rect>
<text style="--d:2" x="650" y="49" fill="var(--text)" font-size="14" font-weight="600" font-family="var(--font-mono)">9.0</text>
<text style="--d:3" x="248" y="101" text-anchor="end" fill="var(--text-2)" font-size="13" font-family="var(--font-sans)">sequential, no gate</text>
<rect style="--d:2" x="262" y="80" width="323" height="30" rx="3" fill="var(--chart-mute)" opacity="0.6"><title>sequential, no gate: 7.7 runs per certificate</title></rect>
<text style="--d:4" x="595" y="101" fill="var(--text)" font-size="14" font-weight="600" font-family="var(--font-mono)">7.7</text>
<text style="--d:5" x="248" y="153" text-anchor="end" fill="var(--text-2)" font-size="13" font-family="var(--font-sans)">sequential, gated</text>
<rect style="--d:3" x="262" y="132" width="134" height="30" rx="3" fill="var(--chart-1)" opacity="1"><title>sequential, gated: 3.2 runs per certificate</title></rect>
<text style="--d:6" x="406" y="153" fill="var(--text)" font-size="14" font-weight="600" font-family="var(--font-mono)">3.2</text>
<line x1="346" y1="16" x2="346" y2="192" stroke="var(--chart-2)" stroke-width="2"/>
<text style="--d:7" x="354" y="188" fill="var(--chart-2)" font-size="12" font-family="var(--font-sans)">floor of 2</text>
<text style="--d:8" x="480" y="222" text-anchor="middle" fill="var(--text-3)" font-size="12" font-family="var(--font-sans)">runs per certificate</text>
</svg>
<figcaption>Runs spent per certificate under three schedules. Refusing a run whose outcome is already determined is worth about 4×. Running trials in sequence, on its own, is worth almost nothing.</figcaption>
</figure>

Authoring is the part these figures cover worst. Devin's ledger folds authoring, verification and
trials into one account total, so the split between building a task and measuring it cannot be
recovered from the data as it stands. An earlier, partial measurement put authoring near $1.25 per
task, which is small against the trial bill but should be read as an estimate.

Re-measuring what you already know is what makes a task factory expensive. Generating tasks is the
cheap half.

## Conclusion and future work

Stage 1 is Go, nine repositories, in-repo cuts, and one model for roughly three runs in four. Those are budget
choices, not findings. This is self-funded, so the bank is small and deep instead of broad. It is
enough to show the method works, not enough to claim it generalizes.

Removing behavior cleanly leans on Go’s package layout and test conventions, so a second language
is the real test. A certificate may not hold for a model that never took part in screening; right
now, too easy means Composer 2.5 solved it. L1 and L3 through L6 are sparsely sampled, so whether
information helps smoothly or all at once is unmeasured. Per-repository yield varies widely, but
those numbers need re-deriving before they can be claimed.

A solve rate belongs to the model that produced it, and so does a certificate. The method treats that as a
premise rather than as a shortcoming. Difficulty is a relation between a task, a model, and an
amount of information, and what this work adds is a way to set the third term.

Four results here should hold for anyone building a task factory. Put the difficulty in the prompt,
because whatever you leave in the repository specifies what you took out. Use two prompts, because
a failing run alone cannot distinguish a hard task from a broken one. Keep the test writer away
from the answer key, because tests written from an implementation check that implementation, while
tests written from a specification check the behavior. And budget for the guards before the
generator, because a gate that refuses a redundant run beat every generation improvement in this work.

Stage 2 runs the same factory in a second language, which is the test of whether the cut mechanic
survives outside Go. The cut, the blind tests, and the certificate stay. A held-out model screens
the bank, which answers whether a certificate means anything to a model that took no part in
producing it. Filling in L1 and L3 through L6 gives the dose-response curve, and shows whether
information helps smoothly or arrives all at once. Per-repository yield needs an instrumented
unit-to-repository map before it can be claimed at all.

---

*Code and trial ledger:
[open_swe_traces_research](https://github.com/Evan-Kim2028/open_swe_traces_research). Counts are a
2026-09-21 snapshot of a run still in progress, derived from `trial_ledger.py` and `roots.py`.
Earlier in this series: [Terminal-Bench Task: Lakehouse Schema Contract
Drift](/writings/terminal-bench-task-lakehouse-schema-contract-drift/) and [Four Verifiable
Properties of a Useful Agent Task](/writings/four-verifiable-properties-of-a-useful-agent-task/).*
