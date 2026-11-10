# PRE-BUILD — KANI5116 KF1

Candidate: the full pushed commit SHA in the PRE-BUILD REVIEW marker. No build before exact-packet coordinator GO.
Branch `experiment/kani-k1-kani5116-20261110`; owner `k1-merge`; slug `kani5116`; stage `kani5116-kf1`.
Request `kani5116-kf1-main-20261111-01`, kind `kani-tests`, standard4 pool. T0 starts at GO; main window 360 minutes + 30 closeout.

## Identities and source boundary

- Kani pin: `f046b70644e113be0df9c22c2e6ea44a65a57566`; toolchain nightly-2026-10-23.
- Original accepted KT1 tooling: `383fd7089550aeabac3ad92366cd7c71e2f237ee`.
- **KF1 tooling base: `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`**. The coordinator explicitly authorized this separate `[skip ci]` commit: only the branch-limit block in `k1g.sh` and its existing Python service test changed. Branch cap is cumulative $2.30 = KT1 $0.80 + KF1 $1.50; the 59-minute timeout limit remains. No other tooling, lane, dependency, pin or workflow changes.
- Local Kani branch: `fix/default-fn-contracts-5116`, commit `42dd86287d181210b95717d88605d774a3fcab35`, in `/root/kani-fix-5116`. Only official Kani origin is configured; no Kani push. `/root/kani-src-f046b70644` remains the read-only reference.
- Patch: `kani-fix.patch`, SHA-256 `91ce8329f9cc2e11c4ed77f4e789d10341d6914005710b04e970a3b5f53a571f`.
- Request SHA-256: `0d6ec56aafce4e4ffe1f47762bf99fd956e7012d3102087019b0baf7545401f7`.
- Applied tree: **`a5782891059cd86d4129056d992819ecf25b3945`**, equal to the local Kani commit tree. `preflight.json` records the pin, patch, request, tree and complete diffstat.
- Patch was produced from the committed Kani tree against the full pin, including all 9 new `.rs` and 5 new `.expected` files. Exactly 17 paths, all under `library/kani_macros/` or `tests/`.

## Production change

`ContractFunction` parses the full method with `ImplItemFn`, retaining its original `default` token alongside an `ItemFn` for existing helpers.
The handler and initializer keep this adapter. Initial expansion emits `default` between the original visibility and signature; subsequent expansions clone the adapter and serialize it as `ImplItemFn`.
No keyword is added to check/replace/assert/recursion/modifies closures. The original signature, where clause, qualifiers, attributes, spans and inline markers are retained. No resolver/compiler change or contract inheritance is introduced.
Production diff: **3 files, +52/-11 lines** (`contracts/mod.rs`, `bootstrap.rs`, `initialize.rs`). Tests: **14 files, +423/-0 lines**. Existing fixtures and golden files are unchanged.

## Exact typed manifest: 19 selectors

`manifest.json` is byte-for-byte JSON-equivalent to request `kani_tests`. Every entry has `expect: pass`; no `expect: fail`.
The four new kani fixtures use edition 2021, `-Zfunction-contracts`, `min_specialization`, a blanket `impl<T>` with `default fn`, and a specializing `u8` impl. All stub fixtures also use `-Zstubbing`.
For every positive below, `require_success: true`; positive expected-mode tests receive `--require-success`. Negative expected/ui tests have `require_success: false` and require the listed own-child-output diagnostic as well as native compiletest PASS.

| New selector (relative to tests/) | Coverage / required diagnostic |
|---|---|
| kani/FunctionContracts/specialization_default_fn_5116.rs | Original ensures+modifies #5116 repro; PFC for nonspecialized `u16`, sorted-pair assertion |
| kani/FunctionContracts/specialization_default_clauses.rs | Requires-only, ensures-only, modifies-only; requires/ensures/modifies and reversed order; five PFC harnesses and default stub caller |
| kani/FunctionContracts/specialization_default_generic.rs | Method-local `F: FnMut` with a where clause; default PFC and stub; specializing override with its own distinct postcondition and its own PFC/stub |
| kani/FunctionContracts/specialization_default_old.rs | Eager scalar `old(*value)` snapshot across mutation, PFC and stub caller |
| expected/function-contract/specialization_default_ensures_fail.rs | `Failed Checks: \|result\| *result == 0` (false postcondition) |
| expected/function-contract/specialization_default_requires_fail.rs | `Failed Checks: value != 0` (invalid caller through verified stub) |
| expected/function-contract/specialization_default_modifies_fail.rs | `is assignable`; golden ties assigns/FAILURE/assignable description on consecutive lines and requires failed-check/FAILED summary |
| expected/function-contract/specialization_default_old_fail.rs | `Failed Checks: \|_\| *value == old(*value)` (stale postcondition after increment) |
| expected/function-contract/specialization_override_no_contract.rs | `has no contract.`; golden also requires `error: Failed to check contract:` and advice to add a contract. PFC on the override must not inherit the default summary |

The four verification-failure golden files require a concrete assertion or assigns failure, its corresponding failed-check summary, and `VERIFICATION:- FAILED`. The modifies pointer temporary name is deliberately unconstrained; the property kind and failure status are constrained together.

| Existing selector (relative to tests/) | Group / expectation |
|---|---|
| kani/FunctionContracts/generic_trait_specialization.rs | Required #5135 regression, native PASS (includes its existing should-panic harness) |
| kani/FunctionContracts/generic_fn_pointer_argument.rs | KT1 neighbor, native PASS |
| kani/Stubbing/stub_set_multiple_use.rs | KT1 neighbor / stubbing, native PASS |
| ui/function-contracts/trait_default_fn_err.rs | KT1 neighbor, native PASS; diagnostic `cannot be applied to trait function declarations without default bodies` |
| expected/function-contract/generic_default_missing_required.rs | KT1 neighbor, native PASS; diagnostic ``unable to find implementation of associated function `Probe::probe` for NoDefault`` |
| expected/function-contract/arbitrary_ensures_pass.rs | Ordinary free function, native PASS + successful Kani exit |
| expected/function-contract/checking_in_impl.rs | Inherent method, native PASS + successful Kani exit |
| expected/function-contract/trait_impls/methods.rs | Trait and inherent receiver contracts, native PASS + successful Kani exit |
| expected/function-contract/modifies/simple_pass.rs | Modifies framing, native PASS + successful Kani exit |
| expected/function-contract/history/stub.rs | Old snapshots and stub_verified, native PASS + successful Kani exit; retains its existing 8-object-bit flags |

Declared NOT_RUN before dispatch: `kani/FunctionContracts/fixme_receiver_contracts.rs`, `fixme_static_interior_mut.rs`, `fixme_static_mut.rs`; `expected/function-contract/modifies/refcell_fixme.rs`, `unsafe_rc_fixme.rs` (no golden); `expected/function-contract/history/ui/noncopy_ignore.rs` (ignored). No ignored/fixme selector is in the PASS packet. The remaining upstream matrix is outside this bounded subset.

## Static validation and budget

- Full Python tooling suite: **109 PASS**, including existing runner/error paths. Updated dispatcher service test accepts $2.2950 and rejects $2.3085 for both 59-minute and 42-minute reservations, and accepts a 26-minute prior reservation plus the KF1 reservation. No credentials are read by the agent; service tests use empty fake keys and mocked gcloud.
- `bash -n k1g.sh`, request/schema validation, `git diff --check`: PASS. Fresh clean detached pin checkout: `git apply --check --index` and apply via unchanged `prepare_kani`: PASS. Applied index tree equals local committed tree.
- All 19 fixture paths and all 12 required expected/ui golden paths exist after apply (5 new + 7 existing). Headers and edition-2021 flags verified on all 9 new Rust fixtures. No existing golden changed.
- Pinned rustfmt wrapper with Kani configuration: `--check` zero diff on 3 macro files (edition 2024 per kani_macros/Cargo.toml) and 9 new Rust fixtures (edition 2021 per compile-flags). No local cargo/rustc/Kani/CBMC invocation.
- Build 1 request: **29 work minutes + unchanged 30 overhead = 59 paid minutes**. Standard4 price $0.0135/min; maximum reservation **$0.7965**. Verify cutoff is validation start + 53 minutes, leaving six minutes for summary/upload. Per-selector child timeout 180 seconds, outer timeout at most 210 seconds, one Rust test thread.
- KT1 observed Kani build 263–276 s and compiletest build 16–18 s; total build about 8–9 min. Nineteen small selectors replace five; the 29-minute work field leaves substantial room beyond the observed setup and test time. Inner per-selector limits and existing runner/gate semantics are unchanged.
- KF1 actual spend/reserved before dispatch: **$0 / $0**; $0.7965 fits the independent $1.50 cap. At most one repair, only if KF1 actual cost plus the new reservation fits $1.50; a second full-size reservation requires actual Build 1 cost <= $0.7035. A new exact-packet GO is required.
- Historical KT1 actual cost remains $0.3510. Branch used + proposed reservation is **$1.1475 <= $2.30**. This cumulative branch allowance does not replace the independent KF1 cap or project ledger. Dispatcher rechecks the live project/branch ledgers atomically at submit time.

Live project ledger snapshot (2026-11-10T21:32:34+00:00, via `k1g.sh budget`): 261 builds, $111.1695 used, $1.3500 reserved, $118.96 cap. Including the proposed $0.7965 gives $113.3160, within the project cap. Dispatch must recheck this changing ledger.

## After GO

Dispatch this exact pushed candidate with `k1g.sh dispatch experiment/kani-k1-kani5116-20261110`; start `k1g.sh watch BUILD`, then end the turn. Do not poll status.
On wakeup, use only bounded `k1g.sh summary/native` pages and follow returned continuation offsets; check all new/old native names, own diagnostics, request/patch/pin/applied-tree identities and absence of timeout/ignored outcomes.
Run `k1g.sh check-tooling BUILD c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`; compare the reported applied tree with `preflight.json`. Use `k1g.sh budget BUILD` for own cost.
An unexpected existing-test failure is a regression; inspect its bounded excerpt and preserve expectations/selectors. Repair stays within macros/fixtures and the authorized budget, with another PRE-BUILD review/GO.
Update RESULT (<=45 lines), then `REVIEW REQUEST <sha>` or `KANI5116 KF1 ЗАВЕРШЁН`, and stop. Full upstream CI, core safety attributes and core-default smoke remain outside KF1.
