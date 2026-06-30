---
title: "Liquidity Management and Supply Issuance Optimization Model"
date: "2022-04-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://mirror.xyz/evandekim.eth/Q2tdbKQjTyrSixC4YaElqr83zJE0gUIOIzltxFa-VIQ
source_platform: mirror
slug: liquidity-management-and-supply-issuance-optimization-model
---

**This paper extends the results of** **[DeFi Liquidity Management via Optimal Control](https://people.eecs.berkeley.edu/~ksk/files/Ohm_Liquidity_Management.pdf)** **(Tarun, Kshitij, Guillermo, Alex, Victor) by optimizing liquidity management and supply issuance via bonding and staking. The result is increased capital efficiency of bond supply issuance, decreased risk by minimizing price volatility, and sustainable long term supply emissions growth. By implementing this liquidity management model in practice, this will add an additional layer of risk management and capital efficiency to POL (protocol owned liquidity)  assets and increase decentralized exchange volume.**

## History of Liquidity Management

Given the recent explosion of financial innovation in DeFi (decentralized finance) and the broader decentralized web3 movement, a novel way to obtain liquidity has been through the rise of decentralized exchanges using constant functions such as xy=k to create liquid markets for web3 native assets. Although this opens up a decentralized, permissionless way to provide liquidity, centralized exchanges currently dominate volume with more than 5x the amount of monthly volume compared to decentralized exchanges. 

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/0ae4af632f97fd74d9654d8a5897b5da100f23ef3c14cfec7f03e5c9c5a246bf.png)

The economic reason for this is simple - it is not very profitable to be a LP (liquidity provider) on a decentralized exchange. For example the majority of LPs in Uniswap v3 [underperform non-LPs](https://arxiv.org/abs/2111.09192) due to IL (impermanent loss) and it is simply better to hold tokens passively than to provide liquidity. 

One solution that protocols used to incentivize LP was to provide liquidity mining rewards. In return for providing liquidity, LPs would be entitled to a bonus APY. Although liquidity mining attracted more liquidity, it turned out to be very dilutive for the token needing liquidity. This resulted in mercenary LPs hopping between pools of liquidity for new projects to farm these token rewards and dump immediately to lock in profits, which made attracting liquidity temporary and expensive. 

In late 2021, Olympus popularized a bonding model in which bonders would exchange OHM liquidity tokens for a OHM premium, based on an inflation schedule. Bonders could then stake their OHM and receive additional rewards from future OHM bonders. This was successful in attracting up to hundreds of millions in POL. Since the protocol became the primary LP, this eliminated the need to attract mercenary LPs via dilutive liquidity mining rewards. Unfortunately this model fell apart because it didn’t account for the fact that staking OHM did not lock OHM up, resulting in high levels of dilution into the liquidity pool when the staking rate dropped. Even a 10% drop from [90% to 80% supply staked](https://dune.xyz/queries/277250/523233) resulted in a significant amount of dilutive price pressure on OHM. 

The [recent paper posed liquidity management as a control theory problem](https://people.eecs.berkeley.edu/~ksk/files/Ohm_Liquidity_Management.pdf) and used Olympus as a case study. The theoretical result showed that by increasing the number of bonds offered and their durations, optimal parameter tuning could lead to price stability between issuing bonds and managing liquidity thus increasing capital efficiency by minimizing price volatility. The idea is that by targeting a certain amount of locked supply with variable bond durations, the bond model that Olympus uses would be able to obtain both liquidity management and price stability.

## Liquidity Management and Supply Issuance Model

This paper outlines the framework for an  off-chain algorithm to manage liquidity and supply issuance. By converging to the ideal economic state, this implies a convergence towards minimum price volatility as well. 

In order to construct an optimization algorithm for supply issuance, we define a set of ideal parameters that describe an ideal economic state with minimum price volatility. Then we monitor the economic state of the protocol and adjust supply issuance dynamically with respect to variable market conditions.

This model tracks three parameters - lock rate, growth rate, and lp rate where lp growth rate is the inverse of the lock rate. The growth rate is set at 2x the current circulating supply. The lock rate is set at 90% of circulating supply. The lp rate is set at 1 - lock rate which is 10% of circulating supply. Although these parameters are fixed to make the simulation more straightforward, note that it is not difficult to change these parameters over time either through dynamic or manual intervention. 

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/d61f67bcdc45f8f2b9268b975e6a5b371e57c504a02148a2f0c02e298561b80a.png)

The current state represents the current market behavior at a specific time. The closer the current state looks with respect to the expected state, the more optimized the economic state is. Notice that the use of this model creates a dynamic supply curve and a dynamic bond curve, which is reactive to market volatility.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/ab903f36b23467725d0c0ee680456dda11fd4308748511ca4ed1186bb912336a.png)

Finally there is a transition state which represents the difference between the expected state and the current state. A random variable is chosen from a gaussian distribution to simulate volatility from market behavior.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/9b4906b34e584b6965c740b926e22415bda0c7e17cab70bb1d0c6002f20b79c1.png)

As the volatility of the transition state decreases over time, the closer we get to the ideal economic state. This can be more closely monitored by how far off the expected and current lock and lp rates are throughout the simulation. 

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/ee94abb3d0088caaa69352e88c2930345ee7478df02f41a8d5e84828e944b19f.png)

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/2d06e068d8afcc64a5c9e0cf1d2d943978d7fdfa014248e2fe85195bca2ff825.png)

## Conclusion

Using the theoretical framework for liquidity management via control theory, we can construct an off chain optimization algorithm that adjusts parameter weights based on changing market conditions to reach a desired level of expected price stability over the long run. Future work involves using this model in production, adding variable lockup/unlock periods, adding anticipated supply unlocks into projected issuance, and performing monte carlo simulations. Additional future work also includes code refactorization and building an [open source library](https://mirror.xyz/0x829Ceb00fC74bD087b1e50d31ec628a90894cD52/1ZwO757VjK9M0Gt-1JiQbXoIz4FZw5AHnuGXpQl-jV4) that provides a framework to create and build and test models robustly thus increasing the pace of innovation in DeFi.

## Sources

* [Cex vs Dex Trading Volume via theblock](https://www.theblockcrypto.com/data/decentralized-finance/dex-non-custodial/dex-to-cex-spot-trade-volume)
* [Locked Supply Optimization Algorithm Model](https://colab.research.google.com/drive/1X9v6Rf1aK6kC6YVFVZMXIv0_sSo_PK6C?usp=sharing#scrollTo=KlPmHoTiKosi)
* [DeFi Liquidity Management via Control Theory](https://people.eecs.berkeley.edu/~ksk/files/Ohm_Liquidity_Management.pdf)
* [DeFi Primitive Risk Methodology (DPRM)](https://mirror.xyz/0x829Ceb00fC74bD087b1e50d31ec628a90894cD52/1ZwO757VjK9M0Gt-1JiQbXoIz4FZw5AHnuGXpQl-jV4)
