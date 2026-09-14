<!-- Final outline, frozen 2026-09-14, for the post of the same name.
     Kept as an artifact of the argument structure before drafting. -->

# Four verifiable properties of a useful agent task

**Thesis.** There are four verifiable properties that make an agent task useful, and they are not equally verifiable.

---

**I. Four properties define a useful task.**

A. Soundness means the task's own answer key satisfies its own grader.

B. Difficulty means the model it is meant for sometimes passes and sometimes fails.

C. Shelf life means it still sometimes fails once models improve.

D. Taste means the task matches what this benchmark's own reviewers keep.

E. The four were derived from measurement, not from a rubric.

1. Each was kept only where an existing pool could be measured against it.

2. Completeness is not established, and other properties may matter.

3. Every figure comes from the pools measured.

**II. Strong verification: soundness and difficulty.**

A. Soundness is a necessary condition, so its failure needs no interpretation.

1. Running the reference and an empty submission in a fresh container settles it.

2. Terminal-Bench repaired 28 tasks between versions; the check flags 9 of 27 before the repair and clears 7 after.

3. Sampling converts the count into a population upper bound.

4. Against a known census the bound covers the true rate in 100% of 4,000 draws.

5. Harbor-Index shipped 82 tasks after a model screen, fourteen reviewers and a fix pass, and 2 of its 53 executable references fail on every run.

6. One of the two fails half its own tests; the other writes a zero reward while its log reports 0.97.

7. Passing is necessary and not sufficient, by four known routes.

B. Difficulty is measurable once the reference model is named.

1. A task always solved, or never solved, cannot tell two models apart.

2. Broken tasks sit at a 2% median solve rate against 33% for sound ones.

3. Harbor-Index cut 6,627 candidates to 1,311 on solve rate, and its public trial data reproduces the cut at 1,331.

4. The figure is relative to that model and must be reported with it.

**III. Weak verification: shelf life and taste.**

A. Shelf life is difficulty measured again later, and the least examined property.

1. Terminal-Bench 4 has 27 of 66 tasks gaining more than 40 points of solve rate as models get stronger.

2. The typical task across 6,613 gains 13 points, so the steep group is the exception.

3. Task features do not substitute, ranking same-benchmark pairs at 51%, which is chance.

4. Expert review does not substitute, since Harbor-Index survivors are no flatter than its rejects.

5. Capability tier is a confounded axis, since a submission is a model and a harness.

6. CurveShift (arXiv 2608.00355, July 2026) measured the same construct first and named the same confound.

B. Taste is measurable inside a benchmark that has enough reviewed tasks.

1. SWE-bench has 500 kept tasks and ranks kept above rejected 60% of the time.

2. Terminal-Bench 2.1 has 26 and sits at chance.

3. Harbor-Index averages three kept tasks per source, too few to fit at all.

4. Taste directs generation and cannot gate acceptance.

5. A new benchmark has no reviewed set, so taste is undefined for it.

**IV. Conclusion and future work.**

A. Shelf life needs a capability axis that separates model from harness.

B. Taste needs benchmarks to publish which candidates they rejected.

C. Whether the four predict a task's downstream value remains untested.

---

Data index and ingest scripts: [`evaltrials`](https://github.com/Evan-Kim2028/evaltrials)
