# SEL1 six-row replay CI overlay

Preparation only. Current local candidate `e59c3527a852d805a4d1317a400a3229b398eead`, tree `bed4a1cffe4f12f86e017fec34276d3cd10f9d9d`, cumulative CI delta against exact Gate B′ recipe `0c1cc8a7d05184044d496b01f5ed41cebfde0cac` (tree `cbb04807c711a9d1bad2ac2dbe1f77538d5658b0`). Clone `/root/kani-fix-3300-sel1-replay-w15`, local branch `ci/kani3300-sel1-replay-w15`. Original recipe clone/HEAD were left unchanged. Author and committer: Tiramisu-Cake <igkharin@gmail.com>, through git -c.

`ci-overlay-delta.patch` is a Git-apply delta against that exact recipe, not a full Kani source patch. Its checksum is in `ci-overlay-delta.patch.sha256`; seven destination files are in `full-export/`. It replaces the old C1 binding/patch with `sel1-source-binding.json`/`sel1-test-only.patch`. The committed overlay changes only `.github/workflows/kani3300-replay.yml` and `scripts/kani3300-replay/`.

Kani is bound to `ec85b782a1b7156ad434cfac25403acd4e326dc1`, tree `0c9e5e67ba0a17128f71af415644f3fad84099d3`. This tests-only followup corrects four volatile-read golden spellings and one unused-field lint; production is byte-identical to priorb6f1b08eb5. See ../followup-43609527860/RESULT.md. Quick43609527860 reported fmt/build/clippy PASS and24/29 select controls ok with5 fixture failures; new native/replay outcomes remain NOT_RUN.

Std stays at frozen `70ba5befc617627073738e26cb1466bd4fb76e41`; the embedded full test-only patch reproduces overlay `6075e7ce17179f45642c9ffe8fe09e3ec9395726`, library tree `12e87bd4a4e141a8f829d8a0519efc09260c5059`. The wrapper checks the exact base/patch and all five changed-file hashes. It retains run4's URL `https://github.com/Tiramisu-Cake/verify-rust-std.git`, string URL argument, `--destination "$RUNNER_TEMP/kani3300-std"` and `git submodule update --init --depth 1`.

Six ON rows exactly preserve the issued SEL1 CI-REQUEST roots: sort4-closure, swap-if-less-closure, raw legal/negative sort4, and both merge closure regressions. `sort4-closure-on` now expects SUCCESS,0 failed checks and useful assertions/covers. Raw-negative requires the intended source[1] uninitialized u64 read; the runner preserves its nonzero child exit and never auto-credits an arbitrary negative. Receipts stay UNKNOWN until source/body/property review, including exit0 cases. All actual replay outcomes remain NOT_RUN.

The push trigger names only `ci/kani3300-sel1-replay-w15`, with existing Tiramisu-Cake/kani repository guard. Matrix max-parallel1, Kani jobs1, six invocations, no retries. Per-row60min job and2400s child caps are inherited; six serial jobs give a proposed360min envelope. This package does not publish or start the workflow. Python service preflight runs before source checkout/build. Setup failure produces a NOT_RUN fallback receipt, and complete/partial child receipts preserve original exits, timeout/signal, RSS and artifacts.

Local validation only:

- 29 Python service tests pass; prior20 controls retained with inventory/cap adaptations.
- 7 generator Python tests pass: exact roundtrip, mismatched patch/checksum/export, missing/extra export, wrong base tree; original recipe HEAD/status preserved.
- `make-ci-delta.py` and `make-ci-delta.py --check` reconstruct from immutable0c1 objects, reverse/check/apply in temporary Git, then compare every output byte against full-export. `--check` does not overwrite the patch/checksum.
- Candidate reverse-apply check, exact six-root comparison, CI-only path inventory and git diff --check pass.

Commands (Python/Git only):

```sh
python3 make-ci-delta.py --repo /root/kani-fix-3300-replay-c1-w15 --check
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q test_make_ci_delta.py
```

Run service tests from `full-export/scripts/kani3300-replay/` or the candidate's corresponding directory with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_replay.py`.

`REPLAY-CI-OVERLAY.json` binds request/source/std/workflow/file identities; `VALIDATION.json` records static/Python checks. `independent-review.md` is the prior static review; ../followup-43605855700/independent-review.md binds the current source/replay delta. The delta's runtime builds/verification and binary hashes remain NOT_RUN/pending. No local builds, Kani/rustc/CBMC/Miri, source push, CI dispatch or Cloud execution took place. Research here remains uncommitted for the owner; no production tool/std changes were made.

Latest binding/static validation: ../followup-43609527860/VALIDATION.json. Prior independent reviews apply to unchanged production/runner semantics; this delta only adjusts test fixtures and pins.
