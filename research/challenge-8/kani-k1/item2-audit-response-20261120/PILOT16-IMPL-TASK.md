# Кампания 16. Первые wide merge roots и Check sort13

Подготовить один пакет на **11 object bits, 10 GiB local**. Цели — замкнуть N20, проверить смешанный N25, измерить провайдер sort13 и максимальный merge N32. Остальные длины разложены по точным call sites в плане покрытия. Кампания 15 дала SUCCESS на actual-swap Check sort9 при 14,2 млн дизъюнктов, 162–168 с VT, 212–213 с child и 4,29–4,33 GiB. Replace-swap Check в том же профиле достиг 10 GiB. Поэтому presort и merge providers этого пакета выполняют реальные тела с пустыми stubs. [Сводка 15](run-44884852864/SUMMARY.md) · [План N20–N32](MERGE-WIDE-PLAN.md)

## Std и контракты

База `c5dc2a415eb11cb12d1e3a2af8e311739e085f92` / tree `ceca4e449422c32e307b4cde6a1490423ed4b8dc`, worktree `/root/verify-rust-std-ch8-q-pilot-v1`. Один локальный commit. Добавить Kani-only `merge_wide = merge_c_sort9 + --cfg=kani_smallsort_q_merge_wide`, сохранив normal guards с исключением S2, q-mutant и bad-tie. Дельта — contract guards в `smallsort.rs` и расширение verification-модулей `sorting_q_merge.rs` и `sorting_q_merge_model.rs`. Сохранить тела и сигнатуры runtime, компаратор и legacy profiles, включая `CAP=17`. Для взаимоисключающих clauses проверить ровно один активный набор на каждой функции. У `&mut`-контрактов с `old` использовать один `ensures` с конъюнкцией. Снимки `old` — `Clone + Copy`, с проверкой типа, длины и доступности до чтения. [Пины и проверенная форма](PILOT15-IMPL-HANDOFF.md)

- **Presort.** В wide cfg sort9 принимает диапазон 9–12, sort13 — 13–16. У sort13 отключить в wide cfg прежние len17 Pre/assigns/post и сохранить их в legacy. Для exact `u8/KeyLess<u8>` проверять валидный initialized span и writable prefix. Thin `modifies` на первые 9 или 13 элементов, числовой порядок этого префикса, сохранение `count(byte < q)` и q. Упорядоченность плюс count дают всю пороговую маску префикса. Проверить native assigns и отдельный V34 outside-prefix frame, включая хвосты будущих вставок. В каждом Check — произвольный V34, независимый q, actual swaps и те же семь covers, что в 15.
- **Insert.** Сохранить pointer и q Pre, пороговый post, q-frame и inclusive span в `modifies`. В wide cfg распространить numeric post на inclusive длины 10, 11, 12, 14, 15 и 16. Числовой порядок старого префикса влечёт порядок нового span. Проверить этот вывод реальным `insert_tail` с прежним q-монотонным pre, в том числе на q-монотонном, численно неупорядоченном входе. Capture читает только старый префикс. Сохранить q и outside frame. Covers подтверждают каждую заявленную пару base/tail, numeric и q-only префиксы, ранний возврат, полный sift и useful return. L в этом пакете доказывается на base1 с выбором только из tails 9, 10, 11. R — литерально base11/rel9.
- **Merge.** В wide cfg активна отдельная сводка с длинами 20–32 и split `len/2`. Сохранить раздельные native Pre для readable initialized source / writable disjoint dst и числового порядка каждой половины. B18/B19 clauses остаются активны в legacy cfg. Каждый Check использует литеральный `&v[1..1+N]` и отдельный `MaybeUninit<[u8;32]>` с dst offset 0. Исполняются actual up/down, odd copy и ord-guard. Сверить курсоры, все N записей, `modifies` ровно на активный dst, source/q-frame и normal return. Snapshot читает только source. При len=32 вычислять target как `((1_u64 << len) - (1_u64 << below)) as u32`, с `below <= len <= 32`. У выхода shift по индексу максимум 31. Сохранить шесть covers B, добавить на N32 `below==32` и `below==0`. Actual odd copy N25 записывает slot 12. OFF оставляет memory/bounds/overflow/unwind checks. Для native uninit/validity требуется отдельный ON-профиль. [Геометрия и запись merge](MERGE-PLAN.md)

## Потребители и контроли

У N20 и N25 оставить actual `small_sort_network` и copy-back. Литеральные срезы `v[1..21]` и `v[1..26]`, произвольный V34 и q. До вызова захватить target **по исходным байтам всего среза**. Проверить native pre всех Replace, включая числовой порядок на вызове merge, и после copy-back проверить итоговую пороговую маску, q и outside frame. Сохранить шесть covers C13. У N20 вызовы sort9 на `v[1..11]` и `v[11..21]`, вставка rel9 на каждой стороне. У N25 sort9 на `v[1..13]`, sort13 на `v[13..26]` и три левые вставки rel9–11. [Исходник network](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:332) · [Обязательства consumer](PILOT13-IMPL-TASK.md)

- **N25 q-post control.** Нулевой активный вход, q=1, остальной V34 произволен. Те же Replace и actual маршрут. После возврата покрыть `v[1]==0`, присвоить `v[1]=255` и покрыть путь порчи. Проверить q/frame и ожидать одну FAILURE `MW_N25_CORRUPT_QPOST`.
- **N32 numeric Pre control.** Plain с единственным `stub_verified(bidirectional_merge)`. Геометрия N32 как у Check, валидный scratch, q=2, активный source `[1, 0 × 31]`. До вызова покрыть q-монотонность обеих половин, числовую инверсию слева и достижимость литерального входа. Ожидать одну native caller-Pre FAILURE `merge_halves_numeric_order` при валидной геометрии. Проверить exact ID/class/location обоих контролей.

## Exact roster

Префикс selector — `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Все строки `merge_wide`, ordinary stubs пусты. Check строки используют `proof_for_contract` указанной actual функции. У positives ожидается native SUCCESS с полным inventory и covers.

| № | ID | Суффикс selector | Режим и домен | Verified stubs | Child, с |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | MW-S9-L10 | `mw_sort9_left_len10` | Check sort9, `v[1..11]` | ∅ | 600 |
| 2 | MW-S9-R10 | `mw_sort9_right_len10` | Check sort9, `v[11..21]` | ∅ | 600 |
| 3 | MW-INSERT-L | `mw_insert_left_rel9_11` | Check insert, base1/rel9–11 | ∅ | 600 |
| 4 | MW-INSERT-R | `mw_insert_right_b11_rel9` | Check insert, base11/rel9 | ∅ | 600 |
| 5 | MW-MERGE-N20 | `mw_merge_n20` | Check merge, `v[1..21]` | ∅ | 600 |
| 6 | MW-NETWORK-N20 | `mw_network_n20` | Proof N20 | sort9_optimal, insert_tail, bidirectional_merge | 450 |
| 7 | MW-S13-R13 | `mw_sort13_right_len13` | Check sort13, `v[13..26]` | ∅ | 1 800 |
| 8 | MW-S9-L12 | `mw_sort9_left_len12` | Check sort9, `v[1..13]` | ∅ | 600 |
| 9 | MW-MERGE-N25 | `mw_merge_n25` | Check merge, `v[1..26]` | ∅ | 600 |
| 10 | MW-NETWORK-N25 | `mw_network_n25` | Proof N25 | sort9_optimal, sort13_optimal, insert_tail, bidirectional_merge | 450 |
| 11 | MW-N25-QPOST-CORRUPT | `mw_network_n25_corrupt` | Proof N25, контроль | sort9_optimal, sort13_optimal, insert_tail, bidirectional_merge | 300 |
| 12 | MW-MERGE-N32 | `mw_merge_n32` | Check merge, `v[1..33]` | ∅ | 600 |
| 13 | MW-N32-NUMERIC-PRE | `mw_merge_n32_numeric_pre` | Proof N32, контроль | bidirectional_merge | 300 |

## Бюджет sort13 и развилки

Выделить **один** 1 800-секундный Check sort13 с 45 actual swaps, на первом нужном span N25. Старый P‑2b на 11 битах с другими fixture и контрактом построил 25,4 млн дизъюнктов, дошёл до solve и дал timeout 600 с при 5,45 GiB. У sort9 14,2 млн и успешное решение. Отношение размеров CNF не даёт оценки SAT-времени. Удлинённый child — ограниченный исследовательский замер. Сравнить фазу, первую CNF, VT/child и effective/PGID/component RSS. При SUCCESS квалифицировать его точный домен. При solve timeout не размножать 1 800-секундные корни. Следующий эксперимент — раздельно измерить numeric и q/footprint обязательства на том же actual теле либо проверить N25 plain с actual sort13 и verified byte swaps, после свежего Check swap на 11 битах для base13 и пар sort13. N25 с actual sort13 даст покрытие только этого consumer. При cap до CNF сначала измерить footprint/capture encoding с сохранением точного домена и свойств. [P‑2b](run-44849901344/SUMMARY.md) · [Результаты sort9](run-44884852864/SUMMARY.md)

Runner проходит фиксированный roster при штатном cleanup и наличии бюджета. При cutoff листа native SUCCESS зависимого consumer остаётся диагностическим. Для N20 нужны строки 1–5, для N25 и его контроля — 3, 7–9. Сверить exact Pre/post/assigns, source/type/cfg bindings, covers, safety inventory и основания для нужных U. В этом пакете все потребители и их провайдеры на 11 битах. Согласование и повтор исторических N18/N19 на едином профиле ведутся отдельно с результатами воркера qualification. [Профиль всего графа](MERGE-WIDE-PLAN.md)

## Control и handoff

- База control v15 `29e75d9887c2145b5beedf9eb6b170d13bf9218a` / tree `1b6ae480bc28d83df61c4e5f0907e5f4ef3282d6` в `/root/kani-ch8-q-pilot-control-v12`. Локальный `experiment/ch8-q-pilot-control-v16` с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Заморозить roster, cfg, timeout каждой строки, std pins/trees и hashes. Сохранить workflow, event ref, cleanup и bounded raw runner. Request `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`.
- Tool `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`. CaDiCaL, **11 object bits**, `--exact --jobs=1 --no-assert-contracts`, OFF, unwind36, пустые extra CBMC args, отдельные target dirs. Local 10 GiB, outer 12 GiB, резерв 2 GiB и штатный effective cap.
- 8 100 с child budget, job 180 мин, setup/build до 1 800 с, финализация 540 с, остаток 360 с. Latest start = child timeout + 30 с до supervisor cutoff. Capture 16/1/8 MiB на stdout/stderr/export, aggregate **384 MiB** для 13 строк (до 325 MiB members плюс индекс). Зафиксировать первопричину cutoff и `NOT_RUN` у не запущенных строк.
- Локально сверить runtime diff, cfg и уникальность clauses, exact roster и call sites, N32 mask edge и expected control assertions. Выполнить rustfmt check-only, `git diff --check`, `validate` с синтетическими GitHub metadata, `check-source` и `python3 -m unittest -v test_run.py`. Проверить все четыре timeout/latest-start окна, 11 бит, artifact/drift и error paths. Подготовить `PILOT16-IMPL-HANDOFF.md` с pins/trees/hashes, матрицей зависимостей и проверками. Коммиты `[skip ci]`, `Tiramisu-Cake <igkharin@gmail.com>`. Подготовка локальная, запуск после review и отдельного GO.
