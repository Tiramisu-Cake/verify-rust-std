# RESULT PART2-POSTS8 — split of u64 N8 posts: sortedness 67.8 s SUCCESS, full-value count TIMEOUT (GCB, jobs1)

Reviewed: PRE-BUILD 1de9841dc4 (G1 GO) and 465494ccbb (G2 GO). Branch experiment/kani-k1-partposts-20261102, owner k1-network.
Base PART2-FAST 2104e7a596 (tree d4ec476a); task 9f4712c29c. Library commit 6fe5864e8d → library tree d646cb40 (both Builds):
network.rs append-only `#[cfg(kani_smallsort_controls)] mod posts;` (first 54177 bytes identical), new verify/network/posts.rs.
Kani 9461e07af7ec / nightly-2026-10-12; check-tooling vs 30f77e859903: pool, lane files, 6 bound files ok in both Builds.
Profile: gcb-e2-standard-4 → k1-standard4 4 CPU/15.6 GiB, swap off, controls on, jobs 1, uninit off, 10 min/row, unwind 25.
G1 partposts-g1-baseline-u64n8-20261102 (8f30cf6b…06d5) → ac1574d8-50ce-4b16-bd31-25d778a46253 @1de9841dc4;
G2 partposts-g2-split-u64n8-20261102 (0326ea44…a170) → 97be7f87-ce8e-4ee2-8099-ee248a9bb66f @465494ccbb. T0 20:20:30Z, last finish 21:04:13Z.

Domain (all 5 rows): T=u64, exact `[u64;8]=kani::any()`, offset 0, `pre` copy, independent `probe:u64=any`, F = existing
function item `strict_less::<u64>` (inferred, `<`), actual `<u64 as UnstableSmallSortTypeImpl>::small_sort` → network →
presorted 1 → insertion offset 1 (insert_tail tails 1..7) → no_merge. No stubs/PFC/assume; proof + unwind 25 only.

| Pkt | Root (verify::network::) | Property | Status | VT s | failed/total | unreach. | covers | CBMC row RSS |
|---|---|---|---|---:|---|---:|---|---:|
| G1 | network_correctness_u64_n8 (old, unchanged) | sorted + count | TIMEOUT 600 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | 0.16 GiB |
| G2 | posts::partposts_sorted_u64_n8 | sortedness | SUCCESS | 67.8 | 0/323 | 18 | 3/3 | 0.15 GiB |
| G2 | posts::partposts_count_u64_n8 | full-value count ∀probe | TIMEOUT 600 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | 0.15 GiB |
| G2 | posts::partposts_order_negative_u64_n8 | control | FAILED `partposts negative: sortedness` | 2.1 | 1/334 | 18 | 2/2 | UNKNOWN |
| G2 | posts::partposts_count_negative_u64_n8 | control | FAILED `partposts negative: full-value count preserved` | 1.9 | 1/328 | 18 | 2/2 | UNKNOWN |

Controls: witnesses P=1<<40, Q=1<<41; each failed only at its designated literal (posts.rs:65, :88), initial and
after-corruption checks passed, both root covers satisfied. Control row RSS not attributable (PIDs 9234/9263, ≤0.07 GiB).
Packet peaks (per Build, not per row): G1 time -v max 1636904 KiB (kani-compiler 1.56 GiB), driver 0.01 GiB, process-sum
1.77 GiB, wall 11:10; G2 1754428 KiB (kani-compiler 1.67 GiB), driver 0.12 GiB, process-sum 2.04 GiB, wall 12:22. OOM none.
No compile error in either Build; no repeat used (TIMEOUTs are resource outcomes, repeat not allowed).

Gates: old baseline gate NOT MET (TIMEOUT; no counterexample/UB, timing UNKNOWN). **Split proof gate NOT MET**: sorted
SUCCESS 3/3, controls designated-only 2/2 each, but count positive TIMEOUT at 600 s, so the combined domain is not closed.
Comparison: max VT(sorted,count) > 600 s cap (UNKNOWN), sum UNKNOWN; baseline VT UNKNOWN — no speed-up computed from 600.
Finding: on this profile the full-value probe count over the actual entry is the cost driver; sortedness alone fits
(67.8 s, ≪ 250–300 s screen). Splitting the posts does not make the count part fit ≤600 s, so it is not (yet) a useful CI
optimization for this root. No discrepancy (no SUCCESS vs counterexample). Scope equivalence held (same input/F/entry/profile).
Cost: G1 $0.2430 + G2 $0.2565 = own spent $0.4995 of cap $2.50, own reserved $0; project used $82.7925, reserved $0, cap $88.96.

Meaning: sorted PASS is an opt-in bounded proof of sortedness only for this exact u64 N8 domain, not a generic F/N theorem,
not ordinary promotion, and alone does not replace the combined root. No credit for other backings/offsets, stability,
uninit/full alias-validity or Rust unwind; unwinding assertions at 25 are not unwind-cleanup/ownership proofs.
macOS/jobs3/600 s with 400–450 s margin stays OPEN. Receipts: partposts/PREBUILD.md, partposts/g1.result.md, g2.result.md.
