---
title: "Crypto Speculation Index (CSI)"
date: "2022-01-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://mirror.xyz/evandekim.eth/ujJJbOtc25RAGJMewlPahBUcDyozOJaBF7qznEET3ik
source_platform: mirror
slug: crypto-speculation-index-csi
---

## Overview of CFGI

The goal of [CFGI](https://alternative.me/crypto/fear-and-greed-index/) attempts to quantify buying and selling opportunities based on the overall fear and greediness of the market and tries to predict when market corrections will occur and when buying opportunities present themselves.

CFGI gathers data from five sources - Volatility (25%), Market Momentum/Volume (25%), Social Media (15%), Dominance (10%), and Trends (10%).Why those weights specifically?

## Overview of CSI (CFGI 2.0)

CSI aims to generalize levels of fear and greed to levels of speculation. Positive speculation implies more greed. Less speculation implies a choppy (equilibrium) market condition. Negative speculation implies fear. CSI consolidates categories down from five to two - Momentum and Stablecoin Dominance, both of which are calculated by measuring the acceleration of the change of the indicators. 

CSI uses daily data and has both a 30 day and 90 day signal converted to a percentile scale from 0% to 100% for easier understanding. Below are the last  5 days worth of values from the signals in ascending order. Values below ~50% are negative while values above 50% are positive. 

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/0a9d3439fe343e8ecc30cb9c91208bb33e19458c3eddde92d718a969cd516ccd.png)

The charts below show cumulative levels of speculation accrued in the system throughout the year. These charts show the raw data that the CSI is calculated from and is not in a percentile scale. Interestingly, levels of speculation are overall lower at the beginning 2022 compared to the beginning of 2021. 

The 30day chart shows that there were 3 bull markets and 3 bear markets, characterized by the peaks/valleys of the chart. The 90day chart doesn’t have this much granularity but still captures the trend as 2 major bull cycles and 1 major bear market, with a potential second bear market approaching if current market conditions persist.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/b942dbc19a1c00fa27344ef5c2be365b06042d2bea40054605a5556c3b83acf6.png)

By having multiple signal time frames, we can identify turning points in the market. For example when the 30 day flips the 90 day in the chart below for an extended period of time, say a week, that provides a high level of confidence that a macro trend reversal is occurring. This can be further expanded to include 5 vs 15, 15 vs 30, 30 vs 60, etc to identify turning points along multiple short term and long term time frames.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/a00fbf2811dd338f368715ee6859d720abefc2c6468adcf5156941fb6d06d67a.png)

## Reasoning behind changes:

* Volatility + Market Momentum/Volume categories were replaced with a single Momentum category. Momentum is calculated using a time-invariant “momentum” algorithm on bitcoin and Ethereum market caps. Market caps were used because this takes into account the asset bubble price appreciations that occur during highly speculative markets. Ethereum is included in CSI to account for speculation occurring in the NFT market, of which virtually all assets are primarily denominated in Eth.
* Dominance is replaced by Stablecoin Dominance, which expands the original definition to account for more speculative assets. Stablecoin Dominance is a ratio between the market cap fluctuations of the largest stablecoins vs the market cap fluctuations between bitcoin and Ethereum market caps. As Stablecoin Dominance increases, more people are going from speculative assets into stablecoins, thus decreasing levels of speculation. As Stablecoin Dominance decreases, people are decreasing their stablecoin positions to invest in more speculative assets. Stablecoins that are used are USDC, USDT, BUSD, DAI, FEI, FRAX, LUSD, MIM, and UST.
* Social Media and Trends were stripped out due to the unquantifiable amount of biased noise that they bring to the model. See [here](https://cdn.cms-twdigitalassets.com/content/dam/blog-twitter/official/en_us/company/2021/rml/Algorithmic-Amplification-of-Politics-on-Twitter.pdf) and [here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8186442/) for expanded reasoning. More is not always better.

 

## Code

**<https://colab.research.google.com/drive/1R-L293PPtQvRSeNFLCtONvEj-ND-Q43t#scrollTo=BQeTHMTozpaP>**
