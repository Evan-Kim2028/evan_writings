---
title: "Conquering Solana Data Analytics Part 1 - Tooling"
date: "2024-08-01"
collection: data
tags:
  - writing
  - data
  - paragraph
source_url: https://paragraph.xyz/@evandekim/conquering-solana-data-analytics-part-1-tooling
source_platform: paragraph
slug: conquering-solana-data-analytics-part-1-tooling
---

## Intro

This is the start of a series of posts that examines how to analyze Solana data in SQL using different platforms. We start off the series with a couple of key queries that yield insights to both the data platforms and the data themselves.

The best free SQL based tools are [Cryptohouse (powered by Goldksy)](https://crypto.clickhouse.com/), [Dune](http://dune.com) and [Flipside](https://flipsidecrypto.xyz/) for accessing Solana data. This post evaluates the tradeoffs between using each of these platforms by using a test of useful queries. These queries look at the most fundamental table for Solana data, the `transactions` table, which forms the basis of most fundamental research on Solana.

We'll examine three queries:

1. **Transaction Sample**: A basic query to quickly inspect the dataset.
2. **Filter Array for Accounts**: A more complex query that filters transactions based on a subset of accounts, an essential task given that many Solana transactions have columns stored as arrays.
3. **Filter + GroupBy Aggregation**: A sophisticated query that filters account arrays and performs a groupby aggregation, a common task in data analysis.

### `Transactions` Dataset

The `transactions` table is a fundamental table for Solana blockchain data and understanding how to effectively navigate through the table is key to unlocking more on-chain insights. Every Solana transaction touches a set of accounts, which are stored in an array. There is also a pre-balance and post-balance column arrays which store the SOL amount before and after the transaction, which are important to derive SOL related volume for fees, compute costs, and validator revenue.

This table also has a status/success column that determines whether the transaction was successful or not. Continuously higher than normal transaction failures can indicate an interesting research direction.

Finally the `transactions` table contains all of the instructions required to execute the transaction in a set of logical steps. For those familiar with EVM data, Solana instructions are similar to EVM log event data.

### Tooling

There are three primary criteria for evaluating these tools: performance, features, and data availability. The importance of each criterion depends on the specific research outcomes desired.

For instance, Cryptohouse tends to have faster query results, but it currently lacks features like dashboards and full data availability compared to Flipside and Dune. Dune has custom Trino-based DuneSQL, while Flipside uses a more standardized SQL dialect, making it easier to use with AI models like ChatGPT. Dune also offers intelligent caching, speeding up queries that are run multiple times.

## Query #1 - select most recent transactions

This is a basic query that is commonly used to take a quick look at the dataset that you are working with. It is important to see that the dataset you choose has both the columns and accurate (e.g. non null) data in those columns. Although blockchain data is standardized at the node level, each data indexer chooses the most efficient way to store and format their data to serve to users.

Some notable comments about the `transactions` dataset differences is namely what is available and what format it shows up in. If the columns you want do not exist in the dataset, then that automatically restricts what data platform suits your needs.

For example Cryptohouse does not have an `instructions` column. While dune has `instructions`, the output is not friendly for longer formats so it's not possible to inspect the output of larger sized columns. While Flipside has `instructions` as well, the layout is the opposite of dune where each column is maximally sized. This is not the most ergonomical because the width of the data returned is quite large to scroll through. Another example is that both Cryptohouse and Dune have a `tx_index` column whereas flipside doesn't.

### Performance

| Platform | Query Execution Time (seconds) | Rows Read | Bytes Read |
| --- | --- | --- | --- |

|  |  |  |  |
| --- | --- | --- | --- |
| **Dune** | 15 | 30,228,504 rows | 50.0 GB |

|  |  |  |  |
| --- | --- | --- | --- |
| **Crypto-house** | 13.437 | 149,395,554 rows | 248.11 GiB |

|  |  |  |  |
| --- | --- | --- | --- |
| **Flipside** | 8 | N/A | N/A |

### Cryptohouse

```
SELECT
  *
FROM
  solana.transactions
WHERE block_timestamp >= now() - INTERVAL 12 HOUR
ORDER BY
  block_slot,
  index
LIMIT 1000
```

### Dune

```
SELECT
  *
FROM solana.transactions
WHERE block_time >= CURRENT_TIMESTAMP - INTERVAL '12' HOUR
ORDER BY
  block_slot,
  index
LIMIT 1000
```

### Flipside

```
SELECT 
  *
FROM 
  solana.core.fact_transactions
WHERE 
  block_timestamp >= DATEADD(HOUR, -12, CURRENT_TIMESTAMP)
ORDER BY 
  block_id
LIMIT 1000;
```

## Query #2 - filter array for accounts

This is a more complex query that filters transactions based on a subset of accounts. This is a very useful query because a lot of Solana `transactions` columns are stored as arrays so it's important to know how to filter through arrays. The second is that most analysis will be geared towards specific accounts (protocol accounts, mev accounts, trading accounts, etc).

Notably Crytpohouse starts to shine with these kinds of queries and offers superior performance compared to Dune and Flipside. Cryptohouse also scanned nearly 4x as much data as the Dune. Flipside also performed fairly well with the filter task as well, but not as much data is available on the query statistics.

### Performance

| Platform | Query Execution Time (seconds) | Rows Read | Bytes Read |
| --- | --- | --- | --- |

|  |  |  |  |
| --- | --- | --- | --- |
| **Dune** | 115.874 | 30,428,286 rows | 50.5 GB |

|  |  |  |  |
| --- | --- | --- | --- |
| **Crypto-house** | 16.269 | 149,123,945 rows | 198.12 GiB |

|  |  |  |  |
| --- | --- | --- | --- |
| **Flipside** | 37 | N/A | N/A |

### Cryptohouse

```
SELECT
  *
FROM
  solana.transactions
WHERE
  arrayExists(
    x -> x.1 IN (
      'Fc8bpeCMifWYv97pQ3k5xDvd98nuVg6yAaZrwmy4RRp6',
      -- zeta contract
      'rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ' -- pyth contract
    ),
    accounts
  )
  AND block_timestamp >= now() - INTERVAL 12 HOUR
ORDER BY
  block_slot,
  index
LIMIT 10000
```

### Dune

```
SELECT
  *
FROM
  solana.transactions
WHERE
  arrayExists(
    x -> x.1 IN (
      'Fc8bpeCMifWYv97pQ3k5xDvd98nuVg6yAaZrwmy4RRp6',
      -- zeta contract
      'rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ' -- pyth contract
    ),
    accounts
  )
  AND block_timestamp >= now() - INTERVAL 12 HOUR
ORDER BY
  block_slot,
  index
LIMIT 10000
```

### Flipside

```
WITH filtered_accounts AS (
  SELECT 
    *
  FROM 
    solana.core.fact_transactions
  WHERE 
    block_timestamp >= DATEADD(HOUR, -12, CURRENT_TIMESTAMP)
)
SELECT 
  *
FROM 
  filtered_accounts f,
  LATERAL FLATTEN(input => f.account_keys) AS a
WHERE 
  a.value:pubkey IN (
    'Fc8bpeCMifWYv97pQ3k5xDvd98nuVg6yAaZrwmy4RRp6', 
    'rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ'
  )
ORDER BY 
  block_id
LIMIT 10000;
```

## Query #3 - filter + groupby aggregation

This is a more complex query that filters the account arrays and then performs a groupby aggregation. Groupby aggregations are the bread and butter for most analytics questions and provides strong intuition on the overall shape of the data. In this particular query, we filter accounts for the [pyth contract](https://docs.pyth.network/price-feeds/contract-addresses/solana) and groupby whether the transaction was a failure or success to analyze the failure rates specific to that contract. It turned out that the Pyth contract is [experiencing 3x higher failure](https://paragraph.xyz/@evandekim/economic-costs-of-failed-transactions-on-solana) rates than the average Solana transaction (more on this soon).

The Pyth example is a query example that does not rely on a dashboard to gain insights into the data. These types of queries would be best suited for the fastest performing tool, which happens to be Cryptohouse. Here Cryptohouse really shines, reading more rows and processing more bytes than Dune while being multiples faster than both Dune and Flipside.

### Performance

| Platform | Query Execution Time (seconds) | Rows Read | Bytes Read |
| --- | --- | --- | --- |

|  |  |  |  |
| --- | --- | --- | --- |
| **Dune** | 54.143 | 150,493,063 rows | 50.3 GB |

|  |  |  |  |
| --- | --- | --- | --- |
| **Crypto-house** | 13.247 | 704,857,665 rows | 225.74 GiB |

|  |  |  |  |
| --- | --- | --- | --- |
| **Flipside** | 38 | N/A | N/A |

### Cryptohouse

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
    AND block_slot > 282400000
    AND block_slot < 282900000
GROUP BY
    status
```

### Dune

```
SELECT
  success,
  COUNT(*) AS transaction_count
FROM solana.transactions
WHERE
  block_slot > 282400000
  AND block_slot < 282900000
  AND ANY_MATCH(account_keys, x -> x = 'rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ')
GROUP BY
  success
```

### Flipside

```
WITH filtered_transactions AS (
  SELECT 
    *
  FROM 
    solana.core.fact_transactions
  WHERE 
    block_id > 282400000
    AND block_id < 282900000
)
SELECT 
  SUCCEEDED,
  COUNT(*) AS status_count
FROM 
  filtered_transactions f,
  LATERAL FLATTEN(input => f.account_keys) AS a
WHERE 
  a.value:pubkey IN (
    'rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ'
  )
GROUP BY 
  SUCCEEDED;
```

### Conclusion

In conclusion, while all three platforms—Cryptohouse, Dune, and Flipside—offer valuable tools for analyzing Solana data, each has its strengths and weaknesses. Cryptohouse excels in performance, particularly with more complex queries, but lacks some features and full data availability. Dune offers flexibility with its custom SQL dialect and intelligent caching, while Flipside provides a more standardized experience with solid performance. The best choice of platform will depend on your specific needs, whether it be speed, ease of use, or the availability of specific features.
