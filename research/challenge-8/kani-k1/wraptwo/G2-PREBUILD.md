# WRAP-N2 G2 PRE-BUILD REVIEW — explicit coordinator GO pending

G1 accepted package: `9f3da88a0b7973df3d7a7ec9d4701c6be11982cc`.
Build `7d5d04ec-f1da-493d-8be2-7ce36de3624b`: COMPILE_ERROR, all5 rows NOT_RUN.
Bounded compiler diagnostic: wrap.rs:84/103/118 E0502 at `old(count(v, probe))`,
conflicting immutable/mutable captures generated around the &mut slice/body.
No proof, contract rejection, solver failure, native cover, VT or CBMC RSS was obtained.
Compile wall44.88s; max RSS1326476KiB; sampled kani-compiler peak1324600KiB.
Exact build/head/pin/request identities match; check-tooling vs30f77e8599 PASS.
Own actual$0.108, reserve0; evidence retained in g1.* files (bounded K-1 interface only).

## Candidate delta

Source commit `811c78777dc6d324444111bb1104d2166aef727c`; library tree `47a9f618077d539860f6c7f2ce92d5a059e45c57` (not compiled).
Only verify/wrap.rs changes from G1; runtime/signatures, registration, other verify modules,
tools/flags/pin/workflows remain unchanged. Original PREBUILD.md and G1 evidence are historical.

Each concrete wrapper now takes an unsafe raw element pointer to a fixed span of exactly2.
Requires check can_dereference(raw slice2) and can_write(raw slice2) before model reads.
Stable additionally requires scratch disjoint from the raw input span: empty scratch, separate
allocation or nonoverlapping same-allocation ranges; distance is evaluated only for two live
nonempty regions after same_allocation. Same element size/alignment for Cell and MaybeUninit.
This expresses the exclusivity previously supplied by the two safe &mut slice arguments.
No new raw domain is credited beyond the unchanged concrete PFC backing[4]/active[1..3] and
separate scratch backing2 with exposed len0..2.

Modifies is exactly ptr::slice_from_raw_parts_mut(v,2). Postconditions use pair_sorted(v) and
`old(pair_count(v,probe)) == pair_count(v,probe)`. Both adapters form only an initialized pair
and call the same original pure sorted/count helpers as the corruption control; count is still
full-u8 and old still captures a scalar, never a pointer/reference. Probe remains independent,
by value and shared. No F call/statics/stubs/assumes or weakened value/frame clauses added.
After the canonical guard, the body forms &mut[T] len2 and calls the same real qualified trait
entry with the supplied fn pointer. Rejected comparator returns before constructing that slice.
Input arrays, sentinels, scratch initialization/tail, fn identity, covers and unwind16 unchanged.

This is a source fix proposal for the measured E0502; compilation on the pin remains NOT_RUN.
No compile-success claim is inferred from syntax checks or the analogous StageA raw profiles.

## Exact G2 and budget

RUN-REQUEST.json byte-equals g2-retry.request.json (already prepared in initial review).
Request `wraptwo-g2-retry-20261031`, SHA-256 `ab2eacf9e622b2e4f0dd9fe58b91911ed7efc6ff90fab5595f824ed62c40ca3e`.
Measurement, gcb-e2-standard-4/k1-standard4, controls true, jobs1, uninit off, timeout10min.
Same5 full names, expectations and expect_check strings as G1, without dropping any row:

| Prefix slice::sort::shared::smallsort::verify::wrap:: | Expect | Planned covers |
|---|---|---|
| stable_cell_n2 | SUCCESS | 9 |
| unstable_byte_n2 | SUCCESS | 7 |
| freeze_noncopy_n2 | SUCCESS | 7 |
| rejects_always_true | FAILED: wrap canonical comparator required | 3 |
| rejects_payload_corruption | FAILED: wrap full-value checker rejects payload corruption | 1 |

Current source literals: guard wrap.rs:61, corruption wrap.rs:266; only those checks
may fail for their controls. Old G1 clauses/locations are preserved in g1.compile-diagnostic.txt.
All three invalid function-pointer cases still call real wrappers in a plain proof. Corruption
is still outside any wrapper, after an unmutated plain real-body sorting/count check.

G2 is the second and final permitted build. Reserve(5×10+30)min×$0.0135=$1.08.
Own actual+reserve=$0.108+$1.08=$1.188≤$2; own live reserve currently0.
Project review-time ledger: used$70.0215/reserved0/cap$88.96; with G2≤$71.1015.
Fresh global/own budget checks still required after GO, before dispatch. No third build,
no inventory after G2; another compile/semantic failure means PARTIAL with exact blocker.
Ordinary inventory remains NOT_RUN: whole cfg-off library projection byte-identical to base;
controls:false cannot see wrap and cannot validate this fix.

Static gate32 checks PASS, exact request validation PASS, rustfmt --check and diff --check PASS.
Luna High bounded read-only delta review found no explicit raw-to-ref, scratch-disjointness,
N2-domain, oracle or frame error. It does not establish pinned compilation or proof acceptance.
G2 compile, all proofs, native covers/VT/RSS/failure locations remain NOT_RUN.
STOP at PRE-BUILD REVIEW pending a new GO; the earlier GO authorized G1 only.
After GO: fresh budget → dispatch branch → k1g.sh watch UUID → end turn, no polling.
