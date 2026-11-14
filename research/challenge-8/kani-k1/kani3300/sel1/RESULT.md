# SEL1 result — preparation complete

READY `46e46583ff112cae9c43aea1ba5dd6145e5e8387`

Source clone `/root/kani-fix-3300-sel1`, branch `fix/kani-3300-sel1`, tree `0a46fad6c1adc3022d39e25a45096ed9cd622844`, exact base69b13711e60a87458200833445d47488ab466344. Three neutral local commits by Tiramisu-Cake <igkharin@gmail.com> through git -c: compiler fallback/protocol+points-to52f2ef41f9f3c81c42e1207981b0e28a9171bdf2; controls27eba17c1d2503233dfe525da9fdb2df31685226; isolated per-harness oracles46e46583ff112cae9c43aea1ba5dd6145e5e8387.

Only validated standard select_unpredictable with usable fallback gets ordinary argument/return pairing. Both actual Move sources are snapshotted before clearing; Copy remains live. Fallback owns selected byte state; typed masks and false padding persist. Points-to follows the same body and joins both value-arm referents; no condition alias/pointee blessing/backend transfer.

Prepared29 native selectors (12 expected SUCCESS,17 intended negative), plus6 exact std ON rows. Expectations are proposals: every new verdict/check/cover remains NOT_RUN. Independent static review has no remaining findings; static source/identity/diff checks pass. Compiler/typecheck/fmt/build/clippy/Kani/CBMC/Miri/CI remain NOT_RUN. No push, CI dispatch, PR or Cloud spend.

Separate std test overlay `/root/verify-rust-std-kani3300-sel1-swap`, branch prep/kani3300-sel1-swap: `6075e7ce17179f45642c9ffe8fe09e3ec9395726` over B′ package01d75b8e839c751e7ab679fdaaa5fba6384983b6. It contains the swap closure commitda47945f47c6d61e6e207a749299a74f840a01f0 and frozen raw sort4 control commit6075e7ce17179f45642c9ffe8fe09e3ec9395726. Production std unchanged. STD-OVERLAY.json and full/delta patches bind all trees/files. CI-REQUEST and TARGET-GATE-MAP describe controls, two target gates and two merge regressions; exact binary hashes/caps remain pending coordinator build/assignment.

Research in this directory is intentionally uncommitted for the owner. g0 task pin remains38ed07ba0a94bd5a845cfec3bf95b44f0b9c46fa; concurrent C2-S2 research commit1e48f6dfe481296b5eccc5ea68efd4d12bc5cc2d was observed and preserved. No C2-S2 source fixes imported.

Handoff: coordinator publishes/rebinds reviewed CI-only recipe, runs fmt/build/clippy and targeted+existing suites, then named ON rows. Existing B′ receipts are bounded C1 source reports only. S1 composition drift stays S5 debt. After final C2: reviewed port, new freeze, Gate A on3 accepted platforms and agreed SmallSort replay. SEL1 is not Part1/SmallSort release acceptance; no new proof credit is claimed. No other stage was started.
