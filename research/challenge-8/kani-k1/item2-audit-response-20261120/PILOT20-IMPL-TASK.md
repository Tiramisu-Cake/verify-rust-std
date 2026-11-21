# Кампания 20. N20 matched и actual вставки в wide network

Подготовить один serial пакет на **OB11, local cap 6 GiB**. N20 закрывает width и новый q-post control на actual вставках. N25 проверяет устранение object-capacity/RSS отказов на том же компактном harness. N24 и N27 проверяют схему в двух разных геометриях. Кампания 19 продолжает свой замороженный roster. [Сводка 18](run-44907708573/SUMMARY.md) · [Матрица wide](MERGE-WIDE-PLAN.md)

## N20 matched

Оставить `compact_network_n20_actual_insert` и повторить его на **OB11**. Нужны два дешёвых корня, consumer и новый контроль. Это сразу согласует ширину с тремя успешными Check из 16: `MW-S9-L10` на `v[1..11]`, `MW-S9-R10` на `v[11..21]` и `MW-MERGE-N20` на `v[1..21]` → scratch32+0. Исторический actual consumer на OB12 — 2,49 GiB, 68 с child, 33,6 с VT и 0,61 млн clauses. Вариант с Replace вставок — 8,34 GiB, 203 с child и 8,9 млн clauses. Эти данные обосновывают сначала повтор пары на 11 вместо трёх Check на 12, но ёмкость actual-insert варианта на OB11 ещё измеряется. Прежний capacity отказ на OB11 относится к маршруту с Replace insert. [Провайдеры 16](run-44890498157/SUMMARY.md) · [A/B 18](run-44907708573/SUMMARY.md)

Verified stubs ровно `sort9_optimal, bidirectional_merge`. Обе вставки rel9 исполняют actual `insert_tail`, на base1 и base11. Для этого маршрута нет insert provider edge. Новый `compact_network_n20_actual_insert_corrupt` использует те же stubs и геометрию. Сохранить q=1, нулевой активный вход, произвольные внешние байты и компактный frame. Проверить полезный возврат, внести `v[1]=255`, покрыть порчу, проверить q/frame и ожидать единственную `COMPACT_N20_ACT_INSERT_CORRUPT_QPOST`. Контроль 18 со сводками вставок служит для своего маршрута.

При capacity отказе actual пары на OB11 следующий минимальный вариант — оставить исторический actual consumer OB12, подтвердить перенос harness без дрейфа, сделать новый actual контроль на OB12 и повторить эти три exact Check на OB12. Отдельно оценить fit каждого. При RSS/timeout локализовать фазу. Capacity, RSS и неуспех свойства остаются разными исходами.

## Wide. N25, N24 и N27

В compact consumers сохранить V34/base1, произвольные байты и независимый q, target по исходному активному срезу, q-frame, каждый внешний байт и шесть covers. Вставки выполняет реальная сеть. Обязательные native geometry/numeric Pre merge доказываются на actual состоянии после presort и insert. Сохранить bounds/memory/overflow/unwind у вставок, обе actual ветви выбора половины и actual copy-back. Whole-merge Check исполняет реальные up/down, курсоры, guard и, где есть, odd copy. Check берёт отдельный `MaybeUninit<[u8;32]>` с dst offset 0 и проверяет q/byte source frame, q-post, полный active write footprint и шесть covers. OFF scope сохраняется. [Реальная сеть](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:332) · [Wide provider fixtures](PILOT16-IMPL-HANDOFF.md)

| Длина | Actual вставки и exact диапазоны | Check → Replace |
| --- | --- | --- |
| **N25** | `v[1..26]`, split 12+13. Слева rel9–11, справа пусто, odd scratch slot12 | 16 `MW-S9-L12` на `v[1..13]`, `MW-S13-R13` на `v[13..26]`, `MW-MERGE-N25`, все OB11. Stubs sort9, sort13, merge. Добавить exact actual N25 control по форме N20 с тем же N25 stub set и `COMPACT_N25_ACT_INSERT_CORRUPT_QPOST`. |
| **N24** | `v[1..25]`, split 12+12. Шесть вставок, rel9–11 при base1 и base13, even merge | 16 `MW-S9-L12` и новые right sort9 Check на `v[13..25]` и whole merge Check на `v[1..25]`. Stubs sort9, merge. |
| **N27** | `v[1..28]`, split 13+14. Слева пусто, справа base14/rel13, odd scratch slot13 | 17A `NM-S13-L13` на `v[1..14]` после сверки active presort clauses, новый right sort13 Check на `v[14..28]` и whole merge Check на `v[1..28]`. Stubs sort13, merge. |

N24 выбран как верх двух sort9 и максимум вставок в этой группе. N27 проверяет первый actual tail после sort13 и случай с двумя sort13. Для `NM-S13-L13` сверить `no_merge_sort13` и `merge_wide` на точном len13. Расширение допустимой длины до 17 в первом профиле и q-only insert clauses сохраняют действующие предикаты presort на len13. Вставка в новом consumer идёт в Original. При дрейфе активных ролей оставить левый Check открытым. Новый right sort13 Check сохраняет `v[27]` и остальные байты вне `v[14..27]`. У новых sort9/sort13 Check — реальные swaps, присваивания только первых 9/13, numeric/q post и семь covers.

N25 с Replace вставок исчерпал объекты на OB12 и 10 GiB на OB13 после CNF. Начать с OB11 actual, где все его провайдеры уже имеют результаты. При capacity cutoff рассмотреть ту же actual пару на OB12 как отдельное измерение с отдельным matched планом. Q-post controls этого пакета ставим на N20 и N25. N24/N27 — диагностические exact positives, для следующего допуска учитывать их собственные Check и требуемую контрольную привязку. [Отказы 18](run-44907708573/SUMMARY.md) · [Области Check](MERGE-WIDE-PLAN.md)

**Дальше.** При успешном N24 добавить N21–N23 с exact sort9 `(base,len)=(1,11),(11,11),(12,11),(12,12)`, тремя whole-merge Check и exact consumers. При рабочем N27 начинать оставшуюся группу с N26 как случая двух sort13 и пустых циклов вставок, затем N28–N31 с их actual tails по матрице. Новые правые sort13 после N27 — `(14,13),(15,14),(15,15),(16,15),(16,16)`. Левые `(1,13..=15)` из 17A требуют такой же сверки active scope и ресурса. Каждый новый merge и consumer сохраняет exact длину. Для actual маршрута Check insert не входит в proof graph. Если более длинный consumer достигает cap, выделить первый проблемный exact span и измерить actual insertion loop с его реальной геометрией. [Полная матрица](MERGE-WIDE-PLAN.md)

## Std, roster и бюджет

База std `a9e7dba799a22b49f4bad3be1579c08d9e0763a3` / tree `78079cf6e72d4cc56f77876c4ba61e98fe689dbf` в `/root/verify-rust-std-ch8-q-pilot-v1`. Один локальный commit только с verification harnesses в `verify/sorting_q_merge.rs`. Переиспользовать `define_compact_wide_network!` и существующие Check helpers, оставить runtime, модели, active clauses и старые roots. Для reuse из 16 и 17A сверить применимые исходники, active cfg, exact type/domain, tool и OB11. [База 18](PILOT18-IMPL-HANDOFF.md)

Префикс `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Все строки `merge_wide / OB11`, ordinary stubs пусты. Check используют пустые verified stubs. Positives ожидают SUCCESS, у двух контролей по одной назначенной FAILURE и два covers.

| № | Root ID | Exact selector suffix | Режим / verified stubs | Child, с |
| ---: | --- | --- | --- | ---: |
| 1 | COMPACT-N20-ACT-INSERT-OB11 | `compact_network_n20_actual_insert` | Proof, sort9 / merge | 600 |
| 2 | COMPACT-N20-ACT-INSERT-CORRUPT-OB11 | `compact_network_n20_actual_insert_corrupt` | Proof control, sort9 / merge | 300 |
| 3 | COMPACT-N25-ACT-INSERT-OB11 | `compact_network_n25_actual_insert` | Proof, sort9 / sort13 / merge | 600 |
| 4 | COMPACT-N25-ACT-INSERT-CORRUPT-OB11 | `compact_network_n25_actual_insert_corrupt` | Proof control, sort9 / sort13 / merge | 300 |
| 5 | MW-S9-R-B13-L12-OB11 | `mw_sort9_right_b13_len12` | Check sort9 | 600 |
| 6 | MW-MERGE-N24-OB11 | `mw_merge_n24` | Check merge | 600 |
| 7 | COMPACT-N24-ACT-INSERT-OB11 | `compact_network_n24_actual_insert` | Proof, sort9 / merge | 600 |
| 8 | MW-S13-R-B14-L14-OB11 | `mw_sort13_right_b14_len14` | Check sort13 | 1 200 |
| 9 | MW-MERGE-N27-OB11 | `mw_merge_n27` | Check merge | 600 |
| 10 | COMPACT-N27-ACT-INSERT-OB11 | `compact_network_n27_actual_insert` | Proof, sort13 / merge | 600 |

Один setup/build, **6 000 с child**, setup/build до 1 800 с, финализация 540 с, job 180 мин, запас 2 460 с. Latest start за timeout + 30 с до supervisor cutoff. R14 Check при 6 GiB — измерение fit новой геометрии. Ближайший R13 занимал 7,32 GiB, поэтому возможен RSS cutoff. Runner сохраняет исходную причину и при штатном cleanup запускает оставшиеся строки. Если right Check открыт, SUCCESS N27 остаётся условным диагностическим результатом. Считать максимум RSS по **всей** цепочке, включая перенесённых провайдеров. У N25 прежний R13 Check уже выше 6 GiB.

## Sort13. Ресурсное решение

Компактный L17 observer дал 7,23 против 7,35 GiB, 25,3 против 25,5 млн clauses и больший VT. Дальнейшая подстройка observer слабо обоснована. Наиболее вероятный источник — DFCC проверки actual swap и модели pointer copies на 45 вызовах, включая учёт lifetime и версии таблиц объектов. Замеры не отделяют конкретную операцию. Перспективный отдельный эксперимент на tool-ветке — уменьшить DFCC учёт **доказанно локальных и неэкранирующих** temporaries в lowering `memcpy/memmove`, сохранив все проверки внешних записей. До проверки поддержанных alias/overlap/escape случаев и записей вне frame с последующим восстановлением текущие Check остаются основой. В кампании 20 tool и proof clauses сохраняются. [Анализ DFCC](PILOT-RUN5-ANALYSIS.md) · [Замеры 17A](run-44896810040/SUMMARY.md) · [Компактный L17](run-44907708573/SUMMARY.md)

Для решения владельца подготовить **узкую serial полосу с cap 8 GiB только для пяти `NM-S13-L13`…`L17` из 17A**. Точный std `3fff6aa0db`, `no_merge_sort13`, OB11, текущий tool/checks, actual swaps, 1 200 с child и jobs=1. Наблюдавшийся пик 7,35 GiB оставляет около 0,65 GiB запаса, калибровка 8 GiB ещё нужна. Обычный cap для consumers остаётся 6 GiB. Допуск требует результатов 19, native привязки и решения владельца. N25 R13 и новый N27 R14 учитываются отдельно по их собственным измерениям.

## Control и handoff

- Основа 19 `400b54a57cc1b1de2ebeca3060e95cf5954ec69c` / tree `e548edece4474ec5412c29e359b3959fa2716095` в `/root/kani-ch8-q-pilot-control-v19`. Новый кандидат `experiment/ch8-q-pilot-control-v20` с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Сохранить workflow/event ref, cfg definitions, cleanup и bounded runner. Заморозить roster, timeouts, pins и hashes. Request `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`.
- Tool `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`. CaDiCaL, `--exact --jobs=1 --no-assert-contracts`, regular, unwind36, OFF, пустые extra CBMC args и отдельные target dirs. Local 6 GiB, outer 12 GiB, reserve 2 GiB. Capture 16/1/8 MiB на stdout/stderr/export, 384 MiB aggregate. Сохранить effective RSS, PGID/outer/component peaks, capacity/CNF/solve, VT/child, native inventory или первопричину cutoff.
- Локально сверить cfg, exact slices и stub sets, назначенные негативы и роли из inventory. Выполнить rustfmt check-only, `git diff --check`, `validate` с synthetic GitHub metadata, `check-source` и `python3 -m unittest -v test_run.py`. Проверить frozen roster, запуск независимых roots после cutoff, все latest-start окна и error paths. Handoff `PILOT20-IMPL-HANDOFF.md` с pins/trees/hashes и зависимостями для qualification. Коммиты `[skip ci]`, `Tiramisu-Cake <igkharin@gmail.com>`. Подготовка локальная, диспатч после review и отдельного GO.
