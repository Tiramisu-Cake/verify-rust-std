# REV2 N26–N31 consumer · независимое ревью R1

**GO_WITH_NITS**, блокеров нет. Ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26.

Пины:
- Std `50609bb850c64080aedd74c00c9865dcae1ce74b` (tree `c2e93c5665`, parent `71953c45a9`);
- control `a02a710c0c1206459d924c7467c9092b6921c674` (tree `7a92427bc3e81e99016536ee6ef87dd761eb7f3a`, parent `108c45668b`);
- review-trigger `1d33084054` (тот же tree, sole parent `467af9cb8d`);
- handoff g0 `83c3a8ebb6`.

[Задание](REV2-N26-N31-CONSUMER-TASK.md) · [Handoff](REV2-N26-N31-CONSUMER-HANDOFF.md)

## Неблокирующее

1. **Форма совпадает с N22–N25 по смыслу, но не побайтно.** В `rev2_n26_n31_consumer.rs:21–352` oracle и заполнение V34 встроены прямо в каждый `check_nN`. Прецедент выносит их в `backing_with_bits`/`matches_sorted_mask`. Семантика та же: `before` после записи битов, `expected = low ^ (low >> popcount)`, те же канонические условия. Место отказа контроля остаётся в `check_nN::<true>`. Отметить в admission.
2. **Guard `not targets` (`run.py:283–290`) стал шире прежнего.** Он действует для standard harness всех REV2-модулей, а `read_list` (`run.py:233`) включает в `known` и standard selectors. Это строже исторической формы. Принятие 78 унаследованных записей на 45861423438 не перепроверялось, это утверждение handoff.

## Проверено

- **Std-дельта.** Только check-cfg, cfg-gate (18 cfg) и новый модуль на 352 строки. Runtime и прежние модули не изменились. Stubs, Replace, loop contracts и assume нет. 12 plain proof с `unwind(36)`, actual `small_sort_network::<u8, KeyLess<u8>>` на точном `backing[1..1+N]`. Порчу `backing[1] ^= 1` делает только контроль, после возврата. Порядок: N31, затем N26–N30.
- **Независимая модель на Python.** Модель воспроизводит S13 (45 пар `:612–656`), вставки, merge и нечётный центр. Все шесть контрольных масок отказывают именно на `CANONICAL_SORTED_POPCOUNT`. Нечётные центры дают ожидаемые состояния. На каждой длине 20 000 битовых и 5 000 байтовых случайных входов отсортированы верно.
- **Roster.** Хэши request, bundle (55 091 байт), roster, bindings и вложенного merge roster сходятся. Все 12 корней с `copy_back=true`. Covers и `expected_failure` на нужных строках и столбцах.
- **Гейт результата.** Grouped `copy_nonoverlapping` на `ptr/mod.rs:587:14`, все unwind SUCCESS, у контроля единственный отказ assertion с привязкой.
- **Discovery.** Preflight идёт до discovery, дельта ровно 12.
- **Часы.** 12×205 с, measure 44:05 при внешних 46 мин, cutoff 102:55, upload до 110:00, план 119:00 при job 120 мин.
- **Сбои.** При превышении cap и подтверждённом reap следующие слоты продолжаются. Без подтверждения — `PROCESS_CLEANUP_COULD_NOT_BE_VERIFIED`.
- **Trigger gate и перенос замечаний.** Trigger gate по новой переменной `CH8_REV2_N26_N31_CONSUMER_TRIGGER_TREE`. Три замечания merge-ревью закрыты (`run.py:289`, `results.py:230–232`, handoff:118).
- **Прочее.** `test_supervisor.py` `df63a457`. `bundle verify` PASS. Suite 122/122 OK в чистом clone, rustfmt и `git diff --check` чистые. Авторство и `[skip ci]` в порядке.

NOT_RUN: cargo, rustc, Kani, CBMC, нативный compile и discovery; шкалы 1/5/60 с (у автора 122/122); YAML и `bash -n`; bundle на bare shallow-базе.

Решение координатора: замечания не требуют FIX. Пакет передаётся на GO. Запуск — после прогона валидности 45870184232.
