# Independent CI candidate review

## Reviewed identities

- Baseline: `0c1cc8a7d05184044d496b01f5ed41cebfde0cac`, tree `cbb04807c711a9d1bad2ac2dbe1f77538d5658b0`.
- Candidate: `c9619b15022fb43f1e961e01695e64875ad68fe9`, tree `e17787b7ef41250e8e55bb90e2fc7f5d254943ba`.
- Review-packet diff SHA256: `3c1f4f5f38a3d146799b13bf0fac797ddd86960d01c99ce2c13107ce9284f71e`.
- Candidate worktree: `/root/kani-fix-3300-sel1-replay-w15`, branch `ci/kani3300-sel1-replay-w15`; clean at review.
- SEL1 tool pin: commit/export `46e46583ff112cae9c43aea1ba5dd6145e5e8387`, tree `0a46fad6c1adc3022d39e25a45096ed9cd622844`.
- Frozen std base: `70ba5befc617627073738e26cb1466bd4fb76e41`, commit tree `84ab170ccdcc29fba69e55e0a46e6acdf52d9704`, library tree `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`.
- Test overlay commit/library tree: `6075e7ce17179f45642c9ffe8fe09e3ec9395726` / `12e87bd4a4e141a8f829d8a0519efc09260c5059`.
- Request SHA256: `8e9c8bf74858fdfd76c24c21e24c039bf11e8cb78d8a8ca39a92cbdf693ac70a`.
- Test patch SHA256: `473526895d6d57a99bd356a060195745cc6aba9ee2b70fcc7ae90fecb6676f06`.
- Package delta SHA256: `cbcb31b360b872d6ed8e8440b0decf15d424cf47f9e6f5f82dff01bea435b27a` (70,994 bytes).

## Findings

No blocking correctness findings in the reviewed CI-only candidate or its delta packaging.

The candidate has exactly the six issued ON row IDs. The row selectors, modes, unwind bounds, expected result/failure counts, exact argv, environment, flags, output paths, and standard-library bindings match the issued request. Its fixed request and patch digests are checked before preparation or execution. `verify-source` also passed against `/root/kani-fix-3300-sel1`: it confirmed the pinned commit/tree, 42 bound source files, six bound subtrees, request digest, and std identities.

The std overlay in the local clone has the five requested file hashes. Comparing pinned base and overlay commits showed the expected `library` tree transition and the five intended source paths; the additional `research/` files belong to the separate overlay commit, not to the CI test patch or the replay std checkout. The replay preparation code pins the base commit, verifies commit and library trees, applies the hashed patch once, and checks exact changed paths and patched bytes.

The workflow has the requested push-only branch trigger and repository guard, a six-row matrix, `max-parallel: 1`, 60-minute job cap, no retry mechanism, and a Python service-test preflight before source checkout/build. It preserves the run4 std URL, `$RUNNER_TEMP/kani3300-std` destination, and shallow submodule initialization. No compiler or standard-library production files are changed by the candidate diff; changes are limited to replay CI paths and the test-only std overlay.

Receipt behavior is fail-closed for malformed, missing, partial, null, wrong-type, wrong-selector, and explicit `NOT_RUN` exports. It records original positive child exits, signals, timeout, wait4 RSS, logs, and runtime identities; an atomic initial receipt precedes fallible postprocessing. Successful envelopes stay `UNKNOWN` pending property/body review. The raw-negative row preserves the child's nonzero exit and requires manual review of the intended `source[1]` failure; a red CI row is therefore possible by design.

The uncommitted package delta generator's `--check` passed. Its temporary-Git reverse/check/apply round trip reproduced every full-export path byte-for-byte and removed the replaced C1 paths. The patch checksum matched the adjacent checksum file. The source candidate repository remained clean and unchanged.

## Validation performed

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_replay.py`: 29 tests passed.
- `python3 make-ci-delta.py --repo /root/kani-fix-3300-sel1-replay-w15 --package .../sel1/ci --output .../ci-overlay-delta.patch --check`: passed exact-base round trip and checksum verification.
- `replay.py verify-source --repo /root/kani-fix-3300-sel1`: passed exact immutable-source checks.
- `git diff --check` and production-path diff check: passed; no production paths changed.

## Evidence limits

All six replay rows, Kani runs, and proof outcomes remain `NOT_RUN`. This review grants no proof credit, CI admission, or authorization to publish or dispatch. The raw-negative acceptance remains manual, and successful result envelopes alone cannot establish proof credit.
