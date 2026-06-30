---
title: "Censorship, Latency, and Preconfirmations in the Blob Market"
date: "2024-02-01"
collection: mev
tags:
  - writing
  - mev
  - mirror
source_url: https://mirror.xyz/preconf.eth/cxUO8pPBfqnqAlzFUzoEUa6sgnr68DRmsNhBWPb2u-c
source_platform: mirror
slug: censorship-latency-and-preconfirmations-in-the-blob-market
---

`🙏 Special thanks to @terencechain for reviewing, @BertKellerman for his insights,and @ethpandaops for holesky data.`

## TL;DR

* Our research dives into the emerging EIP-4844 blob market, which operates similarly to EIP-1559 gas pricing but lacks a direct block builder tipping mechanism for blob inclusion, potentially resulting in an unreliable blob tx experience and inclusion challenges.
* We note that while blob transactions are large (~125 kB) and cheaper than equivalent calldata, they add significant size to Ethereum blocks but bring incremental bidding power for a block.
* We demonstrate that this new market’s capacity absorbs current rollup data needs and reduces standard blockspace gas costs by 15-20%, unlocking lower-cost mev opportunities.
* We observe that blob transactions risk slowing block propagation by orders of a hundred milliseconds in times of increased network activity, which may lead to block builders censoring blobs to maintain competitive bidding in mev-boost.
* We assess that a “preconf bid” can alleviate these challenges and blob preconfs can enhance EIP-4844’s capabilities, offering enhanced transaction experiences for L2 users and a stable inclusion experience for rollups.
* We will be experimenting on the Holesky testnet, collecting block builder data, and setting up relays as blob preconf providers using mev-commit, and we invite PBS actors to participate.

# Introduction

EIP-4844 expands the data availability capabilities of Ethereum with the introduction of a blob market. This nascent market uses a similar EIP-1559 gas price mechanism to price and burn blob base gas fees. However, unlike type2 transactions, there is no direct way to bid for a builder tip for inclusion in the blob market. The lack of a priority fee makes it difficult to price blob inclusion accurately. Additionally, blob containing blocks are expected to propagate more slowly through the network due to blobs being some of the largest Ethereum transactions in size. If builders accept many blobs in a block, they currently face heightened block reorg risk, and an economically rational builder would opt to censor blobs at times to keep block building latency low, likely correlating with mev spikes.

We put forward a blob-related block building and mev-boost data collection effort, along with a blob preconfirmation provider experiment using [mev-commit](https://docs.primev.xyz), and invite the community of rollups, relays, block builders, and proposers for participation. Our insights on blob related behavior in EIP-4844 suggest that L1 blob preconfirmations can enhance the blob market’s capabilities to provide a better transaction experience for L2 users, reliable inclusion for rollups under emerging mev conditions, and a more stable rollup centric future for Ethereum.

# Understanding the Blob Market

### Blob Transactions

[EIP-4844](https://eips.ethereum.org/EIPS/eip-4844#blob-transaction) introduces a type3 transaction(tx) called a blob tx. A blob-carrying tx is like a regular transaction, but enhanced with blob data, KZG commitments, and proofs. Blobs are extremely large (~125 kB) compared to standard Ethereum txs, and are much cheaper than an equivalent amount of calldata. Whereas calldata is priced at 16 gas per non-zero byte and can have variable size, blob data is priced at 1.04 gas per byte and has a fixed size of [131,072 gas](https://eips.ethereum.org/EIPS/eip-4844).

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/8d45ecb14bdd018c9ffe141576d4de0225f86005838bb601d864ecb6a6f8ccd4.png)

### **Blob Gas Mechanics**

[Blob base gas pricing](https://eips.ethereum.org/EIPS/eip-4844#gas-accounting) has a congestion fee mechanism similar to EIP-1559. The primary difference is that the blob gas is a target blob count, whereas EIP-1559 is based on target gas utilization. The target blob count is 3 (0.375 MB), and the maximum is 6 (0.75 MB) per block. The minimum blob base gas is set at 1 *wei*.

When a blob transaction is submitted, the sender will submit a `max_fee_per_blob_gas` as the highest price they are willing to pay for the base blob gas fee, all of which gets burned. The `max_fee_per_blob_gas` is similar to `max_fee_per_gas` in type0 and type2 transactions. If the user wanted to submit an additional fee to incentivize inclusion, then they would also submit a `max_priority_fee`. However, the `max_priority_fee` only covers the non-blob gas portion of the transaction. This leaves no direct way to submit an inclusion tip to the builder.

### Blob Market Capacity

In this section, we [perform a backtest](https://github.com/Evan-Kim2028/ethereum_block_explorer/tree/master/panel) on historical rollup activity from January 2023 to January 2024 to demonstrate the capacity of the blob market. We focus on txs from the most active rollups on Ethereum and use the historical data to simulate a live blob market. While this market is actively growing and not on mainnet yet, [we use historical data](https://github.com/Evan-Kim2028/ethereum_block_explorer/tree/master/panel) from the whole year of 2023 to simulate its potential.

Based on historical rollup calldata activity used on type3 tx blockspace, we see that the blob market price can comfortably absorb all of the rollup capacity without moving the blob market price past minimum blob base gas.

![base blob gas per block](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/2b832cc319197d6acf8b2b126325481176e2c5c36e950d9f807d5e9d534475a9.png)

base blob gas per block

Although rollups are posting more data to Ethereum, the majority of blocks are still below target, which ensures that the blob gas price stays low.

![The lighter color indicates a higher number of times a block would be built with a certain number of blobs included.](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/383f207a08ea6b6c6513b94745290c8509471567e25ba59eeb18755f89fdc516.png)

The lighter color indicates a higher number of times a block would be built with a certain number of blobs included.

`💡 The implications are that as well as the cost of calldata will be lower in the blob market (factor of 16), the gas price will also be much cheaper (wei vs gwei) which translates in two layers of additional cost savings for rollups.`

Not only can the blob market comfortably absorb current rollup data availability needs, it also frees up blockspace in the non-blob market, reducing gas costs upwards of 15-20%. Reducing gas costs proportionally increases the bidding capabilities for users/searchers, builders, and validators, and unlocks new mev opportunities that were priced out prior to EIP 4844.

![EIP 4844 effect on standard blockspace using 2023 data.](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/1a265cd52fbe9c05fb15467fc4ff31f8e3e5de8eedc280dacbbc89b090341951.png)

EIP 4844 effect on standard blockspace using 2023 data.

### Rollups Demand More Data Availability

Rollups have a major influence on how much gas is used in blocks, and they are the largest class of gas users of Ethereum blockspace today. In 2023, rollups have stored record amounts of transaction data on Ethereum, as we depict below:

![Calldata saved on Ethereum is at all-time highs.](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/dc93a428c5f35f67f0b743412985f9a1e280c136c77e49725d8d8ee70062b530.png)

Calldata saved on Ethereum is at all-time highs.

Daily average charts below show that rollups are starting to take upwards of 15% of every block they are in, directly affecting the price for other users.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/1feac32af50bfaa922455bd4a641ea0e2e1eb49697ad333ea0bbd0eb414cdf97.png)

This can be further exacerbated in black swan demand situations. [Recently in December 2023, inscription spam took the Arbitrum sequencer offline](https://dedaub.com/blog/arbitrum-sequencer-outage) for about an hour due to the overwhelming amount of transactions. As the Arbitrum sequencer resumed operations and started to post the backlog of saved states, the sequencer monopolized blockspace, causing [gas prices to spike above 140 gwei and consuming upwards of 90% of gas](https://twitter.com/EvanDeKim/status/1736150655226540457) in entire blocks, making the network unusable for the majority of users for a period of several hours.

In the next section, we unfold how timing games and censorship are likely to affect this market even in the absence of such spikes in demand.

## Blob Market Challenges: Censorship

### Blob Propagation

EIP-4844 increases the bandwidth requirements per beacon block by a maximum of ~0.75 MB, 42m gas to accommodate an additional up to 6 blobs into each beacon block. Unlike calldata, which is stored forever, blobs are persisted in beacon nodes for a short period of time (18 days as of Feb 2024) to keep the growth of the network archive state manageable.

Moreover, blob transactions have two network representations - to the block builder as a blob tx and to the validator as a blob sidecar. The blob sidecar exists for [forward-compatibility](https://eips.ethereum.org/EIPS/eip-4844#consensus-layer-validation) purposes.

Blobs first must propagate through the execution layer before passing through the consensus layer. **This means that the builders, not validators have the final say on** **[blob inclusion](https://ethresear.ch/t/validator-timing-game-post-eip4844/18129/3?u=murat)****.** Proposers are only able to exclude blob transactions based on commitment or proof invalidity under mev-boost dynamics.

![Execution verification happens by builders. Consensus verification happens by validators.](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/10b9cac569c3e00bfdea12cfb09c796aff4947c946a61bfd4e0005ce0fe34152.png)

Execution verification happens by builders. Consensus verification happens by validators.

### The Block Builder Perspective

Recent research [on validator timing games](https://arxiv.org/pdf/2312.09654.pdf) highlights that latency optimization can strategically benefit node operators to maximize profits by delaying block proposals. The authors explain that this is detrimental to the chain health. Blob transactions further complicate the timing games by adding a variable amount of latency when the blob [sidecar propagates](https://ethresear.ch/t/validator-timing-game-post-eip4844/18129).

Blob transactions are equivalent to the largest possible transaction sizes. As a result, blocks containing these transactions can propagate more slowly, making block builders [less competitive at winning mev-boost bids](https://arxiv.org/pdf/2311.09083.pdf). As a result, this incentivizes block builders to censor blobs temporarily or even indefinitely so that they can submit mev bids with [higher frequency](https://twitter.com/specialmech/status/1714748986492699115).

The [ethpanda](https://twitter.com/ethpandaops) team has been conducting real-world latency tests on the testnets using [Xatu](https://notes.ethereum.org/@ethpandaops/xatu-overview). Sentries are placed in NYC, FRA, BLR, and SYD regions to represent real latency measures using consensus clients Prysm, Nimbus, Lodestar, and Lighthouse. A data snapshot with Holesky blob data on Feb, 20 2024 indicates a non-trivial amount of latency is incurred throughout the mev pipeline.

After the block builder wins the mev-boost bid auction, the proposer must wait for the blob sidecars to propagate before being able to verify the blobs included in the block. The below table shows that the minimum time for a single blob sidecar to propagate is ~400ms over a sample size of ~800 blob sidecars.

**Table 1. Blob propagation vs number of blobs for slot**

![Small data size contributes to some of the counterintuitive observations depicted in this dataset](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/ab31a80450bf2a35a384d834f3607f541c9ff7df67375e507e95d857cb11c536.png)

Small data size contributes to some of the counterintuitive observations depicted in this dataset

The next table shows the latency variances on waiting for more blob sidecars to arrive. The 50th percentile (p50) indicates that the latency variance between a 2 blob block and 6 blob block is ~225ms.

**Table 2. Time difference between the first and last blob sidecar grouped by the total number of blob sidecars in the block**

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/7321fe2f43d6c52fe2c790187abfc9e9df594d583621dd024d386f9394ff9d73.png)

This blob propagation latency puts additional block reorg risk on block builders as they fill their blocks up with blobs, for little economic gain. The builder might opt to exclude/censor the blob transaction to avoid a potential reorg. **If a block contains a lot of mev, economically rational builders would need to be compensated appropriately by rollups for this risk.**

### On Blob Market Inclusion Bidding UX

The [validator timing games research](https://arxiv.org/pdf/2312.09654.pdf) points out that bigger bids are correlated with larger size blocks later in the mev-boost bidding process. As the bids and gas price rise, a larger share of ETH is burned in subsequent slots. If the base fee increases while mev extraction remains constant, builders have less to bid toward a proposer’s future income.

In the expected blob market where capacity exceeds current demand, the blob base fee that gets burned will remain very small, in the tens or hundreds of wei. It becomes essential for rollups to recognize that their blob transactions might not get included despite paying the sufficient base fee. The low base fee blob market implies that the blobs will need to bid many multiples higher to incentivize builders to include the transactions. In such cases, the blob transaction will have to be resubmitted with an increased fee, resulting in a poor UX.

Additionally, since the initial blob market under EIP-4844 will not have an inclusion tipping mechanism (e.g., a blob priority gas fee), this further exacerbates the UX issue because the rollup cannot bid directly on the blob transaction.

We look at an example transaction and calculate the equivalent blob cost assuming a 10 wei base blob gas. Note that this example assumes there is an effective inclusion bidding mechanism in place to be able to bid on blobspace in the first place.

💡[Here is a sample transaction](https://etherscan.io/tx/0x757203267709f0f6a8175af063337307ecaafc41aa83db1198f29108b835519e):

```
Calldata - 129,998 bytes (129429 nonzero bytes) ~ 2,094,140 gas used at 10.56 gwei (10.55 gwei base price + .01 gwei Priority Fee) = .022 ETH 

Blob - 128,000 bytes ~ 131,072 gas used at 1 gwei (10 wei base price + .99999999 gwei priority fee) = 0.000131072 ETH
```

**The calculation concludes that if rollups use the blob market, they can submit a potentially 100x larger bid due to the lower blob base fee while still saving over 150x the cost.** The lower blob `baseFee` will allow rollups to offer more competitive inclusion bids while still saving on costs. The inclusion fee will need to be as competitive with existing mev opportunities in the block to compensate the potential builder reorg risk, and thus even bidding 100x higher may not be enough. That is, in the absence of blob preconfirmations.

## Blob Preconfirmations with mev-commit

Under such timing games, the primary role of a blob preconfirmation becomes to make a list of blobs that a provider preconfirmed *available across the mev pipeline*. On mev-commit, each preconf provider issues their own commitments to txs. The provider can then give access to this data to others (e.g. block builders, relays, sequencers). The data availability of the preconf list to other actors across the mev pipeline allows the matching execution payload to be sent in parallel by a block builder. This notion can be leveraged to create preconf’d blob inclusion lists, or have the type3 blockspace be collaboratively built by a relay.

With the advanced knowledge of preconfirmed blobs, block builders can start building future blocks with blobs before their slot begins. This creates a pricing basis and lays the foundation for a robust futures market that gives rollups more reliable inclusion and blockspace price stability. Additionally, mev-commit preconf bids give rollups a more reliable price discovery mechanism because rollups can update their preconf bids in real time without resubmitting the entire blob tx.

Finally, bundling blobs and using a preconf bid allows rollups to build alliances. Preconf bids can be applied to bundles of blob txs or aggregated blobs, allowing rollups to share their bidding power and inclusion with other rollups, helping stabilize and grow the Ethereum blob market.

### Conclusion

All in all, we show that economics for rollups are getting better, while a new market emerges with additional considerations ranging from timing games to lacking a tipping mechanism. While it is too early to jump to the solution phase for the issues we highlight, we can easily experiment on this with PBS actors since mev-commit is active on Holesky testnet. Primev will be collecting data on blob effects on block building and proposer latency, and hope to surface insights about potential behavioral patterns.

While economics and UX are primary drivers to preconf type2 transactions; it looks like inclusion, reliability, and stability of the rollup and the rollup centric ecosystem will become important reasons to preconf blobs under EIP-4844. We will also be experimenting with a blob preconfing relay that can leverage blob preconfs and block builder coordination to improve blob sidecar latency propagation on Holesky testnet. We invite the community to reach out and participate in this experiment as it will inform a potential solution for the whole community.
