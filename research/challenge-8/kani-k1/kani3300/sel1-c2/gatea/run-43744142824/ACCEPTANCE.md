# SEL1-C2 Gate A — ACCEPTED (run 43744142824)

2026-11-15, coordinator. Fork run [43744142824](https://github.com/Tiramisu-Cake/kani/actions/runs/43744142824),
trigger `ce2227aa9b` (child of worker15 package `b69a040ded`, same tree), export = FREEZE `14bc57fdb9`.
ubuntu-24.04 (41 min), ubuntu-24.04-arm (40 min), macos-15 (76 min); aggregate `COMPLETE_EXIT_ZERO_REQUIRES_REVIEW`, problems [].

Every row: 33/33 ordered stages, script exit 0, source clean before/after, problems []. Counts identical on all three rows and equal to
C2 Gate A (43665002636) except `suite:expected` 773/0/13 vs 744/0/13 — exactly the +29 `select-unpredictable-*` controls. Ignores
unchanged (kani 23, expected 13, firecracker 2, kani-fixme 655, unit 1+2). No proof credit; next: six-row SmallSort replay on the freeze.
