# SmallSort harness manifest (Challenge 8)

`smallsort-harnesses.tsv` lists every harness in `core::slice::sort::shared::smallsort::verify` (names relative to that
module): 144 ordinary in Part 1, 328 in Part 2, 423 with `--cfg kani_smallsort_controls`.

| Column | Meaning |
| --- | --- |
| `part1`, `part2` | `ordinary` or `opt-in` (behind `kani_smallsort_controls`) in each PR |
| `expected` | `pass`, `fail` (negative control) or `deferred` |
| `p6_ubuntu`, `p6_macos`, `*_vt_s` | `check-kani-on-std` partitions of [run 40748125754](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/40748125754) at `6cfc76cb`: status and Kani verification time in seconds |
| `p7_ubuntu`, `p7_macos` | `check-kani-on-std` partitions of [run 40928266862](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/40928266862) at `770d222a` (Part 1 tree) |
| `p7_auto_*_vt_s` | `kani_autoharness` job of the same run: verification time in seconds (all SUCCESSFUL) |

An empty cell means the harness was not in that run's ordinary suite. Values were extracted from the job logs by
matching each thread's `Checking harness`, `VERIFICATION:-` and `Verification Time:` lines. Between `6cfc76cb` and
`770d222a`, the code of the harnesses in the `p6` columns changed only in `cfg` attributes and import grouping.
