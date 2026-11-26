# REV2 · опоры половин N26–N31

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`

Актуальные пины и повторная валидация приведены в [FIX1](#fix1). R1 получил GO с неблокирующими замечаниями. [Ревью R1](REV2-N26-N31-HALVES-REVIEW.md)

Один офлайн-пакет Ubuntu с шестью обязательными корнями S13. Правые вставки закрываются офлайн переносом с B17/L16 и индукцией по actual циклу. Состав зафиксирован до discovery. Нативные preflight, discovery и измерения этого пакета ожидают отдельного GO. Следующие пакеты покрывают merge pair, нечётный центр, copy-back, сквозные корни и контроли. [Задание](REV2-N26-N31-HALVES-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Базы

Задание g0 `13da20e6a37f5200d7618c85a9a2f9f52a7b0806`, blob `c5d431766d9d98e07c65f6970e993dd7ffae1541`. Входной HEAD g0 `e869692e3dd9aa7d92e90fe178d2f57ee03b0d19` содержит R2 GO для consumer FIX1. Пины задания совпадают с выбранным пакетом N22–N25 перед B. Std FIX1 `8fe1b01f0a85ee60118d1813d6b74645e4594213` / `f754c01d0ed26cb8d4e28c81efe8467cdf97d034`, Control FIX1 `fd941d949379ac437b9071cf9a1e636ae72aee5b` / `f4d42df994425e251022feeedcfd89e608b3d17a`. Отдельный pin предыдущего trigger требует тот же Control tree. В ledger записан фактический предшественник перед B, run `45829863637`. Локальный объект его payload `f898afc9baf7463e489d8414d20e4b08d135b6c8` имеет tree `f4d42df994425e251022feeedcfd89e608b3d17a` и sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Request и bundle совпадают с FIX1 по SHA-256 из GO. По ledger run завершился со статусом `success`, 8/8 `MATCHED`, `CONSUMER_PAIRS_WITHIN_PROFILE` и аттестацией `COMPLETE`. Порядок fork lane — consumer N22–N25 → B (ITER/SELECT) → A (валидность) → этот пакет. [FIX1 handoff](REV2-N22-N25-CONSUMER-HANDOFF.md#fix1) · [FIX1 GO](REV2-N22-N25-CONSUMER-GO.md) · [R2](REV2-N22-N25-CONSUMER-REVIEW.md#r2-после-fix1--go) · [Ledger](CH8-DISPATCH-LEDGER.md)

## Рёбра для actual половин

Домен — живой, инициализированный V34 с независимым `q: u8` и числовым `u8/KeyLess<u8>`. Активный срез `v[1..1+N]`, `N≥26` даёт `no_merge=false`. Actual `smallsort.rs:385:5` вычисляет `m=N/2`. Срезы создаются на `:391:31` и `:416:27`, обе длины проходят guard на `:395`, обе ветви вызывают S13 на `:396:13` и driver с offset 13 на `:405:9`. Половины смежны и не пересекаются. Срезы в таблице имеют исключённую верхнюю границу. `rel/abs` означает относительный индекс хвоста и его индекс в V34. [Actual caller](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort.rs:385)

| N | Левая половина, S13 и вставки | Правая половина, S13 и вставки |
| ---: | --- | --- |
| 26 | `v[1..14]` B01/L13. Exact B01 L13. `tail=end=14`. | `v[14..27]` B14/L13. B14 L14→L13. `tail=end=27`. |
| 27 | `v[1..14]` B01/L13. Exact B01 L13. `tail=end=14`. | `v[14..28]` B14/L14. Exact B14 L14. B17→B14, rel/abs 13/27, end 28. |
| 28 | `v[1..15]` B01/L14. B01 L17→L14. Первая итерация B01/L16, rel/abs 13/14, end 15. | `v[15..29]` B15/L14. B15 L15→L14. B17→B15, rel/abs 13/28, end 29. |
| 29 | `v[1..15]` B01/L14. B01 L17→L14. Первая итерация B01/L16, rel/abs 13/14, end 15. | `v[15..30]` B15/L15. Exact B15 L15. B17→B15, rel/abs 13–14/28–29, end 30. |
| 30 | `v[1..16]` B01/L15. B01 L17→L15. Первые две итерации B01/L16, rel/abs 13–14/14–15, end 16. | `v[16..31]` B16/L15. B16 L16→L15. B17→B16, rel/abs 13–14/29–30, end 31. |
| 31 | `v[1..16]` B01/L15. B01 L17→L15. Первые две итерации B01/L16, rel/abs 13–14/14–15, end 16. | `v[16..32]` B16/L16. Exact B16 L16. B17→B16, rel/abs 13–15/29–31, end 32. |

Левая половина использует `S13-BASE1-BITS`, `S13-B01-L17-BITS` и `S13-SWAP-LEAF`. Каждая правая строка использует свой Check на B14, B15 или B16 вместе с указанным битовым корнем. После нативного подтверждения этих корней перенос даёт порядок и полные кратности каждой половины перед merge, прежние q и frame снаружи обрабатываемой половины. [Принятый перенос B01](REV2-S13-LEFT16-REVIEW.md) · [Пороговый аргумент](REV2-S13-BINDING-DESIGN.md#перенос-на-произвольные-байты)

### Все 45 вызовов S13

Длина используется для guard `len >= 13` на `smallsort.rs:601:5`. После `:605:18` actual тело получает один указатель на начало среза. В порядке строк 612–656 каждая пара вызывает `swap_if_less` с этим указателем и тем же `KeyLess<u8>`. Ни одна пара не обращается к хвосту. Это обосновывает переносы B14 L14→L13, B15 L15→L14, B16 L16→L15 и B01 L17→L14/L15. [Actual тело](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort.rs:597)

У каждой строки два однобайтовых адреса `(base+a,base+b)` внутри соответствующего живого префикса. Они различны, выровнены для u8, инициализированы и доступны для чтения и записи через эксклюзивный срез. Сохранение инициализированности перед следующим вызовом следует из двух однобайтовых записей и frame. Для B01 та же замена даёт `(1+a,1+b)` в `[1,14)`. Таблица извлечена из actual исходника и сверена с `SWAP_PAIRS` FIX3 в исходном порядке. [Расписание FIX3](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:13)

| Строка `smallsort.rs` | `(a,b)` | B14 | B15 | B16 |
| ---: | --- | --- | --- | --- |
| 612 | `(0,12)` | `(14,26)` | `(15,27)` | `(16,28)` |
| 613 | `(1,10)` | `(15,24)` | `(16,25)` | `(17,26)` |
| 614 | `(2,9)` | `(16,23)` | `(17,24)` | `(18,25)` |
| 615 | `(3,7)` | `(17,21)` | `(18,22)` | `(19,23)` |
| 616 | `(5,11)` | `(19,25)` | `(20,26)` | `(21,27)` |
| 617 | `(6,8)` | `(20,22)` | `(21,23)` | `(22,24)` |
| 618 | `(1,6)` | `(15,20)` | `(16,21)` | `(17,22)` |
| 619 | `(2,3)` | `(16,17)` | `(17,18)` | `(18,19)` |
| 620 | `(4,11)` | `(18,25)` | `(19,26)` | `(20,27)` |
| 621 | `(7,9)` | `(21,23)` | `(22,24)` | `(23,25)` |
| 622 | `(8,10)` | `(22,24)` | `(23,25)` | `(24,26)` |
| 623 | `(0,4)` | `(14,18)` | `(15,19)` | `(16,20)` |
| 624 | `(1,2)` | `(15,16)` | `(16,17)` | `(17,18)` |
| 625 | `(3,6)` | `(17,20)` | `(18,21)` | `(19,22)` |
| 626 | `(7,8)` | `(21,22)` | `(22,23)` | `(23,24)` |
| 627 | `(9,10)` | `(23,24)` | `(24,25)` | `(25,26)` |
| 628 | `(11,12)` | `(25,26)` | `(26,27)` | `(27,28)` |
| 629 | `(4,6)` | `(18,20)` | `(19,21)` | `(20,22)` |
| 630 | `(5,9)` | `(19,23)` | `(20,24)` | `(21,25)` |
| 631 | `(8,11)` | `(22,25)` | `(23,26)` | `(24,27)` |
| 632 | `(10,12)` | `(24,26)` | `(25,27)` | `(26,28)` |
| 633 | `(0,5)` | `(14,19)` | `(15,20)` | `(16,21)` |
| 634 | `(3,8)` | `(17,22)` | `(18,23)` | `(19,24)` |
| 635 | `(4,7)` | `(18,21)` | `(19,22)` | `(20,23)` |
| 636 | `(6,11)` | `(20,25)` | `(21,26)` | `(22,27)` |
| 637 | `(9,10)` | `(23,24)` | `(24,25)` | `(25,26)` |
| 638 | `(0,1)` | `(14,15)` | `(15,16)` | `(16,17)` |
| 639 | `(2,5)` | `(16,19)` | `(17,20)` | `(18,21)` |
| 640 | `(6,9)` | `(20,23)` | `(21,24)` | `(22,25)` |
| 641 | `(7,8)` | `(21,22)` | `(22,23)` | `(23,24)` |
| 642 | `(10,11)` | `(24,25)` | `(25,26)` | `(26,27)` |
| 643 | `(1,3)` | `(15,17)` | `(16,18)` | `(17,19)` |
| 644 | `(2,4)` | `(16,18)` | `(17,19)` | `(18,20)` |
| 645 | `(5,6)` | `(19,20)` | `(20,21)` | `(21,22)` |
| 646 | `(9,10)` | `(23,24)` | `(24,25)` | `(25,26)` |
| 647 | `(1,2)` | `(15,16)` | `(16,17)` | `(17,18)` |
| 648 | `(3,4)` | `(17,18)` | `(18,19)` | `(19,20)` |
| 649 | `(5,7)` | `(19,21)` | `(20,22)` | `(21,23)` |
| 650 | `(6,8)` | `(20,22)` | `(21,23)` | `(22,24)` |
| 651 | `(2,3)` | `(16,17)` | `(17,18)` | `(18,19)` |
| 652 | `(4,5)` | `(18,19)` | `(19,20)` | `(20,21)` |
| 653 | `(6,7)` | `(20,21)` | `(21,22)` | `(22,23)` |
| 654 | `(8,9)` | `(22,23)` | `(23,24)` | `(24,25)` |
| 655 | `(3,4)` | `(17,18)` | `(18,19)` | `(19,20)` |
| 656 | `(5,6)` | `(19,20)` | `(20,21)` | `(21,22)` |

Check использует прежнее предусловие FIX3 и нативный `modifies` на двух адресах `smallsort.rs:467:1`. Геометрия дана на `rev2_provider_cost.rs:90–103` и требует, среди прочего, числовой компаратор нужной специализации. Actual `swap_if_less` на `smallsort.rs:488–519` читает оба значения, сравнивает `b<a`, и всегда записывает оба адреса через `ptr::copy` и `ptr::copy_nonoverlapping`. В отсутствие перестановки записи сохраняют те же значения, в том числе при равных байтах. `ptr::copy` допускает совпадение источника с первым адресом, второй источник — отдельный временный байт. Post Check и oracle harness проверяют min/max и q, frame проверяет все 32 остальные ячейки. Covers проверяют actual comparator, swap, no-swap, равенство на разных позициях, mixed q и нормальный возврат. [Actual Check и тело](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort.rs:467)

Битовый корень подаёт независимую 13-битовую маску в префикс. Остальные 21 байт, включая хвост среза, выбираются как произвольные полные u8. Каноничность и равенство ожидаемой маске `LOW_BITS ^ (LOW_BITS >> popcount)` задают порядок и исходное число единиц. Frame проверяет 21 байт и q. Нужны mixed, inversion, actual comparator и reached post. Для произвольного байта порог `P_t(x)=[x≥t]` превращает min/max в AND/OR на каждом шаге. Индукция по таблице отождествляет каждый пороговый след с битовой сетью. Если `x_i>x_j` при `i<j`, порог `x_j+1` дал бы инверсию. Счётчик единиц `C(t)=count(x≥t)` сохранён для каждого t, поэтому кратность b равна `C(b)−C(b+1)` при `b<255` и `C(255)` для 255. Сохранение q и frame следует отдельно из листа и битовых проверок. [Разбор переноса](REV2-S13-BINDING-DESIGN.md#перенос-на-произвольные-байты)

### Actual вставки и решение по roster

Обе исторические опоры N32 вызывают `insertion_sort_shift_left::<u8, KeyLess<u8>>` с тем же offset 13 на полностью инициализированном V34. Левая использует B01/L16, правая B17/L16. Перед шагом rel=r префикс `[base,base+r)` упорядочен, инициализирован и содержит исходные значения обработанных r позиций с их кратностями. Хвост `[base+r,end)` и V34 вне половины сохраняют исходные байты. Это верно при r=13 после S13.

- `begin=base`, `end=base+len` и `tail=base+13` образуются внутри одного живого среза и общей аллокации V34. `tail` разыменовывается только при `tail!=end`. Для L13 адреса равны сразу, поэтому driver возвращается без вызова `insert_tail`. L14/L15/L16 заканчиваются на собственном one-past-end после одного, двух или трёх шагов.
- Если байт в `tail` не меньше предшественника, ранний возврат удлиняет упорядоченный префикс без записей. Иначе `tail.read()` сохраняет байт в отдельном живом `ManuallyDrop` и образует gap на tail. На каждом сдвиге `[sift,sift+1)` копируется в соседний `[sift+1,sift+2)`. Источник и цель различны. Источник каждого сдвига инициализирован и лежит в `[begin, tail−1]`. Все цели сдвигов лежат в `[begin+1, tail]`. Затем gap переходит в sift. Проверка `sift==begin` выполняется до вычитания. Иначе поиск останавливается при первом predecessor ≤ tmp. Сдвигаются только байты, строго большие tmp.
- `CopyOnDrop` до возврата записывает tmp в последний gap. Tmp остаётся живым до Drop и находится в отдельном объекте, поэтому источник и назначение этой копии не пересекаются. В итоге `[base,base+r+1)` снова инициализирован, упорядочен и сохраняет кратности, а необработанный суффикс и все внешние ячейки неизменны. Этот промежуточный пост следует из шага индукции.
- `KeyLess::call_mut` читает операнды и сравнивает их через `<` независимо от q. Нативные драйверы проверяют итоговый порядок, `C(q)=count(x<q)`, q/V34 frame и normal return. Для одного и того же входа результат независим от q, значит `C(b+1)−C(b)` даёт кратность b при `b<255`, а `L−C(255)` — кратность 255. Для коротких путей тот же вывод следует из промежуточного поста после соответствующего шага. [Actual driver](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort.rs:742) · [Шаг вставки](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort.rs:701) · [Восстановление gap](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort.rs:357)

Слева B01/L14 и B01/L15 используют первые одну и две итерации исторического B01/L16 с теми же адресами rel13/14. Соответствующие порядки и кратности установлены индукцией для остановок на abs15 и abs16. Исторический B01/L16 проверяет итог после третьего шага. [Ревью коротких путей](REV2-N13-N16-OFFLINE-REVIEW.md)

Справа применяется внешний шаг композиции **external base translation + loop induction**. Инициализация правой половины, временного байта и источников чтения на каждом шаге установлена внешним аргументом при `uninit OFF` (`init external under uninit OFF`). Он использует инициализированный V34, диапазон источников сдвига и восстановление gap до перехода к следующей итерации. Каждый адрес `17+j` из исторической области B17/L16 заменяется на `B+j` для требуемых `0≤j≤len`. Сохраняются порядок, разность двух соседних адресов и внутрисрезовая принадлежность. Исторический one-past-end 33 заменяется на соответствующий `B+len` из таблицы рёбер, с которым сравнивается tail. Адрес tmp по-прежнему вне V34. Остальные ячейки V34 могут содержать произвольные байты и не участвуют в сдвиге. Для B16/L16 это перенос всего пути с той же длиной и offset, а для L14/L15 — перенос первых одного/двух шагов с собственным end. У исторического B17/L16 cover `REV2_N32_INSERT_SHIFT` подтверждает сдвиг только на rel13. Достижимость сдвига на rel14 и rel15 установлена офлайн. В качестве свидетеля достаточно 13 байтов со значением 3 и хвоста `2, 1, 0`. На каждом существующем шаге его байт строго меньше предшественника со значением 3. [Драйверы N32](REV2-N32-CONSUMER-RESULTS-ANALYSIS.md)

| Проверенный кандидат | Решение до заморозки |
| --- | --- |
| `INSERT-B14-L14-BYTES` | Не включён. Перенос B17→B14 и первый шаг закрывают N27 на end 28. N26 имеет пустой driver. |
| `INSERT-B15-L15-BYTES` | Не включён. Перенос B17→B15 и первые один/два шага закрывают N28 и N29 на end 29/30. |
| `INSERT-B16-L16-BYTES` | Не включён. Перенос B17→B16 и первые два шага закрывают N30 на end 31. Все три шага закрывают N31 на end 32. |

Каждый insert-edge обоснован на уровне исходника с исторической нативной опорой N32. У новых баз статус отдельного нативного driver — `NOT_RUN`. Финальный пост исторического L16 применяется к своему полному пути. Промежуточные посты коротких путей установлены изложенным инвариантом. К нативному `stub_verified(sort13_optimal)` допускает отдельная проверка целевого контракта или принятый нативный механизм передачи доказательства. [Правило композиции](REV2-COMPOSITION-RULE.md)

## Blobs и исторические свидетельства

| Файл | Blob на кандидате | Существенные координаты |
| --- | --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` | Drop `357–364`, caller `385:5, 391:31, 396:13, 405:9, 416:27`, swap `467:1, 468:1, 488:1, 495–518`, S13 `597:1, 601:5, 605:18, 612–656`, insert `701–735, 742–769`, verification gate `1075–1077` |
| `verify/cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` | Actual `call_mut` и comparator cover `26–30`, `28:9` |
| `core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` | `copy_nonoverlapping` `587:14`, overlapping copy `682:9` |
| `verify/rev2_provider_cost.rs` | `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` | FIX3 пары `13–59`, контракт `90–142`, Check `144–179` |
| `verify/rev2_s13_binding.rs` | `8718e67a68f473a6e7367d168a34410f40d324eb` | Actual B01/L13 `35:5`, посты `37:5, 38:5, 48:5, 53:5` |
| `verify/rev2_s13_geometries.rs` | `c403b343270752fb03fc087a101b55d8dc20a7ab` | Actual bit S13 `51:5`, посты `53:5, 54:5, 64:5, 69:5` |
| `verify/rev2_n32_consumer.rs` | `9a4dffb25fd63f5f40f73155a238dd77094fd8cf` | B01/B17 roots `72:1, 78:1`, pre `88:5`, actual `90:5`, посты `92:5, 93:5, 97:5, 98:5`, covers `102:5, 103:5` |
| `verify/rev2_n26_n31_halves.rs` | `92de2daf5b195e6340af59a8b9b7a1e0a22e8770` | Check actual вызовы `23, 47, 71`, bit actual вызов `96:5`, посты `98:5, 99:5, 109:5, 111:5, 122:5, 123:5, 129:9` |
| `smallsort/verify.rs` | `3b26f1440c5229a07c9ef92ac819f7222a02236e` | Новый cfg gate `239–257` |
| `core/Cargo.toml` | `6af630936fd4969e7ed8df54d6ce2b0e2eaed0d2` | Новый check-cfg `64` |

Первые три blobs совпадают на кандидате, FIX1 и всех исторических Std-пинах ниже. Blobs трёх исторических S13-модулей совпадают с собственными пинами. Исторический blob N32 — `7c7823d549dbd2203f3dd8f0b1307b618c474f53`. Последующая дельта касается сквозного битового корня и отдельного composite witness. Константы и весь блок byte drivers побайтно совпадают. Исторические B01/B17 roots на `66:1, 72:1`, pre на `82:5`, actual на `84:5`, посты на `86:5, 87:5, 91:5, 92:5`, covers на `96:5, 97:5`. В текущем файле эти строки сдвинуты на +6. Все старые модули, контракты и actual runtime побайтно сохранены от FIX1. [Исходники Std](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort.rs)

| Run / attempt | Std commit | Std tree | SHA-256 index.json |
| --- | --- | --- | --- |
| `45661535099/1` | `32129c149a15fb1b60a7314e738f3cb466d076e5` | `1b0cc32c571b370178e64f2b8c79773d2ce27051` | `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be` |
| `45676394046/1` | `32c2857f4b7137601de54ea42a02610c8fd29ed9` | `0e682cfceaed5d33d3d3374b5dc97da5012bba93` | `bcb05483715c3b6067586c26059f2b341f84b6c3a6b5ba7018db0395258f89d6` |
| `45688753097/1` | `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a` | `ff2563b5867b8327b95db909262ddf80e3ed9c03` | `e575daf8b20bab3c3023b8809e61cc21ea1a4bf9be85153d572368e6bbf663b7` |
| `45710831239/1` | `b93859fb447a39c0c8c7d854f70dedf9a47b263f` | `562a2fac5ed349a9fc09097789d0816f200c3819` | `9145808434de22a0cc31f8f15630c7510e723dd870862cb06d59d5624ce7bfa6` |

Exact исторические selectors имеют префикс `slice::sort::shared::smallsort::verify::`. Сверены SHA-256 структурированных receipts/projections по индексам. Все пять корней дали `VERIFIED`, exit 0, полную проекцию и подтверждённый reap. `MATCHED` есть у обоих битовых корней и обоих N32 drivers. Ранний FIX3 использует stock `COMPLETED/SUCCESS`. Оба N32 результата относятся к insert slots, а общий результат run включает отдельное ограничение на контрольном корне. [B01 и FIX3](REV2-N13-N16-OFFLINE-REVIEW.md) · [S13 геометрии](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md) · [N32](REV2-N32-CONSUMER-RESULTS-ANALYSIS.md)

| Слот | Selector, вид, covers | SHA-256 receipt / projection |
| --- | --- | --- |
| `S13-SWAP-LEAF` | `rev2_provider_cost::s13_swap_leaf`, Check `swap_if_less`, 6/6 | `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c`<br>`3f81b2c134cdba1348d9720fafb5569dbc37195693e47485c8bb1b80fe28d596` |
| `S13-BASE1-BITS` | `rev2_s13_binding::s13_base1_bits`, Proof, 4/4 | `66fbadf4bb9ef514bb367f35d50da6e2f421c17266aa3ca03f3228af12fd7ddd`<br>`33875cb4ad55dfa468410b6083fc3c92f50bf2b0359fe903c4013a62380a2bf2` |
| `S13-B01-L17-BITS` | `rev2_s13_geometries::s13_b01_l17_bits`, Proof, 4/4 | `119b822970d1386f3d15e5edefefaf847d4ee63a5358610f0bd9e22880c63c79`<br>`6c37276170ebe94470fa4a1d17b92bc09e05e5ac6b66d22aadd21508f255696a` |
| `N32-INSERT-LEFT-BYTES` | `rev2_n32_consumer::n32_insert_left_bytes`, Proof, 3/3 | `7cac457115063a8ffb3f46ff207c23f0361523a93c7d73395f6b7115639c4f4e`<br>`6b407b8d1f9e6ffa67786e07e06fd1a91e373f72527df8dd93bc9afbae0d3f40` |
| `N32-INSERT-RIGHT-BYTES` | `rev2_n32_consumer::n32_insert_right_bytes`, Proof, 3/3 | `3bcb3d314501ddb8d35bfc01396bfba094b2a65cd8ade7e54f4763ceac1b6a84`<br>`0a7a7f482845d9f4609b9a83b1856b12cc81489146693e39ab48dc7cc2946c25` |

Профиль исторических слотов — Ubuntu X64, stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC 6.11.0 / CaDiCaL 3.0.0, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, safety/overflow/unwind/undefined-function/assertion-reach ON, uninit/validity OFF. Пустые stub/Replace списки. Для N32 утверждения `check_insertions::<1/17>.assertion.3/.4/.5/.6` и grouped `copy_nonoverlapping::<u8>` на `ptr/mod.rs:587:14` имеют `SUCCESS`. В обоих insert roots покрыты actual compare, сдвиг на первом rel и возврат. [Индексы исторических корней](REV2-N13-N16-OFFLINE-HANDOFF.md#исторические-нативные-anchors) · [N32 индексы](REV2-N32-CONSUMER-RESULTS-ANALYSIS.md#что-приняли-из-run-45710831239)

В исторических receipts общая cfg-цепочка начинается с `kani_smallsort_cal1`, `kani_smallsort_cal2_merge_mask`, `kani_smallsort_rev2_provider_cost`. У BASE1 добавлен `kani_smallsort_rev2_s13_binding`, у L17 ещё `kani_smallsort_rev2_s13_geometries`, у обоих N32 drivers ещё `kani_smallsort_rev2_n32_consumer`. Effective cap всех пяти slots — 4 194 304 KiB. VT / cold wall у FIX3 составили 32,658 / 59,738 с, у BASE1 11,656 / 37,525 с, у B01/L17 13,645 / 41,734 с, у N32 left 8,391 / 35,727 с и у N32 right 9,159 / 35,129 с. Run 45710831239 дал `COMPLETE` аттестацию, при этом отдельный сквозной контроль упёрся в cap и итог пакета остался `UNMATCHED`. [N32 анализ](REV2-N32-CONSUMER-RESULTS-ANALYSIS.md)

## Замороженный roster

Точный префикс всех новых selectors — `slice::sort::shared::smallsort::verify::rev2_n26_n31_halves::`. Все корни имеют unwind 36, OB12, требуют `VERIFIED` / exit 0 и `MATCHED`. Для Check stock target — `ProofForContract(swap_if_less)`, discovery target — `slice::sort::shared::smallsort::swap_if_less` в `core/src/slice/sort/shared/smallsort.rs`. Для plain — `Proof` без contract target. Все шесть исполняют actual тела без stubs, Replace и loop contracts. [Модуль Std](/root/verify-rust-std-rev2-n26-n31-halves-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_n26_n31_halves.rs) · [Frozen request](/root/kani-rev2-n26-n31-halves-control-w15/ch8-cal1/CI-REQUEST.json)

| k | Слот | Суффикс selector | Вид | Домен | Latest start |
| ---: | --- | --- | --- | --- | --- |
| 0 | `S13-B14-SWAP` | `s13_b14_swap` | Check | B14, 78 допустимых пар в `[14,27)` | 3000 с / 50:00 |
| 1 | `S13-B14-L14-BITS` | `s13_b14_l14_bits` | Proof | `v[14..28]`, хвост `[27,28)` | 3205 с / 53:25 |
| 2 | `S13-B15-SWAP` | `s13_b15_swap` | Check | B15, 78 допустимых пар в `[15,28)` | 3410 с / 56:50 |
| 3 | `S13-B15-L15-BITS` | `s13_b15_l15_bits` | Proof | `v[15..30]`, хвост `[28,30)` | 3615 с / 60:15 |
| 4 | `S13-B16-SWAP` | `s13_b16_swap` | Check | B16, 78 допустимых пар в `[16,29)` | 3820 с / 63:40 |
| 5 | `S13-B16-L16-BITS` | `s13_b16_l16_bits` | Proof | `v[16..32]`, хвост `[29,32)` | 4025 с / 67:05 |

Stock объект Check связывается с нативным contract symbol через `single_top_level_call` и `no_recursive_call` специализации `swap_if_less::<u8, KeyLess<u8>>`. Успешный нативный post относится к `::{closure#2}.assertion.1` той же специализации. Write set привязан к `modifies` на `smallsort.rs:467:1` и к четырём `memmove.assigns.1/.2`, `memcpy.assigns.1/.2`. Групповые свойства проверяют условия двух видов копирования. В каждом Check anchors min/max, q, byte frame и covers привязаны к своему `assert_swap_post::<B>`. У Proof anchors включая q/V34 frame, каноничность, sorted popcount, mixed, inversion и reached post привязаны к `check_bits::<B, L>`. Оба вида требуют actual comparator cover на `cal1_model.rs:28:9`. Receipt хранит выбранные ID/location/status и stock cover IDs. Stock сверяет суммарное число успешных checks и ID остальных статусов по export. [Разбор нативных опор S13](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md)

## Профиль и часы

Одна `ubuntu-24.04` job с пределом 120 мин. Stock Kani и CBMC/CaDiCaL по профилю выше. На слот отдельные cold CWD, Cargo/Kani targets, TMPDIR и export. Пределы измерения — 180 с cold wall, 10 с reap, 5 с receipt, 10 с launch headroom, VT ≤120 с, группа ≤4 GiB, резерв машины 2 GiB. Сохраняется ограничение выборочного Linux RSS, который может быть занижен при смене worker TID. Checkpoint исхода и подтверждение reap предшествуют проекции. При неподтверждённом reap проекция пропускается и последующие слоты останавливаются. `finish` может восстановить отложенный receipt из bounded journal в пределах общего cutoff. Поздний receipt остаётся поздним, повторных запусков слота из recovery нет. Проекции до 4 MiB, общий артефакт до 96 MiB. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)

| Граница | Эпоха job + секунды | mm:ss |
| --- | ---: | ---: |
| Setup, включая compile preflight и оба discovery | 2940 | 49:00 |
| Входной gate и первый latest start | 3000 | 50:00 |
| Конец шести окон `6×205` | 4230 | 70:30 |
| Конец финальной аттестации | 4350 | 72:30 |
| Общий cutoff `finish` / `upload-gate` | 4645 | 77:25 |
| Абсолютный конец upload | 5070 | 84:30 |
| Конец резерва плана | 5610 | 93:30 |

Внутренний `measure` — 1415 с (23:35) от входа, включая до 60 с на входной gate, 1230 с окон, до 120 с на аттестацию и 5 с на journal. Внешний таймаут — 36 мин. `finish` ограничен 300 с от входа и общим cutoff. После общего cutoff предусмотрены 5 с на переход и до 420 с на upload. Таймеры и roster выведены из frozen request. Для `PROVIDERS_WITHIN_PROFILE` нужны все шесть exact слотов с полным своевременным receipt, нативными anchors, подтверждённым sampler/reap и выполненными лимитами, а также финальная аттестация `COMPLETE`.

## Пины R1

| Роль | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-n26-n31-halves-w15), `work/rev2-n26-n31-halves-w15` | `ea34c58ab95b4cbccd9acaa3080597b8b2517a87` | `75c4a374a0c906c989e2770a26990c7cdc6cdf83` | `8fe1b01f0a85ee60118d1813d6b74645e4594213` |
| [Control](/root/kani-rev2-n26-n31-halves-control-w15), `work/rev2-n26-n31-halves-control-w15` | `b22438e7bec284757a84e4da85bf959f6eec4617` | `22b10aa3749096a520f265b2e64f1b386f575250` | `fd941d949379ac437b9071cf9a1e636ae72aee5b` |
| [Detached review-trigger](/root/kani-rev2-n26-n31-halves-trigger-w15/control), ref `review/rev2-n26-n31-halves-trigger-w15` | `6161972f92c9e93c73459a17fc101a48dcec9327` | `22b10aa3749096a520f265b2e64f1b386f575250` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std CI-base — `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Все три коммита сверены до заморозки через `git show -s --format='%an <%ae> | %cn <%ce>'`. Автор и коммиттер каждого коммита — `Tiramisu-Cake <igkharin@gmail.com>`. Коммит handoff использует те же author и committer. Все новые сообщения содержат `[skip ci]` и используют форму идентификаторов без решётки перед цифрой.

Независимый pin R1 — `CH8_REV2_N26_N31_HALVES_TRIGGER_TREE=22b10aa3749096a520f265b2e64f1b386f575250`. Workflow передаёт его как `REV2_N26_N31_HALVES_TRIGGER_TREE` в `pins`, `sources` и `finish`. Gate принимает чистый detached checkout с этим tree, единственным ожидаемым parent и `HEAD == GITHUB_SHA == payload.after`. Дополнительные условия — `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1. `sources` и `finish` сверяют admission receipt. После сборки инструмента ранний compile preflight с первыми ошибками rustc предшествует cfg-off/on discovery. Дельта discovery ограничена тремя Check и тремя Proof с точным file, selector, kind и Check target. Прежний inventory сравнивается целиком по этим полям. [Workflow](/root/kani-rev2-n26-n31-halves-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-n26-n31-halves-control-w15/ch8-cal1/request.py)

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-n26-n31-halves-control-w15/ch8-cal1/CI-REQUEST.json) | `62aba9968f429c46cbcddc2485b1dfb8fdf99bb53560d4fa2a764746416a2564` |
| Roster, canonical JSON | `e097e28d327c11481824c7fd95df9c2be66936186b99b0da4a953c09c730b4c9` |
| [std-overlay.bundle](/root/kani-rev2-n26-n31-halves-control-w15/ch8-cal1/std-overlay.bundle), 46 832 байта | `2033e104fffe29918a14bb2e94b156999d532bb1673f4becf71d5a62f4da3588` |
| Source bindings, canonical JSON | `05b42ed7e1b159e493371b9366232e256221bdb8ba6c02562377069ef153b07c` |

Canonical JSON для двух digest использует сортировку ключей и разделители `(",", ":")`. Blob `ch8-cal1/test_supervisor.py` на обоих деревьях Control и trigger равен `df63a457c3adf648d360f3d559d5d40ef00a9427`.

## Локальная валидация R1

- Проверены Rust-видимость actual функций через `super::super`, доступность `KeyLess<u8>::with_q/q` из соседнего модуля, attrs, внешний `cfg(kani)` и цепочка cfg нового модуля. От FIX1 меняются только регистрация модуля, check-cfg и новый verification-only файл. Снятие вставок побайтно восстанавливает registry и manifest. Отдельный Python перебор 8 192 масок проверил 45 сравнений, извлечённых из actual расписания.
- `rustfmt --check` для нового модуля и registry прошёл бинарником nightly-2026-11-19 с `--edition 2024 --config use_small_heuristics=Max,skip_children=true,reorder_modules=false`. Прошли `git diff --check`, YAML с запретом дубликатов ключей, `bash -n` для восьми shell-блоков и Python AST для 15 файлов.
- На свежей bare shallow Std базе depth 2 без alternates прошли `bundle verify/list-heads/unbundle`. Prerequisite — Std CI-base, единственный объявленный HEAD — Std кандидата. HEAD, refs и shallow boundary совпали до и после импорта. Сверены 17 троек commit/tree/sole-parent, все авторства цепочки, cfg-off blobs, 100 source координат и 51 нативная координата. Каждая отдельная мутация столбца на +1 отклонена.
- Для синтетического replay на всех шести слотах использована форма свойств из структурированных исторических проекций B13 с заменой геометрии и координат. Получены шесть `MATCHED`, каждый отдельный сдвиг столбца провалил соответствующий replay. Эти fixtures проверяют парсер и привязки.
- На финальном detached trigger выполнен точный shell-блок `pins` с синтетическим GitHub payload. Прошли последовательно 118/118 тестов на обычной шкале и при старте с 1, 5 и 60 с. Время suite по порядку — 24,658 / 24,384 / 23,747 / 24,788 с. Полный shell-блок завершился за 100,149 с.
- Синтетика отклонила wrong tree/payload, неверный Check target/kind/file, чужой base и отдельно чужую длину при том же base, сдвиг столбца и потерю обязательного anchor/cover. Различены late receipt и неподтверждённый reap. Общий cutoff `finish`/`upload-gate` проверен с резервом 5 с на переход. Синтетический CLI `finish` и `upload-gate` отработали на допущенном trigger. Получены шесть `NOT_STARTED`, `PROVIDERS_OPEN` и девять членов индекса со сверенными размерами и SHA-256.
- Нативные compile preflight, discovery и измерения имеют статус `NOT_RUN`. Локальная работа выполнена без CI, push, изменений Actions variables и запуска cargo, rustc, Kani или CBMC.

## FIX1

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`

Выполнено задание g0 `5d59065e7d31aade0cc602c55f88c684f64e4328`. Для каждого из шести frozen half-root slots валидатор требует `copy_back=false`. Негативный тест меняет этот флаг на `true` у каждого слота. Второй тест принимает исходную проекцию `S13-B14-SWAP`, сдвигает якорь `ptr::copy_nonoverlapping::<u8>.precondition_instance.1` с `ptr/mod.rs:587:14` на `588:14` и требует `MISMATCHED` с неполными mandatory anchors. Дельта Control от R1 состоит из `ch8-cal1/results.py` и `ch8-cal1/test_results.py`. Офлайн-привязка правых вставок уточнена в разделе [Actual вставки](#actual-вставки-и-решение-по-roster). [Задание FIX1](REV2-N26-N31-HALVES-FIX1-TASK.md)

| Роль | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-n26-n31-halves-w15) | `ea34c58ab95b4cbccd9acaa3080597b8b2517a87` | `75c4a374a0c906c989e2770a26990c7cdc6cdf83` | `8fe1b01f0a85ee60118d1813d6b74645e4594213` |
| [Control FIX1](/root/kani-rev2-n26-n31-halves-fix1-control-w15), `work/rev2-n26-n31-halves-fix1-control-w15` | `302604ce810495c342282fba17cbdaea9aaf8cc5` | `b235397dd83b5ee85a53d56ebe40e01f547e8403` | `fd941d949379ac437b9071cf9a1e636ae72aee5b` |
| [Detached review-trigger FIX1](/root/kani-rev2-n26-n31-halves-fix1-trigger-w15/control), ref `review/rev2-n26-n31-halves-fix1-trigger-w15` | `e9e81a222ef86379c0cbbabbfb5580afda138468` | `b235397dd83b5ee85a53d56ebe40e01f547e8403` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Ожидаемый независимый pin для FIX1 — `CH8_REV2_N26_N31_HALVES_TRIGGER_TREE=b235397dd83b5ee85a53d56ebe40e01f547e8403`. Std, request, roster, source bindings, workflow и bundle побайтно совпадают с R1. Автор и коммиттер новых Control, review-trigger и g0 handoff — `Tiramisu-Cake <igkharin@gmail.com>`. Новые commit messages содержат `[skip ci]`.

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-n26-n31-halves-fix1-control-w15/ch8-cal1/CI-REQUEST.json) | `62aba9968f429c46cbcddc2485b1dfb8fdf99bb53560d4fa2a764746416a2564` |
| Roster, canonical JSON | `e097e28d327c11481824c7fd95df9c2be66936186b99b0da4a953c09c730b4c9` |
| [std-overlay.bundle](/root/kani-rev2-n26-n31-halves-fix1-control-w15/ch8-cal1/std-overlay.bundle) | `2033e104fffe29918a14bb2e94b156999d532bb1673f4becf71d5a62f4da3588` |
| Source bindings, canonical JSON | `05b42ed7e1b159e493371b9366232e256221bdb8ba6c02562377069ef153b07c` |

`test_supervisor.py` в Control и trigger имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Оба регрессионных теста прошли на FIX1. В изолированной копии восстановление проверки только на тип bool привело к отказу первого теста, а отключение сверки локации выбранного Check-свойства привело к отказу второго.

На финальном detached trigger прошёл точный shell-блок `pins` с синтетическим payload. На обычной шкале и свежих шкалах 1, 5 и 60 с последовательно прошли 120/120 тестов. Время suite по порядку — 30,082 / 32,145 / 41,278 / 48,737 с. Полный блок завершился за 155,420 с. Синтетические `finish` и `upload-gate` прошли, индекс содержит девять членов со сверенными SHA-256, для шести слотов записан `NOT_STARTED`.

Прошли YAML без дубликатов ключей, `bash -n` всех восьми shell-блоков, Python AST и `git diff --check`. Работа выполнена офлайн без CI, push, изменений Actions variables и запусков cargo, rustc, Kani или CBMC.
