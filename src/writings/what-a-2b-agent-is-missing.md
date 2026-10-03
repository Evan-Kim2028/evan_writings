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
description: "Fine-tuning Qwen3.5-2B on verified trajectories leaves it at the base model's 24%. The information ladder shows why: the method lifts it to 35%, the program to 69%, and a third fail even then."
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

- **Fine-tuning on trajectories changed nothing.** One pass of LoRA SFT on 4,439 verified
  trajectories leaves `Qwen3.5-2B` at 25.6% against the base model's 24.0% on 250 held-out tasks, and
  the released upstream adapter scores 19.2%. Our own trajectories make the model fragile at greedy
  decoding and are otherwise neutral.
- **The ladder says the gap is knowing what to compute.** Telling the base model the method lifts it
  from 24% to 35%, and handing it the reference program lifts it to 69%. With the program in hand,
  easy, medium and hard tasks pass at nearly the same rate.
- **Control is the wall, and it cannot be asked for.** More than half of the base model's episodes
  end with no answer, and in 36 of them the correct value was already on screen. Adding behavior
  rules to the prompt made the model worse, from 24.0% to 16.8%.

## Intro

[SmolDataEnvs](https://huggingface.co/collections/FineEnvs/smoldataenvs) is a set of 5,000
data-analysis tasks: a question about one or more CSV files, a deterministic grader, and a held-out
test split of 250 harder tasks. The intended use is RL on a small model, with supervised fine-tuning
on 4,677 verified agent trajectories as the first step.

Before training anything, a more basic question needs an answer. When a model this small fails one of
these tasks, what is it missing? Does it not know *what* to compute, or does it know and fail to *carry it
out*? The answer decides what kind of training can help. Imitation teaches a style of working, a
hint curriculum teaches what to compute, and RL rewards finishing. They are not interchangeable.

Two things happened to `Qwen3.5-2B`. We fine-tuned it on trajectories, and we ran it up an
[information ladder](/writings/difficulty-is-an-information-gap/): the same question asked with
progressively more of the solution revealed, so the gap between rungs says what the model lacked.
The ladder is the same instrument as in the previous post in this series, applied to a model instead
of a benchmark.

## The Ladder

Each rung is a prefix of the next, and the model still does all the work at every rung: run the
commands, read the output, write the answer to a file.

| Rung | The model gets |
|---|---|
| L1 | the question and the file names |
| L2 | L1 plus the files, columns and filters the reference solution used |
| L3 | L2 plus the method, in plain words: which split, which model, which aggregation |
| L4 | L3 plus the verified reference program itself, without its final print |

L4 is the diagnostic ceiling. If the model fails with working code in front of it, the problem is
not knowledge. The hints were written by a stronger model from the verified solution and checked for
leaks, and the L2 to L4 rungs exist for the 213 of the 250 tasks with a verified reference.

Take one task from the test split: "What is the difference between the highest and lowest test
accuracy scores among the classifiers evaluated on the Iris dataset?" The question does not say
which classifiers, what train and test split, or what seed, and the reference answer depends on all
3. L2 adds that the solution read the 4 measurement columns and `Species`. L3 adds the recipe:
shuffle, `test_size=0.25`, `random_state=42`, fit 8 named classifiers, and round the difference to 6
decimals. L4 adds the 30-line program. The base model failed this task at L1 and L2 and passed it at
L3 and L4.

## The Setup

The agent has one tool, `bash`, in a sandbox with the data under `/home/user/input`, up to 16 turns,
and must finish by writing only the answer to `/workdir/answer.txt`. The prompt is byte-identical to
the one in the SFT trajectories, checked by replaying every training row through the harness.
Evaluation is at temperature 0 unless stated. A 60-task subset, stratified by difficulty, also ran
with 4 sampled attempts per task to see how much the greedy numbers depend on the decoding.

Two SFT arms, LoRA rank 16, one pass each:

- **A**: upstream's 4,439 verified trajectories, after removing 4 that leak test questions.
- **B**: 1,897 trajectories we collected, by running a strong model through the *same* shell harness
  on tasks from a different pool and keeping the episodes the grader passed. B's rows look like A's:
  about 5 commands, half shell and half Python, the same command lengths.

All of it ran on one AMD MI350X spot instance for a total of $44, including a first session that
produced nothing usable.

## Fine-Tuning Does Not Move Accuracy

| L1, 250 tasks, temperature 0 | Pass | 95% CI | Tasks gained / lost against base |
|---|---:|---|---|
| base | 24.0% | 18.8 to 29.2 | |
| A | 25.6% | 20.4 to 31.2 | +28 / −24, p = 0.68 |
| B, seed 1 | 10.8% | 7.2 to 14.8 | +10 / −43, p < 0.001 |
| B, seed 2 | 13.6% | 9.6 to 18.0 | +12 / −38, p < 0.001 |

A is indistinguishable from the untrained model. Its validation loss had flattened (0.49 to 0.38),
so this is not an under-trained run. It learned to imitate the trajectories, and that did not
translate into more correct answers. Upstream's own released SFT adapter scores 19.2% on the same
tasks, also no better than base.

B is worse than base on both seeds, and not because the data is wrong. Every row is a verified
solution, and in style the rows are as short as A's. The small model trained on them degenerates
at greedy decoding into long runs of `print` lines that hit the output limit and get cut off with an
unclosed quote, 1,050 such commands over 250 tasks, and then it loops. With sampling the effect
disappears.

<figure class="fig-inline">
{% include "figures/smol-ladder/sft-l1.svg" %}
<figcaption><strong>Figure 1:</strong> L1 pass rate by model. Left: one greedy attempt on all 250 tasks. Right: 4 sampled attempts per task on 60 tasks. The three models are equivalent when sampled, and B collapses only at temperature 0.</figcaption>
</figure>

| L1, 60 tasks, 4 sampled attempts | Pass | 95% CI | Against base |
|---|---:|---|---|
| base | 20.0% | 12.5 to 27.9 | |
| A | 22.5% | 15.0 to 31.7 | p = 0.69 |
| B | 18.8% | 11.7 to 26.2 | p = 0.70 |

The three models are equivalent when sampled, and B is fragile at temperature 0. That fragility
is a real cost, since greedy is the cheap, deterministic way to evaluate, but it is a decoding
interaction, not evidence that the trajectories taught anything wrong.

## The Ladder Says the Model Does Not Know What to Compute

<figure class="fig-inline">
{% include "figures/smol-ladder/ladder.svg" %}
<figcaption><strong>Figure 2:</strong> Pass rate by rung for the base model and A, with 95% intervals. Columns alone change nothing, the method is worth 5 to 15 points, and the program is worth about 44. Behavior rules, the second group, cost the base model 7 points.</figcaption>
</figure>

| Rung | base | A | base, tasks gained / lost against L1 |
|---|---:|---:|---|
| L1: question | 24.0% | 25.6% | |
| L2: + columns | 23.5% | 31.0% | +19 / −28, p = 0.24 |
| L3: + method | 34.7% | 36.1% | +34 / −19, p = 0.05 |
| L4: + program | 68.5% | 72.8% | +95 / −8, p < 0.001 |

Three things stand out.

**Columns alone are indistinguishable from nothing.** The base model already finds the right
columns, so L2 is flat. The method in words is worth roughly 5 to 15 points, and the program is worth
about 44. The failures concentrate in *deciding what to do*, then in *writing the code for it*, and
only last in running it.

**With the program in hand, difficulty stops mattering.** At L4 the base model passes 73% of easy,
69% of medium and 65% of hard tasks. At L1 the same model passes 64%, 29% and 5%. "Hard" on this
benchmark means hard to know what to compute, not hard to execute.

<figure class="fig-inline">
{% include "figures/smol-ladder/tiers.svg" %}
<figcaption><strong>Figure 3:</strong> Base model pass rate by difficulty tier at L1, L3 and L4. The spread between easy and hard is 59 points at L1 and 8 points at L4.</figcaption>
</figure>

**A third of tasks fail even with the code.** Of the 67 L4 failures, 32 are wrong answers and 25 of
those are the wrong *kind* of answer: a number where the question wanted a label, or "Not Applicable." Another
16 end in a loop, and 11 ran the context out by printing whole tables. None of that is knowledge. It is
control: reading the question's answer format, not re-printing the data, stopping once the value is
on screen.

### Where the Failures Go as Information Is Added

The same classifier over every failed episode of the base model, at each rung, shows what each hint
fixes and what it leaves alone.

<figure class="fig-inline">
{% include "figures/smol-ladder/failures.svg" %}
<figcaption><strong>Figure 4:</strong> How the base model's episodes end at L1, L3 and L4. Blue is correct. The orange shades are wrong answers, and the grey shades are episodes that never wrote one.</figcaption>
</figure>

L3 fixes knowledge and leaves control alone. The method hint halves the wrong answers, with
"different number" falling from 18 to 8, but 109 of its 139 failures still end with no answer, about
the same as at L1, and in 39 of them the right value had been printed. Context exhaustion rises,
from 21 episodes to 31, because a model that knows the method writes longer scripts and prints more.

L4 leaves only control. With the program in hand the computation is essentially right, with 2 wrong
numbers in 213 tasks. What remains is reporting the wrong kind of value after running the code, and
not committing at all.

## Control Is the Wall, and It Cannot Be Asked For

Every L1 episode of the base model, classified by how it ended:

| Outcome | Episodes |
|---|---:|
| correct | 60 |
| never wrote an answer | 132 |
| &nbsp;&nbsp;repeating one command, which worked | 59 |
| &nbsp;&nbsp;repeating one command, which errored | 26 |
| &nbsp;&nbsp;16 turns of exploring | 26 |
| &nbsp;&nbsp;filled the context with a table | 21 |
| wrote a wrong answer | 58 |

More than half of all episodes end with no answer at all, and in about 36 of them the correct value
had already been printed by one of the model's own commands. The model is not short of the ability
to compute. It is short of the habit of committing.

The obvious fix is to tell it. We appended 7 behavior rules to the L1 prompt: stop repeating
commands, never print whole tables, write the answer once you have it. The base model got **worse**,
from 24.0% to 16.8%, with the loop rate rising from 37% to 47%. The fine-tuned A was unaffected,
25.6% to 24.8%. Control, at this size, is not a thing you can ask for.

That is also what the L4 ceiling is made of. Given a plan, the base model stops by itself in 84% of
episodes against 47% at L1. The behavior improves when the uncertainty is removed, which says the
behavior is trainable. The ceiling should move with training that rewards finishing, which is what
RL does and imitation does not.

## What It Means

**About SFT.** Imitation of trajectories is the wrong tool for this gap. The model already works in
the right style, reads files, writes working pandas, and solves most easy tasks. It fails on
decisions and on commitment, and one pass of SFT changed neither. Two things follow. Verified
trajectories are not automatically useful training data: both arms were correct solutions, neither
moved accuracy, and one made the model fragile. And loss is not the metric: A's validation loss fell
23% while its accuracy stood still.

**About the ladder.** The ladder did what it was built for and localized the failure. Each rung
removes one kind of ignorance while leaving the work to the model, so the gaps are attributable in
a way a loss curve never is: a few points for the method, 44 for the program, and a third of tasks
lost to control even at L4. L3 is the training rung, since it raises the pass rate from 24% to 35%
with the model still doing all the work, which is the difference between RL reward groups that are
all-zero and groups with signal. L4 is the ceiling to measure progress against: when a trained
model's L1 approaches its own L4, control is solved and the remaining gap is knowledge. The ladder
cost a few dollars of GPU and said more about what to train than the SFT runs did.

## On Noise, Since Small Benchmarks Lie

Three things bit us and are worth stating as rules.

1. **Subsets drift.** Easy tasks finish first, so every interim number flattered the trained models.
   Compare only on completed common sets, paired per task.
2. **A 60-task result is a coin.** A beat base 20 to 9 on a 60-task sampled run (p = 0.02). On 174
   tasks the gap was 7 points and insignificant, and on 240 attempts it was 2.5 points.
3. **Greedy determinism is not stability.** Of the tasks the base model solved at L1, only 68% were
   solved again at L3 with a strictly more informative prompt. One attempt per task at temperature 0
   measures the model *and* the prompt's exact wording. Several sampled attempts per task are the
   honest unit.

<figure class="fig-inline">
{% include "figures/smol-ladder/gained-lost.svg" %}
<figcaption><strong>Figure 5:</strong> Tasks the base model gained and lost against L1 at each rung. Churn flips tasks both ways about equally, so only a rung whose gains far outnumber its losses has shown anything. The program has; the columns have not; the method sits at the edge.</figcaption>
</figure>

The reading rules for the last runs were written before running them: two seeds for B, and a
sampled difference counts only if its interval excludes zero. Both seeds of B landed below base at
temperature 0, and no sampled difference cleared the bar.

## Conclusion

A small data agent fails these tasks for two reasons that look the same from a solve rate: it does not
know what to compute, and when it does, it does not commit to an answer. One pass of SFT on verified
trajectories touches neither. The information ladder separates them for a few dollars, puts a number
on each, and names the rung an RL curriculum should use.

These results have 3 main limitations. The ladder ran once per task at temperature 0, so the L2 and
L3 steps carry about as much uncertainty as their size, and only the L4 step and the control result
are beyond doubt. The sampled repeats cover 60 tasks and L1 only. And the behavior rules were one
wording tried once, so "control cannot be prompted" is a result about that prompt on this model, not
a theorem.

What comes next is GRPO with the L3 rung as a curriculum, withdrawn as per-task pass rates rise,
starting from the base model. The thing the ladder says is missing is a reward for finishing, and
that is what RL supplies.

---

*Code, prompts, run trees and the per-episode classifier:
[smol-ladder](https://github.com/Evan-Kim2028/smol-ladder). Earlier in this series: [The
Information Ladder: Measuring Model Capabilities](/writings/difficulty-is-an-information-gap/).*
