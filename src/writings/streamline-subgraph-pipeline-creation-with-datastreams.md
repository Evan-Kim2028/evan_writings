---
title: "Streamline Subgraph Pipeline Creation With DataStreams"
date: "2023-01-01"
collection: data
tags:
  - writing
  - data
  - mirror
source_url: https://mirror.xyz/0x70b0451b1C047ed750C4661B4624B67FD94A31c5/P-ZBadPVJLENgsLKoxgA9nPGchVARK9QoD0EfaNQeh8
source_platform: mirror
slug: streamline-subgraph-pipeline-creation-with-datastreams
---

[DataStreams](https://github.com/Evan-Kim2028/DataStreams) a Subgraph query utility package that allows users to execute complex Subgraph queries. It provides extended functionality on top of The Graph data access python package [Subgrounds](https://github.com/Protean-Labs/subgrounds). The main benefit is that now anyone can query Subgraph data, save it to their local storage as csv files, and perform data analytics immediately. DataStreams creates a reproducible data pipeline creation process in a transparent, lightweight manner. No database needed!

The main package in DataStreams is the `Streamer` class. `Streamer` streamlines the Subgraph query process in Python, exposing key information such as the queryable Subgraph schemas and filter clauses. In v1.0.0, functionality includes:

* DRY Subgraph Query Code - reuse code to reduce complexity of Subgraph queries
* Parallelized Subgraph Queries - Leverage the standard Python package `concurrent` to unlock concurrency at the Subgraph query level

### Example #1 - Access Historical Chainlink Node Data

Query the Chainlink Subgraph node for multiple token prices over a customized ranged period. [Example notebook found here](https://github.com/Evan-Kim2028/DataStreams/blob/master/examples/chainlink_historical_price.ipynb)

### Example #2 - Parallelized Multi Schema Query

Query the Cowswap Subgraph node for four specific schemas with parallelization support. [Example notebook found here](https://github.com/Evan-Kim2028/DataStreams/blob/master/examples/cowswap_schemas.ipynb)
