# KANI3300 CMP3 — пошаговая локализация ложного uninit `IndexRange::len` на пути `[usize;2].into_iter()` в core

**Выдано координатором 2026-11-11, ночной GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-CMP3-ANSWER.md`, п.1–9 — прочитать целиком,
они обязательны).** Диагностика, не исправление. Runtime **Codex**, одна стадия. Dispatch только после exact-packet
PRE-BUILD review/GO координатора.

## Контекст

CMP1/CMP2 (`/root/verify-rust-std-kani3300-cmp`, `kani3300/cmp1|cmp2/RESULT-*.md`): на патче compound storage positive
IntoIter падают на `IndexRange::len.safety_check.1/.2` («uninitialized `usize`» @ core ops/index_range.rs:52:51/:52:61);
минимальные repro вне core проходят. Нужна точка на реальном пути.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-cmp3**, ветка **experiment/kani-k1-kani3300cmp3-20261111** от U4 `e1ed2374b7`
  (KT2 tooling `3bb5445d2a`; production-only `kani3300/u4/kani-uninit.patch` sha `46ad585f…` = production CMP2 — переиспользовать
  как `kani_patch` без изменений; пин/toolchain не менять).
- Library-изменения **только**: (а) `verify/uninit_probe.rs` — новые roots (8 harness U0/U2 не менять); (б) минимальные
  `#[cfg(kani)]` диагностические адаптеры в `library/core/src/array/iter/iter_inner.rs` (и при необходимости одна строка
  crate-visible re-export в `array/iter.rs`/`array/mod.rs` под `#[cfg(kani)]`), без изменения настоящих методов, их видимости
  и типов (п.2 планера). `kani_smallsort_controls` вне SmallSort-файлов не использовать.
- Slug **kani3300**, stage `kani3300-cmp3`, owner **k1-merge**, request `kani3300-cmp3-*`. Cap **$0.80**: одна сборка
  `kind: diagnostic`, `uninit_checks: true`, controls on, inventory off, standard4/jobs1, `--harness-timeout 3m`, 9 roots
  (9×3+30 = 57 мин, резерв $0.7695). Без повторов.

## Roots (п.3–5 планера)

1. `IndexRange::zero_to(2)` → `.len()` == 2;
2. `PolymorphicIter::new_unchecked(IndexRange::zero_to(2), [MaybeUninit::new(a), MaybeUninit::new(b)])` → штатный `len()` (sized);
3. то же через unsize в `&PolymorphicIter<[MaybeUninit<usize>]>` → `len()`;
4. `ManuallyDrop::new(PolymorphicIter)` → deref → unsize → `len()` (как `IntoIter::unsize`);
5. `IntoIterator::into_iter([a, b])` → `len()` == 2;
6. `into_iter([a, b])` → `next()==Some(a)`, `next()==Some(b)`, `next()==None`;
7. U8 `small_sort_general_with_scratch_u8_n4` (интеграционный probe);
8. U1 `pincheck_calibration_uninit_read_u8` (FAILED на uninit), 9. U2 `pincheck_calibration_init_read_u8` (SUCCESS).
Данные полностью инициализированы, cover после целевой операции; ошибки Drop отделять от len. Без «проверочных» raw-read/
AddressOf перед len (п.8).

## RESULT

**RESULT-KANI3300-CMP3.md** в `kani3300/cmp3/` (≤ 30 строк): таблица 9 roots (status, failed/total, covers, Failed Checks
дословно с локацией из KT2/native-field, omitted count); первый провальный шаг; что это локализует и что нет (п.6–7);
данные для связки transfer/delayed get, если есть, иначе причина UNKNOWN; предложение следующего шага (исправление или
немутирующая трассировка, п.8). Расход.

## Коммиты, ожидание, запреты

- Library-коммит отдельно от research, все `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force,
  без `git stash`. rustfmt через обёртку `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh
  --edition 2024 --config-path research/challenge-8/kani-k1/codefix/rustfmt.toml`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native/native-field/rows`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC. Никаких Actions/PR/issue.
- Это верификация корректности стандартной библиотеки Rust инструментом Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 CMP3 ЗАВЕРШЁН**, одна стадия, затем стоп.
