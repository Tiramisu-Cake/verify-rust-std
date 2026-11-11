# KANI3300 U1T — PRE-BUILD

Статус: пакет подготовлен; все native результаты **NOT_RUN**. Dispatch только после GO координатора для exact published SHA.
Runtime Codex; одна стадия `kani3300-u1t`, stable owner `k1-merge`, slug `kani3300`.
Assigned task: `research/challenge-8/kani-k1/TASK-KANI3300-U1T.md`; окно main 240 + closeout 30 минут сохраняется.

## Identities

- Research branch `experiment/kani-k1-kani3300u1t-20261111`, input HEAD `fe350690cbc6bb917ea187f03e6d24649f42f51e` (task поверх U1R `0bc1a0e8d4`).
- Tooling base `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`; lane/toolchain/pin files unchanged.
- Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; author clone `/root/kani-fix-3300`, branch `fix/kani-3300`.
- Tests-only local Kani commit `647109cf6342474d899aa463315a37dac14fd831`, parent `546bcf30379b9b2894f94b1305d5277cc5b4574c`; no Kani remote push.
- Combined patch `kani-uninit-tests.patch`, SHA-256 `37689b6c615b6c8e4f321113f07c6c8d124cdf2aa30ff94eeda909a6ba18a1e6`.
- Request `kani3300-u1t-native-20261111-01`, SHA-256 `f0e8f7ca4082f69108ded989780eefe69ff89b4d4c6941427b1b07a38be2768b`.
- Fresh pin + patch index tree `0e16a12fd4ce531e03c121c1160243426a51f49e` = local Kani commit tree.

## Production equality and static checks

U1 patch SHA-256 `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467` preserved.
The production diff sections (every section outside `tests/`) are byte-for-byte identical to U1;
SHA-256 of that concatenation is `c529f960ae6ae8cc1287d0006b20c30885df5208a33da9c4bed571984fce5b1d`.
Production remains 7 files, +548/−150. All original U1 test/golden files are unchanged.
Local Kani delta adds only 14 fixture files, +242 lines; no existing controls/checks removed or weakened.
Tests-only addition does not require a new semantic review under CORE. Coordinator PRE-BUILD review/GO remains mandatory.

PASS: existing `kani_k1.py validate`, existing `prepare-kani` (SHA validation, fresh exact pin, `git apply --check --index`,
apply/index tree and companion files), `git diff --cached --check` on the applied tree, wrapper `rustfmt --edition 2021 --check`
on all seven new sources, source flags/golden harness/type/count checks, exact tooling equality.
Five original single-harness candidates retain their code modulo rustfmt whitespace/trailing commas; overlap is split below.
No local cargo/rustc/Kani/CBMC, Cloud builds, Actions, PRs, issues, raw evidence, U2 or reviewer clone access performed.

## Selectors and paired controls

All paths below are relative to `tests/expected/uninit/`, with suffix `/main.rs`.
Every negative has `expect: pass`, `require_success: false`, and its concrete diagnostic in the request and golden.
Each golden binds FAILURE and the uninit type to the named harness safety property, plus FAILED and the exact harness totals.
Overlap requires both distinct harness properties; a failure in just one direction cannot satisfy its golden.
All positives have `require_success: true`, no negative diagnostic, and a golden requiring all their harnesses to succeed.

| Negative fixture suffix after `maybe-uninit-review-` | Expected uninit type / negative harness | Positive harness in `maybe-uninit-review-positive` |
|---|---|---|
| `overwrite-copy` | `[u8; 2]` / `overwrite_copy` | `overwrite_copy_written_byte`: same partial copy, read initialized first byte |
| `overlap-copy` | `u8` / `overlap_copy_right`, `overlap_copy_left` | `overlap_copy_right_written_slot`, `overlap_copy_left_written_slot`: same mixed slots and memmove, read initialized destination slot 1 |
| `repeat-local` | `u64` / `repeat_local` | `repeat_local_initialized_source`: same raw write/repeat/last-slot read with initialized source |
| `reset-zst` | `u64` / `reset_after_zst` | `reset_after_zst_then_initialize`: same ZST prefix and raw reset, rewrite payload before reading |
| `padded-manually-drop` | `Padded` / `incomplete_padded_transmute` | `complete_padded_transmute`: initialize both fields, leave padding uninitialized, same ManuallyDrop transmute |
| `argument-return` | `u16` / `argument_return` | `argument_return_both_initialized`: same non-inlined select/return with both arguments initialized and nondeterministic branch |

No candidate expectation was changed. Original overlap's nondeterministic directions became separate harnesses so both refusals are checked.
The positive fixture requires 7/7 successful harnesses. With 8+1 original positive and 3 original negative regression harnesses,
the request contains 12 selectors / 26 harnesses (16 positive, 10 negative).
Regression selectors: `maybe-uninit-initialized` and `maybe-uninit-scratch-array` are mandatory positives;
`maybe-uninit-partial-copy` checks partial-byte transfer, `maybe-uninit-reset-alias` checks alias reset plus call/transmute,
and `maybe-uninit-volatile-read` keeps a distinct raw intrinsic read control.

## Budget and acceptance

`kind: kani-tests`, `runner: gcb-e2-standard-4`, `harnesses: []`, native job 5 minutes, selector timeout 150 seconds.
Reservation `(5 + 30) × $0.0135 = $0.4725` ≤ stage cap $0.50; paid builds so far $0, no dispatch performed.
Selector timeout remains U1's 150 s; whole-job 300 s bounds the run. Prior U1 reported 17 s native work; this is planning context only.
Project cap $6.40 and shared owner/slot/ledger limits must be checked through the existing coordinator before dispatch;
this packet neither registers a phase nor grants GO. No repair without observed failure, remaining cap, and a new GO.
After authorized build: fresh tree identity, all native selectors PASS, each negative's own uninit output and both overlap properties,
all positive Kani exits successful, no timeout/ignored. Inspect bounded `k1g.sh summary/native`; preserve integrity vs proof distinctions.
A negative SUCCESS is a correctness blocker: retain minimal case and production file:line, then `Координатор, вопрос`; no production edit.
A false positive is reported without changing production. Await exact-packet coordinator GO; after any future dispatch use `k1g.sh watch BUILD` and end turn.
