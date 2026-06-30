---
title: "Economics of Sui Shared Liquidity Pool Objects"
date: "2024-12-01"
collection: highlights
tags:
  - writing
  - highlights
  - paragraph
source_url: https://paragraph.xyz/@evandekim/economics-of-sui-shared-liquidity-pool-objects
source_platform: paragraph
slug: economics-of-sui-shared-liquidity-pool-objects
---

***Sentio Referral Code****: Reach out to @is\_ye in the* *[sentio telegram chat](https://dune.com/evandekim/t.me/sentioxyz)* *and give the referral code evandekim2025 for a 20% discount for Sentio subscription!*

# TLDR

* Shared liquidity pool object mutations have been consistently increasing, now occurring in nearly every Sui checkpoint (≈100% of blocks).
* Over 50% of transactions to mutate shared liquidity pool objects that pay the maximum gas fee end up above the median block position.
* Users paying max gas fees have a 0.001-0.002% chance of securing the top block position, compared to 7-10% for those not paying the highest fees.
* SIP-45 proposes increasing the max gas price to 1 trillion MIST and making transaction inclusion faster at the expense of increased validator network bandwidth utilization.

# Introduction

The Sui blockchain faces unique challenges in processing shared object transactions that require consensus. This analysis examines shared object change data across 28 weeks, focusing specifically on shared liquidity pool objects and their gas fee patterns. The findings inform critical decisions about SIP-45, a proposed change to transaction prioritization mechanisms.

The following data and query can be found in the appendix section and run using [Sentio data studio](https://docs.sentio.xyz/reference/executesql). Objects are filtered specifically for shared objects such as liquidity pools and swaps. Query performance took about 8:30 minutes so it is recommended to run on a lower time frame first. All of the charts can be found in the [Suinomics Dune dashboard](https://dune.com/evandekim1/suinomics#shared-liquidity-objects) under shared liquidity pool objects

# Shared Liquidity Pool Objects

Shared object mutations now occur in nearly every Sui checkpoint, indicating market saturationSui's shared objects are mutable, lack specific ownership, and enable complex interactions between multiple users by leveraging their own authorization logic within smart contracts. Unlike owned objects, which are tied to a single user and can be updated without consensus, shared objects require a consensus protocol to ensure safe and consistent modifications when accessed by multiple parties.

The most common examples of shared objects are liquidity pools, where users have shared access to many pools of liquidity. Over the past six months, the number of shared liquidity pool objects has reached saturation, with at least one shared object being [mutated](https://intro.sui-book.com/unit-two/lessons/2_ownership.html) in almost every Sui checkpoint (equivalent to a block).

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/028c31c970c574d5cb27d605f8be10f9.png)

This saturation indicates growing network activity and highlights the importance of efficient transaction ordering mechanisms. The data reveals that shared object mutations have become a fundamental part of Sui's daily operations, particularly in DeFi applications where multiple users frequently interact with the same liquidity pools.

# Max Gas Fees

Max gas fees represent the highest amount a user is willing to pay for the computational and storage resources required to process their transaction. According to [Sui documentation](https://docs.sui.io/concepts/tokenomics/gas-pricing), gas fees are calculated based on the computation units and storage units consumed by a transaction, multiplied by their respective prices. The computation price itself is a combination of a network-wide reference price and an optional user-specified tip aimed at incentivizing faster processing by validators.

However, quantitative analysis of 28 weeks of transaction data, focusing on shared liquidity pool objects, reveals an intriguing insight: paying the maximum gas fee does not consistently guarantee a superior position within a block. The data shows that over 50% of transactions that opted for the highest gas fees ended up in positions that were worse than the median block position.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/901283a51bc2d992532df1662733e5ff.png)

Ideally, users expect that higher gas fees would translate to higher priority and quicker inclusion in blocks, but this is only the case approximately 20% of the time. This discrepancy suggests that while the Sui network's gas pricing mechanism is designed to prioritize transactions based on fee offerings, other factors—such as network congestion and validator behavior—significantly influence transaction ordering. Consequently, users do not always benefit from setting their max gas fees to the highest possible values to maximize transaction inclusion.

Additionally, while the number of shared liquidity object mutations has increased, the number of max gas paid for these mutations has decreased. At the same time the number of shared objects that get the top position has been rising steadily. The below chart shows that a sender has a higher probability of getting top of block (~ 7 -10%) over those paying the max gas fee (.001 - .002%).

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/1d18bc2aece9158a3cca825e3b0d36dd.png)

This misalignment between gas fees and transaction positioning presents a significant challenge for users seeking predictable transaction inclusion times. The data suggests that the current gas fee mechanism may need refinement to better serve its intended purpose of transaction prioritization.

# [SIP-45](https://github.com/shio-coder/sips/blob/main/sips/sip-45.md): Prioritized Transaction Submission

SIP-45 introduces greater economic incentives to utilize more validator bandwidth for more reliable inclusion. However, this adjustment could inadvertently drive spamming, as users and bots exploit the opportunity to secure consistent inclusion in blocks. An amplification factor of 5 has been proposed as the supremum gas price required to be immediately broadcasted. Thus if a reference gas price is 750 MIST and the amplification factor is 5, then a transaction will only need 3,750 MIST to be broadcast faster.

SIP-45: Prioritized Transaction Submission a SIP that is going to test the boundaries of consensus spam on Sui. The major changes are:

1. Increase the max gas price from 99,999 MIST to 1,000,000,000,000 (1 trillion MIST).

1. Allow transactions that pay a higher gas price to be immediately broadcasted.

Chains offering low transaction costs and high blockspace are inherently vulnerable to transactions spamming, as [bots exploit these conditions](https://x.com/smyyguy/status/1835030196258246692) to to maximize profits. While this increases blockspace usage, it also boosts [validator compensation](https://x.com/smyyguy/status/1870953803606049064), often leading to higher yields.

A brief numerical analysis is provided [in the SIP-45 proposal](https://github.com/shio-coder/sips/blob/main/sips/sip-45.md) which demonstrates potential effects with an amplification factor of 5. The [authors make the assumption](https://github.com/sui-foundation/sips/pull/45#discussion_r1870864858) that most transactions are not competitive in nature. They isolate competitive transactions based on the amount of gas being paid. An important observation in the initial data shows that the gas price bucket distribution is heavily skewed at the tail end at the 90,000 - 100,000 MIST maximum range, suggesting that a higher gas price is warranted.

# Optimal Amplification Factor

Choosing an amplification factor will strike a balance between higher yield vs increased bandwidth usage. For example a low amplification factor of 2 will make it very low cost to spam the network, soaking up additional bandwidth. A higher amplification factor such as 100 will decrease the subset of transactions that will spam the network, making the supremum gas price a much higher hurdle.

Given that the numerical analysis indicated a heavily skewed tail at the current maximum gas price range already, indicating an active market at that price point, an argument could be made that a higher amplification factor of 120 could be set as a conservative factor, making the supremum gas price 750 MIST \* 120 = 90,000 MIST a good starting point and can be gradually lowered from there as a tradeoff to introducing a new priority fee feature while still conserving validator bandwidth.

Another reason to set a more conservative amplification factor is to also to understand what the effects of increasing the max gas fee will have on network activity. With the current fee cap, it is not clear what the upper bounds for max gas fees will be for contentious shared objects and whether the higher certainty of transaction inclusion will also spark higher demand that is not reflected in historical data numbers. Intuitively as the surface area of mutated shared liquidity pool objects increases, so should too the number of contentious opportunities.

# Conclusion

This article expands on the initial results so that a more data informed decision can be made. A more sui-native way to quantify contentious transactions based on ownership. If an object has a single owner, then these transactions get filtered out into a fast path, skipping the consensus mechanism. If an object is a shared object and can have different owners, then these objects will fall into state contention based on user is claiming ownership and getting the state lock on that object.

The implementation of SIP-45 represents a critical evolution in Sui's transaction processing mechanism. While the proposed changes offer potential improvements in transaction inclusion predictability, careful consideration must be given to the amplification factor to prevent network congestion while maintaining economic efficiency. Ongoing monitoring and analysis of shared object mutations and gas fee patterns will be essential to fine-tune these parameters and ensure optimal network performance.

## Appendix: Sentio SQL Query

```
WITH object_changes_filter AS (
    SELECT DISTINCT
        digest,
        checkpoint
    FROM sui.object_changes
    WHERE owner_type = 'shared'
      AND timestamp >= now() - INTERVAL 28 WEEK
      AND (object_type LIKE '%pool%' OR object_type LIKE '%swap%')
),
recent_transactions AS (
    SELECT 
        t.digest, 
        t.checkpoint, 
        t.sender,
        t.gas_price, 
        t.transaction_position,
        toStartOfHour(t.timestamp) AS hour
    FROM sui.transactions AS t
    INNER JOIN object_changes_filter AS ocf
    ON t.digest = ocf.digest AND t.checkpoint = ocf.checkpoint
),
precomputed_metrics AS (
    SELECT
        hour,
        min(rt.gas_price) AS min_gas_price,
        max(rt.gas_price) AS max_gas_price,
        min(rt.transaction_position) AS min_position,
        max(rt.transaction_position) AS max_position,
        median(rt.transaction_position) AS median_position
    FROM recent_transactions AS rt
    GROUP BY hour
),
aggregated_data AS (
    SELECT
        rt.hour,
        avg(rt.gas_price) AS avg_gas_price,
        pm.min_gas_price,
        pm.max_gas_price,
        avg(rt.transaction_position) AS avg_position,
        pm.min_position,
        pm.max_position,
        pm.median_position,
        countIf(rt.gas_price = pm.min_gas_price) AS count_min_gas_price,
        countIf(rt.gas_price = pm.max_gas_price) AS count_max_gas_price,
        countIf(rt.transaction_position = pm.min_position) AS count_min_position,
        countIf(rt.transaction_position = pm.max_position) AS count_max_position,
        countIf(rt.gas_price = pm.max_gas_price AND rt.transaction_position = pm.min_position) AS max_gas_in_min_position,
        countIf(rt.gas_price = pm.max_gas_price AND rt.transaction_position > pm.median_position) AS max_gas_higher_than_median_position,
        uniqExact(rt.checkpoint) AS unique_checkpoints_count,
        count() AS total_rows
    FROM recent_transactions AS rt
    INNER JOIN precomputed_metrics AS pm
    ON rt.hour = pm.hour
    GROUP BY rt.hour, pm.min_gas_price, pm.max_gas_price, pm.min_position, pm.max_position, pm.median_position
)

SELECT
    hour,
    avg_gas_price,
    min_gas_price,
    max_gas_price,
    avg_position,
    min_position,
    max_position,
    median_position,
    count_min_gas_price,
    count_max_gas_price,
    count_min_position,
    count_max_position,
    max_gas_in_min_position,
    max_gas_higher_than_median_position,
    unique_checkpoints_count,
    total_rows AS total_shared_objects_hourly
FROM aggregated_data
ORDER BY hour DESC;
```
