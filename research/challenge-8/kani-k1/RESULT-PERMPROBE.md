# RESULT PERMPROBE — u64 N8 permutation: index-probe+kissat SUCCESS 574.0 s; index/quadratic default TIMEOUT

Reviewed PRE-BUILD e1e9a6082a (GO). Branch experiment/kani-k1-permprobe-20261103, owner k1-merge, base 4d0121052b.
Library 7151b012eb → tree 6af2d315 (posts.rs append `mod perm;`, new verify/network/posts/perm.rs; old roots unchanged).
Build 87487311-6dac-45c4-acdd-7393199ced19 @e1e9a6082a, request permprobe-g1-oracles-u64n8-20261103 (07ad4c6d…f32e).
Kani 9461e07af7ec / nightly-2026-10-12; check-tooling vs 30f77e859903 ok. gcb-e2-standard-4 → k1-standard4, 4 CPU /
15.6 GiB, swap off, controls on, jobs 1, uninit off, 10 min/row, unwind 25. T0 10:02:31Z, finish 10:41:36Z.
Domain = partposts_count_u64_n8: `[u64;8]=any` full width, offset 0, pre copy, inferred `strict_less::<u64>`, actual
`<u64 as UnstableSmallSortTypeImpl>::small_sort`; no stubs/PFC/summaries/payload assume/cuts; probe = pre[j] (j<8) or all i.

| Root (network::posts::) | Oracle | Status | VT s | failed/total | covers | row RSS (cbmc + solver) |
|---|---|---|---:|---|---|---|
| perm::perm_index_u64_n8 | index probe, default SAT | TIMEOUT 600 | UNKNOWN | UNKNOWN | UNKNOWN | cbmc 0.16 GiB |
| perm::perm_quadratic_u64_n8 | O(N²), default SAT | TIMEOUT 600 | UNKNOWN | UNKNOWN | UNKNOWN | cbmc 0.18 GiB |
| perm::perm_index_kissat_u64_n8 | index probe, kissat | **SUCCESS** | 573.99 | 0/342 | 2/2 | cbmc 0.09 + kissat 0.05 GiB |
| perm::perm_index_negative_u64_n8 | control | FAILED `permprobe negative: index count` | 1.85 | 1/335 | 2/2 | UNKNOWN |
| perm::perm_quadratic_negative_u64_n8 | control | FAILED `permprobe negative: quadratic count` | 3.23 | 1/330 | 2/2 | UNKNOWN |
| ref: partposts_count_u64_n8 (POSTS8 97be7f87) | ∀ u64 probe | TIMEOUT 600 | UNKNOWN | — | — | cbmc 0.15 GiB |

Metatheorem: ∀j<8 count_pre(pre[j]) = count_post(pre[j]) covers every distinct x ∈ S with Σ = 8 = len(post), so post is a
multiset permutation of pre (≡ ∀ u64 probe on this domain); O(N²) unrolls the same over all i.
Controls: each failed only at its designated literal (perm.rs:105, :130), initial and after-overwrite checks passed,
2/2 covers. Build peaks: max RSS 1755380 KiB (kani-compiler 1.67 GiB), driver 0.11 GiB, process-sum 2.01 GiB, wall
30:50.69; OOM none_seen. No compile error; no repair/retry used.
Gates: index+kissat SUCCESS 0 unintended / 2/2 covers → **permutation credit** for this domain. index default and
quadratic TIMEOUT → no credit. Controls gate met. Kissat vs default is one paired run (574.0 s vs > 600 s), not a ranking.
No speed-up vs old count root computed (its VT UNKNOWN).
Cost: $0.5130 own spent of cap $1.10, own reserved $0; project used $83.9130, reserved $0, cap $88.96.

Conclusion: for v7 only perm_index_kissat_u64_n8 is a usable oracle, and only as opt-in evidence: 574 s sits 26 s
under the 600 s cap and far above the 250–300 s screen, so it is not CI-fit (macOS/jobs3 margin untested). Composition:
POSTS8 partposts_sorted_u64_n8 (SUCCESS 67.8 s, same entry/F/input; posts.rs roots and runtime byte-unchanged in this
tree) + perm_index_kissat_u64_n8 together give sortedness + permutation for the u64 N8 domain (two builds, two trees
differing only by the perm child). PASS is an opt-in proof of this exact domain, not ordinary promotion or generic T/F/N.
Receipts: permprobe/PREBUILD.md, permprobe/g1.result.md, permprobe/g1.request.json.
