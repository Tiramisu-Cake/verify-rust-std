# RESULT SPECFIX — StageA, PARTIAL (F03 OPEN)

Status: **PARTIAL / StageA**. The full atomic F03 transfer is not made; no new clause has proof
evidence (G1 compile error). Not "SPEC-FIX готов".
T0 2026-10-31T16:22Z (session start), deadline 21:22Z; work ended 17:35Z.
Base `d8f97fb2df` (library tree `9000a3c7a0`), cap `30f77e8599` unchanged (88.96).
Pin Kani `9461e07af7`, nightly-2026-10-12; tools/workflows/flags/toolchain untouched.

| Commit | Role | Library tree |
|---|---|---|
| `0b5cbd2a3b` | StageA source: specfix module, Drop profile, probe guard | `4865c40287` (built) |
| `938898a745` / `2d971415af` / `a2d75d911e` | review package; RUN-REQUEST G1 / G2 / G3 | `4865c40287` |
| `3282e976b0` | own revert of the stubbing harness (cfg-on only) | `31997f7781` (final, **not built**) |

## Builds (k1-standard4, all after coordinator GO)

| Build | UUID / request | Result | Own cost |
|---|---|---|---|
| G1 | `e6a1c83d-1a53-49ab-8c88-47d7fa8c87ed` / `specfix-g1-20261031` | COMPILE_ERROR, 12/12 NOT_RUN | $0.1215 |
| G2 | `d2152e6e-9d33-486d-a275-11216095d40a` / `specfix-g2-inventory-ordinary-20261031` | COMPLETE: 197 names = frozen P1 exactly | $0.5805 |
| G3 | `12180ab6-5d11-4962-96e6-ca0abbc7da49` / `specfix-g3-inventory-controls-20261031` | TOOL_ERROR: same compile error, list exit 1 | $0.1485 |

Total 3 builds $0.8505 (≤ $4), reserved 0; project used $69.6030 / $88.96. `check-tooling`
against `30f77e8599` ok for all three. Build/source/pin/request SHAs match the summaries.

G1/G3 error (kani.log:677, the same in G3): `error: Failed to find contract closure
__kani_recursion_check_bidirectional_merge in function ...smallsort::bidirectional_merge`.
Source attribution: the only `kani::stub` of a contracted function, row 10
(`kani::stub(bidirectional_merge, merge_adapter)` + `stub_verified(merge_profile)`). The pin
does not let an adapter stub a raw target that keeps a contract. The error comes from
kani-compiler after rustc analysis; whether the rest of specfix passes Kani codegen is UNKNOWN.
No retry: no fourth build, and G2/G3 already used the fixed tree.
Fix: `3282e976b0` removes that harness and its helper (own edit, cfg-on items only;
`merge_adapter` kept unused, documented). Cfg-off text is unchanged, so G2's exact-197 holds
for the final tree **by projection argument only**; cfg-on compile of the final tree is NOT_RUN.

## F03–F05/F09 per claim

| Claim | Ordinary tree | StageA profile (opt-in) | Evidence |
|---|---|---|---|
| F03 ordered ensures for any F (sort4/insert/merge) | unchanged, still false for unlawful F | fixed T, canonical fn-pointer guard, pure model order; no F call in 20 spec clauses | static only; G1 NOT_RUN |
| F03 swap extra F calls / Cell frame | unchanged (OPEN) | decision from pre-models, transfer per branch, model pair order | static only |
| F03 stub consumers | unchanged | adapter via `kani::stub` rejected by pin | G1/G3 compile error = measured blocker |
| F04 init/readable vs writable | unchanged | declared premise: `can_dereference` source/region, `can_write` dst, bounds before `offset_from`, `2<=N<=32` first | static; stock is_initialized=true → not a detector |
| F05 probe OOB T>128 | **guard in `matches_value_probe`** (assert + return before read) | typed full-value model counts, scalar `old` count | G2 compiles ordinary; guard check NOT_RUN |
| F05 padding | byte oracle unsupported, OPEN | typed models avoid bytes | NOT_RUN |
| F09 uninit/invalid detection | unchanged OPEN | unchanged OPEN | — |

Separation: helper guard = F05 assert in `matches_value_probe`; logical model = `Profile::model`
(u8/u64/[u8;16] identity, Cell `get()`, DropValue payload); declared init premise =
`can_dereference` in profile requires; actually detected UB: none in this session. B1≠B2:
no proof credit from either inventory.

## Changed target/property matrix and G1 rows

Ordinary: only `verify/merge.rs` probe guard (+ registration lines); smallsort.rs byte-identical;
every probe-using proof gains one constant check, so old PASS transfers only as a
source-equivalence argument (fresh acceptance NOT_RUN). Opt-in: 4 profiles, 8 profile PFCs,
1 positive regression, 2 negative controls remain (manifest `removed_after_g1`).
G1 rows 1–12 (`specfix/manifest.json`): all NOT_RUN — no asserts, covers, failure locations,
VT or RSS (G1 compile peak 1.85 GiB kani-compiler, wall 1:04). Planned expectations:
1–9 SUCCESS; 11 FAILED at merge/specfix.rs:611 in the built tree (588 in the final tree); 12 FAILED at
merge.rs:46; row 10 removed.

## Native inventories

- Ordinary (G2): exact frozen P1 set, 197/197, no missing/extra; names SHA-256
  `5e86596c…df8b`; tree `4865c40287`. P2 343 not re-derived natively (source-only).
- Cfg-on (G3): FAILED (compile); exact controls set UNKNOWN for both trees.

## NOT_RUN / OPEN and next step

All profile PFCs, guard/full-value controls, positive regression, cfg-on compile of
`31997f7781`, P2 343 native set, padding, uninit/invalid detection, locality transfer.
StageB (`specfix/STAGEB-PLAN.md`): profile key (T, comparator); atomic removal of F-calling
generic clauses; adapters only if the raw target becomes contract-free (needs a targeted
control) or real-body consumers; rerun G1 rows. Full CI after spec changes is the
coordinator's; past macOS ADMIT / GEOM16 527 s do not transfer. No general FnMut, padding or
unwind theorem is claimed.

Artifacts: `specfix/TRANSFER.tsv` (342 + 16 omissions), `make_transfer.py`, `manifest.json`,
`check_specfix.py`, `static-check-prebuild.json` / `static-check-final.json` (ok),
`REVIEW.md`, `STAGEB-PLAN.md`, `g{1,2,3}.request.json|summary.md|tooling.txt|cost.txt|
dispatch.txt|wait.txt`, `g1.extracted.txt`, `g2.inventory.txt`, budget files. No full/raw logs.

## A2 — feasibility build of the final StageA tree (no raw adapter)

Task `TASK-SPECFIX-A2.md`; request commit `f3086d0c4b` (library tree `31997f7781`, unchanged),
`specfix-a2-20261031`, build `623e141b-4bf1-4929-ac16-0a077af7a798`, k1-standard4, FAILURE (gate
False: row 9). Own cost $0.3105 (reserved $1.89, released); project $69.9135 / $88.96.
check-tooling vs `30f77e8599` ok; head/pin/request sha match. cfg-on compile of the final tree
**confirmed**: kani-compiler 1.85 GiB, ends ~62 s; all 11 harnesses ran. Run 15:40, 3.18 GiB.

| Row | Harness (merge::specfix unless noted) | Status | VT s | cbmc RSS | Covers | Failure |
|---|---|---|---|---|---|---|
| 1 | swap_profile_four_positions_u8 | SUCCESS | 15.4 | 0.30 GiB | 5/5 | — |
| 2 | swap_profile_cell_i32_n2 | SUCCESS | 19.0 | UNKNOWN¹ | 5/5 | — |
| 3 | network::swap_profile_drop_u8_n2 | SUCCESS | 18.7 | UNKNOWN¹ | 5/5 | — |
| 4 | sort4_profile_u64_n4 | SUCCESS | 65.7 | 0.90 GiB | 1/1 | — |
| 5 | sort4_profile_bytes16_n4 | SUCCESS | 78.1 | 0.99 GiB | 1/1 | — |
| 6 | insert_tail_profile_u8_prefix | SUCCESS | 159.8 | 1.68 GiB | 4/4 | — |
| 7 | insert_tail_profile_u64_start1_tail2_to8 | SUCCESS | 287.1 | 3.18 GiB | 8/8 | — |
| 8 | merge_profile_u8_n8 | SUCCESS | 158.2 | 1.43 GiB | 1/1 | — |
| 9 | specfix_positive_regression | **FAILED** (exp. SUCCESS) | 17.1 | 0.26 GiB | 9/10, 1 unreach. | specfix.rs:535 |
| 11 | specfix_full_value_checker_rejects_payload_change_u8 | FAILED = exp. | 3.1 | 0.09 GiB | 1/1 | specfix.rs:588 only |
| 12 | specfix_probe_guard_rejects_t129 | FAILED = exp. | 0.1 | UNKNOWN¹ | 1/2, 1 unreach. | merge.rs:46 only |

¹ not among the 8 sampled cbmc processes (2 s sampling). Checks: 0 failed in rows 1–8; exactly
1 failed in 9, 11, 12. Row 11: key-order assert :586 holds, only the full-value check fails.
Row 12: guard fails, no pointer/OOB check fails; the unreachable cover is the only one after
the guard (`returns no match`; the one before it is satisfied) — domain rejection, not OOB.
Row 9: only `specfix typed swap keeps full 129-byte values` (case 5, real `swap_if_less` on
`[u8;129]` with `a[0] < b[0]`, no probe) fails; the other 6 cases have no failed check. Cause
UNKNOWN (terse output, no trace, no rerun); no probe is involved; which cover is unreachable is
not printed. Neither a library defect nor a Kani bug is claimed (SPECDIAG19 checked zero values via
byte `same`). Next: case 5 as its own harness with a trace / smaller N (library edit → review).

Meaning for the P1-clean gate: first proof evidence on the pin that the 8 profile PFCs (fn-pointer
canonical guard, callback-free specs, real raw helper bodies) hold with all covers, and that
controls 11/12 detect exactly their target. The final tree compiles cfg-on, so the G1/G3 blocker
was row 10 alone. Not reached: positive regression red (case 5); the ordinary set was not
rebuilt (G2 exact 197 holds for `31997f7781` by projection only); no consumer is migrated, so
F03 stays OPEN and no P1/P2 proof credit transfers. P1-clean needs row 9 green or case 5
diagnosed, then StageB migration and the coordinator's full CI.
Artifacts: `specfix/a2.*`, `A2-PREBUILD.md`, `static-check-a2.json`, `budget-{before,after}-a2.txt`.
