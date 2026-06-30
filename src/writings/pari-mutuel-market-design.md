---
title: "Pari-Mutuel Market Design"
date: "2022-08-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://mirror.xyz/evandekim.eth/0KZf_XYMCfjgy7fng4nJL_2JOH2k1UOgb_deXoIQg_A
source_platform: mirror
slug: pari-mutuel-market-design
---

I read a paper from 2009 by Agrawal et al titled [“A Unified Framework for Dynamic Pari-Mutuel Information Market Design”](https://arxiv.org/pdf/0902.2429.pdf) and these are my takeaways:

## 1 - Hanson’s Logarithmic Market Scoring Rule (LMSR) AMM designs a truthful, efficient prediction market using pari-mutuel designs.

Pari-mutuel betting is an antiquated term used to describe (modern) prediction markets. However, since Hanson’s LMSR paper came out in 2002, there wasn’t better words to describe the concept of automated market making.

> **Parimutuel betting** (from [French](https://en.wikipedia.org/wiki/French_language) *pari mutuel*, "mutual bet") is a betting system in which all bets of a particular type are placed together in a pool; taxes and the ["house-take" or "vigorish"](https://en.wikipedia.org/wiki/Vigorish) are deducted, and payoff [odds](https://en.wikipedia.org/wiki/Odds#Gambling_odds_versus_probabilities) are calculated by sharing the pool among all winning bets. In some countries it is known as the **Tote** after the [totalisator](https://en.wikipedia.org/wiki/Tote_board), which calculates and displays bets already made. - [Wikipedia](https://en.wikipedia.org/wiki/Parimutuel_betting)

I suspect the term is French because France has a [rich history of analysis](https://famous-mathematicians.com/10-famous-french-mathematicians-and-their-contributions/) (a precursor modern probability theory) - Fermat, Laplace, Legendre, Cauchy, Hermite, Fourier, Poincare. There were too many individuals to keep track of so we just started calling new mathematicians as Bourbaki in the 20th century (a joke!).

## 2 - The truthfulness of Hanson’s LMSR relies on the laws of conditional probability to establish an instantaneous market price.

Truthfulness and conditional probability go hand in hand. Conditional probability is special because it gives a mathematical language to quantify a prior belief. This insight wasn’t learned directly from the paper, but also from reading [Hanson’s LMSR paper](https://mason.gmu.edu/~rhanson/mktscore.pdf) and [Othman’s liquidity sensitive paper.](https://www.cs.cmu.edu/~sandholm/liquidity-sensitive%20automated%20market%20maker.teac.pdf)

## 3 - In general, any market scoring rule has an equivalent cost function formulation.

The fact is attributed to Chen & Pennock [5]. This makes intuitive sense and I felt like I didn’t need further convincing. This fact hints more deeply at idea of duality, a rabbit hole that is easy to go down.

## 4 - Each time a new order arrives, an optimization problem is solved. The state prices are defined to be the optimal dual variables corresponding to the first set of constraints. The trader is charged according to the inner product of the final price and the order filled.

This was a succinct statement. Certainly the inner product as the measure of choice is very important. The concepts of inner products, space duality, and smooth manifolds are always fun to ponder.

## 5 - The Sequential Convex Pari-mutuel Mechanism (SCPM) is a convex optimization model with concave continuous utility function.

> In the SCPM model, the market organizer will typically charge the trader for an accepted number of shares based on the final price calculated by the mechanism. However, in the market scoring rules such as LMSR, the trader is actually charged by a cost function which is equivalent to the integral of the pricing function over the number of shares accepted. Thus, as the price increases while the order is filled, the trader is charged the instantaneous price for each infinitesimally small portion of his order that is filled.

Although SCPM and LMSR appear to have different mechanisms, the paper provides a “unified framework” that offers a classification for these mechanisms. SCPM and LMSR are essentially equivalent.

## 6 - The market maker is implicitly defining a risk attitude with respect to potential revenues obtained from the market when selecting a non-decreasing utility function.

This was a great take from the market maker point of view. If a market maker or liquidity provider wants to change their risk profile, they can select a different non-decreasing, concave utility function. Unfortunately this is easier said than done in the world of DeFi and CFMMs.
