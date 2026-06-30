---
title: "MEV Arbitrage on Olympus"
date: "2022-10-01"
collection: mev
tags:
  - writing
  - mev
  - mirror
source_url: https://mirror.xyz/evandekim.eth/Mc11J16dVP7Ervk1r2Sx_wkJ7dzb7Ce60Y2EpbRBlHY
source_platform: mirror
slug: mev-arbitrage-on-olympus
---

```
1 - Abstract
2 - Intro
  2a - MEV Arbitrage
  2b - Olympus POL
3 - Data Collection
  3a - Sushiswap LP
  3b - Olympus POL
4 - Results
  4a - Swap Distributions
  4b - Swap Statistics
  4c - Buy/Sell Trading Flows
5 - Final Remarks
```

# 1 - Abstract

Maximal extractable value (MEV) bots perform atomic arbitrage transactions on DEX-based liquidity pools. Although accounting for less than 1% of total unique addresses,  these bots execute the majority of transactions in Olympus protocol owned liquidity (POL) both in transaction size and trading volume. This handful of bot addresses creates greater capital efficiency by increasing liquidity utilization and contributes most of the POL fees. Atomic arbitrage bots are also more motivated to execute higher valued swaps to allow OHM price to reflect the true market price. This behavior also extends to the OHM-BTRFLY liquidity pair, where MEV bots contribute the majority of trading volume (90%+) and liquidity utilization to the pool.

# 2 - Intro

MEV broadly describes the activity of bots on the blockchain. Critical DeFi mechanisms such as arbitrage and liquidations are driven almost entirely by bot activity. This research presents the first data-driven research to analyze MEV activity and behavior across OHM liquidity pools. A data pipeline, created by the [Subgrounds python library](https://github.com/Protean-Labs/subgrounds) and Flashbots data via Dune, collects on-chain data for further analysis. Data observations emphasize the difference between humans and MEV arbitrage bots. This handful of bots contributes significantly to volume and liquidity utilization, resulting in greater capital efficiency for Olympus POL.

### 2a - MEV Arbitrage

In most decentralized exchange (DEX) liquidity pools (LPs), there are three categories of trading:

1. Human Trading
2. DEX-DEX Arbitrage (atomic)
3. CEX-DEX Arbitrage (toxic)

Atomic arbitrage is positive for LPs because they rely on the atomic arbitrageurs to rebalance the LP portfolio of assets in the pool actively. The existence of atomic arbitrage is also a [healthy sign of market efficiency](https://arxiv.org/abs/1911.03380), explicitly quantifying the [no-arbitrage bounds](https://en.wikipedia.org/wiki/No-arbitrage_bounds). The no-arbitrage bound property in financial markets is required to prove a true market price equilibrium. Atomic arbitrage bots are rational market actors because they look for profitable opportunities to close arbitrage gaps. They are not motivated by macroeconomic conditions or irrational behavior like humans. The primary motivations of an arbitrage bot are related to execution costs. The arbitrage will not occur if swap fees and gas costs exceed profit. Arbitrage failure can lead to stale market prices during periods of little volatility when the transaction expenses exceed the profit spread.

On the other hand, [toxic arbitrage is detrimental to LPs](https://insights.deribit.com/market-research/toxic-flow-its-sources-and-counter-strategies/). The toxic arbitrageur makes decisions with an asymmetrical information advantage from a centralized exchange (CEX). In atomic arbitrage, there is no information asymmetry between traders and LPs, given the deterministic nature of the blockchain. Information asymmetry occurs because CEXs can read information from the blockchain. However, the blockchain can’t read information from CEXs. This information asymmetry gives an unfair advantage to toxic arbitrageurs. It lets them make trades in a zero-sum game against the LP by giving them suboptimal transactions to execute. The latter has no choice but to accept the toxic trade flow because of the permissionless nature of the blockchain.

### 2b - Olympus POL

Any token with liquidity on a CEX suffers from the toxic arbitrage problem. Olympus POL is unique because all of OHM’s liquidity is entirely on-chain. There are not sufficient sources of liquidity to conduct toxic arbitrage between a DEX and CEX, which makes OHM liquidity pools the true market reference price for the token. This is critical for Olympus Bonds because the price of bonds rely on the OHM market price. An OHM token price that reflects the market demand price accurately creates more efficiencies between POL and bonds. Conversely, a stale OHM price poorly reflects the market and creates more inefficiencies that can be exploited by recycling bonds into POL and vice versa with inverse bonds.

The only types of OHM traders are humans and atomic arbitrage MEV bots. OHM token pairs offer natural protection against toxic arbitrage flow, further strengthening the Olympus POL case.

During this DeFi bear market phase which has seen on-chain activity slow significantly, MEV bots continue to utilize Olympus POL liquidity for atomic arbitrage. These bots arguably play a more critical role in POL during this market phase because they are indifferent to bear markets. Bots offer a consistent, stable user base for Olympus POL.

# 3 - Data Collection

### 3a - Sushiswap LP

Ethereum on-chain data is accessed from the Sushiswap subgraph and queried in python using [subgrounds](https://github.com/Protean-Labs/subgrounds), the python library created by the Playgrounds team. Swap data for OHM v1 and OHM v2 is collected and aggregated, creating a homogeneous dataset consisting of 473k swaps and $12b of trading volume over 18 months from March 2021 to September 2022. **The python scripts, analysis, and datasets are all publicly available and can be found** **[here](https://github.com/Evan-Kim2028/ohm_mev_research)****.**

### 3b - Flashbots MEV Arbitrage Addresses

Flashbots MEV arbitrage data is accessed via this [dune query.](https://dune.com/queries/1339253) The arbitrage address list contains many false positive MEV bots such as routing addresses. Addresses that do not have $1,000 in profits and over 50 transactions are filtered out, reducing the list of arbitrage addresses from 3.4k to 550. In contrast, a little more than 87k unique addresses have transacted with Ohm POL. MEV bots are approximately .6% of the entire population of trading addresses.

MEV detection is a non-trivial task. Currently, Flashbots data uses mev-inspect to identify MEV addresses with implementations in [python](https://github.com/flashbots/mev-inspect-py) and [rust](https://github.com/flashbots/mev-inspect-rs). There are also [new projects in progress to improve MEV detection](https://twitter.com/DestinerX/status/1575196912193773568?t=x0ggobzFv_Fi6qf_IEgUPw&s=19). Although there could still be false positives, the address population after filtering looks heuristically more reasonable, as shown below.

![Fig 1 - profits and activity scatter plot of MEV Arbitrage Addresses](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/c4efac4c77c774d699cbfac09ac621fd20a9e2c2f893c59aae2d92384b0fb6ad.png)

Fig 1 - profits and activity scatter plot of MEV Arbitrage Addresses

## 4 - Results

Analysis from the on-chain data shows that MEV bots contribute more significant size swaps than human traders. Although there are more human addresses than MEV addresses, MEV bots contribute most of the trading volume and fees to POL in every liquidity pool. MEV bots are the largest user base of Olympus POL and contribute significantly to overall liquidity utilization. In particular, the OHM-BTRFLY pair enjoys the benefits of MEV trading flows.

The first pair of charts shows swap distributions for trading pairs between bots and humans, showing much distinct activity, particularly in the fourth quartile of data. The second pair of charts characterize trading activity between bots and humans, showing that most trading activity comes from bots. Finally, the third pair of graphs shows trading flows into each trading pair and indicates another divergence in trading behavior between humans and bots.

### 4a - Swap Distributions

The swap distributions are plotted as boxplots to emphasize how different the fourth quartiles of data are. A few outliers were identified in the data, showing large 10m+ swaps, particularly in the OHM-LUSD pool. Further analysis revealed that data from Sushiswap included inaccurate values, vastly inflating the transaction size amount recorded on etherscan. A quartile filter removes these incorrect values of the top .00001% and .0001% transactions from bots and humans, respectively.

Although the median values are relatively small and most swap sizes are small, the fourth quartiles for both bots and humans contain many outliers. Within these outliers, it is clear that the MEV bots are responsible for all the more significant trades, particularly all of the $4m+ size trades in the DAI and ETH pairs.

![Fig 2 - Distribution of the financial size differences between MEV and human swaps](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/41b7f919a0fab5d5148521ce4eceb7815450f6a1eced2ec05148ec04b5a1733a.png)

Fig 2 - Distribution of the financial size differences between MEV and human swaps

### 4b - Swap Statistics

We see below the breakdown in trading activity between bots and humans. Although bots account for less than 1% of the entire trading population, the below histogram charts visually show that the bots contribute upwards of 75% of all swap transactions and volume across all token pairs. Notably, the bots contribute the vast majority of OHM-BTRFLY trading activity and liquidity utilization.

![Fig 3 - Difference in Swap Volume between MEV and humans (CHARTS HAVE DIFFERENT Y-AXIS SCALES)](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/a67ac280a045b2abb02012734c9ba43abc1d8b4e80a812a4f3ae6f78e064bd46.png)

Fig 3 - Difference in Swap Volume between MEV and humans (CHARTS HAVE DIFFERENT Y-AXIS SCALES)

### 4c Buy/Sell Trading Flows

The below charts express the different trading flows of MEV and humans. Within the most significant pools, there seems to be a divergence of behavior between bots and humans. For example, on the DAI pair, MEV bots contributed to higher selling flows within the pool. In comparison, humans contributed to higher buy flows, two contrasting trading behaviors. For the LUSD pair, it is unclear whether heavier selling flows are a pattern related to stablecoins or whether additional data discrepancies need to be adequately accounted for.

![Fig 4 - Trading Flows of bots compared to humans (CHARTS HAVE DIFFERENT Y-AXIS SCALES)](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/129efa1a972e83a58aef0e3dfe1fe515bb26d5369350b80f22ded528907d843c.png)

Fig 4 - Trading Flows of bots compared to humans (CHARTS HAVE DIFFERENT Y-AXIS SCALES)

It is also worth noting that the WETH and BTRFLY pairs had relatively even trading flows for MEV bots. At the same time, humans exhibited higher selling flows for WETH (and maybe BTRFLY too, but this isn’t immediately clear because of the y-axis scale). Due to current data engineering limitations (which requires more blood, sweat, and tears), it is only clear that there are different dynamics between bots and humans. However, further efforts are needed to determine these dynamics' best characterization and implications.

# 5 - Final Remarks

This initial data-driven research sheds light on the different behaviors and motivations of bots and humans. An on-chain data pipeline built with Subgrounds, Flashbots, and Dune provides clear empirical evidence on-chain that bot activity is the largest user base for Olympus POL.

Different research directions include but are not limited to the following:

* Understand the extent that MEV bots also interact with the bonding mechanisms and recycle bonded OHM back into the liquidity pools. What are the bot motivations for bond recycling and what kind of market dynamics does bond recycling lead to?
* Further explicitly quantify bot trading and human behaviors, using pattern recognition to mitigate black swan scenarios via risk management recommendations across all Olympus products.
* Analysis of liquidity conditions that maximize Olympus POL fee revenues (by maximizing bot trading volume)
* Build a more advanced data streaming application that supports dashboards to show bot activity in real-time
