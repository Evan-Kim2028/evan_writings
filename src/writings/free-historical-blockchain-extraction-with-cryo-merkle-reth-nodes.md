---
title: "Free Historical Blockchain Extraction with Cryo + Merkle Reth Nodes"
date: "2023-11-01"
collection: data
tags:
  - writing
  - data
  - mirror
source_url: https://mirror.xyz/0x70b0451b1C047ed750C4661B4624B67FD94A31c5/86O5gGvnrm3q_J2ZCAkZZL0o9ernHSGVMvoX564hzlA
source_platform: mirror
slug: free-historical-blockchain-extraction-with-cryo-merkle-reth-nodes
---

### **Introduction**

Historical blockchain data poses challenges for analysis. Despite its general accessibility, obtaining and analyzing such data has been historically hindered by paywalls and restrictions imposed by node service providers. Setting up a personal archive node is also a non-trivial task, introducing extra steps before data analysis becomes feasible.

By leveraging [Cryo to extract historical data](https://github.com/paradigmxyz/cryo) and utilizing the [free Merkle RPC with archive node support](https://freerpc.merkle.io/), researchers can now easily access Ethereum historical data at no cost. This breakthrough provides quantitative researchers with production-grade access, allowing more time for data exploration and less time spent on building data pipelines.

## [Cryo](https://github.com/paradigmxyz/cryo)

Cryo, a recent addition to data extraction tools, was announced in [July 2023](https://twitter.com/notnotstorm/status/1687517038305308672). It employs [ethers.rs](https://github.com/gakonst/ethers-rs) for JSON-RPC requests, making it compatible with various chains, including Ethereum, Optimism, Arbitrum, Polygon, BNB, and Avalanche. Since Cryo is built in rust, querying data is [embarassingly parallel](https://en.wikipedia.org/wiki/Embarrassingly_parallel). This actually makes Cryo so fast that by default, it will be too fast to use with most node providers.

When extracting data from a historical node, a common challenge involves preprocessing raw blockchain data to make it human-usable. Cryo takes care of this and standardizes the dataset across a wide variety of datasets. y default, data is saved into Apache's free, universal, and open-source column-oriented storage format—parquet files. These files use the `lz4` compression method by default (modifiable with the `--compression` syntax).

Some example datasets that are available in Cryo already:

* balance\_diffs
* balances
* blocks
* erc20\_balances
* erc20\_supplies
* erc20\_transfers
* erc721\_transfers
* eth\_calls
* geth\_calls
* geth\_code\_diffs
* geth\_balance\_diffs
* geth\_opcodes
* logs (alias = events)
* native\_transfers
* slots (alias = storages)
* storage\_diffs (alias = slot\_diffs)
* storage\_reads (alias = slot\_reads)
* traces
* trace\_calls
* transactions (alias = txs)

Cryo is user-friendly, accessible through the CLI or Python bindings, significantly simplifying the process of extracting and curating historical data for research. The [Cryo GitHub readme](https://github.com/paradigmxyz/cryo) provides a set of starter commands. Additionally, Cryo is [idempotent](https://www.fivetran.com/blog/what-is-idempotence), enabling researchers to resume interrupted pipelines without duplicating queried data.

### [Merkle RPC](https://freerpc.merkle.io/)

Cryo's efficiency is limited by rate limits and throttling from various node endpoints or personal node hardware. Merkle addresses this bottleneck by offering a [free RPC with no throttling and unlimited requests](https://blog.merkle.io/blog/improving-reth). [The endpoint can be found here](https://freerpc.merkle.io/). How is this possible?

Merkle is a private mempool provider and operates a group of RETH nodes, allowing them to save ~$250,000 annually on expenses ([source](https://blog.merkle.io/blog/building-a-eth-load-balancer)) and [improve performance](https://www.paradigm.xyz/2022/12/reth) compared to other mempool services like Kolibrio and Bloxroute. Of equal importance, their cloud provider, OVH, grants them **unlimited outgoing/incoming bandwidth** so don’t feel guilty using the node!

While Cryo currently supports BSC and Polygon, Reth does not. However, Merkle plans to offer similar public endpoints for BSC and Polygon once they support them.

### Short Example

Here is an example of how I am using Cryo CLI to build a dataset with blocks, transactions, and intra-block balance changes. Two lines of code downloads ~50gb of historical data for the month of September. The limiting factor was my internet speed! The pipeline is largely self managed because of the idempotent nature of Cryo so the only thing I needed to do was create a data folder, Cryo takes care of the subfolder management with `--subdirs datatype`

```
`cryo blocks_and_transactions -b 18039828:18251969 -o /home/evan/Documents/blockspace/data/cryo_september/ --rpc "https://eth.merkle.io" --subdirs datatype --hex`

`cryo balance_diffs -b 18039828:18251969 -o /home/evan/Documents/blockspace/data/cryo_september/ --rpc "https://eth.merkle.io" --subdirs datatype --hex`
```
