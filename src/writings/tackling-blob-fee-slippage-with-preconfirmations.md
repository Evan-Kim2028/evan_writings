---
title: "Tackling Blob Fee Slippage with Preconfirmations"
date: "2024-09-01"
collection: highlights
tags:
  - writing
  - highlights
  - mirror
source_url: https://mirror.xyz/preconf.eth/xX2wu_3DC76qVYy1GHi1WVeOV2cXDF_rtDh7GlD6ZEU
source_platform: mirror
slug: tackling-blob-fee-slippage-with-preconfirmations
---

# TL;DR

* **Excessive Blob Fee Slippage:** Long inclusion times averaging 730 seconds exacerbated large fee spreads, which we coin as blob slippage, significantly increasing costs for rollups.
* **Ineffective Blob Posting Strategies:** Rollups employed various methods during the June 2024 congestion but failed to reduce blob inclusion times or mitigate fee slippage.
* **Network Instability and Builder Censorship:** The network experienced a spike in instability due to increased reorg rates, with approximately 10% of a typical month's reorgs occurring within half a day. Builders censored blobs because they weren't adequately compensated for the higher reorg risks.
* **Blob Preconfirmation Experiment:** We applied Blob Preconfirmations on mev-commit testnet and proved it as a method for faster, private bidding for blobs —offering a promising solution by reducing inclusion times, mitigating fee slippage, and fostering fee privacy through private blob mempools.

# Intro

This research delves into the challenges faced by the blob market during the June 2024 congestion, focusing on factors that drove higher fees and prolonged inclusion times. Two major issues—**blob slippage** and **nonce gaps**—led to an inefficient blob market, and existing rollup strategies couldn't adequately address these problems to achieve lower inclusion times.

By conducting an in-depth analysis on the Holesky network, we propose **preconfirmations** as a solution to enhance blob transaction efficiency. We tested preconfirmations through mev-commit, a p2p platform that facilitiates real time exchange of preconfirmations bids. mev-commit is also strengthened by [cryptographic commitments](https://mirror.xyz/preconf.eth/iz2J0uTXHhl8DiAkG-VLLwvCp-8qcc_Z7A8_4rU0A3g), enabling complete end to end privacy.

Our findings demonstrate that preconfirmations significantly improve inclusion times and create a more cost-effective environment for rollups. In addition to reducing fee slippage and inclusion times, this approach strengthens network stability and fosters innovation through private blob mempools.

# Blob Market Congestion: Causes and Impact (June 2024)

On June 20, 2024, the blob market experienced severe congestion as a result of a surge in transactions from the Layer Zero airdrop on Arbitrum. [Blocknative reported](https://www.blocknative.com/blog/june-20th-blob-contention-event-retrospective) blob gas fees spiking to 8000 gwei, marking a staggering 1 trillion-fold increase from the 1 wei minimum. This resulted in ~166 of ETH overpayment as rollups were slow to switch from blobs to calldata.blob fee market spike before returning to a lower price

![blob fee market spike before returning to a lower price](/assets/images/479c51d9934a9d289e9c66caf4270bcb7221fa8bdaa01f8462128783c0ad1af3.png)

blob fee market spike before returning to a lower price

# Increased Inclusion Time

The maximum capacity of 30 blobs per minute was overwhelmed, causing an excess of over 100 pending blobs per block. This volatility caused the blob market to cease functioning, sending the average blob inclusion time to 730 seconds with a 5 block standard deviation of 184,000% (2049 seconds).

![100 pending blobs = ](/assets/images/15ef69a42036c74ded8cb6dcfb18ece333cfa47ca9d2741908f5a19206b88548.png)

100 pending blobs =

Despite rollups adopting different strategies, none were able to lower blob inclusion times or mitigate fee slippage. Arbitrum, in particular, [faced significant difficulties](https://x.com/potuz_eth/status/1803885117384917228) in handling the large influx of traffic from the Layer Zero airdrop, though it managed to [dynamically switch to calldata](https://x.com/sosecrypto_kr/status/1803976329584611695) to cope with the situation.

In contrast, rollups without this capability incurred substantially higher fees until a manual switch to calldata could be made. For example, [Blast paid 5.22 ETH](https://x.com/sosecrypto_kr/status/1803976329584611695) for a single blob, and Linea ceased posting blobs entirely.

![Linea decided to stop posting blobs for the entire period. ](/assets/images/b8bbe9638d6c2d57d6c828ede6ca5e22be7b393b1f1bf23ef81ee048e93b4bc3.png)

Linea decided to stop posting blobs for the entire period.

### Network Instability: Builder Censorship and Reorg Risk

Amid the market volatility, block builders widely engaged in blob censorship. This is seen in the chart below, which shows that a significant number of blocks were built with zero blobs, even though the mempool contained many pending blobs. We are aware some block builders are trying to include blobs on a best effort basis, yet this social fallback is insufficient during times of high demand.

![post image](/assets/images/9f1b71f96b99fae75fbeb6731f5c03dd637db6a06228bd406c2ed342d0c486e6.png)

This behavior could be attributed to a lack of proper economic incentives, as builders were not compensated for the higher reorg risks associated with including blobs.

A [blob reorg study](https://mirror.xyz/dashboard/edit/xX2wu_3DC76qVYy1GHi1WVeOV2cXDF_rtDh7GlD6ZEU) conducted by Toni at the EF revealed that 92 reorgs occurred and 1,202 slots were missed per month. In particular the 6 blobs per slot were reorg rate for the month of January was .3%. During this intense blob congestion event, which spanned about 3,000 blocks, missed slots for 6 blob blocks surged to 1.05% and blob reorg rates spiked up to 7%.

![post image](/assets/images/ee054be7c7b66adfc0356d7a848e77dc0a0816ad926c78fbac13e7dd751c3720.png)

The combination of increased reorg risk and a lack of economic compensation may have driven builders to censor blobs, further exacerbating the congestion and instability during this period.

# Blob Bidding Strategy Inefficiencies

Blob posting strategies currently face two major inefficiencies that impede faster transaction inclusion: fee slippage and nonce gaps.

1. Fee slippage: This refers to the difference between the fee when a transaction is submitted and the actual fee paid at the time of inclusion. Blob transactions are particularly prone to slippage due to fluctuating market conditions and delayed inclusion times.
2. Nonce gaps: Ethereum's mempool processes transactions sequentially, meaning transactions with lower nonces must be included before those with higher nonces. This can create bottlenecks, especially when a lower-nonce transaction has a lower fee, forcing higher-fee transactions to wait.

These inefficiencies disrupt the bidding process, making it difficult for rollups to secure optimal pricing and faster inclusion. As a result, transaction pricing and inclusion are adversely affected, leading to higher costs and delays.

## Blob Fee Slippage

Blob slippage refers to a form of multi-block fee slippage, occurring when there is a gap between the blob market price at the time of submission to the mempool and the price at which it is finally included in a confirmed block. This slippage reflects the fee difference between submission and confirmation, often driven by market fluctuations or block inclusion delays.

A positive slippage value means the blob fee was higher at confirmation than at submission, indicating that the rollup overpaid. During the blob congestion event, blob slippage was notably more pronounced than non-blob slippage, as demonstrated in the charts below.

![post image](/assets/images/9fc3e571a0e0bb639ac6ceef75448d74da235d884fa166cda7f6b6e4285fde5a.png)

The most “favorable” blob slippage seemed to occur at shorter inclusion times as seen by the negative values in the chart below. This is logical, as shorter mempool durations reduce the uncertainty around market pricing.

![post image](/assets/images/8c0c72e6cbb4a409b8c6722fcdafc2079c2d33c14ca61dabb1596321cf4d2077.png)

## Priority Fee Slippage

Blob transactions exhibited negative priority fee slippage, meaning the actual fees paid were lower than expected, benefiting rollups. In contrast, positive blob fee slippage, as shown in the chart below, reflects overpayment caused by delayed inclusion. Although builders can't capture blob slippage because the fees are burned, they still collect priority fees.

![post image](/assets/images/cc927b6081404350cf8971298b6dcb4f42ab511b689e70bf8a338200da898579.png)

Negative priority fee slippage removes builders' incentive to prioritize these transactions for quicker inclusion, creating a misalignment between market pricing and faster transaction processing.

## Nonce Gap

[Geth's mempool enforces sequential nonces](https://github.com/ethereum/go-ethereum/blob/80b529ea713d71a27282ae76c2741c8bc5486502/core/txpool/blobpool/blobpool.go#L167C25-L168C25), meaning a transaction with a lower nonce must be included before one with a higher nonce, regardless of the priority fee amount. For rollups, this means that even if later transactions have higher fees, they remain pending until the earliest transaction is included. As a result, bids are limited by the strength of the lowest-nonce bid.

A negative nonce gap indicates that blobs were submitted in sequence, while a positive gap suggests that later nonces were submitted first. The chart below shows that all major rollups had nonce gaps within their submissions, explaining why transactions with [higher priority fees weren’t getting included](https://x.com/roberto_bayardo/status/1803888408072511926).

![post image](/assets/images/28226325208c671cd892a60e10dae82880809db31456c94cae8294262097b985.png)

One issue with this is that if a rollup wants to speed up the inclusion time for multiple pending blobs, it must first resubmit all lower-nonce blobs with higher fees. During a volatile situation, this would test the limits of the public mempool by increasing the number of blob resubmissions needed to improve inclusion rates.

# Preconfirmations: Enhancing Blob Posting Strategies

Preconfirmations directly address fee slippage by accelerating inclusion and minimizing delays, reducing costs for rollups and significantly enhancing network stability. By cutting slippage, preconfirmations give rollups a strategic edge, improving cost efficiency and competitiveness. Crucially, network stability is strengthened since only the blob inclusion fee (preconfirmation bid) needs updating, rather than resubmitting the entire blob transaction through the mempool.

However, even with preconfirmations, **blob fee slippage remains an additional cost** that rollups must manage effectively. The paper [Efficient Rollup Batch Posting Strategy on Base Layer](https://arxiv.org/abs/2212.10337)\* highlights the importance of optimizing posting strategies to balance posting and delay costs. The paper [Optimal Publishing Strategies on a Base Layer](https://arxiv.org/pdf/2312.06448) further generalizes these results to both zk and optimistic rollups, categorizing optimistic rollup cost functions as a homogeneous publishing cost with linear decay and zk rollup cost function as a constant publishing cost.

### Speed and Reliability of Preconfs

To assess the impact of preconfirmations on inclusion speed, we compared preconf acceptance times to standard mempool inclusion times. To test the effectiveness of preconfirmations under real-world conditions, we focused on blobs that were struggling to get included in a timely manner. We sent 6 blob transactions with un-competitive priority fee bids.

As shown in the chart below, approximately ~247,000 blobs were confirmed within 24 seconds, while ~15,000 took longer, with some exceeding 24 seconds. The chart below only shows blobs confirmed after 24 seconds.

![post image](/assets/images/d14c42e0ecd3045b42384d31d269c4dd79c4ee87f3f00c11fa977737472651bc.png)

Each preconf has a `decayStartTimestamp`, marking the point when the bid begins to decrease in value, and once a builder accepts the bid, the `dispatchTimestamp` is recorded on-chain, ensuring transparency and accountability in bid timing. Details about the bid decay mechanism [here](https://docs.primev.xyz/concepts/bids/bid-decay-mechanism#mechanism-description). We use the bid decay function to measure preconf bid acceptance latency, which is the time it takes for the builder to notify the bidder that the preconf has been accepted.

On average, preconf bid latency was just ~75ms—dramatically faster than the ~96 seconds (8 blocks) typically needed for inclusion through the public mempool. This represents a 1000x improvement.

This faster response time allows for more agile bidding strategies, particularly during high volatility or congestion when public mempool inclusion times can spike, allowing rollups to have more fine tuned control and more sophisticated blob posting strategies.

![post image](/assets/images/10c214b80c074c238733941fa14f4d457ae4097ecbf4da5e5009bdc00f6cf6d7.png)

### Preconf Bid is all you need

If the preconfirmation (preconf) bid is sufficiently high, it acts as a substitution for priority fee, seamlessly integrating into the block-building process. Our inclusion rate tests, as shown in the chart below, demonstrate that blobs submitted with only preconf bids achieve can reliably drive transaction inclusion.

![post image](/assets/images/a1b4725b64536934dadb46a83e58b66be41da40163226200a862473c2b3d03f5.png)

### Private Blob Mempool

Using mev-commit, rollups can send their [blob transaction payloads directly](https://docs.primev.xyz/get-started/bidders/best-practices#transaction-payload) to a builder, creating a private mempool. Using a private mempool [has advantages](https://x.com/bertcmiller/status/1836139173159264579) for the rollup because it obfuscates the inclusion bid amount, bypasses the public mempool rules, which are unforgiving to blobs, and prevents more sophisticated rollups from front-running other rollups blobs.

Additionally, private blob mempools offer greater room for innovation than public mempools. Private mempools also allow for more innovation such as [Titan’s custom blob pool](https://docs.titanbuilder.xyz/api/eth_sendblobs) that enables the sending of all permutations of blob transactions from a single sender, which allows partial blob inclusion and allows for multiple transactions with the same nonce.

# Conclusion

This research underscores the transformative potential of preconfirmations in optimizing the blob market, particularly during periods of congestion. Preconfirmations drastically reduce blob inclusion times and mitigate fee slippage. This offers rollups a strategic advantage by securing optimal transaction pricing and faster inclusion. Additionally, the implementation of preconfirmations enhances network stability by reducing the need for costly public mempool resubmissions.

Furthermore, private blob mempools open new avenues for innovation, allowing rollups to bypass the rigid constraints of the public mempool, further improving transaction efficiency. The integration of strategies like Titan’s custom blob pool demonstrates the broader potential for optimizing blob transactions through private infrastructure.

As the Ethereum ecosystem continues to scale, preconfirmations will be critical in solving the bottlenecks that currently limit the blob market. Future work should explore refining preconfirmation pricing models, optimizing blob posting strategies, and deepening the integration of private blob mempools, ultimately contributing to a more efficient and resilient Ethereum network.
