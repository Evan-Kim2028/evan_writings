---
title: "Streaming Embedded OLAP Data Pipeline with LanceDB + DuckDB in Python"
date: "2024-05-01"
collection: data
tags:
  - writing
  - data
  - paragraph
source_url: https://paragraph.xyz/@evandekim/streaming-embedded-olap-data-pipeline-with-lancedb-duckdb-in-python
source_platform: paragraph
slug: streaming-embedded-olap-data-pipeline-with-lancedb-duckdb-in-python
---

## Intro

This post goes over a simple solution to create an embedded streaming OLAP data pipeline that leverages historical blockchain data from [Hypersync](https://github.com/enviodev/hypersync-client-python) and mutable columnar storage format [Lance](https://lancedb.github.io/lance/). Using the new python package [lancedb-tables](https://pypi.org/project/lancedb-tables/0.1.1/), it is easy to create LanceDB tables, update without complex file management systems, and stream real time data. 

## Python Data Ecosystem

Python has been experiencing massive leaps and bounds in open source data standards via the Apache Arrow standard. Apache Arrow plays a significant role in standardizing the Python data ecosystem by providing a unified, language-agnostic columnar memory format for data. This standardization is crucial for several reasons:

* System Interoperability: Arrow's language-agnostic format enhances data exchange across diverse systems and languages, minimizing serialization costs between different data processing tools. For example, Arrow enables seamless transition between dataframe and SQL apis.
* Community and Ecosystem Growth: Wide adoption across languages fosters a robust developer community, driving continuous enhancements in Arrow and its libraries.
* Future-Proofing Data Engineering: Arrow standardizes data formats and processing methods, supporting large-scale analytics and future data engineering innovations in Python.

Apache Arrow makes it possible to have seamless integration between LanceDB, DuckDB, and Polars.

## Data Pipeline Stack

* Hypersync - Query historical blockchain data
* LanceDB - write data to a LanceDB table
* DuckDB - OLAP Queries on the LanceDB table

### Hypersync

Envio is a real-time indexing solution specifically designed for EVM-compatible blockchains. It provides developers with Hypersync, a more efficient way to sync and aggregate blockchain data compared to JSON-RPC, offering up to 20-100x faster syncing on historical data as a result.

The following example utilizes the `lancedb-tables` package to sync a sample of 50,000 blocks from Hypersync to a local LanceDB table. Example code and instructions can be found in [this repository](https://github.com/Evan-Kim2028/hypersync_lancedb). The Hypersync client is used to query blocks and transactions from blocks 19,825,000 to 19,850,000. Then running the back fill table example will then back fill the LanceDB table from blocks 19,800,000 to 19,825,000.

Polars is used as an analytical preprocessing API of choice to perform a bit of data cleaning before writing data into the LanceDB table.

### LanceDB

LanceDB contains a powerful writer that makes it very simple to read and write new Lance datasets. The key reason is that LanceDB decouples read and write operations. This is by design as all LanceDB files are read-only. New data writing operations create new fragments without affecting existing data, allowing for independent operation of read and write nodes in a distributed environment. 

This design ensures that read operations on current data remain unaffected by concurrent writes. This makes the Lance format behave as a **mutable** columnar storage format. In contrast, parquet is a **immutable** columnar storage format and requires additional overhead and code complexity to manage streaming data.

### DuckDB

The example notebook `analytics.ipynb` is an easy example that shows how easy it is to add OLAP functionality by using DuckDB on top of a LanceDB table. Notably using DuckDB to count the number of unique blocks is much faster than Polars, on a magnitude of about 10x.

### Conclusion

This was a short example of how to leverage a modern data engineering stack to build a local embedded OLAP streaming data pipeline with ease in a local environment. Follow up writings will show how to save this pipeline in a cloud environment and add more data sources.
