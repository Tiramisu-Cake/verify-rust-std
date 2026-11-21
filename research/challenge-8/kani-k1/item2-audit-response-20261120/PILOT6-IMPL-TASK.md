# Кампания 6 q-пилота: A/B кодировки массивов CBMC без изменения std (воркер, 2026-11-21)

Основание: `PILOT-RUN5-ANALYSIS.md`. Решение координатора: **слоевая декомпозиция пока откладывается** — она требует разнести тело runtime-функции `sort13_optimal` на новые helper-функции, а это изменение кода std, которое критерии челленджа и организаторы, скорее всего, не примут. Сначала дешёвый A/B на текущем std pin из раздела «Если первый пакет не закроет провайдер»: `--refine-arrays` и статистика `--show-array-constraints`.

Изменяется **только control**. std `c8b703918a40c03d5b889d3018d8d818a70c233f` и tool `0aac16ef62…` без изменений.

Новая ветка от `experiment/ch8-q-pilot-control-v5` (`d453bb80a5`), коммит с parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Roster, по порядку, cap 6 GiB / outer 12 / reserve 2, CaDiCaL:

| ID | Селектор (после `slice::sort::shared::smallsort::verify::sorting_q_pilot::`) | object bits | дополнительные CBMC-аргументы | child, с |
| --- | --- | ---: | --- | ---: |
| P17-STATS | `d13_check_p17` (точное имя из std) | 12 | `--show-array-constraints` | 180 |
| P17-REFINE | то же | 12 | `--refine-arrays --show-array-constraints` | 180 |
| P-2b-OB11-REFINE | `p2b_sort13_u8_b01_len17_q_any_actual_swaps` | 11 | `--refine-arrays` | 600 |
| P-2-OB11-REFINE | `p2_sort13_u8_b01_len17_q_any` (45 Replace swap) | 11 | `--refine-arrays` | 600 |

Дополнительные аргументы — фиксированный закрытый список в request на корень, передаются после `--cbmc-args` вместе с `--object-bits`; согласовать с per-root timeout и latest start; записывать в raw index. Сначала проверь по исходникам CBMC 6.11 (в зависимостях Kani на пине) и Kani `call_cbmc.rs`, что оба флага существуют и проходят через `--cbmc-args`; если `--show-array-constraints` несовместим с выводом Kani (например, требует JSON UI и ломает разбор), исключи его и опиши это в handoff. Тесты на roster/argv/лимиты; validate, check-source, test_run.py локально.

Без cargo, rustc, Kani, CBMC, CI и пушей. Коммит `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Handoff `PILOT6-IMPL-HANDOFF.md` здесь, коммит в g0 `[skip ci]`.
