# Maintainer review package — Rust ZST size repair

Status: experimental/unaccepted; integration remains a maintainer decision.
Policy read: `c7ca8c467aecf10a4b53039372ee97714f854ee3`.

The candidate removes the contradictory Rust positive-struct-size premise
when native `[MaybeUninit<T>]` meets its existing `sizeof(MU<T>)=sizeof(T)`
rule. [Rationale](ZST-REPAIR-RATIONALE.md) identifies the exact two changed
rules, Rust applicability, prior conclusions invalidated, unchanged C/C++
semantics, bounds/alignment/footprint/resource rules, and regression gates.
Only `src/verifast1.ml` changes in [rust-zst-size.patch](rust-zst-size.patch).
Complete empty Rust field maps get size zero; opaque and ghost-only structs
are not classified as complete empty structs.

[Tool manifest](ZST-REPAIR-TOOL-MANIFEST.json) pins tool HEAD, kernel,
patch, and base/result verifast1 hashes. [Full base/result manifest](ZST-REPAIR-BASE-RESULT-MANIFEST.json)
includes the historical frozen base, all effective spec/source/binary hashes,
and fresh C1 result profile. The historical snapshot is unchanged. All tool
build/apply/export/refinement/verifier execution was in isolated Cloud checkouts.

Fresh evidence:

- [First review](FRESH-B1BABB85-REVIEW.md): model pair and intended negatives
  succeeded, but the concrete matrix stopped at an alignment assertion because
  the fixture omitted the existing layout lemma. Consumer skipped. No patch
  change was made to obtain alignment; the next source calls the existing lemma.
- [Fresh full review](FRESH-ED016F05-REVIEW.md), [index](FRESH-ED016F05-INDEX.json):
  model gates pass; native C1 verifier exit 0, 196 statements, zero errors.
  Actual source145 sizezero guard, MIR/AST/control flow and run-local dead-code
  identities establish reachable ZST return. Normal/unwind false controls fail
  at intended assertions 226/210; admission controls refuse before proof.

Exact fresh proof/infra Git SHA: `f1e139053eac06da27a4068b47b0d44cbca1cb73`.
Build: `ed016f05-c66b-4d9f-8be4-12b8c0271f8f`, `smallsort-ci/global`, lane
`o26-sort4-c1-current-recovery`. Archive hash is in the fresh index/review;
original complete logs and inventories remain in Cloud evidence, not committed.
[Reproduction](REPRODUCTION.md) documents the existing lane and pinned chain;
this session uses the explicitly new phase/profile and ZST manifest.

Read-only evidence retrieval (while this phase's controller remains available):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11 \
  --ledger research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET-ZST-REPAIR-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-native-c1-zst-repair-20261011 \
  --owner select-sort4 download ed016f05-c66b-4d9f-8be4-12b8c0271f8f \
  --output /tmp/maintainer-zst-ed016-review --text-logs
```

No future dispatch is authorized by these reproduction commands. A fresh
session/budget is required after this session closes.

Open trust obligations: review the Rust complete-empty definition/spec trust,
full size/layout rule interaction beyond the deliberately narrow regression
matrix, and pre-existing experimental native binding/strict-cut/source-specific
translator chain. A finite gate matrix is no general soundness proof. No
MU/reference-own inverse, added raw permissions, changed callback/kernel/solver
semantics, or accepted theorem is introduced by this size repair.

This is a guarded research native C1 fragment, not full actual sort4 or a
verified std caller. In particular its added sizezero guard is not established
at the actual caller; successful return does not prove generic ZST safety.
Native C4 progression is separately recorded in the final session checkpoint.

Exact Cloud reproduction invocation for the successful C1 input (historical
command, not standing dispatch authorization):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11 \
  --ledger research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET-ZST-REPAIR-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-native-c1-zst-repair-20261011 \
  --owner select-sort4 submit \
  --infra-sha f1e139053eac06da27a4068b47b0d44cbca1cb73 \
  --proof-sha f1e139053eac06da27a4068b47b0d44cbca1cb73 \
  --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 1200
```

Internal tool apply/build and verifier argv are recorded verbatim in each
Cloud stage JSON. `zst-model/*/verification-stage.json` and
`supplied/native-c1-bound-positive/verification-stage.json` record the
positive consumers; `native-c1-bound-tool/effective-profile.json` records isolation.
