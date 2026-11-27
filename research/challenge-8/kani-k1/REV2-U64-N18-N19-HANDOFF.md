# REV2 · полноширинные опоры сети u64 N18/N19

**FIX1 · `READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE` · Item 2.** Готовы три Check слияния и четыре plain Proof для sort9, правой вставки и swap на полном числовом `<`. Независимое ревью и отдельный GO координатора предшествуют публикации. Ubuntu compile preflight, фактический discovery и нативные исходы семи слотов открыты. [Задание w15](REV2-U64-N18-N19-TASK.md)

## Worktrees и входы

| Роль и рабочее дерево | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n18-n19-w15), `work/rev2-u64-n18-n19-std-w15` | `c8eefae4c8073cff31e5576b372d5105b52797a1` | `4f9687a4edccf69ef86ee8b4c2e01de9b3517539` | `eb5b697e44b1d0ca1acc4e5f14222ef50864af38` |
| [Control](/root/kani-rev2-u64-n18-n19-control-w15), `work/rev2-u64-n18-n19-control-w15` | `44aa6a2273588502083e47e204730dd67e0fba51` | `74f90d62acda5157906272454ec9d6c4bb9819db` | `d81a8587933a38aa05b9deb136878ec804c6852a` |
| [Review-trigger](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control), detached, ref `review/rev2-u64-n18-n19-fix1-trigger-w15` | `3a6597853af12e60526ea677d30a47c5e29df42c` | `74f90d62acda5157906272454ec9d6c4bb9819db` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Деревья исходных баз задания Std и Control соответственно `b1d2c899753acd6e137e9c10e153270f30a65846` и `fe9dfbd9a9670cc435190210578d68fa7e363f4e`. Bundle начинается от CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`, объявляет единственный `HEAD` и содержит 24 последовательных overlay-коммита. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`. [Проверка цепочки](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/run.py:145)

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/CI-REQUEST.json) | `b431696745a0a6f302bc696b657dab912d920c30fa757eaf1d0861d73d933caf` |
| Exact roster, канонический JSON | `2110ee3258b72773dc4edafc2795ed986808de7277d8a834c93099e820dfe0a3` |
| Source bindings, канонический JSON | `d243f3261469380a7928b2e0bec87c731ebbab5c213b17e87da245ea689590ca` |
| [std-overlay.bundle](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/std-overlay.bundle), 65 279 байт | `320e2eee02af5589a80be043d5746e1135f61ac687119c9f0f14f9c1dbdd674d` |
| [Workflow](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) | `6f6970f411ff0b2a9154abbeab62507979b94dbbb3a58d80cceafe01f41c58dd` |

| Исходник | Git blob |
| --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `verify/rev2_u64_n18_n19.rs` | `4ea168fc664f9f4733a80082af9cdd441f06a2ed` |
| `verify/rev2_u64_n14_n17.rs` | `0a23131ac174f4f7b6793823e49336c69397091f` |
| `verify/rev2_u64_n13.rs` | `47c129a11d6cd0d0adce0be450b91eca84a25c0c` |
| `smallsort/verify.rs` | `85c1bf874dd514a2ae9cf4959aac865d22bf2789` |
| `core/Cargo.toml` | `ddbec1f7f6ee2b416145d16ccd4dba8a7ce58504` |

Std добавляет модуль, две строки регистрации и одно check-cfg. Регистрация требует флаг N13 для видимого `pub(super) u64_less` и флаг N18/N19 внутри `cfg(kani)` на `smallsort.rs:1075`. Удаление добавленной регистрации и check-cfg побайтно восстанавливает файлы базы. Runtime, контракты и все прежние проверки побайтно совпадают с исходной базой Std N14–N17. Схема discovery сохраняет 103 прежние записи при cfg-off и добавляет ровно семь на cfg-on. Параметр `targets` пуст у plain, у трёх Check регистрируется единственная точная цель. Прежние записи сопоставляются вместе с видом, файлом и целями. [Гейт исходников](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/request.py) · [Discovery](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/run.py:254)

## Roster и привязка

Exact selector начинается с `slice::sort::shared::smallsort::verify::rev2_u64_n18_n19::`. Для всех строк ожидаются `VERIFIED`, exit 0, `copy_back=false` и все закреплённые covers. Stock проверяется на `Proof` или `ProofForContract.target_fn` по таблице. Вызовы существующих функций используют Original с `--no-assert-contracts`. Роли Replace, stubs и loop contracts отсутствуют. Координаты корней и обёрток относятся к [rev2_u64_n18_n19.rs](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n18_n19.rs).

| Слот | Суффикс selector, root | Check target, `cfg_attr` / `modifies` | Assertions / covers | Latest start |
| --- | --- | --- | ---: | --- |
| `U64-N18-PAIR-STEP` | `u64_n18_pair_step`, 64:1 | `actual_pair_step_n18`, 15:1 / 21:5 | 8 / 10 | 55:00 |
| `U64-N19-PAIR-STEP` | `u64_n19_pair_step`, 168:1 | `actual_pair_step_n19`, 119:1 / 125:5 | 8 / 10 | 58:25 |
| `U64-N19-ODD-CENTER` | `u64_n19_odd_center`, 266:1 | `actual_odd_center_n19`, 230:1 / 236:5 | 8 / 4 | 61:50 |
| `U64-N19-INSERT-RIGHT` | `u64_n19_insert_right`, 318:1 | Plain | 2 / 5 | 65:15 |
| `U64-S9-B01-L09-BITS` | `u64_s9_b01_l09_bits`, 358:1 | Plain | 3 / 4 | 68:40 |
| `U64-S9-B10-L10-BITS` | `u64_s9_b10_l10_bits`, 364:1 | Plain | 3 / 4 | 72:05 |
| `U64-S9-B10-SWAP` | `u64_s9_b10_swap`, 401:1 | Plain | 3 / 5 | 75:30 |

Запрос закрепляет полные метки, классы, file/line/column и native function. В таблице опущен общий префикс меток `REV2_U64_`. Assertions требуют `SUCCESS`, covers требуют `SATISFIED` в regular и соответствующий ID в stock. Применимые Check-утверждения курсоров выбираются по closure того же target, который Tool назначил Check. Все native unwind properties должны иметь `SUCCESS`, stock подтверждает сам unwind36 и включённые unwind checks. [Frozen roster](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/CI-REQUEST.json) · [Сопоставление regular и stock](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/results.py:234)

| Метки | Класс и точка привязки |
| --- | --- |
| `N13_COMPARATOR_CALLED` | cover `rev2_u64_n13::u64_less`, 9:5, у всех кроме odd-center |
| `N18_PAIR_UP_CURSORS`, `DOWN_CURSORS` | assertion `actual_pair_step_n18`, 43:9 и 53:9 |
| `N19_PAIR_UP_CURSORS`, `DOWN_CURSORS` | assertion `actual_pair_step_n19`, 147:9 и 157:9 |
| `N18_PAIR_` и `N19_PAIR_` + `READ_APPLICABILITY`, `WRITE_APPLICABILITY`, `DISJOINT_APPLICABILITY`, `UP_VALUE`, `DOWN_VALUE`, `SOURCE_FRAME` | assertion в соответствующем root, 71/75/79/104/105/106 и 175/179/183/208/209/210, столбец 5 |
| Те же pair prefix + `UP_TAKES_LEFT`, `UP_TAKES_RIGHT`, `DOWN_TAKES_LEFT`, `DOWN_TAKES_RIGHT`, `UP_TIE`, `DOWN_TIE`, `K_ZERO`, `K_LAST`, `RETURNED` | cover в соответствующем root, 107–115 и 211–219, столбец 5 |
| `N19_ODD_` + `READ_APPLICABILITY`, `WRITE_APPLICABILITY`, `DISJOINT_APPLICABILITY`, `SELECTED_SOURCE`, `VALUE`, `LEFT_CURSOR_END`, `RIGHT_CURSOR_END`, `SOURCE_FRAME` | assertion `u64_n19_odd_center`, 273/277/281/299/300/301/305/309, столбец 5 |
| `N19_ODD_` + `LEFT_REMAINDER`, `RIGHT_REMAINDER`, `LEFT_REVERSE_SENTINEL`, `RETURNED` | cover `u64_n19_odd_center`, 310/311/312/313, столбец 5 |
| `N19_INSERT_` + `EXACT_POST`, `V34_FRAME` и `NO_SHIFT`, `NINE_SHIFTS`, `AFTER_EQUAL`, `RETURNED` | assertion 347/352, cover 330/331/332/353, столбец 5 в `u64_n19_insert_right` |
| `S9_` + `CANONICAL_WORDS`, `SORTED_POPCOUNT`, `V34_FRAME` и `MIXED_INPUT`, `INPUT_INVERSION`, `RETURNED` | assertion 389/390/395, cover 377/378/396, столбец 5 в `check_sort9_bits::<1, 9>` или `::<10, 10>` |
| `S9_SWAP_` + `MIN`, `MAX`, `V34_FRAME` и `GREATER_INPUT`, `LESS_INPUT`, `EQUAL_INPUT`, `RETURNED` | assertion 418/419/424, cover 409/410/411/425, столбец 5 в `u64_s9_b10_swap` |

В каждом singleton Check изолированный selector, stock contract symbol и regular `single_top_level_call` / `no_recursive_call` на соответствующем `cfg_attr` закрепляют Check scope. Обязательные `memcpy.assigns.1/.2` класса `assigns` имеют builtin-координаты 46/47. Группа `ptr::copy_nonoverlapping::<u64>` включает `precondition_instance.1/.2/.3`, `safety_check.1/.2` и `arithmetic_overflow.1` на `core/src/ptr/mod.rs:587:14`. Для пары actual copy sites находятся на `smallsort.rs:885:9` и `:918:9`. Для центра сайт на `rev2_u64_n18_n19.rs:257:9` повторяет actual `smallsort.rs:1034:13`. Каждая копия передаёт `count=1`. Обязательные post и cover возврата фиксируют полезный путь через записи. Групповой ID относится ко всем достигнутым SSA-экземплярам в scope. Stock сохраняет статусы cover с ID и агрегированные счётчики успешных checks, regular сохраняет индивидуальные успешные ID. [Правило grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

Для правой вставки координаты shift, gap fill и intrinsic сохраняются в отдельных группах проекции (`:722:13`, `:362:13` и `ptr/mod.rs:587:14`). Требуются успешные typed safety groups для u64. Caller ID сохраняется при наличии точного места и функции в regular. Общий ID intrinsic даёт grouped-сверку, форматы caller ID устанавливаются на прогоне. Для sort9 и swap проекция сохраняет наблюдаемые семьи `ptr::copy::<u64>` и `ptr::copy_nonoverlapping::<u64>`.

## Поверхности и композиция

### Sort9 и вставка

`S=&v[1]` адресует инициализированный `[u64;34]`. В actual `small_sort_network` для N18 и N19 `len_div_2=9`, `no_merge=false`. Левый регион `v[1..10]`, правый `v[10..19]` у N18 и `v[10..20]` у N19. Guard на `:398` и `:542` пропускает все три региона. Все 25 вызовов `:553–577` используют одну базу `:546` и пары в rel0..8. Два битовых Proof устанавливают канонические полные слова, выходную маску с исходным popcount и скалярный внешний frame. Правый `v[19]` в Proof len10 произволен и входит во frame. При переходе len10 → len9 guard остаётся истинным, база B10 совпадает, все девять используемых адресов остаются валидными в том же backing. [Actual регионы](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort.rs:385) · [Sort9](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort.rs:538)

Для левых сравнений подходит допущенный `U64-N13-SWAP` с базой B01 и `b<13`, ограниченный парами `b<9` с теми же адресами и компаратором. Правый лист проверяет все `0≤a<b<9` на B10, min/max и равенство остальных 32 полных слов. Для каждого порога `t∈[0,u64::MAX]` имеем `[min(x,y)≥t]=[x≥t] AND [y≥t]` и `[max(x,y)≥t]=[x≥t] OR [y≥t]`. На всех 25 рёбрах проекция полного состояния на пороговые биты совпадает с битовой сетью. Инверсия полных выходных слов дала бы битовую инверсию на пороге большего слова. Сохранение числа единиц `C(t)` на каждом пороге сохраняет кратность слова `t` как `C(t)−C(t+1)` при `t<MAX` и `C(MAX)` при `t=MAX`. Скалярные frames каждой пары сохраняют позиции за rel8. [Допуск N13](REV2-U64-N13-ADMISSION.md) · [Actual swap](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort.rs:488)

Actual driver на `:405` получает offset 9. У двух сторон N18 и слева N19 `tail=v_end` сразу. Справа N19 `:759–760` вычисляют `v_end=&v[20]`, `tail=&v[19]` от `v_base=&v[10]`. На `:764` вызывается ровно один `insert_tail`, после `:767` `tail==v_end`. Для отсортированного префикса и полного `x=before[19]` элементы `≤x` составляют единственный начальный отрезок длины `p∈0..=9`. Точный пост сохраняет прежнее слово при `j<p`, кладёт `x` при `j=p`, копирует прежнее `j−1` при `p<j≤9`. Эта карта сохраняет полные кратности и порядок с местом после равных. Слово `x` включено ровно один раз. Остальной V34 сохраняется. Covers проверяют границы p, внутреннюю вставку после равного слова, компаратор и возврат. [Actual driver и insert_tail](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort.rs:701) · [Plain Proof](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n18_n19.rs:318)

На `:722` источник `sift` и зазор `gap_guard.dst` соседние, `dst=sift+1`. Первый шаг читает rel8 и пишет rel9, крайний при `p=0` читает rel0 и пишет rel1. При девяти сдвигах байты источников внутри V34 лежат в `[80,152)`, байты целей в `[88,160)`, для каждой индивидуальной копии два 8-байтовых интервала раздельны. На `:715–716` отдельный живой `tmp` получает x, guard с `len=1` заполняет последний зазор rel p из `tmp` на `:362`. Внешний вывод об инициализации следует из начальной инициализации, порядка чтения предшественников и Drop. При `p=9` `:707` возвращается до первого сдвига. Этот лист связан с driver на B10/r=9 из нового пакета.

### Шаг пары, адреса и нечётный центр

На Ubuntu X64 модуль статически проверяет `size_of=align_of=8`. V34 занимает 272 байта. N18 занимает `[8,152)` в V34 и `[0,144)` от S, N19 соответственно `[8,160)` и `[0,152)`. Половины занимают `[0,72)` и `[72,144/152)` от S. D32 выделен отдельно, выровнен на 8 и занимает `[0,256)` от D. Check требует readable активный срез, writable всё D32 и разные allocations. У fixture source инициализирован полностью, `k,a,c` вводятся независимо как u8 с приведением к usize и ограничениями `0≤a,c≤k≤8`. Предпосылка порядка относится к внешней композиции. Локальные min/max, значения и курсоры проверяются на произвольных полных словах. Раздельность закреплена непосредственно через `same_allocation`, чтобы область Check охватывала отдельный D32 целиком. Нативные slot IDs для N18 и N19 привязаны к разным целям без параметра длины с литеральными смещениями.

В таблице `[i,j]` — включительно для возможных смещений указателей, `[b,e)` — байты затрагиваемых слов. Для каждого чтения или записи с элементным смещением x область равна `[8x,8x+8)` от соответствующей базы.

| Ребро шага при `b=k−a`, `d=k−c` | N18, элементы / байты от S или D | N19, элементы / байты от S или D |
| --- | --- | --- |
| up left `S+a`, down left `S+8−c` | [0,8] / [0,72) | [0,8] / [0,72) |
| up right `S+9+b` | [9,17] / [72,144) | [9,17] / [72,144) |
| down right `S+N−1−d` | [9,17] / [72,144) | [10,18] / [80,152) |
| up write `D+k` | [0,8] / [0,72) | [0,8] / [0,72) |
| down write `D+N−1−k` | [9,17] / [72,144) | [10,18] / [80,152) |
| up next left / right | [0,9] / [9,18], байтовые адреса 0..72 / 72..144 | [0,9] / [9,18], 0..72 / 72..144 |
| down next left / right | [−1,8] / [8,17], −8..64 / 64..136 | [−1,8] / [9,18], −8..64 / 72..144 |
| next up / down destination | [1,9] / [8,16], 8..72 / 64..128 | [1,9] / [9,17], 8..72 / 72..136 |

Check вызывает up на `D+k`, затем down на `D+N−1−k`. Один и тот же read-адрес двух направлений допустим. Up выбирает левую сторону при равенстве, down правую. У исходных тел та же ветвь задаёт адрес копируемого слова и продвигаемый source cursor. Assert курсоров проверяет все шесть адресов. Fixture читает из scratch две доказуемо записанные ячейки, проверяет два скалярных u64 и 34 слова source frame. `modifies` содержит только две u64-ячейки D. Следующие граничные курсоры соответствуют началу соседней половины, позиции за логическим входом N18 или `S−1`. Они остаются в backing и участвуют в адресной арифметике. `S−1` вычисляется wrapping и соответствует `&v[0]`. [Up](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort.rs:883) · [Down](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort.rs:916)

| Ребро центра после 9 пар | Левый остаток | Правый остаток |
| --- | --- | --- |
| Счётчики | `a=0..8, b=9−a, c=8−a, d=1+a` | `a=0..9, b=9−a, c=9−a, d=a` |
| Остатки | `(1,0)` | `(0,1)` |
| Прочитанное слово | `S+a`, покрытие [0,72) | `S+18−a`, покрытие [72,152) |
| Цель и объём | `D[9]`, [72,80), один u64 | `D[9]`, [72,80), один u64 |
| Конечные left/right относительно S | `a+1` / `18−a` | `a` / `19−a` |
| Особая граница | При `a=8` left доходит до `S+9` | При `a=0` left_rev равен `S−1`, left_end равен S, right_end равен `S+19` |

Для odd-center отдельная обёртка воспроизводит `:1027–1036`. Она строит `S.add(8).wrapping_sub(c)` и `S.add(18).wrapping_sub(d)`, затем оба end через `wrapping_add(1)`. В sentinel-состоянии `S−1` используется только для wrapping. Из `left_nonempty` следуют выбранный source и продвигаемый курсор. Fixture проверяет сам адрес, полный u64, оба равенства `:1042` с ожидаемыми end-адресами и source frame. `modifies` ограничен `D[9]`. Компаратор в этом пути отсутствует. [Actual нечётная ветвь](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort.rs:1027) · [Check центра](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n18_n19.rs:230)

### Ранговая индукция до записи D

Упорядочим записи по `(полное значение, индекс после вставок)`. Внутри каждой отсортированной половины это тот же порядок, что и последовательность адресов. Между половинами tie-left у up выбирает меньший индекс, tie-right у down — больший. Перед парой k начала сняли `a+b=k` наименьших рангов, концы `c+d=k` наибольших. Эти два множества лежат в `D[0..k]` и `D[N−k..N]` в ранговом порядке. При k<9 остаётся минимум два ранга. В непустой половине direct/reverse кандидаты — её крайние оставшиеся ранги. Если половина исчерпана, равенство суммы её счётчиков длине и валидность обоих read-адресов означают, что direct-кандидат уже снят сверху, reverse-кандидат уже снят снизу. Они проигрывают соответствующее сравнение всем оставшимся рангам. Поэтому up/down выбирают разные крайние ранги k и N−1−k даже при равных значениях. Раздельные цели оставляют прежние края D целыми. Actual `:1014–1024` даёт базу k=0 и тот же шаг девять раз.

После девяти пар в N18 получаем `a+c=9`, `b+d=9`. При продвижении reverse на один `S+a=S+9−c`, `S+9+b=S+18−d`, то есть оба равенства `:1042`. Для N19 остаётся ровно один ранг 9, и нечётный Check записывает его в `D[9]` и доводит оба курсора до end. Тем самым до чтения полностью записано `D[0..N]`. Инициализация — внешний вывод о конкретной последовательности записей при uninit OFF. [Индукция для прежней геометрии](REV2-N26-N31-MERGE-ADMISSION.md#привязка-нативных-опор-к-actual-циклу) · [Actual merge loop](/root/verify-rust-std-rev2-u64-n18-n19-w15/library/core/src/slice/sort/shared/smallsort.rs:1014)

## Циклы и unwind36

Ревью R1 на N13 выявило развёртку `memcmp` по 160 байтам при unwind36. Сравнения нового модуля используют отдельные u64. [Исправление N13](REV2-U64-N13-REVIEW.md#r2--fix1)

| Цикл или примитив | Верхняя граница и видимость для кодогенерации |
| --- | --- |
| `source_frame` двух pair и odd, модуль `:224` | 34 скалярных сравнения, литеральный `0..34`. |
| Порядок, partition p, exact mapping и внешний frame вставки `:324/327/337/349` | 8 / 9 / 10 / 34 итерации. Все ranges литеральны, p выбирает ветку и адрес слова. |
| Запись битов, проверка каноничности/маски и frame S9 `:372/384/392` | 9 / 9 / 34. Литеральные ranges для каждой мономорфизации, BASE и LEN — константы. |
| B10 swap frame `:421` | 34, литеральный `0..34`. Символические a/b выбирают два исключения. |
| `Range::next` и `Range::contains` | У `next` один скалярный шаг на итерацию вышеперечисленных конечных циклов. `contains` даёт два сравнения границ и выполняется без отдельного цикла. Индексирование диапазона и скаляра проверяет границы без сканирования среза. |
| `kani::any::<[u64;34]>`, снимок и сравнения | Stock специализация `Arbitrary::any_array` для u64 вызывает `any_raw::<[u64;34]>` напрямую. Снимок — Copy фиксированных 272 байтов. Сравниваются скалярные u64. В этих постах отсутствует путь через `memcmp`. `u16::count_ones` использует `ctpop` ширины 16. |
| Actual driver и `insert_tail`, `smallsort.rs:761/718` | Driver выполняет одну итерацию при фиксированных len10/offset9, встроенное `insert_tail` до девяти сдвигов с перемещением зазора от `S+18` к `S+9`. При потере видимости границ в MIR или symex бюджет кодогенерации учитывает unwind36 на каждом из этих циклов. |
| Actual S9, swap, Drop, up/down, odd wrapper, указатели и предикаты памяти | Фиксированные 25 вызовов S9 развёрнуты в исходнике. Другие перечисленные тела и обёртки не содержат Rust-циклов. У CBMC 6.11.0 `memcpy` использует `array_copy` и `array_replace`. Модель работает над 8 байтами на каждый `count=1`. `ptr::copy` в swap тоже переносит одно слово. |
| DFCC `write_set_check_assignment` и `write_set_record_deallocated` | `cprover_contracts.c:837–849` и `:740–750` сканируют `contract_assigns.max_elems`. Конструктор write set получает два targets в pair и один в odd, а трасса может задействовать пустой окружающий set. Число берётся из полей DFCC, поэтому при отсутствии статического сокращения учитывается unwind36. Check требует наличия нативных unwind assertions по форме FIX3 и успеха всех выведенных, включая builtin. |
| Actual caller и `bidirectional_merge`, `smallsort.rs:394/1022` | В композиции выполняются две итерации по половинам, девять по парам и условная прямая ветвь центра. Это рёбра внешнего вывода. В код с семью текущими корнями циклы caller и общего merge не входят. |

## Ubuntu job и сроки

Один `ubuntu-24.04` X64 job на 100 мин. CBMC 6.11.0/CaDiCaL, OB12, unwind36, safety/overflow/unwinding/undefined-function/assertion-reach ON, uninit/validity OFF. Check и plain используют общую схему argv. `RUSTFLAGS` задаёт все 22 cfg из roster в указанном порядке, последним `--cfg=kani_smallsort_rev2_u64_n18_n19`. У каждого слота отдельные холодные CWD, Cargo target, Kani target, tmp и export. `KANI_JOBS=1`, `CARGO_TARGET_DIR=$slot/cargo-target`, `TMPDIR=TMP=TEMP=$slot/tmp`. [Формирование argv](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/run.py)

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Prepare запускает cfg-on preflight после сборки и проверки stock tool и checkout overlay, перед discovery. В preflight предел 180 с, тот же набор `-Z` и `--no-assert-contracts`, параметры `--no-codegen --only-codegen --quiet`, отдельный target и запись первых rustc diagnostics при отказе. Native list выполняется с последним cfg выключенным и включённым. [Prepare](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/run.py:423)

| Стадия | Абсолютная граница от monotonic epoch | Внешнее окно |
| --- | --- | --- |
| Prepare | 54:00 | 56 мин |
| Measure identity gate | до 55:00 и до 60 с от входа | в measure |
| 7 слотов по 205 с | конец 78:55 | measure 29 мин, внутренний 27:00 |
| Финальная аттестация | до 80:55 | в measure |
| Finish и upload-gate | cutoff 85:50, finish в пределах 5 мин от своего входа | 6 мин и 1 мин |
| Upload и проверка конца | до 92:55 | 7 мин |
| План с резервом 6 мин | 98:55 | job 100 мин |

На слот VT ≤120 с, group RSS ≤4 GiB, cold wall ≤180 с, reap 10 с, receipt 5 с и launch headroom 10 с. Supervisor держит 2 GiB системного резерва. Внутренний measure может сдвинуть latest starts раньше при сохранении полной длительности слота. Checkpoint сохраняет исход процесса и reap до проекции. При неподтверждённом reap остающиеся слоты останавливаются. Отложенный receipt повторяется в ограниченном окне finish с сохранённой отметкой об опоздании. Caps проекции и артефакта 4/96 MiB. Публикуются последняя фаза, первая CNF, VT, cold wall, group/CBMC RSS и PSS по доступным выборкам. При смене TID после выхода основного потока Linux sampler может недоучесть RSS. [Профиль и метрики](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/report.py) · [Измерение](/root/kani-rev2-u64-n18-n19-fix1-trigger-w15/control/ch8-cal1/run.py:700)

`U64_N18_N19_PROVIDERS_WITHIN_PROFILE` требует семь совпавших нативных исходов и exit 0, полные применимые свойства, `MATCHED`, своевременные receipts, полные опубликованные проекции, лимиты, sampler/reap и своевременную аттестацию `COMPLETE`. Незавершённые роли остаются `OPEN`. При неполной проекции сохранён `observed_outcome`. Публикация также проходит строгий cutoff.

Для `pins/sources/finish` используется самостоятельная Actions variable `CH8_REV2_U64_N18_N19_TRIGGER_TREE` со значением дерева Control из таблицы. Гейты требуют `Tiramisu-Cake/kani`, push attempt 1, `refs/heads/uninit-ci/ch8-q-pilot-v1`, SHA HEAD равный `GITHUB_SHA` и `event.after`, тот же ref и fork в payload, sole parent и чистый detached checkout. `sources` и `finish` сверяют admission receipt от `pins`. Review-trigger содержит `[skip ci]`. Публикуемую идентичность утверждает отдельный GO.

## Локальная проверка и открытые роли

- Статически сверены видимость, cfg, побайтный runtime/contract diff, TOML, YAML с уникальными ключами, восемь shell-блоков через `bash -n` и 15 Python AST. После FIX1 новый модуль проходит `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max --check`. Для `verify.rs` остаточный diff форматтера совпадает с унаследованным diff исходной базы. Регистрация следует сразу за `mod rev2_u64_n14_n17;`.
- Локальный depth-2 shallow clone без alternates прошёл `bundle verify/list-heads/unbundle`, HEAD, refs и shallow boundary сохранились. Сверены 24 commit/tree/parent, 25 текущих source blobs, 509 текстовых якорей и 77 нативных привязок новых слотов. Старые привязки N13 и N14–N17 сверены с их frozen rosters.
- При R1 офлайн-модель сверила 25 actual пар и все 512 масок на каждую базу, 12 012 выборок вставки на крайних u64 и границы p, 285 комбинаций k/a/c для каждой длины и 19 состояний центра. Дополнительно проверены 48 620 / 92 378 ранговых чередований половин N18 / N19, включая исчерпание любой половины.
- Detached review-trigger принял `pins` при +2 с, `sources` при +30 с, `finish` при +5100 с, `upload-gate` при +5150 с и `upload-check` при +5575 с. Отклонены подменённые tree и payload SHA во всех трёх гейтах, изменённый admission receipt в `sources/finish` и опоздание публикации на 0,01 с. Индекс содержит 11 членов, семь ролей `NOT_STARTED/OPEN`. Локальная симуляция проверила чистые Git-пины, bundle и source bindings с временными путями checkout. Проверка submodules выключалась только для этих локальных клонов.
- `test_supervisor.py` имеет заданный blob `df63a457c3adf648d360f3d559d5d40ef00a9427` в Control и review-trigger. На чистом detached trigger последовательно прошли 128/128 тестов на обычной шкале и на свежих шкалах 1/5/60 с. Время suite 35,807 / 36,797 / 38,011 / 37,355 с. Тесты отклоняют неверный kind/target, отсутствие typed copy, scoped assigns или cover, сдвиг координаты, выход за профиль, late receipt, отсутствие reap/attestation и позднюю публикацию.
- Std, Control и review-trigger имеют author/committer `Tiramisu-Cake <igkharin@gmail.com>`. Локальный g0 handoff использует ту же идентичность. Нативные программы и CI в этой стадии не запускались. Actions variables и remote refs не менялись.

Run `45926757103` завершён `success`, попытка 1 на `be69da84cbcc8667c766b5c11a9f4442db764286`. По метаданным GitHub прошли measure, finish и upload. Обновлённые ledger и задание w13 сообщают пять из шести `MATCHED`, аттестацию `COMPLETE`, битовый N17 `VERIFIED` за 81,224 с VT и четыре ожидаемых `FAILED/MATCHED` контроля. Символический insert-step r13..16 получил `RSS_LIMIT` при 90,650 с cold wall после первой SAT CNF 2 708 984 / 13 149 479. На отсечке группа достигла 4 242 916 KiB, CBMC 4 234 588 KiB. Reap подтверждён по отчёту w13. Нативные terminal, VT и covers insert-step не получены. Роль полноширинной вставки N14–N17 остаётся открытой под `U64_N14_N17_OPEN`. Evidence Brief принимает Cloud Build UUID, поэтому детальные исходы приведены по опубликованной записи w13. [Run N14–N17](https://github.com/Tiramisu-Cake/kani/actions/runs/45926757103) · [Ledger](CH8-DISPATCH-LEDGER.md#L309) · [Разбор и следующее задание w13](REV2-U64-N14-N17-FIX1-TASK.md#что-показал-45926757103)

У нового B10 insert фиксированы длина 10 и offset 9, место p остаётся символическим и выбрано через верхнюю границу. Этот слот измеряется отдельно. Вопросы после предыдущей отсечки — войдёт ли точный скалярный пост правой вставки в лимиты на этой геометрии и какая фаза определит стоимость каждого из трёх Check. При отсечке следует сохранить первый CNF, фазу, RSS/PSS и статус reap из receipt.

При отсечке pair сохранить фазу и нативные метрики. Разбиение на up/down или по k остаётся отдельным решением после измерения и GO. При успешных опорах следующему пакету остаются actual обратная копия N элементов на `smallsort.rs:425` (144/152 байта), конечный frame, сквозные positives и независимые контроли N18/N19.

## FIX1 · устранение замечания R1

Ревью R1 заблокировало прежний пакет из-за форматирования нового Rust-модуля и позиции его регистрации. FIX1 применяет закреплённый форматтер к восьми участкам и переносит только две строки регистрации. Новый модуль побайтно совпадает с результатом форматирования исходника R1. Сверка токенов подтвердила только удаление трёх необязательных завершающих запятых при свёртке вызовов. Удаление новой регистрации побайтно восстанавливает унаследованный `verify.rs`. [Ревью R1](REV2-U64-N18-N19-REVIEW.md#r1)

R1 Std `eb5b697e44b1d0ca1acc4e5f14222ef50864af38` и Control `d81a8587933a38aa05b9deb136878ec804c6852a` остались родителями FIX1. Прежний detached trigger `bc7c22292e83eb9a5ea050751a49c2cb405d5608` сохранён под отдельным ref. Пересчитаны координаты новых корней, свойств, Check-атрибутов, копии центра и регистрации. После учёта сдвига координат roster совпадает с R1 по ролям, селекторам, проверкам и профилю.

Ожидаемое значение `CH8_REV2_U64_N18_N19_TRIGGER_TREE` для FIX1 — `74f90d62acda5157906272454ec9d6c4bb9819db`. По порядку из R1 запуск N18/N19 следует после N14–N17 FIX1 на том же ref и после отдельного GO по новому дереву. [Ревью R1](REV2-U64-N18-N19-REVIEW.md#r1) · [Ledger](CH8-DISPATCH-LEDGER.md)
