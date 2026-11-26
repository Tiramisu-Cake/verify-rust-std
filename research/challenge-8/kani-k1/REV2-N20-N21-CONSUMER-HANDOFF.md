# REV2 · сквозные N20/N21 с контролями

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** Локальный Ubuntu-пакет из четырёх exact singleton. Для каждой длины positive проверяет все канонические входы, а контроль меняет первый активный байт после actual возврата и covers. У обоих корней одной длины общий helper, oracle и отдельные проверки q/V34 frame. Сквозные нативные результаты и допуск ожидают независимого ревью и отдельного GO. [Задание](REV2-N20-N21-CONSUMER-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Привязка сквозного маршрута

Общий домен внешнего вывода — инициализированный V34, полный `u8`, независимый `q: u8` и actual `small_sort_network::<u8, KeyLess<u8>>` на `v[1..21]` или `v[1..22]`. `KeyLess<u8>::call_mut` сравнивает байты числовым `<`. Состояние q не влияет на сравнение. [Actual маршрут](/root/verify-rust-std-rev2-n20-n21-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:367) · [Компаратор](/root/verify-rust-std-rev2-n20-n21-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)

| Ребро | Привязка к actual коду и опоре |
| --- | --- |
| Разбиение и sort9 | `smallsort.rs:385–416` даёт `len_div_2=10`, `no_merge=false`. На :399 обе половины идут в sort9, слева `v[1..11]`, справа `v[11..21]` у N20 и `v[11..22]` у N21. Guard :542, base :546 и все 25 пар :553–577 одинаковы внутри каждой геометрии переноса. |
| Левый presort | `S9-B01-L09-BITS` (`rev2_n18_n19_providers.rs:14`) переносится с len9 на len10 при base 1. FIX3 `S13-SWAP-LEAF` (`rev2_provider_cost.rs:146`) покрывает `0≤a<b<13` на той же базе, в том числе все rel0–8 sort9. Два выровненных живых адреса и write set пары сохраняются. Rel9 остаётся во frame. |
| Правый presort | `S9-B11-L11-BITS` и `S9-B11-SWAP` (`rev2_n20_n21_providers.rs:14,52`) exact для N21. У N20 перенос len11 → len10 сохраняет base 11, guard, все адреса rel0–8 и frame доступного среза. За пределами rel0–8 пары не читают и не пишут, включая rel10 у N21. Byte leaf даёт min/max, frame V34/q и точный write set на двух целевых адресах. |
| Вставки | Actual :405 вызывает `insertion_sort_shift_left` с offset 9. Driver :742–768 начинает с rel9 и доходит до one-past-end, вызывая `insert_tail` на :764. Для обеих длин `N20-INSERT-LEFT-BYTES` (`rev2_n20_n21_providers.rs:84–106`, вызов :91) соответствует `v[1..11]`, rel9/abs10. В `N20-N21-INSERT-RIGHT-BYTES` (:110) ветка `odd=false` (:147) даёт `v[11..21]`, rel9/abs20. Ветка `odd=true` (:119) даёт `v[11..22]`, rel9–10/abs20–21. Оба поста проверяют порядок, `count(<q)` и frame, справа также экстремумы. |
| Merge | Actual вызов :424 входит в цикл :1022–1025. `M20-PAIR-FIXED` и `M21-PAIR-FIXED` из run `45785063793` привязаны к своим N, `rev2_merge_pair_fixed.rs:147,186` и :271,310. В каждой паре actual up/down читают те же четыре фронта и копируют по одному байту на :885 и :918. Success anchors курсоров :165:9/:175:9 и :289:9/:299:9, значения и frame :245–248 и :369–372, точный двухбайтовый write set и grouped copy properties. |
| Copy-back | После нормального возврата :424 actual :425 вызывает `ptr::copy_nonoverlapping(scratch_base, v_base, len)` с exact `len=N`. На :383 отдельная writable scratch32, active V34 доступен для записи N байтов. `u8` имеет размер и выравнивание 1, обе области живы и disjoint. Инициализация ровно N читаемых байтов следует из безусловных записей рангов в scratch при `uninit/validity OFF`. Копия сохраняет q, `v[0]` и `v[1+N..34]`, а активный диапазон получает упорядоченное исходное мультимножество. |

Для presort `P_t(x)=[x≥t]` переводит min/max пары в AND/OR. Индукция по тем же 25 парам переносит результат битового sort9 на каждый порог. Числовая инверсия проявилась бы на пороге большего байта. Равенство пороговых счётчиков восстанавливает кратности, включая 0 и 255. Для вставок при фиксированных исходных байтах результат один для всех q. Если `C(q)=count(byte<q)`, кратность `b<255` равна `C(b+1)-C(b)`, а кратность 255 равна `len-C(255)`. Перед merge обе полные половины численно упорядочены и сохраняют исходные кратности. [Геометрии и anchors опор](/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/REV2-N20-N21-PROVIDERS-HANDOFF.md#presort-и-вставки)

### Ранги и нечётный центр

Пусть S — base активного диапазона, D — base scratch. Перед парой k счётчики `a,b` относятся к up и `c,d` к down слева/справа. Изначально все нули. При `a+b=c+d=k<10` четыре read-адреса `S+a`, `S+10+b`, `S+9-c`, `S+N-1-d` лежат в своих половинах. Applicability exact Check следует из этих границ, порядка половин, readable N, writable 32 и disjointness. Порядок по паре `(byte, индекс в S после вставок)` согласует tie-left для up и tie-right для down. Up идёт по этому порядку вперёд, down назад. Из записанных рангов `[0,k)` и `[N-k,N)` очередные min/max имеют ранги `k` и `N-1-k`. Они различны, хотя курсоры двух проходов могут читать один и тот же кандидат. Source frame сохраняет значения между проходами. Точный write set `D[k]`, `D[N-1-k]` сохраняет прежние записи и продвигает индукцию.

- N20 после десяти пар заполняет `D[0..10]` и `D[10..20]`. `a+c=b+d=10` даёт `left=S+a=S+10-c=left_end` и `right=S+10+b=S+20-d=right_end`. Odd branch пропускается, оба равенства проходят guard :1042.
- N21 заполняет `D[0..10]` и `D[11..21]`. Остатки `(10-a-c,11-b-d)` дают одну из двух веток. Для левого остатка все десять конфигураций имеют `(a,b,c,d)=(a,10-a,9-a,1+a)`, `0≤a≤9`, выбирают `S+a` и увеличивают `left`. Для правого остатка все одиннадцать имеют `(10-b,b,b,10-b)`, `0≤b≤10`, выбирают `S+10+b` и увеличивают `right`. Итого 21 конфигурация ранга 10, по одной на каждый исходный адрес в S. Это арифметическая сверка домена Check и фактической ветки.

`M21-ODD-CENTER` из `45772968167` использует локальный wrapper `rev2_n20_n21_providers.rs:371–394`. Как actual ветка :1027–1036, он вычисляет `left_end=S+10-c`, `right_end=S+21-d` через `wrapping_add(1)`, сравнивает `left < left_end`, выбирает `last_src`, копирует один байт в `D[10]` и двигает выбранный прямой курсор. В нативном Check прошли `SELECTED_SOURCE` :454:5, значение :455:5, оба терминальных равенства :456:5/:460:5 и frame :464:5/:465:5. При `c=10` получаем `a=0,b=10,d=0`, `left_rev=S−1`, `left_end=S` и источник `S+20`. `S−1` используется в wrapping-вычислении, копия читает правый остаток. Оба равенства :1042 следуют из выбранного остатка. [Сверка N19](/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/REV2-N18-N19-ADMISSION.md#нечётный-центр-n19) · [N21 wrapper](/root/verify-rust-std-rev2-n20-n21-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_providers.rs:371)

## Exact roots, пути и координаты

Модуль `rev2_n20_n21_consumer` зарегистрирован под inherited cfg и `kani_smallsort_rev2_n20_n21_consumer`. Префикс selector `slice::sort::shared::smallsort::verify::rev2_n20_n21_consumer::`. У положительных корней каждый из N битов независим. Все четыре корня получают произвольные байты вне active range и независимый q. Oracle проверяет одновременно каноничность и маску `LOW_N ^ (LOW_N >> popcount(input))` с младшим битом в `v[1]`. [Корни и helper](/root/verify-rust-std-rev2-n20-n21-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_consumer.rs)

| Слот | Suffix | Helper | Ожидаемый исход | Covers | Latest start |
| --- | --- | --- | --- | ---: | ---: |
| `N20-ACTUAL-BITS` | `n20_actual_bits` | `check_n20::<false>` | `VERIFIED`, exit 0, 2²⁰ входов | 5 | 50:00 |
| `N20-WITNESS-CORRUPT` | `n20_witness_corrupt` | `check_n20::<true>` | `FAILED`, exit 1, sole post failure | 5 | 53:25 |
| `N21-ACTUAL-BITS` | `n21_actual_bits` | `check_n21::<false>` | `VERIFIED`, exit 0, 2²¹ входов | 7 | 56:50 |
| `N21-WITNESS-CORRUPT` | `n21_witness_corrupt` | `check_n21::<true>` | `FAILED`, exit 1, sole post failure | 6 | 60:15 |

На `0x0007_fdff` обе половины имеют prefix9 из единиц и нулевой rel9. У N21 также нулевой правый rel10. На каждой стороне первая вставка сдвигает девять единиц. Вторая справа у N21 сдвигает именно девять единиц и останавливается у первого нуля, поскольку `0 < 0` ложно на actual проверке `insert_tail` :731. Поэтому одной метки `BOTH_RIGHT_SHIFTS` достаточно для этих двух сдвигов. У N20 пост ожидает `0x000f_fffc`, после `v[1] ^= 1` получается `0x000f_fffd`. У N21 down берёт девять правых единиц на ties и затем левую единицу, up берёт левый ноль, два правых нуля и семь левых единиц. Терминальные счётчики `(8,2,1,9)` оставляют левую единицу ранга 10 в `S+8`. Odd branch пишет её в `D[10]`. Oracle ожидает `0x001f_fff8`, после мутации наблюдается `0x001f_fff9`.

N21 positive отдельно покрывает `0x0000_03ff`. Слева десять единиц, справа одиннадцать нулей. Down берёт все десять левых единиц, up десять правых нулей. Со счётчиками `(0,10,10,0)` actual sentinel `left_rev=S−1` даёт `left_end=S` и выбор правого нуля из `S+20`. Этот cover привязан к входу после actual возврата, а исполнение odd branch следует из пути. [Actual insert_tail](/root/verify-rust-std-rev2-n20-n21-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:701) · [Actual odd branch](/root/verify-rust-std-rev2-n20-n21-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:1027)

| Суффикс literal-метки `REV2_N{N}_ACTUAL_` | N20 | N21 |
| --- | ---: | ---: |
| `AFTER_COPY_BACK` | 47:5 | 72:5 |
| `MIXED_INPUT` | 48:5 | 73:5 |
| `LEFT_FULL_SHIFT` | 49:5 | 74:5 |
| `RIGHT_FULL_SHIFT` / `BOTH_RIGHT_SHIFTS` | 53:5 | 79:5 |
| `ODD_LEFT_REMAINDER` | — | 81:5 |
| `ODD_RIGHT_REMAINDER_LEFT_REVERSE_SENTINEL` | — | 85:9 · positive |
| `Q_FRAME` | 57:5 | 90:5 |
| `V34_FRAME` | 58:5 | 91:5 |
| `CANONICAL_SORTED_POPCOUNT` | 60:5 | 93:5 |

Отдельный cover actual компаратора закреплён на `cal1_model.rs:28:9` для `KeyLess<u8>` как `FnMut`. Все обязательные regular anchors требуют точных файла, line, column, helper и статуса. Для положительных корней вместе с `AFTER_COPY_BACK` обязательны шесть успешных grouped свойств `ptr::copy_nonoverlapping::<u8>` на `ptr/mod.rs:587:14`. Это `.safety_check.1/.2`, `.arithmetic_overflow.1`, `.precondition_instance.1/.2/.3` с выравниванием, размером в байтах, disjoint/readable/writable. Группа покрывает вызовы с общим property ID. Actual :425 связывается с группой через достигнутый post-return cover, exact вызов и тот же pinned источник. Для контролей regular/stock должны согласовать один и тот же sole failure ID, класс `assertion`, литерал поста и файл/строку. Regular дополнительно фиксирует столбец и `check_nN::<true>`. Остальные failures запрещены, frame и обязательные covers должны пройти. [Frozen roster](/root/kani-rev2-n20-n21-consumer-control-w14/ch8-cal1/CI-REQUEST.json) · [Проверка результата](/root/kani-rev2-n20-n21-consumer-control-w14/ch8-cal1/results.py)

## Пины пакета

| Роль и worktree | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Вход g0 | `9c6f5b939f8481e0c0cc268d02cc308f3f1d6b45` | `26ed66048964b5dc6cae40e03ff27820d4e2b8b4` | `f48c39df1e2dd73e74ee2ea2616b500f2928de9a` |
| Std base | `f72f4303bacfff4706b20268a87b2a1031a8ee0b` | `03f9ce753b375729c2f8e53c18b2eaf7f3f07fc1` | `87ef4442ded137d2ee5f65bc29a4f87b8a3b69cd` |
| [Std](/root/verify-rust-std-rev2-n20-n21-consumer-w14) · `work/rev2-n20-n21-consumer-w14` | `000e6c4bf6ef0436e83e745618c077d988543169` | `c79edb9b6caf4734907f31590b782f2698b7e647` | `f72f4303bacfff4706b20268a87b2a1031a8ee0b` |
| Control base | `8e1603eef95407eaf03bb592266d7513540682f8` | `b4a386280f9a01b72e435ce0fe0546353fd757c4` | `c3108126877ae4e26c934bec638dca01d76546ba` |
| [Control](/root/kani-rev2-n20-n21-consumer-control-w14) · `work/rev2-n20-n21-consumer-control-w14` | `2404b83ff5adcc969939764f405670c00c0bfcaa` | `510af47eeb2689e8e27a20b44e881f5f624f00cf` | `8e1603eef95407eaf03bb592266d7513540682f8` |
| [Review-trigger](/root/kani-rev2-n20-n21-consumer-trigger-w14/control) · detached | `da69269470612c4a6db44fb89a2695f141c00e4f` | `510af47eeb2689e8e27a20b44e881f5f624f00cf` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Локальный ref `review/rev2-n20-n21-consumer-trigger-w14`. Ожидаемая независимая Actions variable `CH8_REV2_N20_N21_CONSUMER_TRIGGER_TREE=510af47eeb2689e8e27a20b44e881f5f624f00cf` передаётся как `REV2_N20_N21_CONSUMER_TRIGGER_TREE`. `pins`, `sources` и `finish` сверяют tree, clean detached checkout, exact SHA из push payload, fork `Tiramisu-Cake/kani`, ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1 и sole parent. `sources` и `finish` сверяют первичный admission receipt, upload требует успешных `pins` и `finish`. [Workflow](/root/kani-rev2-n20-n21-consumer-control-w14/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-n20-n21-consumer-control-w14/ch8-cal1/request.py:214)

Стартовая отсечка bundle — Std CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock tool — `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`. Принятый `ch8-cal1/test_supervisor.py` в обоих control trees имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427`.

| Замороженный вход | SHA-256 |
| --- | --- |
| `CI-REQUEST.json` | `d2b57b34b9e3bbd343ba45f9477588231912da4e5aac83cbac3981f52a43357c` |
| Canonical JSON roster | `988b517db4b5e008654ba01ca43b32562909396e9c14815abae2e3db50f0f288` |
| `std-overlay.bundle`, 39 548 байт | `c7b59bca9c2a79017477fdebfa42c2f638d4b942ce2d2678537d858bcbb08e72` |

| Pinned Std source | Blob |
| --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `library/core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `verify/cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` |
| `verify/cal1_q_merge_model.rs` | `d3c2a137f7332d79e7ce8596a517fd8b5f2dbe19` |
| `verify/rev2_provider_cost.rs` | `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` |
| `verify/rev2_n18_n19_providers.rs` | `9f5f22527656fd0b9b6afa879d7b8bb7574ff5c3` |
| `verify/rev2_n20_n21_providers.rs` | `c88c3a1240181b0949be7cd7154de20ff83304b3` |
| `verify/rev2_merge_pair_fixed.rs` | `b8580df3448e100d7ecb0811ebba0f14041ad412` |
| `verify/rev2_n20_n21_consumer.rs` | `a82bbf483c1d445dbdd6dacf4b5b12f3ac8dd7eb` |
| `smallsort/verify.rs` | `81ead461262ac23e27b360bfbb75f67a04f9e518` |
| `library/core/Cargo.toml` | `4414bf274b8a1c429c84f8b7084bb6d5184b1471` |

## Привязка исторических опор

Сверены exact Std commit/tree, stock tool, attempt 1 и trigger commit/tree/sole parent по четырём индексам. Их request, roster где поле опубликовано, и bundle закреплены в индексах. Для девяти перечисленных слотов сверены размеры и SHA-256 обоих структурированных членов, resolved unwind36 и CaDiCaL, OB12, CBMC 6.11.0, `uninit/validity OFF`, `VERIFIED`, exit 0, timely receipt, sampler, reap, полная projection и завершённая аттестация. Восемь новых относительно FIX3 имеют `MATCHED`. У FIX3 stock `COMPLETED/SUCCESS` с `ProofForContract(swap_if_less)`. Профили содержат свои cfg-префиксы, соответствующие каждому overlay. Runtime, ptr и comparator совпадают на всех четырёх пинах. Файлы опор совпадают с их историческими пинами. [Разбор FIX3 пар](REV2-MERGE-PAIR-FIXED-RESULTS-ANALYSIS.md) · [Разбор N20/N21](REV2-N20-N21-PROVIDERS-RESULTS-ANALYSIS.md)

| Run | Std commit / tree | SHA-256 индекса |
| --- | --- | --- |
| [45661535099](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/index.json) | `32129c149a15fb1b60a7314e738f3cb466d076e5` / `1b0cc32c571b370178e64f2b8c79773d2ce27051` | `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be` |
| [45749463113](/root/ch8-artifacts/run-45749463113/ch8-rev2-n18-n19-providers-Linux-X64-45749463113-1/index.json) | `86ea7aa5b773888e52f9fb78fda38d5cbff9ea61` / `63b199cc33052d6390fd0fdaa2b5c36962545fc4` | `065a9d8c2738117b36101eb7f3dcb5c8e568506c79b90b7953d561ae49d39504` |
| [45772968167](/root/ch8-artifacts/run-45772968167/ch8-rev2-n20-n21-providers-Linux-X64-45772968167-1/index.json) | `87ef4442ded137d2ee5f65bc29a4f87b8a3b69cd` / `832289728d493a114f89c318546c7e50d36f6d45` | `589ba3e863d61651dc6b644e53659864dbf8e75187e45cb7d0df60a0d46f4e37` |
| [45785063793](/root/ch8-artifacts/run-45785063793/ch8-rev2-merge-pair-fixed-Linux-X64-45785063793-1/index.json) | `f72f4303bacfff4706b20268a87b2a1031a8ee0b` / `03f9ce753b375729c2f8e53c18b2eaf7f3f07fc1` | `ded8803087eab9aedcc2bfcda6dd1d5184fc6e6b640f796bd206a391fc313c06` |

| Слот · run | Режим и covers | SHA-256 receipt | SHA-256 projection |
| --- | --- | --- | --- |
| `S13-SWAP-LEAF` · 45661535099 | Check `swap_if_less`, 6/6 | `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c` | `3f81b2c134cdba1348d9720fafb5569dbc37195693e47485c8bb1b80fe28d596` |
| `S9-B01-L09-BITS` · 45749463113 | Proof, 4/4 | `41e3435e50904c0cd683a7503a05d4428418557b3bfeddee95242d97c59551e3` | `46478975751c93569d9d1d0c681a9d623b2414db7129a1668e4ba05962649e48` |
| `S9-B11-L11-BITS` · 45772968167 | Proof, 4/4 | `cde14ec4b2d6f5a32cb14873a4e54345a47f6872f9d0f763af556c00af6efe5b` | `4e1009fd16e2cc534c6a921fdac2ee9668686ffe8ee0a7ad3f8ca0a47ae31e55` |
| `S9-B11-SWAP` · 45772968167 | Check `swap_if_less`, 5/5 | `6c3c1bd747f8a9c3b46e1e8ec0889abd31ce253bb4902f328af2fcdb55d7ff63` | `70de44ea12e3dc35542653f1118227d4d391dddd0f709398c7e0a9e964fd7c4c` |
| `N20-INSERT-LEFT-BYTES` · 45772968167 | Proof, 4/4 | `3d2fdc20c81702cceeca6aff39dda74836e0dc08cffca8c8fbe65272749d145a` | `461cb3ae48731661e1d43c1c0297df0411f3fb02bc7312b93dbebc827759f251` |
| `N20-N21-INSERT-RIGHT-BYTES` · 45772968167 | Proof, 9/9 | `ef2f3e284e5891b88fbc7bf9e0263ca652395c407910d76661d572c0f6ede207` | `799a9a9d55ca111bfcc380fb4a89d3983ddf45095a856fce90dd0360cd7aa46b` |
| `M21-ODD-CENTER` · 45772968167 | Check `actual_odd_center`, 4/4 | `be0768578749ba7ba273a2a5da135be402f3e26df5c0fbb5a76d19c3b388bcf5` | `dfade5a32d5f9d2d2b079c50772d7282dc306c0b6f4d124848fbc25ddc759b5d` |
| `M20-PAIR-FIXED` · 45785063793 | Check `actual_pair_step_n20`, 11/11 | `0265257bde45ae9795dc4970639f58f4483101ee46f64ac6f76bd29dc8dc7b73` | `4349b8235e167ee0a573bb8d35f3f87e73fb9bdb811df7332057b61fb1dfba32` |
| `M21-PAIR-FIXED` · 45785063793 | Check `actual_pair_step_n21`, 11/11 | `1c0f97dd8ca49d680e492c2c3f9de8e7fbf28bd5cb64331f5d5642fbe61264b1` | `1f6b561a96745d005b6b938edf65a25e8037f2c8cf68560535004d61f3da9241` |

## Профиль и приёмка

Одна job `ubuntu-24.04` на 100 мин. CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, safety/overflow/unwind/undefined-function/assertion-reach ON, uninit/validity OFF. Каждый слот имеет 180 с cold wall + 10 с reap + 5 с receipt, launch headroom 10 с. Cap группы 4 GiB, резерв доступной памяти 2 GiB, VT для отбора ≤120 с. Setup 50:00, четыре слота 13:40, post-attestation 2:00, finish 5:00, upload 7:00, резерв 9:00. План 86:40. Внешние таймауты pins/sources/prepare/measure/finish/upload равны 8/3/51/18/6/8 мин и покрывают внутренние окна, включая четыре watchdog suite по 90+5 с в pins.

Ранний compile preflight сохраняет первые rustc diagnostics. Оба списка discovery сверяют весь унаследованный инвентарь и требуют ровно четыре новых plain Proof на cfg-on. Слоты имеют отдельные cold target/temp/export. Атомарный checkpoint предшествует проекции, дедлайн и retry receipt ограничены. Проекция ≤4 MiB, артефакт ≤96 MiB. Итог каждой пары требует exact roster, финальной аттестации и обоих полных terminal projections, anchors, reap, sampler, timely receipt и измерений в профиле. Любой незакрытый слот оставляет свою пару `OPEN`. [Runner](/root/kani-rev2-n20-n21-consumer-control-w14/ch8-cal1/run.py) · [Сводка пары](/root/kani-rev2-n20-n21-consumer-control-w14/ch8-cal1/report.py:132)

## Локальная валидация

- Статически сверены видимость Rust, actual call sites, четыре пары атрибутов и весь inherited cfg. Delta Std включает только новый модуль, его gate и check-cfg декларацию. После снятия добавлений восстанавливаются исходные blobs registry/manifest. Runtime, контракты и опоры побайтно совпадают. `rustfmt --check` прошёл с `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max`. Registry проверен с `skip_children=true,reorder_modules=false`.
- Bare shallow Std depth 2 получен через локальный Git transport без alternates. `bundle verify/list-heads/unbundle` прошли, сверены 14 commit/tree/sole-parent, точный layout и 35 координат roster. HEAD, refs и shallow boundary сохранились. Каждый отдельный сдвиг столбца на +1 отклонён. Для bare-импорта проверки чистоты рабочих копий и submodules заменены прямой проверкой shallow base и объектов. YAML прошёл разбор с уникальными ключами, `bash -n` прошёл для шести shell-блоков, Python AST и проверка имён в runner/request/report/results прошли.
- Офлайн-сверка actual расписания проверила все 512 битовых префиксов sort9, три конкретных входа и все 21 терминальную конфигурацию N21. Синтетика отвергла неверную длину/специализацию, неверный или пропущенный столбец, потерю copy-back или odd cover, неверную привязку grouped properties, посторонний failure, late receipt и потерю reap.
- На финальном detached trigger точный блок pins завершился за 95,921 с. Suite прошёл последовательно на native / 60 / 5 / 1 с, каждый 113/113. Длительности 23,021 / 23,352 / 23,483 / 22,751 с. Отдельно на шкале 1 с synthetic push прошёл `pins` и `finish`, получены четыре `NOT_STARTED`, обе пары `OPEN`, три совпавших входных SHA-256 и семь проверенных членов индекса. `pins`, `sources`, `finish` отклонили tree базы, посторонний tree, старое имя переменной и подмену payload SHA. `sources` и `finish` также отклонили подменённый admission receipt. Всего 14 ожидаемых отказов.
- `git diff --check` прошёл для Std, control, trigger относительно sole parent и handoff. Коммиты локальные, с `[skip ci]`, автор Tiramisu-Cake. Push, CI, изменение Actions variables и локальные запуски cargo, rustc, Kani и CBMC отсутствуют.

Открыты нативная компиляция и cfg discovery, четыре терминальных результата и их ресурсы, actual copy-back group и post/frame на положительных корнях, matching sole failure на обоих контролях и итоговая аттестация. Допуск полного байтового вывода по композиции, `stub_verified` и допуск в pr752 требуют отдельного рассмотрения. [Правило допуска](/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/REV2-COMPOSITION-RULE.md)
