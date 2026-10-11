# Exact native C1-bound reproduction inputs

Experimental, unaccepted profile. Tool HEAD alone is insufficient:
frozen C4 chain (../sort4-native-c4/FROZEN-C4-SNAPSHOT.json) → capture86952a6a
(../sort4-native-opaque/native-c1-capture.patch) → separately named bound patch.
Final translator381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6;
patcheea19eda3723a0f60970df751c7600c326f98ad476d41f61e3f39442beb88693.
Tool HEADf76012fb518703b1d98e243ac4f487f16877cfcb; nightly2026-09-25;
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c.
All other critical/exporter/refiner/prelude hashes frozen and independently
checked by driver against FROZEN-C4-SNAPSHOT.json before target verification.

Exact source7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742;
original7c35a7e01915233308d113b081f26784c4ad5aaf6f7049dc209d126e3eb326a1;
normal MIR8e9adcccd136d3c1ee4dc1e7bd929c3cd60883f497178eab24da40f60754dee4;
readonly MIRbde6d797d56e0e11e9837fc922f6def819c6931d1349f42c5b36d4570e2001aa;
preAST18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5.
Recipe o26-sort4-c1-current-recovery, proof76/infra16 sorted unique closure;
source-mode pinned-objects, marker SORT4_NATIVE_C1_BOUND_PHASE=1. Six
exact-source cases require these full hashes and all8 paired support/refinement
before verifier. Two mutated admission cases retain their own source/MIR pins.

Authorized final experiment used this command in the own worktree (new
submission requires a new authorized session/account; do not reuse closed
ledger for dispatch):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-BOUND-CLOUD-2026-10-10 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET.json \
  --state-dir /tmp/smallsort-cloud-native-c1-bound-20261010 \
  --owner select-sort4 submit \
  --infra-sha 2e995605f5183907817d92db082624281665d61e \
  --proof-sha 2e995605f5183907817d92db082624281665d61e \
  --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 900
```

Canonical archive locations and exact Build IDs/create→finish charges are in
BUDGET.json and fresh review/index files. Evidence replay is read-only, not a
new fresh proof. Proof/extraction compilation never runs on the VPS.

Exact Git-object packaging preflight for2e995605:561577gzipbytes,
188sourceparts at3990chars/part, below191bound. Four skipped native_cases
caller-entry files removed; no source/tool/proof/check/gate changes. Earlier
8ab attempt exceeded bound beforeAPI, no Build/reservation/charge.

## Physical-node / entry-bound diagnostic session, 2026-10-11

Historical3521 command above is preserved, not a dispatch authorization.
Diagnostic phase `SORT4-NATIVE-C1-ZST-DIAG-CLOUD-2026-10-11` uses the separate
BUDGET-2026-10-11.json account; start00:21UTC, main02:21, finish-only02:51.
Lane and owner unchanged. Recipe adds only diagnostic manifest+patch to proof
role:78 proof paths;16 recipe infra paths /23 total infra including core.
Captured original3521 postAST c5fa49a0 remains byte-identical in009. General
code patch changes only vfconsole/verify_expr logging, with original visit
registration/removal, check filtering and refusal preserved. Full diagnostic
pins in NATIVE-DEAD-CODE-IDENTITY-DIAGNOSTIC-MANIFEST.json.

009 proof=infra f8115f33f35d745b9da9ab5e01f0ee3b7908ce56 ran verbosity4 native
and fresh callback-free with/without MU controls. Entry-beforecalls follow-up
9ae319b8 uses b81f1c3ccce23e0b5e2a029350c0a6443b929747, only new minimal
probe assertions and verbosity6; target source/tool semantics unchanged.
Preflight b81:565261 gzip bytes,189parts, packed SHA256
c511986a7fead8b7b75adff476d8acd053ed0c74e73c411ee5871a112dd242ba;
role-specific object bytes/hash checks pass for driver, wrapper, discovery
helper and both diagnostic proof dependencies. Static Python AST, bash syntax
and diff-whitespace checks pass; no local proof/extraction/compilation.

Executed command (reproduction record; a closed session needs new authorization):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-ZST-DIAG-CLOUD-2026-10-11 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-native-c1-zst-diag-20261011 \
  --owner select-sort4 submit \
  --infra-sha b81f1c3ccce23e0b5e2a029350c0a6443b929747 \
  --proof-sha b81f1c3ccce23e0b5e2a029350c0a6443b929747 \
  --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 900
```

Specific status/download used the same explicit phase/ledger/state-dir/owner,
with `status BUILD_ID` then `download BUILD_ID --output /tmp/native-c1-zst-diag-009-read
--text-logs` (009) or its9ae saved-evidence directory. Canonical GCS archive is
`gs://smallsort-ci-evidence-504462351565/cloud-build/BUILD_ID/evidence.tar.gz`.
Raw verifier argv is captured in each verification-stage.json: `-rustc_args
"--edition 2021" -verbose 4 verified/lib.rs` for native;6 only for entry probes.
Paired export/decode/refinement always precede verifier. Saved evidence reader
executes no prover; fresh evidence review/checkpoint state separate verdicts.
