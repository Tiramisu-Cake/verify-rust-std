# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0c1cc8a7d05184044d496b01f5ed41cebfde0cac`
- Candidate: `c9619b15022fb43f1e961e01695e64875ad68fe9`
- Candidate tree: `e17787b7ef41250e8e55bb90e2fc7f5d254943ba`
- Diff SHA256: `3c1f4f5f38a3d146799b13bf0fac797ddd86960d01c99ce2c13107ce9284f71e`

## Defect

Rebind exact Gate B-prime replay CI recipe to SEL1 tool/std and six issued ON rows, retaining run4 fixes and service controls.

## Applicability

CI-only overlay and delta packaging; no compiler/std production code edits. Owner reported quick43605855700 started on tool46e46583ff; no runtime result queried.

## Invariants
- Exact tool46e46583ff112cae9c43aea1ba5dd6145e5e8387 tree0a46fad6c1adc3022d39e25a45096ed9cd622844; frozen std70ba plus exact test-only overlay6075e7ce17179f45642c9ffe8fe09e3ec9395726; five exact patched hashes.
- Exactly six issued ON rows, jobs1/maxparallel1/no retries, inherited60min job and2400s child caps; sort4 SUCCESS and raw-negative intended source[1] failure.
- Keep original child exit, timeout/signal/wait4RSS, atomic partial receipts, setupNOT_RUN fallback, useful property review; never infer credit from success envelope or arbitrary failure.
- Preserve run4 std URL, --destination and submodule init. Push trigger only ci/kani3300-sel1-replay-w15 with existing repository guard.
- Changes only replay CI paths; no build/push/CI/tool invocation.

## Required controls
- 29 service unittest cases pass, original20 retained with six-row inventory/cap adaptations; preparation/runtime mocks never run Kani or clone.
- make-ci-delta.py generation and --check passed, reverse/check/apply in temporary Git recreates seven full-export paths exactly from immutable0c1 base.
- Reject request/source-stage/target/argv/profile/std binding mismatches; preserve explicitNOT_RUN, partial/missing/null/wrong-type and original failure exits.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)
- `rust-toolchain.toml` → `dependencies/0001.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)
- `kani-dependencies` → `dependencies/0002.bin` (mode 100644, SHA256 94bfe751e4574561519bd26a99196280eb018c30d9db408416b231ddb6f8b7bc)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- All actual six-row replay builds/proofs/outcomes NOT_RUN. Only local Python tests/static Git metadata performed; no push/network/CI.
- Raw negative may leave CI row red because original nonzero exit is preserved; expected-negative acceptance remains manual review.
- Generator/package artifacts in g0 sel1/ci are uncommitted; source CI overlay commit is local.

Do not execute source or evidence from this packet. Do not claim new proof credit.
