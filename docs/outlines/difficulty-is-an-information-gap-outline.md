<!-- Final outline, frozen 2026-09-21, for the post of the same name.
     Kept as an artifact of the argument structure before drafting. -->

# Building a synthetic SWE factory: difficulty is an information gap

**Thesis.** A coding task is hard because of what its prompt leaves out, so difficulty is a quantity you set rather than one you inherit.

---

**I. Difficulty is an information gap.**

A. A generated task fails in two ways that look identical from a solve rate: too easy, or underspecified.

B. Both failures are about information, since a task is too easy when the prompt and the repository already contain the answer, and underspecified when together they leave out something nobody could derive.

C. Seven levels, L0 through L6, each add one kind of information about the removed behavior.

1. L0 is a bug report, L2 is every behavior the hidden tests check, L6 is every test.

2. The levels build tasks; they do not read existing ones.

3. Mapping the levels onto Terminal-Bench puts almost every task at L1, so that benchmark cannot vary the axis or test it.

D. A certificate is one model failing at L0 and passing at L2.

1. The L0 failure shows the task is hard for a named model at a named amount of information.

2. The L2 pass shows the task is solvable from prose naming no file, symbol, or line.

3. One prompt leaves hard and impossible indistinguishable, and re-running it cannot separate them.

E. Every comparable pipeline sets difficulty by whether some model failed, which leaves that ambiguity in place.

1. CodeMidas is the closest relative: source-only, 23 languages, 5,545 tasks, screened on a model's pass rate.

2. CodeMidas derives tests from the original code; these are derived from a written specification of it.

**II. The evidence that the gap is what matters.**

A. One certified task, `gin-clientip`, shows the gap concretely: 168 words at L0, 668 at L2, one L0 failure and three L2 passes.

1. The L0 bug report names the symptom and cannot name the precedence rule, because the documentation left with the code.

2. The L2 contract states five clauses of caller-visible behavior plus worked examples.

3. None of the extra 500 words names a file, a line number, or a function.

B. Inverting one line of a description flips seven of eight passing tasks.

1. The code, the tests, the repository, and the model were held fixed.

2. Each of the seven failed on exactly the property that was inverted.

3. 40% of the first batch described the removed code incorrectly.

4. Every double failure investigated, 7 of 7, was a defect in the description.

5. A level is therefore a claim about what a competent programmer could derive from what they were handed.

C. The repository leaks information in three places, and closing them is how the gap gets set.

1. Call sites specify a removed dependency: 19 of 23 such tasks were solved from the bug report alone, and 12 of 14 after targeting unmemorizable code.

2. A complete in-tree test suite is a specification: 36 of 36 and 26 of 26 such tasks were solved.

3. Test names leaked the removed symbol until a check was added.

4. Structural complexity does not create difficulty: 25 tasks across eight knobs produced 25 passes and moved only solve time, from 1.34 to 7.57 minutes.

**III. The factory.**

A. One agent removes a behavior, keeps the public signatures, and writes a bug report and a behavior list.

B. A second agent writes one hidden test per behavior without seeing the removed code, which keeps the tests about observable behavior.

C. Execution proves the cut fails, the answer key passes, a hardcoded fake fix fails, and the answer key never edits a test.

D. A third agent writes the full description, one line per assertion.

E. The checks reject real tasks, not hypothetical ones.

1. Two tasks shipped whose answer key failed their own tests.

2. One task passed with a hardcoded special case.

3. A derivability pass dropped or weakened 245 of 1,560 behavior lines.

4. Blocking the network disqualified 15 of 30 runs from one model and 0 of 32 from another.

**IV. What came out.**

A. 527 authored, 339 trialled, 299 decided, 139 certified.

B. 131 of 299 were solved from the bug report alone and were never hard.

C. 29 of 299 failed both prompts, and every one audited was a defective description.

D. 124 of 139 certificates have one model on both ends; 15 do not and are labelled separately.

E. 1,545 task files contain zero references to issues, pull requests, or CVEs, so the tasks predate no training set.

F. The median answer key is 127 lines and a quarter touch two or more files.

G. 1,239 runs, 2.32B tokens, and $519 produced 139 certificates, or 8.3 runs each against a floor of two.

H. 73% of tokens paid for runs past that pair, and gating beats ungated parallel trials 3.2 against 9.0.

**V. Scope and what transfers.**

A. Go only, nine repositories, and one model for 95% of runs, all budget choices rather than findings.

B. Whether the method transfers past Go is stage 2 and the real test.

C. Whether a certificate holds for a model that never took part in screening is open.

D. The levels between L2 and L6 are sparsely sampled, so the dose-response curve is unmeasured.

E. Per-repository yield needs re-deriving before it can be claimed.

F. A solve rate belongs to the model that produced it, and so does a certificate.

---

Code and trial ledger: [`open_swe_traces_research`](https://github.com/Evan-Kim2028/open_swe_traces_research)
