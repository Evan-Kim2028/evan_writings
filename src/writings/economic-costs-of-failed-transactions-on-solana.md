---
title: "Economic Costs of Failed Transactions on Solana"
date: "2024-08-01"
collection: data
tags:
  - writing
  - data
  - paragraph
source_url: https://paragraph.xyz/@evandekim/economic-costs-of-failed-transactions-on-solana
source_platform: paragraph
slug: economic-costs-of-failed-transactions-on-solana
---

# TLDR:

* Pyth contract has a 26.5% tx failure rate (292,165 txs) across 1.1m transactions, resulting in 1.45 SOL in lost fees. The failure rate is cross referenced with [Dune](https://dune.com/queries/3980333?category=canonical&namespace=solana&id=solana.transactions) and [solscan](https://solscan.io/account/rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ).
* Total tx failure rate during this period is 8% (69,356,928 txs failed) across ~781m transactions, resulting in 346 SOL in lost fees. The failure rate cross referenced with [Dune](https://dune.com/queries/3980339).
* Pyth receiver contract has a 3.3x higher tx failure rate than the general tx failure rate.
* Tx failures are an additional revenue source for Solana validators and there is no economic incentive to lower the tx failure rates.

# Introduction

This research looks at some behavior related to failed Solana transactions. Specifically we compare the general tx failure rate to the [Pyth receiver contract](https://docs.pyth.network/price-feeds/contract-addresses/solana). This contract has critical functionality to the Pyth oracle model and receives price feed updates from publishers. We see that the failure rate and see that the Pyth contract generates nearly 3x more failed transactions on average, costing about ~10 SOL monthly in lost fees to the publishers.

### Cryptohouse and Dune

The results are validated by replicating the queries between Dune and Cryptohouse, two strong data sources for free Solana data. A 600,000 slot range [282300000, 282900000], about 3 days, is chosen to keep resource usage in check. For the duplicate queries between Cryptohouse and Dune, Dune was generally faster (~5 seconds) vs (~15 seconds).

* [Cryptohouse](https://x.com/ClickHouseDB/status/1821192971896627585) is a new public goods data source for Solana data powered by Clickhouse and Goldsky. Current functionality is limited - can't save and share queries through a url, a non-trivial amount of data columns are missing, can't perform joins or multi-statements. Please refer to the Appendix section for the Cryptohouse queries.
* Dune needs no introduction. Currently the crypto data standard for public goods dashboards. [Query here](https://dune.com/queries/3980333?category=canonical&namespace=solana&id=solana.transactions) for pyth contract tx failure rates. [Query here](https://dune.com/queries/3980339) for general tx failure rates.

# Results

The analysis of transaction failures on the Solana network reveals significant insights, particularly regarding the performance of the Pyth contract. Over a three-day period, the Pyth contract experienced a high transaction failure rate of 26.5%, resulting in 1.45 SOL in lost fees.

This failure rate is 3.3 times higher than the network-wide average of 8%, which led to 346 SOL in lost fees over the same period. Extrapolating these figures to a monthly timeframe, the Pyth contract could lose 10.45 SOL, while network-wide losses could reach 3,460 SOL. The high failure rate of the Pyth contract suggests potential inefficiencies or persistent issues within its logic.

Moreover, the economic implications of transaction failures are significant, as they contribute to validator revenue, presenting little incentive for reducing these rates, despite the potential for wasted resources. This complex interplay between transaction failure rates, validator incentives, and network performance highlights the challenges and opportunities within the Solana ecosystem.

### **Pyth**

If we extrapolate these 3 day values to monthly values, then the amount of lost fees for the Pyth contract becomes 10.45 SOL and 3460 SOL for all transactions. Manually checking the [solscan contract transactions page](https://solscan.io/account/rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ), the main tx failure reasons are:

* `Program Error: "Instruction #1 Failed - The posted VAA account has the wrong owner"`
* `"Instruction #1 Failed - Failed to deserialize the account"`
* `Program Error: "Instruction #1 Failed - UnverifiedVaa"`

A hypothesis would be that there is some logic that keeps producing these errors. A deeper dive into solana instructions data would be required to prove the hypothesis though. It would be very important to know whether these failure rates are delaying Pyth prices to be published on-chain by multiple slots as this would present an additional hidden latency for using Pyth oracles.

### Validator Revenue

Although the 8% tx failure rate is an extra tax on the users who submit failed transactions, conversely it represents an alternative form of Validator revenue because they are the ones who ultimately keep the fees from failed transactions.

Although failed transaction rates end up wasting blockspace and computation power, the corollary is that validators do not have an economic disincentive to lower the transaction failure rates because they are still being economically rewarded. A major reason for tx failure rates is due to mev-searcher competition on Solana. Searchers will use spam strategies to land profitable mev opportunities which end up making spamming strategies economically viable. Instead of being seen as a "waste of blockspace", this could also be interpreted as an "abundance of blockspace".

# Conclusion

In conclusion, the analysis of transaction failures on the Solana network reveals a significant discrepancy between the Pyth contract's failure rate and the network-wide average. The Pyth contract's 26.5% failure rate indicates possible inefficiencies or recurring issues within its logic, resulting in considerable lost fees.

These transaction failures also play a crucial economic role, generating revenue for validators and offering little incentive to reduce failure rates. This interplay between high failure rates, validator incentives, and overall network performance highlights both the challenges and opportunities present in the Solana ecosystem.

Further investigation into the underlying causes of the Pyth contract's high failure rate, as well as its potential impact on price feed latency, is essential to fully address these concerns.

# Appendix: Cryptohouse Queries

### Pyth Receiver Contract Tx Failure Rates

```
SELECT
    status,
    COUNT(*) AS status_count
FROM
    solana.transactions
WHERE
    arrayExists(
        x -> x.1 IN [
            'rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ'
        ],
        accounts
    )
    AND block_slot > 282300000
    AND block_slot < 282900000
GROUP BY
    status
```

### General Contract Tx Failure Rates

```
SELECT
    status,
    COUNT(*) AS status_count
FROM
    solana.transactions
WHERE block_slot > 282300000
    AND block_slot < 282900000
GROUP BY
    status
```

**A note on lamports:**

* The average lamports per slot for the Pyth contract is 5.7m lamports (0.00575 SOL).
* The average lamports per slot is 4.6b lamports (4.6 SOL).
* I am interpreting lamports as the total "cost" for compute units used per transaction. The [google bigquery definition](https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=crypto_solana_mainnet_us&page=dataset&project=quickstart-tutorial-245520&ws=!1m5!1m4!4m3!1sbigquery-public-data!2scrypto_solana_mainnet_us!3sAccounts), where cryptohouse data is sourced from, defines lamport column as `The account's balance, in Lamports` which doesn't seem as useful though.

### Pyth Average Lamports per Block

```
SELECT 
    AVG(block_slot_avg) AS average_lamports_per_block_slot
FROM (
    SELECT 
        block_slot,
        AVG(lamports) AS block_slot_avg
    FROM 
        solana.accounts
    WHERE 
        owner = 'rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ' -- pyth receiver contract
    GROUP BY 
        block_slot
) AS subquery;
```

### General Average Lamports per Block

```
SELECT 
    AVG(block_slot_avg) AS average_lamports_per_block_slot
FROM (
    SELECT 
        block_slot,
        AVG(lamports) AS block_slot_avg
    FROM 
        solana.accounts
    GROUP BY 
        block_slot
) AS subquery;
```
