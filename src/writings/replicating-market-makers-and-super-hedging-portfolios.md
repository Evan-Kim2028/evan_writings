---
title: "Replicating Market Makers and Super Hedging Portfolios"
date: "2022-05-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://mirror.xyz/evandekim.eth/aUULTZFwhJ9XsOZ6XIbAYl1iaSncDKpDwKazCemJlI8
source_platform: mirror
slug: replicating-market-makers-and-super-hedging-portfolios
---

## What is a Replicating Market Maker?

Decentralized exchanges (DEXs) have fueled immense growth and activity on the Ethereum blockchain, trading over [1 trillion USD in volume in 2021](https://www.theblockcrypto.com/linked/128500/decentralized-exchanges-saw-over-1-trillion-in-trading-volume-this-year#:~:text=Decentralized%20exchanges%20(DEXs)%20reported%20more,%24115%20billion%20in%20trading%20volumes.). **Constant function market makers (CFMM)** such as Uniswap are the most widely used DEX designs and offer permissionless ways for users to provide liquidity and trade tokens. CFMMs allow investors to permissionlessly construct short gamma portfolios and provide liquidity for a spot market for these portfolio positions.

**Replicating Market Makers (RMMs)** extends the DEX design space even further, allowing for the creation of permissionless liquid derivatives. Formulated by Angeris et al. [[Replicating Market Makers, March 2021]](https://arxiv.org/abs/2103.14769), an RMM is a more general type of CFMM that can replicate different financial derivative payoffs. RMM liquidity pools act as spot price markets for derivatives and do not rely on external oracles, eliminating oracle manipulation attack vectors.

Using convex analysis, Angeris et al. [[Replicating Monotonic Payoffs Without Oracles, September 2021]](https://arxiv.org/abs/2111.13740) provide a general method to construct various derivatives. Estelle et al. [[Primitive RMM-01, October 2021]](https://primitive.xyz/whitepaper-rmm-01.pdf) showed the first implementation on the Ethereum mainnet, replicating the Black Scholes price of a European covered call. Estelle et al. [[Replicating Portfolios: Constructing Permissionless Derivatives, May 2022]](https://arxiv.org/abs/2205.09890) then derived more theoretical results, expanding the arsenal of possible derivative implementations to binary options, cash or nothing calls, straddles, and liquidation free lending.

![post image](/assets/images/67534b37f8c02c95a92993758660a3b0c0c29a1fc51d98692eac682fc1b30023.png)

## Replicating Portfolios

A **replicating portfolio** for a given asset or series of cash flows is a portfolio of assets with the same financial properties like cash flows. There are two types of replication - static and dynamic. **Static** **replicating** portfolios have the same cash flows as the reference asset and require no rebalancing. Since CFMMs use constant functions for liquidity, CFMMs are examples of static replicating portfolios.

**Dynamic** **replicating** portfolios do not have the same cash flows, but have the same option “Greeks” as the reference asset and require continual rebalancing. RMM-01 is an example of a dynamic replicating portfolio and requires continual rebalancing to replicate the payoff of the covered call payoff.

A **self-financing portfolio** is a type of replicating portfolio that contains long and short investments such that the sum of their investment weights, or net investment, is zero. This contrasts with a standard portfolio that has investment weights summing to one. Examples of self-financing portfolios are hedges, overlays, arbitrage portfolios, swaps, and long/short portfolios. Both CFMMs and RMMs are incomplete self-financing dynamically replicating portfolios. The key here is that the combination of any CFMMs will never form a self-financing replicating portfolio whereas it is theoretically possible to create one using RMMs by super hedging. **Super hedging** is a risk management strategy that hedges positions in a self-financing portfolio. In theory, super hedged portfolios remain profitable regardless of the market's ups and downs. In a complete market, which assumes negligible transaction costs and perfect information (completely rational), super hedging is equivalent to hedging. In practice, however, markets are incomplete and investors rationality is bounded.

![post image](/assets/images/6ef5a714b11901efc28cbde8bdb243187c7b8f82008c88a1ad07d718ed7fd4db.png)
