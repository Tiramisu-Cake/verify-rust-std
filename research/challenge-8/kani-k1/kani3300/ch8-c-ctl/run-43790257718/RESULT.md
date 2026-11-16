# C-02 intake — run 43790257718

One intake stage, input g0 `5a8d67271044c5f2f13690d2cce732c076ac700a`.
C budget exhausted: no C-03, retry, new source/control candidate or dispatch.

## Identities and evidence

- GitHub artifact `14192182726`, `ch8-c-43790257718-1`, attempt1, 30852 bytes.
  ZIP SHA256 `f173d93202dbd8e7b71c2edf3484429fc628f2fff330230b529952c2d922f6dd`
  matches the independently fetched GitHub artifact digest and run/head metadata.
- Dispatch sibling `b97c4d6cf6eb2c84667209f211a1a703f0ebf5e9` and prepared control
  `59b5c663e3a2a0fb79bc565cdda20342e51ac7bd` share tree
  `e10c359aba4830016105bb7e8a8b95544e4c3664`; sibling's sole parent is stock tool
  `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Std `597e54c5cb503955f9483edc6acc9d4752d57713`, tree
  `b3bd6d8c939e08b13fc7a4c6c9da694cc8a2aa97`, on P′ `c5ff36ff433692140605891f646043f991db05de`.
  Relative to C-01 std `d073585946093071b696eada41b8c8cac18362a7`, only the two
  merge harness unwind attributes changed8→17; source assertions/writes/oracles are preserved.
- Request SHA256 `defc5fc6d75a62623fda86b1a37f430a08ed0b4eb90ac30f7b94da65ca7b532c`
  matches inventory and job-status. Pinned source hashes, source snapshots before/after,
  and before/after tool binary hashes agree. Kani0.68.0, CBMC6.11.0, rustc
  `1.101.0-nightly (7189d39d9 2026-10-22)` are reported, not locally executed.

Only selected structured JSON members were read from the supplied scratch ZIP; no raw logs.
Exact member hashes, export pointers and property inventories are in
[artifact-metadata.json](artifact-metadata.json) and [ANALYSIS.json](ANALYSIS.json).
Original receipts are copied byte-for-byte under `original-receipts/`; no classifier,
historical receipt or ledger was changed. The original parser reproduced both row exports exactly.

## Two rows

All roots have prefix `slice::sort::shared::smallsort::verify::c_controls::`.
`279/1` means total properties/failed properties, including4 covers;
each row has275 checks. Group-01 COMPLETE, compile43.307s, group95.815s, exit1;
no timeout/truncation. Group exit1 is expected for a negative and does not classify the companion.

| Root | Exported Kani result | Covers | Classification against frozen oracle |
|---|---|---|---|
| `c_merge_source_write_restore` | FAILURE279/1; exactly `ptr::write_volatile::<u64>.assigns.1` | 4/4 SATISFIED | N1 frame diagnostic caught cleanly, no exported unwind failure; strict negative oracle UNKNOWN: callback-write binding still PENDING |
| `c_merge_source_read_only` | SUCCESS279/0 | 3 SATISFIED,1 UNREACHABLE | Expected legal companion result; non-SAT branch is not required by its source oracle, but policy/coverage/property binding still prevent independent acceptance |

N1's sole failure: class `assigns`, description `Check that *dst is assignable`,
location `library/core/src/ptr/mod.rs:2282`, `trace_available=true`.
The named oracle still requires callback source writes at `verify/c_controls.rs:23/25`.
The JSON contains no trace body or independent causal binding from that implementation
location to both retained callback writes. The matcher was not broadened.
Thus the observation is an isolated frame failure, not an independently accepted N1 oracle.

The C-01 `memcmp.unwind.0` failure is absent in both C-02 rows; no check is UNDETERMINED.
This supports the bound17 fix for this two-u64 fixture, not a general merge/unwind theorem.
Both rows have8 UNREACHABLE checks and4 successful unsupported properties.
The old runner returns `INCOMPLETE_CHECK_INVENTORY` / UNKNOWN for both before later gates.
[Acceptance policy](../../../ACCEPTANCE-POLICY-BATCH.md) permits reasoned unreachable/unsupported
exceptions, not a blanket veto or blanket exemption. Successful unsupported statuses are
reported with exact IDs in ANALYSIS; they are not extra failures. The eight unreachable
checks include four target-named `bidirectional_merge...assertion.1..4`, two `usize::abs_diff`,
one alignment and one formatting assertion. Their exact roles/clone binding remain
unestablished; no required target assertion is silently treated as a helper exception.

## The single non-SAT cover

Exact exported ID:
`slice::sort::shared::smallsort::verify::c_controls::merge_fixture::<false>::{closure#0}.cover.2`,
status **UNREACHABLE**, not UNDETERMINED or UNSATISFIABLE.

The pinned closure's covers in source order are:

| Source label / line in `verify/c_controls.rs` | Source condition | Read-only export correspondence |
|---|---|---|
| `C_merge_callback`:21 | unconditional callback entry | closure `.cover.1`, SATISFIED |
| `C_N1_transient_write`:24 | inside `if WRITE` | closure `.cover.2`, UNREACHABLE |
| `C_merge_live_read_after_restore`:29 | unconditional after live read | closure `.cover.3`, SATISFIED |
| `C_merge_return`:38 | after actual call and final assertions | fixture `.cover.1`, SATISFIED |

This correspondence is a static source/order/monomorphization inference; JSON exports
IDs without cover labels or locations, so independent label→ID binding stays PENDING.
The read-only harness instantiates `merge_fixture::<false>()`; its frozen request and
[ORACLES](../ORACLES.md) require exactly callback entry, live read and return (count3).
They do **not** require `C_N1_transient_write`: requiring it would contradict this companion.
No required source label is shown to be missing by the3/4 count alone.

Policy clause4 nevertheless literally requires **all emitted covers SATISFIED**, as well as
the required covers. Its present text grants no cover-specific constant-false exemption.
We record the source-oracle distinction without adopting an exception, deleting the cover,
or changing receipts. Independent acceptance remains **UNKNOWN** under that policy;
the result is not relabelled a missing mandatory callback/return cover or a C PASS.

## Other limits and closeout

Source-spelling PFC binding now passes the static import/attribute/line/unwind and export
token checks for this pair; independent resolution of the mangled contracted symbol,
generated modifies wrapper, retained writes, successful assertion labels and cover IDs remains PENDING.
This does not retroactively repair the six C-01 PFC binding receipts.

Resource receipt reports cap12582912KiB (12GiB), versus request6291456KiB (6GiB).
Pinned runner `_group_rss_limit_kib()` uses `min(12GiB, MemAvailable-2GiB)` independently
of that request field. The sampled group peak1942804KiB (~1.85GiB) is below6GiB;
per-root RSS is UNKNOWN. This is a cap-conformance discrepancy, not proof of a6GiB enforced limit.
No runner change or rerun is part of this intake.

Final status: observations reconciled; independent acceptance **UNKNOWN**, B1/B2 proof credit **NONE**.
The complete eight-control table is [C-SUMMARY.md](../C-SUMMARY.md).
English [LIMITATIONS-DRAFT](../../ch8-c-now/LIMITATIONS-DRAFT.md) updated without publication.
Push/CI/publication/ledger/local cargo/rustc/Kani/CBMC:0.
