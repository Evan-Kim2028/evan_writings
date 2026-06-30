---
title: "Applying Balancer’s Managed Pool Controllers to Manage Liquidity in Bonding Curves"
date: "2022-12-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://mirror.xyz/evandekim.eth/YPI5RbKi9CyIEgpnrFtmnyACHMtTHM9FBsMJFjdwLXI
source_platform: mirror
slug: applying-balancers-managed-pool-controllers-to-manage-liquidity-in-bonding-curves
---

```
Table of Contents:
  Intro
  Managed Pools (MP)
  MP Controller Design
    Valory’s Smart Managed Pool Off-Chain Controller (SMP)
    Orb’s Managed Pool On-Chain Controller (MPC)
  Canonical Bonding Curves
  MP Controllers for Bonding Curve Liquidity Management
  Optimizing Bonding Curve Liquidity with MP Controllers
    Circuit Breakers
    Add/Remove Tokens
    Dynamic Token Weight and Fee Management
  Conclusion
```

# Intro

Managed pool (MP) controllers can manage liquidity across multiple sources. Managed pools (MPs) are a new type of liquidity pool introduced by Balancer. MP controllers extend the functionality of the MP through automated liquidity management. MP controllers follow a set of predefined rules and conditions and can be built both off-chain or on-chain. Controllers can also manage other sources of liquidity by taking inputs from those sources of liquidity such as a bonding curve. 

# Managed Pools (MP)

Balancer's managed pools (MPs) allow users to construct and manage multi-asset liquidity pools with flexibility. MP functionality includes LP whitelists, the ability to include up to 50 tokens in a pool, and the ability to toggle variable fees. The composition of token weights can be changed dynamically and circuit breaker mechanics can protect against malicious/compromised tokens. However, the flexibility of MPs can also be overwhelming, and additional infrastructure is required for automated liquidity management.

# MP Controller Design

To access the full capabilities of MPs, controllers are being built that extend their functionality. On Ethereum, Valory is building a smart managed pool (SMP) based on their off-chain autonomous agent bot infrastructure, while Orb is building a managed pool controller (MPC) to manage MP state parameters directly on the chain. On Celo, GoodDollar and Symmetric are building an MP controller for bonding curves. These controller designs reflect the flexibility of MPs, and can offer a lot of flexibility for liquidity management, such as implementing trading strategies and managing bonding curves.

### Valory’s Smart Managed Pool Off-Chain Controller (SMP)

Valory is a team that focuses on building open source autonomous applications on distributed ledger technology. Their [Autonolas](https://www.autonolas.network/) application uses the Open Autonomy framework to manage multi-agent services off-chain, extending smart contract functionality and allowing complex operations to be executed in a decentralized, trust-minimized, and transparent way. Autonomous sources can pull data from a variety of sources, such as AWS storage buckets and cryp-native data sources like IPFS, Ceramic, or The Graph. Agents that run services must agree on servicer terms similar to service level agreements (SLAs) and achieve consensus using the tendermint library, which is the same consensus method used by the Cosmos ecosystem. Valory [recently received a Balancer grant](https://medium.com/@BalancerGrants/valory-is-building-smart-managed-pools-on-balancer-1b03a2f4cc89) to extend the current MP structure to include automation via smart managed pools (SMPs), which use autonomous agent software to create robotic MP managers.

![Source for diagram ](/assets/images/3f19ef18e94a8805d40ee1ff00ac06c8d773f4e698275c41e1a0ddafd6b09d4d.png)

Source for diagram

### Orb’s Managed Pool On-Chain Controller (MPC)

Orb Collective, a team spun out from Balancer Labs, is [leading the development and adoption of managed pools and has developed the MP controller V1](https://forum.balancer.fi/t/orb-collective-november-2022-update/4102) with features including the ability to add/remove tokens, an emergency stop, token trading and reweighting, adjusting the MP management fee, transferring manager rights, and updating circuit breakers. The MP state is managed by state parameters under the direction of a controller smart contract. Since the smart contract is the controller, the MP is managed entirely on-chain.

One complex feature that the MP controller V1 provides is the ability to add or remove tokens from an MP without providing initial seed capital. This mechanism relies on arbitrageurs to fill or drain the pool's token balance and restore the MP to its desired composition. While this mechanism usually works, there are some unforeseen negative consequences around token joins and exits. A potential fix has been identified, but it is not yet clear whether it offers a permanent solution to the problem.

When initial token liquidity is being added or removed from an MP, the MP controller has to consider two distinct states. The first state occurs when a token's liquidity weight is going from 0% to the minimum 1% weight. The current mechanism enables trading by using the MP controller to set a virtual balance to get around the initial 0 liquidity weight. A swap fee is then used to incentivize further rebalancing and smooth arbitrage opportunities as the new token is added or removed. The second state occurs when the token is going from the 1% minimum weight to the desired weight. Arbitrageurs are incentivized by a gradual weight shift until the desired weight is reached.

The flexibility of MPs allows for multiple techniques for adding and removing tokens. For example, token replacement could involve trading all of Token A for Token B. Another technique, which involves trust and custody assumptions for the manager, is for the MPC to add Token A, then provide the minimum Token A liquidity denominated in Token A as seed liquidity.

# Canonical Bonding Curves

A canonical bonding curve is a trading function that determines the swap rate between ratios of two different assets, setting the price between the ratio of the assets being traded. The concept was popularized initially [by Bancor](https://drive.google.com/file/d/0B3HPNP-GDn7aLXFWOFpTZEgyaEk/view?resourcekey=0-4Ig-YpDMIC0W2rLmTtWeDA). Bancor's bonding curve uses a constant reserve ratio (CRR) to calculate the price of a bonding curve swap. A higher CRR means there is more supply in liquidity to absorb volatility, while a lower CRR means there is less liquidity and less in circulation, which can be considered as a "credit" compared to the original amount. However, this bonding curve design is [susceptible to sandwich attacks and encourages speculation](https://arxiv.org/pdf/2203.10644.pdf).

An [allocation curve](https://arxiv.org/pdf/2203.10644.pdf) design is a more general bonding curve that improves on the canonical bonding curve sandwich attack flaw. Allocation curves introduce harbinger-like taxes to make token allocation between investors and speculators. The investment efficiency becomes more efficient for investors as opposed to speculators and aims to make token allocation more equitable.

# MP Controllers for Bonding Curve Liquidity Management

Recently, there has been interest in providing controllers for bonding curves to extend DeFi composability and liquidity depth around bonding curve token liquidity. [Carbon](https://resources.carbondefi.xyz/pages/CarbonLitepaper.pdf), created by the Bancor team, manages bonding curve liquidity across multiple bonding curves on-chain using an asymmetric liquidity design. Instead of providing liquidity to a single curve that trades symmetrically in both directions, users provide liquidity to two curves that each trade in one direction. This design gives users greater control to express their trading preferences.

Asymmetric liquidity allows for the creation of individual user strategies composed of two bonding curves, where each curve executes irreversible trades. This gives users the ability to create automated trading strategies composed of one or two on-chain limit or range orders for any given token pair, with each order represented by a unique, adjustable bonding curve.

![post image](/assets/images/a5dd62a3fdc9ee321d11dbd9646238a46a5f0c8d282996877a93cd30514ca032.png)

The specifics of Carbon require Bancor DAO governance approval and are subject to change, with voting occurring via Carbon's proposed governance token, vBNT. Although Bancor governance might make Carbon adoption difficult outside of Bancor, the ideas of asymmetric liquidity are similar to MP liquidity, where the token weight composition is mapped to a range of buying and selling price ranges for tokens within the pool.

# Optimizing Bonding Curve Liquidity with MP Controllers

Unlike Carbon, which only manages multiple bonding curves, the balancer MP controller can be used to work between a bonding curve and a MP. If the MP provides the majority of liquidity for the bonding curve token assets, then controlling the MP directly impacts the liquidity of the bonding curve. The MP acts as a gateway to the bonding curve by increasing the bonding curve liquidity depth and offering more control over the tokens within the bonding curve.

This section examines the connection between MP controllers and bonding curves. We explore design considerations and tradeoffs to adapt a MP controller to incorporate bonding curve state parameters, such as circuit breakers, the ability to add and remove tokens, token weights and fees, and constant reserve ratios.

#### Circuit Breakers

The circuit breaker should only be used in emergency situations, such as highly volatile market movements. The circuit breaker is designed to freeze the system state if it becomes very volatile, such as in the event of a hack that drains a token in the pool or some other catastrophic event. If the CRR between two tokens in a bonding curve reaches an unstable level, the circuit breaker in the MP can be triggered to stop trading. If the MP is the main source of liquidity, enabling the circuit breaker would cause liquidity to freeze and prevent the reserve ratio from deteriorating further. Although the circuit breaker does not solve the issue directly, it provides time to develop a solution to restore the reserve ratio to a more stable level.

#### Add/Remove Tokens

There are many cases where the MP token index needs to be changed, such as when new partner tokens need to be added to the MP or when liquidity migration occurs and old tokens need to be removed. Currently, Orb is researching and developing best practices for adding and removing tokens through the on-chain MPC. For example, a large amount of tokens may need to be transferred from the MP to the bonding curve to adjust the reserve ratio. Depending on the blockchain, if there is not sufficient MEV protection, this type of token transaction between the MP and bonding curve reserve may be vulnerable to sandwich attacks. Sandwich attacks can frontrun these transactions if there is information leakage that MEV bots can exploit.

#### Dynamic Token Weight and Fee Management

Finally, the dynamic token weight management is a more general controller feature that enforces on the monetary policy set by the controller. There is flexibility to automate token weight management around desired reserve ratios or other economic conditions that a DAO sees fit by modifying the controller. 

Although the canonical bonding curve usually has fee mechanisms in place, if the MP holds the majority of liquid tokens from the bonding curve, the MP swap fees could act as a fee collector for the bonding curve if they are added to the bonding curve periodically over time.

By creating a dynamic fee policy for the MP controller, this also creates a dynamic fee policy for the bonding curve.

# Conclusion

In conclusion, managed pool (MP) controllers are an essential extension of MP functionality that enables automated liquidity management. Balancer MP controllers provide a new framework to manage liquidity across multiple sources. The MP controller framework can be used to manage liquidity within bonding curves. Leveraging Balancer MPs offers more granular control over the bonding curve and increases liquidity depth for the bonding curve tokens.
