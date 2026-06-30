---
title: "Cross-Chain NFT Marketplace MEV Strategy with Artemis: A Technical Commentary"
date: "2023-05-01"
collection: mev
tags:
  - writing
  - mev
  - mirror
source_url: https://mirror.xyz/0x70b0451b1C047ed750C4661B4624B67FD94A31c5/8yqC4SPzhEqeG5ZyNNIWtlP6oQxi5Nr1oO7wVrF3_w0
source_platform: mirror
slug: cross-chain-nft-marketplace-mev-strategy-with-artemis-a-technical-commentary
---

**"A strategy implementing atomic, cross-market NFT arbitrage between Seaport and Sudoswap. At a high level, we listen to a stream of new seaport orders, and compute whether we can atomically fulfill the order and sell the NFT into a sudoswap pool while making a profit."**

Paradigm recently released [Artemis: An Open-Sourced MEV Bot Framework](https://www.paradigm.xyz/2023/05/artemis) with a cross-market NFT arbitrage strategy implementation included. This is a brief technical commentary focusing on how the initial strategy is setup and how all of the pieces of the library come together.

## Artemis-core

Artemis-core provides a shared codebase in which strategies can be executed on. Artemis-core contains a lot of boilerplate overhead. The boilerplate is split into three folders:

* `collectors` - provides boilerplate for streaming general events for every new block from the blockchain and transactions in the mempool.
* `executors` - contains execution logic to send transactions (strategy `actions`) to the mempool or flashbots relay.
* `utilities` - contains logic to update and maintain the internal state for a given strategy
* `engine.rs` - not a folder, but contains the core logic (aka the engine) of Artemis. `engine.rs` is used to orchestrate the dataflow between the data stream, the internal state, and sending transactions back on-chain for execution.

## Smart Contracts

`strategy.rs` utilizes two smart contracts - `SudoOpenseaArb.sol` and `SudoPairQuoter.sol`.

* `SudoOpenseaArb.sol` contains the `executeArb` and `withdraw`.
* `SudoPairQuoter.sol` contains `getSellQuote` and `getMultipleSellQuotes`. These are both view functions that return the on-chain Sudo pool quote price.

## strategy.rs logic

In the opensea-sudo-arb folder, `strategy.rs` holds the bulk of the code for executing this arbitrage strategy. The logic for the strategy can be broken down into these core async functions:

* `sync_state` gets the on-chain state of all Sudo pools. The list of Sudo pool addresses are retrieved by searching within a block range for all pools deployed. This set of addresses is used to initialize an empty internal state.
* `process_event` updates the internal state with Opensea orders from the API and sudo pool offers. Sudo pool offers are retrieved by using the `view` functions in `SudoPairQuoter.sol`
* `process_order_event` filters out the state space for orders that are not on ethereum, not denominated in eth, and are not profitable. This leaves the only remaining pool addresses as the profitable arb transactions to submit for execution.
* `process_new_block_event` updates the internal state space with new Sudo pools created in the last block and retrieves updated quotes for Sudo pools that have changed price since the last block.

## Conclusion

Paradigm has done the heavy lifting for taking a bot project from 0 to 1. New strategies that are added benefit from `Artemis-core`, which contains a lot of boilerplate code for retrieving blockchain data, building a strategy around the inputs, and executing transactions.

##
