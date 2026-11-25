# REV2 · handoff actual N32 consumer

Локальный кандидат содержит пару actual N32 на канонических битах и два plain-корня для вставок на полных байтах. Рекомендованный первый roster — все четыре корня. Exact нативный результат и составной допуск всей сети остаются открыты. `go=NOT_GRANTED`, `proof_credit=NONE`. [Задание](REV2-N32-CONSUMER-TASK.md) · [Утверждённое правило](REV2-COMPOSITION-RULE.md) · [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)

## Пины и область

| Роль | Идентичность |
| --- | --- |
| Задание / утверждение правила в g0 | `aa51bcd93740897dd34fcc25b02933dd7e574f8e` / `c61d7066338741b73299e428379aa4b6258f15af` |
| Входной g0 / исправления w15 | `5f981c3105585549b53b48fc0a4ff5d25f26e79c` включает `86f6ba877839f47c42181be9c97b36b72b2c64e7`. Перебор закоммичен и повторён. Список зависимостей расширен, SHA ролей заданы явно, receipt и projection сверены с индексом. |
| Std кандидат | `b93859fb447a39c0c8c7d854f70dedf9a47b263f`, tree `562a2fac5ed349a9fc09097789d0816f200c3819`, единственный parent `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a` |
| Std base | Tree `ff2563b5867b8327b95db909262ddf80e3ed9c03`. Цепочка parent — S13 binding `32c2857f4b7137601de54ea42a02610c8fd29ed9` / tree `0e682cfceaed5d33d3d3374b5dc97da5012bba93`, затем FIX3 `32129c149a15fb1b60a7314e738f3cb466d076e5` / tree `1b0cc32c571b370178e64f2b8c79773d2ce27051`. |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`, launcher 0.68.0 |
| Локальный checkout Std | `/root/verify-rust-std-rev2-n32-consumer-w14`, ветка `work/rev2-n32-consumer-w14`. Sparse checkout экономит место. Полное дерево доступно из Git. |

Домен произвольных байтов — initialized `V34: [u8; 34]`, эксклюзивный `&mut v[1..33]`, отдельно живой `KeyLess<u8>::with_q(q)` при независимом `q: u8`. Exact мономорфизация `small_sort_network::<u8, KeyLess<u8>>`. `KeyLess::call_mut` вычисляет числовое `a < b`, сохраняет q и операнды и не удерживает ссылок. `u8` удовлетворяет `FreezeMarker` через blanket impl. [Actual caller](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:367) · [Компаратор](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)

## Граф на полном байтовом домене

Интервалы полуоткрытые. При len=32 порог scratch равен 32, оба входных guard проходят и `no_merge=false`. Первый `from_raw_parts_mut` берёт 16 байтов от `v_base = &mut v[1]`. После левых S13 и вставок `region.as_ptr() == v_base`, поэтому `region` создаётся заново от `v_base.add(16)` с длиной 16. Предыдущий эксклюзивный регион больше не используется, ссылки из сравнений не сохраняются. После правых S13 и вставок `region.as_ptr() != v_base`, цикл заканчивается. `slice::from_raw_parts_mut(v_base, 32)` для merge снова охватывает весь активный срез. Обе пары call sites — `smallsort.rs:396,405`, затем merge и copy-back на `:424,425`. [Тело сети](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:374)

| Actual ребро | Pre, post и frame | Опора и состояние |
| --- | --- | --- |
| S13 слева `v[1..17]` | Инициализированный эксклюзивный срез, len16. 45 actual swap читают и меняют внутри `[1,14)`. Префикс возвращается инициализированным и численно упорядоченным с теми же кратностями. q и все байты вне префикса, включая `[14,17)`, сохранены. | Составное свидетельство. Exact битовые `(1,13)` и `(1,17)` и байтовый лист V34/base1. Принятый перенос по длине сохраняет исходный префикс, тонкий указатель, последовательность и доступ двух targets. Пороговый перенос применён к min/max каждого swap. [Ревью левого S13](REV2-S13-LEFT16-REVIEW.md) |
| Вставки слева `v[1..17]` | Sorted initialized prefix13 из S13, хвост произвольный. `insert_tail` на abs14,15,16 удлиняет упорядоченный префикс с сохранением его мультимножества, q и frame за каждым tail. Выход — sorted initialized `[1,17)`, остальные 18 байтов V34 и q сохранены. | Внешний вывод по exact телу ниже. Совпадающий нативный post открыт, минимальная проверка — `n32_insert_left_bytes` с native order/count/frame и useful return. |
| S13 справа `v[17..33]` | Левый вызов сохраняет всю правую половину. Те же 45 swap, цели в `[17,30)`, три хвостовых байта `[30,33)` и весь остальной V34 сохранены вместе с q. | Составное свидетельство exact `(17,16)` из run `45688753097`, слоты `S13-B17-L16-BITS`, `S13-B17-L16-SWAP` и различающий `S13-B17-L16-CORRUPT-MASK`. Пороговый перенос даёт числовой порядок и полное мультимножество префикса. [Анализ геометрий](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md) |
| Вставки справа `v[17..33]` | Sorted initialized prefix13 из S13, хвост произвольный. `insert_tail` на abs30,31,32 с теми же pre/post относительно правой базы. Sorted initialized `[17,33)` сохраняет своё полное мультимножество, q, готовую левую половину и оба внешних байта. | Тот же внешний вывод с exact правой геометрией. Совпадающий нативный post открыт, минимальная проверка — `n32_insert_right_bytes`. |
| Merge 16+16 на `v[1..33]` | Обе половины численно упорядочены. `MaybeUninit<[u8; 32]>::uninit()` создан внутри сети и живёт до copy-back. Тонкий `scratch_base` даёт writable 32 байта с выравниванием 1 в отдельной аллокации. Source initialized/readable, `len>=2`, `merge_geometry` и numeric halves выполнены. | `M32-PAIR-STEP` + принятая ранговая индукция на тех же blobs. Для каждой из 16 пар read cursors внутри соответствующих половин и пишутся только `D+k`, `D+31-k`. По выходе guard курсоров выполнен, нечётная ветка пропущена, все 32 байта scratch инициализированы и численно упорядочены с полным мультимножеством source. V34 и q сохранены. Whole merge return и инициализация — внешний вывод. [Handoff w15](REV2-MERGE-RANK-INDUCTION-HANDOFF.md) · [Независимое ревью](REV2-MERGE-RANK-INDUCTION-REVIEW.md) |
| Copy-back сразу после merge | На `smallsort.rs:425` actual `ptr::copy_nonoverlapping::<u8>(scratch_base, v_base, 32)`. Все `D[0..32)` читаемы и инициализированы. Exclusive `v[1..33]` доступен для 32 записей. Обе области живы, выровнены для u8 и принадлежат разным аллокациям. Запись целиком внутри активного среза, q и внешние байты сохранены. | Внешний вывод по normal-return post merge и семантике копии. Перенос значений и инициализации даёт `v[1..33]` порядок и полное мультимножество входного snapshot до сети. Exact native copy-back и наблюдаемый normal return ожидаются в битовой паре. [Примитив copy](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/ptr/mod.rs:475) |

Каждый нативный leaf Check доказывает свою exact роль и write set. Transfer использует те же инициализированные target/source позиции под действующими правами reborrow. [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md) определяет, как принимать общий ID повторных safety checks. Составной вывод использует обычный normal-return путь. При uninit/validity OFF инициализация выводится из семантики actual чтений и записей. Для нативной замены провайдера всё ещё нужен успешный согласованный Check на достижимом домене либо проверенная передача этого свидетельства в Replace. [Правило композиции](REV2-COMPOSITION-RULE.md)

### Шесть exact вставок

Инвентарь дал исторический `COMPACT-N32-ACT-INSERT-OB11`, run `44919643424` attempt 1, Std `e2bd3c6adc870729794a6b2fe44eece988402d8f`, tool `0aac16ef62da9e9d5645782d458593e5d78143ba`, OB11. Numeric merge Pre, offset guard, insert safety и whole-network q-post имеют `SUCCESS`. Numeric Pre проверяется после обеих actual вставок перед merge Replace. Whole-network post и frame относятся ко всей сети с Replace для S13 и merge. Этот receipt не изолирует полное мультимножество и frame на обеих границах вставок. На текущем Std/stock/OB12 найденные adjacent harnesses проверяют safety на других доменах. Поэтому нужны оба байтовых plain-корня в roster. [Исторический допуск](item2-audit-response-20261120/ADMISSION-N32.md#native-роли-consumer-и-контроля) · [Inventory](item2-audit-response-20261120/NATIVE-INVENTORY-N32.jsonl:1) · [Existing helper checks](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs:134)

Driver на `smallsort.rs:742–769` считает `v_end = v_base.add(16)` и начинает с `tail = v_base.add(13)`. На каждом из rel13–15 `begin < tail`, оба указателя получены из одного живого эксклюзивного среза. Весь `[begin,tail]` читаем, записываем и инициализирован, в том числе предшествующий упорядоченный префикс. После третьего шага `tail.add(1)` ровно one-past-end, его проверяют на равенство и не разыменовывают. [Driver](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:742)

Пусть на шаге с относительным tail `t` значение tail равно `x`. Если `x >= v[t-1]`, `insert_tail` возвращается сразу и уже упорядочен префикс до `t` включительно. Иначе `tail.read()` переносит `x` в отдельный `ManuallyDrop`, а логический gap начинается в `t`. Каждая копия переносит следующий больший байт из `sift` ровно на одну позицию вправо, затем guard переводит gap на `sift`. Копия длины 1 идёт между соседними различными позициями. Дальнейшие сравнения читают `tmp` и ещё не сдвинутого предшественника. Указатель уменьшается только после проверки `sift != begin`. Упорядоченность входа делает сдвигаемый отрезок ровно суффиксом `[j,t)` со значениями `> x`. На нормальном выходе из блока `CopyOnDrop` копирует `x` из отдельного `tmp` в `j`. Все прежние байты префикса до `j` сохранены, суффикс перенесён в `[j+1,t+1)`, и весь префикс до `t` включительно снова инициализирован и упорядочен. Записи ограничены `[begin,tail]`, чтения компаратора q не используют. Это индукционная предпосылка следующей вставки на каждой стороне. [Insert tail](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:701) · [CopyOnDrop](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:351)

Оба plain-корня задают arbitrary V34 и отдельный q, предполагают только sorted prefix13 в выбранной половине и проверяют порядок всех 16, `count(<q)` на полных половинах до и после, q и все байты вне половины. Если эти свойства пройдут, то при фиксированном байтовом входе actual выход один и тот же для всех q, поскольку actual сравнение и последовательность записей q не читают. Для `C(q)=count(byte<q)` кратность `b<255` равна `C(b+1)-C(b)`, а для 255 равна `16-C(255)`. Так универсальное нативное равенство счётчика по q переносится на полное мультимножество одного actual выхода. Нужны normal-return cover, safety и unwind checks на обеих геометриях. [Байтовые корни](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n32_consumer.rs:64)

## Exact roster и anchors

| Слот | Exact selector после `--harness` | Ожидаемый native исход |
| --- | --- | --- |
| `N32-INSERT-LEFT-BYTES` | `slice::sort::shared::smallsort::verify::rev2_n32_consumer::n32_insert_left_bytes` | Plain Proof, `VERIFIED`, exit 0 |
| `N32-INSERT-RIGHT-BYTES` | `slice::sort::shared::smallsort::verify::rev2_n32_consumer::n32_insert_right_bytes` | Plain Proof, `VERIFIED`, exit 0 |
| `N32-ACTUAL-BITS` | `slice::sort::shared::smallsort::verify::rev2_n32_consumer::n32_actual_bits` | Plain Proof, `VERIFIED`, exit 0 |
| `N32-ACTUAL-CORRUPT` | `slice::sort::shared::smallsort::verify::rev2_n32_consumer::n32_actual_corrupt` | Plain Proof, `FAILED`, exit 1, один ожидаемый `FAILURE` |

У всех четырёх Check отсутствует, `replace=[]`, стубы пусты. `H` ниже — `library/core/src/slice/sort/shared/smallsort/verify/rev2_n32_consumer.rs`. Пара исполняет одну общую функцию `check_network` с разными значениями const `CORRUPT`. Домен — все `2^32` масок канонических байтов, произвольные `v[0],v[33]` и q. На `H:36` вызов actual сети, единственное изменение в контроле — `backing[1] ^= 1` на `H:43` после возврата. Во время сети промежуточных `assume` нет. Маска ожидаемого ответа имеет popcount входа и единицы на старших позициях. Сдвиг выполняется в u64 и определён и при popcount32. Если actual output удовлетворяет oracle, инверсия канонического нулевого бита маски меняет popcount на единицу и сохраняет каноничность. [Общая функция пары](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n32_consumer.rs:23)

| На каких roots | Обязательный anchor в regular | Ожидание |
| --- | --- | --- |
| Обе стороны пары | `REV2_N32_ACTUAL_AFTER_COPY_BACK` `H:38:5`, `REV2_N32_ACTUAL_MIXED_INPUT` `H:39:5`, `REV2_N32_ACTUAL_LEFT_INSERT` `H:40:5`, `REV2_N32_ACTUAL_RIGHT_INSERT` `H:41:5`, `CAL1 q actual comparator executed` `cal1_model.rs:28:9` для `KeyLess<u8>::call_mut` | Все пять `SATISFIED`. Первые четыре стоят после actual call и до порчи. |
| Обе стороны пары | `REV2_N32_ACTUAL_Q_FRAME` `H:45:5`, `REV2_N32_ACTUAL_V34_FRAME` `H:46:5` | Оба `SUCCESS`, после возможной порчи. |
| Бит positive / corrupt | `REV2_N32_ACTUAL_CANONICAL_SORTED_POPCOUNT` `H:54:5`, класс `assertion` | Positive `SUCCESS`. В corrupt только этот `FAILURE`. Ожидаемый символ — `…::rev2_n32_consumer::check_network::<true>`. Точный native ordinal ещё `UNKNOWN`, сверяется по обоим каналам. |
| Обе вставки | `REV2_N32_INSERT_NUMERIC_ORDER` `H:86:5`, `REV2_N32_INSERT_COUNT_BELOW_Q` `H:87:5`, `REV2_N32_INSERT_Q_FRAME` `H:91:5`, `REV2_N32_INSERT_V34_FRAME` `H:92:5` в `check_insertions::<1/17>` | Все четыре `SUCCESS`. |
| Обе вставки | `REV2_N32_INSERT_SHIFT` `H:96:5`, `REV2_N32_INSERT_NORMAL_RETURN` `H:97:5`, `CAL1 q actual comparator executed` `cal1_model.rs:28:9` | Все три `SATISFIED`. |

`LEFT_INSERT` и `RIGHT_INSERT` — условия на вход, наблюдаемые после общего возврата. Первый хвост есть bit13 слева и bit29 справа. Если он нулевой и в соответствующем prefix13 есть хотя бы одна единица, actual S13 ставит единицу на rel12 и сохраняет хвост. Тогда первое сравнение в `insert_tail` на rel13 истинно и путь через сдвиг исполнен. Вывод привязан к exact S13 на обеих геометриях и к проверкам `smallsort.rs:705–722`. Для произвольных байтов используются pre/post рёбер из таблицы. Вставка и merge сравнивают полные байты и могут выбрать разные пути при равенстве пороговых проекций. [Условия covers](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n32_consumer.rs:38)

В обоих каналах нужны завершённые regular/stock результаты, совпадающие verdict, категории и counts по общему формату. Сверять exact root и location stock, cover IDs/status и единственный corrupt ID, class, file suffix и line в regular и export, колонку 5 в regular. Успех frame и других assertions привязывать по regular, stock сверяет доступные агрегаты. Сохранять native safety, overflow, unwind, undefined-function и reachability результаты. Для exact body связать reported safety anchors с `from_raw_parts_mut` на `smallsort.rs:391,416,424`, `insert_tail` на `:764`, actual merge pair helpers `:1023,1024`, guard `:1042` и `copy_nonoverlapping::<u8>` на `:425`. Нативные группы pointer/safety и copy precondition имеют общие IDs. Привязка к конкретным вызовам опирается на точные аргументы, режим Original, unwind без отсечения и cover после copy-back. Сверять реально напечатанные anchors и `UNREACHABLE`, включая объяснение guard-путей. Исторические ordinals чужих корней не переносить. [Правило grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md) · [Прецедент exact N32](item2-audit-response-20261120/ADMISSION-N32.md#native-роли-consumer-и-контроля)

## Rust, cfg и проверка привязок

| Имена | Разрешение и видимость |
| --- | --- |
| `rev2_n32_consumer`, четыре entry points, `BACKING_LEN`, `HALF_LEN`, `PREFIX_LEN`, `check_network`, `first_tail_moves`, `check_insertions`, `numeric_order`, `count_below` | Новый модуль приватен у `verify`, все определения приватны в новом модуле. Корни отмечены `#[kani::proof]` и `#[kani::unwind(36)]`. `CORRUPT: bool` и `BASE: usize` — локальные const-параметры, обе подстановки каждого заданы явно. Переменные ограничены своими блоками и функциями. Путь `crate::slice::sort` публичный, `shared::smallsort` виден в crate, `smallsort::verify` доступен его потомкам при `cfg(kani)`. |
| `super::super::{insertion_sort_shift_left, small_sort_network}` | Оба имени из предка `smallsort`, приватный `small_sort_network` доступен потомку, driver объявлен `pub` внутри этого предка. Типы выводятся из `&mut [u8]` и `&mut KeyLess<u8>`. |
| `super::cal1_model::KeyLess`, `with_q`, `q` | `cal1_model` — приватный модуль общего предка `verify` под CAL1. Тип `pub(in crate::slice::sort::shared::smallsort)`. Методы `pub(super)` видимы в `verify` и его потомках. Используется публичный trait метод `FnMut::call_mut`, `fn_traits` включён в lib при Kani/CAL1. |
| `crate::kani`, `proof`, `unwind`, `any`, `assume`, `assert`, `cover` | Kani facade создаёт `kani_core::kani_lib!(core)` при `cfg(kani)`. `kani_core` и его re-export макросов открывают атрибуты, функции и `Arbitrary` для u8, u32 и массивов. |
| Индексы, срезы, наблюдатели | Публичные операции примитивов, срезов, пар и trait-методы prelude. Shift output/input mask идёт по позициям 0–31, `count_ones` в 0–32 и применяется к сдвигу u64. `u32::from` и `u8::from` получают u8 и bool соответственно. `numeric_order` читает соседние элементы в пределах 13 или 16. `count_below` ограничен 16, индексы `BASE+PREFIX_LEN` и `BASE+HALF_LEN` в V34. |

Активный набор — `kani_smallsort_cal1`, `kani_smallsort_cal2_merge_mask`, `kani_smallsort_rev2_provider_cost`, `kani_smallsort_rev2_s13_binding`, `kani_smallsort_rev2_s13_geometries`, `kani_smallsort_rev2_n32_consumer`. Первые пять совпадают с геометриями S13. Новая регистрация требует все шесть, `Cargo.toml` добавляет только декларацию check-cfg. Merge loop invariant w15 отсутствует в pinned `smallsort.rs`, флаг `kani_smallsort_rev2_merge_invariant` выключен. CAL1/FIX3 function contracts остаются в источнике, exact roots исполняют Original с `--no-assert-contracts`. При cfg-off статически восстановлены точные blobs реестра и manifest после вычитания нового блока и строки, без операционных изменений. Native discovery и compile ещё предстоят. [Реестр](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify.rs:114)

| Ключевой blob | SHA Git |
| --- | --- |
| `smallsort.rs`, включает все actual call sites, guard drop, S13 и merge helpers | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `cal1_model.rs` / `cal1_q_merge_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` / `d3c2a137f7332d79e7ce8596a517fd8b5f2dbe19` |
| `rev2_provider_cost.rs` / `rev2_s13_binding.rs` / `rev2_s13_geometries.rs` | `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` / `8718e67a68f473a6e7367d168a34410f40d324eb` / `c403b343270752fb03fc087a101b55d8dc20a7ab` |
| `rev2_n32_consumer.rs` / `verify.rs` / `core/Cargo.toml` кандидата | `7c7823d549dbd2203f3dd8f0b1307b618c474f53` / `0a6f285b719c84c8f009c1040ab99393893a823d` / `08e863f00173a3791e08e1a3245b3d2928d7ff3f` |
| `ptr/mod.rs` / `mem/maybe_uninit.rs` / `slice/raw.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` / `401f93066fb8c3236a4038f8728c04b91eea0d75` / `154c5356d99ee7edcb395e2c364a8e2ac22a9375` |

Следующая сверка сравнивает разные роли фиксированными SHA. Выполнить в sparse worktree Std, без развёртывания дерева.

```bash
(
    set -euo pipefail
    candidate=b93859fb447a39c0c8c7d854f70dedf9a47b263f
    base=217b8efaa6c9c0d6e5d44f77e98d74bd5493360a
    binding=32c2857f4b7137601de54ea42a02610c8fd29ed9
    fix3=32129c149a15fb1b60a7314e738f3cb466d076e5
    test "$(git show -s --format='%T %P' "$candidate")" = "562a2fac5ed349a9fc09097789d0816f200c3819 $base"
    v=library/core/src/slice/sort/shared/smallsort/verify
    set -- library/core/src/{lib,cmp,slice/mod,slice/raw,slice/index,slice/iter,slice/iter/macros}.rs \
        library/core/src/{iter/range,iter/traits/iterator,num/uint_macros,mem/mod,mem/manually_drop,mem/maybe_uninit,ub_checks,intrinsics/mod}.rs \
        library/core/src/ptr/{mod,const_ptr,mut_ptr}.rs \
        library/core/src/slice/sort/shared/{mod,smallsort}.rs \
        "$v"/{cal1_model,cal1_q_merge_model,rev2_provider_cost}.rs
    git diff --exit-code "$fix3" "$candidate" -- "$@"
    git diff --exit-code "$binding" "$candidate" -- "$v/rev2_s13_binding.rs"
    git diff --exit-code "$base" "$candidate" -- "$v/rev2_s13_geometries.rs"
    git diff --check "$base" "$candidate"
    git diff --name-status "$fix3" "$candidate"
    git diff "$base" "$candidate" -- library/core/Cargo.toml "$v.rs"
    git ls-tree -r "$candidate" -- "$@" "$v"/rev2_s13_{binding,geometries}.rs "$v/rev2_n32_consumer.rs"
    rustfmt_bin=/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt
    "$rustfmt_bin" --edition 2024 --config use_small_heuristics=Max --check "$v/rev2_n32_consumer.rs"
    "$rustfmt_bin" --edition 2024 --config use_small_heuristics=Max,skip_children=true,reorder_modules=false --check "$v.rs"
)
```

Полная дельта от FIX3 состоит из manifest и реестра, изменённых только для регистрации трёх opt-in модулей, и файлов этих модулей. Обе целевые проверки rustfmt, `git diff --check` и статическая сверка layout прошли. В `verify.rs` зафиксирован унаследованный порядок модулей, а новый дочерний файл проверяется адресно. Рекурсивный default check затронул унаследованные `verify.rs` и `cal1.rs`, где форматтер предлагает перестановку модулей и импортов. В g0 повторены `check_rev2_s13_left16.py /root/verify-rust-std-rev2-s13-geometries-w14` (45 exact вызовов и 8 192 маски) и `check_rev2_merge_rank_induction.py` (23 409 пар, все 17 разрезов). Синтетическая модель вставки проверила 35 840 вариантов на `{0,1,254,255}` и формула oracle проверена на всех 33 popcount и их инверсиях младшего бита. Это проверка рассуждений, доказательная область берётся из pinned тел и нативных опор. [Проверка S13](check_rev2_s13_left16.py) · [Проверка merge](check_rev2_merge_rank_induction.py)

## Сверенный нативный профиль и первый будущий пакет

Для семи строк ниже сверены receipt/projection по размеру и SHA-256 из индексов, trigger tree и parent из Git, frozen request blob и stock tool tree. Regular и stock export полны. Идентичны exact singleton, jobs=1, `--no-assert-contracts`, resolved unwind36, OB12, CBMC 6.11.0, CaDiCaL 3.0.0. Memory safety, overflow, unwinding, undefined-function и assertion-reach checks ON, uninit/validity OFF. `Proof` и `Check` ниже передают фактическую роль, Replace пуст во всех строках. Все run — Ubuntu X64, attempt 1. [Индекс binding](/root/ch8-artifacts/run-45676394046/ch8-rev2-s13-binding-Linux-X64-45676394046-1/index.json) · [Индекс геометрий](/root/ch8-artifacts/run-45688753097/ch8-rev2-s13-geometries-Linux-X64-45688753097-1/index.json) · [Индекс FIX3](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/index.json)

| Run | SHA-256 локального индекса, поле `members` содержит точные member digests |
| --- | --- |
| `45676394046` | `bcb05483715c3b6067586c26059f2b341f84b6c3a6b5ba7018db0395258f89d6` |
| `45688753097` | `e575daf8b20bab3c3023b8809e61cc21ea1a4bf9be85153d572368e6bbf663b7` |
| `45661535099` | `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be` |

| Run / slot | Роль и завершённый вердикт | Привязанные anchors |
| --- | --- | --- |
| `45676394046` / `S13-BASE1-BITS` | `rev2_s13_binding::s13_base1_bits`, Proof SUCCESS | `check_s13_base1::<false>.assertion.3/.6/.8/.9` q/frame/canonical/mask `SUCCESS`, 4/4 covers. |
| `45688753097` / `S13-B01-L17-BITS`, `S13-B17-L16-BITS` | `rev2_s13_geometries::s13_b01_l17_bits` и `s13_b17_l16_bits`, Proof SUCCESS | `check_bits::<1,17,false>` и `check_bits::<17,16,false>`, в обоих `.assertion.5/.8/.11/.12` q/frame/canonical/mask `SUCCESS`, 4/4 covers каждый. |
| `45661535099` / `S13-SWAP-LEAF` и `45688753097` / `S13-B17-L16-SWAP` | `rev2_provider_cost::s13_swap_leaf` и `rev2_s13_geometries::s13_b17_l16_swap`, Check `swap_if_less` SUCCESS | `smallsort.rs:467` Check single call, `memcpy/memmove.assigns.1–2` SUCCESS, harness `.assertion.1/.14/.19` q/min-max/byte frame в `s13_swap_leaf` и `assert_swap_post::<17>`, 6/6 covers каждый. |
| `45688753097` / `S13-B17-L16-CORRUPT-MASK` | `rev2_s13_geometries::s13_b17_l16_corrupt_mask`, Proof FAILURE | Только `check_bits::<17,16,true>.assertion.12`, `REV2_S13_GEOMETRIES_SORTED_POPCOUNT`, `rev2_s13_geometries.rs:69:5`. Остальные post/frame SUCCESS, 4/4 covers. Историческая порча наблюдаемой маски. |
| `45661535099` / `M32-PAIR-STEP` | `rev2_provider_cost::m32_pair_step`, Check `actual_pair_step` SUCCESS | `.assertion.1–3` applicability, `.14–17` value and frame. Check-wrapper `.assertion.7/.10` курсоры, `memcpy.assigns.1–2` цели, `copy_nonoverlapping` preconditions. 11/11 covers, 4/4 unwind goals. [Точные native ID и координаты](REV2-MERGE-RANK-INDUCTION-HANDOFF.md#нативные-anchors-и-их-роль) |

Предложение — один будущий Ubuntu пакет после утверждения roster и отдельного GO, четыре singleton в указанном порядке. Изолированные byte roots дешевле по структуре, каждый исполняет три вставки и обходы наблюдателей. Измеренного ресурса для них пока нет. Исторические bit S13 дают 37,52–41,73 с cold wall и ~2,09–2,20 GiB, однако whole N32 добавляет вторую S13, шесть вставок, 16 пар merge и copy-back. FIX3 `M32-PLAIN-MASK` на полных байтах исчерпал 180 с после symex/SSA и начала решения. Инвариантный whole merge исчерпал 180 с в symex. Эти результаты задают риск, время и RSS новой пары пока неизвестны. **Предел на слот** — 180 с cold wall, VT ≤120 с, RSS группы ≤4 GiB, резерв Ubuntu 2 GiB. Если пара упрётся в ресурс, зафиксировать отдельно исход процесса, последнюю подтверждённую стадию и маркеры compilation/symex/SSA/SAT, RSS, VT при наличии и отсутствующие post/cover/control anchors. Exact native путь или различающий отказ остаются открыты до завершённого результата. [FIX3 замеры](REV2-NETWORK-PROVIDERS-RESULTS-ANALYSIS.md) · [Инвариантный cutoff](REV2-MERGE-INVARIANT-RESULTS-ANALYSIS.md)

Для будущего control использовать проверенный FIX1 каркас и сохранить следующие условия.

- Gate `pins` и `finish` независимо вычисляют tree фактического trigger checkout и сравнивают с отдельно установленным review pin. SHA event/payload и sole parent, clean detached tree, immutable request digest, tool pin и Std overlay commit/tree проверяются своими путями. Подстановка одновременно согласованных event SHA и request не заменяет внешний tree pin. `finish` повторно сверяет начальный admission receipt.
- Предварительный exact `core` compile witness и discovery сверяют четыре новые Proof, ноль Check/Replace, ожидаемые наследуемые регистрации и отсутствие нового модуля при отключённом opt-in. Roster исполнения задаётся зафиксированным request, а не результатом discovery. На каждый слот отдельные cargo/kani target, TMPDIR и экспорт. Сохранять effective flags и профиль с обоих нативных каналов.
- При 180 с cold wall заложить 10 с reap, 5 с на receipt и 10 с на latest-start headroom. От epoch первого шага предложенный верхний бюджет — 45:00 setup, 13:40 на четыре слота, 2:00 аттестация, 5:00 finish и 7:00 upload, 9:00 reserve. Сумма 81:40 помещается в 90:00. Внешний timeout каждого шага должен вмещать его внутренний бюджет с запасом. Для FIX1-разбивки measure включает аттестацию, значит внутренние 15:40 требуют хотя бы 16 минут. Для finish 5 минут оставляют 10 с к внутреннему пределу 290 с от входа в CLI. Его также ограничивает общий receipt publication deadline. Глобальное окно отсчитывается от того же epoch. Для prepare и setup steps сверить эту же иерархию по фактической разбивке.
- Дедлайн receipt определяется раньше из `supervisor_return + 5s` и конца окна слота. Сначала атомарный checkpoint наблюдённого exit, стадии, reap/containment и часов, затем bounded projection с запасом до receipt deadline. Просрочка или неполнота блокирует paired acceptance с сохранением настоящего исхода процесса. Повторная запись в finish сохраняет отметку просрочки. Удаление partial files использует отдельное имя уровня `partial_path`, словарь pending receipts остаётся доступен. Upload разрешён только после успешных gate и finish.
- Синтетика должна начинать тесты со свежей монотонной шкалы, подменяя все связанные чтения clock, включая finish, latest start и publication. Проверить раннюю и позднюю границы, timeout каждого шага и завершение вне дедлайна, развилки stale/wrong tree, missing/partial/type mismatch, исходный exit и receipts после reap, `NOT_STARTED` после неподтверждённого reap. Отдельно воспроизвести partial file при одновременно pending receipt, включая сохранение исходного verdict, затем проверку index hash. [FIX1 и регрессии](REV2-S13-GEOMETRIES-HANDOFF.md#fix1)

Стадия завершается передачей на независимое ревью. Control, trigger и GO относятся к следующей стадии. Локально использованы Git, Python и указанный rustfmt. Cargo, rustc, Kani, CBMC, CI, push и публикация отсутствовали.
