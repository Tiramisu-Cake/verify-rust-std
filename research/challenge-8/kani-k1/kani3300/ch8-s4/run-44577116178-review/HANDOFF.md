# HANDOFF — independent review of S4P3 run 44577116178

**APPROVE N8 and N9 as exact bounded SOURCE_REPORTED S1 candidates. APPROVE the N13 and N17 BLOCKER classifications and censored-cost reporting. Zero blocking findings; zero required changes.** Approval of the last two classifications supplies no positive candidate: both remain ineligible without completed same-invocation inventories. No admission, ledger entry, newly qualified leaf, closed proof obligation or independent B1/B2 credit is created by this review.

Reviewed w14 intake commit **8bf99aa314310e4a3d5b86b8d0f112ddff2886ab**. `review.py`, adapted from the S4P2-r2 independent checker, directly reads the authenticated compact member and pinned Git objects, imports no intake modules and records every exact U property dictionary, invocation, member hash, source identity and independently assessed argument in `REVIEW.json`. The original intake is unchanged.

## Per-case verdicts

All four source roots use initialized V34/base1, all 34 independent full-domain u8 values, `KeyLess<u8>`, Original/Proof registration in core, target null and no positive stubs, verified stubs, providers or summary edges. These are exact finite domains; neither a general network theorem nor an extension of the historical S1 smoke theorem is asserted.

| Case / exact root | Invocation ID | Native inventory | Required roles / covers | Verdict and scope |
| --- | --- | --- | --- | --- |
| N8 `s4p3_network_b01_n08_fullbyte` | `fe373c1bdded4ac4803b3ca7136359c0` | 258 properties: 241 SUCCESS, 11 U, 6 SAT | 4/4 SUCCESS; 6/6 SAT | **APPROVE**, exact S1 candidate |
| N9 `s4p3_network_b01_n09_fullbyte` | `a44f674c95fa4dc8acd37fd9253aa9e4` | 258 properties: 241 SUCCESS, 11 U, 6 SAT | 4/4 SUCCESS; 6/6 SAT | **APPROVE**, exact S1 candidate |
| N13 `s4p3_network_b01_n13_fullbyte` | `2db2b7d35b6f4e9f983d6e787d5a025b` | UNKNOWN; INCOMPLETE | all roles/covers UNKNOWN | **APPROVE BLOCKER classification**, no positive candidate |
| N17 `s4p3_network_b01_n17_fullbyte` | `bde7d953e8d542d9a05f74cd268ef8eb` | UNKNOWN; INCOMPLETE | all roles/covers UNKNOWN | **APPROVE BLOCKER classification**, no positive candidate |

**N8:** the literal call is `[1..9]`, length8. At smallsort340 the early-return condition is false; no_merge at351 is true and354 constructs a region of exactly8. The conditions at360/363 select neither sort13 nor sort9, giving presorted_len1. At370 the actual insertion helper is called with offset1: its guard715 permits1<=8, tail727 starts at index1, and loop728 invokes insert_tail731 for suffix indices1..7. If this call returns normally,372–373 immediately returns from the network caller. A nonreturning call cannot continue to381/389 either. N8 does not supply an actual sort9/sort13 or merge result.

**N9:** the literal call is `[1..10]`, length9. The same no_merge branch selects the whole region9. At360 the >=13 test fails;363–365 calls actual sort9_optimal and sets presorted_len9. Its own source500–540 contains the length guard and25 swap_if_less calls, with no replacement registered in this invocation. In insertion_sort_shift_left, offset9 equals len9: tail727 equals v_end726, so loop728 has no suffix iterations. Normal continuation returns at372–373 before381/389. This is the actual length9 network path, assessed separately from N8's insertion path.

**N13/N17:** literal `[1..14]`/`[1..18]` source calls select sort13, with no suffix for13 and insertion suffix13..16 for17. Both lengths also have no_merge=true. These are source branch facts only, not native proofs. Their captured registrations establish invocation/source context; they do not establish roles, SAT covers or safety. The native exports have no `harnesses` field. Rich exports retain an empty selector placeholder and `missing regular harness RESULTS`; the review preserves null/UNKNOWN inventories rather than counting that placeholder as zero checks or success. No evidence from N8/N9 is lent to these cases.

## Every U is assessed at its exact domain and site

All **40** observed U records match the authenticated member and the exact std commit/file SHA256/line, namespace and invocation, with no duplicate, missing or additional argument. `REVIEW.json` preserves each full native dictionary and reviewer argument. Counts are **28 source-path exclusions +12 generated failure-edge exclusions**: 11 U per completed positive and18 U across the four fixed negatives. Nothing is inferred about N13/N17 U counts.

For **each** of N8 and N9, the four exact `bidirectional_merge::<u8, ...KeyLess<u8>>.assertion.1` through `.4` records at smallsort974/990/991/992 and `small_sort_network::<u8, ...KeyLess<u8>>.assertion.3` at381 are excluded by that case's caller branch described above. Neither second-region update381 nor merge call389 is reachable after the first region. The callee's `intrinsics::assume` supplies no premise. These ten records are not excused merely because both lengths are small or because their status is U.

The other **six U per positive** have separate source-local definedness arguments:

| Exact property ID suffix / source site | Checked premise and excluded error edge |
| --- | --- |
| `num::<impl usize>::abs_diff.assertion.1`, uint_macros3222 | self<other selects other-self, which cannot underflow |
| `num::<impl usize>::abs_diff.assertion.2`, uint_macros3224 | else implies self>=other, so self-other cannot underflow |
| `num::<impl usize>::is_multiple_of.assertion.1`, uint_macros3916 | rhs=0 has its own match arm; remainder requires rhs!=0 |
| `ub_checks::is_valid_allocation_size.assertion.1`, ub_checks148 | size=0 bypasses division; division requires size!=0; u8 also has size1 |
| `ptr::const_ptr::<impl *const ()>::is_aligned_to.assertion.1`, const_ptr1479 | continuation follows the nonzero power-of-two check, so align-1 cannot underflow |
| `fmt::Arguments::<'_>::from_str.assertion.1`, fmt820 | literal shift count1 is below x86_64 usize width64; no high-bit preservation or transmute-validity claim |

These exclude the specified generated **failure edges**; they do not establish why the producer marked the check instructions themselves UNREACHABLE. Compiler/emitter causality remains UNKNOWN. The S1 source-local method permits this distinction. No native U is relabelled SUCCESS, and SAT covers do not justify any U exemption.

The18 negative U arguments also use exact fixtures and source branching: order-corrupt `[1,2] -> [2,1]` and unchanged descending weak-seam len13 return at model98 before later sites100/106–118. The weak comparator seam is explicitly empty and registered only in the fixed negative. Count-corrupt32 has first-query multiplicities32/31; logical Cell `[0,1] -> [0,0]` has1/2, returning116 before118. These controls do not prove a general actual sort13 failure or a Cell provider theorem. Each negative retains exactly its intended FAILURE label and no additional FAILURE.

## Non-vacuity, safety, guards and locations

Each completed positive has the four exact labelled assertions ACTIVE_CONCRETE_MODEL, SORTED_FULL_VALUE_COUNT, FULL_OUTSIDE_FRAME and ARBITRARY_OUTSIDE_CANARY **SUCCESS** in its own invocation. N8 source lines24/30/32/36 and N9 lines47/53/55/59 match the pinned declarations. All declared covers are SAT: length, unsorted input, duplicate, nonconstant output, descending input and useful return. N8 covers37–42 and N9 covers60–65 occur after the helper call and all four roles, including the nonempty34-iteration frame loop and arbitrary outside canary. These supply continuing witnesses; a required role marked U would remain a blocker.

The complete per-positive partition is252 non-cover checks=241 SUCCESS+11 U, plus6 SAT covers. All safety IDs and class/status partitions match the full native dictionaries and `NON-VACUITY.json`; no FAILURE, unknown/error status or unsatisfied cover is hidden. Both have requested/resolved unwind36 and **zero exported class=unwind records**. Zero is the exact residual exported inventory, not an invented unwind assertion or a theorem that36 suffices for larger lengths. Full safety/unwind inventories for N13/N17 remain UNKNOWN.

All **655** observed records have positive coordinates; std coordinates lie within the actual pinned files. The seven non-std location records were checked individually: ToISize model203 in NEG-Cell/N8/N9, plus memcpy.pointer.1/.2 pseudo-lines33/34 in each completed positive. Each ToISize SUCCESS record has the retained SUCCESS `to_isize.safety_check.1` sibling (`Offset value overflows isize`) and the pinned stock model's failed-conversion branch. The builtin records are native backend displays; actual builtin source/lowering origin is UNKNOWN. No coordinate is invented, no missing-location precedent is transferred and no generic parser/std/builtin waiver is proposed.

Seven SUCCESS unsupported guards remain present: one in NEG-Cell and three per positive. Pinned stock producer semantics retain a failing assertion plus assume for unsupported operations; these guards report no reachable violation in the bounded invocation. They grant no general operation/panic/unwind support. The producer's strict empty-array rejection remains in force. N13/N17 guard inventories are UNKNOWN.

Applied `S1-ACCEPTANCE-DECISION-2026-11-17.md` and the exact S4P2-r2 review discipline: individually justified U, source-reported registrations and full domains, located/non-U required roles, SAT covers and complete inventories. Independent compiler/AST/MIR proof is neither claimed nor added as an extra S1 gate. Historical exact-run S3/S4 location decisions provide a method, never a transferable exemption.

## Censored cost and next-attempt options

Campaign elapsed **1722.9530094749998s** is distinct from connected-job, setup, child and native verification time. N8's exported verification is109.308341638s, whole child143.320s; N9's is207.137589015s, whole child242.435s. These are not exclusive solver times.

| Case | Initial-export marker upper bound | Whole child through termination | Completed native verification | Termination |
| --- | --- | --- | --- | --- |
| N13 | 33.869s | 600.071s | UNKNOWN_CENSORED | timeout, original exit−15, SIGTERM15 |
| N17 | 32.884s | 600.152s | UNKNOWN_CENSORED | timeout, original exit−15, SIGTERM15 |

The compile markers precede the180s compile subcap. Child shutdown/containment is verified and no outer/RSS cutoff is reported. Supervisor exit0 is distinct from native child exit−15. Sampled, non-atomic PGID/owned-process VmRSS is not a kernel/cgroup/full-tree maximum, and component peaks need not be simultaneous. Initial-export markers are compile/link observation upper bounds, not exclusive compiler CPU.

Only the existing compact receipt tails were examined. N13 prints symex3.62284s,106518 expression steps,7885/1976 generated/remaining VCCs and six completed SAT messages; N17 prints5.69742s,149116 steps,13277/2914 VCCs and five messages. Both tails end `Running propositional reduction`. These partial observations have neither complete property IDs nor timestamps at termination: they identify no required SAT cover, successful role, expensive property, stalled phase or helper/oracle bottleneck. Arithmetic differences566.202/567.268s after the marker are not exclusive backend/solver cost. Completed verification cost, exact speedup and a sufficient next cap remain UNKNOWN;600s is a censoring threshold, not a completion measurement.

The four planning options are sound with their stated conditions:

1. Prepare bounded per-property/stage timing with monotonic boundaries and exact IDs; independently review reporting and timeout/error paths before a new GO.
2. Consider a separately reviewed higher child cap, recalculating child/slot/campaign/outer/phase/step envelopes and cleanup reserve under fresh budget/window/ledger authorization. Current evidence guarantees no sufficient cap.
3. Use measurements to choose source-preserving backend/checker optimizations, with new exact pins, equivalence reasoning and review, keeping full sortedness/value-count/frame/canary, byte domain, safety/unwind checks, controls and covers.
4. Diagnose N13 before N17 while retaining required negative controls. These invocations are already singleton and serial; reducing campaign selection alone does not remove a per-child600s timeout. No incompatible cross-run property composition or automatic retry/admission follows.

No option is executed or authorized by this review.

## Identities, validation and preserved history

Run44577116178/attempt1; std **7b31b060b90ce286e94547993f6a698c549bc5fa**; stock tool **0aac16ef62da9e9d5645782d458593e5d78143ba**; control **65a9ea656a4b5f1e66f7b31eceffb5eefeba7541**; trigger **960cc686097c093fe0d64f73f4f4a9736e06eec2**. Trigger and reviewed control have the same tree and sole parent, not a parent/child relationship. Request SHA256 `693e12689bfee859560d5042a36fd8b80051e9fca4082fd1a612642d7e389e30`; workflow SHA256 `fc21d9f44a403b6294daaca2b25fdfcebe38d3dd7e89a927af0d289a86c177a0`.

Compact gzip SHA256 `57bb8bf06ec7115d9a188a7a19089f4c3e7ecce77793a7c76541bf21616736cf`; decompressed structured payload SHA256 `8431646bbe82f1d3f47e45adabd9d1c5c5a6664b64ce794fc8c5401c8bd46a15`. All119 structured member hashes and byte counts match. The manifest and all47 listed intake files match the reviewed commit. No reacquisition was performed.

Independent review: **2,351 checks PASS**. Frozen reference replay: **943 checks PASS**; audit: **1,518 checks PASS plus10 adverse checks**; addendum: **136 checks PASS**; cost analysis: **14 checks PASS**; packet check: **165 checks PASS**; original seal: **47 files PASS**. Reference modules ran in clean interpreters with a compare-only JSON writer. Regenerated projections match committed bytes except RESULT.json object-key ordering; its parsed values are exactly equal. The first strict-byte replay stopped at that cosmetic difference; the successful rerun records the explicit formatting-only comparison in `VALIDATION.json`. The intake files remained byte-identical throughout. These are offline source/reader/reporting checks, not fresh native verification.

The original partition remains **599 SUCCESS +4 intended FAILURE +40 UNREACHABLE +12 SAT =655 observed properties in six complete inventories**; two further inventories remain UNKNOWN. Workflow FAILURE, SELECTED_PARTIAL, strict0/8, ZERO_U/REJECT_ALL, disabled proposal and every `s3_expected_match=False` remain historical facts. No original receipt, rejection, accounting record or ledger is rewritten.

**HANDOFF; requested one-stage independent review complete.** Coordinator may separately assess only the two approved exact candidates. N13/N17 remain BLOCKER. Admission/newly qualified leaves/newly credited obligations/independent B1/B2 credit from this review: **false /0 /0 /NONE**. Residual lengths/types, generic/provider/summary/caller/initmask/ownership/panic/Drop/fullN16/N32 and independent compiler/emitter/MIR obligations remain open. Only this review directory changes. No acquire.py, compiler/Kani/CBMC/full runner, CI, push, ledger/admission or external messaging action. Local commit uses `[skip ci]` and Tiramisu-Cake <igkharin@gmail.com>; its SHA is returned separately.
