---
title: "Terminal-Bench Task: Lakehouse Schema Contract Drift"
date: "2026-09-10"
collection: latest
description: "A Terminal Bench Task Counterexample"
tags:
  - writing
  - latest
  - data
  - evals
  - coding-agents
  - terminal-bench
  - iceberg
source_url: https://github.com/Evan-Kim2028/eval_tasks
source_platform: github
slug: terminal-bench-task-lakehouse-schema-contract-drift
series: Evals
series_index: 1
---

![A field of arrows pulling one way, a single green contract line pointing the other, and an agent trajectory that bends toward the contract then falls back](/assets/images/lakehouse-priors-hero.png)

## Research Question - Learned Conventions as behavioral priors

**When a local specification conflicts with a strongly learned convention, which signal controls a coding agent's behavior?**

Coding agents develop strong expectations about how familiar software systems behave. Training data contains repeated implementations, documentation, examples, and conventions that allow models to recognize common structures and apply familiar solutions quickly. These learned conventions function as behavioral priors. When an agent encounters a recognizable system, the prior can provide a useful starting point for reasoning about the task. 

The same mechanism can create failure modes when the local specification changes a rule that the familiar convention normally determines. A useful evaluation should therefore create exactly this conflict and measure whether the agent follows the local contract.

## Terminal-Bench Counterexample: Lakehouse Schema Contract Drift

The lakehouse task, which I designed and [can find here](https://github.com/Evan-Kim2028/eval_tasks), introduces a deliberate **schema contract drift**. The surrounding system follows familiar lakehouse patterns. However the schema semantics diverge from relevant Iceberg convention, using numeric field IDs but assign a fresh, disjoint ID set to every schema epoch.

Each schema epoch receives a fresh set of numeric field IDs. The ID sets for different epochs must remain disjoint. A schema attached to a commit represents the schema for that particular epoch rather than a globally stable column identity.

The environment therefore presents a recognizable lakehouse problem while changing one of the assumptions that an agent may carry into that environment.

![Schema contract drift: Iceberg convention vs task contract](/assets/images/lakehouse-priors-fig1-schema-drift.png)


The task documentation states the fresh-ID requirement explicitly. The hidden verifier checks whether the implementation preserves that requirement across schema readers, peer publishing, and composed recovery.

This creates a narrow semantic difference inside an otherwise recognizable system. The experiment can therefore isolate three layers of the phenomenon:

1. **Research phenomenon:** learned priors influencing behavior under conflicting specifications.  
2. **Experimental mechanism:** schema contract drift.  
3. **Specific counterexample:** fresh, disjoint field IDs across schema epochs instead of stable field IDs across schema evolution.

The expected failure mode is straightforward: the agent recognizes a familiar lakehouse pattern, applies the associated schema convention, and fails to account for the local rule governing schema epochs.

### Evaluation Verification Design

This design gave the verifier a simple invariant to check while allowing the task itself to remain complex. The primary checks test whether different schema epochs receive disjoint field-ID sets. Additional tests propagate those identities through peer reconstruction and composed recovery, where the final catalog must match the serial reference state.

A correct implementation must follow the local schema contract. An implementation that imports the stable-ID convention will produce overlapping identities and eventually diverge from the reference recovery state.

The oracle score was 1.0, confirming that the task has a valid solution. The adversarial and cheat trials also received 0, providing additional evidence that the observed failure came from the agent's implementation behavior rather than a missing solution path.

### Results

Six honest trials were run across Claude Opus 5 Max and Grok 4.6 xhigh. Every trial received a reward of 0.

All six trials failed the same four tests:

`test_schema_epoch_fresh_ids_and_readers`  
`test_peer_email_rebuilds_schema_epoch`  
`test_composed_recovery_matches_serial`  
`test_seeded_random_variant`

The agents consistently produced behavior compatible with stable field identities while the task required fresh identities for each epoch. **Both frontier models encountered evidence supporting the local contract but ultimately converged on the familiar convention.**

### Agent Reasoning Traces

The reasoning traces show a consistent pattern across both frontier agents. The agents encountered the schema-ID collision during execution, recognized the surrounding lakehouse conventions, and repeatedly evaluated the local requirement through the familiar stable-ID behavior.

The critical evidence appeared directly in their execution traces. The agents printed epoch-1 and epoch-2 field IDs, inspected the resulting schemas, and constructed tests around those observations. The traces therefore show that the agents had access to the information required to identify the contract violation.

The failure persisted during interpretation and verification. Rather than testing the complete epoch-level disjointness requirement, the agents constructed narrower invariants that preserved the familiar stable-ID convention. These checks allowed the agents to validate an implementation against their interpretation of schema evolution while leaving the local contract untested.

The two models expressed this pattern differently. Opus repeatedly encoded the stable-ID interpretation into its verification logic. Grok produced a stronger trajectory in which **the agent temporarily implemented and verified the contract-conformant behavior before reverting it.**

![Flow of the six traces from observation to shipped artifact](/assets/images/lakehouse-priors-fig3-trace-flow.png)


### Opus 5: Verifying the Familiar Convention

Across all four Opus reconstruction runs, the agents printed the colliding field IDs during their investigation. The traces showed epoch 2 reusing IDs from epoch 1, including sequences such as `[1, 2, 3, 4]` and `[1, 2, 3, 4, 5]`.

The agents then constructed narrow verification logic around the stable-ID interpretation. One run created `/tmp/invariants.py` with a check that treated changing a field's ID across epochs as evidence of an error. That invariant would reject the contract-conformant behavior because the task requires fresh IDs in each epoch.

One agent verified that the new `email` field received a fresh ID without checking whether the complete epoch-2 ID set remained disjoint from epoch 1. Another property group used the label `"epoch 2 allocation is fresh relative to epoch 1"` but filtered the comparison to newly added field names.

All Opus runs left `schema.py` byte-identical to the starter. The agent repeatedly observed the collision, constructed checks around the stable-ID interpretation, and retained the implementation that produced the collision.

### Grok 4.6: Reverting a Verified Correct Fix

The Grok traces provide a more explicit example of the same conflict. **The agent reached the contract-conformant implementation, constructed the correct invariant, observed the invariant pass, and then rejected the implementation in favor of the familiar convention.**

In one run, the agent implemented the correct fresh-ID behavior and wrote the corresponding disjointness assertion:

`ids1.isdisjoint(ids2)`

The assertion passed with epoch-1 IDs `{1,2,3,4}` and epoch-2 IDs `{5,6,7,8,9}`.

The agent then reverted the implementation and restored the stable-ID behavior. After the reversal, the test count changed from `128/5` to `127/6`. The run concluded that the implementation was working and attributed the remaining failures to the tests.

![Grok 4.6 trial 1 timeline: fix, verify, revert, ship](/assets/images/lakehouse-priors-fig4-grok-revert.png)


Other Grok traces show the same tension. One run stated, `"I don't want to risk breaking the verifier,"` before later producing the correct diagnosis of the schema-ID requirement. Another argued that the requirement described additive schema evolution rather than a complete reset of field identities. A separate hardening run correctly described epoch 2 as using IDs `5-9` and called the result `"Fresh. Good."`

The Grok traces therefore show the same underlying conflict as the Opus traces, with a more explicit implementation-level reversal: the local contract produced a verified solution, while the familiar convention ultimately controlled the final implementation.

## Conclusion

This counterexample shows how a familiar software convention can compete with an explicit local specification in frontier coding agents. The reasoning traces provide even stronger evidence. 

Local contract shifts provide a simple way to expose this behavior and verify the output. Preserve a familiar environment, change one semantic rule, and test whether the agent conditions its implementation on the local specification.

Coding-agent evaluations should test more than unfamiliarity and implementation complexity. They should also test whether agents can override strong learned conventions when the task explicitly requires them to do so.