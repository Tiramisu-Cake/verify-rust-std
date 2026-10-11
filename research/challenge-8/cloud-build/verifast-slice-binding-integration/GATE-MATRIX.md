# Slice binding candidate I: gate matrix

Tool `b6cb276afd13107c2a90ca50acbb12ff0a992dd8`, profile `verifast-slice-as-mut-ptr-native-c3-20261011-i`. First Build `5cb5b5d3-e4d6-4185-9234-f3a89e79829e`, delivery `7f5f88b54d9d631fee24ec84ab868d42c2f174b3`, console `9fc7c65b438e41ad014a08fe2f8b3e8f9b296866e010d8c423468b21565b3fd5`. Independent raw reviews: [binding](../../verifast-review/slice-as-mut-ptr-20261011/RAW-EVIDENCE-REVIEW.md), [compatibility](../../verifast-review/slice-as-mut-ptr-20261011/COMPATIBILITY-REVIEW.md). **READY_FOR_INTEGRATION_REVIEW**, using independently reviewed same-tool evidence from first Build plus supplement `d7e340fc-4cb9-4bd1-8a3f-d43d84fdf1d6` / delivery `99deac7a0275359124038d134aa46a08e5131fe6`. Owner adoption remains OPEN. Raw Cloud FAILURE and machine-incomplete flags remain unchanged. Corrected complete full runner `0371f4f8` is UNRUN.

| Required group | Reviewed result | Evidence / boundary |
|---|---|---|
| Exact method / receiver / casts | PASS scoped source admission | Full pinned slice source, exact methodbody, normal/readonly MIR actual T and MaybeUninit calls; runner checks external to translator |
| Generic / MaybeUninit components | PASS, 53 / 53 statements | First Build, unchanged copied methodbody; full native normal return/leak checks |
| Isolated actual-call consumer | PASS, 63 statements | Two actual as_mut_ptr calls, pointer value relations, preexisting source/MU frames restored |
| Wrong pointer | Intended VC observed | `v_base != source_base` first assertion failure after actual calls |
| Missing raw rights | Intended VC observed | Unrelated `array<T>(unrelated,1,_)` chunk missing on reached unequal-pointer branch |
| MU to initialized T | Intended VC observed | Existing `array<MaybeUninit<T>>`/foreach retained; initialized `array<T>` missing on reached len>=1 branch |
| Three slice source mutants | Expected admission refusals | Fullsource hash/body mismatch before verifier; not semantic negatives |
| Native C1 / C4 | PASS, 196 / 485 statements | Same console; exact paired source/fullMIR/refinement; four actual callbacks in guarded native C4 |
| Native posts / unwind / admission | Expected outcomes, 8 + 11 cases | False normal / four callback unwind VCs separately from default-off/mixed/malformed/source/extra-body refusals |
| Fresh bounded C4 controls | 9 intended VCs observed | First Build fresh adapter rows; historical rows in integration aggregate are not new-profile credit |
| ZST / non-ZST / MU / C/C++ | Expected outcomes, 11 cases | Nine Rust model cases plus C/C++ with `-shared`, one statement each, link successful |
| Nine selector bodies / bounded C4 / composition | PASS, 141 / 370 / 466 statements | First Build same invocation producer seal and typed location-only transport; fresh supplement repeats all three with new producer receipt, same 141/370/466 counts |
| FRAME / thread / CURRENT / original pointer / posts | 6 intended composition VCs observed | Raw first errors at agreed sites, no pointer-right grant |
| Cleanup / source-contract-type-Move-edge admission | Expected targeted outcomes | Three unreachable cleanup spans justified; partial opt-in and reachable-cleanup exact refusals distinct from VCs |
| Basic strict lifetime | Four expected outcomes observed | First Build raw logs; outer positive not completed in first Build |
| Outer-F positive Bool closure | PASS, 95 statements, reviewed supplement | Registration, actual callback103, both cut106/recovery/post/leak paths, six locals inside scope; not metadata-negative |
| Pointer-value / ManuallyDrop | Reviewed expected outcomes, fresh supplement | Two pointer cases incl no-pointee-rights VC; five MDnew cases incl expected should_fail post harness outcomes, distinct from printed VCs; H results retain H pins |

Normal/unwind posts remain present; the pure pointer-cast method has no actual unwind path, so binding positives establish normal return/leak closure, not observed unwinding execution. Native/callback unwind controls are separate. Historical first Cloud FAILURE and SETUP_OR_EXECUTION_FAILURE aggregate remain unchanged. Missing outer manifest pin was setup failure, never negative credit.

The translator lowers the exact symbol/substitution shape/one argument; it does not independently enforce the sourcebody or fullreceiver compiler signature. Qualification uses pinned compiler/welltyped MIR and runner source/refinement checks. No new heap permissions, writable authority, initialized-T, lifetime or alias facts. Unknown methods keep former lowering; no default-off mode exists for this unconditional exact-symbol binding.

Actual caller len+16, public ZST guard correspondence, native C4+select/fullsort4, broader O23/reference-output metadata negative, inherited assumptions, full upstream regression coverage and owner adoption remain OPEN. They do not block this narrow existing-fixture binding/compatibility candidate, and receive no proof credit. Separate nativeC4 and old bounded composition do not prove their connection.

The supplement repeats four strict-lifetime cases and the outer Bool positive, two pointer-value and five retained ManuallyDrop cases. Its only ten completion blockers are immutable raw-review-pending labels now addressed by the independent note; no raw result is edited. Same console and seven source/spec hashes were checked before its verifier invocation. Slice/native groups are NOT_RERUN references to the first fresh I Build, not H evidence and not fresh supplement proofs. The false normal/unwind ManuallyDrop tests use the unchanged verifier `-allow_should_fail` harness at source annotations; their expected outcomes are not presented as printed error VCs. No remaining mandatory gate in this exact fixture scope is open. The assessment is human review readiness, with no profile acceptance or full caller theorem.
