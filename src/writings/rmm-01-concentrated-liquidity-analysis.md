---
title: "RMM-01 Concentrated Liquidity Analysis"
date: "2022-07-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://primitive.mirror.xyz/wXPmtmaO4yvhyra36XKqwX36gM0qmR0X3YNTOBZB5Kk
source_platform: mirror
slug: rmm-01-concentrated-liquidity-analysis
---

### Introduction

Liquidity providers (LPs) can use the Primitive RMM-01 protocol to create portfolios that express directional views with respect to asset prices. Setting an out of the money (OTM) strike implies an expectation of positive market movement while setting an in the money (ITM) strike implies expectation of negative market movement. Implied volatility (IV) and time to maturity parameters describe the dynamic behavior of concentrated liquidity. 

The key insight is that the directional view that LPs derive from their parameter selections can be used to provide dynamic concentrated liquidity adapted to market conditions. In contrast, Uniswap LPs cannot specify a market direction due to the symmetric behavior of the pricing function. While RMM-01 pools have dynamic concentrated liquidity based on the initial Black-Scholes parameter selection, Uniswap V3 concentrated liquidity is static and does not adjust to changing market conditions.

This article analyzes the performance for a recent ETH/USDC pool created on July 5, 2022 and expired July 10, 2022. Pool profitability hinges on setting parameters that accurately describe the direction and behavior of the market. The efficacy of dynamically concentrated liquidity distributions are analyzed by the statistical kernel density estimate (KDE) tool. Code can be found [in this jupyter notebook](https://github.com/primitivefinance/pool-analytics/blob/main/RMM_Swaps_Stats_v3.ipynb), and can be easily modified to analyze any other RMM-01 pool.

### Pool Parameters

The parameters set by a recently expired ETH/USDC pool were defined as:

Strike price: 1255 USDC

Implied volatility: 77%

Time to maturity: 5 days

Initial reported price: 1107 USDC

By selecting a 1255 USDC strike price, which is higher than the initial reported price, we can discern that the liquidity was provided to this pool with the expectation of a positive price movement.  Setting the IV and time to maturity parameters tell the Black-Scholes equation how much volatility should be priced in and what the underlying volatility of the pool composition will be. Ideally, a pool composition that oscillates around a 50/50 split is the best outcome and is the most effective if liquidity can be dynamically concentrated around this split. 

### Directional LP Performance

We compared performance to a static portfolio equal to the composition of pooled assets at creation. While the static portfolio appreciated 12.249%, the RMM-01 replicating portfolio appreciated 12.596%, outperforming the static portfolio by over .3% as shown in the below chart. Unlike Uniswap pools, there is no impermanent loss from the upside gains of specifying an accurate liquidity direction on RMM-01.

![Static Portfolio vs RMM-01 Porftolio absolute returns](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/6e2e21399207fe5af4d476e915efabb0dab3a520c515da3c589b0962a209fdda.png)

Static Portfolio vs RMM-01 Porftolio absolute returns

We calculated realized volatility based on the ETH reported price in the chart below. The first half of the pool duration had an average volatility of 79% and swap volume of 541,472 USDC. In the second half, average volatility fell to 18% while swap volume increased to 783,097 USDC. Realized volatility followed IV more closely in the first half compared to the second half.

![Real Volatility vs IV](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/8146182bba467610c72032e18765527751d0e0b91e58d34a9a9d4907acb6c562.png)

Real Volatility vs IV

There were a total of 44 swaps routed through the pool that accounted for a total swap volume of 1,324,570 USDC. Total swap fees collected were 6,224 USDC and 5.8594 ETH for a total value of 13,548 USDC. Swaps on this pool represent 36% of all time swap volume and 12.6% of total swaps across all RMM-01 pools. Comparing volume with IV, more swap volume occurred when realized volatility was lower than IV. This means that the liquidity depth from the concentrated liquidity was thicker at the end of the pool than at the beginning because it facilitated more swap volume with less realized volatility, but less dynamic because the IV parameter didn’t accurately describe realized volatility.

The chart below shows how the replicating portfolio composition shifted from the original 690 ETH and 79,623 USDC to 756 ETH and 41.83 USDC. Although the pool composition shifted almost entirely to ETH, since the payoff function is being replicated by Black-Scholes, the riskiness of the different pool compositions remains the same.

![IV, real volatility vs swap volume](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/ebd74bf564ce3d3532a9072c658c2d594ead6e51e748d5ce2d849fd1f31138cd.png)

IV, real volatility vs swap volume

As the reported price converged towards the strike price, the replicating portfolio composition approached a 50/50 split. However, the reported price ultimately did not end above the strike price, so the replicating portfolio composition shifted towards nearly 100% ETH. If the reported price had ended above the strike price, the replicating portfolio composition would have shifted towards 100% USDC.

![Replicating Portfolio Portfolio Composition](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/e913ba6b23a9a601c2a09b7d789d1fd1870b46b5560f973137fc207aee1485cc.png)

Replicating Portfolio Portfolio Composition

### Analysis of Dynamically Concentrated Liquidity Distributions

To measure dynamically concentrated liquidity, we use a KDE to estimate various liquidity distributions and illustrate how liquidity dynamically concentrates over time. By observing the peaks in the chart below, we can see that liquidity was most concentrated when the pool was composed of 15% USDC and 80% ETH. There was not a large overlap where ETH/USDC reserves oscillated around 50/50. This implies liquidity could have been better dynamically concentrated.

![Reserve Liquidity Distributions](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/f477c9f6223773999f45b92309059af3e793c4c4c1752647fff9bb863a299422.png)

Reserve Liquidity Distributions

Creating another KDE on the swap distributions, we can see that swapping USDC to ETH had a very tight range compared to swapping ETH to USDC. If the terminal-reported price ended above the strike price, the portfolio composition would have become more USDC heavy, allowing a larger dynamic range for the USDC liquidity to be deployed. 

![Liquidity Depth Distributions](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/2cb8e845227519682cf0b7139eed07ebb42d5c5145773e31a69cd487edc3373f.png)

Liquidity Depth Distributions

The liquidity efficiency measures the percent of the portfolio reserve used for market making. ETH to USDC swaps saw levels of usage around 5% of USDC reserves. USDC to ETH had a much larger usage, around 10-20% of ETH reserves. This means that liquidity was more dynamically concentrated around ETH reserves.

![Dynamic Reserve Liquidity Utilization](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/084272a8c0119a15eff34e4a119e74637c7120187142debab30e89230e205010.png)

Dynamic Reserve Liquidity Utilization

### Conclusion

In conclusion, we visually analyzed how this RMM-01 pool behaved. We saw how RMM-01 pools could be used for directional LPing and analyzed the results of having dynamically concentrated liquidity distributions. This pool was initialized with parameters that roughly predicted the direction of the market. However, the implied volatility parameter caused looser concentrated liquidity ranges, decreasing the efficacy of the dynamically concentrated liquidity. Further research will explore optimization of the IV parameter behavior on liquidity depth and the effect dynamically concentrated liquidity has on concentrated liquidity bounds in general.
