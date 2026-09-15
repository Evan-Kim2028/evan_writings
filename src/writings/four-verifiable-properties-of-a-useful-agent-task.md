---
title: "Four Verifiable Properties of a Useful Agent Task"
date: "2026-09-14"
collection: data
lede: true
tags:
  - writing
  - data
  - evals
  - benchmarks
  - agents
source_url: https://github.com/Evan-Kim2028/evaltrials
source_platform: github
slug: four-verifiable-properties-of-a-useful-agent-task
description: "Soundness and difficulty settle by running an agent task. Durability and taste need data almost no benchmark publishes."
series: Evals
series_index: 2
no_related: true
hero: /assets/images/agent-task-properties-hero.png
hero_dark: /assets/images/agent-task-properties-hero.dark.png
---

Soundness, difficulty, durability and taste decide whether an agent task is worth keeping. Soundness and difficulty settle by running the task. Durability and taste need data that almost no benchmark publishes.

## Introduction

A benchmark for a coding agent is a pool of tasks, each packaging an instruction, an environment, a reference solution, and a grader. Every benchmark reports how many broken tasks its curation caught. None reports how many survived. Those answer different questions, and anyone buying task data needs the second.

These 7 task pools carry the figures below, all measured with one procedure and spanning hand-curated benchmarks and machine-generated lots: [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/), the retired [Terminal-Bench](https://www.tbench.ai) 2.0 and 2.1, [Harbor-Index 1.0](https://harbor-index.org), and the generated sets [RST](https://arxiv.org/abs/2608.05466) and [SETA-Env](https://arxiv.org/abs/2607.10891), alongside a pilot of hand-written tasks. A [public dump](https://huggingface.co/datasets/kendx/Harbor-Adapter) of 793,698 recorded agent trials feeds the durability work, covering 8,468 tasks across 60 benchmarks, 16 models and 6 agent harnesses, of which 6,627 carry enough trials at both ends of the capability range to measure. Taste rests on two label sets: 1,699 SWE-bench tasks rated by humans, and [Harbor-Index's funnel](https://arxiv.org/abs/2609.04298) from 6,627 candidates down to 82.

Terminal-Bench 2.1 shipped in May 2026 after a pass that repaired 28 of its 89 tasks, and a census run against all 89 in September 2026 found 5 reference solutions still failing their own tests. The benchmark moved to a separately authored version 3 in July 2026 and to version 4 in August 2026, so the 2.x figures describe retired pools. Version 4 shares no tasks with 2.1, so figures drawn from each describe different pools rather than one pool measured twice.

## Four properties define a useful task

The 4 properties below decide whether a task in the pool is worth keeping, and they are not equally verifiable.

1. **Soundness.** A task is sound when its own reference solution satisfies its own grader. Checking it needs no model and no judgment call. Run the packaged answer key, score it with the packaged verifier, and the task either passes or it does not.

2. **Difficulty.** A task has difficulty when its target model sometimes passes and sometimes fails. A task that always fails cannot tell two models apart, and neither can a task that always passes.

3. **Durability.** Difficulty measured a second time. Models improve, and a task that separates them today can stop separating them at the next model generation. A task is durable when it still fails sometimes for stronger models.

4. **Taste.** The loosest of the four. A task has taste when it matches what the benchmark's own reviewers choose to keep.

Each property earned its place only where an existing pool could answer for it. Other properties may matter, and this list does not claim to be complete. Every figure below comes from a pool this work measured directly.

## Strong verification

Soundness and difficulty each reduce to a procedure whose answer needs no adjudication. Both also scale past the sample. A hypergeometric bound turns a count of flagged tasks into a 95% upper limit for the whole pool, and the tolerance sets the sample size rather than the size of the pool. Against a census whose true rate is already known, that bound covers it in every one of 4,000 simulated draws.

### Soundness

A sound task's own reference solution passes its own verifier in a fresh container, and an empty submission does not. A failure needs no interpretation because a task whose answer key cannot satisfy its grader has contradicted itself. A pass proves less. A verifier can still under-test the requirement, accept a wrong implementation, or lean on accidental environment state. It can also report one score and emit another, which a pass-fail probe cannot see at all.

Running the check finds what maintenance and review both miss. Terminal-Bench repaired 28 tasks between versions 2.0 and 2.1, and the check flags 9 of the 27 comparable pairs before the repair and clears 7 after. Harbor-Index shipped 82 tasks after a model screen, expert review and a fix pass, and 2 of its 53 executable references still fail every run: one fails half its own tests, the other scores its reference at 0.97 out of 1.0 in its own log and then writes a reward of zero to the file that counts. Any submission as good as that reference would score zero too, so doing the task correctly cannot pass it. The same check, run on samples and bounded, released a SWE-bench pool at 4.65% and a generated pool of 4,569 tasks at 2.32%, and rejected the Terminal-Bench 2.1 census at 5.6%.

### Difficulty

Naming a reference model makes difficulty verifiable. The measurement reduces to a solve rate, the share of scored attempts that succeed. A task pinned at either end cannot rank two models against each other.

A low solve rate alone cannot tell a hard task from a broken one, so difficulty follows soundness rather than replacing it. Across the 1,699 SWE-bench tasks that 3 raters each annotated for OpenAI in 2024, two years before these measurements, the ones they called invalid sit at a median solve rate of 2% while sound tasks sit at 33%. Brokenness ages more slowly than taste does, which is why labels that old still carry here. Harbor-Index built a benchmark on this measurement. Between March and May 2026 it ran 3 trials of each candidate across 6 frontier pairings, Opus 4.6, GPT-5.4 and Gemini 3.1 Pro against two harnesses each, then kept the tasks those models solved at most a third of the time. That cut 6,627 candidates to a published 1,311, reported in [the Harbor-Index paper](https://arxiv.org/abs/2609.04298) in September 2026. Rebuilding the same rule from the trial data the authors released reproduces it at 1,331, within 1.5%. Every solve rate belongs to the models that produced it, and travels with them.

## Weak verification

Durability and taste are measurable, but neither reduces to a procedure, and both need data most benchmarks do not publish.

### Durability

Durability is difficulty measured a second time against models of different strength on the same tasks. The Harbor-Index authors released every trial behind their benchmark as [Harbor-Adapter](https://huggingface.co/datasets/kendx/Harbor-Adapter), 768,956 scored trials from 16 models and 6 agent harnesses recorded between March and May 2026. Ordering those models by aggregate solve rate and splitting them into thirds gives each task a slope: its solve rate in the strongest third minus its rate in the weakest, measured in percentage points. Newer models have since passed that generation, so the slopes understate how far a current model climbs. Across the 6,613 tasks with enough trials in both outer tiers the median slope is 13 percentage points, so steep tasks are the exception. [Terminal-Bench 4](https://www.tbench.ai/news/terminal-bench-4-0) shows what the exception costs from its leaderboard of current models. Of its 66 tasks, 27 gain more than 40 percentage points across the benchmark's own 13 submissions, which is 41% of a pool built to be hard for one model generation and already ordinary for the next.

Measuring the slope is the only way to get it, because nothing cheaper recovers it. Guessing it from a task's features fails: a model fitted on how tasks look and how agents behaved on them, asked which of two tasks from the same benchmark will hold up better, gets it right 51% of the time, which is chance. Human review fails too. A durable task has a low slope, and the 80 Harbor-Index tasks the reviewers kept carry a median slope of 2.9 percentage points against 0.2 for the 1,262 they rejected. The kept tasks are if anything slightly steeper, and the gap is not statistically significant, so the reviewers were not selecting for durability at all. The capability axis is itself confounded, since a submission in the dump is a model and a harness together and the tier ordering cannot pull them apart. [CurveShift](https://arxiv.org/abs/2608.00355), published in July 2026, measured the same construct first and named the same confound.

### Taste

Taste covers what the other three leave over. Among tasks that pass the soundness check, sit at a useful solve rate, and hold that rate as models improve, taste decides which one a reviewer keeps. Every pool measured here leans on it, and none of them defines it in a form anything can check.

Reviewers work from written criteria that stay qualitative. [Terminal-Bench](https://github.com/harbor-framework/terminal-bench/blob/main/docs/REVIEWING.md) asks whether a task is difficult for a good reason and whether it resembles work someone is paid to do. [Harbor-Index](https://arxiv.org/abs/2609.04298) had a senior panel weigh difficulty, diversity, and the insight a task gives into model behavior. Both lists need a human to apply them.

Learning the judgment from examples takes both halves of a review, the tasks reviewers kept and the ones they turned down, and currently very few benchmarks publish both. [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) is the exception, where raters called 935 of 1,699 tasks valid, OpenAI kept 500, and the 435 sound tasks it passed over are the half that goes missing everywhere else. A model fitted to those two groups and tested on tasks it has not seen picks the kept task out of a pair 60% of the time, against 50% for a coin flip. The signal is real and nowhere near strong enough to accept or reject a task on.

No other pool carries enough rejections to repeat the test. Terminal-Bench 2.1 kept 26 of its 84 valid tasks, and Harbor-Index keeps 82 drawn from 29 source benchmarks. Taste today has neither a definition a machine can check nor a labeled set big enough to learn one from.

## Conclusion and future work

The four properties split on verifiability. Soundness reduces to a two-probe container run. Difficulty reduces to attempt counts against a named model. Durability needs a capability axis that separates the model from the harness that ran it, and today's trial data joins the two into a single submission. Taste needs benchmarks to publish the candidates their reviewers rejected, not only the tasks they kept. Nobody can fit a keep label where the rejects stay private. One reconstruction recovered labels for all 6,627 candidates, and only because the trial data survived outside the benchmark.

One question sits underneath all four, and nobody has answered it. These properties may or may not predict a task's downstream value. Nothing measured here shows that data selected this way trains a better model, and that experiment would settle more than any of the measurements above.

Datasource: [evaltrials](https://github.com/Evan-Kim2028/evaltrials).
