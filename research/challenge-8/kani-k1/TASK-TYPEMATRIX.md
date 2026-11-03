# TYPEMATRIX — фаза B4: safety dispatch на типах (u8, u32), u128, [u8; 9]

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-typematrix**, ветка **experiment/kani-k1-typematrix-20261103** от
  **e8e238db9d87323fa4da011a1a8b37fb76ec91c0** (v6 library tree + K-1 tooling + cap 93.96).
- Slug **typematrix**, stable owner **k1-merge**. Новые stage/ledger/UUID/request_id `typematrix-*`.
- Project cap **$93.96**, свой cap **$1.80**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Окно: main 150 + closeout 30 мин.

## Контекст

Dispatch-safety уже есть для (), u8, u64, [u8; 16], [u8; 17], [u8; 85], DropValue, Cell. Маршрут по `smallsort.rs`:
- stable, Freeze → `small_sort_general_with_scratch`;
- unstable, Freeze + Copy:
  - `size_of ≤ 8` (`has_efficient_in_place_swap`) → `small_sort_network`;
  - иначе `size_of × 48 ≤ 4096` → `small_sort_general`.

Аудит просил закрыть матрицу типов: другой размер элемента, выравнивание, padding. Только safety. Перестановку для
типа с padding не заявляем.

| Тип | size / align | unstable | Что нового |
|---|---|---|---|
| `(u8, u32)` | 8 / 4, padding 3 байта | network | padding в копиях network и general |
| `u128` | 16 / 16 | general | выравнивание 16, scratch на стеке |
| `[u8; 9]` | 9 / 1 | general | первая длина, где `has_efficient_in_place_swap` ложно |
| `u16` | 2 / 2 | network | только ширина элемента — **отложен**, в пакет не входит |

Первым шагом PRE-BUILD подтвердить эту таблицу по source (size/align, выбранная ветка). В модуле — target-specific
const assertions на size/align; layout `repr(Rust)` не выдавать за гарантию языка.

## Source scope

Новый opt-in child `network::typematrix` в файле `verify/network/typematrix.rs`. В `network.rs` добавить только
`#[cfg(kani_smallsort_controls)] mod typematrix;`. Существующие roots, макросы и компараторы не менять.

Использовать существующие `dispatch_safety_cases!` и `dispatch_pair_safety_cases!` (или копию смысла, если
видимость макроса не позволяет — тогда semantic diff в PRE-BUILD). Тот же компаратор `volatile_reading_less`, тот же
stub, unwind 65, scratch 48. Semantic diff — те же реальные entry calls, без summaries и дополнительных assumptions.
`ArbitraryValue`:
- для `(u8, u32)` и `u128` — полный `kani::any()` по значениям/полям, без обнуления и проверки padding;
- для `[u8; 9]` новый impl не нужен: есть `impl<const M: usize> ArbitraryValue for [u8; M]`.

Берём именно кортеж `(u8, u32)`: явное поле-padding не заменяет неинициализированный padding.

**Состав зафиксирован, ровно 10 roots:**
- для каждого из `(u8, u32)`, `u128`, `[u8; 9]` — три stable+unstable pair-группы: {0,1,2,7,8}, {15,16,17}, {31,32}
  (9 roots);
- плюс `(u8, u32)` unstable {9,12,13,18} (1 root).

Объединённые группы могут дать TIMEOUT; пригодность для CI не обещаем. Автоматическое дробление после результата
запрещено. Exact names и covers заморозить в PRE-BUILD.

Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta;
- rustfmt;
- без warnings.

## Пакет

10 строк, measurement, expect SUCCESS:
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (10×10+30)×$0.0135 = **$1.755**.

Project ≤ 2 unfinished, ≤ 1 на k1-merge. Параллельно может идти CELLSPLIT G3 (k1-network).

PRE-BUILD содержит:
- таблицу маршрутов по source;
- список roots × длины;
- semantic diff против исходного макроса, если копировали;
- hashes, budget.

Коммиты library/research отдельно, `[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в
фоне.

## Gate и RESULT

**Gate root.** SUCCESS, 0 failures, все объявленные route × length covers. Scope — default checks на путях
нормального возврата; не доказывает uninit/validity и байтовую перестановку. TIMEOUT/FAILED — bounded facts, без retry и split. Для FAILED —
bounded `k1g.sh log-grep`. Настоящий counterexample — немедленно мне.

**RESULT-TYPEMATRIX.md**, ≤ 30 строк:
- таблица строк: status, VT, checks, unreachable, covers, CBMC RSS;
- какие клетки «тип × маршрут × длины» закрыты;
- кандидаты в v7 (≤ 300 с GCB, затем полный fork-CI).

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **TYPEMATRIX ЗАВЕРШЁН**, одна стадия, затем стоп.
