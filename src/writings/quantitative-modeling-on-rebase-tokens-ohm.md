---
title: "Quantitative Modeling on Rebase Tokens (Ohm)"
date: "2022-01-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://mirror.xyz/evandekim.eth/_6voXoEEfJqy58fNAhQjDWo6K3PvDeCxubfFBC6oAes
source_platform: mirror
slug: quantitative-modeling-on-rebase-tokens-ohm
---

## Introduction

This research was done in an effort to understand what the ideal trading strategy is for tokens with rebase mechanics. The rebase yield is amplified when a protocol is in the early days and has a high rebase rate. The (3,3) vanilla strategy captures 100% of the rebase yield and sets a high benchmark to beat.

Analysis is performed on a 6 month historical data time frame ranging from June 21st - December 14th 2021 and compares a custom built quantitative trading model vs (3,3). The quantitative model utilizes a crossover momentum strategy based on the 15day vs 30day [Crypto Speculation Index (CSI)](https://mirror.xyz/0x829Ceb00fC74bD087b1e50d31ec628a90894cD52/ujJJbOtc25RAGJMewlPahBUcDyozOJaBF7qznEET3ik). 

## Model Setup & Methodology

The quantitative model derives a trading signal based on the crossover between the 15day and 30day CSI line using a time-invariant algorithm that measures the acceleration of the CSI signal. A shorter time frame was chosen over a 30day and 60day strategy so that the trades could be more reactive and capitalize on higher market volatility short term trends in the market. 

Every 5 days, the trading algorithm is used to determine when to trade based on how strong the trading signal is. If the trading signal reaches a certain positive threshold, then a buy order is executed. If the trading signal reaches a certain negative threshold, then a sell order is executed. During the 6 month time period, there are a total of 16 trades made with varying frequency. Interestingly no trades were made in the entire month of November. 

The initial starting position is split evenly between ohm and stables at a total initial portfolio value of ~$1.25m. Stables were assumed to sit idly in a wallet and receive no yield at any time. With an initial starting position of ~1.3m and trade sizes being well within ohm liquidity, variables such as fees, gas, and slippage were not included in this backtest because they would have had negligible impacts on the results. Only ohm price and rebase percentage were used as backtest data, both resampled to daily values. 

The following models tested are - balanced, conservative, aggressive, and vanilla where the models that trade are differentiated only by the swap sizes.

* Balanced uses fixed 10% swap for both buy and sell.
* Conservative uses a 10% swap for buy but 30% for sell.
* Aggressive uses 30% for buy and 10% for sell.
* Vanilla is (3,3) and does not trade.

 

## Results

![Fig 1 - Portfolio Returns](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/618742edb137f7d49a64810f73fc97c17438987037f83058804acd767591672e.png)

Fig 1 - Portfolio Returns

Returns at the end of the backtesting period:

* Balanced = 83m
* Conservative = 68m
* Aggressive = 99m
* Vanilla = 78m

Fig 1 shows a fairly high correlation between all of the strategy returns. This is because they all receive rebase yield to a varying degree and that is the main driver of returns, and not price appreciation. Aggressive performs the best while conservative performs the worst due to the fact that aggressive buys more ohm and maximizes the rebase yield while conservative sits on a larger position of stables. Balanced performs slightly better than buy and hold. This is hypothesized to be due to the fact that it is dipping into the stable position more to accumulate more Ohm, which taps into a higher rebase yield compared to Vanilla.

![Fig 2 - Stablecoin Position Size](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/e1a2a0f43e01f96b9abda0103685f9bb32b8eea779f76683093d7fdf47676994.png)

Fig 2 - Stablecoin Position Size

![Fig 3 - Ohm Position Size](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/f0b9edf09e5c9654a7af3dcb158baa4dc26938c6666c3cb3d581602ea272a7ef.png)

Fig 3 - Ohm Position Size

Unsurprisingly, Conservative has the biggest stable position per Fig 2, quadrupling the stable position from $~600k to over $~2.5m. Consequently this leaves Conservative with the smallest ohm token amount and benefits the least from the rebase yield. Conversely, Aggressive has the most ohm tokens and extinguishes nearly all of the initial stable position over time.

## Conclusion

The biggest takeaway from this research is that the rebase yield sets a very high bar to beat when designing a rebase strategy. The strategies that outperformed Vanilla were the ones that bought more Ohm and thus benefited from receiving a higher rebase. On the other hand, the conservative strategy quadrupled the stable position, which while not a significant percent of the overall portfolio, might make investors feel psychologically safer during periods of higher volatility at the expense of returns.

As Ohm rebase yield continues to depreciate, we should expect to see much more differentiation in the returns profile and less correlation between the strategies as price appreciation starts to account for more of the returns going forward. 

## Code:

<https://colab.research.google.com/drive/1Rf-NYsprb7c2moWWp95TN_ONFNIiAVpI?usp=sharing>
