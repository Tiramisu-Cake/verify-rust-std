# KANI3300 U4B — разделение U9: чтение записанного scratch[3] и незаписанного scratch[4] отдельными harness

**Выдано координатором 2026-11-11, ночной GO владельца.** Диагностика. Runtime **Codex**, одна стадия. Dispatch только после
exact-packet PRE-BUILD review/GO координатора.

## Контекст

U4 (`kani3300/u4/RESULT-KANI3300-U4.md`, build 6a2c009d, production CMP2 `46ad585f…`): U8 SUCCESS 0/550; U9 — 2 отказа
(`*const u8` и `u8`, оба @ core ptr/mod.rs:1769, `ptr::read`), covers 6/6; нельзя различить, не падает ли чтение
записанного `scratch[3]`.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u4**, ветка **experiment/kani-k1-kani3300u4-20261111** (head `ee79e37c0f`);
  KT2 tooling, `kani_patch` = тот же `kani3300/u4/kani-uninit.patch` (sha `46ad585f…`) без изменений.
- Library: только **добавить** в `verify/uninit_probe.rs` два harness (существующие 9 не менять), та же геометрия, что U9
  (N4, `[MaybeUninit::<u8>::uninit(); 20]`, `strict_less`, тот же panic stub, unwind 17):
  - **U9a** `small_sort_general_scratch_written_slot_u8_n4`: после реального sort — только наблюдаемое
    `assume_init_read` `scratch[3]` (+ covers) → ожидание **SUCCESS**;
  - **U9b** `small_sort_general_scratch_unwritten_slot_only_u8_n4`: только `assume_init_read` `scratch[4]` → ожидание FAILED
    на uninit (`expect_check: Reading from an uninitialized`); записать число отказов и их типы.
- Stage `kani3300-u4b`, owner **k1-merge**, request `kani3300-u4b-*`. Cap **$0.60**: одна сборка `kind: diagnostic`,
  `uninit_checks: true`, controls on, inventory off, standard4/jobs1, `--harness-timeout 3m`, roots: U9a, U9b, U8, U1
  (4×3+30 = 42 мин, резерв $0.567 ≤ cap;
  без повторов).

## RESULT

**RESULT-KANI3300-U4B.md** в `kani3300/u4b/` (≤ 20 строк): таблица (status, failed/total, covers, Failed Checks с локацией);
вывод: U9a SUCCESS ⇒ записанный слот не даёт ложного отказа, оба отказа U9 — от чтения scratch[4] (две точки
инструментирования); иначе — описать. Расход.

## Коммиты, ожидание, запреты

- Library-коммит отдельно от research, все `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force,
  без `git stash`. rustfmt через обёртку `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh
  --edition 2024 --config-path research/challenge-8/kani-k1/codefix/rustfmt.toml`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/rows`; raw logs, archives, credentials не читать. Никаких локальных cargo/rustc/Kani/CBMC.
- Это верификация корректности стандартной библиотеки Rust инструментом Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U4B ЗАВЕРШЁН**, одна стадия, затем стоп.
