# SEL1-C2 worker15 — Gate A READY, runtime NOT_RUN

Source FREEZE: `14bc57fdb99960240c4944845a3d985c8af4dcf7`, tree `1efb6e4dfa69d346df8e23741d11839b1932403d`.
CI-only package: `b69a040ded46d5ee7edf35b8eb727b66e5838930`, tree `4141fba67952dc6ac018ecc3dc17b96e49461533`, parent FREEZE.
Local worktree `/root/kani-fix-3300-sel1-c2-w15`, branch `uninit-ci/sel1-c2-gatea-w15`.
No push, dispatch, local build, source edit or replay preparation in this session.

Worker14 reviews the candidate and bindings before the coordinator launches it. Independent bounded Luna review is recorded
separately in REVIEW.md; it does not impersonate worker14 or establish native acceptance.

The only workflow is `.github/workflows/kani3300-sel1-c2-gatea.yml`, push on `uninit-ci/sel1-c2-gatea-*`, fork-only jobs.
The requested research/CI commit convention requires `[skip ci]`, so pushing the prepared package SHA alone **will skip CI**.
After review the coordinator creates one empty trigger commit without a skip marker, as a child of this package,
and pushes that head once to a fresh matching fork branch. No workflow_dispatch or preliminary diagnostic run is needed.
Worker15 has not created or pushed that trigger commit. This is a publication instruction for the authorized coordinator.

Before the single push, verify the trigger commit's parent equals the package SHA, its tree equals the package tree,
the fork source object/ref resolves to exact FREEZE, and the branch is available without force/update of another owner's ref.
Push the reviewed trigger SHA to `https://github.com/Tiramisu-Cake/kani.git`, branch matching the above pattern.
Check the resulting remote head and run head equal that exact trigger SHA, run_attempt1, the expected workflow,
and exactly three platform jobs. Never rerun/retry automatically.

Runtime `GITHUB_SHA`/control identity is the trigger SHA; the packaged overlay SHA remains provenance.
All rows and the aggregate must bind the same trigger SHA, source SHA/tree and run ID. The observer accepts no alternate source.
The empty trigger commit changes no source or CI recipe bytes. Record its exact SHA in the coordinator launch record.

Seven requested checks before READY:

1. Matching push trigger; no fork workflow_dispatch reliance. Skip marker publication handling stated above.
2. `runner.arch` is only in the artifact step env; upload consumes `env.GATE_ARCH`. No runner context at workflow/job scope.
3. All three checkout declarations have fetch-depth2, including independent export and summary control.
4. Sibling `control`/`export`; lifecycle cwd control with `../export`; regression cwd export with `../control` observer/binding.
   Gate A has no Quick structural-input path normalization or selected-root path comparison.
5. Regression job never checks out a Cargo workspace at their parent; setup receives `kani_dir: export`.
6. Accepted owner-variable guard for Bash3.2 retained byte-for-byte; Linux shell self-test passed, macOS runtime remains NOT_RUN.
7. `check_workflow.py` parses duplicate-free YAML, checks available expression contexts, references, shell syntax,
   matrix/caps/always paths, exact binding/copies and CI-only scope. Four known-error mutations rejected.
   This targeted offline checker is not the complete upstream actionlint implementation.

`VALIDATION.json`: static checks PASS, 26 synthetic observer/lifecycle tests PASS, shell self-test PASS.
`CI-REQUEST.json`, `CI-OVERLAY.json`, `LOCAL-CI.json`, `TEMPLATE-INVENTORY.json` contain exact local identities and hashes.
`ci-only-template.patch` is the exact binary-capable diff from FREEZE to the package.
`full-export/` contains the exact six added files. Stock workflow deletion is confined to the CI-only commit.

Gate A remains NOT_RUN: require all three complete clean-source receipts, 33 ordered stages each, script exit0,
complete bounded events and actual runtime identities; inspect counts/ignores and explain SEL1 additions against C2.
Missing/failed/truncated/UNKNOWN events require coordinator review. No formal proof credit or replay admission follows from READY.
