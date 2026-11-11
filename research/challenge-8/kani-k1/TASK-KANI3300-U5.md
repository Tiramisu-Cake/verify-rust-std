# KANI3300 U5 — core replay u64/N4 через реальный `StableSmallSortTypeImpl::small_sort` под uninit-checks

**Выдано координатором 2026-11-11, ночной GO владельца; состав — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-AFTER-U4B-ANSWER.md`, п.3–5 — прочитать).**
Диагностика, research-ветка. Runtime **Codex**, одна стадия. Dispatch только после exact-packet PRE-BUILD review/GO координатора.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u5**, ветка **experiment/kani-k1-kani3300u5-20261111** от U4B `6931d0d24b`
  (KT2 tooling `3bb5445d2a`; `kani_patch` = `kani3300/u4/kani-uninit.patch`, sha `46ad585f…`, production CMP2 — **без изменений**).
- Library: только добавить roots в `verify/uninit_probe.rs` (существующие 11 не менять). Core (`smallsort.rs` и др.) не менять.
- Stage `kani3300-u5`, owner **k1-merge**, request `kani3300-u5-*`. Cap **$0.80**: одна сборка `kind: diagnostic`,
  `uninit_checks: true`, controls on, inventory off, standard4/jobs1, `--harness-timeout 3m`; 5 roots (резерв $0.6075) или 6
  с опциональным B6 ($0.648). Без повторов.

## Roots

- **B1** `<u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut less_u64)`, N4, `scratch =
  [MaybeUninit::<u64>::uninit(); 20]`, `less_u64` — function item строгого `<` (без приведения к fn pointer); тот же panic stub;
  проверить sortedness, count по произвольному probe, нормальный возврат; затем прочитать **только** `scratch[3]`
  (`assume_init_read`), covers до/после → SUCCESS, без uninit/Unsupported/посторонних отказов.
- **B2** тот же Stable-entry/N4, отдельный root: после возврата читать **только** `scratch[4]` → ожидается uninit u64
  (`expect_check: Reading from an uninitialized`); число и типы отказов зафиксировать, pointer-отказ классифицировать отдельно.
- **B3** U8 `small_sort_general_with_scratch_u8_n4` (SUCCESS), **B4** U1 (uninit FAILED), **B5** U2 (SUCCESS) — без изменений.
- Опц. **B6**: `MaybeUninit<u64>` с записанным одним байтом, чтение всего u64 → uninit FAILED (mask-control).
Сверить по исходнику, что Stable-entry для u64 (Freeze) идёт в general scratch-путь и пишет scratch[0..4], не трогая scratch[4].

## RESULT

**RESULT-KANI3300-U5.md** в `kani3300/u5/` (≤ 25 строк): таблица (status, failed/total, covers, Failed Checks с локацией);
формулировка достигнутого в стиле п.1 планера (scope, caveats); расход.

## Коммиты, ожидание, запреты

- Library-коммит отдельно от research, все `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force,
  без `git stash`. rustfmt через обёртку `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh
  --edition 2024 --config-path research/challenge-8/kani-k1/codefix/rustfmt.toml`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/rows`; raw logs, archives, credentials не читать. Никаких локальных cargo/rustc/Kani/CBMC.
- Это верификация корректности стандартной библиотеки Rust инструментом Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U5 ЗАВЕРШЁН**, одна стадия, затем стоп.
