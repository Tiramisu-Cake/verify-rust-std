# PR5195 exact cleanup and coverage matrix

All paths/symbols below are at head9b67828707f8d7d5e691484896a82475dcf34d28. P = `tests/script-based-pre/delayed-shared-body/`. Outcomes are source intentions; no native probe ran during review. There is no harness quota. Retain the two Rust harnesses and both call-path configurations; reduce redundant invocations and the separate duplicate control.

## Every changed file

| Current file | Disposition / exact edit |
| --- | --- |
| `kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs` | KEEP byte-exact. ExtraChecks predicate, unit warmup, conditional per-harness clone and selected transformer argument are the fix. Keep its comments. |
| `kani-compiler/src/kani_middle/transform/mod.rs` | KEEP byte-exact. Clone derive for BodyTransformation uses existing clone-capable pass/body/map fields. |
| P `Cargo.toml` | KEEP package, edition and isolated [workspace]. RENAME the sole feature delayed-first -> delayed-indirect. |
| P `src/lib.rs` | KEEP Padded, both read helpers, both harnesses and all assertions/initialization operations. RENAME all four cfg strings delayed-first -> delayed-indirect only. Preserve line structure so read_value's read remains line12. |
| P `control.rs` | REMOVE entire file, its separate Padded and uninitialized_control harness. It has no shared-cache interaction; the retained bad singleton/paired checks enforce the negative at the actual shared leaf. Existing raw-padding/initialized-byte baselines are cited below. |
| P `check.py` | EDIT main/compare schedules to eight cases below; remove uninitialized_control lookup/probes and standalone-kani edition override; rename feature/key strings. KEEP parse/inventory/normalization/config/selection/exit and per-harness binding. In parse return only properties/verdict/failed_properties; specialize unsafe_control to src/lib.rs:12 without weakening conditions. No new module/framework. |
| P `config.yml` | KEEP EXACT: script test.sh, expected expected. |
| P `test.sh` | KEEP EXACT and executable: set -euo pipefail; python3 check.py. Five-line platform-standard wrapper propagates failures. |
| P `expected` | KEEP EXACT: `Shared function checks agree for singleton and paired harnesses.` The sentence remains true for the uninit singleton/pair comparison and appears only after all retained probes pass. |

## Every Rust harness and helper

| Current symbol | Disposition / distinct obligation |
| --- | --- |
| src/lib.rs `Padded` | KEEP exact layout/fields/repr(C). Struct-store padding makes the subsequent full u64 read unsafe under uninit checking. |
| src/lib.rs `read_value` | KEEP EXACT, inline(never), read at12. This is the body shared by the two harnesses and the precise required failure location. |
| src/lib.rs `read_indirect` | KEEP EXACT, inline(never). Distinct call depth on opposite sides of the pair; both variants meet at read_value. |
| src/lib.rs `delayed_harness` | KEEP body/initialization/cast/store and cfg structure; rename feature only. Under uninit checking: singleton and paired both must fail at read_value, preserving detection of actual bad initialization. Ordinary pair: expected verifier SUCCESS with no uninit checks, not a memory-safety proof for this program. |
| src/lib.rs `initialized_control_harness` | KEEP body, value7 and result==7 assertion; rename feature only. Under uninit checking: singleton and pair SUCCESS, assertion property SUCCESS and identical full normalized inventory. Ordinary pair SUCCESS with assertion property SUCCESS and no uninit properties. |
| control.rs `Padded` | REMOVE with file. Duplicate standalone layout, no cross-harness body/cache. |
| control.rs `uninitialized_control` | REMOVE with both explicit main probes. Raw-padding detection has an existing expected baseline; this regression's delayed harness remains a stronger local activation/location oracle for its own checked read. |

Supporting existing baselines, unchanged between base and head: `tests/expected/uninit/access-padding-uninit/access-padding-uninit.rs:11–16::check_uninit_padding` and `.expected` demand raw u8 padding UB; `tests/kani/Uninit/access-padding-init.rs:10–15::access_padding_init` reads an initialized data byte. These are supporting generic checks; the retained regression itself must still fail at its full-word read of overwritten interior padding. Do not replace that local negative with mere reliance on baseline suite status.

## Every Python helper and control/oracle

| Current helper/data | Disposition / requirements |
| --- | --- |
| `HERE` | KEEP: resolved test directory for cwd/manifest/source. |
| `NAMES` | KEEP EXACT two names in the same order for filters and result binding. |
| `UNINIT` | KEEP exact diagnostic prefix; unsafe failures must also have class safety_check and source file/line. |
| `require` | KEEP. Its ValueError checks remain active independently of Python assertion optimization. |
| `inventory` | KEEP behavior: per-harness stdout grouping, duplicate harness rejection, property IDs/indices/status/description/location. Regular serial output is necessary; no file-wide substring shortcut. |
| `parse` | KEEP all existing validations and exported/printed identity joins. Replace only result[name] assignment with an explicit dict containing properties=props, verdict=verdict['verdict'], failed_properties=failed; all consumed fields remain. Do not drop exact inventories, safety flags, completed verdicts or failure partitions as boilerplate. |
| `signature` | KEEP normalized tuple list and multiplicity. Optional comment: `Compare check identities, statuses, descriptions and locations; numeric suffixes may vary between builds.` |
| `unsafe_control(harness, file, line)` | SPECIALIZE to unsafe_control(harness), requiring the same nonempty completed safety failures, UNINIT prefix, file suffix src/lib.rs and line '12'. Delete only control.rs:16 dispatch. No generic-exit or any-failure replacement. |
| `ordinary_control` | KEEP EXACT behavior for both paired entries with the flag off. Positive verdict alone is insufficient: require empty failed_properties and no uninit descriptions. |
| `compare` | REMOVE independent uninitialized_control block. For uninit mode, keep delayed singleton/pair unsafe controls, initialized singleton/pair assertion SUCCESS and both complete signature equalities. For ordinary mode, inspect both paired entries with ordinary_control and the paired initialized assertion SUCCESS; no absent singleton key access or signature comparison. Rename mode keys as specified. |
| `probe` | KEEP fresh JSON unlink, explicit exact filters, regular output, -j1, flags, timeout120, exit0/1 handling, stdout+JSON parsing and useful diagnostics. The command is now cargo kani in every case. Do not conflate expected verification exit1 with crashes/partial exports. |
| `main` | REMOVE the independent control entry and standalone kani/RUSTFLAGS edition override. Keep environment cleanup, temp directory, per-case unique target directories, separate flag modes, JSON path freshness and final marker after every comparison. Schedule the eight cases below, not a new cross-product. |

## Complete current invocation disposition

Current feature-on mode `delayed_first` becomes `delayed_indirect` with `--features delayed-indirect`; delayed uses read_indirect and initialized uses read_value. Feature-off `control_first` becomes `control_indirect`; delayed uses read_value and initialized uses read_indirect. Neither label promises compiler order.

| Current flag / mode / case | Exact disposition and future oracle |
| --- | --- |
| uninit / independent uninitialized_control | REMOVE with control.rs. |
| ordinary / independent uninitialized_control | REMOVE with control.rs. |
| uninit / delayed_first / delayed_alone | KEEP as delayed_indirect. Exact delayed name only; exit1; nonempty, correctly located uninit safety failures. |
| uninit / delayed_first / control_alone | KEEP as delayed_indirect. Exact initialized name only; exit0; result==7 property SUCCESS. |
| uninit / delayed_first / paired | KEEP as delayed_indirect. Exact two names; exit1; delayed fails as above, initialized succeeds with assertion SUCCESS; each full signature equals its corresponding singleton. |
| uninit / control_first / delayed_alone | KEEP as control_indirect, same bad-harness requirements for the direct call path. |
| uninit / control_first / control_alone | KEEP as control_indirect, same good-harness requirements for the indirect call path. |
| uninit / control_first / paired | KEEP as control_indirect, same paired requirements and per-harness signature equalities. |
| ordinary / delayed_first / delayed_alone | REMOVE. Flag-off paired run covers the same plain/default behavior; uninit singleton coverage is retained. |
| ordinary / delayed_first / control_alone | REMOVE. Its initialized result property is explicitly checked in the ordinary paired run. |
| ordinary / delayed_first / paired | KEEP as delayed_indirect. Exit0, exact two names, both completed SUCCESS, nonempty inventories, no failed/unresolved/uninit properties, initialized result assertion SUCCESS. |
| ordinary / control_first / delayed_alone | REMOVE for the same flag-off reason; its alternate call path remains in the paired run. |
| ordinary / control_first / control_alone | REMOVE; paired initialized assertion remains mandatory. |
| ordinary / control_first / paired | KEEP as control_indirect, same ordinary paired oracle. |

Implementation schedule inside the existing uninit/mode loops: choose the existing three named cases when uninit is true, and only ('paired', NAMES) when false. Initialize runs={} instead of seeding it with uninitialized_control. Preserve target-dir separation by flag, mode and case and fresh results.json per probe. compare must retrieve singleton keys only in the uninit branch. No new Rust harness or generic runner abstraction is required.

## Robustness and acceptance boundaries

Preserve these failure conditions: stale/missing/malformed JSON; incomplete run; missing, duplicate or unmatched harnesses; zero/partial properties; unresolved/error/unsupported failures; stdout/JSON identity disagreement; wrong verification exit; unsafe failure at another location or for another reason; failed/unreachable initialized assertion; extra/lost/changed paired properties. Per-harness records and complete normalized signatures are essential; matching just counts, one bad failure and one global success sentence would miss the original cross-harness leakage.

Keep both call-path shapes and all uninit singleton/pair comparisons. A later implementation should recheck the pure oracle's acceptance/rejection cases after the small schedule/key/return-record edits, without adding a new schema-test framework. Actual compiler/base-vs-fixed behavior, order and all native outcomes still need separately authorized validation; this review supplies no causal-order trace or native pass. Default compiler behavior, flags/checks, namespaces, Cargo isolation and platform discovery must remain intact. No new ignores, diagnostic goldens or check suppression are proposed.
