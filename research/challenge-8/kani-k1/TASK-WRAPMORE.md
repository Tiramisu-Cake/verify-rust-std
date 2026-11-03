# WRAPMORE — контракты-обёртки на двух непокрытых реализациях и на N4 (фаза D1)

**Выдано координатором 2026-11-03; каждый dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-wrapmore**, ветка **experiment/kani-k1-wrapmore-20261103** от
  **2104e7a596fabb058a99c8bcdf0e3f487d9a7753** (v6 library tree d4ec476a7a + K-1 tooling).
- Slug **wrapmore**, stable owner **k1-merge**. Сборки только после terminal/accounting PERMSOLVER (тот же owner).
  Новые stage/ledger/UUID/request_id `wrapmore-*`.
- Project cap **$88.96** (свободно мало), свой cap **$1.95**. Два плановых Build (G1, G2), retry нет. Один
  compile-error repair на стадию — только если own spent + reserve ≤ cap **и** project остаётся ≤ cap; иначе стоп.
- Окно: main 180 мин + closeout 30 мин.

## Контекст: что уже есть

В v6 `verify/wrap.rs` (ordinary) — три `cfg(kani)`-обёртки N2 с контрактами. Их PFC проходят на real body без stubs:

| Обёртка | Реализация (trait → impl) | Маршрут при N2 |
|---|---|---|
| `stable_cell` | `StableSmallSortTypeImpl` blanket (`default fn`, `Cell<u8>`) | insertion |
| `unstable_byte` | `UnstableSmallSortTypeImpl` Freeze → `UnstableSmallSortFreezeTypeImpl` Copy (`u8`) | network |
| `freeze_noncopy` | `UnstableSmallSortFreezeTypeImpl` default (`NonCopyU8`) | general |

Форма контракта:
- `requires`: регион, канонический fn-pointer компаратора;
- `modifies` региона;
- `ensures`: sorted по модели и `old(count) == count` с независимой by-value пробой u8;
- canonical guard;
- input frame в PFC;
- covers входов.

Компараторы чистые (сравнивают старшие 7 бит), модель — полный байт. Перестановка значений корректна, потому что
компаратор не мутирует. Для `Cell` это частный чистый domain, а не произвольный FnMut.

**Не покрыты две из шести реализаций:**
- `StableSmallSortTypeImpl` для `T: FreezeMarker` → `small_sort_general_with_scratch`;
- `UnstableSmallSortTypeImpl` blanket (`default fn`, не-Freeze `Cell<u8>`) → `small_sort_fallback`.

Все контракты только при N2.

## Цель

1. **G1 — две новые обёртки N2 в той же форме:**
   - **`stable_freeze_byte`**: `u8` через `<u8 as StableSmallSortTypeImpl>::small_sort(v, scratch, ...)`, Freeze →
     general with scratch. В requires — регион входа и scratch, длиной не меньше требуемой маршрутом
     (`len + 16`; проверить по source). Disjointness как в `stable_region`. `modifies` — вход **и** scratch. Ensures —
     sorted + count по входу.
   - **`unstable_cell`**: `Cell<u8>` через `<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort` → fallback. Чистый
     canonical `cell_less`.
   - **Плюс opt-in control** `rejects_always_true_more`: два nondeterministic branch для новых обёрток, единственный
     failure — существующий literal `wrap canonical comparator required`. Существующий `rejects_always_true` не менять.
2. **G2 — N4 для всех пяти** (три старые и две новые): отдельные обёртки `*_n4` с регионом из 4 элементов, PFC с
   backing 6 (frame слева и справа), те же модели, компараторы и проба. Union длин не делать: только фиксированное N4.

Все новые элементы — **opt-in** (`#[cfg(kani_smallsort_controls)]`), в отдельном child-файле
`verify/wrap/more.rs`. В `wrap.rs` — только `#[cfg(kani_smallsort_controls)] mod more;`. Существующие обёртки,
helpers и PFC не менять. Если нужен общий helper (region для N), добавить его в child, а parent не трогать.
Visibility не расширять без обоснования.

Ordinary 202 / PFC 36 неизменны. Static delta по cfg-on/opt-in — проверить exact name-set.

## Требования к контрактам

- Спецификации не вызывают компаратор и не читают scratch или uninit (как в `wrap.rs`).
- `old()` — только скаляр count от пробы, как сейчас.
- Covers входов (reversed/increasing/tied/duplicate/probe hit/miss) — по образцу `input_covers`. Для N4 достаточно
  reversed, increasing, tie, duplicate и probe hit/miss на первой паре плюс «перестановка, требующая ≥ 2 перемещений».
- Frame: элементы backing вне региона неизменны; для stable_freeze — scratch вне `modifies` не проверяется, но в
  PREBUILD указать, что он `modifies`.
- Never stub; unwind — рассчитать по source и записать в PREBUILD (у N2 сейчас 16).

## Пакеты

| Пакет | Rows | Expect | Резерв |
|---|---|---|---|
| G1 | PFC `stable_freeze_byte_n2`, PFC `unstable_cell_n2`, control `rejects_always_true_more` | SUCCESS, SUCCESS, FAILED (literal `wrap canonical comparator required`) | (3×10+30)×$0.0135 = $0.810 |
| G2 | PFC N4 ×5 | SUCCESS каждая | (5×10+30)×$0.0135 = $1.080 |

Итого $1.89 ≤ cap $1.95.

Профиль measurement:
- gcb-e2-standard-4, controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10;
- Kani 9461e07a, tooling 30f77e85, check-tooling.

Порядок: PRE-BUILD G1 → GO → dispatch → wait. Затем PRE-BUILD G2 → GO → dispatch. G2 запускается при любом
proof-исходе G1, кроме общего compile-blocker. Перед каждым submit сверить project used + reserved + резерв ≤ $88.96.
Если не помещается — стоп и ко мне, cap не трогать.

PRE-BUILD каждого пакета содержит:
- semantic diff;
- таблицу контрактов: requires / modifies / ensures;
- маршрут каждой обёртки по source при данном N, с доказательством, что вызов попадает именно в целевую impl;
- covers и literal table, static delta, hashes, budget/slots.

Коммиты library/research отдельно, `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <sha>`, стоп до
GO. `k1g.sh wait BUILD` в фоне, завершить ход.

## Gate и RESULT

- **Gate PFC:** SUCCESS, 0 unintended failures, все covers.
- **Gate control:** только свой literal, covers до guard.
- TIMEOUT/OOM — факт строки, retry нет, N не уменьшать.

**RESULT-WRAPMORE.md**, ≤ 40 строк:
- матрица 6 реализаций × {N2, N4} — что доказано контрактом (с учётом старых трёх N2);
- VT и RSS;
- кандидаты в v7 (≤ 300 с);
- что остаётся без контракта и почему.

PASS — контракт обёртки на конкретных типах и N, а не контракт на самих методах (K5) и не generic T/F.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **WRAPMORE ЗАВЕРШЁН**, одна стадия, затем стоп.
