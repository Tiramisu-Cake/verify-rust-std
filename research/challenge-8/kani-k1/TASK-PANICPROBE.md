# PANICPROBE — фаза E1: что скрывает panic-stub и как `should_panic` работает на пине

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-panicprobe**, ветка **experiment/kani-k1-panicprobe-20261103** от
  **e8e238db9d87323fa4da011a1a8b37fb76ec91c0** (v6 library tree + K-1 tooling + cap 93.96).
- Slug **panicprobe**, stable owner **k1-network**. Новые stage/ledger/UUID/request_id `panicprobe-*`.
- Project cap **$93.96**, свой cap **$1.30**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Окно: main 150 + closeout 30 мин.

## Контекст

Safety-корни стабят `panic_on_ord_violation → assume_order_violation`, то есть отрезают пути, где компаратор не задаёт
порядок. Аудитор спрашивал, не прячет ли stub что-то кроме самой паники. Guard вызывается в `bidirectional_merge`
(`smallsort.rs` около 832), его вызывают:
- `small_sort_general_with_scratch` (около 286);
- `small_sort_network` при N ≥ 18 (около 368);
- `sort8_stable` (около 672).

Известно по коду пина: `#[kani::should_panic]` засчитывает успех, если все упавшие свойства — класса assertion. Поэтому
одного `should_panic` мало: нужен парный корень без него, чтобы увидеть, какие именно проверки падают.

## Source scope

Новый opt-in child `network::panicprobe`, файл `verify/network/panicprobe.rs`. В `network.rs` — только
`#[cfg(kani_smallsort_controls)] mod panicprobe;`. Существующие roots, stubs и компараторы не менять.

Ровно 6 roots, без `kani::stub`:

| # | Root | Тело | Ожидание |
|---|---|---|---|
| 1 | `panic_control_plain` | `should_panic`; `if kani::any() { panic!("panicprobe control") }` | SUCCESS |
| 2 | `panic_control_ub` | `should_panic`; две независимые ветки по `kani::any()`: явный `panic!` и raw OOB-read `u8` через указатель за границей локального массива, результат используется (не ZST, не volatile, не bounds-index) | FAILED: should_panic не принимает смесь panic + pointer-check |
| 3 | `panic_network_u8_n18_should_panic` | `should_panic`; `<u8 as UnstableSmallSortTypeImpl>::small_sort` на `[u8; 18]` из `kani::any()`, компаратор возвращает `kani::any()` без чтения памяти | SUCCESS |
| 4 | `panic_network_u8_n18_plain` | то же без `should_panic` | FAILED |
| 5 | `panic_general_u8_n16_should_panic` | `should_panic`; `<u8 as StableSmallSortTypeImpl>::small_sort` на `[u8; 16]`, scratch `[MaybeUninit<u8>; 48]`, тот же компаратор | SUCCESS |
| 6 | `panic_general_u8_n16_plain` | то же без `should_panic` | FAILED |

Unwind — как у dispatch-корней (65); сверить по source. У каждого root — cover нормального возврата, где он возможен.
Entry-cover не доказывает достижение guard. Свидетельство guard — однозначно атрибутированная упавшая проверка
plain-пары (4, 6). Если сообщение общее и атрибуции не хватает — итог UNKNOWN. Stub или инструментацию guard ради
cover не добавлять.

Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta (+6);
- rustfmt;
- без warnings.

## Пакет

6 строк, **kind diagnostic**, expect FAILED + expect_check там, где ожидается отказ. Frozen `_row_meets` требует
located failure, а terse location не даёт: тогда lane gate строки остаётся непринятым. Ожидание на SUCCESS не
подменять. Диагностическую классификацию ниже вести отдельно от автоматического gate.
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (6×10+30)×$0.0135 = **$1.215**.

Project ≤ 2 unfinished, ≤ 1 на k1-network. Параллельно может идти WRAPEIGHT (k1-merge).

PRE-BUILD: таблица roots с маршрутами по source (какие вызовы `bidirectional_merge` достижимы на N16 и N18), hashes,
budget. Коммиты library/research отдельно, `[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO.
`k1g.sh wait` в фоне.

## Классификация

Для всех FAILED строк — bounded `k1g.sh log-grep` по `Failed Checks` (только описания, terse).

Засчитываем только если:
- 1 SUCCESS и 2 FAILED, то есть калибровка `should_panic` верна;
- 3 и 5 SUCCESS;
- в 4 и 6 **все** упавшие проверки — описание паники guard (сообщение `panic_on_ord_violation`), и нет ни одной
  pointer/arithmetic/assertion-проверки другого вида.

Тогда вывод: «stub отрезает пути, дошедшие до guard; иных failures default checks на этих двух доменах не
обнаружено». Uninit/validity, unwind-cleanup и исходный volatile-компаратор этим не проверяются. Любая другая упавшая
проверка — немедленно мне, с bounded excerpt, без интерпретации как UB.

**RESULT-PANICPROBE.md**, ≤ 30 строк:
- таблица 6 строк: status, VT, checks, failed descriptions, covers, CBMC RSS;
- вывод по критерию выше;
- ограничения: terse не даёт location; домен — u8, N16/N18, компаратор any-bool без мутации.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **PANICPROBE ЗАВЕРШЁН**, одна стадия, затем стоп.
