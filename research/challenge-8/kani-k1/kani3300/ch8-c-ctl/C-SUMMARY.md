# C controls — final C-01 + C-02 summary

C budget exhausted. This is the complete eight-control summary, not a new dispatch request.
C-01: [run43788110742](run-43788110742/RESULT.md), std `d073585946`, control `64ec781bc1`,
sibling `d224c83361`. C-02: [run43790257718](run-43790257718/RESULT.md), std `597e54c5cb`,
control `59b5c663e3`, sibling `b97c4d6cf6`. Both use experimental P′ `c5ff36ff43` and
stock Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`; these observations do not add
credit to submitted production std `872d5a4338` / tool `cd355b0bcc`.

Root prefix: `slice::sort::shared::smallsort::verify::c_controls::`.
Counts below are properties/failures, not successful-check counts. SAT counts include
generated copies; source-label correlation is separately qualified.

| Control | Frozen expectation | C-01 Kani; SAT covers | C-02 Kani; SAT covers | Established observation / open qualification |
|---|---|---|---|---|
| `c_merge_source_write_restore` (N1) | assigns/frame FAIL at retained callback writes | FAILURE280/2;3/4 | FAILURE279/1;4/4 | Frame diagnostic caught in both; C-02 isolates exactly `Check that *dst is assignable` without unwind failure. Callback-source causality/strict oracle UNKNOWN |
| `c_merge_source_read_only` (L1) | SUCCESS | FAILURE280/1;2/4 | SUCCESS279/0;3/4 | Legal companion succeeds after bound17; only constant-false write-branch cover non-SAT. Independent acceptance UNKNOWN |
| `c_callback_live_shared_in_outer_frame` (N2) | stock SUCCESS / ALIAS_GAP | SUCCESS292/0;4/7 | Not selected; retain C-01 | Documented stock alias gap observation for deliberately invalid transient write inside outer frame; no Rust permission or independent alias-enforcement credit |
| `c_callback_read_only_in_outer_frame` (L2) | SUCCESS | SUCCESS292/0;3/7 | Not selected; retain C-01 | Expected read-only companion observation; PFC/cover/clone/property qualification PENDING |
| `c_external_mut_state` (L3) | SUCCESS, explicit external counter frame | SUCCESS274/0;2/3 | Not selected; retain C-01 | Expected legal disjoint captured-mut state observation; full qualification PENDING |
| `c_external_cell_state` (L3) | SUCCESS, explicit Cell pointee frame | SUCCESS245/0;2/3 | Not selected; retain C-01 | Expected legal external Cell observation; full qualification PENDING |
| `c_insert_tail_local_lifetime` (L4) | SUCCESS, actual helper/local lifetime/copy-back | SUCCESS193/0;3/3 | Not selected; retain C-01 | Expected concrete lifetime/copy-back observation; no general lifetime/unwind theorem; full qualification PENDING |
| `c_local_storage_reuse` (L4) | SUCCESS after old borrow ends | SUCCESS30/0;2/2 | Not selected; retain C-01 | Expected ended-borrow/reinitialization observation; no general storage-reuse enforcement; full qualification PENDING |

**What the runs establish as observations.** C-02 removed the exported memcmp unwind
failure for both fixed merge fixtures. N1 now has exactly one assigns failure while
the matching read-only companion has no failed checks. Five other legal companion
roots returned SUCCESS in C-01. These are bounded, source-reported Kani results;
none is promoted to independent formal proof credit by this intake.

**What remains a gap.** Stock N2 returned SUCCESS for source code that writes and restores
through a raw alias while the callback shared reference is live. Its matching companion
also returned SUCCESS. Frames alone do not enforce temporal shared-reference permissions.
C-01 cover statuses are consistent with the generated active callback path, but complete
body/write/label→property binding remains PENDING. No C PASS or complete borrow inventory follows.

**Coverage.** C-01 group-01 had18/30 SAT:3 UNDETERMINED and9 UNREACHABLE, analyzed in its
RESULT/ANALYSIS; group-02 had3/3 SAT. C-02 has7/8 SAT and no UNDETERMINED.
The sole non-SAT ID is `merge_fixture::<false>::{closure#0}.cover.2` (full ID in C-02 RESULT).
Static source comparison identifies the constant-false `C_N1_transient_write` branch,
which L1's three-label oracle does not require. Exact exported label binding remains PENDING.
Policy clause4 still requires all emitted covers SATISFIED; no exception is adopted here.

**What remains PENDING/UNKNOWN.** Both original C-02 receipts remain UNKNOWN /
`INCOMPLETE_CHECK_INVENTORY`. Each row has8 unreachable checks (including4 target-named
merge assertions) and4 successful unsupported properties; their roles/binding need the
policy's explicit review, not automatic rejection or exemption. The N1 failure is located
at `ptr/mod.rs:2282`, not the frozen callback-write sites23/25. Source-spelling/line/unwind
binding is checked for C-02 only; generated contract-wrapper/contracted-symbol causality,
both retained writes, named successful assertions and cover-ID correlations remain open.
Six original C-01 PFC receipts retain `CONTRACT_TARGET_BINDING_MISMATCH`; two ordinary
receipts retain `INCOMPLETE_CHECK_INVENTORY`. Historical receipts are unchanged.
The C-02 resource cap also differs: request6GiB, actual group cap12GiB, sampled peak~1.85GiB,
per-root RSS UNKNOWN. See C-02 RESULT for exact fields and pinned runner cause.

**Final:** independent acceptance **UNKNOWN**; new independently established B1/B2 credit **NONE**.
No further C attempt is authorized or prepared. English limitations updated only in the
[unpublished draft](../ch8-c-now/LIMITATIONS-DRAFT.md); no push, CI, publication or ledger edits.
