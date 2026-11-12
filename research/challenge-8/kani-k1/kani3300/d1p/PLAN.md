# D1-P bounded preparation

Only this stage. Source evidence: audit @ab7509822453bbf0778da0265c67f51bc08b4755
(read in full), brief v2 @cbf575f3aa6ec7b81f2359dd300d1426a4ee57bf and m2br6b
manifest/CI request. Two exact independent parents, same overlay bytes. No model,
production compiler/driver/runtime/library/toolchain/check/solver/slicing changes.

1. Fix manual diagnostic capture: bounded drain, identities/argv, owned process
   sessions, explicit phase statuses, NOT_RUN semantic verdict and always upload.
2. Capture specialized pre-DFCC, immediate post-DFCC and actual CBMC input with
   hashes. In-place source is copied first; no extra mutating transformations.
3. One stock --program-only view per mandatory P1/pin, plus read-only stock
   symbol/function views of saved snapshots and bounded offline text summaries.
4. Synthetic Python/YAML tests, shell syntax and one Luna High boundary review;
   fix localized findings. Commit at most once per parent; no Kani push/CI.
5. Research-only [skip ci] commit and ordinary g0 push; STOP with READY SHA.

Not compiled; no observed A/B data or offenders yet. No SAT, solver retry, P2,
R7/R8/upstream rerun, scope change, optimization or D1-A. Width/Layout/owner/
property/feasibility bindings UNKNOWN; proof credit0. D1-A is a separate session.
