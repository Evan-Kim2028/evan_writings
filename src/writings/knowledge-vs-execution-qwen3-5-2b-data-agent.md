---
title: "Knowledge vs Execution in a Qwen3.5-2B Data Agent"
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
  - sft
  - lora
  - qwen3.5-2b
source_url: https://github.com/Evan-Kim2028/smol-ladder
source_platform: github
slug: knowledge-vs-execution-qwen3-5-2b-data-agent
description: "One SFT pass with LoRA on verified SmolDataEnvs trajectories doesn't move Qwen accuracy. The information ladder shows why."
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

- **Knowledge vs execution.** On SmolDataEnvs' 250 held-out tasks, `Qwen3.5-2B` scores 24%
  bare, 35% with the method, and 69% with the reference program (the working solution code).
- **Execution.** A third still fails after seeing the reference program: loops, wrong formats,
  and answers never submitted. 36 episodes ended with the right answer on screen. The model submits
  in 84% of episodes with the program, against 47% without.
- **SFT.** One pass over 4,439 SmolDataEnvs-sft trajectories leaves bare-question scores
  unchanged. Gains show only on the rungs: 8 points above base with added behavior rules and 7.5
  more from hints naming the right columns. Although the tuned model gets more out of the prompt,
  it knows nothing new.

## Intro

[SmolDataEnvs](https://huggingface.co/collections/FineEnvs/smoldataenvs) is a set of 5,000
data-analysis tasks: a question about one or more CSV files, a deterministic grader, and a held-out
test split of 250 harder tasks. The intended use is RL on a small model, with SFT on 4,677
verified agent trajectories as the first step. The [tasks](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs),
[trajectories](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-sft), and
[code](https://github.com/adithya-s-k/FineEnvs/tree/main/04-smoldataenvs) are public, and this post
extends that work: same tasks, same trajectories, plus a ladder that separates what training moves.

Before training, one question needs an answer. When a model this small misses, is it missing
*what* to compute or how to *carry it out*? Imitation teaches a working style, hints teach what to
compute, and RL rewards finishing.

The two gaps are **knowledge** and **execution**. **Knowledge** is the missing information:
columns, method, and code.
**Execution** is turning that into an answer: running the code, reading the format, stopping,
and submitting.

`Qwen3.5-2B` went up an
[information ladder](/writings/difficulty-is-an-information-gap/): the same question with more of
the solution revealed at each rung. Then its SFT version climbed the same ladder. The miss splits into knowledge and execution, and SFT moves only the second.

## Ladder Setup

Two pieces make the measurement: the ladder and the agent that climbs it. Each rung is a prefix of the next. The model still does all the work at every rung: run the
commands, read the output, and write the answer to a file.

| Rung | The model gets |
|---|---|
| L1 | the question and the file names |
| L2 | L1 plus the files, columns, and filters the reference program used |
| L3 | L2 plus the method, in plain words: which split, which model, and which aggregation |
| L4 | L3 plus the verified reference program itself, without its final print |

L4 is the ceiling: knowledge supplied, execution measured. A stronger model, `stealth/space-bunny-alpha`, wrote the hints
from verified solutions, a leak check screened them, and L2 to L4 cover the 213 tasks with a
verified reference.

One task makes it concrete. It asks for the difference between the highest and lowest test
accuracy among classifiers on Iris.

- L1 shows only the question and the file listing.
- L2 adds the notes: read `Iris.csv`, use `SepalLengthCm`, `SepalWidthCm`, `PetalLengthCm`,
  `PetalWidthCm`, and `Species`, with no filters.
- L3 adds the method: the four measurements as features and `Species` as the target, a shuffled
  split with `test_size=0.25` and `random_state=42`, eight named classifiers scored on the test
  split, and highest minus lowest accuracy rounded to six places.
- L4 adds the verified program: 67 lines that load the table, fit the eight classifiers, and print
  the difference.

The agent climbing the ladder gets `bash` in a sandbox with 16 turns and must write only the answer to
`/workdir/answer.txt`. The prompt matches the SFT trajectories exactly. Decoding is greedy unless
stated. A 60-task subset also ran 4 sampled attempts per task. As a cross-check, the same 60
tasks under the stronger model score 72% in Harbor containers against 68% in our harness (gained 9,
lost 7, p = 0.80).

The run used two LoRA arms, rank 16, one pass each, against an untrained `Qwen3.5-2B` base, all for $47 on one AMD MI350X spot instance:

- **A**: 4,439 [SmolDataEnvs-sft](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-sft) trajectories (4,677 before filtering).
- **B**: 1,897 trajectories we collected with `stealth/space-bunny-alpha` in the same harness. It matches A
  in shape: about 5 commands, half shell and half Python.

## Execution vs Knowledge

<figure class="fig-inline">
{% include "figures/smol-ladder/ladder.svg" %}
<figcaption><strong>Figure 1:</strong> Pass rates by rung for base and A, with 95% intervals.</figcaption>
</figure>

The climb separates what the model doesn't know from what it can't carry out. Base climbs from 24% at L1 to 35% at L3 (gained 34 tasks, lost 19, p = 0.05) and 69% at L4
(gained 95, lost 8, p < 0.001). L2 matches L1: the model already finds the right columns. The lift is *deciding what
to do*, then *the code for it*.

With the program, difficulty flattens: 73% easy, 69% medium, and 65% hard at L4, against 64%,
29%, and 5% at L1. Hard here means hard to know what to compute.

<figure class="fig-inline">
{% include "figures/smol-ladder/tiers.svg" %}
<figcaption><strong>Figure 2:</strong> Base pass rates by tier at L1, L3, and L4, where the easy-hard spread falls from 59 points to 8.</figcaption>
</figure>

The last third is execution. At L4 the computation is right (2 wrong numbers in 213 tasks). Of the
67 misses, 25 report the wrong format, 16 loop, and 11 print whole tables. Habits: read the
format, print less, and stop once the value is on screen.

<figure class="fig-inline">
{% include "figures/smol-ladder/failures.svg" %}
<figcaption><strong>Figure 3:</strong> The chart splits base episodes at L1, L3, and L4 by ending. Blue is correct, orange is wrong answers, and gray never wrote one.</figcaption>
</figure>

L3 cuts wrong answers from 23% to 14%. L4 cuts repeat loops from 34% to 8% and lifts correct
episodes to 69%. The gray left at each rung is what training can reach.

### Execution Is Trainable

The opportunity is the no-answer episodes: at L1 the base model scored 60 correct, 58 wrong answers, and 132 with no answer. In 36 of
those 132, the model's own
commands had already printed the right value. Submitting there alone would take it from 24% to as
high as 38%, with no new knowledge.

The finishing habit responds to conditions and to training. At L4 the model submits an answer in
84% of episodes against 47% at L1, and loops fall from 37% to 8%. With 7 behavior rules appended
to L1, A holds 24.8% against base at 16.8% (gained 30, lost 10, p = 0.002). A reward for finishing
is the condition RL supplies.

### SFT Moves Behavior

Model A matches base on the bare question and separates wherever the prompt carries more:
it holds 24.8% under behavior rules against base at 16.8% (gained 30, lost 10, p = 0.002), gains 7.5 more
points from hints naming the right columns (31.0% vs 23.5%, p = 0.03), and submits an answer in 91% of L4 episodes
against 84%. Its validation loss fell from 0.49 to 0.38, so undertraining does not explain the flat bare-question score.

<figure class="fig-inline">
{% include "figures/smol-ladder/sft-l1.svg" %}
<figcaption><strong>Figure 4:</strong> L1 pass rates by model, greedy on the left and sampled on the right. The left panel uses one greedy episode on 250 tasks, while the right uses 4 sampled attempts per task on 60 tasks.</figcaption>
</figure>

Sampled, all three models agree: base 20%, A 23%, and B 19% on the 60-task set. B, trained on our own
trajectories, loops least (14% vs 18% base, 39% A) but is fragile at temperature 0, scoring 14% as greedy decoding amplifies its `print`-heavy style into repeated commands.

The SmolDataEnvs authors report no SFT-alone number. Their headline is the [GRPO endpoint](https://huggingface.co/AdithyaSK/smoldataenvs-grpo-2b-v0) on the 144-task eval split, so this fills a gap rather than disputing one. Across decodings, the result holds. SFT moves behavior, not accuracy.

## Results

For $47 of AMD MI350X time, the ladder returned attributable gaps: 5 to 15 points for the
method, 44 for the program, and a last third that is execution. L3 is the training rung, lifting the
pass rate to 35% with the model still doing all the work, giving RL reward groups a signal to learn from.
L4 is the ceiling: when a trained model's L1 nears its L4, execution is solved.

One SFT pass shifts behavior more than accuracy: Model A submits more often,
uses hints better, and holds up under prompt changes. The ladder made that visible. On the bare
question the two models look the same. This is the textbook signature of off-policy SFT: it
imitates a fixed demo distribution instead of optimizing the outcome, so it teaches style and
format (the [LIMA superficial-alignment hypothesis (2023)](https://arxiv.org/abs/2305.11206)).
It never trains on the model's own mistakes, so errors compound ([Ross and Bagnell
(2010)](https://proceedings.mlr.press/v9/ross10a.html)). The model saw 4,439 correct answers and
scores the same.

Three practices keep a benchmark this small readable.

1. **Pair on completed common sets.** Easy tasks finish first. Every comparison uses the tasks
   all models finished, with tasks gained and lost beside the rate.
2. **Repeat sampled attempts.** One attempt per task put A ahead 20 to 9. Four attempts per task
   shrank the gap to 2.5 points.
3. **Count churn.** Of the tasks base solved at L1, it solved only 68% again at L3. A rung shows a
   lift when gains far outnumber losses.

<figure class="fig-inline">
{% include "figures/smol-ladder/gained-lost.svg" %}
<figcaption><strong>Figure 5:</strong> The base model gained and lost tasks against L1 at each rung.</figcaption>
</figure>

We wrote one reading rule before the last runs: a sampled difference counts only if its
interval excludes zero.

## Conclusion

A solve rate reports two gaps as one: knowledge and execution. The ladder separates them,
puts a number on each, and names the rung for an RL curriculum. SFT moves the second gap and the
ladder shows it. GRPO comes next on an L3 curriculum, withdrawn as per-task pass rates rise, to
supply the scarce reward for finishing.

---

*Code, prompts, run trees, and the per-episode classifier:
[smol-ladder](https://github.com/Evan-Kim2028/smol-ladder). Earlier in this series: [The
Information Ladder: Measuring Model Capabilities](/writings/difficulty-is-an-information-gap/).*
