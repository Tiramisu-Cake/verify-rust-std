# HANDOFF — PR5195 cleanup, one stage complete

The authorized offline implementation stage is complete. **Stop at HANDOFF.** No push, CI, native tool execution or external PR/body update was performed. This is a committed cleanup candidate, not a native validation or publication approval.

- PR: model-checking/kani#5195, published branch Tiramisu-Cake:fix/per-harness-global-transforms.
- Pinned parent: `9b67828707f8d7d5e691484896a82475dcf34d28`.
- New worktree: `/root/kani-pr5195-cleanup-w11`.
- New local branch: `cleanup/pr5195-20261119`.
- Cleanup commit: `153be639a0c048e3be3d1f1f006e47060fd74e83`.
- Cleanup tree: `7f784cca53dc02589d5c8459a2fe4217395122bf`.
- Exactly one commit above the pinned parent; author and committer: Tiramisu-Cake <igkharin@gmail.com>.
- Commit message: `Simplify shared-body regression coverage and call-path labels` (no skip-ci or Co-Authored-By).
- The g0 packaging commit includes [skip ci]; its full SHA is reported in the delivery message to avoid a circular self-pin.

[FINDINGS.md](FINDINGS.md) records the coordinator's independent **CONFIRMED** disposition and pinned code evidence for every proposed edit. It was written before candidate edits. No proposed edit was withdrawn; historical native outcomes, deterministic ordering and speedup were not accepted as established evidence. The pr-9487 correction was read, and actual Kani discovery, runner and export code were inspected rather than assuming generic test semantics.

The implementation changes four paths under `tests/script-based-pre/delayed-shared-body/`: rename the feature in Cargo.toml and the four cfg strings in src/lib.rs; delete control.rs; adjust check.py. It removes the two standalone padding-control invocations and four ordinary singleton repeats. It keeps all six uninit runs and both ordinary paired runs. Mode names are now `delayed_indirect` / `control_indirect`, and the feature is `delayed-indirect`; they describe which harness takes read_indirect and make no promise about compiler order.

The parser returns only its three consumed fields. unsafe_control is specialized to src/lib.rs:12 with every previous predicate retained. The signature comment describes the compared fields. The ordinary branch never retrieves removed singleton results. No generic runner/framework, suppression, new harness or compiler change was introduced.

## Retained invocation matrix (source-inspected, NOT_RUN)

Both modes use fresh target directories keyed by flag/mode/case. delayed_indirect enables `--features delayed-indirect`; control_indirect uses the default feature-off path. Every invocation uses cargo kani, the exact package manifest and --lib.

| Checks | Path mode | Case | Exact requested harnesses | Required process exit and oracle |
| --- | --- | --- | --- | --- |
| uninit | delayed_indirect | delayed_alone | delayed_harness | 1; uninitialized safety failure at read_value, src/lib.rs:12 |
| uninit | delayed_indirect | control_alone | initialized_control_harness | 0; initialized equality assertion SUCCESS |
| uninit | delayed_indirect | paired | both names | 1; same unsafe failure, initialized assertion SUCCESS, each full signature equals its singleton |
| uninit | control_indirect | delayed_alone | delayed_harness | 1; uninitialized safety failure at read_value, src/lib.rs:12 |
| uninit | control_indirect | control_alone | initialized_control_harness | 0; initialized equality assertion SUCCESS |
| uninit | control_indirect | paired | both names | 1; same unsafe failure, initialized assertion SUCCESS, each full signature equals its singleton |
| ordinary | delayed_indirect | paired | both names | 0; both SUCCESS, no failed or uninit properties, initialized assertion SUCCESS |
| ordinary | control_indirect | paired | both names | 0; both SUCCESS, no failed or uninit properties, initialized assertion SUCCESS |

## Preserved oracle and source integrity

References below are in the cleanup commit's `tests/script-based-pre/delayed-shared-body/check.py`.

| Required protection | Retained implementation / inspection evidence |
| --- | --- |
| Exact selection and completed exports | parse:49–67 still requires schema 0.1.0, COMPLETE/COMPLETED, exact requested filters, no unmatched filters, exact counts/names in JSON and stdout. probe:148–154 retains --exact, -j1, regular output, export-json and per-name filters. |
| Actual check flags/configuration | parse:52–60 still checks the exact unstable feature set, empty cbmc_args, coverage disabled, enabled safety/overflow/unwinding/undefined-function/reachability checks, prove_safety_only=false and ignore_global_asm=false. probe:151–152 adds both ghost-state and uninit-checks only for uninit runs. |
| Nonempty per-harness inventories and identity joins | inventory:24–46 retains per-harness grouping and duplicate rejection. parse:69–98 retains nonempty/exact totals, sequential indices, unique IDs, nonempty identity strings, resolved statuses, exact partitions, no unresolved/errors, no coverage, completed verdicts, failed-property ID joins and stdout description/status joins; unsupported failures still fail. |
| Unsafe failure reason/class/location | unsafe_control:111–116 requires FAILURE, nonempty failures, each status FAILURE, class safety_check, UNINIT description prefix, file ending src/lib.rs and line '12'. compare:131–134 applies it to delayed singleton and pair in each uninit mode. |
| Initialized assertion SUCCESS | compare:129–144 checks successful initialized verdict and the exact SUCCESS property `assertion failed: result == 7` in every retained initialized singleton/pair. |
| Singleton/pair signatures | signature:104–108 retains all normalized-ID/status/description/location tuples and multiplicity; compare:136–137 compares both harnesses separately in both uninit modes. No count-only/global-text replacement. |
| Ordinary paired behavior | ordinary_control:119–123 and compare:138–140 require both pair entries to succeed without failed/uninit properties, with the initialized assertion additionally required. |
| Fresh exports/targets/environment and exits | probe:148 unlinks each old export; main:165–186 keeps the temporary directory, cleared inherited flags/targets, unique per-case target dirs and manifest/feature binding. probe:155–162 retains timeout120, allowed native exits 0/1, JSON reading and diagnostic propagation; parse:100 still binds exit to exported verdicts. Final success marker appears only after all comparisons. |
| Compiler and regression fixtures | Both compiler files are byte-identical to parent, including comments. Both proof harnesses, read_value/read_indirect, initialization/cast/store/assertion and inline(never) boundaries remain; inverse feature-name replacement reproduces the parent Rust file exactly, with dereference still line12. config.yml, expected and executable test.sh are byte-identical. test.sh still propagates Python failure; inspected compiletest code requires script exit0 as well as expected output. |

[STATIC-CHECKS.json](STATIC-CHECKS.json) records byte hashes and the committed candidate identity. Compiler file SHA256 values are `14cf16762c3475238941c254fc4080b00149c1618a156a5baab8dbdc7de78db3` (compiler_interface.rs) and `0901d9ee2f60efb02949200822406713a4a1e6f068ecb52d053716a6c07957b7` (transform/mod.rs). Committed bytes were checked again after committing.

## Validation and next-stage boundary

PASS: Python `compile(source, filename, 'exec')` syntax check without executing the source; `bash -n test.sh`; `git diff --check`; static byte and AST comparisons. require/inventory/signature/ordinary_control/probe ASTs are unchanged. parse AST is unchanged apart from the explicit three-field return record; unsafe_control AST is unchanged apart from replacing its file/line parameters with the retained location constants. The eight-case schedule and compare branch were inspected as source, never executed. An initial auxiliary static-inspection assertion selected the configuration loop instead of the harness loop; selecting the entry loop corrected that inspection script without any candidate change.

NOT_RUN: dynamic/synthetic oracle checks, regression execution, cargo, rustc, Kani, CBMC, native base/fixed comparison, causal order trace, CI and independent review. Syntax/static checks do not establish native PASS, platform completeness, performance improvement or proof credit. The existing CI paragraph in the old PR snapshot was not promoted into validation for this candidate.

[PROPOSED-PR.md](PROPOSED-PR.md) is the concise updated body draft, with the license and AI disclosure lines checked exactly against the original pinned PR body. Suggested title remains “Keep delayed UB instrumentation specific to each harness.” The draft explicitly reports syntax-only validation and no native/CI run for this revision. It has not been published.

The candidate worktree is clean. `/root/kani-pr5195-slop-readonly-20261119` remains clean at the original head. The PR branch was not checked out or mutated. g0 commits only this new cleanup directory; other workers’ files and index entries are left alone, including the unrelated ch8-s4/ch8-s5 work present at intake. No phases, owners, budgets, ledgers, evidence records, settings or other workers' files were changed. No subagents were used.

Next work requires a separate assignment for any further review, native validation, push, CI or PR-body publication. This one-stage task stops here with HANDOFF.
