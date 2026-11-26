# REV2 · опоры N20/N21 (m=10)

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** Локальный пакет из шести последовательных слотов для Ubuntu 24.04. Домен — инициализированный V34, `u8/KeyLess<u8>` с числовым `<` и независимый `q: u8`. Нативная компиляция, измерения и результаты новых корней ожидают отдельного GO после независимого ревью. [Задание](REV2-N20-N21-PROVIDERS-TASK.md) · [Допуск N18/N19](REV2-N18-N19-ADMISSION.md)

## Presort и вставки

| Длина | Левая половина | Правая половина |
| --- | --- | --- |
| N20 · `v[1..21]` | `v[1..11]`. Перенос `S9-B01-L09-BITS` на len10 с FIX3 `S13-SWAP-LEAF`, затем `N20-INSERT-LEFT-BYTES` на rel9 / abs10. | `v[11..21]`. Перенос `S9-B11-L11-BITS` на len10 с `S9-B11-SWAP`, затем N20-ветка `N20-N21-INSERT-RIGHT-BYTES` на rel9 / abs20. |
| N21 · `v[1..22]` | Тот же `v[1..11]`, те же base, rel9 / abs10 и левый корень. | `v[11..22]`. Exact `S9-B11-L11-BITS` и `S9-B11-SWAP`, затем N21-ветка правого driver на rel9 / abs20 и rel10 / abs21. |

При `len_div_2=10` обе половины длиной 10 или 11 проходят guard `len>=9` и попадают в sort9, затем в driver с offset 9. На обеих базах sort9 получает `v.as_mut_ptr()` и исполняет это расписание в порядке исходника.

```text
(0,3) (1,7) (2,5) (4,8) (0,7) (2,4) (3,8) (5,6) (0,2)
(1,3) (4,5) (7,8) (1,4) (3,6) (5,7) (0,1) (2,4) (3,5)
(6,8) (2,3) (4,5) (6,7) (1,2) (3,4) (5,6)
```

Слева при len9 и len10 guard, base 1 и все 25 пар совпадают. Узел FIX3 покрывает `0≤a<b<13` на этой базе, включая весь домен пар `b<9`. Справа при len11 и len10 guard, base 11 и 25 пар также совпадают. Правый Check специализирует тот же `swap_if_less` на `u8/KeyLess<u8>` и base 11, проверяет min/max, native modifies двух адресов и V34/q frame. Все адреса имеют provenance живого V34 и выравнивание 1. Обе стороны оставляют rel9 и последующие байты во frame. Правый Proof оставляет произвольными abs20 и abs21. Rel10 отсутствует в расписании, поэтому перенос на правую len10 сохраняет тот же пост. [Actual dispatch](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:385) · [Guard и расписание](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:538) · [FIX3 leaf](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:143)

Проекция `P_t(x)=[x>=t]` переводит min/max каждой пары в AND/OR. Индукция по расписанию даёт битовую проекцию actual byte sort9 для каждого t. Битовый oracle `LOW9 ^ (LOW9 >> popcount(input))` упорядочивает девять канонических бит и сохраняет popcount. Байтная инверсия проявилась бы на пороге большего байта, а сохранённые пороговые счётчики дают все кратности. Поэтому byte driver получает ровно требуемый численно упорядоченный префикс длины 9 и произвольный хвост. [Предыдущая левая опора](REV2-N18-N19-PROVIDERS-RESULTS-ANALYSIS.md#что-закрыто-по-рёбрам) · [Правый корень](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_providers.rs:14)

Actual driver увеличивает `tail` от offset 9 до one-past-end. Для len10 выполняется одна вставка, для len11 две. У каждой первый compare с predecessor выполняется на входе `insert_tail`. У второй вставки в N21 границы уже обработанного префикса равны `min(before[11],before[20])` и `max(before[19],before[20])`. Поэтому covers rel10 различают истинные no-shift и full-shift, отдельно от covers rel9. Точные границы заданы actual срезами и внешними frame. Посты правых веток проверяют экстремумы, полный порядок, `count(<q)` и V34/q frame. Левый driver даёт те же order/count/frame для обеих строк на `v[1..11]`. Actual `KeyLess<u8>::call_mut` зависит только от сравниваемых байтов. Для фиксированного входного V34 результат driver один для всех q. При `C(q)=count(byte<q)` кратность каждого `b<255` равна `C(b+1)-C(b)`, а кратность 255 равна `len-C(255)`. [Actual driver](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:742) · [Actual компаратор](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)

## Десять пар и нечётный центр

Пусть S — начало `v[1..1+N]`, D — начало отдельного writable `MaybeUninit<[u8;32]>`. Перед парой k счётчики a,b описывают уже выбранные up байты слева и справа, c,d — down. При `a+b=c+d=k<10` четыре read-адреса `S+a`, `S+10+b`, `S+9-c`, `S+N-1-d` лежат в своих половинах. Обе цели `D[k]` и `D[N-1-k]` различны и попадают в scratch32. Modifies пары содержит ровно эти два адреса. Check вызывает actual `merge_up` и `merge_down` последовательно, сравнивает обе тройки курсоров, min/max и source/q frame. Up выбирает левую сторону на tie, down выбирает правую. Exact bounds, курсоры, записанные значения, frame и covers разделены по N. [Wrapper пары](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_providers.rs:180) · [Actual up/down](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:861)

Полный порядок на элементах — `(byte, исходный индекс)`. Каждая половина уже упорядочена по нему. При k=0 оба прохода начинают с пустых списков выбранных элементов. Если up ранее записал ранги `[0,k)`, его следующий минимум находится на одном из двух прямых фронтов и имеет ранг k. Если down записал `[N-k,N)`, его следующий максимум находится на одном из двух обратных фронтов и имеет ранг `N-1-k`. Tie rules совпадают с порядком по индексу. Source frame позволяет каждому проходу сравнивать исходные байты своих фронтов независимо от другого. При `k<10` ранги k и `N-1-k` различны, поэтому один элемент не выбирается дважды. Курсоры продвигаются в точности по выбранной стороне. Записи приходятся на новые ячейки scratch и сохраняют уже заполненные края. [Actual цикл](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:1013)

| Длина | Записи после десяти пар | Остаток и конечные курсоры |
| --- | --- | --- |
| N20 | `D[0..10]` и `D[10..20]`, все 20 рангов. | `a+c=10`, `b+d=10`. `left=S+a=S+10-c=left_end` и `right=S+10+b=S+20-d=right_end`. Guard допускает нормальный возврат. |
| N21 | `D[0..10]` и `D[11..21]`, свободен `D[10]`. | `(10-a-c,11-b-d)` равно `(1,0)` или `(0,1)`. Единственный оставшийся элемент имеет ранг 10. Odd branch записывает его и продвигает выбранный курсор до соответствующего end, после чего выполняются оба равенства guard. |

Локальный odd Check восстанавливает из терминальных счётчиков `left=S+a`, `right=S+10+b`, `left_rev=(S+9).wrapping_sub(c)`, `right_rev=(S+20).wrapping_sub(d)`, `dst=D+10`. В actual ветке на строках 1027–1036 и wrapper на 385–392 совпадают `wrapping_add(1)`, `left < left_end`, выбор `last_src`, копия одного байта и оба обновления. Oracle отдельно вычисляет индекс источника по целочисленному остатку и сравнивает его с возвращённым указателем. При `c=10` имеем `a=0,b=10,d=0`, `left_rev=S−1` и `left_end=S`. Sentinel используется только для wrapping-перехода. Копия читает `S+20`, а отдельный cover требует именно этот случай исчерпания левой половины. Native modifies ограничено `D[10]`. [Actual odd и guard](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:1027) · [Wrapper центра](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_providers.rs:367)

При `uninit/validity OFF` инициализация ровно 20 или 21 байта следует из безусловных actual копий известных живых байтов и точного write set. Merge читает S. Harness читает из scratch только соответствующие уже записанные ячейки. Grouped IDs покрывают вызовы с общим ID при достижимом normal return и успешных unwind/DFCC/safety checks. Actual copy-back и сквозной пост входят в следующий consumer-пакет. [Правило grouped свойств](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md) · [Actual копия назад](/root/verify-rust-std-rev2-n20-n21-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:425)

## Exact roster

Префикс selector — `slice::sort::shared::smallsort::verify::rev2_n20_n21_providers::`. Каждый слот ожидает `VERIFIED`, exit 0, `MATCHED`. Обязательные метки, точные строки и столбцы и anchors Check закреплены в [frozen request](/root/kani-rev2-n20-n21-providers-control-w14/ch8-cal1/CI-REQUEST.json).

| ID | Selector после префикса | Kind и цель | Latest start |
| --- | --- | --- | ---: |
| `S9-B11-L11-BITS` | `s9_b11_l11_bits` | Proof | 50:00 |
| `S9-B11-SWAP` | `s9_b11_swap` | Check `swap_if_less` | 53:25 |
| `N20-INSERT-LEFT-BYTES` | `n20_insert_left_bytes` | Proof | 56:50 |
| `N20-N21-INSERT-RIGHT-BYTES` | `n20_n21_insert_right_bytes` | Proof | 60:15 |
| `M20-M21-PAIR-STEP` | `m20_m21_pair_step` | Check `actual_pair_step` | 63:40 |
| `M21-ODD-CENTER` | `m21_odd_center` | Check `actual_odd_center` | 67:05 |

Для Check stock export фиксирует выбранную функцию, а regular связывает с ней `single_top_level_call` и `no_recursive_call` нужного target instance. Для swap закреплены FIX3 ensures, `memcpy.assigns.1/.2` и `memmove.assigns.1/.2`. Для пары и центра обязательны `memcpy.assigns.1/.2` и группы `ptr::copy_nonoverlapping::<u8>` в `ptr/mod.rs:587:14`. Это три `precondition_instance`, два `safety_check` и `arithmetic_overflow.1`. У пары оба actual вызова предшествуют per-N covers полезного возврата. Литеральные координаты wrapper-утверждений закреплены отдельно по N и привязаны к Check instance. [Native gate](/root/kani-rev2-n20-n21-providers-control-w14/ch8-cal1/results.py)

## Идентичности

| Роль и локальный worktree | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Задание в [g0](/root/verify-rust-std-kani3300-g0) | `78e47d827a1eff9e07fafed2aab36f05ef8ad5c9` | `5298edf5fc517e6b9a84aa869af6fa0d2b04d961` | `e6a6adae84aaeb68f2fbf8853e3f422623eb19d9` |
| Std base | `959087ac8632c68d8a6f0e28f58a8708475d564b` | `2123d3d5a77af26c6faf2d98d031904e75771300` | `a6f189eecbee57fe7517547bf7461c9dd2897e27` |
| [Std](/root/verify-rust-std-rev2-n20-n21-providers-w14) · `work/rev2-n20-n21-providers-w14` | `87ef4442ded137d2ee5f65bc29a4f87b8a3b69cd` | `832289728d493a114f89c318546c7e50d36f6d45` | `959087ac8632c68d8a6f0e28f58a8708475d564b` |
| Control base | `6a599af76402e61eef6746c32d7500b6ac101945` | `13057fe3d9479899217b3ab3b048d9a6571ec3a3` | `33db7a6351c4549098c52ce0e245fd072eb2152f` |
| [Control](/root/kani-rev2-n20-n21-providers-control-w14) · `work/rev2-n20-n21-providers-control-w14` | `414f0060c5eea9aded387c0431d9aae8b13a9870` | `bc097e25cfacdf059bf9c648022fb5f15bc6fed0` | `6a599af76402e61eef6746c32d7500b6ac101945` |
| [Review-trigger](/root/kani-rev2-n20-n21-providers-trigger-w14/control) · detached, ref `review/rev2-n20-n21-providers-trigger-w14` | `e69b5ed39f6350d0bdfbfec15c903dae38852d9a` | `bc097e25cfacdf059bf9c648022fb5f15bc6fed0` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`. Bundle объявляет один `HEAD` поверх shallow Std CI-base и включает 12 связанных overlay-коммитов.

| Pinned source на Std HEAD | Blob |
| --- | --- |
| `library/core/Cargo.toml` | `d6a3dfd8a380345aa1f3f9ead9c99f90c30a510a` |
| `library/core/src/slice/sort/shared/smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `smallsort/verify.rs` | `92bce8dda491da93311abb72bd4b1e9a0b396f72` |
| `verify/rev2_n20_n21_providers.rs` | `c88c3a1240181b0949be7cd7154de20ff83304b3` |
| `verify/rev2_n18_n19_providers.rs` | `9f5f22527656fd0b9b6afa879d7b8bb7574ff5c3` |
| `verify/rev2_n18_n19_consumer.rs` | `fa87c0d702815dbc9da4393d911bd32273de8c1f` |
| `verify/rev2_provider_cost.rs` | `c1f34296a2ff77b5f40f73155a238dd77094fd8cf` |
| `verify/cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` |
| `verify/cal1_q_merge_model.rs` | `d3c2a137f7332d79e7ce8596a517fd8b5f2dbe19` |
| `library/core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |

Actual `smallsort.rs`, компаратор и FIX3 contract model совпадают побайтно с `32129c149a15fb1b60a7314e738f3cb466d076e5` / `1b0cc32c571b370178e64f2b8c79773d2ce27051`. Левый S9 и N18/N19 consumer FIX1 привязаны к тем же blob, что и на входном Std. [Предыдущие нативные опоры](REV2-N18-N19-PROVIDERS-RESULTS-ANALYSIS.md) · [Пин FIX3](REV2-N17-HANDOFF.md#идентичность-источников-и-исторические-anchors)

| Вход | SHA-256 |
| --- | --- |
| [Frozen request](/root/kani-rev2-n20-n21-providers-control-w14/ch8-cal1/CI-REQUEST.json) | `d0228c3a68a32079783f0d2a1f9da39eb14a8c3dba91a1384eb5b99b64f48ad1` |
| Canonical JSON roster, сортированные ключи и разделители `(",", ":")` | `ff3cf539fa64d13ce785b5698a83e37dda731b7eb5ae197f7af41d84bafcc017` |
| [Std overlay bundle](/root/kani-rev2-n20-n21-providers-control-w14/ch8-cal1/std-overlay.bundle), 32 783 байта | `f93c1a4550244dd769c23fcda6a5010843ba85f3ebd4f90d636d813d68178367` |

Внешний pin `CH8_REV2_N20_N21_PROVIDERS_TRIGGER_TREE` для будущего запуска соответствует `bc097e25cfacdf059bf9c648022fb5f15bc6fed0`. Workflow передаёт его процессу через `REV2_N20_N21_PROVIDERS_TRIGGER_TREE`. Stages `pins`, `sources` и `finish` сверяют независимый tree, clean detached checkout, fork `Tiramisu-Cake/kani`, push exact ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, exact payload SHA и sole parent. `sources` и `finish` сверяют admission receipt. Upload требует успешных `pins` и `finish`. [Workflow](/root/kani-rev2-n20-n21-providers-control-w14/.github/workflows/ch8-q-pilot.yml) · [Gate](/root/kani-rev2-n20-n21-providers-control-w14/ch8-cal1/request.py)

## Профиль и бюджет

Одна job `ubuntu-24.04` на 100 мин. Stock Kani, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwinding, undefined-function и assertion-reach ON, uninit/validity OFF. Каждый слот имеет отдельные cold CWD, Cargo/Kani targets, TMPDIR и export. Cfg-off включает десять унаследованных флагов. Cfg-on добавляет `kani_smallsort_rev2_n20_n21_providers`. Overlay preflight до discovery сохраняет первые диагностики rustc. Exact discovery сверяет унаследованные корни и дельту из трёх Proof и трёх Check по selector/kind/file.

| Этап | Бюджет | Отсечка от epoch |
| --- | ---: | ---: |
| Setup, preflight и discovery | 50:00 | 50:00 |
| Шесть последовательных слотов | 20:30 | 70:30 |
| Итоговая аттестация | 2:00 | 72:30 |
| Finish | 5:00 | 77:30 |
| Upload | 7:00 | 84:30 |
| Резерв | 9:00 | 93:30 |

У слота 180 с cold wall, 10 с reap, 5 с receipt и 10 с launch headroom. Пределы VT 120 с, RSS группы 4 GiB, резерв 2 GiB, проекция 4 MiB, артефакт 96 MiB. Атомарный checkpoint сохраняет исход процесса и reap перед проекцией. Таймер receipt ограничен концом слота и пятью секундами после supervisor. Поздний receipt сохраняется с late flag, неподтверждённый reap блокирует следующие слоты. Проекция и итоговый отчёт сохраняют exact selector/kind, native ID/Location/Status, фазу/CNF, VT/wall, групповой и CBMC RSS, sampler и reap. При отсечке общего m=10 фаза и доступные метрики остаются в receipt для решения о разбиении. Критерий `PROVIDERS_WITHIN_PROFILE` — все шесть exact `VERIFIED` / exit 0 / `MATCHED`, mandatory covers, полные своевременные receipts и успешная финальная аттестация. Возможен недоучёт Linux RSS при смене worker TID. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md) · [Runner](/root/kani-rev2-n20-n21-providers-control-w14/ch8-cal1/run.py) · [Отчёт](/root/kani-rev2-n20-n21-providers-control-w14/ch8-cal1/report.py)

Внешние таймауты `pins/prepare/measure/finish/upload` составляют 8/51/25/6/8 мин, `sources` — 3 мин. Внутренний `measure` ограничен более ранней из общей границы и 1 415 с от начала шага. В 1 415 с входят 1 230 с слотов, 120 с аттестации, 5 с журнала и 60 с запуска входного gate. При ранней отсечке все latest starts сдвигаются с сохранением полного окна на слот. `finish` ограничен 300 с от входа в шаг и абсолютной границей 77:30. Бюджет `pins` на gate и четыре последовательных watchdog составляет 425 с из 480 с.

Ориентир для слота пары — прежний m=9 с VT 91,73 с, cold wall 124,56 с и пиком группы 2,46 GiB. Первая CNF имела 346 076 переменных и 1 972 867 дизъюнктов. Для m=10 действует тот же порог VT 120 с. [Замер m=9](REV2-N18-N19-PROVIDERS-RESULTS-ANALYSIS.md)

## Локальная проверка

- Вручную сверены видимость и cfg. `verify` объявлен под `cfg(kani)`. `super::super` разрешает private actual helper, `KeyLess<u8>` и `with_q/q` доступны дочернему модулю `verify`, `numeric_order` доступен внутри `smallsort`. Actual targets и FIX3 атрибуты совпадают с базой. Std diff содержит только harness, регистрацию и check-cfg. `rustfmt --check --edition 2024 --config use_small_heuristics=Max` прошёл на модуле, на registry с `skip_children=true,reorder_modules=false`. Использован `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt`.
- Извлечённые 25 actual пар проверены на 512/512 входных битовых масках. Локальный перебор проверил по 385 допустимых геометрий пары для каждого N, 4 356 и 5 148 отсортированных тернарных пар, все 11 и 21 терминальные комбинации курсоров и guard. Семь операций odd wrapper совпали с actual исходником после выравнивания отступов. Это статическая сверка привязки и индексной арифметики.
- Bare shallow Std depth 2 получен по локальному Git transport без alternates. `git bundle verify/list-heads/unbundle` прошли. До импорта overlay отсутствовал. После него сверены все 12 commit/tree/sole-parent, exact layout, шесть root-атрибутов и байтовое восстановление cfg-off registry/manifest. HEAD базы, refs и shallow boundary сохранились. На том же импорте `sources`-проверка приняла 92 координаты на шести строках и отклонила каждый отдельный сдвиг столбца на +1. Это 87 различных литеральных меток в новом Rust-модуле и отдельная метка actual FnMut на 28:9 в пяти слотах.
- YAML разобран с проверкой дублирующихся ключей, `bash -n` прошёл на шести shell-блоках, разобраны два вложенных Python-блока и Python control. Внешние таймауты сверены с внутренними бюджетами, включая 1 415 с для `measure`.

Полный синтетический suite пройден последовательно на четырёх шкалах.

| Шкала `monotonic` | Тесты | Wall |
| --- | ---: | ---: |
| Обычная | 109/109 | 32,68 с |
| 60 с + elapsed | 109/109 | 33,35 с |
| 5 с + elapsed | 109/109 | 33,69 с |
| 1 с + elapsed | 109/109 | 30,75 с |

Синтетика проверила exact roster, kind, файл и объект Check, неверную и отсутствующую колонку, потерю отдельного N/cover, compile preflight до discovery, cold paths, receipt deadline и потерю подтверждения reap. В первом проходе `test_escaped_descendant_is_killed_by_its_owned_pid` вернул `REAP_UNVERIFIED` вместо `TIMEOUT`. В финальной серии сбой не повторился. Отдельную стабилизацию supervisor self-tests ведёт w15. [Задание w15](REV2-SUPERVISOR-SELFTEST-TASK.md)

Detached review-trigger на шкале от 1 с прошёл `pins` и `finish` с синтетическим push payload. Получены шесть `NOT_STARTED`, `proof_credit=NONE`, `PROVIDERS_OPEN`, три подтверждённых входных SHA-256 и девять проверенных хэшей членов артефакта. `pins`, `sources` и `finish` отклонили tree базы, посторонний tree, прежнее имя переменной и подменённый payload SHA. `sources` и `finish` также отклонили изменённый admission receipt. Всего 14 ожидаемых отказов.

`git diff --check` прошёл для Std, control, review-trigger относительно его sole parent и handoff. Коммиты пакета локальные, с `[skip ci]`. Проверки этого этапа были статическими и синтетическими. Push, CI, изменения Actions variables и локальный запуск cargo, rustc, Kani или CBMC не выполнялись.
