---
title: "What a 2B Data Agent Is Missing, One Hint at a Time"
date: "2026-10-03"
collection: data
lede: false
table_highlight: true
tags:
  - writing
  - data
  - evals
  - agents
  - fine-tuning
  - information-ladder
source_url: https://github.com/Evan-Kim2028/smol-ladder
source_platform: github
slug: what-a-2b-agent-is-missing
description: "The information ladder lifts Qwen3.5-2B from 24% to 35% with the method and to 69% with the reference program on 250 held-out data tasks, and shows the remaining gap is control."
series: Evals
series_index: 4
hero: /assets/images/smol-ladder-hero.png
hero_dark: /assets/images/smol-ladder-hero.dark.png
og_image: /assets/images/smol-ladder-hero.dark.png
---

<!-- vale House.FirstPerson = NO -->
<!-- vale Google.Headings = NO -->
<!-- vale Google.Slang = NO -->

## TL;DR

- **The ladder locates the gap.** Telling `Qwen3.5-2B` the method lifts it from 24% to 35% on
  held-out data-analysis tasks, and handing it the reference program lifts it to 69%. With the
  program in hand, easy, medium and hard tasks pass at nearly the same rate.
- **The rest of the gap is control, and control is trainable.** Given a plan, the model stops by
  itself and commits to an answer in 84% of episodes, against 47% from the question alone. In 36
  unanswered episodes the correct value was already on screen, so commitment alone is worth up to
  14 points.
- **Fine-tuning changes how the model behaves.** A model fine-tuned on 4,439 verified trajectories
  holds its accuracy when behavior rules join the prompt, 8 points above the base model, and gains
  7.5 points more from the column hints.

## Intro

[SmolDataEnvs](https://huggingface.co/collections/FineEnvs/smoldataenvs) is a set of 5,000
data-analysis tasks: a question about one or more CSV files, a deterministic grader, and a held-out
test split of 250 harder tasks. The intended use is RL on a small model, with supervised fine-tuning
on 4,677 verified agent trajectories as the first step.

Before training anything, a more basic question needs an answer. When a model this small misses one
of these tasks, what is it missing? Is it *what* to compute, or how to *carry it out*? The answer
decides what kind of training can help. Imitation teaches a style of working, a hint curriculum
teaches what to compute, and RL rewards finishing.

Two things happened to `Qwen3.5-2B`. We ran it up an
[information ladder](/writings/difficulty-is-an-information-gap/): the same question asked with
progressively more of the solution revealed, so the gap between rungs says what the model lacked.
And we fine-tuned it on trajectories, then ran the fine-tuned model up the same ladder. The ladder is
the instrument from the previous post in this series, applied to a model instead of a benchmark.

## The Ladder

Each rung is a prefix of the next, and the model still does all the work at every rung: run the
commands, read the output, write the answer to a file.

| Rung | The model gets |
|---|---|
| L1 | the question and the file names |
| L2 | L1 plus the files, columns and filters the reference solution used |
| L3 | L2 plus the method, in plain words: which split, which model, which aggregation |
| L4 | L3 plus the verified reference program itself, without its final print |

L4 is the diagnostic ceiling: it measures execution alone, with the knowledge supplied. A stronger
model wrote the hints from the verified solution, a leak check screened them, and the L2 to L4 rungs
exist for the 213 of the 250 tasks with a verified reference.

Take one task from the test split: "What is the difference between the highest and lowest test
accuracy scores among the classifiers evaluated on the Iris dataset?" The reference answer depends
on which classifiers, which train and test split, and which seed. L2 adds that the solution read the
4 measurement columns and `Species`. L3 adds the recipe: shuffle, `test_size=0.25`,
`random_state=42`, fit 8 named classifiers, and round the difference to 6 decimals. L4 adds the
30-line program. The base model passed this task at L3 and L4.

## The Setup

The agent has one tool, `bash`, in a sandbox with the data under `/home/user/input`, up to 16 turns,
and must finish by writing only the answer to `/workdir/answer.txt`. The prompt is byte-identical to
the one in the SFT trajectories, checked by replaying every training row through the harness.
Evaluation is at temperature 0 unless stated. A 60-task subset, stratified by difficulty, also ran
with 4 sampled attempts per task to measure how the numbers depend on the decoding.

Two SFT arms, LoRA rank 16, one pass each:

- **A**: upstream's 4,439 verified trajectories, after removing 4 that leak test questions.
- **B**: 1,897 trajectories we collected, by running a strong model through the *same* shell harness
  on tasks from a different pool and keeping the episodes the grader passed. B's rows look like A's:
  about 5 commands, half shell and half Python, the same command lengths.

All of it ran on one AMD MI350X spot instance for a total of $47.

## The Ladder Locates the Gap

<figure class="fig-inline">
{% include "figures/smol-ladder/ladder.svg" %}
<figcaption><strong>Figure 1:</strong> Pass rate by rung for the base model and A, with 95% intervals. The method is worth 5 to 15 points and the program about 44. A holds its accuracy when behavior rules join the prompt, the second group.</figcaption>
</figure>

| Rung | base | A | base, tasks gained / lost against L1 |
|---|---:|---:|---|
| L1: question | 24.0% | 25.6% | |
| L2: + columns | 23.5% | 31.0% | +19 / −28 |
| L3: + method | 34.7% | 36.1% | +34 / −19, p = 0.05 |
| L4: + program | 68.5% | 72.8% | +95 / −8, p < 0.001 |

Three things stand out.

**The lift comes from the method and the program.** The base model already finds the right columns
on its own, so its L2 matches its L1. The method in words is worth roughly 5 to 15 points, and the
program is worth about 44. What the model gains from is *deciding what to do*, then *the code for
it*.

**With the program in hand, difficulty flattens.** At L4 the base model passes 73% of easy, 69% of
medium and 65% of hard tasks. At L1 the same model passes 64%, 29% and 5%. "Hard" on this benchmark
means hard to know what to compute, and the model executes hard tasks as well as easy ones.

<figure class="fig-inline">
{% include "figures/smol-ladder/tiers.svg" %}
<figcaption><strong>Figure 2:</strong> Base model pass rate by difficulty tier at L1, L3 and L4. The spread between easy and hard is 59 points at L1 and 8 points at L4.</figcaption>
</figure>

**The last third is control.** With the program in hand the computation is right: 2 wrong numbers
in 213 tasks. Of the 67 remaining L4 misses, 25 report the wrong *kind* of value, a number where the
question wanted a label, 16 end in a loop, and 11 print whole tables into the context. Each of those
is a habit: reading the answer format, printing less, stopping once the value is on screen.

### Where the Episodes Go as Information Is Added

The same classifier over every episode of the base model, at each rung, shows what each hint fixes.

<figure class="fig-inline">
{% include "figures/smol-ladder/failures.svg" %}
<figcaption><strong>Figure 3:</strong> How the base model's episodes end at L1, L3 and L4. Blue is correct. The orange shades are wrong answers, and the grey shades are episodes that never wrote one.</figcaption>
</figure>

L3 fixes knowledge. With the method hint, wrong answers fall from 23% of episodes to 14% and correct
ones rise from 24% to 35%. L4 fixes the computation, taking correct episodes to 69% and repeat loops
from 34% of episodes down to 8%. The grey that remains at each rung is the part training can reach.

## Control Is Trainable

Every L1 episode of the base model, classified by how it ended:

| Outcome | Episodes |
|---|---:|
| correct | 60 |
| wrote an answer, wrong | 58 |
| repeated one command, which worked | 59 |
| repeated one command, which errored | 26 |
| explored for 16 turns | 26 |
| filled the context with a table | 21 |

In 36 of the unanswered episodes, one of the model's own commands had already printed the correct
value. Committing in those episodes alone would take the base model from 60 correct to as many as
96, from 24% to 38%, with no new knowledge.

The ladder also shows the habit can change. Given a plan at L4, the base model stops by itself in
84% of episodes, against 47% at L1, and its repeat-loop rate falls from 37% to 8%. The behavior
improves when the uncertainty goes away, so it responds to conditions, and a reward for finishing is
the condition RL supplies.

Fine-tuning moves the same habit from another direction. We appended 7 behavior rules to the L1
prompt: stop repeating commands, print only what you need, write the answer once you have it. Model
A kept its accuracy under the longer prompt, 24.8% against the base model's 16.8%, gaining 30 tasks
and losing 10 against base (p = 0.002). Trained behavior carries through a prompt change.

## What Fine-Tuning Changes

Fine-tuned on upstream's trajectories, model A matches the base model on the plain question and
separates from it wherever the prompt carries more.

| base against A, temperature 0 | base | A | A, tasks gained / lost against base |
|---|---:|---:|---|
| L1: question | 24.0% | 25.6% | +28 / −24 |
| L1 + behavior rules | 16.8% | 24.8% | +30 / −10, p = 0.002 |
| L2: + columns | 23.5% | 31.0% | +32 / −16, p = 0.03 |
| L4: + program | 68.5% | 72.8% | +31 / −22 |
| L4: episodes that wrote an answer | 84% | 91% | |

A turns the column hints into 7.5 more points than the base model does, keeps its accuracy under
added rules, and writes an answer more often at L1, L2 and L4. Its validation loss fell from 0.49 to
0.38 over the same run.

<figure class="fig-inline">
{% include "figures/smol-ladder/sft-l1.svg" %}
<figcaption><strong>Figure 4:</strong> L1 pass rate by model. Left: one greedy attempt on all 250 tasks. Right: 4 sampled attempts per task on 60 tasks. With sampling, the three models score within 4 points of each other.</figcaption>
</figure>

| L1, 60 tasks, 4 sampled attempts | Pass | 95% CI | Episodes ending in a repeat loop |
|---|---:|---|---:|
| base | 20.0% | 12.5 to 27.9 | 18% |
| A | 22.5% | 15.0 to 31.7 | 39% |
| B | 18.8% | 11.7 to 26.2 | 14% |

Model B, trained on our own trajectories, matches the other two when sampled and loops least of the
three. It is also the model most sensitive to decoding: at temperature 0 it scores 10.8% and 13.6%
on two seeds, as greedy decoding amplifies its `print`-heavy style into long repeated commands. For
B, sampled evaluation is the setting that shows what it learned.

## What It Means

**About the ladder.** The ladder localized the gap for a few dollars of GPU. Each rung removes one
kind of ignorance while leaving the work to the model, so the gaps are attributable in a way a loss
curve is not: 5 to 15 points for the method, 44 for the program, and a last third that is control.
L3 is the training rung, since it raises the pass rate from 24% to 35% with the model still doing
all the work, which gives RL reward groups a signal to learn from. L4 is the ceiling to measure
progress against: when a trained model's L1 approaches its own L4, control is solved and the
remaining gap is knowledge.

**About SFT.** One pass on verified trajectories shifts behavior more than accuracy. The fine-tuned
model answers more often, uses hints better, and holds up under prompt changes, and those are the
behaviors the ladder says are scarce. The ladder is what made that visible: on the plain question
the two models look the same, and the difference appears on the rungs.

## Measuring a Small Benchmark

Three practices made these results readable.

1. **Pair on completed common sets.** Easy tasks finish first, so every comparison here uses the
   tasks all models finished, paired per task, with tasks gained and lost beside the rate.
2. **Repeat sampled attempts.** A 60-task run with one sampled attempt put A ahead 20 to 9. With 4
   attempts per task the gap is 2.5 points. Per-task pass rates over repeats are the stable unit.
3. **Count churn.** Of the tasks the base model solved at L1, 68% were solved again at L3. A rung
   has shown a lift when its gains far outnumber its losses, which Figure 5 reports for each one.

<figure class="fig-inline">
{% include "figures/smol-ladder/gained-lost.svg" %}
<figcaption><strong>Figure 5:</strong> Tasks the base model gained and lost against L1 at each rung. The program gains 95 tasks and loses 8, and the method gains 34 and loses 19.</figcaption>
</figure>

The reading rules for the last runs were written before running them: two seeds for B, and a
sampled difference counts only if its interval excludes zero.

## Conclusion

A small data agent's gap on these tasks has two parts that a solve rate reports as one: knowing what
to compute, and committing to an answer. The information ladder separates them, puts a number on
each, and names the rung an RL curriculum should use. Fine-tuning on trajectories moves the second
part, and the ladder is the instrument that shows it.

These results have 3 main limitations. The ladder ran once per task at temperature 0, so the L2 and
L3 steps carry about as much uncertainty as their size, while the L4 step and A's edge under added
rules are well clear of it. The sampled repeats cover 60 tasks and L1 only. And the behavior rules
were one wording tried once.

What comes next is GRPO with the L3 rung as a curriculum, withdrawn as per-task pass rates rise. The
ladder says what is scarce is a reward for finishing, and that is what RL supplies.

---

*Code, prompts, run trees and the per-episode classifier:
[smol-ladder](https://github.com/Evan-Kim2028/smol-ladder). Earlier in this series: [The
Information Ladder: Measuring Model Capabilities](/writings/difficulty-is-an-information-gap/).*
