# Reproduction: slice as_mut_ptr candidate I

Tool `b6cb276afd13107c2a90ca50acbb12ff0a992dd8`, based on H `46181aff379a5d4231cc51814cfe3732bda21c03`. Runner/infra/proof `7f5f88b54d9d631fee24ec84ab868d42c2f174b3`; profile `verifast-slice-as-mut-ptr-native-c3-20261011-i`. [Manifest](manifest.json), [semantic review](../../verifast-review/slice-as-mut-ptr-20261011/SEMANTIC-REVIEW.md), [runner review](../../verifast-review/slice-as-mut-ptr-20261011/RUNNER-REVIEW.md), [checkpoint](END-CHECKPOINT.md).

Actual command (this account is historical once closed; a future replay requires separate authorization and new phase/ledger):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir .verifast-slice-i-state \
  --phase-id VERIFAST-SLICE-BINDING-INTEGRATION-CLOUD-2026-10-11-I \
  --ledger research/challenge-8/cloud-build/verifast-slice-binding-integration/BUDGET.json \
  --owner verifast submit \
  --infra-sha 7f5f88b54d9d631fee24ec84ab868d42c2f174b3 \
  --proof-sha 7f5f88b54d9d631fee24ec84ab868d42c2f174b3 \
  --lane verifast-slice-binding-integration --timeout 1500
```

One console build applies preserved C3 patches, H native/ZST overlay and exact one-line binding overlay against official `f76012fb518703b1d98e243ac4f487f16877cfcb`. Kernel and seven effective source hashes are pinned. No specs/contracts/CURRENT change. Translator after binding `a392cf28f72a8ae9c54faabf2454ddaff07757b6f0f98548ed72a7b8daab9ba3`. Exporter/refinement stock26.10, Rust nightly2026-09-25/f7575a9d, decoder2d6606d9 and deps25.01 remain H pins. Full30-module/twoXZ dependency pack retained, slice fullsource additionally restored from XZ with raw/compressed/Gitblob checks. Actual Python imports and preparation of all fixtures execute Cloud before costly build. I-only packed transport retains original Git objects; legacy lanes retain their encoding; no coordinator/cap change.

The fresh run covers six unchanged slice components/consumer controls, three expected source admission refusals, nine selector bodies, boundedC4 and C4+firstselect466, nativeC1/C4 and affected ZST/native/C3 controls. C/C++ controls retain `-shared`. Explicit runner diagnostic/acceptance fields remain conservative while raw review is pending; raw Cloud status is historical, separate from human integration assessment.

The method is a pointervalue projection, with no pointee rights/writable/initialized-T/lifetime/aliasing grant. Source/receiver/MIR checks belong to runner admission; the translator alone does not enforce all these pins. Caller len+16/publicZSTguard transfer/nativeC4+select/fullsort4 remain proof-owner missions. General O23, inherited native assumptions and owner adoption stay open. Historical H pins/readiness and unrelated upstream packet are preserved.


The first command executed the new slice/native/Bool proofs but its regression aggregate stopped at a missing `outer_scope_capture_pins` manifest field. Build `5cb5b5d3-e4d6-4185-9234-f3a89e79829e` remains Cloud FAILURE. Complete corrected full runner `0371f4f8c19e488cd32fb719a8b2f8fcf3dbcbd0` restores the exact preexisting outer normal/readonly pins and required-key preflight; whole corrected full run is **UNRUN**. It is the complete recipe for a separately authorized future full replay, using the same command above with both infra/proof SHAs replaced by `0371f4f8c19e488cd32fb719a8b2f8fcf3dbcbd0`.

Actual required-gate supplement:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir .verifast-slice-i-state \
  --phase-id VERIFAST-SLICE-BINDING-INTEGRATION-CLOUD-2026-10-11-I \
  --ledger research/challenge-8/cloud-build/verifast-slice-binding-integration/BUDGET.json \
  --owner verifast submit \
  --infra-sha 99deac7a0275359124038d134aa46a08e5131fe6 \
  --proof-sha 99deac7a0275359124038d134aa46a08e5131fe6 \
  --lane verifast-slice-binding-integration --timeout 1200
```

Supplement Build `d7e340fc-4cb9-4bd1-8a3f-d43d84fdf1d6` freshly executes the existing Bool pipeline and all affected regressions. The producer, positives and composition controls necessarily run again because regressions consume their in-memory receipts; no old proof/AST or assumed summary is imported. The rebuilt console must equal first Build SHA `9fc7c65b438e41ad014a08fe2f8b3e8f9b296866e010d8c423468b21565b3fd5` before proof, and all seven effective hashes are pinned. Full dependency delivery and all fixture source preparations still precede compilation. Slice/native/ZST verification is explicitly NOT_RERUN_BASELINE_REFERENCE_ONLY in this supplement; their fresh first Build evidence retains its original delivery/fixture/manifest/archive pins. Human assessment of the same-tool union is separate from raw diagnostic flags, Cloud status and owner adoption.
