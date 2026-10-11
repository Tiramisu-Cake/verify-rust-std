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
