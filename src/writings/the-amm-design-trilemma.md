---
title: "The AMM Design Trilemma"
date: "2022-08-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://mirror.xyz/evandekim.eth/SVp-wan8A0VtZVff8YgUKTQAhJlpKa4CPXNVKqW_d5o
source_platform: mirror
slug: the-amm-design-trilemma
---

Recently I have been on a quest to understand AMM’s from a historical context (pre-DeFi). This 2013 paper by [Othman et al titled “A Practical Liquidity-Sensitive Automated Market Maker”](https://www.cs.cmu.edu/~sandholm/liquidity-sensitive%20automated%20market%20maker.teac.pdf) takes an axiomatic approach to unify AMM designs by characterizing AMMs by three properties - path independence, translation invariance, and liquidity sensitivity.

## 1 - Three properties to characterize AMMs - path independence, translation invariance, and liquidity sensitivity

### Path Independence

> Path independence means that market state transitions remain the same for trader costs and payments in aggregate. From a trader's point of view, it does not matter whether the trader makes one large trade or executes smaller sequential trades. From a probabilistic point of view, this ensures that the conditional probability of outcomes throughout time remains independent.

Path independence was formulated initially from a probabilistic point of view to design more efficient prediction markets. Hanson's logarithmic market scoring rule (LMSR) is the literature's earliest path independent AMM design.

### Translation Invariance

> Translation invariance refers to the cost of a payout to an LP for market making. Translation invariance guarantees that the spreads shrink to zero, leaving no upside for the LP to capture from greater spreads.

Thus a translation invariant pricing rule means that the LP will take a loss as long as the ﬁnal market prices diverge from initial market prices.

**How this is related to the concept of impermanent loss in CFMMs?** I couldn’t find a direct bridge to any literature. The closest thing I could find was Angeris et al describing the CFMM LP “portfolio value function” (payoff to LPs) as concave [in this paper](https://angeris.github.io/papers/cfmm-monotone.pdf). Angeris et al also talk about arbitrage earnings. Aribtrageurs and LPs seem to be at odds with each other - either the arbitrageur profits or the LP profits. **Is there a world where this can exist as a non-zero sum outcome?**

The first thing I think about for translation invariance are the parallels to [translation vectors in an affine space](https://en.wikipedia.org/wiki/Affine_space) (or invariant curves in an affine variety). Intuitively this suggests to me that the space of CFMM liquidity curves can be characterized as invariant curves in a reproducing kernel hilbert space (RKHS).

### Liquidity Sensitivity

The price of an asset changes based on market activity volume. An AMM is liquidity insensitive if the asset price is not dependent on volatility. Uni v2 and Uni v3 designs are liquidity insensitive at the base layer, but liquidity sensitivity can be built at a higher level by active liquidity management solutions. In contrast, Curve v2 has a dynamic fee based on volatility so it is liquidity sensitive.

## 2 - AMM’s can only have 2 of the 3 properties - the AMM trilemma

> THEOREM 2.9. No pricing rule is translation invariant, path independent, and liquidity sensitive. - [Othman et al (2013)](https://www.cs.cmu.edu/~sandholm/liquidity-sensitive%20automated%20market%20maker.teac.pdf)

The argument is roughly as follows. First construct Hanson’s AMM, the LMSR. Then verify that it is path independent, translation invariant and show that it is not liquidity sensitive.

## 3 - The AMM trilemma is not binary - it is a spectrum of choice

The authors use an axiomatic approach to construct a liquidity sensitive AMM, a modified LMSR that trades the translation invariance property in favor of liquidity sensitivity. However, they do this by relaxing the translation invariance property, not removing it. This implies to me that the AMM trilema is not binary - it is a spectrum of choice.

**Is the existence of impermanent loss based on the path independent nature of CFMMs?** But wait are CFMMs even path independent? In the absence of fees, CFMMs are path independent. This is why the [Loss vs Rebalancing (LVR)](https://moallemi.com/ciamac/papers/lvr-2022.pdf) and [LP CFMM returns](https://arxiv.org/pdf/2006.08806.pdf) papers assume no fees to derive their results.

> A question left open by this paper concerns fees. In practice, most G3Ms charge fees that introduce path dependencies in LP share payoffs. As fees may alter both the frequency and the cost of CFMM rebalancing, it may be instructive to consider the corresponding constant-mix portfolio under rebalancing restrictions and transaction costs. - [Alex Evans, LP CFMM Returns paper](https://arxiv.org/pdf/2006.08806.pdf)

Authors Tarun and Guillermo also talk about path independence/dependence of CFMMs with fees in the [Improved Price Oracles paper](https://arxiv.org/pdf/2003.10001.pdf) as a “path deficiency”.

Perhaps a more accurate way to characterize the path of a CFMM is that there are **two components - a path independent and a path dependent part (scalar constant when the fee is fixed)**.
