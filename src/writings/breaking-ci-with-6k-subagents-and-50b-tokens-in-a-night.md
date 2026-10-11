---
title: "Breaking CI with 6k Subagents and 50B Tokens in a Night"
date: "2026-10-11"
collection: data
lede: false
tags:
  - writing
  - data
  - agents
  - ci
  - devops
  - merge-trains
  - muse
  - space-bunny
  - deepseek
source_url: https://github.com/Evan-Kim2028/lake-of-rage
source_platform: github
slug: breaking-ci-with-6k-subagents-and-50b-tokens-in-a-night
hero: /assets/images/agent-fleet-ci-hero.png
hero_dark: /assets/images/agent-fleet-ci-hero.dark.png
og_image: /assets/images/agent-fleet-ci-hero.dark.png
description: "6,000 agent sessions and 50B tokens in one night jammed CI with 150 half-finished PRs. Local test gates and merge trains cut test time per PR five-fold."
---

<!-- vale House.FirstPerson = NO -->
<!-- vale Google.Headings = NO -->
<!-- vale Google.Slang = NO -->
<!-- cspell:ignore bursty deepseek -->

## Intro

A couple weeks ago, I took advantage of the free unnamed model space bunny. I quickly discovered
that there were truly "no limits" by spinning up about
[100 subagents at once (over 4,000 output tokens/second combined at peak)](https://x.com/EvanDeKim/status/2103867433060569143)
in an attempt to work through my GitHub issue backlog.

I had one open question: "If I burn tens of billions of tokens, what does the output look like?"

Excited, I started a workflow and went to sleep. The next day, almost 50 billion tokens later, I
woke up eager to see what progress had been made. To my chagrin, a massive traffic jam had occurred
somewhere. There were about 150 open PRs across both repos, all half finished, and the agent swarm
had stopped working sometime during the night.

An initial diagnosis revealed that the bottleneck was CI. It couldn't support the sustained burst of
work from hundreds of agents. By design, there was no hosted CI in the loop, to avoid spending money
on hosted runners. Each agent would run tests on its own branch locally and merge on green. This was
fine at sub-hundred-agent scale, but not at a scale of thousands of agents. Nearly 6,000 agents had
launched, but only 156 of them got as far as opening a PR and only 3 of those PRs merged.

Digging further, the problems became apparent:

1. **The test selector picked far too much. A 100-line change often ran the full suite, so even
   simple PRs jammed up the CI.**
2. **Every PR was also being tested about twice, both times on the runners:** once when the branch
   was pushed, and again on main after it merged, plus re-runs of failed or superseded jobs.

I diverted the fleet to cut down every inefficiency I saw. The goal was simple. If I change a few
files, the PR should merge with green CI within a minute or two.

Fixing both of these issues cut test time per PR about five-fold. The average PR wait went from
~60 minutes to under 5, which let me triple output from ~60 to ~180 PRs a day while spending fewer
resources on CI.

## Fixing the CI

On Oct 2, the full suite was thinned out and stopped from running on every PR, but it made no real
difference. The real impact came on Oct 5, when CI runs per PR were cut from 2 to 1.

There was a brief spike on Oct 9, when a massive database migration workflow, roughly +50k/-50k
LOC, introduced a bug in the CI. The fix landed that night and minutes per PR dropped back down.

<figure class="fig-inline">
{% include "figures/agent-fleet-ci/minutes.svg" %}
<figcaption><strong>Figure 1:</strong> Python test minutes per merged PR on lake-of-rage. Runner
minutes from the CI provider's API plus laptop test time from agent logs, scaled to runner
speed.</figcaption>
</figure>

Today the CI is holding up great. Over the last ~10 days and 30 billion tokens, there have been no more
traffic jams, and Oct 10 was the first time breaking over the 200 PR count.

<figure class="fig-inline">
{% include "figures/agent-fleet-ci/tokens.svg" %}
<figcaption><strong>Figure 2:</strong> Input tokens per day by model, from each agent CLI's local
session logs on the laptop and the lake-of-rage VPS, Sep 20 to Oct 10. The line is PRs merged per
day across both repos.</figcaption>
</figure>

## Local test gates and merge trains

Now that CI was under control, the next step was future-proofing the codebase. If the number of
PRs doubles, how does the time to ship a PR stay the same, or better yet drop? Only a quarter of
runner test time went to the run that let a PR merge. The rest was failure re-runs, runs cancelled
by a newer push, and the re-test on main after every merge.

Two key observations.

1. Agent fleet work is bursty. Over 24 hours there is plenty of compute available on the VPS and
   laptops, but most of the work comes while the human is managing the fleet during daylight hours
   across multiple terminals.
2. It was clear that the amount of re-computations from re-runs and run cancellations needed to be
   crushed.

<figure class="fig-inline">
{% include "figures/agent-fleet-ci/tests-per-branch.svg" %}
<figcaption><strong>Figure 3:</strong> Test files selected per branch merged, single-branch PRs
beside branches that rode a merge train. Selector replay of every lake-of-rage PR merged Oct 6 to
10; train member counts from PR bodies and merge commits.</figcaption>
</figure>

To handle the bursts, the bulk of the CI and running tests was moved locally to the laptops.
Initially self-hosted runners were run on a VPS server to get away from cloud hosted solutions.
However that became clogged within the day due to the agent PR bursts. Since the laptop generally
had spare capacity and more compute available, the bursts could be more easily absorbed and managed.

To reduce the amount of computational redundancy, PR trains were adopted. The main orchestrator
agent batches related branches into merge trains where a single monolithic PR can carry anywhere
from 3 to over 20 branches of work. The end result was that merging would not trigger a merging
storm, and since all of the CI was run locally on every branch, there was no need to re-run most of
the CI again after merge. Trains have been very productive so far. Over the last six days, 109
trains merged next to about 390 single-branch PRs.
