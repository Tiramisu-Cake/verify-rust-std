# Кампания 16. Handoff wide merge N20, N25 и N32

Подготовлен локальный пакет из 13 exact-корней для `u8/KeyLess<u8>`. N20 проверяет два sort9 и две вставки. N25 добавляет правый sort13, три левые вставки и отдельный Check нечётного merge. N32 измеряет максимальный actual merge. Request имеет `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Пакет остаётся `RESEARCH_ONLY`. [Задание 16](PILOT16-IMPL-TASK.md) · [План N20–N32](MERGE-WIDE-PLAN.md)

## Pins и hashes

| Объект | Worktree и ветка | Commit | Tree | Parent |
| --- | --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `ed184d3f172def1b4d1bf6281a03ba2a0d5bb8f1` | `e2a757c2ca5659a83e70f3775ebce3e672dd0463` | `c5dc2a415eb11cb12d1e3a2af8e311739e085f92` |
| Control | `/root/kani-ch8-q-pilot-control-v12`, `experiment/ch8-q-pilot-control-v16` | `0578f584b650488cee98281961e8f699a82ab942` | `6e0f3a04555c4dfe90a5d3195610b86c541cc253` | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` | — |

У std один commit поверх Pilot 15. Control v16 основан по содержимому на v15 `29e75d9887c2145b5beedf9eb6b170d13bf9218a` / tree `1b6ae480bc28d83df61c4e5f0907e5f4ef3282d6` и сохраняет заданный единственный parent. Workflow и event ref `refs/heads/uninit-ci/ch8-q-pilot-v1` совпадают с v15. Историческое имя шага `Run seven q-pilot roots` сохранено, число запусков задаёт roster. [Handoff 15](PILOT15-IMPL-HANDOFF.md) · [Замороженный request](/root/kani-ch8-q-pilot-control-v12/ch8-q-pilot-control/CI-REQUEST.json)

| Файл | SHA-256 |
| --- | --- |
| std `smallsort.rs` | `d0b92f486e68ff4853bdca12b8fceb196391c97ec22086409fa0b50756c4c848` |
| std `sorting_q_merge.rs` | `075e96a93a0774ea37cc1c580b5bffae545185b21c31d2056670761f016f1ee7` |
| std `sorting_q_merge_model.rs` | `a0772234d7e4709fda006f09529a0f5f18a0db803ce02b89bba767080796eaa2` |
| Control `CI-REQUEST.json` | `11592b80dd83eb39aab8cfc5458a049660d4314ee93050fbdb7a6afb6770eeae` |
| Control `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| Control `run.py` | `a51f08f2a0973ef8f03ba43ef6e51a8880ad487d99a37a3e0efc1d3bbd49614c` |
| Control `test_run.py` | `eb3bae3bbb5eccc9be5d1faa2dba48ecf6014a351f2e1784c13fd5afad27dfba` |

Хэши остальных пяти std-файлов совпадают с Pilot 15. Request хранит весь список из восьми файлов. [Инвентарь SHA-256](/root/kani-ch8-q-pilot-control-v12/ch8-q-pilot-control/CI-REQUEST.json:15)

## Roster и зависимости

Префикс селекторов `slice::sort::shared::smallsort::verify::sorting_q_merge::`. На каждой строке `merge_wide`, пустые ordinary stubs, пустые дополнительные CBMC args. Для Check verified stubs тоже пусты. Ожидания для 11 положительных строк — native SUCCESS с полным inventory и достижимыми covers.

| № | Root ID | Суффикс | Область или зависимость | Лимит, с |
| ---: | --- | --- | --- | ---: |
| 1 | MW-S9-L10 | `mw_sort9_left_len10` | Check sort9, `v[1..11]`, пишет `v[1..10]` | 600 |
| 2 | MW-S9-R10 | `mw_sort9_right_len10` | Check sort9, `v[11..21]`, пишет `v[11..20]` | 600 |
| 3 | MW-INSERT-L | `mw_insert_left_rel9_11` | Check insert, base1, rel9, 10 или 11 | 600 |
| 4 | MW-INSERT-R | `mw_insert_right_b11_rel9` | Check insert, base11/rel9 | 600 |
| 5 | MW-MERGE-N20 | `mw_merge_n20` | Check merge, `v[1..21]` → scratch32 +0 | 600 |
| 6 | MW-NETWORK-N20 | `mw_network_n20` | Plain `v[1..21]`, Replace sort9 ×2, insert ×2, merge. Провайдеры 1–5 | 450 |
| 7 | MW-S13-R13 | `mw_sort13_right_len13` | Check sort13, `v[13..26]`, 45 actual swaps | 1800 |
| 8 | MW-S9-L12 | `mw_sort9_left_len12` | Check sort9, `v[1..13]`, пишет `v[1..10]` | 600 |
| 9 | MW-MERGE-N25 | `mw_merge_n25` | Check merge, `v[1..26]` → scratch32 +0 | 600 |
| 10 | MW-NETWORK-N25 | `mw_network_n25` | Plain `v[1..26]`, Replace sort9, sort13, insert ×3, merge. Провайдеры 3, 7–9 | 450 |
| 11 | MW-N25-QPOST-CORRUPT | `mw_network_n25_corrupt` | Контроль того же маршрута и Replace, провайдеры 3, 7–9 | 300 |
| 12 | MW-MERGE-N32 | `mw_merge_n32` | Check merge, `v[1..33]` → scratch32 +0 | 600 |
| 13 | MW-N32-NUMERIC-PRE | `mw_merge_n32_numeric_pre` | Контроль caller Pre, один Replace merge в геометрии 12 | 300 |

`merge_wide` добавляет `--cfg=kani_smallsort_q_merge_wide` к `merge_c_sort9`. Профиль использует CaDiCaL по умолчанию закреплённого tool, 11 object bits, `--exact --jobs=1 --no-assert-contracts`, OFF, unwind36 и отдельные target dirs. Local cap 10 GiB, outer 12 GiB и резерв 2 GiB. Runner использует меньший из nominal и доступного cap. [Roster и лимиты](/root/kani-ch8-q-pilot-control-v12/ch8-q-pilot-control/run.py:47) · [Solver](/root/kani-upstream-ch8-s1/kani-driver/src/call_cbmc.rs:105)

Child budget 8100 с. Job 180 минут, setup/build до 1800 с, резерв финализации 540 с, остаток 360 с. Latest start для child 300/450/600/1800 с наступает за 330/480/630/1830 с до supervisor cutoff. Caps stdout/stderr/export 16/1/8 MiB на строку, до 325 MiB членов плюс индекс при совокупном лимите 384 MiB. Runner сохраняет первопричину cutoff и `NOT_RUN` для корней, где запуск не состоялся. [Граница и сбор результатов](/root/kani-ch8-q-pilot-control-v12/ch8-q-pilot-control/run.py:299)

## Контракты и маршруты

- В wide при валидных guards каждый из семи затронутых контрактов имеет один активный `ensures` с одним `old` и один `modifies`. Presort и merge передают в `old` owned `Option` от снимка `Clone + Copy` по форме компилировавшегося sort9 Pilot 15. Legacy sort13 на `c8b703918a40c03d5b889d3018d8d818a70c233f` использует owned снимок `Clone + Copy` напрямую. Для Check/Replace insert tuple состоит из прежнего q-снимка inclusive span и `Option<bool>` числового снимка старого префикса. Оба компонента `Clone + Copy`. Wide step clauses объединяют byte, q и cursor предикаты, wide swap сохраняет byte post. Во всех корнях Pilot 16 эти листья исполняются actual. Legacy clauses совпали при статическом раскрытии guards. [Форма снимков Pilot 15](PILOT15-IMPL-HANDOFF.md#сверка-check-и-формы-контракта) · [Аннотации std](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:533)
- Presort проверяет точную пару типов, длину 9–12 или 13–16, читаемость всего span и writable prefix. Thin assigns ограничен первыми 9 или 13 элементами. Numeric order, сохранение `count(byte < q)` и q определяют пороговую маску. Семь covers и V34 frame у каждого Check проверяют тот же домен, включая хвосты будущих вставок. Numeric post insert поддерживает inclusive длины 10, 11, 12, 14, 15, 16. Старый q-монотонный Pre допускает инверсию внутри порогового класса. Левый Check ограничивает rel тремя значениями, правый задаёт литеральные указатели. [Wide модель](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:467) · [Корни insert](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1341)
- Merge проверяет читаемый initialized source, writable disjoint dst и отдельный числовой Pre обеих половин со split `len/2`. Capture читает только source. `modifies` охватывает ровно `dst[0..len]`. При `m=len/2` actual up пишет `0..m`, down пишет `len-m..len`, N25 дополнительно заполняет slot 12 через actual odd copy. Up выбирает левый при равенстве, down правый. Это противоположные концы порядка `(byte, индекс источника)`. За `m` пар они потребляют непересекающиеся части, а actual ord-guard проверяет финальные равенства курсоров. `u64` в формуле target вмещает `1 << 32`. При `below=32` маска нулевая, при `below=0` равна `u32::MAX`. Оба края покрыты отдельными covers. Пороговая проверка читает только активный выход после normal return, с индексами до 31. [Тело merge](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:1225) · [Check N32](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1487)
- В consumers capture берёт все исходные байты активного среза до вызова. N20 использует halves `v[1..11]` и `v[11..21]` с rel9 на обеих. N25 использует `v[1..13]` и `v[13..26]` с rel9–11 слева. Actual network сохраняет выбор половин, цикл вставки и copy-back. Native Replace Pre merge относится к числовому порядку того же состояния после presort и insert. После copy-back проверяются q-mask, q и outside frame. [Маршрут std](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:332) · [Consumers](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1543)

## Контроли и критерии квалификации

| Контроль | Ожидаемый native класс и source anchor |
| --- | --- |
| MW-N25-QPOST-CORRUPT | Единственная FAILURE `assertion` в `mw_network_n25_corrupt` с сообщением `MW_N25_CORRUPT_QPOST`. При нулевом span и q=1 после actual copy-back запись 255 в `v[1]` меняет младший бит ожидаемой нулевой маски. Capture valid, q/frame и два covers должны пройти. [Assert](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1621) |
| MW-N32-NUMERIC-PRE | Единственная FAILURE `assertion` от caller `requires(merge_halves_numeric_order)` в Replace `bidirectional_merge::<u8, KeyLess<u8>>`. При q=2 вход `[1, 0 × 31]` даёт q-монотонные половины и левую инверсию. Самостоятельный assert геометрии и три pre-call covers должны пройти. [Requires](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:1218) · [Вызов и fixture](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1640) |

Точные native ID с ordinal и экспортированные locations подтверждаются результатом запуска на этих pins. Для применения Check к Replace нужны совпадающие source/type/cfg, object bits, режим checks, геометрия обеих аллокаций, Pre/post/assigns, covers и основания для нужных U. Native SUCCESS зависимого consumer при cutoff его provider остаётся диагностическим. OFF включает memory/bounds/overflow/unwind, а native uninit/validity требуют matched ON. [Чек-лист qualification](QUALIFICATION-CHECKLIST.md)

Для единственного sort13 Check на 1800 с сравнить фазу, первую CNF, VT/child и effective/PGID/component RSS с Pilot 5 и 15. В случае solve timeout следующий замер следует развилкам задания 16, с раздельными numeric и q/footprint обязательствами либо с actual sort13 у N25 и свежим matched Check byte swap. Остальные exact геометрии N21–N24 и N26–N32, а также согласование N18/N19 на 11 битах остаются в плане покрытия. [Бюджет sort13](PILOT16-IMPL-TASK.md#бюджет-sort13-и-развилки) · [Порядок расширения](MERGE-WIDE-PLAN.md#порядок-расширения)

## Локальные проверки

- `validate` с синтетическими GitHub metadata подтвердил commit/tree/parent control, event/ref/attempt и SHA-256 payload. `check-source` подтвердил чистые std/tool checkout, оба commit/tree и восемь std SHA-256. `python3 -m unittest -v test_run.py` прошёл 14/14 на синтетических Python-процессах. Проверены 13 запусков в порядке roster, все четыре timeout/latest-start окна, exact argv и 11 бит, оба cap, artifact/capture, cleanup, drift, error paths и `NOT_RUN`.
- `git diff --check` прошёл. При исключении `cfg_attr` содержимое `smallsort.rs` побайтно совпало с базой. Активные clauses сверены для восьми legacy конфигураций и wide. Подтверждены literal call sites, список Check/Replace, `CAP=17`, маска N32 и предикаты обоих контролей. Python replay 2592 пар бинарных отсортированных половин N20–N32 проверил курсоры, запись каждого слота и пороговую маску как статическую сверку геометрии исходника.
- `rustfmt --check` из `nightly-2026-11-19` с `--edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features` прошёл на добавленных wide-блоках. Полные файлы дали код 1 с теми же 1/30/4 замечаниями, что и база. В `smallsort.rs` новых замечаний нет. Cargo, rustc, Kani, CBMC, CI и push не выполнялись. Компиляция, native outcomes, ресурсы и proof credit Pilot 16 остаются открытыми.
