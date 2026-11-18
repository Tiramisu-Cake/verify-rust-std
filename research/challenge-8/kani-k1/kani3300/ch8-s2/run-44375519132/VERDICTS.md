# Native verdicts and strict qualification

Full11 = 5 positive/6 exact negatives/20 covers. Selected9 = 4 positive/5 exact negatives/16 covers. Deferred general32 pair = 1 positive/1 exact negative/4 covers, NOT_SELECTED/UNKNOWN. No fullN32 or full11 qualification follows from this partial campaign.

| Root | Selection | Expected / assurance | Compile / native start | Native verdict | r5_expected_match | Stored status / collector outcome |
| --- | --- | --- | --- | --- | --- | --- |
| checker_order_corrupt | SELECTED | DETECTED / NEGATIVE_CONTROL | COMPLETE / OBSERVED_SINGLETON | FAILURE | False | OBSERVED / RECORDED |
| checker_count_corrupt | SELECTED | DETECTED / NEGATIVE_CONTROL | COMPLETE / OBSERVED_SINGLETON | FAILURE | False | OBSERVED / RECORDED |
| swap_pfc | SELECTED | SUCCESS / QUALIFICATION_ATTEMPT | COMPLETE / OBSERVED_SINGLETON | SUCCESS | False | OBSERVED / RECORDED |
| sort13_weak | SELECTED | DETECTED / NEGATIVE_CONTROL | COMPLETE / OBSERVED_SINGLETON | FAILURE | False | OBSERVED / RECORDED |
| merge32_real | SELECTED | SUCCESS / ACTUAL_BODY | COMPLETE / OBSERVED_SINGLETON | UNKNOWN | False | UNKNOWN / UNKNOWN |
| sort13_assumed | SELECTED | SUCCESS / DIAGNOSTIC_ASSUMED | COMPLETE / OBSERVED_SINGLETON | UNKNOWN | False | UNKNOWN / UNKNOWN |
| merge_count_corrupt | SELECTED | DETECTED / NEGATIVE_CONTROL | FAILED / UNKNOWN_NOT_PUBLISHED | UNKNOWN | NOT_RECORDED | INTERRUPTED / UNKNOWN |
| merge_order_corrupt | SELECTED | DETECTED / NEGATIVE_CONTROL | NOT_STARTED / NOT_STARTED | UNKNOWN | NOT_RECORDED | NOT_RUN / UNKNOWN |
| summary_witness | SELECTED | SUCCESS / MODEL_DIAGNOSTIC | NOT_STARTED / NOT_STARTED | UNKNOWN | NOT_RECORDED | NOT_RUN / UNKNOWN |
| general32_assumed | DEFERRED_NOT_SELECTED | SUCCESS / DIAGNOSTIC_ASSUMED | NOT_STARTED / NOT_SELECTED | UNKNOWN | NOT_RECORDED | DEFERRED_NOT_SELECTED / UNKNOWN |
| general32_weak | DEFERRED_NOT_SELECTED | DETECTED / NEGATIVE_CONTROL | NOT_STARTED / NOT_SELECTED | UNKNOWN | NOT_RECORDED | DEFERRED_NOT_SELECTED / UNKNOWN |

All three completed negatives retain native COMPLETED/FAILURE and one failed assertion, native exit1, PANICS_ONLY. Actual failed description is exactly `This is a placeholder message; Kani doesn't support message formatted at runtime`. Exact regular-stream/rich-export agreement is checked by the reviewed collector; description is not an accepted S2_NEG role. Same source file for all: `/home/runner/work/kani/kani/export/library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs`, SHA e0f47062d71f256fed49b8ad8144c2a83c9a96ecd85646605b1c2fe9b707d0dc. Native line is retained as a string; expected oracle line is the exact pinned source assertion. The count case also mismatches assertion identity `.2` vs `.1`. No reclassification or label waiver is approved; separate stub-confirm policy does not apply.

| Negative | Actual failed property | Source line | Expected property / role | r5_expected_match |
| --- | --- | --- | --- | --- |
| checker_order_corrupt | `slice::sort::shared::smallsort::verify::sorting_s2_batch::checker_order_corrupt.assertion.1` | 140 | `slice::sort::shared::smallsort::verify::sorting_s2_batch::checker_order_corrupt.assertion.1` / `S2_NEG_CHECKER_ORDER` | false |
| checker_count_corrupt | `slice::sort::shared::smallsort::verify::sorting_s2_batch::checker_count_corrupt.assertion.2` | 134 | `slice::sort::shared::smallsort::verify::sorting_s2_batch::checker_count_corrupt.assertion.1` / `S2_NEG_CHECKER_COUNT` | false |
| sort13_weak | `slice::sort::shared::smallsort::verify::sorting_s2_batch::sort13_weak.assertion.1` | 149 | `slice::sort::shared::smallsort::verify::sorting_s2_batch::sort13_weak.assertion.1` / `S2_NEG_SORT13_WEAK` | false |

swap_pfc native COMPLETED/SUCCESS, exit0, verification_time_s10.680759458, 322 total properties = 318 checks (314 SUCCESS/4 UNREACHABLE, zero failure/error/unknown) + 4 SATISFIED covers. PFC metadata kind ProofForContract target_fn=swap_if_less, contracted function name retained in JSON, no stubs/verified_stubs; unwind34, solver cadical, source line74. Unsupported constructs4 are recorded with SUCCESS status, not omitted. Exact covers S2_SWAP_EQUAL/TAKEN/REVERSE/USEFUL_RETURN at source84–87 all SATISFIED.

Qualification remains NOT_GRANTED; **stored and replayed r5_expected_match=false**, because the current strict success predicate requires zero unreachable checks and all318 success, and named successful S2_ACTIVE_SWAP_PFC/S2_SWAP_EXACT_TRANSFER/S2_SWAP_FULL_FRAME descriptions are absent. Actual four unreachable checks are num::usize::abs_diff assertions1/2, fmt::Arguments::from_str assertion1, ptr::const_ptr::is_aligned_to assertion1; full locations/IDs in JSON. Native SUCCESS is preserved. No assertion-origin/contract-origin inference from a formatted description or source coordinate.

Domain: swap harness u8/KeyLess<u8>, concrete [u8;15], nondeterministic a,b<13, actual swap_if_less on pointer+1, pair post/full frame. Qualification attempt for this context is separate from generic callee proof/admission. merge32 uses actual body for u8/32 with sorted16+16 halves, concrete destination/canaries, no final verdict. sort13_assumed uses verified-stub swap_if_less and remains DIAGNOSTIC_ASSUMED. general32 provider registrations/stubs (sort8, insert_tail, merge) are not proof of leaves. sort13_weak tests the faithful caller copy with weak s2_swap_seam; caller-copy/original identity restrictions remain. No causal main stub/contract diagnosis from this std run.

Two child600 cutoffs are UNKNOWN, not backend TIMEOUT600 or detected negatives; merge_count compilation interrupted without final inventory; two later selected NOT_RUN and deferred pair distinct. Required covers/role maps/oracles for each root remain explicit in VERDICTS.json, including absent final inventory. Only four covers have final satisfied observations, not the required selected16/full20. Exact compiler-instance/MIR/contract/property-origin binding remains UNKNOWN despite runner invocation/selector/crate/native metadata binding. Independent B1/B2 credit NONE, qualification/admission NOT_GRANTED, closed obligations0.
