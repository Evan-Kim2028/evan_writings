---
title: "Building an Agentic Native MCP for Data Science"
date: "2025-10-01"
collection: latest
tags:
  - writing
  - latest
  - paragraph
source_url: https://paragraph.com/@evandekim/building-an-agentic-native-mcp-for-data-science
source_platform: paragraph
slug: building-an-agentic-native-mcp-for-data-science
---

## Introduction

This is a build log of my first steps building an MCP server for Snowflake. It captures what I tried, what exists today, what worked, what did not, and where I am going next. If you are exploring or building your own MCP, I hope these notes and code references save you time. For install and a quickstart, see the [igloo-mcp README](https://github.com/Evan-Kim2028/igloo-mcp).

### Table of contents

* Why I started building an MCP
* How igloo-mcp differs from Snowflake Labs MCP
* How igloo-mcp works
* Learnings
* What's next

## Why I started building an MCP

As a data scientist, there are always more questions than answers. I built `igloo-mcp` to optimize how agents run sequences of queries on my Snowflake database to answer the never ending stream of questions. The major benefit of agentic querying is that agents can quickly build the context needed to derive nontrivial insights with minimal instructions.

It's magical when everything works smoothly. I can rapidly debug and improve data pipelines, develop metrics faster, and also ask low priority but potentially interesting questions about datasets that I never had time to answer before. I also wanted a way to codify behaviors I found effective. MCPs are a natural choice to standardize tools that make agents' outputs more reliable and trustworthy.

Finally, I wanted to build the MCP from scratch to experiment with managing agents to design a repo from the ground up. When I use agents on the Snowflake database, I almost always use `igloo-mcp` to run tens of queries at a time. In contrast, building a repository lets me test multi agent workflows on code.

## How `igloo-mcp` differs from Snowflake Labs MCP

* Stacking on top instead of rebuilding: `igloo-mcp` boots the [Snowflake Labs MCP](https://github.com/Snowflake-Labs/mcp) runtime and layers catalog/dependency workflows on top, which keeps the upstream Cortex/object/query tools available while adding the metadata utilities I rely on.
* Zero config profiles vs YAML service maps: `igloo-mcp` reuses the SnowCLI profile that already exists on my machine, while Snowflake Labs MCP expects a `configuration.yaml` that lists Cortex services, tool groups, and SQL permissions before the server can start.
* Safety first execution path: `igloo-mcp` runs queries through the CLI to inherit profile RBAC, validate statements against allow/deny lists, check profile health, and optionally return verbose error diagnostics. Snowflake Labs MCP executes through the connector and surfaces failures through a generic `SnowflakeException`, leaving destructive statements enabled unless you turn them off in YAML.

## How `igloo-mcp` works

I evaluated Snowflake Labs MCP to understand its strengths and how to make an MCP that better fits my agentic workflows. `igloo-mcp` reflects those choices.

In practice, the server prioritizes safe, observable query execution for agent loops:

* Guardrails default to read‑only and provide clear, actionable messages when a statement is blocked (including when Snowflake classifies it as a generic `Command`).
* Each request can attach a short `reason` that is propagated to the Snowflake `QUERY_TAG` and to the optional local history, making it easy to correlate Snowflake history with local runs.
* Schema‑first tool design: each tool declares a tight JSON schema (with `additionalProperties=false`) and concrete examples so clients discover and call tools predictably.
* Predictable ergonomics: compact errors by default keep LLM loops clean; opt‑in verbose mode adds structured “quick fixes” when you need depth.

Currently, functionality includes:

### Tools

* `execute_query` — Executes SQL via SnowCLI; supports warehouse/database/schema/role overrides, allow/deny validation, timeouts, and optional verbose errors
* `preview_table` — Returns a limited preview of a table
* `build_catalog` — Builds metadata from INFORMATION\_SCHEMA (account or database scope) with JSON/JSONL output; includes DDL
* `get_catalog_summary` — Reads and returns catalog summary from a directory
* `build_dependency_graph` — Produces object dependency graph (JSON or DOT)
* `test_connection` — Verifies Snowflake connectivity using the configured profile
* `health_check` — Reports server and profile health

### Defaults

* SQL guardrails default to read-only. `INSERT`, `UPDATE`, `CREATE`, `ALTER`, `DELETE`, `DROP`, and `TRUNCATE` are blocked by default; can be explicitly opted into for controlled workflows. Statements Snowflake classifies as generic "Command" are also rejected by default.

### Execution

* Error handling:

  + Compact by default keeps agent loops readable and reduces noise
  + Verbose on demand includes a SQL snippet, timeout, and context for faster debugging
  + Profile health checks fail fast when a profile is missing or misconfigured
  + Allow/deny validation blocks risky or unsupported statements before anything runs
  + Clearer safety messages when Snowflake's parser falls back to a generic `Command` type, so agents know why a statement was blocked and what safe alternatives exist
  + Messages are formatted so MCP clients surface actionable feedback instead of long stack traces
* Session overrides: per request overrides for warehouse, database, schema, and role
* Timeouts & cancellation: per‑request timeouts are enforced; on local timeout a best‑effort server‑side cancel is issued and the tool returns immediately. Query ID is captured when available; verbose timeouts include concrete next steps.

### Observability

* Lightweight local query history (opt‑in): set `IGLOO_MCP_QUERY_HISTORY=/path/to/history.jsonl` to write one JSON object per executed query. Each event includes a status (`success`/`timeout`/`error`), a truncated statement preview, optional `query_id` (when available), `rowcount`/`duration_ms` for successful reads, the effective timeout, and any session overrides. The optional `reason` you pass is stored in both Snowflake `QUERY_TAG` and the local history, which makes it easy to join Snowflake account history with local events for auditing and debugging.

#### Why add local history?

* Tie agent prompts to database activity without standing up infra; JSONL is append‑only and portable.
* Correlate with Snowflake’s `ACCOUNT_USAGE.QUERY_HISTORY` by `QUERY_TAG` to get warehouse cost, bytes scanned, or execution profile.
* Debug timeouts and cancellations: even when `query_id` is missing, the preview + `reason` + status help reconstruct sequences.
* Lightweight telemetry: count queries per task, calculate duration distributions, and quickly spot recurring errors.

#### Enable and sample entries

```
export IGLOO_MCP_QUERY_HISTORY=./igloo_query_history.jsonl
```

Example lines (one JSON object per line):

```
{"ts": 1737412345, "status": "success", "profile": "quickstart", "statement_preview": "SELECT * FROM customers LIMIT 10", "rowcount": 10, "timeout_seconds": 30, "overrides": {"warehouse": "COMPUTE_WH"}, "query_id": "01a1b2c3d4", "duration_ms": 142, "reason": "Explore sample customers"}
{"ts": 1737412399, "status": "timeout", "profile": "quickstart", "statement_preview": "SELECT * FROM huge_table WHERE date >= '2024-01-01'", "timeout_seconds": 30, "overrides": {"warehouse": "COMPUTE_WH"}, "error": "Query execution exceeded timeout and was cancelled"}
{"ts": 1737412468, "status": "error", "profile": "quickstart", "statement_preview": "SELECT * FROM missing_table", "timeout_seconds": 30, "overrides": {}, "error": "Object 'MISSING_TABLE' does not exist."}
```

## Learnings

I pushed the boundaries to see where agent capabilities currently end. The biggest revelation was that agents cannot be trivially parallelized on large codebases. It requires thoughtful planning, and there are not yet great solutions to monitor multiple agents working on different things. However, there are promising products like Claude Subagents and Zed CLI CRDTs (Conflict free Replicated Data Types).

Another limitation is the human ability to keep up with multiple agents' work. That said, it feels like more parallel autonomous agents are getting closer, and I am looking forward to seeing more of this soon.

A large refactor cut the codebase from more than 20k LOC to less than 5k LOC; repo wide renaming required multiple assistive passes.

## What's next

I will keep iterating on `igloo-mcp` to continue learning how to build strong MCP tools and what does and does not work in practice for different workflows. For instance, I am doing heavy quantitative research and I am exploring a cache for the `execute_query` tool and richer query history features (per‑project grouping, rotation, and search) on top of the current JSONL history.

The other angle is that I find it useful to hand pick issues by defining the problem and desired result, then have the LLM write a more in depth issue and eventually fix it and open a PR. As a result, I spend more time as a product manager and power user of my own work while delegating more boilerplate aspects of development to different agents in the background.
