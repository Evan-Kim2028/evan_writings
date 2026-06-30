---
title: "Fetching Uniswap Historical Swap Data With Python and Subgrounds"
date: "2023-11-01"
collection: data
tags:
  - writing
  - data
  - mirror
source_url: https://mirror.xyz/0x70b0451b1C047ed750C4661B4624B67FD94A31c5/-gq99zeoHqQxc1ViSJV4135u2ZgaH8v6q_WacrPECSA
source_platform: mirror
slug: fetching-uniswap-historical-swap-data-with-python-and-subgrounds
---

## Introduction

Subgraphs provide a highly curated source of data that can be used for historical data analytics compared to archive nodes. While historically used primarily to power frontend dashboards with recent data, subgraphs are similar to archive nodes because they contain all historical data for a protocols set of contracts.

We query historical Uniswap swap data from two subgraphs on [The Graphs decentralized network](https://thegraph.com/explorer) with [Subgrounds](https://github.com/0xPlaygrounds/subgrounds):

* [streamingfast univ3](https://thegraph.com/explorer/subgraphs/HUZDsRpEVP2AvzDCyzDHtdc64dyDxx8FQjzsmqSg4H3B?view=Playground&chain=arbitrum-one)
* [univ2](https://thegraph.com/explorer/subgraphs/A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum?view=Overview&chain=arbitrum-one)

Use these links to find a list of available query fields and schemas.

[This example repository](https://github.com/Evan-Kim2028/uniswap_subgraph_downloader) provides example scripts to get started. The repository wraps additional functionality to:

* control the query date range
* pre-defined query fields for a complete swaps dataset
* asynchronous query per day
* idempotent local data storage

Currently playgrounds gives 5000 free query credits to start with when signing up for their API key. Each query credit is equivalent to 1000 rows queried. You can sign up for an [API key here](https://docs.playgrounds.network/api/key/).

# Data Exploration with Polars

The pre-defined query fields contain the following columns with respective types. These schemas are defined using polars types, which leverages the [apache arrow columnar data format](https://en.wikipedia.org/wiki/Apache_Arrow).

```
univ3_schema = {
    '': pl.Int64,
    'protocol': pl.Utf8,
    'swaps_timestamp': pl.Int64,
    'swaps_transaction_id': pl.Utf8,
    'swaps_transaction_blockNumber': pl.Int64,
    'swaps_transaction_timestamp': pl.Int64,
    'swaps_transaction_gasPrice': pl.Float64,
    'swaps_transaction_gasUsed': pl.Int64,
    'swaps_logIndex': pl.Int64,
    'swaps_sqrtPriceX96': pl.Float64,
    'swaps_pool_id': pl.Utf8,
    'swaps_pool_feeTier': pl.Int64,
    'swaps_pool_liquidity': pl.Float64,
    'swaps_pool_token0Price': pl.Float64,
    'swaps_pool_token1Price': pl.Float64,
    'swaps_recipient': pl.Utf8,
    'swaps_sender': pl.Utf8,
    'swaps_origin': pl.Utf8,
    'swaps_amount0': pl.Float64,
    'swaps_amount1': pl.Float64,
    'swaps_token0_name': pl.Utf8,
    'swaps_token0_decimals': pl.Int64,
    'swaps_token0_symbol': pl.Utf8,
    'swaps_token1_name': pl.Utf8,
    'swaps_token1_decimals': pl.Int64,
    'swaps_token1_symbol': pl.Utf8,
}
```

```
univ2_schema = {
    '': pl.Int64,
    'protocol': pl.Utf8,
    'swaps_transaction_id': pl.Utf8,
    'swaps_transaction_blockNumber': pl.Int64,
    'swaps_transaction_timestamp': pl.Int64,
    'swaps_logIndex': pl.Int64,
    'swaps_amount0In': pl.Float64,
    'swaps_amount0Out': pl.Float64,
    'swaps_amount1In': pl.Float64,
    'swaps_amount1Out': pl.Float64,
    'swaps_amountUSD': pl.Float64,
    'swaps_from': pl.Utf8,
    'swaps_id': pl.Utf8,
    'swaps_sender': pl.Utf8,
    'swaps_to': pl.Utf8,
    'swaps_pair_id': pl.Utf8,
    'swaps_pair_reserve0': pl.Float64,
    'swaps_pair_reserve1': pl.Float64,
    'swaps_pair_token0_decimals': pl.Int64,
    'swaps_pair_token0_id': pl.Utf8,
    'swaps_pair_token0_name': pl.Utf8,
    'swaps_pair_token0_symbol': pl.Utf8,
    'swaps_pair_token1_decimals': pl.Int64,
    'swaps_pair_token1_id': pl.Utf8,
    'swaps_pair_token1_name': pl.Utf8,
    'swaps_pair_token1_symbol': pl.Utf8,
}
```

The notebook in the repository demonstrates some basic joins and charts to get started analyzing data between the two protocols. Note the query size is set at `2,500` so there are only `17,500` rows for each protocol in the sample data.

The main benefit from using subgraphs for historical analysis is that the data is already nicely curated. To concat the dataframes together, only the column names need to be standardized. Below shows an example of the nicely curated dataset.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/456d02a7c15bd68afe3b2f86244cff01ba9c9c83b70071357f9a154c39025c76.png)

From this dataset, a simple scatterplot is made to show the number of swaps in a pool and the total volume from those number of swaps. Each dot represents a unique pool.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/82390ed21ca9b84b26adcc1f4626be9ca9cdae3ffab9e4c4ba70675a88a101e2.png)

# Limitations and Conclusion

The main benefit from querying a subgraph for historical data is access to a curated dataset, full of information. In contrast with an archive node, schemas and metadata (such as USD volume and token data) must be written from scratch.

While subgraphs provide an easy means to access curated datasets with minimal effort, they come with limitations. The decentralized graph network is currently undergoing growth challenges, and the technology stack is not fully matured. Query performance depends on the indexers, and optimizing their stacks and establishing sustainable businesses around the decentralized network is an ongoing process.
