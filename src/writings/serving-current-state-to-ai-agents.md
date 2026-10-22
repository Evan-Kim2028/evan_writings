---
title: "Serving Current State to AI Agents: A Hot + Cold Architecture"
date: "2026-10-21"
collection: data
lede: false
tags:
  - writing
  - data
  - agents
  - postgres
  - iceberg
  - architecture
source_url: https://github.com/Evan-Kim2028/evan_writings
source_platform: github
slug: serving-current-state-to-ai-agents
description: "How a two-tier Postgres and Iceberg architecture design serves AI agents at scale."
---

<!-- vale Google.Headings = NO -->

Data that serves AI agents has to answer questions about current state fast, because agents can query far more often than people do. A person checks a price now and then, while an agent may check it at every step of a task. History matters too, but it belongs off that path.

Splitting the data into two stores keeps that path fast. Current state lives in one small, fast store, and history lives in a large, cheap one. Each question goes to the store built for it, and the agent never pays for a history scan when it only needs today's value.

## The data

Many businesses price entities with many variants, and the split matters most when those variants multiply into millions of keys. A retailer prices SKUs by size, color and region. Each combination is a key with its own value, and values change all day. Trading cards show this shape at its extreme, and some back-of-the-napkin math sets the scale. About 50,000 cards, each in about 46 graded and raw conditions, gives over 2 million keys. That count is modest for a database, but large enough that the split between current state and history matters.

<figure class="fig-inline">
<img class="img-light" src="/assets/images/hot-cold-h1-composite-key.png?v=2" alt="A composite key of card, grader and grade that maps to one current row in Postgres and one append-only sales log in Iceberg" loading="lazy">
<img class="img-dark" src="/assets/images/hot-cold-h1-composite-key.dark.png?v=2" alt="A composite key of card, grader and grade that maps to one current row in Postgres and one append-only sales log in Iceberg" loading="lazy">
<figcaption><strong>Figure 1:</strong> Each card, grader and grade forms its own priced key, shown for Umbreon VMAX in PSA 10.</figcaption>
</figure>

Some keys on the same card trade every hour. Others trade once every couple of years, and a few keys log only a handful of sales in more than a year.

<figure class="fig-inline">
<img class="img-light" src="/assets/images/hot-cold-h1b-sales-density.png?v=2" alt="Sale dates for three keys of the same card, with PSA 10 dense and PSA 5 and CGC 6 sparse" loading="lazy">
<img class="img-dark" src="/assets/images/hot-cold-h1b-sales-density.dark.png?v=2" alt="Sale dates for three keys of the same card, with PSA 10 dense and PSA 5 and CGC 6 sparse" loading="lazy">
<figcaption><strong>Figure 2:</strong> Sale dates for three keys of one card, where the two CGC 6 sales share one day.</figcaption>
</figure>

## The architecture

The architecture puts current state in a hot Postgres tier and history in a cold Iceberg tier. Each key combines card, grader and grade into one flat composite key. Postgres holds the current value for every key, indexed by card, grader and grade and overwritten in place. Each entity has one serving table, the table that apps and agents read. Iceberg holds the full history and the wide detail that is mostly text. Redpanda, a streaming platform compatible with Kafka, carries incoming data. dbt models define the transforms, and Dagster runs them to feed both tiers. Those runs refresh Postgres on a schedule, and the `as_of` timestamp on every answer tells an agent exactly how fresh a value is.

Every key therefore maps to exactly one current row and one sales log. The design pairs a log with a materialized view, which is a table computed from the log and kept up to date. Iceberg holds each key's append-only sales log, and Postgres holds the current value derived from it. Jay Kreps laid out this idea in [The Log](https://www.linkedin.com/blog/engineering/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) (LinkedIn Engineering, December 16, 2013), and Martin Kleppmann extended it in [Turning the database inside out](https://martin.kleppmann.com/2015/03/04/turning-the-database-inside-out.html) (March 4, 2015). Machine learning teams have long used the same split, as Uber's [Michelangelo post](https://www.uber.com/blog/michelangelo-machine-learning-platform/) (September 5, 2017) and [Feast's docs](https://docs.feast.dev/how-to-guides/feast-snowflake-gcp-aws/read-features-from-the-online-store) describe for online and offline feature stores.

<figure class="fig-inline">
<img class="img-light" src="/assets/images/hot-cold-a-reference-architecture.png?v=2" alt="Reference architecture with Redpanda ingest, dbt and Dagster transforms, Iceberg history, Postgres current state, and tools that only read from both stores" loading="lazy">
<img class="img-dark" src="/assets/images/hot-cold-a-reference-architecture.dark.png?v=2" alt="Reference architecture with Redpanda ingest, dbt and Dagster transforms, Iceberg history, Postgres current state, and tools that only read from both stores" loading="lazy">
<figcaption><strong>Figure 3:</strong> Arrows show the direction data flows, from ingest to the tools that agents call.</figcaption>
</figure>

The two tiers stay separate all the way to the agent. The current-price lookup reads one hot Postgres row, and a trend question goes to a separate history lookup that scans Iceberg. Every result carries an `as_of` timestamp and a `source` field that reads "current" or "history", so an agent always knows which kind of answer it holds. Frequent questions about now never wait behind a scan of history.

<figure class="fig-inline">
<img class="img-light" src="/assets/images/hot-cold-h2-query-paths.png?v=2" alt="Three query paths side by side, with current value from the hot Postgres row, the trend from the Iceberg sales log, and a blocked path that returns a stale sale" loading="lazy">
<img class="img-dark" src="/assets/images/hot-cold-h2-query-paths.dark.png?v=2" alt="Three query paths side by side, with current value from the hot Postgres row, the trend from the Iceberg sales log, and a blocked path that returns a stale sale" loading="lazy">
<figcaption><strong>Figure 4:</strong> Values in the first two paths are real, and the blocked stale path is illustrative.</figcaption>
</figure>

The split needs a clear definition of what counts as current. Tiering by age, which keeps the last N days hot, is the usual default and still governs most rows. A rarely traded card breaks it, because its last sales may be years old and still set today's price. The business-rule hot set keeps a row hot when it falls inside the age window or when a live key needs it to compute today's answer, at any age. The long tail of the catalog keeps a current price, so rare items stay quotable and sellable.

<figure class="fig-inline">
<img class="img-light" src="/assets/images/hot-cold-b-core-idea-tiering.png?v=2" alt="Tiering by age compared with the business-rule hot set for a liquid card and a rare card" loading="lazy">
<img class="img-dark" src="/assets/images/hot-cold-b-core-idea-tiering.dark.png?v=2" alt="Tiering by age compared with the business-rule hot set for a liquid card and a rare card" loading="lazy">
<figcaption><strong>Figure 5:</strong> An illustrative case with no real data.</figcaption>
</figure>

## Speed and capacity

Serving current state from Postgres made the main routes much faster and let the same database carry agent workloads. Before the move, the API served reads from Parquet copies of the Iceberg data through DuckDB, and it now serves current state from Postgres. Web server request logs from the old path and from Postgres show p95 latency per call improving 6 to 33 times on the three main routes, and each figure covers a single call.

- Card detail went from 5.67 s to 0.51 s, while the logs recorded about 15 times as many requests.
- Chart went from 19.6 s to 0.60 s.
- Listings went from 8.2 s to 1.34 s.

<figure class="fig-inline">
<img class="img-light" src="/assets/images/hot-cold-e-p95-dumbbell.png?v=2" alt="p95 latency per call, old path vs Postgres, for card detail, chart and listings" loading="lazy">
<img class="img-dark" src="/assets/images/hot-cold-e-p95-dumbbell.dark.png?v=2" alt="p95 latency per call, old path vs Postgres, for card detail, chart and listings" loading="lazy">
<figcaption><strong>Figure 6:</strong> p95 latency per call on a log scale, from web server request logs on both paths.</figcaption>
</figure>

The deals endpoint shows how precomputed state holds up under load. Every 5 minutes, a background job ranks likely deals and stores them in a Postgres table. Each request takes the top rows and checks them again against live listings and live prices before returning them. The stored ranking holds the median response at about 44 ms, with 0 errors across 1,114 requests at up to 20 requests per second. The live check keeps every returned deal current, so a buyer can still act on it.

Whole agent workflows that chain several lookups stay fast as well. A workflow that checks a deal runs three steps, which are item detail, then listings, then fair value. Timed without load tuning and alongside other load on the same database, the whole workflow reached a p95 of 0.91 s for one agent and 1.31 s for ten agents running at once. That is fast enough for an agent to run while a person waits.

## What platforms automate

Platforms now automate the plumbing of this pairing, but the design choices that make it fast stay with the builder. The largest data platforms are converging on Postgres next to the lake. In 2025 Databricks [agreed to acquire Neon](https://www.databricks.com/company/newsroom/press-releases/databricks-agrees-acquire-neon-help-developers-deliver-ai-systems), and Snowflake [announced its intent to acquire Crunchy Data](https://www.snowflake.com/en/news/press-releases/snowflake-acquires-crunchy-data-to-bring-enterprise-ready-postgres-offering-to-the-ai-data-cloud/). Both deals cited AI agents as part of the reason. RedMonk's Stephen O'Grady [summed up the trend](https://redmonk.com/sogrady/2025/06/06/data-consolidation/) with the line "Convergence, put simply, is the goal."

Managed tools now handle much of the plumbing, such as copying finished lakehouse tables into Postgres. A managed sync copies whatever table it points at. Choosing the hot set, keying and indexing it, and labeling which rows are current and which are history stay with the builder. Those choices decide whether agents get fast, cheap answers about now, on any platform.
