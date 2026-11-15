# SEL1-C2 six-row SmallSort replay — ACCEPTED (run 43751703000); SEL1-C2 complete

2026-11-15, coordinator. Fork run [43751703000](https://github.com/Tiramisu-Cake/kani/actions/runs/43751703000), trigger `1ce0b1e5b6`
(child of package `fff42ed46`, same tree), Kani FREEZE `14bc57fdb9`, std `70ba5befc6` + SEL1 test-only package. ubuntu-24.04,
six serial jobs. Profile: uninit ON, object-bits 12, valid-value OFF, controls cfg ON, closure comparators.

| Row | Result | C2 B′ (43683557088) | Old SEL1 (43611601987) |
|---|---|---|---|
| merge-raw-closure-on | SUCCESS, 0 of 572 (16 unreachable), covers 5/5 | 0/572 | 0/572 |
| merge-profile-closure-on | SUCCESS, 0 of 1030 (68 unreachable), covers 2/2 | 0/1030 | 0/1030 |
| **sort4-closure-on** | **SUCCESS, 0 of 753 (14 unreachable), covers 3/3** incl. return | 1/760: select_unpredictable boundary | 0/753 |
| **swap-if-less-closure-on** | **SUCCESS, 0 of 585 (12 unreachable), covers 6/6** | — | 0/585 |
| raw-legal-on | SUCCESS, 0 of 382 (12 unreachable), covers 2/2 | — | 0/382 |
| raw-negative-on | exactly 1 of 382: `sort4_stable::<u64, …read_less_u64>.safety_check.1` "Reading from an uninitialized pointer of type `*const u64`" at smallsort.rs:751:26; covers 2/2 | — | same |

No return cover unreachable in any legal row. Job "failure" of raw-negative-on is the intended verifier exit 1.
Receipt `outcome` UNKNOWN reviewed here. Scope: bounded helper evidence for these geometries/targets with closure comparators;
not whole SmallSort, not fn-pointer `P::CMP`, not all T/N; #5104 not addressed.

SEL1-C2 chain: port `14bc57fdb9` → Quick 43740679160 → Gate A 43744142824 (3 platforms) → replay 43751703000. PR text — separate stage.
