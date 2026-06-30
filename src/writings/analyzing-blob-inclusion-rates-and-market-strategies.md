---
title: "Analyzing Blob Inclusion Rates and Market Strategies"
date: "2024-04-01"
collection: highlights
tags:
  - writing
  - highlights
  - mirror
source_url: https://mirror.xyz/preconf.eth/6lZYL62DR9U14KC7wCC4RHReVdHcBeMy5PKeHVbPq5k
source_platform: mirror
slug: analyzing-blob-inclusion-rates-and-market-strategies
---

`Special thanks to @sui414 for review, @ethpandaops for mempool, beacon chain data, and @envio_indexer for execution layer data.`

### **Abstract**

This article follows up [on our pre EIP-4844 article](https://mirror.xyz/preconf.eth/cxUO8pPBfqnqAlzFUzoEUa6sgnr68DRmsNhBWPb2u-c) with real data and insights from the nascent blob market, focusing on blob posting strategies blob producers such as Optimism and Base are using and providing quantitative analysis for strategy efficiency metrics such as how fast a blob is included in a slot and the priority fee premium paid for that slot inclusion rate.

# Blob Market Utilization

As of April 16th, a month after the Dencun upgrade, about 40% of blocks contain a blob. This number indicates that the market has yet to reach a saturation point, with the average blob fee still at the minimum 1 wei mark due to being below the target of 3 blobs per block average.

![In the last week of March, the runup on the blob base fee briefly flipped the block base fee as a result of blobscriptions briefly pushing the blob market to full capacity.](/assets/images/c5a0557c1a748f917d18b64568db0818f949a8de0dd3eb2d2d2d3a4d64b30a3f.png)

In the last week of March, the runup on the blob base fee briefly flipped the block base fee as a result of blobscriptions briefly pushing the blob market to full capacity.

Currently the upper bound is about 400 blobs posted per hour. The market saturation for the Ethereum data availability is about 900 blobs per hour to meet the 3 blob target, which indicates the market is at about 40% capacity right now.

![The 3 blob target is 900 blobs per hour https://dune.com/hildobby/blobs](/assets/images/ca04691fb55fd857963cd3487319064bd556ae2b59ddc5cfaff786873841583f.png)

The 3 blob target is 900 blobs per hour https://dune.com/hildobby/blobs

[The flashbots blob-block builder dashboard](https://dune.com/flashbots/blob-block-builder-board) provides blob data insights at the builder level. Given that 40% of blocks contain a blob, it’s safe to assume a builder should also have around a 40% inclusion rate for blobs as well.

![https://dune.com/queries/3522584/5923355](/assets/images/58127c2568b771343274379c2107958f2fc04daec0909945ccc52f0129330bc3.png)

https://dune.com/queries/3522584/5923355

Builders representing 20% of total block production currently have lower than expected blob inclusion rates varying from 1% to 16% inclusion rates, indicating potential delayed inclusion by builders due to lack of incentives as predicted in [our pre-EIP 4844 article.](https://mirror.xyz/preconf.eth/cxUO8pPBfqnqAlzFUzoEUa6sgnr68DRmsNhBWPb2u-c)

Among the top 7 builders who make up 96% of Ethereum block production, builders ranked at #3 and #7 by market share (which totals 20%) showed a much lower rate of blob concentration in their blocks. This indicates that they drop blobs transactions when building the block content, due to a lack of economic incentives.

Blocks built by vanilla validators, which we define as a validator that builds its own block locally, have fewer mev opportunities, so there is less precedent of economic competition for inclusion and latency. These validators typically do not run mev-optimized code either. Since these validators build their own blocks, there is no longer [a timing game](https://ethresear.ch/t/validator-timing-game-post-eip4844/18129) from blob propagation latency through relays. Most of the other top builders maintain a similar blob inclusion rate as vanilla validators, showing good intentions for accommodating the blob market. However whether this altruistic strategy holds during times of high mev contention is yet to be seen.

# Optimism and Base Blob Strategy Insights

Currently Optimism and Base use a blob-maximization strategy - posting the maximum of 6 blobs per transaction, practically filling the blobspace for that block with a single type 3 transaction. The advantage to submitting 6 blobs in every transactions is to minimize gas costs. Rather than paying the transaction block base fee 6 times for 6 blobs, the cost is paid only once.

This strategy increases the blob gas by the maximum amount 12.5%, resulting in higher blob gas fees for the next block’s blobs. If a different rollup only posts 1 blob at a time and shares the mempool with the size 6 blob transaction, depending on the blob gas cost, it could be more beneficial for the rollup to try and frontrun the base blob tx and avoid the 12.5% blob fee increase. While the savings amounts would be negligible today due to low blob contention, blob front running could be a viable strategy to save costs in the future if this strategy holds. This also implies that others employing this strategy could potentially be censored indefinitely by single blob blocks submitted by other rollups or inscription users.

Base is currently the largest user of the blob market, followed by Arbitrum and Optimism. Overall, the strategy employed by Optimism and Base accounts for about half of the blob market utilization. We emphasize the market is currently underutilized, so competition between market participants is yet to pick up.

![https://dune.com/queries/3522241/5922814 - 4 hour time period (April 16, 2024)](/assets/images/2a40bab0e278db9bb402e54b598084f0af8aefc8948e4a543f60e0cb8b6b4acb.png)

https://dune.com/queries/3522241/5922814 - 4 hour time period (April 16, 2024)

# Blob Inclusion Analysis

The effectiveness of the blob posting strategy outlined above can be measured by the slot inclusion rate and the EIP-1559 priority fee premium correlation with the slot inclusion rate.

The first measurement is the slot inclusion rate. This indicates the number of slots it took for a blob to be included in the beacon chain, with a higher rate signifying a slower inclusion time. The best slot inclusion rate is 1, indicating inclusion within a single block. However, since blobs traverse the mempool slowly as very large transactions, we consider 2 slots as an acceptable slot inclusion rate target.

The second measurement is to understand the correlation that the EIP-1559 priority fee premium has on faster slot inclusion rates. Ideally a higher priority fee would lead to faster slot inclusion rates.

The live dashboard data for all rollups that have adopted blobs can be [found here](https://blobs.primev.xyz/dashboard). Note the dashboard has not been optimized and takes a bit of time to load. The backend can be found [in this repository](https://github.com/primevprotocol/ethpandaops_python) and the frontend can be found [in this repository](https://github.com/primevprotocol/eip4844_blob_data).

### Slot Inclusion Rates

Despite an underutilized market, Optimism and Base have a fairly slow blob inclusion rate, as seen in the chart below, with frequent spikes above the 2-slot inclusion rate. Initially, it seems counterintuitive that there would be blob inclusion delays in a market that is not operating at capacity.

![Historical Slot Inclusion chart depicting delayed blob inclusion in an underutilized market benchmarked against a 2-slot inclusion rate as a reliable inclusion target.](/assets/images/b1bcad9c15198d7ed321ace0cc21401ad0db0bc66dd7954d6c0e2b12e4b19de7.png)

Historical Slot Inclusion chart depicting delayed blob inclusion in an underutilized market benchmarked against a 2-slot inclusion rate as a reliable inclusion target.

### EIP-1559 Priority Fee Premium Correlation with Slot Inclusion Rates

The Optimism and Base bidding strategy follows [Geth’s spec](https://github.com/ethereum/go-ethereum/blob/66e1a6ef496e001abc7ae7433282251a557deb2c/core/txpool/blobpool/blobpool.go#L132) to double all parameters upon blob resubmission. The chart below shows that this bidding strategy does not have a significant influence on faster slot inclusion, with priority fees as high as 40 gwei securing inclusion in over 10 slots while priority fees as low as 2 gwei securing inclusion in a single slot at times.

![The blue dots are individual priority fee bid premiums and the green line is the median bid premium.](/assets/images/bd0a254a9711b14866632e4c8c8d5bf3190c43dad013c89bba15eb9058d6f62a.png)

The blue dots are individual priority fee bid premiums and the green line is the median bid premium.

It is unclear what the optimal priority fee is for reliable slot inclusion. Generally speaking, it is not beneficial for a blob to remain stagnant in the mempool. A slower slot inclusion rate adds more uncertainty around gas price variance, rotating builder selection, and sporadic mev opportunities.

# Blob Market Adoption and Scaling

The blob market is still nascent and its adoption continues to be underway - with Scroll [recently adopting EIP-4844](https://twitter.com/Scroll_ZKP/status/1780222815423381611?t=vgTHwvnYtqnTQYxdG83iCQ&s=19) and zk rollups such as Aztec and Taiko targeting mainnet launches later in the year. [Per L2Beat](https://l2beat.com/scaling/data-availability?sort-by=da-layer&sort-order=desc), more rollups use Ethereum calldata as the data availability layer than blobs.

Additionally, [blobscriptions](https://blobscriptions.io/) aim to make it easier for a non-rollup user to access blobspace via an easy to use frontend UI. With blobscriptions enabled, [we saw the blob market reach capacity](https://vitalik.eth.limo/general/2024/03/28/blobs.html) very quickly, although activity has waned since.

After EIP-4844, [the next major technological step for scaling blob usage](https://ethresear.ch/t/from-4844-to-danksharding-a-path-to-scaling-ethereum-da/18046) is to implement full danksharding after potentially increasing the target from 3. Implementing data availability sampling technology will allow the current blob market to expand from 6 blobs up to 64, and eventually up to 256 blobs.

# Blob Market Outlook

Blob producers who are looking for a reasonable slot inclusion rate are currently restricted to use EIP-1559 max priority fee, which isn’t an effective parameter because there isn’t a significant correlation with faster blob inclusion rates. Additionally the priority fee gets updated slowly because the entire blob needs to be resubmitted into the mempool. As blob adoption continues to increase, we anticipate that it will be more difficult to rely on this bidding mechanism due to increased bandwidth usage and slower inclusion feedback.

As the blob market matures, it will necessitate more sophisticated bidding strategies to ensure on demand access to the data availability layer. Primev is monitoring the blob market and has [proposed mev-commit’s blob preconfirmations as a viable solution](https://ethresear.ch/t/blob-preconfirmations-with-inclusion-lists-to-mitigate-blob-contention-and-censorship/19150) for reliable blob inclusion. If you’re a blob producer or another Ethereum actor interested in optimizing blob inclusion, reach out to our team to participate in our experiments.
