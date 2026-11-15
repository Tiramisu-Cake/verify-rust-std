# U → F test/oracle map — worker15, stage 0

Static source map, no native runs. U/B1/F identities in INPUTS.json; exact per-path blobs/modes/SHA-256, flags, source assertions, all golden lines and 28 compiler units in ORACLE-MAP.json. Each table row owns both source and golden, with unchanged B1 paths retaining B1 ownership in the JSON path records.

Owner = semantic slice; run = first cumulative head with the complete fixture prerequisites. A later run bound never licenses an incomplete source head or a new ignore. Where a golden lacks exact N, the map preserves its literal negative and marks the precision limitation; F is unchanged.

| Fixture under tests/expected/uninit/ | Owner | Run | Prerequisites | Exact property N in F |
|---|---:|---:|---|---|
| closure-upvars/holes | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-upvars/layout | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-upvars/ordinary | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-aligned-hole | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-aligned-legal | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-mu-reference-new | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-mu-reference-uninit | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-mu-value-new | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-mu-value-uninit | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-padded | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-raw-hole | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-raw-legal | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-reference-hole | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-reference-legal | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-scalar | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-union-reference | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-union-value | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-unit-hole | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/capture-unit-legal | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| closure-zst/scalar-pfc-hole | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 3 |
| closure-zst/scalar-pfc-legal | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| contract-immutable-masks/ensures-left-hole | 5 | 5 | ANALYSIS, IMMUTABLE, LAYOUT_RAW, STORAGE, CLOSURE | not pinned |
| contract-immutable-masks/ensures-right-hole | 5 | 5 | ANALYSIS, IMMUTABLE, LAYOUT_RAW, STORAGE, CLOSURE | not pinned |
| contract-immutable-masks/ordinary-singleton | 5 | 5 | ANALYSIS, IMMUTABLE, STORAGE, CLOSURE | not pinned |
| contract-modes/recursive-check | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 1 |
| contract-modes/recursive-ordinary | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 1 |
| contract-modes/recursive-simple-check | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| contract-modes/replace-ordinary | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| contract-modes/replace-simple-check | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| contract-modes/replace-transfer-uninitialized | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| contract-modes/replace-transfer | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 2 |
| copy-source-arguments/arg0-hole | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 2 |
| copy-source-arguments/arg0-initialized | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 0 |
| copy-source-arguments/arg1-hole | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 2 |
| copy-source-arguments/arg1-initialized | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 0 |
| immutable-descriptor-coalescing/aggregate-constant-initializer | 2 | 2 | IMMUTABLE | 0 |
| immutable-descriptor-coalescing/const-fn-initializer | 2 | 2 | IMMUTABLE | 0 |
| immutable-descriptor-coalescing/direct-first-volatile | 2 | 2 | IMMUTABLE | 0 |
| immutable-descriptor-coalescing/direct-first | 2 | 2 | IMMUTABLE | 0 |
| immutable-descriptor-coalescing/nested-first-volatile | 2 | 2 | IMMUTABLE | 0 |
| immutable-descriptor-coalescing/nested-first | 2 | 2 | IMMUTABLE | 0 |
| immutable-masks/copy-hole | 2 | 4 | IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| immutable-masks/empty | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| immutable-masks/zero-byte-hole | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| immutable-masks/zero-bytes-legal | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| marker-hook-calls/fn-item-plain | 4 | 4 | ANALYSIS, STORAGE | 0 |
| marker-hook-calls/fn-item-shadow-return | 4 | 4 | ANALYSIS, STORAGE | 1 |
| marker-hook-calls/generated-modifies-no-shadow | 4 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| marker-hook-calls/marked-body-hole | 4 | 4 | ANALYSIS, STORAGE | 1 |
| marker-hook-calls/marked-body-initialized | 4 | 4 | ANALYSIS, STORAGE | 0 |
| marker-hook-calls/marked-model-hole | 4 | 6 | ANALYSIS, STORAGE, E1 | 1 |
| marker-hook-calls/marked-model-initialized | 4 | 6 | ANALYSIS, STORAGE, E1 | 0 |
| marker-hook-calls/ordinary-hook-return | 4 | 4 | ANALYSIS, STORAGE | 1 |
| marker-hook-calls/ordinary-hook-scalar | 4 | 4 | ANALYSIS, STORAGE | 0 |
| maybe-uninit-argument-buffer/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-argument-return/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-array-reverse-unsupported/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-call-move/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-call-pairing-unsupported/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-call-pairing/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-contract-clause/main | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 1 |
| maybe-uninit-contract-frame/main | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 1 |
| maybe-uninit-initialized/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-overlap-copy/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-overwrite-copy/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-partial-copy/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-repeat-local/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-reset-alias/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-reset-zst/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-transfers/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-transmute-padding/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-transmute-source-read/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-transmute/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-typed-argument-padding/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-typed-array-padding/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-typed-array-partial-data/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-typed-assignment-padding/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-typed-partial-data/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-typed-return-padding/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| maybe-uninit-typed-transfer-data/main | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| mixed-promoted-allocations/eq-u8-stack-left | 3 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| mixed-promoted-allocations/eq-u8-stack-right | 3 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| mixed-promoted-allocations/raw-mu-promoted-left-hole | 3 | 4 | ANALYSIS, IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| mixed-promoted-allocations/raw-mu-promoted-right-hole | 3 | 4 | ANALYSIS, IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| mixed-promoted-allocations/raw-mu-stack-left-legal | 3 | 4 | ANALYSIS, IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| mixed-promoted-allocations/raw-mu-stack-right-legal | 3 | 4 | ANALYSIS, IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| mixed-promoted-allocations/raw-u8-stack-left | 3 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| mixed-promoted-allocations/raw-u8-stack-right | 3 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| nested-aggregate-reset/moved-from-source | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 1 |
| nested-aggregate-reset/reinit-companion | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 0 |
| nested-aggregate-reset/repeated-destination | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 1 |
| nested-enum-different-padding/main | 3 | 4 | IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| nested-enum-same-padding/main | 3 | 4 | IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| nested-pat-data/main | 3 | 4 | IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| nested-pat-padding/main | 3 | 4 | IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| ordinary-slots/padding | 1 | 4 | ANALYSIS, STORAGE | not pinned |
| ordinary-slots/payload | 1 | 4 | ANALYSIS, STORAGE | not pinned |
| ordinary-slots/positive | 1 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| padded-slice-extents/borrowed-hole | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 2 |
| padded-slice-extents/borrowed-initialized | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 0 |
| padded-slice-extents/raw-hole | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 2 |
| padded-slice-extents/raw-initialized | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | 0 |
| part1-composition/move-return-reinit | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| part1-composition/move-return-top-level | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| part1-composition/origin-offset-hole | 4 | 4 | ANALYSIS, IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| part1-composition/origin-offset-legal | 4 | 4 | ANALYSIS, IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| part1-composition/raw-vs-typed-hole | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| part1-composition/raw-vs-typed-legal | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| part1-composition/reset-hole | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| part1-composition/reset-reinit | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| part1-composition/typed-padding-hole | 4 | 4 | ANALYSIS, LAYOUT_RAW, STORAGE | not pinned |
| part1-edges/dst-by-reference-hole | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/dst-by-reference-legal | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/dst-by-value-hole | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/dst-by-value-legal | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/immutable-relocation-hole | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| part1-edges/immutable-relocation-legal | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| part1-edges/immutable-static-hole | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| part1-edges/immutable-static-legal | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| part1-edges/immutable-subrange-hole | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| part1-edges/immutable-subrange-legal | 2 | 3 | IMMUTABLE, LAYOUT_RAW | not pinned |
| part1-edges/raw-field-legal | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/raw-field-neighbor-hole | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/raw-field-padding-hole | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/union-constant-hole | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/union-constant-legal | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/union-variable-hole | 6 | 6 | STORAGE, E1 | not pinned |
| part1-edges/union-variable-legal | 6 | 6 | STORAGE, E1 | not pinned |
| points-to-cycles/capture-free | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | not pinned |
| points-to-cycles/dag | 1 | 4 | ANALYSIS, STORAGE | not pinned |
| points-to-cycles/mutual-cycle | 1 | 4 | ANALYSIS, STORAGE | not pinned |
| points-to-cycles/roots-acyclic-first | 1 | 4 | ANALYSIS, STORAGE | not pinned |
| points-to-cycles/roots-cycle-first | 1 | 4 | ANALYSIS, STORAGE | not pinned |
| points-to-cycles/self-cycle | 1 | 4 | ANALYSIS, STORAGE | not pinned |
| private-transfer-frame/lawful-modifies | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| promoted-allocations/direct-left-hole | 2 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| promoted-allocations/direct-legal | 2 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| promoted-allocations/direct-right-hole | 2 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| promoted-allocations/helper-left-hole | 2 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| promoted-allocations/helper-legal | 2 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| promoted-allocations/helper-right-hole | 2 | 3 | ANALYSIS, IMMUTABLE, LAYOUT_RAW | not pinned |
| raw-eq-uninit/main | 3 | 4 | IMMUTABLE, LAYOUT_RAW, STORAGE | not pinned |
| root-composition/cycle-root | 5 | 5 | ANALYSIS, IMMUTABLE, STORAGE, CLOSURE | 1 |
| root-composition/immutable-hole-negative | 5 | 5 | ANALYSIS, IMMUTABLE, STORAGE, CLOSURE | 2 |
| root-composition/immutable-legal | 5 | 5 | ANALYSIS, IMMUTABLE, STORAGE, CLOSURE | 0 |
| root-composition/ordinary-ensures-legal | 5 | 5 | ANALYSIS, IMMUTABLE, STORAGE, CLOSURE | 0 |
| root-composition/pfc-legal | 5 | 5 | ANALYSIS, IMMUTABLE, STORAGE, CLOSURE | 0 |
| root-composition/pfc-negative | 5 | 5 | ANALYSIS, IMMUTABLE, STORAGE, CLOSURE | 3 |
| root-composition/unrelated-legal-after-cycle | 5 | 5 | ANALYSIS, IMMUTABLE, STORAGE, CLOSURE | 0 |
| transfer-qualification/legal-ordinary | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| transfer-qualification/legal-pfc | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 0 |
| transfer-qualification/normal-abort | 4 | 4 | ANALYSIS, STORAGE | not pinned |
| transfer-qualification/out-pointer | 4 | 4 | ANALYSIS, STORAGE | not pinned |
| transfer-qualification/postcondition-hole | 5 | 5 | ANALYSIS, STORAGE, CLOSURE | 3 |
| unresolved-calls/direct-plain | B1 | B1 | B1 | not pinned |
| unresolved-calls/direct-seeded | B1 | B1 | B1 | not pinned |
| unresolved-calls/entry-initialized-plain | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/entry-initialized-seeded | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/entry-partial-plain | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/entry-partial-seeded | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/erased-pointer-plain | 1 | 1 | B1, ANALYSIS | not pinned |
| unresolved-calls/erased-pointer-seeded | 1 | 1 | B1, ANALYSIS | not pinned |
| unresolved-calls/fn-pointer-plain | B1 | B1 | B1 | not pinned |
| unresolved-calls/fn-pointer-seeded | B1 | B1 | B1 | not pinned |
| unresolved-calls/fn-trait-pointer-plain | B1 | B1 | B1 | not pinned |
| unresolved-calls/fn-trait-pointer-seeded | B1 | B1 | B1 | not pinned |
| unresolved-calls/generated-positive-plain | 1 | 1 | B1, ANALYSIS | not pinned |
| unresolved-calls/generated-positive-seeded | 1 | 1 | B1, ANALYSIS | not pinned |
| unresolved-calls/global-escaped-plain | B1 | B1 | B1 | not pinned |
| unresolved-calls/global-escaped-seeded | B1 | B1 | B1 | not pinned |
| unresolved-calls/item-return-initialized-plain | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/item-return-initialized-seeded | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/item-return-uninit-plain | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/item-return-uninit-seeded | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/pending-ops-plain | B1 | B1 | B1 | not pinned |
| unresolved-calls/pending-ops-seeded | B1 | B1 | B1 | not pinned |
| unresolved-calls/tuple-maybe-uninit-plain | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/tuple-maybe-uninit-seeded | 4 | 4 | B1, ANALYSIS, STORAGE | not pinned |
| unresolved-calls/virtual-plain | B1 | B1 | B1 | not pinned |
| unresolved-calls/virtual-seeded | B1 | B1 | B1 | not pinned |
| unresolved-calls/wrapped-pointer-plain | B1 | B1 | B1 | not pinned |
| unresolved-calls/wrapped-pointer-seeded | B1 | B1 | B1 | not pinned |

See DEPENDENCY-REVIEW.md for the ANALYSIS/late-fixture gate and E1/model seam; BASELINE-DELTA.md for all submitted-fixture changes; DOCS-MAP.json/MD for line ownership; SEMANTIC-LINEAGE.json for all 21 old semantic rows / 22 final selectors.

Strong oracles: exact summaries distinguish check counts from covers; P2 and postcondition-hole N3 = two checks for one read plus outer ensures17. Replace N2 = read checks only. Clause N1 = transmute read; frame N1 = user outside write with lawful out-write SUCCESS. All seven modes and all seven composition roots remain. No broad FAILED/Unsupported substitute. Split roots do not establish mixed isolation.
