# HANDOFF — independent PR5195 cleanup review

**Verdict: APPROVE.** No required code or PR-body changes. The actual pinned diff implements the proposed reduction without weakening any oracle on a retained run. Approval covers this offline cleanup review; native regression results and CI remain **NOT_RUN**. The authorized one-stage task is complete. **Stop with HANDOFF.**

## Reviewed identities and scope

- Date: 2026-11-19.
- PR: model-checking/kani#5195.
- Candidate worktree: `/root/kani-pr5195-cleanup-w11`, branch `cleanup/pr5195-20261119`.
- Parent: `9b67828707f8d7d5e691484896a82475dcf34d28`.
- Candidate: `153be639a0c048e3be3d1f1f006e47060fd74e83`.
- Candidate tree: `7f784cca53dc02589d5c8459a2fe4217395122bf`.
- Verified HEAD/branch, sole parent and exactly one commit above that parent. Candidate worktree was clean.
- Read the complete parent-to-candidate diff and the actual checker, Rust fixture, package configuration, expected output and wrapper. Also read the author's `../pr5195-cleanup/{HANDOFF,FINDINGS,PROPOSED-PR}.md` and the original recommendation's `../open-pr-slop-review/pr-5195/REPORT.md`, `COVERAGE-EDITS.md` and `INPUTS.json`. Conclusions below come from source inspection and independent byte/AST comparisons, rather than accepting the author's verification claims.

All source references below refer to the candidate unless explicitly labeled parent. `P` means `tests/script-based-pre/delayed-shared-body/`.

## Findings

### 1. Change boundary and compiler integrity — PASS

Exactly four paths differ: `P/Cargo.toml`, `P/check.py`, deleted `P/control.rs`, and `P/src/lib.rs`. Both compiler files are byte-identical between parent, candidate and working tree, including comments:

| Compiler file | SHA256 |
| --- | --- |
| `kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs` | `14cf16762c3475238941c254fc4080b00149c1618a156a5baab8dbdc7de78db3` |
| `kani-compiler/src/kani_middle/transform/mod.rs` | `0901d9ee2f60efb02949200822406713a4a1e6f068ecb52d053716a6c07957b7` |

Inverse replacement of `delayed-indirect` with `delayed-first` reproduces the parent's Cargo.toml and Rust fixture exactly. Both proof harnesses, `Padded`, the cast/struct store, initialization to 7, equality assertion and both `inline(never)` helpers remain. `read_value` still dereferences at `src/lib.rs:12`.

### 2. Fourteen to eight driver invocations — justified reduction

Parent `check.py:175–187` schedules `2 × (1 + 2 × 3) = 14` probes. Candidate `check.py:173–186` schedules six uninit probes plus two ordinary pairs. Every retained probe uses `cargo kani`, the package manifest, `--lib`, exact name filters and its own target directory.

| Checks | Mode | Case / selected names | Required result |
| --- | --- | --- | --- |
| uninit | delayed_indirect | delayed_alone / delayed_harness | exit 1; uninit safety failure at src/lib.rs:12 |
| uninit | delayed_indirect | control_alone / initialized_control_harness | exit 0; initialized equality assertion SUCCESS |
| uninit | delayed_indirect | paired / both names | exit 1; respective failure/success; both signatures equal their singletons |
| uninit | control_indirect | delayed_alone / delayed_harness | exit 1; same location-bound uninit failure |
| uninit | control_indirect | control_alone / initialized_control_harness | exit 0; initialized equality assertion SUCCESS |
| uninit | control_indirect | paired / both names | exit 1; respective failure/success; both signatures equal their singletons |
| ordinary | delayed_indirect | paired / both names | exit 0; both SUCCESS, no failures/uninit properties; initialized assertion SUCCESS |
| ordinary | control_indirect | paired / both names | exit 0; same ordinary paired oracle |

The deleted standalone `control.rs:12–17` reads raw padding, has no shared `read_value` body and cannot distinguish harness-local delayed instrumentation. Its two runs are redundant for this regression's obligation: `delayed_harness` still supplies a local negative in both singleton and paired uninit runs for both call paths, checked specifically at the actual shared read. Generic raw-padding detection remains at `tests/expected/uninit/access-padding-uninit/access-padding-uninit.rs:12–15` (`check_uninit_padding`), with its `.expected` requiring the uninitialized-pointer failure and one failed harness. `tests/kani/Uninit/access-padding-init.rs:11–14` (`access_padding_init`) retains the initialized-data-byte positive baseline. All three supporting files are byte-identical to parent. These are supporting source oracles, not newly executed results or a claim of identical layouts: the generic negative reads trailing padding of `S(u32, u8)`; this regression reads a full u64 after a padded struct store.

The four removed ordinary singleton runs repeat the default-check behaviors still required separately for both entries of both ordinary pairs. The compiler's uninit-specific clone branch is unchanged (`compiler_interface.rs:404,437–442`); `DelayedUbPass::is_enabled` uses the same Uninit predicate (`delayed_ub/mod.rs:56–60`). Ordinary paired runs still exercise the shared-cache path and both call-path shapes. The removed ordinary singleton/pair signature comparisons are intentionally no longer coverage: they are not a distinct delayed-uninit obligation. All four uninit per-harness signature equalities remain. Thus this is a justified scope reduction, not a claim that eight runs reproduce every observation from fourteen, nor a measured speedup.

### 3. Retained oracles and plumbing — PASS

| Protection | Actual candidate enforcement |
| --- | --- |
| Exact selection and completed export | `check.py:49–67`: schema 0.1.0, COMPLETE/COMPLETED, exact requested filters and counts, no unmatched filters, exact names/counts in JSON and stdout. |
| Flags/configuration | `52–60,149–154`: exact unstable feature set; ghost-state and uninit-checks only in uninit runs; no coverage/custom CBMC args; memory safety, overflow, unwinding, undefined-function and assertion reachability enabled; no safety-only/global-asm bypass. |
| Per-harness inventory | `24–46,69–90`: duplicate harness rejection; nonempty inventories, exact property totals, sequential indices, unique nonempty IDs, nonempty status/description/location strings, resolved statuses, exact partitions and completed verdicts; no coverage or unresolved/error buckets. |
| Identity joins and unsupported failures | `91–98`: failed count and IDs equal the stdout-derived failure partition; failed/unsupported records join their property ID and status/description to that harness's stdout; failed unsupported constructs rejected. |
| Unsafe reason/class/location | `111–116,133–134`: delayed singleton and pair must have FAILURE and a nonempty failed set; every failure must be FAILURE, class safety_check, UNINIT-prefix description, file suffix src/lib.rs, line string '12'. The source read there is read_value's dereference. |
| Initialized assertion | `129–144`: initialized singleton and pair in each uninit mode, plus each ordinary pair's initialized entry, must have verdict SUCCESS and the actual `assertion failed: result == 7` property with status SUCCESS. |
| Singleton/pair signatures | `104–108,136–137`: compare each harness separately using the full sorted list of normalized ID/status/description/location tuples. Only a final numeric ID suffix is stripped; multiplicity remains. Both uninit modes retain both comparisons. |
| Ordinary checks | `119–123,138–140`: both paired entries must succeed, have no failed properties and no UNINIT-prefixed properties. The initialized assertion is checked additionally. |
| Fresh artifacts and environment | `148,165–186`: old JSON unlinked before every probe; fresh TemporaryDirectory; target directories unique by flag/mode/case; inherited Rust/Kani flags and target settings cleared; exact manifest and feature passed. Reusing the JSON pathname cannot reuse an old file. |
| Exits and completion marker | `100,155–162,187–192`: only native exits 0/1 accepted, actual exit equals whether any exported harness failed; missing/malformed JSON and exceptions propagate; timeout120 remains. Success marker prints only after all probes/comparisons. |

Independent AST comparison confirms `require`, `inventory`, `signature`, `ordinary_control` and `probe` are unchanged. `parse` differs only in the result-record assignment: the explicit `properties`, `verdict`, `failed_properties` fields are exactly those consumed downstream, with `failed` still the validated export list. `unsafe_control` differs only in removing its file/line arguments and substituting the retained constants. Every other predicate remains.

The ordinary branch retrieves only paired results; singleton lookups occur inside `if uninit`. No absent-key access was introduced by reducing the schedule.

The location guard remains the inherited file-suffix/line check; it is not a new function-name or AST-binding check. JSON-to-stdout joins bind IDs/status/descriptions, while failure file/line comes from JSON and signature locations come from stdout. This cleanup preserves those respective guarantees without claiming stronger source binding.

### 4. Wrong-result mutation reasoning — rejects the relevant mutations

These are static counterfactuals traced through the actual control flow, **not executed mutation tests**:

- Return an initialized SUCCESS for the bad read, or drop all its failures: `unsafe_control:112` fails even if parse/exit are internally consistent.
- Report a different failure reason/class/file/line, including line 13 instead of 12, or add an unrelated failure: the loop at `113–116` rejects it. A crash with exit 1 cannot substitute because complete parse/inventory and unsafe predicates still apply.
- Make initialized control fail: its explicit SUCCESS requirement at `142` fails, even if signatures agree. Remove its equality assertion or mark it UNREACHABLE: `142–144` fails even if the exported verdict remains SUCCESS.
- Add/drop/change a paired property while repairing totals, partitions and exits: `136–137` still rejects the changed signature. Status, description, location, normalized identity and multiplicity all participate. Renumbering only final numeric ID suffixes is intentionally accepted.
- Swap a success/failure record between harnesses: exact harness inventories and ID joins prevent aggregate-only acceptance; the named delayed and initialized controls independently reject exchanged outcomes.
- Select a subset, extra harness or wrong filter; report incomplete/partial/missing output, duplicate IDs, unresolved properties, wrong flags or mismatched failure identities: `32,49–98` or parsing exceptions reject it before comparison.
- In ordinary mode, report a failure or even a SUCCESS property describing uninitialized-memory checking: `ordinary_control:120–123` rejects it; omitting the initialized assertion is separately rejected.
- Return exit 0 for a failing export or exit 1 for an all-success export: `100` rejects it. Abnormal exits fail `156`; absent exports/timeouts cannot reach the terminal success marker.

No finite set of these counterfactuals establishes exhaustive parser correctness or rejects a coordinated fabrication of every input. They establish that the edited return plumbing and mode branches retain the concrete wrong-result rejection paths relevant to this cleanup.

### 5. Labels, discovery and PR text — PASS

`Cargo.toml:11`, all four Rust cfg strings (`src/lib.rs:27–39`), the feature argument (`check.py:184–185`) and both mode loops (`127,180`) consistently use `delayed-indirect` / `delayed_indirect` / `control_indirect`. Feature-on routes delayed through read_indirect; feature-off routes initialized through it. No old first/order labels remain in this regression. The names describe call paths; they do not promise an observed compiler order.

`config.yml`, `expected` and `test.sh` retain exact parent bytes and modes; test.sh remains 100755 with `set -euo pipefail` and `python3 check.py`. Its success sentence is unchanged and still true for the retained uninit comparisons; no feature/mode labels need changing there. Actual discovery uses config.yml directories (`tools/compiletest/src/main.rs:440–479`); `run_exec_test` runs the configured script, checks expected output and requires exit 0 (`runtest.rs:420–479`). The deleted control was explicitly invoked by check.py, not independently discovered through its Rust comments.

`../pr5195-cleanup/PROPOSED-PR.md` is accurate and concise. Its first paragraph describes the potential shared-body contamination; its second matches the conditional local clone/shared-cache implementation and the retained test matrix. It avoids deterministic-order, native reproduction and performance claims. The testing paragraph explicitly limits this revision to syntax checks and says native regression/CI have not run. The author's recorded shell syntax result is an author-package claim; this reviewer independently checked Python syntax only.

The license and AI disclosure lines were independently compared with `../open-pr-slop-inputs-20261119/pr-5195/PR-BODY.snapshot.md` and are each preserved exactly once, unchanged:

> By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.
>
> *Disclosure: this change and description were prepared with the help of AI assistants.*

Reviewed draft SHA256: `53d6e6cd28ab76f8ed7c96432ec3238b688e4f4b6bef41031106fb935f635b7c`. No body edits are requested or made.

## Validation and stopping boundary

Independent checks passed: Python `compile(source, filename, 'exec')` on committed parent and candidate checker bytes without executing either; AST comparisons described above; exact changed-path/parent/tree/branch/cleanliness checks; compiler/fixture/integration byte and mode comparisons; inverse feature renames; protected PR-line equality; `git diff --check` on the reviewed diff. No pycache or candidate files were written.

No dynamic/synthetic checker calls, shell-script execution, cargo, rustc, Kani, CBMC, CI, push, external messages or PR/body publication. No new native PASS, causal-order trace, platform-completeness result, performance result or formal proof credit is established. No subagents or settings changes. Existing g0 work from other workers, including unrelated staged files, is outside this review and must remain untouched; commit only this HANDOFF.

The task authorizes a local g0 review commit as Tiramisu-Cake <igkharin@gmail.com>, with `[skip ci]`. Its SHA is reported in the final response to avoid a circular self-pin. Further candidate changes, native validation or publication require a separate stage. **HANDOFF; stop.**
