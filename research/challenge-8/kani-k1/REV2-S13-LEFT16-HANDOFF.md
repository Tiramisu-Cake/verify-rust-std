# REV2 · левый sort13 N32 · перенос base1 на len16

**Вердикт.** `(base=1, len=16)` можно включить в исследовательский граф как **внешне перенесённую геометрию с составным свидетельством** для `sort13_optimal<u8, KeyLess<u8>>`. Перенос по длине применим к `13..=17` на base1 и к левому вызову actual N32. Нативный exact `Proof` для `(1,16)` остаётся запасным вариантом при таком требовании ревью. `go=NOT_GRANTED`, `proof_credit=NONE`. [Задание](REV2-S13-LEFT16-TASK.md)

## Пины и свидетельства

Задание закреплено в g0 `ea5f938771`. Работа выполнена поверх `0924776bd061749b6c2d7dfdac7b55d19d181c7a` с сохранением двух последующих записей о merge. Пин actual Std проверен в `/root/verify-rust-std-rev2-s13-geometries-w14`.

| Std | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| S13 geometries, actual N32 | `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a` | `ff2563b5867b8327b95db909262ddf80e3ed9c03` | `32c2857f4b7137601de54ea42a02610c8fd29ed9` |
| S13 binding | `32c2857f4b7137601de54ea42a02610c8fd29ed9` | `0e682cfceaed5d33d3d3374b5dc97da5012bba93` | `32129c149a15fb1b60a7314e738f3cb466d076e5` |
| FIX3 | `32129c149a15fb1b60a7314e738f3cb466d076e5` | `1b0cc32c571b370178e64f2b8c79773d2ce27051` | `043a1f19f9d36eb1666979f97b8e7e483ab41c5e` |

На всех трёх пинах совпадают blobs `smallsort.rs` (`0b77c3dbb3b767ba35281a2a686aa477ff1344c5`), `cal1_model.rs` (`236394dcfb1ff571ee6f816391f7b2e00cc9e630`), `cal1_q_merge_model.rs` и `rev2_provider_cost.rs` (`c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de`). Совпадают и исходники slice pointer, raw slice и индексации, которые задают доступный диапазон. [Проверка пинов](check_rev2_s13_left16.py)

Исторические вердикты приведены по зафиксированным разборам g0. Общий профиль этих строк — Ubuntu X64, stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC 6.11.0, CaDiCaL, OB12, unwind36, jobs=1, `--no-assert-contracts`, safety/overflow/unwind ON, uninit/validity OFF. [Binding](REV2-S13-BINDING-RESULTS-ANALYSIS.md) · [Geometries](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md) · [FIX3](REV2-NETWORK-PROVIDERS-RESULTS-ANALYSIS.md)

| Геометрия и режим | Run и селектор под `slice::sort::shared::smallsort::verify::` | Свидетельство |
| --- | --- | --- |
| Exact `(1,13)`, actual битовый `Proof` | `45676394046` · `rev2_s13_binding::s13_base1_bits` | `VERIFIED`, 4/4 covers. Каноничность, порядок и popcount на всех 8192 масках, q-frame и V34 frame. |
| Exact `(1,17)`, actual битовый `Proof` | `45688753097` · `rev2_s13_geometries::s13_b01_l17_bits` | `VERIFIED`, 4/4 covers. Те же посты, включая четыре произвольных байта хвоста среза. |
| V34/base1, байтовый `Check` листа | `45661535099` · `rev2_provider_cost::s13_swap_leaf` | `VERIFIED`, 6/6 covers. Все 78 пар `0 ≤ a < b < 13`, числовые min/max, две цели записи, q-frame и frame остальных 32 байтов. |
| **Внешне перенесённая `(1,16)`**, левый actual N32 | Exact битовые опоры `(1,13)` и `(1,17)`, FIX3/base1, сверка исходника и индукция ниже | Составное свидетельство на входе `&mut v[1..17]`. Числовой порядок и полное мультимножество в `v[1..14]`, q-frame и frame всех 21 байта вне префикса. Нативный exact результат для `(1,16)` предстоит получить, если его потребует ревью. |

## Левый вызов actual N32

Вход — живой инициализированный `[u8; 34]` с произвольными байтами, эксклюзивный `&mut v[1..33]` и отдельный `&mut KeyLess::<u8>::with_q(q)` с независимым `q: u8`. `KeyLess::call_mut` выполняет cover и числовое `a < b` по полным байтам. Он сохраняет q и состояние массива. [Компаратор](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)

1. `small_sort_network` читает `len=32`. Нижний guard `len < 2` и верхний `len > SMALL_SORT_NETWORK_SCRATCH_LEN` ложны, поскольку scratch threshold равен 32. `len_div_2=16`, `no_merge=false`, `initial_region_len=16`. Первый `v_base` получен из входного среза и указывает на `v[1]`. `slice::from_raw_parts_mut(v_base, 16)` создаёт первый `region`, соответствующий `v[1..17]`. Предикат `region.len() >= 13` выбирает `sort13_optimal(region, is_less)` и устанавливает `presorted_len=13`. [Caller](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort.rs:367)
2. `sort13_optimal` возвращает с упорядоченным `v[1..14]`. В `v[14..17]` остаются исходные произвольные байты. Следом actual `insertion_sort_shift_left(region, 13, is_less)` начинает с `tail = v_base.add(13)`, шагом `add(1)` идёт до `v_end = v_base.add(16)` и вызывает actual `insert_tail` для rel13, rel14, rel15, то есть абсолютных 14, 15, 16. Здесь фиксируется граница входа в эти три вставки. Их посты входят в отдельный consumer. [Вставки](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort.rs:742)
3. После первых вставок при нормальном ходе `region.as_ptr()` по-прежнему указывает на левое начало. Следующий `region` строится из `v_base.add(16)` с длиной `32-16=16`, то есть `v[17..33]`. Правая S13-геометрия `(17,16)` отчётно exact в `45688753097`. Правая половина также получает вставки rel13–15. Далее actual caller передаёт обе половины в merge с отдельным stack scratch и копирует 32 байта обратно. Actual вставки обеих половин, предусловия merge, сам merge, copy-back и сквозной frame остаются рёбрами N32 consumer. [Правая геометрия](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md#покрытие-по-длинам-сети) · [Граница merge](REV2-MERGE-INVARIANT-REVIEW.md#до-допуска-n32)

## Привязка и перенос

**Длина и адреса.** Для каждого `L ∈ 13..=17` вход `&mut v[1..1+L]` даёт ложный `v.len() < 13`, после чего `sort13_optimal` один раз берёт `v.as_mut_ptr()`. Он получает тонкий указатель на `v[1]`. Весь остаток тела — один блок из 45 вызовов `swap_if_less(v_base, a, b, is_less)` без промежуточных операций. Проверка сравнила все пары литералов с `SWAP_PAIRS` FIX3 в порядке исполнения и проверила первый и четвёртый аргументы каждого вызова. Все вызовы получают тот же `&mut KeyLess<u8>`, а `swap_if_less` строит `v_a = v_base.add(a)` и `v_b = v_base.add(b)` и вызывает `is_less(&*v_b, &*v_a)`. У каждого вызова два различных адреса `v[1+a]` и `v[1+b]` в `[1,14)`. За guard длина нигде не используется, хвост нигде не читается и не пишется. [Guard и вызовы](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort.rs:597) · [Таблица FIX3](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:11) · [Тело swap](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort.rs:488)

**Доступ и область FIX3.** Каждый срез происходит из той же живой аллокации V34. У actual N32 указатель проходит через входной эксклюзивный срез, создание левой 16-байтовой области и reborrow у `sort13_optimal`. Все промежуточные области содержат префикс. При построении `region` родительский диапазон предоставляет эксклюзивный доступ на [1,17), а пока жив reborrow, к этим байтам обращаются через него. Объект компаратора хранится отдельно и получает только краткоживущие shared-ссылки на две цели до записей swap. Обе цели `u8` выровнены, в одной аллокации, допускают чтение и запись, смещения 0–12 остаются внутри объекта и укладываются в `isize`. Вызов листа из его harness использует `backing.as_mut_ptr().add(1)`. Для вызова через срез те же две цели доступны по собственной цепочке reborrow, поэтому выполняются safety и FIX3 requires на каждом вызове. Начальная инициализация дана fixture. `ptr::read` берёт инициализированный байт, а обе записи кладут валидные `u8`. Под cfg CAL1/CAL2/FIX3 предусловие листа проверяет специализацию `u8/KeyLess<u8>` через `exact_keyless_q`. [Предусловия swap](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort.rs:441) · [Геометрия и harness листа](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:90) · [Создание среза](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/raw.rs:193)

**Битовый пост.** Сравним два исполнения на V34 с одинаковыми 13 входными битами и q, при этом хвосты и все остальные внешние байты могут быть произвольными в каждом исполнении. Для любого `L=13..=17` начальный префикс одинаков, guard ложен. После шага `k` префиксы совпадают и остаются инициализированными, q каждого исполнения равен исходному, все внешние байты сохраняют свои значения. На шаге `k+1` совпадают относительные пары и значения на них. При канонических 0/1 min/max даёт AND/OR и канонические выходы. Лист и сохранение доступа устанавливают инвариант для следующего шага. Значит, после 45 шагов exact битовые посты `(1,13)` и `(1,17)` переносятся на `(1,16)` и остальные длины диапазона. Битовый пост означает маску из `13-popcount` нулей и `popcount` единиц от младшего адреса к старшему.

**Байтовый пост.** Фиксируем произвольный байтовый вход, q компаратора и порог `t ∈ 0..=255`. Проекция `B_t(x) = [x ≥ t]` переводит `min(x,y)` в `B_t(x) & B_t(y)`, а `max(x,y)` — в `B_t(x) | B_t(y)`. Индукция по тем же 45 вызовам связывает проекцию байтового префикса с каноническим битовым исполнением на проекции входа. В каждом шаге сохраняются доступ к префиксу, инициализированность, q и все байты `[0,1) ∪ [14,34)`, всего 21. Выбор `t` не участвует в исполнении, а компаратор сравнивает байты без чтения q, поэтому вывод для всех `t` относится к одному байтовому выходу. Инверсия `x>y` в выходе дала бы `1,0` при `t=x`. Для `C(t)=count(x≥t)` битовый popcount сохраняет `C(t)` при каждом `t`. Кратность `t<255` равна `C(t)-C(t+1)`, кратность 255 равна `C(255)`. Это даёт числовой порядок и полное мультимножество ровно 13 байтов, включая `count(<q)=13-C(q)` при исходном q. [Пороговый вывод](REV2-S13-BINDING-DESIGN.md#перенос-на-произвольные-байты)

## Воспроизводимая проверка привязки

Из корня g0 выполнить следующую команду с Python 3.10+ и Git.

```bash
python3 research/challenge-8/kani-k1/check_rev2_s13_left16.py \
  /root/verify-rust-std-rev2-s13-geometries-w14
```

```text
Pinned source and anchor fixtures match; actual N32 split 16+16; 45 ordered FIX3 calls
Extracted Boolean network: 8192/8192 masks match sorted popcount
```

Проверка сверяет цепочку и blobs в Git, содержимое файлов рабочего Std, разделение actual N32, полную форму тела S13 и расписание FIX3. Перебор 8192 масок подтверждает извлечённую булеву модель локально. Фиксация полного `smallsort.rs` требует повторной сверки при изменении любого из двух тел или самого caller, в том числе при объединении Std overlays. Изменения первой пары S13 и перестановки операндов компаратора swap проверены раздельно на временном файле. В обоих случаях скрипт завершился с `Re-audit required`. Статическая независимая сверка видела ту же область reborrow, тот же домен листа и ту же границу вставок. Пробела, требующего нативного exact root для внешней композиции, не выявлено.

## Запасной exact корень

Если ревью потребует нативное exact свидетельство `(1,16)` либо проверка при сборке consumer обнаружит неподтверждённую привязку, добавить следующий блок перед атрибутами `s13_b01_l17_bits` в `library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_geometries.rs`. При расхождении исходников применимость FIX3 надо подтвердить заново, включая тип, происхождение и доступность двух адресов.

```rust
#[kani::proof]
#[kani::unwind(36)]
fn s13_b01_l16_bits() {
    check_bits::<1, 16, false>();
}
```

| Параметр | Будущий exact корень |
| --- | --- |
| Слот и selector | `S13-B01-L16-BITS`, `slice::sort::shared::smallsort::verify::rev2_s13_geometries::s13_b01_l16_bits` с `--exact` |
| Режим | Plain `Proof`, `replace=[]`, `unwind(36)`, тот же stock/OB12 профиль. Ожидается `VERIFIED` и exit 0. |
| Метки постов | `REV2_S13_GEOMETRIES_Q_FRAME`, `REV2_S13_GEOMETRIES_V34_FRAME`, `REV2_S13_GEOMETRIES_CANONICAL_OUTPUT`, `REV2_S13_GEOMETRIES_SORTED_POPCOUNT` |
| Covers | 4/4 ожидаемых `REV2_S13_GEOMETRIES_MIXED_INPUT`, `REV2_S13_GEOMETRIES_INPUT_INVERSION`, `REV2_S13_GEOMETRIES_REACHED_POST`, `CAL1 q actual comparator executed` |
| Бюджет отбора | 180 с cold wall, VT ≤120 с, пик группы ≤4 GiB. Соседние exact `(1,13)` и `(1,17)` дали 37,53/41,73 с cold wall, 11,66/13,65 с VT и 2,09/2,10 GiB на Ubuntu. Для `(1,16)` это ориентир, измерение ещё открыто. |

**Статический аудит.** Это добавление шести строк внутри существующего opt-in модуля. `verify` под `cfg(kani)`, а `rev2_s13_geometries` под совместными `kani_smallsort_cal1`, `kani_smallsort_cal2_merge_mask`, `kani_smallsort_rev2_provider_cost`, `kani_smallsort_rev2_s13_binding`, `kani_smallsort_rev2_s13_geometries`. Все пять флагов уже в `check-cfg`. При всех флагах ожидается семь геометрических корней, из них пять Proof и два Check. Приватному корню доступен приватный `check_bits` в том же модуле. Существующие импорты разрешают `sort13_optimal` в предке `smallsort`, `KeyLess<u8>` и его методы в пределах `verify` и `crate::kani` для атрибутов. `BASE=1`, `LEN=16`, `CORRUPT_MASK=false` дают срез `[1,17)` внутри V34, все 13 инициализированных входных битов в префиксе и три произвольных байта хвоста. Атрибуты `#[kani::proof]` и `#[kani::unwind(36)]` используют тот же путь разрешения, что у соседнего `(1,17)`. В будущей упаковке с прежним контролем потребуется пересверить координаты поста, поскольку вставка сдвигает его на шесть строк. [Реестр и аудит пина](REV2-S13-GEOMETRIES-HANDOFF.md#разрешение-rust-имён-и-cfg)

Однофайловый diff и cfg проверены на временном варианте `rev2_s13_geometries.rs` поверх Std `217b8efaa6`. Команда `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --check --config use_small_heuristics=Max --edition 2024` прошла на этом файле. Std оставлен на исходных commit/tree/parent из таблицы, поскольку для внешней строки exact root пока не требуется. Локальный этап завершён до упаковки запуска. Нативный discovery, вердикт и ресурсы нового корня относятся к первому N32 consumer или отдельному GO после ревью. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)

`stub_verified(sort13_optimal)` требует отдельного успешного `proof_for_contract(sort13_optimal)` на достижимой области consumer с теми же `requires`, `modifies`, `ensures` и frame либо отдельно проверенного механизма композиции. Если самому Replace поручается полное мультимножество, его контракт должен обеспечивать все кратности в одном выходе. Нынешний CAL1 `count(<q)` на одном q такого обязательства на havoc не накладывает. Внешняя строка относится к наблюдаемому actual S13 и сохраняет `proof_credit=NONE`. [Граница Check → Replace](REV2-S13-BINDING-REVIEW.md#допуск-и-native-replace)
