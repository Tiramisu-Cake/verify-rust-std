# Static review — KANI3300 M3-R3

**Result: static acceptance.**

- Baseline: `aac27ed95364989bc045e5cdc227f2a97448f955`
- Candidate: `6c29e38c57fdf646bf07725c5c09008518d04255`
- Candidate tree: `cdc30da3c5327e8070ee4f61a42df37c9ea30104`
- Review spec SHA256: `487cef2cbeb4fd94bc9cade68f9475db5d4c96d8a5bfc808f7e723f276e19615`
- Packet diff SHA256: `855881fe7dea86519548b4da7261da161bc7edf157e506ca2dadc687167dbcdc`

The candidate's first commit is directly on the specified baseline; the diff contains only the requested documentation and tuple/top-level regression fixtures. The four declared dependency snapshots match their candidate files and are unchanged from baseline. No compiler/runtime production paths, B1 unresolved-calls or closure-zst goldens, eight strong oracles, mode boundaries, shared validator, or M3-R2 ordinary-pointer/guard fixtures are changed.

The top-level companion retains `Move(source)`, a normal-edge return, source repair before the source read, assertions for returned `42` and repaired source `23`, and a no-repair negative root. The expected file requires legal SUCCESS and the negative uninitialized-`u8` FAILURE. Static review cannot establish that these expected outcomes occur.

The tuple fixture's source changes only by an explanatory comment. Its expected output pins the supplied R1 property `std::mem::transmute_neo::<std::mem::MaybeUninit<u8>, u8>.safety_check.1`, FAILURE status, and uninitialized-`u8` diagnostic, with both failing-root summaries and `0 successfully verified harnesses, 2 failures, 2 total`. The comment and docs correctly identify the legal root as semantically successful and its failure as a known false positive, not UB detection credit. The docs describe the by-value nested aggregate shadow-transfer gap and explicitly make no fail-closed guarantee.

The expected-output matcher checks required lines/consecutive groups but does not establish complete per-root output inventories; the pinned property/diagnostic and root summaries provide the specified bounded observation.

**Validation limits:** Python/static packet identity checks only. No cargo, rustc, Kani, CBMC, build, CI, or push was run. Top-level compile/proof and full CI are **NOT_RUN**. The tuple observation is from the supplied task and `STOP-R1.md`, not a new run. **Proof credit: NONE.**
