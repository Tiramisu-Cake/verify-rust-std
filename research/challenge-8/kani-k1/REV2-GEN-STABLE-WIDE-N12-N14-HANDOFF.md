# REV2 · Wide N12 и N14 · exact merge Check и контроль N14

**READY_FOR_REVIEW · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Подготовлен один Ubuntu-пакет из пяти последовательных singleton. Первыми идут четыре stock Check фактических `merge_up` и `merge_down` в точной геометрии N12 и N14 на штатном PATH. Последним идёт литеральный контроль фактического входа N14 за отложенным relay stdout CBMC. Результат N12 оценивается отдельно от N14: `OPEN` у N14 не снимает два полных Check N12. Ниже приведены офлайн-перенос S4/fill обеих длин и ранговая композиция merge для независимого ревью. Нативная компиляция и результаты ожидают ревью и отдельного GO координатора. Исполнитель стадии — Claude Code, pane 11. [Задание](REV2-GEN-STABLE-WIDE-N12-N14-TASK.md) · [Решение R3](REV2-GEN-STABLE-N16-ADMISSION-REVIEW.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Пины пакета

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std N12/N14](/root/verify-rust-std-rev2-gen-stable-wide-n12-n14-w11) | `93d0c4a18d2f9e13c366a51c6f15e61c209a32d3` | `08402ed55717ed79fcffd20a5fff0e4b60c9ea2a` | `b465318cc95001c651011c2e5579bba12669b467` |
| [Control N12/N14](/root/kani-rev2-gen-stable-wide-n12-n14-control-w11) | `bfc6f20a86ad00f59b7b97fea2ab35371e7a57de` | `e10399474aacb1f9377be57e79e2ba7e54ef3c99` | `588fc98143a3321d58d58407c916da621b70cccb` |
| [Review-trigger, detached](/root/kani-rev2-gen-stable-wide-n12-n14-trigger-w11/control) | `90fa5b778b8b696d8e26373c08b9be8af348f168` | `e10399474aacb1f9377be57e79e2ba7e54ef3c99` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-wide-n12-n14-control-w11/ch8-cal1/CI-REQUEST.json) | `bfa5a790e7c4c195cc64b55c4c71190e4a7766f995f0d23734e6293d55f86cf2` |
| Exact roster из пяти строк, канонический JSON | `2cb3104aeffc56f7c53332f0b6547de890668bc7d11467f7cc1d8d9d0fe16ff0` |
| Source bindings, канонический JSON | `caca8508f832ff035153afb9aff2e86171b73ab3399c582a8f861a969698a296` |
| [Std bundle](/root/kani-rev2-gen-stable-wide-n12-n14-control-w11/ch8-cal1/std-overlay.bundle), 93 016 байт | `8c7a8b2ddb652a8d908e636bca7bbbf0276ec59cff31f11f9feb993c98a96d3f` |
| `ch8-cal1/cbmc_relay.py`, байты не менялись | `c8b4c070dbd12a8acafa4b23df0b74833b600333f539b66fc9d27eccee3613b7` |

Независимый pin — `CH8_REV2_GEN_STABLE_WIDE_N12_N14_TRIGGER_TREE=e10399474aacb1f9377be57e79e2ba7e54ef3c99`. Сохранены repo `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1 и payload guards. Bundle объявляет один `HEAD` и связывает 36 последовательных overlay-коммитов поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`. Frozen request связывает режим relay `SPILL_THEN_REPLAY`, его слот и SHA-256 исходника. Upload-gate сверяет индекс `smallsort-rev2-gen-stable-wide-n12-n14-artifact-v1` с четырьмя хэшами, хэшем relay и инвентарём. Worktree прошлых пакетов не изменялись.

## Std: модуль `wide_n12_n14`

Модуль дописан в конец `rev2_gen_stable_n16_pilot.rs` под `#[cfg(kani_smallsort_rev2_gen_stable_wide_n12_n14)]` на `:1497`. Check-cfg добавлен на `core/Cargo.toml:81`. Дельта Std от `b465318cc9` — эти два места. Байтовый префикс файла N12 сохранён, модуль закрывает файл. Runtime, контракты и blob `smallsort.rs` `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` не изменены. Blob модуля `ad44f5fe2894fa35a26a09668b01d21e5674cfef`, `core/Cargo.toml` `92b4366d5fc944c62ab9eca29720b4e8a564f7f8`. Модуль импортирует `super::*`, как FIX1, и `super::super::super::UnstableSmallSortTypeImpl`, как N12. Трейт объявлен `pub(crate)` на `smallsort.rs:87`, `merge_up`/`merge_down` — приватные функции родительского модуля `smallsort` (`:862`, `:895`), поэтому они видимы из дочернего `verify`. [Модуль](/root/verify-rust-std-rev2-gen-stable-wide-n12-n14-w11/library/core/src/slice/sort/shared/smallsort/verify/rev2_gen_stable_n16_pilot.rs:1497)

Все selectors и targets начинаются с `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::wide_n12_n14::`. Четыре обёртки зафиксированы по размеру и повторяют форму Wide FIX1. Каждая вызывает фактический `merge_up` или `merge_down` без Replace.

| Слот | Check target, `cfg_attr` | Кандидаты → цель, следующий курсор | Scoped `modifies` |
| --- | --- | --- | --- |
| `GEN-N12-WIDE-MERGE-UP` | `actual_merge_up_wide_n12`, `:1537:5` | `D[a]`, `D[6+b]` → `S[k]`, затем `S[k+1]` | `s.wrapping_add(k)` |
| `GEN-N12-WIDE-MERGE-DOWN` | `actual_merge_down_wide_n12`, `:1617:5` | `D[5−c]`, `D[11−d_count]` → `S[11−k]`, затем `S[10−k]` | `s.wrapping_add(11 - k)` |
| `GEN-N14-WIDE-MERGE-UP` | `actual_merge_up_wide_n14`, `:1698:5` | `D[a]`, `D[7+b]` → `S[k]`, затем `S[k+1]` | `s.wrapping_add(k)` |
| `GEN-N14-WIDE-MERGE-DOWN` | `actual_merge_down_wide_n14`, `:1778:5` | `D[6−c]`, `D[13−d_count]` → `S[13−k]`, затем `S[12−k]` | `s.wrapping_add(13 - k)` |

- **Контракт.** `k<m`, `a<=k` (Up) или `c<=k` (Down), `b=k−a`, `d_count=k−c`. `can_dereference(slice_from_raw_parts(d, N))`, `can_write(slice_from_raw_parts_mut(s, N))`, `!same_allocation(d, s)`. Выравнивание входит в оба предиката: в stock Kani `9834c96ce9` `can_write` — это `is_ptr_aligned && is_inbounds`, `can_dereference` дополнительно требует инициализацию и валидное значение (`library/kani_core/src/mem.rs:35–36`, `:73–79`). Живость и раздельность аллокаций дают те же предикаты и `same_allocation`.
- **Утверждения обёртки.** `_READ`, `_WRITE`, `_DISJOINT` закрепляют чтение обоих кандидатов, запись цели и их непересечение. `_CURSORS` сверяет оба исходных курсора и следующий курсор записи. Up берёт левую запись при `left.key <= right.key`. Down берёт левую при `left.key > right.key`, правую при равенстве. Обратные курсоры Down сравниваются через `wrapping_sub`, указатель перед `D` на последнем шаге только сравнивается.
- **Утверждения корня.** Корень берёт символические `u8` для `k` и счётчика, переводит их в `usize` и ограничивает единственным `kani::assume` счётчиков. Все поля V14/V16 и всех 48 записей D произвольны, условий sorted или tie нет. `D[N..48]` служит произвольными канарейками для frame корня. `_VALUE` сравнивает все три поля записи в `v[1+k]` или `v[N−k]` с ожидаемой. `_V_FRAME` покрывает весь V14/V16 кроме этой позиции. `_SCRATCH_FRAME` покрывает весь D48 двумя проходами `0..32` и `32..48`.
- **Covers 7/7.** `_TAKES_LEFT`, `_TAKES_RIGHT`, `_TIE` (равные ключи, разные метки), `_K_ZERO`, `_K_LAST` (`k == m−1`), `_RETURNED` и компаратор `GEN_N16_WIDE_COMPARATOR_CALLED` на `:35:5` в `wide_less`.
- **Приёмка.** Требуется `VERIFIED/MATCHED`, exact stock target `ProofForContract`, `single_top_level_call` и `no_recursive_call` на строке `cfg_attr`, колонка 5. Нужны scoped `memcpy.assigns.1/.2`, шесть grouped typed-copy свойств `ptr::copy_nonoverlapping::<…::Wide>` на `ptr/mod.rs:587:14` и `SUCCESS` у всех выведенных unwind. Actual copy site — `smallsort.rs:885:9` для Up и `:918:9` для Down. Тело обёртки вызывает ровно один `merge_*` своего направления и не копирует само.

### Источник: гейт по геометрии

`request.check_wide_n12_n14_source` рендерит голову модуля (импорты, три помощника, четыре обёртки с корнями) только из `(N, направление)`, `m=N/2`, и требует побайтного совпадения. Так закреплены все литеральные смещения `m`, `m−1`, `N−1`, `N−2`, границы `k<m`, длины срезов `N`, `wide_array::<N+2>`, `v[1..N+1]`, индексы `1+k` и `N−k`, циклы frame `0..N+2`, `k == m−1`, scoped `modifies`, tie-правила и единственный `assume`. Хвост модуля начинается с маркерной строки `:1859` и проверяется отдельным гейтом литерального контроля. После объявления модуля на колонке 0 закрывается только сам модуль, и он закрывает файл.

## N14 · контроль фактического вызова

Литеральный `v[1..15]` в V16. В каждой семёрке ключи `[1,0,1,0,0,0,0]`, метки 0…13 по исходной позиции, `payload=0x8000_0000_0000_0100+tag`. Внешние записи те же, что у N12: `v[0]=(2,16,0x1111_2222_3333_4444)`, `v[15]=(3,17,0xaaaa_bbbb_cccc_dddd)`. Вызов `<Wide as UnstableSmallSortTypeImpl>::small_sort(&mut v[1..15], &mut less)` на `:1915` идёт через actual trait к general с D48. Там выполняются два actual S4, по три fill `4..7` на половину и семь пар merge. Тело не содержит `assume`, `kani::any()`, stubs, Check, `cfg_attr` и `memcmp`, гейт это проверяет.

| Фаза | Метки `v[1..15]` | Assertions |
| --- | --- | --- |
| До обмена | `[1,3,4,5,6,8,10,11,12,13,0,2,7,9]` | `GEN_N14_WIDE_BEFORE_ORDER` :1919, `_RECORDS_BY_TAG` :1920, `_STABLE_EQUAL_KEYS` :1921, `_SWAP_PAIR` :1922, `_FRAME` :1926 |
| После обмена целых `v[5]`, `v[6]` | `[1,3,4,5,8,6,10,11,12,13,0,2,7,9]` | `GEN_N14_WIDE_AFTER_ORDER` :1936, `_RECORDS_BY_TAG` :1937, `_FRAME` :1938 |
| Последняя проверка | — | `GEN_N14_WIDE_STABLE_EQUAL_KEYS` :1939, ожидаемый `FAILURE` |

Перед обменом у `v[5]` и `v[6]` ключ 0. Метка 6 приходит из левой половины, метка 8 из правой. Скалярный `observe` с литеральной границей `1..14` сверяет полные записи с независимыми константами `EXPECTED` до обмена и `CORRUPTED` после. Covers 3/3: компаратор `:35:5`, `AFTER_WIDE_N14_RETURN` `:1916:9`, `GEN_N14_WIDE_WITNESS_CROSS_HALF_TIE` `:1927:9`. Единственный отказ — `GEN_N14_WIDE_STABLE_EQUAL_KEYS`, класс `assertion`, exit 1. Regular и stock должны совпасть по ID, классу, файлу, строке и метке. Typed-copy и unwind guards такие же, как у N12. Actual sites: S4 `:832–835`, fill `:329`, gap `:722`, guard `:362`, merge `:885`, `:918`.

Независимая Python-модель трассы `smallsort.rs` (S4, `insert_tail`, `bidirectional_merge`, сравнение только по ключу, без `sorted` как оракула) дала ожидаемые метки. Трасса S4: `[1,3,0,2]` и `[8,10,7,9]`. Каждый fill с ключом 0 сдвигает две единицы. После обмена порядок ключей сохраняется и появляется единственная инверсия на позиции 5. Модель подтвердила порядок, точные кратности, устойчивость и frame на всех 3^12 и 3^14 шаблонах ключей.

### Доставка через relay

`SPILL_THEN_REPLAY` применяется только к N14 witness. Четыре Check, prepare, version attestation и discovery используют штатный PATH, тест проверяет `path_prefix=None` и `stdout_delivery=STOCK_PIPE` у каждого Check. Байты relay, установка, проверки реального CBMC (путь, размер, SHA-256, `(dev, inode, size, mtime_ns)`, первая строка версии 6.11.0), предел spill 4 GiB, резерв диска 2 GiB, census, окно разбора префикса после reap и все отказы сохранены из FIX2. Для `MATCHED` нужны полные regular и stock проекции и relay `COMPLETE`. Приёмка сверяет ровно один вызов `--json-ui`, argv-хвост stock `cbmc_flags` с goto внутри слота и verbose-строкой Kani, равные объём и SHA-256 spill/replay, `wait done < replay first byte`, общие PGID/SID и нормальный код CBMC. Профиль argv равен наблюдённому вызову реального CBMC для plain Wide root в `46111911533/1`, тест сверяет его литерально. В receipt и SUMMARY.md режимы различаются колонкой «Stdout delivery»: `STOCK_PIPE` у Check и статус relay у N14. [Relay](/root/kani-rev2-gen-stable-wide-n12-n14-control-w11/ch8-cal1/cbmc_relay.py) · [Сторона runner](/root/kani-rev2-gen-stable-wide-n12-n14-control-w11/ch8-cal1/stdout_relay.py)

## Офлайн-перенос S4 и fill

Привязка маршрута. `Wide` — Copy+Freeze, 24 байта, align 8 (константные проверки `:23–32`). `smallsort.rs:134–139` передаёт вызов в `UnstableSmallSortFreezeTypeImpl`. На `:213–224` `has_efficient_in_place_swap::<Wide>()` ложно, а `24·48 ≤ MAX_STACK_ARRAY_SIZE`, поэтому выбирается `small_sort_general`. На `:261–273` он создаёт внутренний `stack_array` из 48 элементов. На `:282` `len<2` ложно. На `:286` `scratch.len()=48 < N+16` ложно, так как `N+16` равно 28 и 30. На `:297` ветка S8 закрыта размером 24. На `:308` `len>=8`, поэтому `:310–311` вызывают S4 на `S[0..4]→D[0..4]` и `S[m..m+4]→D[m..m+4]`. На `:321–331` для `offset ∈ {0, m}` `desired_len=m` и fill идёт по `i ∈ 4..m`. Каждый шаг полностью копирует `S[offset+i]` в `D[offset+i]` (`:329`) до вызова `insert_tail(D+offset, D+offset+i)` (`:330`).

Нативные опоры N16 (все `VERIFIED/MATCHED`, приняты в допуске Wide N16): левый S4 `close::gen_n16_wide_s4_l48` (`46073528434/1`), правый S4 `gen_n16_wide_s4_r48` (`46054351048/1`), правые fill rel4 `gen_n16_wide_fill_r48_rel4` (`46054351048/1`), rel5 и rel6 `close::gen_n16_wide_fill_r48_rel5/6` (`46073528434/1`). В опорах `S=v[1..17]` в V18. Правый S4 читает `S[8..12]` и пишет `D[8..12]`. Правый fill rel R читает `S[8+R]`, пишет `D[8+R]` и вставляет его в `D[8..9+R]`. Левый S4 работает на `S[0..4]→D[0..4]`. Смещения ниже даны в записях и в байтах от начала своей аллокации. V14 занимает 336 байт, V16 — 384 байта, D48 — 1152 байта.

| Длина, шаг | Нативная опора N16 | Чтение V | Запись D, вставка | Сдвиг | Предпосылка снята |
| --- | --- | --- | --- | --- | --- |
| N12 S4 лев. | S4 L48 | `v[1..5]`, [24, 120) | `D[0..4]`, [0, 96) | 0, V18→V14 сужает только аллокацию | нет |
| N12 S4 прав. | S4 R48 | `v[7..11]`, [168, 264) | `D[6..10]`, [144, 240) | −48 в V и D | нет |
| N12 rel4 лев. | rel4 | `v[5]`, [120, 144) | `D[4]`, [96, 120), в `D[0..5]` | −192 | `:267` ← `SORTED` левого S4 |
| N12 rel5 лев. | rel5 | `v[6]`, [144, 168) | `D[5]`, [120, 144), в `D[0..6]` | −192 | `:1082` ← exact post rel4 |
| N12 rel4 прав. | rel4 | `v[11]`, [264, 288) | `D[10]`, [240, 264), в `D[6..11]` | −48 | `:267` ← `SORTED` правого S4 |
| N12 rel5 прав. | rel5 | `v[12]`, [288, 312) | `D[11]`, [264, 288), в `D[6..12]` | −48 | `:1082` ← exact post rel4 |
| N14 S4 лев. | S4 L48 | `v[1..5]`, [24, 120) | `D[0..4]`, [0, 96) | 0, V18→V16 | нет |
| N14 S4 прав. | S4 R48 | `v[8..12]`, [192, 288) | `D[7..11]`, [168, 264) | −24 в V и D | нет |
| N14 rel4 лев. | rel4 | `v[5]`, [120, 144) | `D[4]`, [96, 120), в `D[0..5]` | −192 | `:267` ← `SORTED` левого S4 |
| N14 rel5 лев. | rel5 | `v[6]`, [144, 168) | `D[5]`, [120, 144), в `D[0..6]` | −192 | `:1082` ← exact post rel4 |
| N14 rel6 лев. | rel6 | `v[7]`, [168, 192) | `D[6]`, [144, 168), в `D[0..7]` | −192 | `:1009` ← exact post rel5 |
| N14 rel4 прав. | rel4 | `v[12]`, [288, 312) | `D[11]`, [264, 288), в `D[7..12]` | −24 | `:267` ← `SORTED` правого S4 |
| N14 rel5 прав. | rel5 | `v[13]`, [312, 336) | `D[12]`, [288, 312), в `D[7..13]` | −24 | `:1082` ← exact post rel4 |
| N14 rel6 прав. | rel6 | `v[14]`, [336, 360) | `D[13]`, [312, 336), в `D[7..14]` | −24 | `:1009` ← exact post rel5 |

Последние исходные записи — `v[6]` и `v[12]` для N12, `v[7]` и `v[14]` для N14. Их цели — `D[5]`, `D[11]` и `D[6]`, `D[13]`. Канарейки `v[0]` на [0, 24) и `v[13]` на [312, 336) в V14 или `v[15]` на [360, 384) в V16 не входят ни в одно множество чтения или записи.

1. **Жёсткий сдвиг.** В `sort4_stable` (`:791–837`) все чтения идут по `v_base.add(0..4)`, все записи — по `dst.add(0..4)`. Ветвления зависят только от сравнений ключей. В `insert_tail` (`:701–735`) все адреса лежат в `[begin, tail]`. Цикл останавливается на `sift == begin`, поэтому указатель ниже `begin` не возникает, в том числе при `begin = D+0`. Копия `:329` и вставка `:330` используют только `src+i`, `dst+i` и `dst`. Значит, поведение шага инвариантно к общему сдвигу обеих баз, если сдвинутые диапазоны лежат в своих аллокациях. Таблица показывает, что это выполняется для V14, V16 и D48. Сдвиги кратны 24 байтам, а V и D — массивы `Wide` с align 8, поэтому выравнивание сохраняется. Свойства выравнивания typed-copy в опорах дали `SUCCESS`.
2. **Раздельность и независимость.** V — срез вызывающего, D — внутренний `stack_array` из `small_sort_general`, это разные живые аллокации. Опоры брали произвольные значения во всех остальных записях V18 и D48. Результат шага зависит только от его входного диапазона, поэтому значения остальной части V14/V16 и D48 на него не влияют.
3. **Frame.** Каждая опора утверждает неизменность всей V18. Значит, S4 и fill ничего не пишут в V: канарейки, следующий источник и записи другой половины остаются исходными, пока к ним не обратится следующий шаг. Scratch-frame опоры сохраняет D48 вне `[base, base+R+1)` для fill и вне `[base, base+4)` для S4. После сдвига каждый шаг меняет только диапазон своей половины, `D[0..m]` или `D[m..N]`, и не трогает уже построенный префикс другой половины. Порядок `:321` — все fill левой половины, затем правой — этому не мешает.
4. **Снятие `kani::assume`.** Fill rel4 (`rev2_gen_stable_n16_pilot.rs:267`) предполагает отсортированный `D[base..base+4]`. Это даёт пост `SORTED` S4 своей половины. Для rel5 (`:1082`) предпосылку даёт exact post rel4: вставка после равных в отсортированный префикс оставляет его отсортированным. Для rel6 N14 (`:1009`) её даёт exact post rel5. Других предпосылок у опор нет.
5. **Устойчивость и произвольные tag/payload.** S4-опора метит четыре входа локальными метками 0–3 и доказывает отсортированность, перестановку полных записей и возрастание меток при равных ключах. Ветвления S4 читают только `key`, копии переносят весь `Wide`. Поэтому выбранная перестановка зависит только от ключей, а метки опоры — от исходных позиций. Значит, для произвольных `tag/payload` S4 даёт устойчивую сортировку по `(key, исходная позиция)`. Fill-опоры работают на произвольных записях и вставляют полную `S[base+R]` в позицию `#{old.key ≤ x.key}`, то есть после всех равных. Источник `S[base+R]` идёт по позиции после всего префикса. По индукции `D[0..m]` и `D[m..N]` — устойчивые сортировки `S[0..m]` и `S[m..N]` по `(key, исходная позиция)`.
6. **Инициализация scratch при uninit OFF** (внешний вывод). `D[base..base+4]` пишется четырьмя копиями `:832–835` до первого чтения. `D[base+R]` пишется копией `:329` до того, как `insert_tail` прочтёт `tail` (`:706`). `sift` читается только внутри уже записанного префикса. Merge читает только `D[0..N]`, полностью записанный к `:342`. `D[N..48]` не читается.

R3 принял перенос N12 при этих условиях. Перенос N14 со сдвигом −24 справа и −192 для левых fill, включая rel6, представлен к независимому ревью.

## Merge и нормальный возврат

На `smallsort.rs:1014–1044` шаги Up и Down идут парами `for _ in 0..m`. Перед парой `k` выполнено `a+b=c+d_count=k`, и каждый счётчик не больше `k<m`. Поэтому оба курсора каждого направления лежат строго внутри своих половин. Это ровно область обоих Check: `k<m`, `a≤k` или `c≤k`, произвольные S и D. Up не пишет в D, поэтому Down той же пары получает тот же D. Произвольный S в Check покрывает V после Up. Цели `S[k]` и `S[N−1−k]` раздельны, так как `k ≤ m−1 < m ≤ N−1−k`. Все левые исходные позиции меньше правых. Поэтому tie-left в Up выбирает меньший элемент по `(key, исходная позиция)`, а tie-right в Down — больший. По индукции Up пишет ранги `0…m−1` в `S[0..m]`, Down пишет ранги `N−1…m` в `S[m..N]`. Ранги разбивают `0..N` ровно один раз, поэтому `a+c=b+d_count=m`. Конечный левый курсор `D[a]` равен `left_end = D[m−1−c]+1`, правый `D[m+b]` равен `right_end = D[N−1−d_count]+1`. Проверка `:1042` выполнена, паники нет. При чётной длине копия центра `:1031–1036` не исполняется. Merge пишет прямо в V (`drop_guard.dst = v_base`, `copy_back=false`), на нормальном пути `mem::forget` на `:347` исключает восстановительную копию. Scoped `modifies` каждого шага и V-frame Check исключают `v[0]` и `v[N+1]`.

Вместе с переносом S4/fill это даёт пост на exact trait входе для произвольных полных записей: порядок по ключу, точные кратности каждой полной записи, устойчивость по исходным позициям и неизменность обеих внешних записей при нормальном возврате. Нативная часть: четыре Check этого пакета и опоры N16. Внешняя часть: перенос S4/fill и ранговая индукция.

Нативный контроль N12 переиспользуется из `46111911533/1`: `GEN-N12-WIDE-WITNESS-LITERAL-CORRUPT` на V14, stock pipe, `FAILED/MATCHED`, единственный отказ `GEN_N12_WIDE_STABLE_EQUAL_KEYS` (`.assertion.25`, `1493:9`), covers 3/3, 27,012 с VT, 71,266 с cold, пик группы 3 690 388 KiB. Std того прогона — `b465318cc9`, родитель этого Std. Байты корня N12 сохранены по append-only цепочке, gate N12 сверяет их на собственной ревизии. [Индекс N12](/root/ch8-artifacts/run-46111911533/ch8-rev2-gen-stable-wide-witness-n12-n16-Linux-X64-46111911533-1/index.json)

## Профиль, argv и часы

Одна Ubuntu 24.04 X64 job до 105 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC 6.11.0/CaDiCaL 3.0.0, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwinding, undefined-function и assertion-reach включены, uninit и validity выключены. На каждый корень 120 с VT, 180 с cold wall, 4 GiB group RSS, резерв ОС 2 GiB. Все пять строк используют 33 флага cfg, cfg-off опускает последний. Ориентир по Wide N16 FIX1 (`46064575550/1`): 59,7 и 60,6 с VT, 94,5 и 97,2 с cold, пик 2 571 448 и 2 611 436 KiB на Check. Геометрии N12 и N14 меньше по V, а D и копируемые записи те же. Ресурсный профиль N14 witness измеряется впервые. Между N12 stock (3 888 543 / 19 738 025, пик 3 690 388 KiB) и N16 relay (4 956 964 / 25 517 502, пик 3 512 460 KiB) ожидаю первую CNF около 4,4 млн / 22,6 млн дизъюнктов. Пик группы с relay ожидаю ниже 4 GiB, но это оценка, а не измерение.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Тест сверяет argv всех пяти строк с receipt N12 из `46111911533/1` с точностью до selector и каталога слота, а `RUSTFLAGS` — с тем же вектором плюс новый флаг. У N14 witness окружение Kani отличается только префиксом `PATH=$slot/relay/bin:…`. Ранний cfg-on compile preflight идёт до обоих discovery list, первые rustc diagnostics сохраняются.

| Стадия | Дедлайн от начала job | Лимит |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Identity gate и latest start `GEN-N12-WIDE-MERGE-UP` | 55:00 | До 60 с с начала measure |
| Latest start `GEN-N12-WIDE-MERGE-DOWN` | 58:25 | Окна по 205 с |
| Latest start `GEN-N14-WIDE-MERGE-UP` | 61:50 | |
| Latest start `GEN-N14-WIDE-MERGE-DOWN` | 65:15 | |
| Latest start `GEN-N14-WIDE-WITNESS-LITERAL-CORRUPT` | 68:40 | |
| Конец окон | 72:05 | |
| Финальная аттестация | 74:05 | Measure 20:10 внутренний, 23 мин внешний |
| Finish и upload-gate | 79:00 | 5 с запаса на запуск upload |
| Upload | 86:05 | Внешние 7 мин |
| План с резервом | 92:05 | Job 105 мин |

Сохранены caps 4/96 MiB, checkpoint перед проекцией, ограничение повтора receipt дедлайном, reap до следующего слота и финальная проверка индекса. Если слот не подтвердил reap, следующие не запускаются. При cutoff receipt сохраняет исход, census и по роли первую CNF, фазу и RSS, у N14 — CNF из префикса spill. `slot_diagnoses` оценивает каждый слот. `length_diagnoses` даёт `N12` только по двум Check N12, `N14` — по двум Check N14 и witness. Общий диагноз `GEN_STABLE_WIDE_N12_N14_WITHIN_PROFILE` требует всех пяти.

## Discovery

Cfg-off содержит 181 историческую запись, включая контроли N10, N12 и N16 FIX2. Cfg-on добавляет четыре `ProofForContract` с exact targets `wide_n12_n14::actual_merge_{up,down}_wide_n{12,14}` и один plain Proof N14 без target, всего 186. Активный roster — пять строк выше в этом порядке. Discovery отклоняет исторический N12 или N16 на месте новой строки, plain-строку на месте Check, перестановку, неполный или удвоенный roster, чужой target и contract target у standard harness. Исторические roster закреплены своими digest: N12 и N16 FIX2 — общим `7f4ae44e…` прошлого пакета, N16 — `9241da11…`, N10 — `528906a5…`, а также CLOSE, FIX1 и pilot. Их координаты сверяются на собственных ревизиях.

## Валидация

- **Std.** Rustfmt `nightly-2026-11-19` (`style_edition=2024`, `use_small_heuristics=Max`) прошёл для нового и прежнего blob модуля. Файл N12 — побайтный префикс нового. TOML разобран, `git diff --check` пройден. Python-модель трассы описана выше.
- **Source gate на Std N12/N14.** На точном trigger и свежем depth-2 Std без alternates и refs шаг `sources` принял bundle. Он сверил 36 commit/tree/parent, append-only слои до N12 и N14, 30 текущих blobs и 1 319 литеральных координат, из них 106 новых. Также совпали native coordinates всех исторических roster и пяти новых строк на реальном blob, actual copy sites, рендер Check по геометрии и обе перестановки N14 из литерального `INPUT`. Gate N12 останавливается на следующем opt-in модуле.
- **Синтетика, Check.** Гейт геометрии отклонил 38 мутаций. Среди них смещения `m`, `m−1`, `N−1`, `N−2`, границы `k<m`, длины срезов, размер V, диапазон `v[1..N+1]`, индексы value и frame, `k == m−1`, scoped `modifies`, оба tie-правила, `sub` вместо `wrapping_sub`, `merge_down` в Up, подмена target в `proof_for_contract`, снятый `same_allocation`, добавленный sorted guard, граница прохода D, импорты и хвостовые элементы после модуля. Проекция отклоняет подмену target, definition, selector, Check, колонки `cfg_attr`, scoped assigns, typed-copy свойства, copy site другого направления, неполные wrapper assertions и неуспешный unwind. Перекрёстная подмена между N12 и N14 тоже отклоняется. Гейт native coordinates отклоняет 10 мутаций строк и модуля.
- **Синтетика, N14 witness.** Отклонены 26 мутаций. Среди них границы `observe`, unwind, диапазон вызова, длина и ключи `INPUT`, канарейки, payload, порядок `EXPECTED` и `CORRUPTED`, индексы наблюдателя, пара обмена, tie cover, сам обмен, frame, переставленные наблюдатели до и после обмена, `kani::any`, `kani::assume`, Check, stub, чужая пара и маркер, перенесённый перед Check. Чужой или второй failure, неверный stock ID или координата отказа отклоняются в проекции.
- **Relay и профиль.** Relay только у N14, Check с PATH-префиксом отсутствуют. Relay на любом Check снимает этот Check и его длину, но не другую. Неполная или не оценённая доставка оставляет N14 `OPEN`, а N12 — в профиле. Просроченный receipt, превышение VT, cold или RSS, неверный exit и неполная проекция оставляют слот `OPEN`. Изоляцию длин тест проверяет на превышении VT у Check N12 и на четырёх мутациях witness N14. Все 25 тестов relay перенастроены на слот N14 без ослабления проверок, включая эквивалентность транспорта на 22 МБ JSON, сбои spill и replay, census и полный префикс spill. Blob `test_supervisor.py` равен `df63a457c3adf648d360f3d559d5d40ef00a9427`, `supervisor.py`, `telemetry.py` и `cbmc_relay.py` не изменены.
- **Trigger.** На точном detached trigger прошли `pins`, `sources`, `finish` с пятью `NOT_STARTED` и диагнозом `OPEN`, `upload-gate` и `upload-check`. Отклонены tree FIX2 `664f75885c`, чужой payload FIX2 trigger `f0f51bd6de`, подмена индекса и receipt, поздние upload-gate и upload-check. Std-checkout сохранил HEAD `dab03cf510`, shallow boundary и отсутствие refs. YAML разобран с проверкой уникальных ключей, job 105 мин, measure 23 мин, восемь блоков прошли `bash -n`, `git diff --check` пройден.
- **Suite.** 175 тестов, последовательно на точном trigger с лимитом 150 с: обычная шкала 175/175 за 77,573 с, старт с 1 с 175/175 за 78,503 с, с 5 с 175/175 за 84,479 с, с 60 с 175/175 за 78,345 с. Четыре прогона занимают около 5,3 мин в шаге с внешним timeout 8 мин.
- Локальная стадия обошлась без Cargo, rustc, Kani, CBMC, CI, push в Kani и изменений Actions variables. Коммиты Std, Control и trigger имеют `[skip ci]` и author/committer `Tiramisu-Cake <igkharin@gmail.com>`.

## Ограничения

- Компиляция нового модуля не проверялась локально. Ранний cfg-on preflight остановит пакет до discovery, если rustc его отклонит. Форма обёрток и импортов повторяет уже скомпилированные FIX1 и N12.
- Перенос S4/fill и ранговая индукция — внешние шаги. Инициализация scratch выведена из путей чтения и записи при uninit OFF. Покрытие UB указано по фактическим флагам.
- Ресурсы N14 witness оценены интерполяцией. При `RSS_LIMIT` до replay receipt даст census по PID и CNF из префикса spill, длина N14 останется `OPEN`, а N12 будет оценена по своим Check.
- Контроль N14 — один литеральный вход. Он не переносится на другие длины и произвольные входы. Профиль 4 GiB у N14, как и у N16, относится к доставке через relay.

## Дальше

Независимое ревью пакета, включая перенос N14, затем отдельный GO координатора на установку tree variable `e10399474a…` и новый trigger с этим tree и sole parent `467af9cb8d`.
