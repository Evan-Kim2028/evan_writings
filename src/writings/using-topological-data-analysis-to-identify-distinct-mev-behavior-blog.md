---
title: "Using Topological Data Analysis to Identify Distinct MEV Behavior (blog)"
date: "2022-11-01"
collection: mev
tags:
  - writing
  - mev
  - mirror
source_url: https://mirror.xyz/evandekim.eth/Xb8XRL7nD-ORyeX76nrG6eOiTYOMTmKfOxEfMEpBae0
source_platform: mirror
slug: using-topological-data-analysis-to-identify-distinct-mev-behavior-blog
---

```
1 - Introduction
2 - Mapper Algorithm
3 - Six Distinct MEV Behaviors
4 - Conclusion
```

### 1 - Introduction

Topological data analysis (TDA) is a powerful data analytics technique that uses the underlying topological and geometric structures of data to create non-trivial, meaningful categories. The Mapper algorithm is a TDA tool that transforms data, which lives in a continuous Reeb space, to a simplicial complex, a topological combinatorial graph which lives in a discrete space. TDA started to turn heads when the Mapper algorithm was used to identify a highly treatable cluster of breast cancer patients from a highly dimensional dataset in 2011.

Although the TDA technique persistent homology has been applied to study some financial asset bubbles, this is the first application of Mapper to MEV and blockchain in general. We review the results in this post, leaving technical details out. A full paper [draft is available on github.](https://github.com/Evan-Kim2028/tda_ohm_analysis/blob/main/Using_Topological_Data_Analysis_to_Identify_MEV_Behavior.pdf)

Previously we created a [MEV dataset](https://mirror.xyz/evandekim.eth/Mc11J16dVP7Ervk1r2Sx_wkJ7dzb7Ce60Y2EpbRBlHY) that contains historical MEV trading data from Olympus Sushiswap POL. In this new research, we add multi-chain liquidation events from Ethereum based Rari and Arbitrum based Vesta obtained via [Playground Analytics Subgrounds](https://github.com/Protean-Labs/subgrounds).

### 2 - Mapper Algorithm

Simply put, the Mapper algorithm is the transformation from a continuous subspace of data to a discrete graph with topological data embedded combinatorially. Mapper algorithm inputs a point cloud of on-chain historical data as shown in Figure 1 and outputs a simplicial complex, as seen in Figure 2.

![Figure 1 -Historical Cumulative Stats](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/95a7bb02a793417cdb2a5879ec9eed45aad08fd10202d6bba668e52718b867c4.png)

Figure 1 -Historical Cumulative Stats

![Figure 2 - Simplicial Complex from Mapper colored by MEV volume](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/ab97690aea8147d126a6f7fadba453789ad412482a48b6d342427f7f3b58d42e.png)

Figure 2 - Simplicial Complex from Mapper colored by MEV volume

### 3 - Six Distinct MEV Behaviors

Intuitively, these distinct MEV behaviors can be considered as MEV emotions. For example the emotions happiness and excitement are both distinct, but positive emotions. In contrast, happiness and despair are contrasting emotions - positive and negative. Emotions that are closer in similarity will also appear closer together as seen in Figure 4.

Figure 3 shows six statistically distinct MEV behaviors where node 0 is called the “base node” and represents the default MEV behavior.

![Figure 3 - Six Statistically Distinct MEV Behaviors ](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/4f66dac5bb562ff792329b3e3bab862720c623e877119966d5114780787c5f66.png)

Figure 3 - Six Statistically Distinct MEV Behaviors

Nodes 1,2, and 3 all have positive MEV mean volume. Positive MEV volume should be considered a desirable MEV behavior because it implies MEV bots are buying OHM and pushing the price up. Indeed Nodes 1,2, and 3 show that the positive MEV volume is counteracting the negative non-MEV volume.

Nodes 4 and 5 are more troublesome. They have very large negative MEV mean volumes. Fortunately they appear to be outlier MEV behaviors because they account for a small amount of data points, a mere 10. Node 4 has the largest mean and standard deviations for liquidations, indicating negatively volatile days due to liquidations.

In contrast, node 5’s negative MEV volume is more correlated with negative non-MEV volume as opposed to liquidations which indicates in general, a lot of negative selling during those days, but not directly a result of OHM liquidations.

![Figure 4 - Geometric Visual Intepretation of the Mapper Algorithm Results](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/19d7f27edf195d6d0f5a1ae3ffe02e38c21deba21564ddecf2c0cae608f0ae3e.png)

Figure 4 - Geometric Visual Intepretation of the Mapper Algorithm Results

Figure 4 shows how the Figure 3 statistical properties of each behavior are visually represented. Looking at 2(b) Daily MEV vs non-MEV Volume scatterplot, each cluster of node points exists within a distinct area. The 2(b) Daily MEV vs Liquidation Volume chart shows similar geometric separation, but appears more cluttered. These geometric distinctions create new ways to categorize heavily connected DeFi data and allows a distinct classification of MEV behavior based on daily data as well as offering a rich area of research to further understand how to incentivize more positive MEV behaviors such as Nodes 1, 2 and 3 and avoid negative behaviors such as Nodes 4 and 5.

### 4 - Conclusion

In conclusion, we have identified six distinct MEV behaviors that exist within the OHM MEV dataset. These behaviors can be thought of as MEV emotions that react to economic incentives within the blockchain multiverse. This is the first application of the Mapper algorithm to MEV data and blockchain data in general. Data is all fully available on-chain and [source code is freely available](https://github.com/Evan-Kim2028/tda_ohm_analysis).
