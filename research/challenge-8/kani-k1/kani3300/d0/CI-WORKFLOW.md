# KANI3300 D0-CI — prepared workflow

CI commit: `34c0848da734d6fab91218643f1e97a002365e1a`.
Local worktree `/root/kani-fix-3300-d0`, branch `ci/d0-diagnostics`.
Exactly one commit above `955cd015649aa79be511fe1732d48fdc8535741f`;
author and committer `Tiramisu-Cake <igkharin@gmail.com>`, configured through
`git -c`; message `CI only: D0 raw_eq diagnostics`. **CI branch not pushed.**
Only `.github/` changed. D0-P request is the published `5956660766` package.

`.github/workflows/d0-diagnostics.yml` is the sole workflow. Trigger:
push to `uninit-ci/**`; runner `ubuntu-24.04`; job timeout 240 minutes.
The existing setup action is used with each checkout. Exact candidate and
baseline `a0a2386001a15fecfe2facc2f6cd87f3dee13b60` are independently built with
`cargo build-dev -- --release`. Actual source/tree/diff/fixture/tool/binary/
sysroot/target/CPU/limit identities are recorded. The candidate-built Kani
libraries are used unchanged by both verification runs after checking identical
library source; Rust sysroot and solver identities must also match.

Candidate cases A/B/AB/BA/D and baseline A/B/pair follow CI-REQUEST argv,
selectors, diagnostic environment, normal prewarm and no-slicing policy.
Each case has a fresh directory/process; case timeout is 600 seconds, build
timeout 2400 seconds, read-only inventory timeout 60 seconds. No retries.
The compiler launcher records the actual child's wait status, separate from
codegen coverage. Case timeout kills/reaps the process group. Exact copies of
`capture_cbmc.py` and `curate_cbmc_trace.py` preserve solver data/exits.
The driver's exact `cbmc --version` probe is inventoried separately from solver
captures. Harness metadata binds roots and linked GOTO inputs; the inventory
decoder binds exact property IDs/source coordinates to unique assertion PCs.

Setup/build/compiler/solver/verification/inventory/curation outcomes remain
separate. Verification FAIL is retained as an original nonzero exit and verdict,
without aborting collection or becoming a PASS claim. Final infrastructure gate
checks setup, compilation, collection/curation and artifact delivery.

- `d0-curated`: bounded JSON, identities, manifests, coverage/control reports,
  original indices, SHA256 references and short `SUMMARY.md`; maximum 5 MiB.
  This is the only packet for D0-A.
- `d0-private`: original CBMC JSON, GOTO inputs/listings, sidecars and private
  phase logs; seven-day retention. Coordinator only in the handoff workflow.
  GitHub artifact ACLs follow repository permissions, not artifact names;
  the coordinator must distribute only `d0-curated` to D0-A.

A/B/D are compared against baseline A/B/pair using full per-harness property
inventories and GOTO listings, normalizing only recorded absolute source/output
paths. Emitted MIR files are compared when available. Missing/mismatched prewarm,
roots, inventories, identities or coverage stop the affected comparison.
Matching inventories do not establish full model equivalence.

**Explicit limits:** original/final/consumed MIR equivalence remains UNKNOWN
where unmodified baseline lacks those observations. Runtime operand, pointer,
tracked-object and executed last-writer chains are not inferred from names,
property suffixes, CLI order or a failing verdict. Failing properties without
those bindings produce `UNKNOWN` witness rows and `INCOMPLETE` curation, with
original exits intact. Caps/missing fields require a precise targeted packet;
no raw trace/GOTO handoff or extra runtime probes are substituted.

Validation: actionlint 1.7.7; Python AST/YAML parse plus trigger/runner/timeout/
scope/copy assertions; 47 passing synthetic tests (including transparent
capture, signal/death/timeout, malformed/missing/hash-mismatched metadata,
property/PC/root ambiguity and source mismatch, baseline pair, preservation of
verification FAIL, private-packet separation and control mismatch);
`git diff --check` and staged diff check. A `/proc` disappearance race in the
copied capture test was fixed without changing the capture shim.

No local cargo/rustc/Kani/CBMC execution. No workflow dispatched; runtime
build/verification/model-equivalence results are NOT_RUN. Cloud spend $0.
Publication/dispatch of the local CI commit remains with the coordinator.
