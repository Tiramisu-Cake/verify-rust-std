# CORR14 — PARTIAL: кандидат перед PRE-BUILD REVIEW

Дата: 2026-10-31. Ветка `experiment/kani-k1-corrfourteen-20261031`.
Base `7c0c345b857bca90cfebed4f204251b6e30eee9c`.
Library SHA `2bc00fceee2d6afcaca8eb136e625064e5449f73`.
Frozen library tree `1a7403c9949e5749a9040127935f86b96cf66a27`.
Request: `corr14-g1-split-scratch-u8-n14-20261031`, measurement/jobs1/controls:true.
Build ID отсутствует: до GO координатора dispatch не разрешён. Свои builds0/2, cost$0.
T0 07:34:39 UTC; работа до11:04:39, закрытие до11:34:39; резерв закрытия30min.
G1 envelope100min/$1.35; G2 optional70min/$0.945; общий максимум$2.295≤$2.3.
Перед dispatch нужны свежий k1g budget и проверка полного envelope в остатке окна.

Все гармоники таблицы — `correct::`; данные измерений PENDING, credit не заявлен.

| Гармоника | Маршрут | Scratch | Статус | VT | CBMC RSS | Covers | Checks |
|---|---|---|---|---|---|---|---|
| sorted_permutation_general_stable_u8_n14 | combined | прежний | PENDING | — | — | — | — |
| sorted_permutation_general_u8_n14 | general | внутренний holder48 | PENDING | — | — | — | — |
| sorted_permutation_stable_nonconst_u8_n14 | stable | non-const48 | PENDING | — | — | — | — |
| sorted_permutation_stable_const_u8_n14 | stable | const48 | PENDING | — | — | — | — |
| sorted_permutation_stable_aggregate_u8_n14 | stable | aggregate48 | PENDING | — | — | — | — |
| stable_aggregate_value_corruption_control_u8_n14 | stable | aggregate48 | PENDING | — | — | — | — |
| stable_aggregate_allocation_bounds_control_u8 | raw write | aggregate48 | PENDING | — | — | — | — |

Split: general + non-const stable статически воспроизводят прежние ветви/входы combined;
объединение fixed-route covers представляет оба маршрута. Выигрыш ещё не измерен.
Форма scratch: const/aggregate сохраняют функциональный T/F/N/input/probe-домен.
Aggregate меняет backing-геометрию; это не proof старой fixture и не transfer.
Подробности и ограничения статического сопоставления: `corr14/source-map.md`.

Общий private opt-in corr14_check_u8_n14 вызывается четырьмя positive и corruption.
В нём прежние asserts в прежнем порядке: sortedness, затем full-value probe count.
Corruption: actual lt_u8, оба stub targets; output[0]^=1 после sort, перед общим checker.
Ожидается только count-assert FAILED; placeholder и location требуют ручной сверки.
Bounds: raw write one-past всей allocation48 через adapter; ожидается object-bounds FAILED.
Фактические locations пока отсутствуют. Safe indexing panic и uninit T read не используются.

Jobs3: PENDING; G2 разрешён лишь при SUCCESS выбранных general/stable, SATISFIED covers,
целевых контролях и измеренном выигрыше пика или суммарной цены по строкам G1.
G2: general N14 + лучшая stable N14 + contract_insert_tail_u8_scratch + merge N14.
Это ресурсная проверка листьев; она не переносит их proof на scratch48 caller.

Статическая проверка PASS: старый файл сохранён, checker совпадает с baseline oracle,
четыре positive и corruption вызывают этот checker; точное извлечение проверено.
новые private items opt-in; ordinary +0, opt-in +6. `corr14/static-check.json`.
Rustfmt заданным wrapper/config --check exit0, изменённый .rs ≤100 колонок.
Request validator: 7 entries accepted; git diff --check PASS.
Локально rustc/cargo/Kani/CBMC не запускались; warnings обеих cfg ещё не установлены.
В library изменён только correct.rs; lane/pin/toolchain/flags прежние, timeout600.

Рекомендации N13/N15 и u64: дождаться matched G1; в этой сессии их не запускать.
Caller conditional: insert_tail/merge callee premises этих доменов остаются открытыми.
Fixture48 ≠ любой backing. macOS UNKNOWN. Пригодность подтверждает только CI организаторов.
Чтение своих результатов — k1g; ожидание — k1g watch с завершением хода.
