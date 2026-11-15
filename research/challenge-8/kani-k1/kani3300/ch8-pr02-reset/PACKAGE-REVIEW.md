# PR02 entry-reset CI package — independent review

Reviewer: independent Codex reviewer, Luna High. This is the CI-package continuation for source candidate `f695f653efaa1f7ac6774a079104de8cc0ff81fc`; source review remains recorded separately at `/root/ch8-pr02-reset-review-source/REVIEW.md`. No source edits, Rust compilation, Kani/CBMC run, build, push, CI, or raw-log review was performed.

## Identity and packet

- Baseline: `f695f653efaa1f7ac6774a079104de8cc0ff81fc`
- Package candidate: `b4edbb18bc8a490197420aac0964a7d55b284380`
- Candidate tree: `a5a1c0b0b06c8af67ec132f107883222e2d220c1`
- Diff SHA256: `2fefcfbbca221361510fd84f637effd57a126caf047d18d7ee6a649dde53e688`
- Spec SHA256: `039b7dc647a11308726f8c78b6bf54692f02e89c3384d22654ae734d852e0e06`
- Packet SHA256: `1fad110a7573174350cecb9bcca658d8d9001e9c8df65078237b87467ba7aa09`
- `smallsort-session review check` returned `PACKET_VALID_NOT_REVIEWED`, 23 files, proof credit `NONE`; this verifies packet identity only.
- The superseded package candidate `cbcffa8365b65c0373e6bf71c3bf2d638b327ef4` had an invalid `cargo test -p kani-compiler --lib` target. The final candidate fixes this to `--bin kani-compiler` and adds a static guard for the package target and formatting command.

## Findings

No remaining package blocker found for the pinned candidate.

- The workflow in `.github/workflows/ch8-pr02-reset.yml` is push-only on `uninit-ci/ch8-pr02-reset-*`, repo-gated, and has one A/B matrix with `max-parallel: 1`, a 120-minute job cap, and `CARGO_BUILD_JOBS=2` / `RUST_TEST_THREADS=2`. All checkouts specify `fetch-depth: 2`. The gate asserts first attempt, `HEAD == GITHUB_SHA`, equal child/parent trees, and `[skip ci]` on the parent message. `runner.*` appears only as step-level `env` values. Other stock workflows are removed in this CI-only tree; source checkouts are separate pinned repositories.
- `CI-REQUEST.json` pins PR02 and SEL1 commit/tree pairs, the patch SHA256 `52173eb8126f00e7cc3285f4b7bd4941e42cec78a9e822588e7bc9cce23ec91a`, and both fixture hashes. `apply_patch.py` verifies the exact HEAD/tree and patch digest, runs `git apply --check`, applies the patch, and verifies the resulting tree. Static checks also bind the source candidate to the expected tree. The request explicitly records runtime `NOT_RUN` and emitted model evidence `NOT_RUN`.
- Arm A's `scripts/ch8-pr02-reset/run_arm_a.sh` now runs `./scripts/kani-fmt.sh --check`, build, workspace/test Clippy with `-D warnings`, `cargo test -p kani-compiler --bin kani-compiler`, compiletest build, and focused uninit, function-contract, new autoharness-reset, and existing autoharness suites. `scripts/kani-fmt.sh` covers crate formatting and Rust test sources, including the added standalone fixture files. `kani-compiler/Cargo.toml` defines package `kani-compiler` with `src/main.rs` and no `[lib]` or explicit bin section, so the corrected Cargo test target matches Cargo's default binary target and includes its module unit tests.
- The old-control runner extracts each fixture's Kani invocation and runs it from a fresh temporary directory against the unpatched PR02 binary with the same source and flags. The three seeded cases (`seed_only`, `argument_seed`, `contract_seed`) require return code 1 and the exact missing-reset fatal. The negative uninitialized-read control accepts either the intended UB failure or success as an observation; other unseeded/initialized/OFF controls require successful completion. This keeps old behavior observable without treating it as proof credit.
- Arm B's two fixture files are byte-identical to the A1 native inputs (SHA256s match). The automatic invocation preserves the original subcommand, autoharness flag, sanity-check flag, duplicate uninit flags, unstable option, `RUST_BACKTRACE`, and `RUSTFLAGS`; it adds only bounded export/timeout/jobs/output settings. The explicit companion uses its own exact proof selector. `run_arm_b.py` binds each completed result to stage B, exact SEL1 source SHA and patched tree, target, harness name, normalized source filename, and automatic/manual harness kind. It requires one selected harness, complete run state, completed-success outcome, and one-success/zero-failure summary; it then runs the repository export-schema validator. Timeout, nonzero exit, missing/malformed/partial export, wrong target, wrong selection/name/file/generation/outcome, and invalid summary fail closed. `test_runner.py` contains five synthetic error-path test methods, including mismatched bindings. These checks do not establish emitted reset/model behavior.
- Final two-file delta from the superseded package is localized to the corrected test/format commands and static verification of those commands. Source candidate remains unchanged.

## Recommendation

**GO for the pinned CI-only package review scope** and source-plus-package handoff. This is not a CI result, runtime proof, or evidence of reset emission in a generated model. All compilation, regression, and verifier outcomes remain `NOT_RUN`; proceed only under the coordinator's existing CI dispatch controls.
