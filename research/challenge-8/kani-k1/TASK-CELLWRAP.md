# CELLWRAP — фаза D2: контракт-обёртка blanket-пути с мутирующим компаратором и защищёнными тегами (N2-пилот)

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-cellwrap**, ветка **experiment/kani-k1-cellwrap-20261103** от
  **e0fda080f5ea479d8f4fb801f4b42adde2b3259f** (v6 library tree + K-1 tooling + cap 98.96).
- Slug **cellwrap**, stable owner **k1-merge**. Новые stage/ledger/UUID/request_id `cellwrap-*`.
- Project cap **$98.96**, свой cap **$0.90**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Tooling base для check-tooling: e0fda080f5.
- Окно: main 150 + closeout 30 мин.

## Контекст

В v6 есть ordinary-обёртки N2 (`verify/wrap.rs`): контракт на `cfg(kani)`-функции, которая вызывает реальный
`small_sort`. Для blanket-пути `Cell<u8>` компаратор там чистый (`cell_less`). Отдельно safety-корни `network.rs`
используют `Cell<TaggedKey>` и `mutating_key_order`: компаратор пишет произвольные ключи и сохраняет теги.

Задача D2 — bounded-пилот контракта для этого случая. Обещать порядок мутируемых ключей нельзя. Обещаем:
- **перестановку тегов**: мультимножество tag по независимой u8-пробе до и после равно;
- **frame**: вне активного участка ничего не меняется.

Это не общий контракт для произвольного `FnMut`.

## Source scope

Новый opt-in child `wrap::cellwrap`, файл `verify/wrap/cellwrap.rs`. В `wrap.rs` — только
`#[cfg(kani_smallsort_controls)] mod cellwrap;`. Существующие wrappers, guard и компараторы не менять.

Тип элемента — `Cell<TaggedKey>` с `key: u8, tag: u8`, тот же смысл, что в `network.rs`. Компаратор — каноническая
`fn`-указатель-функция по образцу `mutating_key_order`: читает оба значения, пишет произвольные ключи, теги сохраняет,
возвращает произвольный bool. Guard — `canonical` по адресу, как в `wrap.rs`.

Ровно 3 roots:

| # | Root | Что | Ожидание |
|---|---|---|---|
| 1 | `cellwrap_stable_tags_n2` | `proof_for_contract` на `<Cell<TaggedKey> as StableSmallSortTypeImpl>::small_sort` (blanket → insertion), backing 4, активная пара 1..3, независимая проба tag, frame | SUCCESS |
| 2 | `cellwrap_tag_corruption_control` | та же обёртка, но тело после сортировки портит один tag (мутант только в контрольной обёртке) | FAILED на ensures перестановки тегов |
| 3 | `cellwrap_wrong_comparator_control` | вызов обёртки с другим `fn`-указателем | FAILED только на guard `canonical` |

Контракт:
- requires: region пары и canonical comparator;
- modifies: активная пара;
- ensures: tag-count по пробе до и после равен.

Unwind — как у wrap N2 (16). Covers: нормальный возврат, проба попадает и не попадает, компаратор сменил ключ.

Static:
- ordinary 202 / ordinary-PFC 36 неизменны;
- exact name-set delta (+3);
- rustfmt;
- без warnings.

## Пакет

3 строки, kind diagnostic (1 expect SUCCESS, 2 и 3 expect FAILED + expect_check; сверить с `kani_k1.py`):
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (3×10+30)×$0.0135 = **$0.810**.

Project ≤ 2 unfinished, ≤ 1 на k1-merge. Параллельно может идти PERMANY (k1-network).

PRE-BUILD:
- semantic diff против `wrap::stable_cell_n2` (тип, компаратор, ensures);
- маршрут blanket Stable по source;
- hashes, budget.

Коммиты library/research отдельно, `[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в
фоне.

## Gate и RESULT

Засчитываем, если:
- 1 SUCCESS с covers;
- 2 и 3 FAILED ровно на назначенной проверке (по описанию и location; terse печатает location упавших проверок).

TIMEOUT/иное — bounded facts, без retry.

**RESULT-CELLWRAP.md**, ≤ 30 строк:
- таблица 3 строк;
- точная формулировка доказанного: тип, N, компаратор, свойство;
- что не доказано: порядок, N > 2, unstable blanket, произвольный `FnMut`.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **CELLWRAP ЗАВЕРШЁН**, одна стадия, затем стоп.
