---
title: "5.3-Flash Has Large Provider Cache Hit Variance"
date: "2026-08-30"
collection: latest
description: "GLM-5.3-Flash cache hit rates on OpenRouter ranged from 80% on Z.AI to 0% on DeepInfra and Fireworks. Quality clustered. Cost did not follow cache, because output tokens dominate this workload."
tags:
  - writing
  - latest
  - data
  - llm-inference
  - openrouter
  - benchmarks
source_url: https://x.com/EvanDeKim/status/2094186460282789994
source_platform: x
slug: glm-53-flash-provider-cache-hit-variance
---

## TL;DR / Summary

GLM-5.3-Flash was measured across five OpenRouter providers on a lakehouse repair gym. Cache hit rates ran from **80% (Z.AI)** to **0% (DeepInfra, Fireworks)**. Pass stayed between 53% and 62%. Cache did not order the bill: prompt cache only discounts input, and output tokens dominate this workload.

GLM-5.3-Flash, released 26 August 2026 ([Z.AI](https://z.ai/blog/glm-5.3-flash)), was measured across 5 providers on OpenRouter on a custom data pipeline evals dataset. The results showed significant variance across all of the providers.

| Provider | Cache hit rate |
| --- | ---: |
| Z.AI | 80% |
| Novita | 31% |
| GMI | 24% |
| DeepInfra | 0% |
| Fireworks | 0% |

Although quality clustered, where every provider passed 53%-62% of tasks, the cache hit rate and end cost did not cluster. The most striking observation was that Z.AI had the highest cache rate, at 80%, across all 5 providers.

The provider caching variance is because GLM-5.3-Flash is an entirely new hybrid linear + sparse **attention** architecture that requires a different inference stack. Linear layers keep a running state for nearby tokens. Sparse layers keep a smaller KV and an indexer for the rest of the context. Z.AI’s [Flash blog](https://z.ai/blog/glm-5.3-flash) mentioned that they built a custom SGLang inference stack on 100% chinese gpus with significant help from their own internal GLM-5.3 infrastructure agent in the loop for kernel optimization.

## Provider benchmark results

The providers were benchmarked on [data-pipeline-eval](https://github.com/Evan-Kim2028/data-pipeline-eval), a small public gym of lakehouse incidents taken from personal production repairs where I've noticed agents predictably fail. The results showed extreme levels of provider variance in caching, with Z.AI scoring 80% while DeepInfra and Fireworks scored 0% and Novita and GMI scoring 31% and 24% respectively.

| Provider | Cache hits | Pass | Average hops | Total tokens | Cost |
| --- | ---: | ---: | ---: | ---: | ---: |
| Z.AI | 36/45 (80%) | 25/45 (56%) | 8.0 | 58,786 | $0.010* |
| Novita | 14/45 (31%) | 24/45 (53%) | 13.1 | 72,502 | $0.014* |
| GMI | 11/45 (24%) | 24/45 (53%) | 9.0 | 58,301 | $0.011* |
| DeepInfra | 0/45 (0%) | 28/45 (62%) | 5.0 | 50,216 | $0.009* |
| Fireworks | 0/45 (0%) | 24/45 (53%) | 5.4 | 48,771 | $0.018 |

\* Cost already includes OpenRouter’s 50% off list through 9 Sep 2026. Fireworks bills full list.

Nine of the hardest broken pipeline problems were tested across 5 rounds per provider, totaling 45 one-shot calls per provider. The same prompt, 0 temperature, and high reasoning effort settings were used across every round and provider.

The nine jobs sit in four categories.

- **Serving.** The next run treats the wrong thing as current or done. Watermarks advance before commit. Output mtime marks unread files as consumed. A catalog drop causes the next writer to recreate the table.
- **Incremental I/O.** A cheap probe plans a full scan, or a retry starts at record one. Empty-key reloads, unique() against a start-of-run snapshot, partitioned writes followed by full-tree reads, and rebuilds that wipe the checkpoint all create this failure mode.
- **Schema.** Schema and field identity drift across runs. A column is dropped, the same name is added back, and the old identity gets reused.
- **Time.** The wrong clock closes the window. Processing-time closes can cause late event-time facts to vanish.

## Why cache hit rates differ across providers

The cache efficiency heavily depends on the provider inference setup. Z.AI scored the highest because they built a custom inference stack around the caching requirements of 5.3-Flash. The other providers serve 5.3-Flash through more general inference infrastructure. The five providers use materially different infrastructure:

- **Z.AI.** Own Chinese-chip cluster, memory-tight accelerators, not NVIDIA. Custom SGLang engine for 5.3-Flash.
- **Novita.** Rented NVIDIA, H200-class for a model this size. Shared serverless pool. Stock vLLM or SGLang.
- **GMI.** Own NVIDIA fleet, H100 and H200 today, B200 and GB200 in the same cloud. Inference Engine picks vLLM, SGLang, or TensorRT-LLM per model.
- **DeepInfra.** Own US B300s (288 GB Blackwell). TensorRT-LLM kernels plus Dynamo to split prefill and decode.
- **Fireworks.** Own multi-cloud NVIDIA fleet, H100 through GB300. In-house engine.

One observation/speculation is around routing. A cache hit requires the next request to reach a replica that still holds the cached state. A provider can have a working prefix cache and still get poor cache hit rates if requests move between replicas.

The provider needs to manage the model's cached state, keep the relevant replicas warm, and route repeated prefixes back to the right replica.

## What this costs

The significant cache hit difference did not translate directly into a significant cost difference.

{% chart "assets/charts/glm-53-flash-cache-vs-cost.json", "<b>Figure 1.</b> Cache hit rate versus total spend at $0.15 input, $0.03 cached, $0.50 output. Marker size is total tokens. Cache hit rate does not order the bill." %}

Prompt cache only discounts input. Input size is almost the same on every provider, about 19k to 20k tokens across the 45 calls and the rest being output tokens. For instance Novita had 52k and DeepInfra had 30k output tokens.

Z.AI’s list is $0.15 per million input, $0.03 cached input, and $0.50 output. OpenRouter takes 50% off that list for Z.AI, Novita, GMI, and DeepInfra through 9 Sep 2026. Fireworks stays on full list.

DeepInfra looks cheapest on billed spend because of that coupon and because it stops thinking earlier on the three unsolved incidents. In contrast Novita did the complete opposite and went into an overthinking spiral on the same problems.

The key point is that cache efficiency and total cost are separate optimization problems. Z.AI gets the highest cache hit rate, but output tokens dominate this workload.

![Input versus output share of the bill](/assets/images/glm-53-flash-input-vs-output.png)

*Red is the input share of each bill. Prompt cache only discounts that slice.*

## Limitations and follow-up work

This evaluation covers a niche dataset of nine pipeline incidents and 45 calls per provider. A larger benchmark and more evaluation datasets are needed to verify that the cache behavior is robust across different workloads.

On this workload, output therefore dominates the bill. Input is roughly 19k to 20k tokens across the 45 calls, while output ranges from 30k to 52k tokens. Prompt caching only discounts the input side.

If the goal is to maximize cache efficiency, higher cache hit rates should reduce input costs, but the total savings depend on how much of the bill comes from input in the first place.

The Fireworks numbers are from OpenRouter. Fireworks' own API documents extra cache settings for direct use, including a session-affinity key that can pin repeats to the replica holding the prefix. OpenRouter did not have a way to send those settings. A direct Fireworks run of this workload might cache differently.

The 50% discount on four providers also ends 9 Sep 2026, so these absolute costs are specific to this pricing window.
