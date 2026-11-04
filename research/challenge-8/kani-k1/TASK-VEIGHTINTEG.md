# VEIGHTINTEG — интегрированный кандидат Part 1 v8 из ночных результатов

**Выдано координатором 2026-11-05 (ночь).** Включать ли кандидат в PR, решает владелец. Этап готовит дерево и
доказательства. Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-veightinteg**, ветка **experiment/kani-k1-veightinteg-20261105** от
  **5378a0ba00** (CODEFIX: library v8 `56efe5c477`, 204 ordinary, 8 контролей).
- Slug **veightinteg**; stable owner — свободный на момент dispatch. Request_id `veightinteg-*`.
- Project cap **$118.96**, свой cap **$3.00**. **Одна сборка**, retry нет. Один compile-error repair.
  Tooling base: **59893bff1f**.
- Окно: main 240 + closeout 30 мин.

## Источники (только наши ветки)

- **REALCONTRACTSTWO** `588c002998`: `requires`/`modifies` на `swap_if_less`, `insertion_sort_shift_left`,
  `insert_tail`, `sort4_stable`, `bidirectional_merge` в `smallsort.rs`, `#[cfg(kani)] use crate::kani;`,
  cfg(kani)-helpers и `verify/realcontracts.rs` (RESULT-REALCONTRACTSTWO с временами).
- **PERMTAGS** `c59410d242`: `verify/permtags.rs` (RESULT-PERMTAGS).
- **SCRATCHGEOM** `151c193b63`: `verify/scratchgeom.rs` (RESULT-SCRATCHGEOM).

## Что собрать: три library-коммита поверх v8, чтобы владелец мог выбрать

1. **Контракты на настоящих хелперах:** атрибуты и helpers в `smallsort.rs` ровно как в `588c002998`; модуль
   `realcontracts`.
   - В ordinary: PFC с SUCCESS ≤ 60 с на GCB — swap u8/u64/`[u8;17]` backing4, swap u8 backing9/13, `insert_tail`
     u64, `sort4` u64, `merge` u64 len2/len4.
   - Также в ordinary: пары consumers `unstable_network_safety_u8_n9/n13_stubbed`, только если их PFC-домен
     совпадает и тоже в ordinary.
   - Остальное (негативные контроли, `insertion` len2/3 > 60 с, `sort4` `[u8;16]` 74 с) — под
     `cfg(kani_smallsort_controls)`.
2. **Перестановка через теги:** `permtags` — в ordinary `network_u8_n9`, `network_u8_n13`,
   `tag_types_preserve_source_routes`. Остальное, включая мутант, — под cfg.
3. **Геометрия scratch:** `scratchgeom` — в ordinary `stable_u64_min_scratch_n2`, остальное — под cfg.

Doc модуля `verify.rs` обновить фактически: что новое, домены, допущение переноса для permtags. Коммиты library
`[skip ci]`, каждый отдельно.

## Статика

- Ordinary = 204 + новые; список имён. Cfg-on = ordinary + все opt-in.
- Тела 204 v8 совпадают с v8 по токенам.
- rustfmt, `git diff --check`, строки ≤ 100. Diff против `233f96f66a` — только `smallsort.rs` (атрибуты, use,
  cfg(kani)-helpers), `smallsort/verify*` и `Cargo.toml` check-cfg.
- Подсчёт строк: всего, ordinary/opt-in, отдельно строки в `smallsort.rs`.
- Оценка добавки к CI: сумма GCB-времён новых ordinary.

## Сборка

Одна, kind diagnostic, `inventory: true` (cfg-off список = точный ordinary-набор), `controls: false`, jobs 1,
лимит 10 мин. Строки: все новые ordinary-корни (≤ 15). Ожидание — SUCCESS и все covers.

## Коммиты, ожидание, RESULT

- Research отдельно, `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.
- **RESULT-VEIGHTINTEG.md**, ≤ 40 строк:
  - три коммита и что в каждом;
  - inventory;
  - таблица строк;
  - строки и CI-оценка;
  - что требует решения владельца: контракты в runtime-файле, новые корни.

## Запреты

- Только bounded evidence; raw logs и credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код и документация Kani; чужие PR не открывать.
- Тела runtime-функций, workflows и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **VEIGHTINTEG ЗАВЕРШЁН**, затем стоп.
