# RESULT-TRAITPFC-G3 — Build 1 COMPILE_ERROR; G3 incomplete

Build `9d94cb84-55e1-4cae-a55b-9597ddd81d87`: Cloud FAILURE, K-1 COMPILE_ERROR; source `55a7fd1c8ada1590ab571b040a6256219ef75e63`; Kani exit1.
Library `aa0859448612246d0c52e1c59f844e777c8ad3b6`, tree `b6f050a21d2781fcc95a8f7e02bf9154affa560a`; patch SHA256 `4f877ee8ece2fcad1ed09938470874ba4f6676316d415df924ff95459f3baf6b`.
Tooling `9b1758ab817af005e96fd52a5fc940d4b6acf984` PASS unchanged; Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`. Brief HTTP404; [bounded evidence](traitpfc/g3/evidence/verification-report.json).
Model: `pub(crate) trait SortModel<T, F>`; `fn enabled(entry: SortEntry, cmp: &F, len: usize) -> bool;` `fn snapshot(base: *const T, len: usize) -> SortSnapshot;` `fn sort_postcondition(pre: SortSnapshot, base: *const T, len: usize) -> bool;`; Copy snapshot `{len, valid, vals:[u64;3]}`, `U64Cmp = fn(&u64, &u64) -> bool`.
T1 literal ensures below; T2/T3 differ only by `SortEntry::Unstable`/`SortEntry::Freeze`; all exact strings in [contracts.json](traitpfc/g3/contracts.json).
```rust
    #[cfg_attr(kani, crate::kani::ensures(|_|
        !old(<() as verify::trait_model::SortModel<T, F>>::enabled(
            verify::trait_model::SortEntry::Stable, is_less, v.len(),
        )) || <() as verify::trait_model::SortModel<T, F>>::sort_postcondition(
            old(<() as verify::trait_model::SortModel<T, F>>::snapshot(v.as_ptr(), v.len())),
            v.as_ptr(), v.len(),
        )
    ))]
```
Native old captures enabled and Copy snapshot; no fallback/new requires. No callback in post checker; one post-snapshot, pure <= and full live-prefix counts (N2 exact pair shortcut).

| Row | Status | Time s | Failed/total | Covers |
|---|---|---:|---:|---:|
| A1 | NOT_RUN | — | — | — |
| A2 | NOT_RUN | — | — | — |
| A3 | NOT_RUN | — | — | — |
| A4 | NOT_RUN | — | — | — |
| A5 | NOT_RUN | — | — | — |
| A6 | NOT_RUN | — | — | — |
| C1 | NOT_RUN | — | — | — |
| K1 | NOT_RUN | — | — | — |
| K2 | NOT_RUN | — | — | — |
| K3 | NOT_RUN | — | — | — |
| K4 | NOT_RUN | — | — | — |
| W1 | NOT_RUN | — | — | — |
| R1 | NOT_RUN | — | — | — |
| R2 | NOT_RUN | — | — | — |

Full compile failures: E0308 mismatched types at `trait_contracts.rs:245:73` (K4), `:261:73` (W1), expected `&fn(&u64, &u64) -> bool`, found `&fn(&u64, &u64) -> bool {trait_less_u64}`; [full diagnostics](traitpfc/g3/evidence/compile-context.txt). No failed proof checks; resolution error, not unsupported/TIMEOUT/ordinary FAILED.
Native cfg-off inventory: all242 names exact, four bounded pages; same source/library tree, names hash independently recomputed. Rows controls-on, jobs1/standard4/5m, no-assert-contracts/object-bits12, uninit/value-validity off; list argv not emitted, flags attributed via frozen list-before-export runner as in G2.
Code-ready: NO (controls compile error); bounded proof PASS: NOT_RUN; resource-open: none. Proposed domains only: u64/canonical U64Cmp, T1 N2/N3 array+scratch N+16; T2/T3 N2/N3 backing N+2 active1..N+1; C1 N3. No new proof credit.
Expense $0.6615/49 billed min; own remaining$2.8385/$3.50. Proposed sole Build2 max100m/$1.35 => spent+reserve$2.0115. Project used$110.9400/reserve$0.6750/cap$118.96; plus Build2 => $112.9650. T0 2026-11-10 19:51:57Z; main deadline 2026-11-11 01:51:57Z.
New ordinary ΣVT=0s (0/7 executed, not proof completion). Source manifest235→242 ordinary, cfg-on260→260; 235+13 inherited root closures and G1 contracts unchanged, rustfmt/apply-check PASS.
No generic T/F, other lengths/types, additional UB classes, unwind theorem, B2/full proof or actual PR-CI on a pin including kani#5135 established.
Coordinator approved the qualification repair; applied library `1aac64c50d69382c8ce90811880225d0a047525f`, tree `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`; [Build2 packet](traitpfc/g3/build2/PREBUILD-BUILD2.md) awaits exact PRE-BUILD review/GO. Build1 evidence above remains bound to its original tree; Build2 NOT_RUN.
