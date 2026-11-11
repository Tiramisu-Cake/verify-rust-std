# RESULT-KANI3300-U3 — U1T amendment
BLOCKED_MISSING_DIAGNOSTIC_BINDING: пункты 1–2 выполнены, источники пунктов 3–4 не установлены; вопрос координатору.
Пакет 52cd0b12353076194296d74d2f59808ace90aceb НЕ диспатчить; native NOT_RUN, приёмка открыта.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; candidate `3fd6f408e1d565ba65aaeb86c0c4ad0bbc57ab52`.
Patch SHA-256 `f9187933ecd69858ae03762baa8dd57f5907e456e7457db7cba73092471ae111`; request SHA-256 `8cda1fa64a8b1c7dfce56c44f30fd5d84bce508e9d93cf03a426e188f9c912da`.
Tooling c98d7cee0d509b1633ab61c9a1ae989e286c8e2a и production reviewed candidate 8bfb7c7 — без изменений.
(a)/(b): прежние exact typed masks/padding=false, source checks, ghost buffer и numeric return transfer.
Full IntoIter NOT_RUN: ожидается Unsupported union-as-field; следующее реальное препятствие UNKNOWN.
U1T amendment: 5 Kani FAILED по координатору; golden mismatch установлен, отказ нужных uninit properties ещё не доказан.
5 goldens требуют Failed Checks: uninit + FAILED + failed Complete; типы T прежние, все 7 Rust sources U1T неизменны.
Overlap: механизм текста — library/std/src/lib.rs:218–244, invocation/cause UNKNOWN; shadow-copy не содержит unreachable!.
Overwrite: foreign function(1) — агрегат, конкретный callee/callsite/reachability UNKNOWN; недостижимость не заявлена.
Вопрос: bounded property status/source_location обеих overlap harness и foreign symbol/callsite overwrite.
Детали: U1T-DIAGNOSTICS-AMEND.md; без source binding production fix по догадке не внесён.
v2−U1: production 2 files +111/−13, tests с U1T 36 files +631/−0; delta от review — 5 goldens +13/−18.
Статика PASS: validate20, fresh apply/tree, diff-check, allowlist; все36 Rust blobs прежние (предыдущий rustfmt PASS).
Все selectors ниже NOT_RUN; префикс uninit/, суффикс /main.rs. Показаны только ожидания.
| Selector | Ожидание |
|---|---|
| maybe-uninit-wrap-u3-positive | 6 SUCCESS: scalar/array Copy, zero/ZST, padded Move/array |
| maybe-uninit-wrap-u3-padding | FAILURE/uninit u8 padding |
| maybe-uninit-wrap-u3-source-read | FAILURE/uninit u64 typed source |
| maybe-uninit-wrap-u3-intoiter | FAILURE/Unsupported union-as-field |
| maybe-uninit-buffer-u3-positive | 4 SUCCESS: plain/PFC, clauses, nested/2 args/return0/stale |
| maybe-uninit-buffer-u3-plain-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-pfc-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-clause-plain-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-clause-pfc-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-frame-negative | FAILURE/Check that *outside is assignable |
| maybe-uninit-buffer-u3-no-mir-unsupported | FAILURE/Unsupported shadow-carrying args without MIR |
| maybe-uninit-review-positive | 7 SUCCESS, обе overlap positive сохранены |
| maybe-uninit-review-argument-return | Failed Checks: uninit u16 |
| maybe-uninit-review-overwrite-copy | Failed Checks: uninit [u8;2] |
| maybe-uninit-review-overlap-copy | 2 failed harnesses + Failed Checks: uninit u8 |
| maybe-uninit-review-repeat-local | Failed Checks: uninit u64 |
| maybe-uninit-review-reset-zst | Failed Checks: uninit u64 |
| maybe-uninit-assume-init | FAILURE/uninit u8 |
| maybe-uninit-partial-copy | FAILURE/uninit [u8;4] |
| maybe-uninit-reset-alias | FAILURE/uninit u8 |
U1T NOT_RUN вне manifest: maybe-uninit-review-padded-manually-drop; остальные U1 NOT_RUN — NOT-RUN.json.
Расход $0, reservation нет; proposed $0.540 / cap $0.90; 20 selectors, job10min/selector150s, repair с новым GO.
Следом: снять diagnostic blocker, новый GO; после native PASS review, затем отдельный replay U1/U2,U6,U7–U9.
Следующий scope: compound storage fields U8/U9, select_unpredictable с alias/init controls; credit нет.
