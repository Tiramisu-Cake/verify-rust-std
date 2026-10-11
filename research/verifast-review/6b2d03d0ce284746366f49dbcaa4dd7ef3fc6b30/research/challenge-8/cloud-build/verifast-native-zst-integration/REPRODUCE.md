# Reproduction — exact merged native/ZST candidate

Tool `46181aff379a5d4231cc51814cfe3732bda21c03`; base Bool tool `4a34010cc3930eec46fc4e72c1b793ad734fa730`; effective profile `verifast-native-zst-c3-integration-20261011-h`. Runner/infra/proof delivery `03c2f4e134473253045d716a9779cc1b8530d0bb`. See [manifest](manifest.json), [recipe](../recipes/verifast-native-zst-integration.json), [ledger](BUDGET.json), [semantic review](../../verifast-review/native-zst-20261011/SEMANTIC-REVIEW.md), [runner review](../../verifast-review/native-zst-20261011/RUNNER-REVIEW.md) and [matrix](GATE-MATRIX.md).

Actual submitted command (historical after this account closes; future replay requires a separately authorized phase/account, not reopening H):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir .verifast-native-zst-h-state \
  --phase-id VERIFAST-NATIVE-ZST-INTEGRATION-CLOUD-2026-10-11-H \
  --ledger research/challenge-8/cloud-build/verifast-native-zst-integration/BUDGET.json \
  --owner verifast submit \
  --infra-sha 03c2f4e134473253045d716a9779cc1b8530d0bb \
  --proof-sha 03c2f4e134473253045d716a9779cc1b8530d0bb \
  --lane verifast-native-zst-integration --timeout 1500
```

Build `47ee47d9-274b-4b13-84e2-167ba88ff770`, `smallsort-ci/global`, E2_STANDARD_2. Native and Bool pipelines use one console build. Official base `f76012fb518703b1d98e243ac4f487f16877cfcb` plus the three preserved C3 patches and exact reviewed [merged overlay](../../verifast-review/native-zst-20261011/merged-extra.patch); full tool [bundle](../../verifast-review/native-zst-20261011/tool.bundle) requires that official base. Kernel and seven effective file hashes are checked by the runner. Stock26.10 exporter/refinement, Rust nightly2026-09-25/f7575a9d, decoder2d6606d9 and dependency release25.01 remain pinned. No whole-chain upstream update.

The complete 30-module pack/two XZ payloads preserve their raw/compressed hashes and exact Git objects. Source prepare/imports occur in Cloud before expensive compilation. Committed delivery is 571076 gzip bytes/191 source parts; the earlier 198-part attempt was a static refusal and created no Build. Omitted new-recipe files are unused historical manifest/run.sh/MDnew provenance; historical files stay unchanged and fixture hashes stay pinned.

Verifier argv, fixture source pair/MIR/refinement/AST hashes, environment settings and stage logs are retained in the evidence archive. Full checks remain enabled: normal/unwind posts, return, leak and dead-code; strict cuts enabled for C4/native; selector-only strict setting remains its original value. No local proof execution is part of reproduction. Raw evidence review may produce a separate assessment without rewriting Cloud FAILURE, logs or diagnostic summaries.

No profile adoption, actual caller, native C4+select or full sort4 theorem follows. General O23 and inherited experimental assumptions remain open.

Supplemental affected-only command (same closed-account warning):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir .verifast-native-zst-h-state \
  --phase-id VERIFAST-NATIVE-ZST-INTEGRATION-CLOUD-2026-10-11-H \
  --ledger research/challenge-8/cloud-build/verifast-native-zst-integration/BUDGET.json \
  --owner verifast submit \
  --infra-sha 491a98e35e5dd3caab257d91074f4aacb06415d4 \
  --proof-sha 491a98e35e5dd3caab257d91074f4aacb06415d4 \
  --lane verifast-native-zst-integration --timeout 1200
```

 Build `15f28723-2e2a-46b0-9b39-145dbb1787fa`. It actually repeats pack imports and source preparation before compilation, checks exact prepared/seven-file/binary hashes, and executes only `bin/verifast -shared c-nonempty.c` and `bin/verifast -shared cpp-empty.cpp`. It neither reruns nor reclassifies other proof results. Primary runner03c2 remains the full-matrix reproduction command; supplemental491a is the exact two-control correction. The current manifest is supplemental; original full manifest is preserved in primary03c2 and evidence. Final assessment is separate ASSESSMENT.json.
