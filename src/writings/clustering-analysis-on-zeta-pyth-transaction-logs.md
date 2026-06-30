---
title: "Clustering Analysis on Zeta <> Pyth Transaction Logs"
date: "2024-08-01"
collection: data
tags:
  - writing
  - data
  - paragraph
source_url: https://paragraph.xyz/@evandekim/clustering-analysis-on-zeta-lessgreater-pyth-transaction-logs
source_platform: paragraph
slug: clustering-analysis-on-zeta-pyth-transaction-logs
---

## Intro

Previous research looked at [transaction faliure rates](https://paragraph.xyz/@evandekim/economic-costs-of-failed-transactions-on-solana) on Solana and identified higher than average failure rates with the Pyth pull oracle contracts. Specifically the signer contract Zeta seems to be failing with many of its price updates, leading to upwards of 20 SOL a week in lost fees from submitting failed transactions.

This post will follow up, examining the on-chain sample data (~1000 blocks is the data cap) more closely with [Polars DataFrame](https://pola.rs/) and [Agglomerative Clustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html) to analyze log message patterns.

Data is abstracted using the Clickhouse python client from Cryptohouse. Once extracted, data is transformed via Polars. Polars allows for complex data transformations and powerful exploratory analysis by structuring data in DataFrames. It excels at handling arrays, unnesting columns, reusing transformations, and supports ad-hoc visualizations—all within a single notebook.

The notebook for all of the code [can be found here](https://github.com/Evan-Kim2028/pyth_analysis/blob/main/cryptohouse_historical.ipynb).

## Jito Blocks

Compared to the average 8% transaction failure rate on Solana, transactions that utilize Jito have [much lower failure rates, around 0.8%](https://crypto.clickhouse.com?query=V0lUSCBtYXhfaW5kZXhfcGVyX3Nsb3QgQVMgKAogICAgU0VMRUNUCiAgICAgICAgYmxvY2tfc2xvdCwKICAgICAgICBNQVgoaW5kZXgpIEFTIGJsb2NrX3NpemUKICAgIEZST00KICAgICAgICBzb2xhbmEudHJhbnNhY3Rpb25zCiAgICBHUk9VUCBCWQogICAgICAgIGJsb2NrX3Nsb3QKKQpTRUxFQ1QgCiAgICBzdGF0dXMsCiAgICBDT1VOVCgqKSBBUyBzdGF0dXNfY291bnQsCiAgICBBVkcoaW5kZXgpIEFTIGF2Z19pbmRleCwKICAgIG1lZGlhbihpbmRleCkgQVMgbWVkaWFuX2luZGV4LAogICAgQVZHKG1heF9pbmRleF9wZXJfc2xvdC5ibG9ja19zaXplKSBBUyBhdmdfYmxvY2tfc2l6ZQpGUk9NCiAgICBzb2xhbmEudHJhbnNhY3Rpb25zCkpPSU4KICAgIG1heF9pbmRleF9wZXJfc2xvdApPTgogICAgc29sYW5hLnRyYW5zYWN0aW9ucy5ibG9ja19zbG90ID0gbWF4X2luZGV4X3Blcl9zbG90LmJsb2NrX3Nsb3QKV0hFUkUKICAgIGFycmF5RXhpc3RzKAogICAgICAgIHggLT4geC4xIElOIFsKICAgICAgICAgICAgJzk2Z1laR0xuSllWRm1ianpvcFBTVTZRaUVWNWZHcVpOeU45bm1OaHZyWlU1JywKICAgICAgICAgICAgJ0hGcVU1eDYzVlRxdlFzczhocDExaTR3VlY4YkQ0NFB2d3VjZloyYlU3Z1JlJywKICAgICAgICAgICAgJ0N3OENGeU05RmtvTWk3SzdDcmY2SE5RcWY0dUVNenBLdzZRTmdoWEx2TGtZJywKICAgICAgICAgICAgJ0FEYVVNaWQ5eWZVeXRxTUJnb3B3amIyRFRMU29rVFN6TDF6dDZpR1BhUzQ5JywKICAgICAgICAgICAgJ0RmWHlnU200akN5TkN5YlZZWUs2RHd2V3FqS2VlOHBiRG1KR2NMV05EWGpoJywKICAgICAgICAgICAgJ0FEdVVrUjR2cUxVTVdYeFc5Z2g2RDZMOHBNU2F3aW1jdGNOWjVwR3dEY0V0JywKICAgICAgICAgICAgJ0R0dFdhTXVWdlRpZHVaUm5ndUxGN2pOeFRnaU1CWjFoeUF1bUtVaUwyS1JMJywKICAgICAgICAgICAgJzNBVmk5VGc5VW82OHRKZnV2b0t2cUtOV0trQzV3UGRTU2RlQm5pektaNmpUJwogICAgICAgIF0sCiAgICAgICAgYWNjb3VudHMKICAgICkKICAgIEFORCBzb2xhbmEudHJhbnNhY3Rpb25zLmJsb2NrX3Nsb3QgPiAyODI2MDAwMDAKICAgIEFORCBzb2xhbmEudHJhbnNhY3Rpb25zLmJsb2NrX3Nsb3QgPCAyODI5MDAwMDAKR1JPVVAgQlkKICAgIHN0YXR1cwo). The majority of Zeta transactions do not go in Jito bundles. When using Jito, the two charts below show that the jito transactions experience an overall lower failure rate.

![post image](/assets/images/76cc26f8cde536ea713c29e0a98736f3.png)

![post image](/assets/images/cd8908cab80f8485974aeb2b1629d0bb.png)

Although utilizing Jito transactions shows a correlative relationship for lower failure rates, it's not clear whether there is a causation with the current data. Noticeably there are still failure rate spikes in the Jito blocks which would be data point outliers that could be explored at a later time.

## Log Message Text Clustering

Agglomerative clustering is chosen for this analysis to group similar log messages together because it excels at identifying natural groupings in data without requiring a predefined number of clusters. This is particularly useful when exploring log messages, where the goal is to uncover patterns or anomalies that might not be immediately apparent from a large selection of verbose log messages.

Two clusters are generated, a failed log cluster and a successful log cluster to provide a more succinct overview of the log messages.

![post image](/assets/images/7c8e2c59a00d52fe3f00979df148bde7.png)

It's an interesting observation that the successful log cluster tends to have a lot more addresses. One hypothesis is that if the transactions are successful, more accounts end up being utilized. In contrast, failed transactions might fail earlier in the process, not utilizing the maximum number of accounts.

![post image](/assets/images/a1970af7e380893ad6881de4d2717990.png)

The raw data from these word clouds can be found here:

log messages in failed transactions

![post image](/assets/images/0ac32d93641ff4f54639a98380a1c341.png)

log messages in successful transactions

![post image](/assets/images/d1accd1a3b80819c93e452b87a6d1ddb.png)
