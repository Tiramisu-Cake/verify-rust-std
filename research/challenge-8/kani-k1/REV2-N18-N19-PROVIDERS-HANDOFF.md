# REV2 · опоры sort9, вставки и merge для N18/N19

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** Подготовлен локальный пакет из шести exact singleton для Ubuntu 24.04. Входы — произвольный инициализированный V34, `u8/KeyLess<u8>` с числовым `<` и независимый `q: u8`. До отдельного GO требуются независимое ревью исходников и контрольных пинов. Результаты новых нативных слотов открыты. [Задание](REV2-N18-N19-PROVIDERS-TASK.md) · [План](REV2-N18-N31-PLAN.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Presort и правая вставка

Обе длины берут ветку `len >= 18`, `len_div_2=9`. Actual сеть сначала делает reborrow `v[1..10]`, затем `v[10..19]` при N18 или `v[10..20]` при N19. У каждой половины длина от 9 до 10, поэтому сеть выбирает `sort9_optimal`, а затем driver с `offset=9`. Guard sort9 пропускает все эти длины. Driver сразу выходит по `tail == v_end` при длине 9. При длине 10 он вызывает `insert_tail` один раз, rel9 / abs19, после чего `tail == v_end`. [Actual dispatch](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:367) · [Sort9](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:522) · [Driver](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:742)

25 вызовов `swap_if_less` сверены на пине в порядке исходника. Каждая пара имеет `0 ≤ a < b < 9`.

```text
(0,3) (1,7) (2,5) (4,8) (0,7) (2,4) (3,8) (5,6) (0,2)
(1,3) (4,5) (7,8) (1,4) (3,6) (5,7) (0,1) (2,4) (3,5)
(6,8) (2,3) (4,5) (6,7) (1,2) (3,4) (5,6)
```

| Ребро | Точная применимость |
| --- | --- |
| Левый S9 → полнобайтовый FIX3 | Для обеих длин base 1 в живом инициализированном V34, каждый вызов использует те же два различных адреса с provenance этого allocation и выравниванием 1. Домен `S13-SWAP-LEAF` на base1 разрешает `a < b < 13` и охватывает все пары. Цель получает base/a/b, компаратор и тип `u8`, без длины среза. |
| Правый S9 → leaf base10 | N19 использует `v[10..20]`. `S9-B10-SWAP` на той же базе, V34 и специализации связывает 25 адресных пар с существующим контрактом min/max и modifies двух ячеек. Arbitrary abs19 входит во frame битового корня. |
| Правый S9 N19 → правый S9 N18 | `v[10..19]` и `v[10..20]` имеют одинаковый base, живой V34 и выравнивание. При длине 9 или 10 guard пропускает вызов. Actual тело берёт один base и вызывает те же 25 пар. Относительный индекс 9 отсутствует в чтениях и записях. Правые префиксы совпадают, а остальной V34 и q сохраняются. |
| Правый S9 N19 → byte driver | Числовой порядок `v[10..19]` даёт единственное содержательное предположение driver. Хвост `v[19]` произволен. Если `before[19] >= before[18]`, сравнение с predecessor ложно. Если `before[19] < before[10]`, сохранённый tail строго меньше каждого байта prefix9, поэтому actual сдвиг проходит до `begin` и `CopyOnDrop` заполняет gap. Ожидаются numeric order `v[10..20]`, `count(<q)`, q и V34 frame. |

FIX3 фиксирует левый Check на Std `32129c149a15fb1b60a7314e738f3cb466d076e5`, tree `1b0cc32c571b370178e64f2b8c79773d2ce27051`. `smallsort.rs`, `cal1_model.rs` и `rev2_provider_cost.rs` в новом Std совпадают с этим пином. Исторический `S13-SWAP-LEAF` имеет исход `VERIFIED` и 6/6 covers в exact Ubuntu run 45661535099. [Идентичности FIX3 и проверенные anchors](REV2-N17-HANDOFF.md#идентичность-источников-и-исторические-anchors) · [Исходный leaf](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:143)

Для любого порога t отображение `Pₜ(x)=[x >= t]` переводит числовые min/max в AND/OR. По последовательности 25 пар это даёт ту же пороговую проекцию на выходе, что и actual битовый вызов, чей oracle равен `LOW9 ^ (LOW9 >> input_mask.count_ones())`. Каждый вход обрезан по `LOW9=(1<<9)-1`. Инверсия байтов обнаруживается при пороге, равном большему байту. Сохранение всех пороговых счётчиков даёт все кратности. Для actual вставки результат на фиксированном V34 независим от q, так как `KeyLess<u8>::call_mut` читает только пару значений и вычисляет `<`. Из `C(q)=count(byte<q)` кратности байтов 0–254 равны `C(b+1)-C(b)`, а кратность 255 равна `10-C(255)`. [Компаратор](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)

## Пара и нечётный центр

Пусть S указывает на `v[1]`, D — на начало отдельного writable `MaybeUninit<[u8; 32]>`. Перед парой k обозначим a,b число съеденных up элементов L,R, а c,d — down. База индукции k=0 даёт нулевые счётчики и пустой write set. При `a+b=c+d=k` actual пара получает `(S+a, S+9+b, D+k)` и `(S+8-c, S+N-1-d, D+N-1-k)`. Для `0 ≤ k < 9` все четыре указателя читают живые байты своих половин, а обе цели in bounds и различны. Check задаёт локальный числовой порядок половин и допускает независимые N, a и c в этих пределах. Source содержит полный V34, q независим.

Порядок `(byte, исходный индекс)` упорядочивает каждую половину, включая дубликаты. Up снимает глобальный ранг k из двух оставшихся фронтов и идёт влево при равенстве. Down снимает ранг `N-1-k` из двух оставшихся концов и идёт вправо при равенстве. Здесь каждая сторона индукции считает собственное потребление. При `k<9` новый низкий и высокий ранги различны, поэтому уже снятый противоположным проходом кандидат из исчерпанного промежутка не становится выбранным рангом. Native Check проверяет обе возвращённые тройки, два байта min/max, обе геометрии, q и V34 frame. Modifies разрешает только `D[k]` и `D[N-1-k]`. Семантика двух unconditional copies устанавливает запись в обе ячейки. Успех общих ID копий с unwind и per-N covers применяется к обоим straight-line вызовам. [Actual up/down](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:861) · [Правило grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

| Длина | Вход merge и девять пар | Последний шаг и cursor guard |
| --- | --- | --- |
| N18 | S покрывает два упорядоченных диапазона `v[1..10]` и `v[10..19]`. Девять пар заполняют `D[0..9]` и `D[9..18]` рангами 0–17. Два семейства целей не пересекаются и при каждом k сохраняют все предыдущие записи. | Потреблены все элементы, `a+c=9`, `b+d=9`. `left=S+a=S+9-c=left_rev.wrapping_add(1)`, `right=S+9+b=S+18-d=right_rev.wrapping_add(1)`. Odd ветка пропущена, оба равенства выполнены. |
| N19 | S покрывает `v[1..10]` и `v[10..20]` после правой вставки. Девять пар заполняют `D[0..9]` и `D[10..19]` рангами 0–8 и 10–18. Source, q и ранее записанные ячейки сохраняются. | После пар `(9-a-c,10-b-d)` равно `(1,0)` или `(0,1)`. Ранг 9 находится в единственном остатке. Odd Check копирует его в `D[9]`, продвигает выбранный прямой курсор и подтверждает оба равенства. |

Odd wrapper восстанавливает `left=S+a`, `right=S+9+b`, `left_rev=(S+8).wrapping_sub(c)`, `right_rev=(S+18).wrapping_sub(d)` на входе конца девяти пар. `wrapping_add(1)` даёт границы `S+9-c` и `S+19-d`. При `c=9` левый reverse sentinel равен `S-1` с исходной provenance. В этом случае выполняется только wrapping-переход от sentinel к S. Далее последовательность actual ветки совпадает с wrapper. Сравнение `left < left_end`, выбор `last_src`, одна `ptr::copy_nonoverlapping(last_src,D+9,1)` и два обновления прямых курсоров. Oracle выбирает исходный индекс из целочисленных длин остатков независимо от pointer comparison. Байтовое чтение scratch выполняется после unconditional copy, native modifies ограничено `D[9]`. [Actual цикл, odd и guard](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:1013)

Полная инициализация `D[0..N]` следует из непересекающихся unconditional записей при `uninit/validity OFF`. У actual consumer scratch и `v[1..1+N]` — отдельные живые области. Ровно N инициализированных байтов источника укладываются в scratch, а ровно N байтов назначения доступны на запись по `v_base`. У следующего пакета остаются native copy-back, привязка точных consumer call sites и сквозной post-return positive/control для каждой длины. Нативные Check в этом пакете относятся к swap, локальной паре и центру. [Actual copy-back](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:418) · [План consumers](REV2-N18-N31-PLAN.md#порядок-и-оценка)

## Exact roster и профиль

Префикс всех exact selectors — `slice::sort::shared::smallsort::verify::rev2_n18_n19_providers::`. Метки в таблице образуются добавлением указанных суффиксов к префиксу своего слота. Первые пять слотов также требуют `CAL1 q actual comparator executed`.

| Слот и selector после префикса | Режим | Префикс меток | Обязательные assertions | Дополнительные covers |
| --- | --- | --- | --- | --- |
| `S9-B01-L09-BITS` · `s9_b01_l09_bits` | Proof | `REV2_S9_B01_L09_BITS` | CANONICAL_MASK_POPCOUNT, Q_FRAME, V34_FRAME | MIXED_INPUT, INPUT_INVERSION, USEFUL_RETURN |
| `S9-B10-L10-BITS` · `s9_b10_l10_bits` | Proof | `REV2_S9_B10_L10_BITS` | CANONICAL_MASK_POPCOUNT, Q_FRAME, V34_FRAME | MIXED_INPUT, INPUT_INVERSION, USEFUL_RETURN |
| `S9-B10-SWAP` · `s9_b10_swap` | Check `swap_if_less` | `REV2_S9_B10_SWAP` | MIN_MAX, Q_FRAME, BYTE_FRAME | SWAP, NO_SWAP, EQUAL_DISTINCT_POSITIONS, NORMAL_RETURN |
| `N19-INSERT-RIGHT-BYTES` · `n19_insert_right_bytes` | Proof | `REV2_N19_INSERT_RIGHT` | NUMERIC_ORDER, COUNT_BELOW_Q, Q_FRAME, V34_FRAME | NO_SHIFT, FULL_SHIFT, NORMAL_RETURN |
| `M18-M19-PAIR-STEP` · `m18_m19_pair_step` | Check `actual_pair_step` | `REV2_M18_M19_PAIR_STEP` | UP_CURSORS, DOWN_CURSORS, READ_APPLICABILITY, WRITE_APPLICABILITY, DISJOINT_APPLICABILITY, UP_VALUE_TIE_LEFT, DOWN_VALUE_TIE_RIGHT, Q_FRAME, SOURCE_FRAME | Суффиксы _N18 и _N19 у каждого из K_ZERO, K_EIGHT, UP_TAKES_LEFT, UP_TAKES_RIGHT, DOWN_TAKES_LEFT, DOWN_TAKES_RIGHT, UP_TIE, DOWN_TIE и USEFUL_RETURN. Также отдельные N18 и N19 |
| `M19-ODD-CENTER` · `m19_odd_center` | Check `actual_odd_center` | `REV2_M19_ODD_CENTER` | READ_APPLICABILITY, WRITE_APPLICABILITY, DISJOINT_APPLICABILITY, ONE_REMAINING_BYTE, ODD_BYTE_VALUE, LEFT_CURSOR_END, RIGHT_CURSOR_END, Q_FRAME, SOURCE_FRAME | LEFT_REMAINDER, RIGHT_REMAINDER, POST_COPY |

Для литеральных меток covers и assertions используются native координаты из exact root. У пары обе проверки курсоров должны принадлежать checked wrapper.

Ожидаются `VERIFIED` и exit 0 у всех шести. Regular сохраняет native ID/Location/Status для assertions, covers и Check anchors. Stock RFC 0015 сохраняет exact selector, режим и terminal verdict, итоговые количества checks, IDs covers и доступные buckets других свойств. Success IDs берутся из regular и сверяются по count со stock. Для каждого Check literal target сверяется со stock, а `single_top_level_call` и `no_recursive_call` связывают exact символ stock с достижимыми native свойствами нужной мономорфизации и координатой Check. Write-set anchors включают grouped `memcpy.assigns`, для swap также `memmove.assigns` и FIX3 ensures. Обязательные точные координаты и ID задаёт frozen request. Их связь с множеством адресов и с экземплярами копий задаёт pinned исходник. [Frozen request](/root/kani-rev2-n18-n19-providers-control-w14/ch8-cal1/CI-REQUEST.json) · [Проекция](/root/kani-rev2-n18-n19-providers-control-w14/ch8-cal1/results.py)

Профиль — stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwind, undefined-function и assertion-reach ON. Uninit и validity OFF. Сохраняются phase/CNF/VT, cold wall, групповая RSS и отдельный пик CBMC, состояние sampler/reap, SHA-256 и размеры членов артефакта. Окно cold wall 180 с, reap 10 с, receipt 5 с и запас на запуск 10 с. Отбор требует VT ≤120 с, sampled group RSS ≤4 GiB и резерв памяти 2 GiB. `PROVIDERS_WITHIN_PROFILE` требует шесть полных слотов и итоговую аттестацию. Timeout, RSS, потеря соответствующего N/cover, неполная проекция или late receipt оставляют слот открытым. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md) · [Отчёт](/root/kani-rev2-n18-n19-providers-control-w14/ch8-cal1/report.py)

## Идентичности и запуск после отдельного GO

| Роль и worktree | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Вход задания в [g0](/root/verify-rust-std-kani3300-g0) | `2288c0cd5e35d220987e756a2d9e823edd245096` | `af4b2f83aefff58345d373d077c57d4ce361e497` | `6031d4cf0b25ddb149976c47cae6a1ce7de4f866` |
| [Std](/root/verify-rust-std-rev2-n18-n19-providers-w14), `work/rev2-n18-n19-providers-w14` | `86ea7aa5b773888e52f9fb78fda38d5cbff9ea61` | `63b199cc33052d6390fd0fdaa2b5c36962545fc4` | `49811849392302943d45b02beb4b0403509b9447` |
| [Control](/root/kani-rev2-n18-n19-providers-control-w14), `work/rev2-n18-n19-providers-control-w14` | `eb182675da584aa3177ee45a3ef110828db292db` | `1294be80f57daf77ffdb1cb28c8a7db13d4890a3` | `ee6156445c9cdd30912d1b3a41f9e4b2444caf25` |
| [Review-trigger](/root/kani-rev2-n18-n19-providers-trigger-w14/control), detached, ref `review/rev2-n18-n19-providers-trigger-w14` | `76e9654869acc93c83c014665d0275becbd627af` | `1294be80f57daf77ffdb1cb28c8a7db13d4890a3` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Std CI-base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |

| Вход | SHA-256 |
| --- | --- |
| [Frozen request](/root/kani-rev2-n18-n19-providers-control-w14/ch8-cal1/CI-REQUEST.json) | `8aaf773d0481446f05f1af4c71b531a2e43c1873cb0d9e543b5d1baf95e09bab` |
| Canonical roster, сортированные ключи и разделители `(",", ":")` | `90a4aa58d539ca95e0264ea56b6cbc8b67eb275339caa76ddd1d0395d08ce23a` |
| [Std overlay bundle](/root/kani-rev2-n18-n19-providers-control-w14/ch8-cal1/std-overlay.bundle), 26 922 байта | `06b310eb8de2dddf3e3e64468cf084c18d972ba57eaaed5b54c163239c0eb1ab` |

Ожидаемое внешнее значение tree — `1294be80f57daf77ffdb1cb28c8a7db13d4890a3`. Точные blobs `smallsort.rs`, `cal1_model.rs` и `rev2_provider_cost.rs` имеют IDs `0b77c3dbb3b767ba35281a2a686aa477ff1344c5`, `236394dcfb1ff571ee6f816391f7b2e00cc9e630` и `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` на FIX3, базе N17 и новом Std. Blob нового модуля — `9f5f22527656fd0b9b6afa879d7b8bb7574ff5c3`. [Корни Std](/root/verify-rust-std-rev2-n18-n19-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n18_n19_providers.rs)

Независимая Actions variable `CH8_REV2_N18_N19_PROVIDERS_TRIGGER_TREE` передаётся в окружение как `REV2_N18_N19_PROVIDERS_TRIGGER_TREE`. `pins`, `sources` и `finish` сверяют внешний tree, чистый detached checkout, fork `Tiramisu-Cake/kani`, push ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, exact event SHA и sole trigger parent. `sources` и `finish` также сверяют admission receipt. Upload открывается после успешных `pins` и `finish`. [Workflow](/root/kani-rev2-n18-n19-providers-control-w14/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-n18-n19-providers-control-w14/ch8-cal1/request.py)

| Этап | Бюджет | Отсечка от epoch |
| --- | ---: | ---: |
| Setup, compile и discovery | 50:00 | 50:00 |
| Шесть последовательных слотов | 20:30 | 70:30 |
| Итоговая аттестация | 2:00 | 72:30 |
| Finish | 5:00 | 77:30 |
| Upload | 7:00 | 84:30 |
| Резерв | 9:00 | 93:30 |
| Job | 100:00 | 100:00 |

Последние старты по порядку roster — **50:00, 53:25, 56:50, 60:15, 63:40, 67:05** от общего epoch. Шаговые лимиты workflow по порядку — 1, 2, 5, 5, 4, 3, 15, 51, 25, 6 и 8 мин. Внутренний лимит `measure` 1 415 с включает 60 с на входные проверки и 5 с на журнал. Если он наступает раньше абсолютного окна, latest starts сдвигаются раньше с сохранением полного бюджета каждого слота. `finish` использует более раннюю из отсечек 77:30 от epoch и 300 с от входа в шаг. Для upload внешняя минута сверх плановых 7 входит в резерв job. `pins` до 45 с и два последовательных watchdog по 90+5 с оставляют 65 с во внешнем окне 5 мин.

Setup сохраняет ранний compile preflight нового cfg до 180 с, первые rustc errors при отказе и точную дельту трёх `standard-harnesses` и трёх `contract-harnesses` по selector/kind/file. У каждого слота отдельные холодные CWD, Cargo/Kani targets, TMPDIR и export. Перед проекцией атомарно сохраняется checkpoint исхода и reap. Deadline receipt — минимум из конца слота и возврата supervisor плюс 5 с. Проекция заканчивается на секунду раньше, повтор отложенной записи выполняет bounded `finish` с late flag. Следующий слот открывает своё окно, если предыдущий процесс подтверждённо reaped или заведомо не запускался. Неподтверждённый reap блокирует остаток очереди. Caps проекции и артефакта составляют 4 MiB и 96 MiB. [Runner](/root/kani-rev2-n18-n19-providers-control-w14/ch8-cal1/run.py)

## Локальная проверка

- Вручную сверены Rust-имена, типы, contract targets и cfg. `verify` включается под `cfg(kani)`, регистрация нового модуля требует все восемь унаследованных cfg и `kani_smallsort_rev2_n18_n19_providers`. `super::super` разрешает private actual helpers и предикат disjoint из `smallsort`. `KeyLess`, `with_q/q` и `numeric_order` доступны в новом модуле по областям видимости соседних CAL1 модулей. `u8` удовлетворяет `FreezeMarker`, `KeyLess<u8>` реализует `FnMut(&u8,&u8)->bool`. `MaybeUninit`, `ptr` и `ub_checks` берутся из core, `crate::kani` предоставляется `kani_core::kani_lib!(core)`. `swap_if_less` импортируется из actual модуля, обе локальные Check цели объявлены в модуле harnesses.
- `rustfmt --check --edition 2024 --config use_small_heuristics=Max` прошёл бинарником nightly-2026-11-19 на новом модуле. Для registry добавлены `skip_children=true,reorder_modules=false`. `git diff --check` прошёл на Std, control, review-trigger относительно его родителя и handoff. Runtime diff пуст. Удаление нового lint и cfg регистрации побайтно восстанавливает registry и manifest базы N17. YAML разобран, прошли `bash -n` для шести shell-блоков и разбор двух встроенных Python-блоков. Синтетика сверила exact argv и 24 раздельных пути для Cargo target, Kani target, tmp и export.
- Локальный перебор по извлечённым из actual исходника 25 парам дал oracle на 512/512 битовых входах. Проверены по 285 легальных курсорных геометрий для N18 и N19, 100/110 пар упорядоченных бинарных половин соответственно и 19 терминальных разложений N19. У девяти разложений остаток слева, у десяти справа. Перебор проверяет расписание, индексную арифметику и guard поверх математического рангового аргумента.
- Полный синтетический suite выполнен последовательно. На обычной шкале **107/107** за 24,004 с (wall 24,352 с), на свежей шкале `monotonic() = 60 + elapsed` **107/107** за 23,312 с (wall 23,638 с). Зависимые чтения, включая `finish`, используют ту же шкалу. Сценарии покрыли неверные roster/kind и Check, чужой Check-символ и неверную координату assigns, потерю per-N cover, ранний compile/discovery отказ, медленную проекцию, повтор атомарной записи и late receipt, позднюю финализацию, неподтверждённый reap и последнее допустимое окно. После пропущенного старта или ошибки sampler с подтверждённым reap очередные слоты сохранили собственные окна.
- На изолированной bare shallow базе depth 2 через локальный Git transport без alternates прошли `git bundle verify`, `list-heads` и `unbundle`. До импорта overlay отсутствовал. После импорта сверены единственный рекламируемый HEAD, девять полных commit/tree/sole-parent и layout. HEAD базы, refs и shallow boundary сохранились.
- Exact локальный review-trigger с синтетическим push payload прошёл `pins` и `finish`. Индекс содержит шесть `NOT_STARTED`, `proof_credit=NONE`, ожидаемые три хэша входов и девять подтверждённых хэшей членов. Для `pins`, `sources` и `finish` отдельно отклонены tree базы control, произвольный tree, только старое имя pin и изменённый payload SHA. Всего 12 отказов в gates.

Нативная компиляция, discovery, фактические ID новых нативных свойств и ресурсные результаты остаются открыты до отдельного GO. Пакет и review-trigger остались локальными. Actions variables, CI и запуск Cargo, rustc, Kani, CBMC находились за границей этапа.
