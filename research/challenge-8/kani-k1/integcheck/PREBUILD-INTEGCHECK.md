# INTEGCHECK — exact pre-build packet

Worktree `/root/verify-rust-std-kani-integcheck`, branch `experiment/kani-k1-integcheck-20261106`.
Owner `k1-merge`; stages/request IDs/ledger use `integcheck-*`. Task `3dc83a02baf16c2115d84011d1665bc68dde043b`.
**GO received from coordinator, 2026-11-06:** review f10ab8c743 accepted with only the G1 timeout/cap correction below. The resulting correction commit has advance exact GO; G2 promotion is authorized only after G1 is fully accepted. No build submitted at this correction commit.

Library reference `85ced7f8a8bcdf6b4ffe2e29a65d1d940ff10737`; entire library tree
`def2d65ddc5e73ed6ccb94df0afbb36e475d80d8` equals RENAMEMODS byte-for-byte.
No library commit or source edit. All lane paths equal tooling base
`59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Only research request/expectation/review/ledger files are changed. No local compiler or verifier was invoked.

## Requests and limits

G1 root `../RUN-REQUEST.json` is byte-identical to this directory’s `RUN-REQUEST.json`.
Request `integcheck-g1-20261106-01`, SHA256 `3c5bc03f8e54ab920f2a1f76908663a9b0a9cb0cff35b49da4760b9dbcb0d542`.
Kind diagnostic, controls=true, inventory=false, kani_jobs=1, gcb-e2-standard-4.
Exactly 21 rows: 13 expected FAILED controls, each with an explicit expect_check, plus eight SUCCESS pair rows.
Per-root timeout **4 minutes (240 s)**; paid build timeout **114 min**, runner cutoff **108 min after validate**.

G2 `G2-RUN-REQUEST.json`: `integcheck-g2-20261106-01`, SHA256 `82ceb5befff1ea704280139081bbedeb04ebb103661432e540deee0aa1b62d6a`.
Kind inventory, controls=true, inventory=true, standard4, harnesses=[]; no proof verification.
Whole-job request budget **44 min**; paid timeout **74 min**, runner cutoff **68 min after validate**.
The unchanged runner caps list itself at 60 min within that cutoff. Controls cfg is exported before list
in kind inventory; using diagnostic inventory would list cfg-off names and is deliberately avoided.

## All 13 negative controls

Full names, prior/new check texts, current exact coordinates, source file hashes and bound RESULT
identities (commit/blob/SHA256) are in [controls-expected.json](controls-expected.json).
Names below are relative to `verify::`; files are relative to `library/core/src/slice/sort/shared/`.
Expectations come from the designated RESULT and authorized NEWPINCAL `732c4e25b2`.
The coordinator’s 2026-11-06 clarification allows our referenced RESULT and explicitly marked source-only
expectations. All 13 controls have a precise RESULT expectation; no source-only fallback is needed.
Current lines below are located in the final tree; renamed literals/comparator follow RENAMEMODS maps.

| Control | RESULT | expect_check | Current designated location |
| --- | --- | --- | --- |
| `fixed_inputs::reject_mutant_swap_u8_n2` | NEWPINCAL | `assertion failed: v[0] <= v[1]` | `smallsort/verify/fixed_inputs.rs:25` |
| `merge::profiles::profile_full_value_checker_rejects_payload_change_u8` | PINCHECK | `full-value checker detects payload corruption` | `smallsort/verify/merge/profiles.rs:347` |
| `merge::profiles::profile_wrong_f_insert_rejected_u8` | PINCHECK | `profile_canonical_comparator::<P>(cmp)` | `smallsort/verify/merge/profiles.rs:273` |
| `merge::profiles::profile_wrong_f_merge_rejected_u8` | PINCHECK | `profile_canonical_comparator::<P>(cmp)` | `smallsort/verify/merge/profiles.rs:311` |
| `merge::profiles::profile_wrong_f_sort4_rejected_u64` | PINCHECK | `profile_canonical_comparator::<P>(cmp)` | `smallsort/verify/merge/profiles.rs:237` |
| `merge::profiles::profile_wrong_f_swap_rejected_u8` | NEWPINCAL | `profile_canonical_comparator::<P>(cmp)` | `smallsort/verify/merge/profiles.rs:212` |
| `tag_permutation::reject_duplicate_network_u8_n9` | PERMTAGS | `every input tag occurs exactly once` | `smallsort/verify/tag_permutation.rs:55` |
| `helper_contracts::rejects_insert_tail_equal_begin_u64` | REALCONTRACTSTWO | `begin < tail` | `smallsort.rs:589` |
| `helper_contracts::rejects_merge_overlapping_dst_u64` | REALCONTRACTSTWO | `merge_contract_regions_disjoint(v.as_ptr(), dst, v.len())` | `smallsort.rs:859` |
| `helper_contracts::rejects_swap_comparator_writing_outside_frame_u8` | TIDYDOCS | `Check that *var_9 is assignable` | `smallsort/verify/helper_contracts.rs:250` |
| `helper_contracts::rejects_swap_outside_backing_u8` | REALCONTRACTS | `crate::ub_checks::can_dereference(v_base.wrapping_add(b_pos))` | `smallsort.rs:410` |
| `forwarding_contracts::rejects_always_true` | PINCHECK | `canonical comparator required` | `smallsort/verify/forwarding_contracts.rs:60` |
| `forwarding_contracts::rejects_payload_corruption` | PINCHECK | `full-value checker rejects payload corruption` | `smallsort/verify/forwarding_contracts.rs:270` |

Acceptance is stricter than a green lane gate: each control must be FAILED with **exactly one failed
check**, its complete description and file/line matching the designated assertion/requires/write-set
check above. Require untruncated failed-check evidence and reconciliation with the reported failed count.
Any other failure, extra failure, missing coordinate, TIMEOUT/OOM, missing result or truncated composition
means the control is not calibrated. `Check that *var_9 is assignable` is the counter write at
helper_contracts.rs:250, not a blanket permission for any write-set failure.

## Four leaf/consumer pairs

All eight rows expect SUCCESS, zero failed checks, the same reachable covers as their earlier RESULT.
[pairs-expected.json](pairs-expected.json) binds old/new names, prior times and cover counts to RESULT SHAs.

| Pair | Row relative to verify:: | Current required covers | Prior time s | Prior RESULT |
| --- | --- | ---: | ---: | --- |
| 1 leaf | `helper_contracts::swap_safety_u8_backing9` | 6/6 | 17.355093 | REALCONTRACTSTWO |
| 1 consumer | `helper_contracts::unstable_network_safety_u8_n9_stubbed` | 1/1 | 11.660206 | REALCONTRACTSTWO |
| 2 leaf | `helper_contracts::swap_safety_u8_backing13` | 6/6 | 17.583559 | REALCONTRACTSTWO |
| 2 consumer | `helper_contracts::unstable_network_safety_u8_n13_stubbed` | 1/1 | 13.978799 | REALCONTRACTSTWO |
| 3 leaf | `helper_contracts_wide::swap_safety_u8_backing32` | 9/9 | 31.575 | VEIGHTROWS |
| 3 consumer | `helper_contracts_wide::unstable_network_safety_u8_n32_stubbed` | 5/5 | 104.319084 | VEIGHTROWS |
| 4 leaf | `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` | 5/5 | 86.45552 | VEIGHTMAX |
| 4 consumer | `helper_contracts_wide::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` | 4/4 | 8.113433 | VEIGHTMAX |

Expected reachable covers sum: **37/37**, with no unreachable covers in the current eight rows.
REALCONTRACTSTWO reported N9/N13 consumers as 1/3: one reachable return, two unreachable callback covers.
The current explicit `stub(comparison_covers, omit_comparison_covers)` omits those two in both consumers
(helper_contracts.rs:86,94). Reachable count remains one; total is now 1/1. TIDYDOCS already measured N9
as 1/1 at 7.0849905 s; N13’s current 1/1 total is **по исходнику** and must be measured in G1.
The table keeps the task’s REALCONTRACTSTWO timing baseline for both pairs; it does not replace historical
1/3 with a fabricated measurement. Non-cover unreachable checks remain separate.

## Timing and budget feasibility

The longest latest task-specified successful pair row is VEIGHTROWS N32 consumer **104.319084 s**;
240 s leaves **135.680916 s (130.06%)** per-root margin (coordinator rejected the previous 120 s limit). Merge8 was 86.45552 s; other selected rows were shorter.
This is a planning allowance, not a guarantee against runtime variation. A timeout is a failed integration
outcome, not grounds for retry or an unreviewed timeout change.

G1: 21 × 4 = 84 harness-minutes; runner bound 84 + 24 = **108 min**, paid bound 84 + 30 = **114 min**.
Reserve **$1.5390** at $0.0135/min. Prior inventory=false runs started verify ~348–366 s after validate;
TIDYDOCS cfg-on reached first CBMC ~68 s into verify. Allow **12 min** total for setup/compilation/
instrumentation: 108 − 12 = **96 min**, leaving the full 84 min of root limits plus 12 min extra slack.
No expensive full compiler list is combined with G1.

G2 uses RENAMEMODS/OPTINMOVE ~42–47 min inventory-build observations. Paid **74 min**, runner **68 min**
after validate, with list capped at 60 min: an 8 min setup allowance still leaves 60 min for compile/list,
at least 13 min over the ~47 min observation. These were cfg-off observations; cfg-on completion remains
unestablished and is an explicit acceptance requirement.

Combined maximum reservation: **$1.5390 + $0.9990 = $2.5380 <= $2.75**, remaining margin $0.2120.
Own cap **$2.75** supersedes task $2.00 by the coordinator’s 2026-11-06 decision for this timeout correction.
At preparation: 250 project builds, used **$107.6595**, reserved **$0**, cap **$118.96**;
with both maximum reservations **$110.1975**. Refresh budget before each dispatch and ensure own spent
plus all live/planned reservations fit $2.75. Build limit2, retry0, repair0.

Main window **300 min + closeout30**. Execution T0/deadlines are recorded in the ledger at this GO;
retain these boundaries. Sequential maximum build time188 min fits the main window.
Use sequential G1 then G2; available pool/owner slot and budget remain prerequisites.

## Exact G2 publication and review boundary

The helper dispatches the pushed branch tip and permits only one build per source SHA. G1 therefore
dispatches the reviewed packet SHA with its root G1 request. G2 needs a subsequent ordinary research
`[skip ci]` commit promoting the **byte-identical** prepared `G2-RUN-REQUEST.json` to root RUN-REQUEST.json,
plus research-only ledger/finished-G1 evidence updates. Library, tooling, G2 request bytes and expectations
must remain unchanged. Push without force, bind the new source SHA and request hash in the ledger.
The task permits both builds under one packet GO. Such GO must explicitly cover this exact G2 promotion;
if GO names only the G1 source SHA, publish the G2 promotion for a new exact PRE-BUILD review/GO.
Preparation alone authorizes neither dispatch. No second build can reuse G1’s source SHA.

## Evidence collection and acceptance after GO

1. Confirm exact local/origin source SHA, unchanged library tree/tooling, own owner slot and refreshed
   project/own budget. Record approved scope, T0/deadlines and request identity in the ledger.
2. Dispatch G1 exactly once through `research/challenge-8/kani-k1/tools/k1g.sh dispatch
   experiment/kani-k1-integcheck-20261106`. Record build/source/request identities and reservation.
   Invoke `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD` and **end the turn**; no status loop.
3. After the completion wakeup, use bounded helper status, summary, `summary BUILD 0 21`, peaks, budget BUILD,
   and `check-tooling BUILD 59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`. Save outputs under G1 evidence.
   For the full failure composition and exact locations, use bounded log-grep with regex
   `^Checking harness |^[[:space:]]*[*][*] [0-9]+ of [0-9]+ failed|^Failed Checks:|^[[:space:]]*File:|^VERIFICATION:|^Complete -`
   and max200. Require complete attribution to all 21 rows and no saturation/clipping; refine targeted
   queries if needed. No raw log/cache/archive reads. Summary truncation never licenses acceptance.
4. Require Cloud SUCCESS, summary COMPLETE, gate/expectations true, expected Kani exit1, exactly13
   designated single-check FAILED controls and eight SUCCESS rows with all required covers and times.
   Bind build/source/request/Kani/pool/tooling identities; report any incomplete or contrary result.
5. Publish/dispatch G2 under the approved promotion scope or obtain its exact-SHA GO as described above.
   Record identities, invoke watch BUILD, end the turn. After completion use bounded status/summary,
   check-tooling, budget and inventory pages of at most80 names, following each reported next_offset.
   Require complete nonoverlapping pages, consistent build/source/request/Kani and inventory hashes,
   no duplicates, and exact set equality to [cfg-on-expected.txt](cfg-on-expected.txt) =246 names.
   Sorted names with a final newline must SHA256 to
   `3e03f6051cb8d0ab71d1a40f73c58234acbc7964315529ac9c603c49f9d222eb`.
   Preserve the distinction between native-order names hash, sorted names hash and artifact hash.
6. For both builds scan relevant locations with bounded log-grep `[-]> .*smallsort(/verify([/.]|$)|[.]rs)`
   (max200), and targeted warning/unused scans as necessary. Existing targeted scans in RENAMEMODS/
   OPTINMOVE cfg-off and LEANHELPERS cfg-on report no match. Require no new warnings in smallsort/verify;
   any match must be classified from bounded evidence. A saturated generic warning sample cannot
   establish absence; preserve uncertainty if bounded output cannot resolve the warning.
7. Write RESULT-INTEGCHECK.md <=40 lines: library SHA/tree/equality, full13 control failures and match,
   eight pair statuses/time/covers/prior time, cfg-on count/sorted hash/exact match, warnings and cost.
   Update ledger with actual spend and outcomes; commit/push research `[skip ci]` without force.
   Finish `REVIEW REQUEST <sha>` / `INTEGCHECK ЗАВЕРШЁН`, then stop. No further proof scope or dispatch.

Pre-build checks establish request/source/expectation consistency only. Runtime calibration, integrated
pair proof and cfg-on compiler inventory remain pending. No universal T/F, uninit/value-validity or
panic-unwinding claim is introduced.
