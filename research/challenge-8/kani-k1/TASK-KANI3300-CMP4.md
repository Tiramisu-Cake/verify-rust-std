# KANI3300 CMP4 — дифференциальная проверка ложного uninit `IndexRange::zero_to(2).len()`: чистый f046 vs CMP2, const vs runtime

**Выдано координатором 2026-11-11, ночной GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-AFTER-CMP3-ANSWER.md`, п.3–6).** Диагностика,
не исправление. Runtime **Codex**, одна стадия. Каждая сборка — после exact-packet PRE-BUILD review/GO координатора.

## Контекст

CMP3 (`kani3300/cmp3/RESULT-KANI3300-CMP3.md` в этой ветке, build ddcd43e2, production CMP2): шаг 1 `IndexRange::zero_to(2).len()`
FAILED (uninit `usize` @ core ops/index_range.rs:57), шаг 4 (ManuallyDrop→deref→unsize→len) и into_iter/next, U8 — SUCCESS.
Гипотеза (не установлена): ordinary-локал получает значение из MIR-константы без typed shadow seed (CMP2 умеет
constant_init_mask → SetStorage только для storage-форм).

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-cmp4**, ветка **experiment/kani-k1-kani3300cmp4-20261111** от CMP3 `5e8bf28b11`
  (KT2 tooling `3bb5445d2a`). Library — только `verify/uninit_probe.rs` и `#[cfg(kani)]` адаптеры `array/iter/iter_inner.rs`
  (как в CMP3); настоящие методы/видимость не менять.
- Две сборки `kind: diagnostic`, `uninit_checks: true`, controls on, inventory off, standard4/jobs1, `--harness-timeout 3m`:
  **(clean)** без `kani_patch` (чистый f046); **(cmp2)** `kani_patch` = production CMP2 `kani3300/u4/kani-uninit.patch`
  (sha `46ad585f…`, без изменений). Одинаковые roots и library в обеих.
- Stage `kani3300-cmp4`, owner **k1-merge**, requests `kani3300-cmp4-clean-*`, `kani3300-cmp4-cmp2-*`. Cap **$1.20** на стадию
  (2 × (4×3+30)=42 мин ⇒ резерв 2 × $0.567). Без повторов.

## Roots (одинаковые в обеих сборках)

1. `cmp3_index_range_len` (как в CMP3: `zero_to(2).len()`);
2. **новый** runtime-вариант: `n = kani::any_where(|n| *n <= 4)`, `IndexRange::zero_to(n).len() == n` (тот же assert/cover);
3. `cmp3_manually_drop_unsized_len` (проходящий шаг 4);
4. U1 `pincheck_calibration_uninit_read_u8` (FAILED на uninit).
Без pre-len raw-read/AddressOf. Если доступно без новых инструментов — указать в RESULT, чем различаются присваивания в MIR
(константа vs вызов) по исходнику/rustc-семантике; иначе UNKNOWN.

## RESULT

**RESULT-KANI3300-CMP4.md** в `kani3300/cmp4/` (≤ 25 строк): таблица root × {clean, cmp2} (status, failed/total, covers,
Failed Checks с локацией через KT2/native-field); вывод по правилам п.5 планера (существовало до CMP2 / регрессия CMP2 /
неразрешено); const vs runtime; расход; предложение следующего шага (узкий фикс constant-assign по п.6 планера или иное).

## Коммиты, ожидание, запреты

- Library-коммит отдельно от research, все `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force,
  без `git stash`. rustfmt через обёртку `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh
  --edition 2024 --config-path research/challenge-8/kani-k1/codefix/rustfmt.toml`.
- Для каждой сборки — свой пакет и `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, конец хода.
- Evidence — bounded `k1g.sh summary/native/native-field/rows`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC. Никаких Actions/PR/issue.
- Это верификация корректности стандартной библиотеки Rust инструментом Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 CMP4 ЗАВЕРШЁН**, одна стадия, затем стоп.
