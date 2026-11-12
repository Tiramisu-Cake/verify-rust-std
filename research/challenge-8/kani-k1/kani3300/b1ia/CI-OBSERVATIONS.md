# B1I-A: historical Quick observations

Provenance: coordinator task `TASK-KANI3300-B1IA.md`, research session input `9615ca8e1a03e35057864a19ea79fa88cccdcdb9`, dated 2026-11-12. Historical B1I manifest/NOTES/REVIEW at `54b7b7fbc4` were read; the manifest matches the current historical file. Historical documents are unchanged.

- Run: Uninit Quick `43196180814`; mixed result, **not Quick PASS**.
- Source: `dc5f5a406749a73f1c3192e0b5338441e79508bb`; tree `085bea5cda2df66a5cb4f72410fe124aa816c90b`; production parent `cdb439b0a4c36e9e595019895ab803230f332941`.
- CI checkout: `b5f87a7e92105965b719b71bb2f4741c14f0816c`. Its parent/source relation and workflow-only diff are coordinator-reported, not independently inspected in this stage.
- Coordinator reports fmt/build/Clippy PASS; expected uninit **111 passed / 7 failed / 2 ignored**, kani Uninit **22/0**, ui **14/0**, mem-init-reinstrumentation **1/0**. Counts describe selectors, not closed proof obligations.

| Historical selector / harness | Coordinator-reported actual observation | Interpretation |
|---|---|---|
| `maybe-uninit-initialized` / exact harness UNKNOWN | previous legal raw_eq failure | Open D0/model blocker, not new B1I regression |
| `shim-plain`, `shim-seeded` / `check` | `calls through function pointers` | FnPtr boundary; no reached bodyless Shim guard established |
| `shim-shadow-argument-only-plain`, `shim-shadow-argument-only-seeded` / `bodyful_shim_shadow_argument_only_is_unsupported` | Unsupported layout `(std::mem::MaybeUninit<u16>,)` | Compound tuple barrier; no direct-shadow argument guard credit |
| `shim-shadow-return-only`, `shim-shadow-return-only-seeded` / `bodyful_shim_shadow_return_only_is_unsupported` | uninit-read `u16` in `transmute_neo<MaybeUninit<u16>,u16>`; closure call Item | Genuine UB after returning uninit and assume_init; no Shim return guard credit |

The manifest's `historical_observations` retains each old path, harness, source/golden SHA256, run and source identity separately from candidate entries. The six selector failures are fixture contract/golden mismatches. Other existing controls passed according to the coordinator. No production regression was identified in these reported outcomes; shim acceptance remains open.

Independently read evidence here consists of Git/source/golden/manifest data and static diffs/hashes. No curated execution report or targeted property/MIR evidence was supplied or independently read; no raw/full-log access was attempted. Thus exact property IDs, full original tuple diagnostic, actual MIR/body/ABI/tuple operands, instrumentation order/count, entry/read bindings, seed collection, plain empty-target state and relevance activation are **UNKNOWN**. The exact tuple Unsupported prefix in the candidate golden is source-derived from `uninit_visitor.rs`'s layout barrier format, not a verbatim historical output claim.

Request to coordinator: supply curated per-harness JSON properties, exact diagnostic text and MIR/call-kind/ABI snippets with source/site/tool/flags identities, operation order and plain/seeded activation evidence as specified in CI-REQUEST.md. Absence of these data grants no independent proof credit. Changed/renamed fixtures and new companions are NOT_RUN regardless of historical observations.
