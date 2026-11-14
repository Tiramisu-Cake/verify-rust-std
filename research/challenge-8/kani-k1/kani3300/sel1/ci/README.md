# SEL1 six-row replay CI overlay

Preparation only. Local candidate `c9619b15022fb43f1e961e01695e64875ad68fe9`, tree `e17787b7ef41250e8e55bb90e2fc7f5d254943ba`, sole parent Gate B′ recipe `0c1cc8a7d05184044d496b01f5ed41cebfde0cac` (tree `cbb04807c711a9d1bad2ac2dbe1f77538d5658b0`). Clone `/root/kani-fix-3300-sel1-replay-w15`, local branch `ci/kani3300-sel1-replay-w15`. Original recipe clone/HEAD were left unchanged. Author and committer: Tiramisu-Cake <igkharin@gmail.com>, through git -c.

`ci-overlay-delta.patch` is a Git-apply delta against that exact recipe, not a full Kani source patch. Its checksum is in `ci-overlay-delta.patch.sha256`; seven destination files are in `full-export/`. It replaces the old C1 binding/patch with `sel1-source-binding.json`/`sel1-test-only.patch`. The committed overlay changes only `.github/workflows/kani3300-replay.yml` and `scripts/kani3300-replay/`.

Kani is bound to `46e46583ff112cae9c43aea1ba5dd6145e5e8387`, tree `0a46fad6c1adc3022d39e25a45096ed9cd622844`. The workflow separately checks out/builds this exact clean export. The CI recipe's own historical compiler tree is not the tool being built. The owner's quick run43605855700 was reported started; no status was queried here and no quick acceptance is inferred.

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

`REPLAY-CI-OVERLAY.json` binds request/source/std/workflow/file identities; `VALIDATION.json` records static/Python checks. `independent-review.md` is the independent static correctness review. The delta's runtime builds/verification and binary hashes remain NOT_RUN/pending. No local builds, Kani/rustc/CBMC/Miri, source push, CI dispatch or Cloud execution took place. Research here remains uncommitted for the owner; no production tool/std changes were made.
