# RESULT UNSTABLEZST — unstable unit-ZST dispatch with `zst_aware_less`: family root TIMEOUT, all 5 per-length roots SUCCESS ≤ 271 s
GO 7c8bdefd81 (coordinator). Build 5228c09f-b2de-48b0-b5c9-1f7e957e6685 @7c8bdefd81, k1-standard4, kind measurement,
request unstablezst-meas-zst-unstable-dispatch-aware-20261103 (sha256 0507b713…08dc), controls on, jobs 1, uninit off,
10 min/row; Kani 9461e07a; check-tooling vs e8e238db9d rc 0 (pool, lane files, 6 bound files). Build FAILURE = Kani exit 1
from the one TIMEOUT row; compile ok, all 6 rows reported, OOM none_seen. Warnings: only `--force-warn unstable-features`
on `core/src/lib.rs` `#![feature]` lines and the pre-existing manifest/future-incompat notes; none at smallsort sources.
| # | Root (`verify::network::zstprobe::`) | Status | VT s | failed/total | unreach. | covers | CBMC RSS GiB |
|---|---|---|---:|---|---:|---|---:|
| 1 | zst_unstable_dispatch_aware_n8_9_12_13_17 | TIMEOUT | >600 | — | — | — | 8.69 (sample @669 s) |
| 2 | zst_unstable_dispatch_aware_n8 | SUCCESS | 195.4 | 0/358 | 18 | 2/2 | 3.69 |
| 3 | zst_unstable_dispatch_aware_n9 | SUCCESS | 251.7 | 0/358 | 18 | 2/2 | 3.76 |
| 4 | zst_unstable_dispatch_aware_n12 | SUCCESS | 230.1 | 0/358 | 18 | 2/2 | 3.76 |
| 5 | zst_unstable_dispatch_aware_n13 | SUCCESS | 242.2 | 0/358 | 18 | 2/2 | 3.83 |
| 6 | zst_unstable_dispatch_aware_n17 | SUCCESS | 270.9 | 0/358 | 18 | 2/2 | 3.84 |
Row 1 bounded facts (log-grep/log-lines): "CBMC timed out" at the 10 min harness timeout, then "Verification failed"; no
check results or covers emitted. Whole-run max RSS 9.13 GiB (time -v) is that CBMC process; below 13 GiB / 16 GB.
## Conclusion
- The unstable unit-ZST dispatch domain of `dispatch_safety_unstable_zst_n8_9_12_13_17` (lengths 8, 9, 12, 13, 17, route
  `small_sort_network`, no merge) is **closed by the five per-length roots**: each SUCCESS, 0 failures, both covers,
  same body as the original with `zst_aware_less` as the only comparator change (PREBUILD root1.diff).
- The family root with the same fix still TIMEOUTs (> 600 s, CBMC ≥ 8.69 GiB): the five lengths together exceed
  the budget, with or without the volatile read. The old volatile root stays TIMEOUT; counted apart.
- No counterexample: no row FAILED.
## v7 candidate (≤ 300 s)
Root 1: not a candidate (TIMEOUT). **Candidate: the full set of 5 per-length roots** `zst_unstable_dispatch_aware_n8`,
`_n9`, `_n12`, `_n13`, `_n17` — max VT 270.9 s, sum 1190.3 s (GCB jobs1; macOS not measured). Final admission after
fork-CI v7.
Cost: build $0.5400 (own spent $0.5400 of cap $1.30, reserved $0); project after: used $89.0700, reserved by others
$1.7550, cap $93.96. Receipts: unstablezst/{PREBUILD.md, summary.md, tooling.txt, cost.txt, budget-final.txt,
log-grep-timeout.txt, log-grep-warnings.txt, log-grep-smallsort-warnings.txt}.
