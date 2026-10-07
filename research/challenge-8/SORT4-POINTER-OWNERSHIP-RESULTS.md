# Pointer MaybeUninit ownership phase results

2026-10-07: IN PROGRESS. Entry e0920ecb07cd05ef08acd6fb5a2fb228af9a1f98.
Model and constructor UNACCEPTED pending full hosted matrix; actual callee NOT RUN.
New budget 265/5400 summed hosted job seconds; no active run.
See [phase and pre-implementation trust decision](SORT4-POINTER-OWNERSHIP-PHASE.md).

O1 [37598560122](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37598560122),
SHA798863a89d8d9420670dd8b3c56766a861a6db34, patch31d3ca50, artifact
smallsort-research-37598560122-1/11471388654: full MIR/source/export/decode/
refinement and14baselines passed; SAFE prototype needs defined own chunk BEFORE
body. Body/acceptance/negatives/actual callee NOT RUN; O2 tests checked introduction.

O2 [37599522829](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37599522829),
SHA0f5b790cc58b30ee3aee12e8989a169e19998fb5, patch023e12f0, artifact
smallsort-research-37599522829-1/11472570359,128s: constructor+defined ownership
introduction SAFE prototype/body/frame return/leak PASS54statements;5intended
proof negatives PASS.14baselines PASS. Model/constructor acceptance withheld
pending complete metadata/source/MIR controls; integer ownership omission and
applicability classification errors are harness fixes. Actual callee NOT RUN.
