# REV2 · сквозные N18/N19 с различающими контролями

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** Один локальный Ubuntu-пакет из четырёх exact singleton для actual `small_sort_network::<u8, KeyLess<u8>>`. Положительные корни берут все канонические входы, отрицательные меняют первый активный байт после actual возврата. Пост для произвольных `u8` опирается на нативные опоры и приведённые ниже внешние рёбра. Новые нативные исходы, ресурсы и допуск открыты. [Задание](REV2-N18-N19-CONSUMER-TASK.md) · [Разбор опор](REV2-N18-N19-PROVIDERS-RESULTS-ANALYSIS.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Рёбра N18

| Ребро | Привязка на pinned Std |
| --- | --- |
| Вход и presort | Инициализированный V34, `&mut v[1..19]`, независимый q и числовое `KeyLess<u8>`. При `len=18` на `smallsort.rs:385–416` получаем `len_div_2=9`, `no_merge=false`, сначала `v[1..10]`, затем `v[10..19]`. Actual вызов :399 берёт `sort9_optimal` дважды. Слева применяются `S9-B01-L09-BITS` и FIX3 `S13-SWAP-LEAF` на base 1. Справа `S9-B10-L10-BITS` и `S9-B10-SWAP` на base 10 переносятся с длины 10 на 9. Guard :542 проходит, base и provenance сохраняются. Все 25 actual пар :553–577 берут два различных rel0–8. Пороговый перенос даёт числовой порядок и полные кратности каждого из двух префиксов длиной 9. |
| Вставки | В обоих вызовах :405 `offset=9=len`. В driver :758–764 получаем `tail==v_end` при входе, поэтому `insert_tail` не вызывается. Оба numeric/multiset поста sort9 и внешний frame передаются в merge. |
| Merge | `M18-M19-PAIR-STEP` применяется при N=18 ко всем девяти actual парам :1022–1025. Записи `D[0..9]` и `D[9..18]` устанавливают ранги 0–17 и полную инициализацию. Ранговая индукция даёт `a+c=b+d=9`. Отсюда `left=S+a=S+9-c=left_end` и `right=S+9+b=S+18-d=right_end`. Odd branch :1031 пропущена, guard :1042 допускает normal return. |
| Copy-back и пост | :425 копирует ровно 18 инициализированных байтов `D[0..18]` в `v[1..19]`, передавая числовой порядок и исходные кратности. `v[0]`, `v[19..34]` и q сохранены. Новый positive связывает grouped copy properties и `AFTER_COPY_BACK` на пути normal return. Контроль проверяет тот же пост на маске `0x0000_0201`. |

## Рёбра N19

| Ребро | Привязка на pinned Std |
| --- | --- |
| Вход и presort | Инициализированный V34, `&mut v[1..20]`, тот же тип и независимый q. На :385–416 `len_div_2=9` и `no_merge=false`. Actual :399 вызывается на `v[1..10]` и `v[10..20]`. Слева применяются `S9-B01-L09-BITS` и FIX3 `S13-SWAP-LEAF` на base 1. Справа `S9-B10-L10-BITS` и `S9-B10-SWAP` имеют exact base 10 и длину 10 для корня sort9. Все 25 пар работают на rel0–8. Правый префикс `v[10..19]` упорядочен и сохраняет кратности, `v[19]` остаётся произвольным входным байтом. |
| Вставки | Левый driver :405 пуст на len9. Справа :758–764 стартует с `tail=v_base+9` при len10. Единственный actual :764 берёт rel9 / abs19, затем :767 доводит `tail` до `v_end`. Numeric sort9 post устанавливает предпосылку `N19-INSERT-RIGHT-BYTES` на том же `v[10..20]` и offset 9. Порядок, равенство `count(<q)` и оба frame передаются в merge. Из q-независимости результата следует мультимножество правых десяти байтов. |
| Merge · девять пар | `M18-M19-PAIR-STEP` применяется при N=19. Actual пары :1022–1025 пишут `D[0..9]` и `D[10..19]`, то есть ранги 0–8 и 10–18. После них `9-a-c` и `10-b-d` неотрицательны и суммируются в 1. Source, q и написанные края D сохраняются. |
| Merge · центр и guard | `dst=D+9`. Actual :1027–1036 вычисляет `left_end=S+9-c`, `right_end=S+19-d`, выбирает единственный остаток сравнением `left < left_end`, копирует его в `D[9]`, увеличивает соответствующий прямой курсор. `M19-ODD-CENTER` связывает этот переход по value/cursors/frame через локальный `Check actual_odd_center`, чья транскрипция на :327–339 в модуле опор восстанавливает те же указатели. В actual сети вызов происходит внутри `bidirectional_merge` и использует курсоры реального цикла. Оба конечных равенства из Check делают :1042 ложным. Полностью заполнен `D[0..19]`. |
| Copy-back и пост | :425 копирует ровно 19 инициализированных байтов `D[0..19]` в `v[1..20]`, с передачей порядка и всех кратностей. `v[0]`, `v[20..34]` и q сохранены. Positive исполняет actual odd branch на битах. Контроль берёт `0x0003_ffff`, full shift справа и odd остаток слева. |

### Внешние шаги для полных байтов

На каждой базе домен byte leaf охватывает все 25 пар, использует два выровненных живых адреса V34 и меняет только целевые ячейки. Порог `Pₜ(x)=[x>=t]` переводит min/max в AND/OR. Индукция по одному actual расписанию связывает проекцию произвольных байтов с битовым sort9. Numeric inversion проявилась бы на пороге большего байта. Равенство всех пороговых счётчиков даёт равенство кратностей. У byte driver N19 actual `KeyLess<u8>::call_mut` сравнивает только два байта, поэтому для фиксированного V34 результат один для всех q. Из `C(q)=count(byte<q)` кратность `b<255` равна `C(b+1)-C(b)`, а кратность 255 равна `10-C(255)`. [Расписание и перенос длины](REV2-N18-N19-PROVIDERS-HANDOFF.md#presort-и-правая-вставка) · [Actual компаратор](/root/verify-rust-std-rev2-n18-n19-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)

Пусть `S=v_base`, `D=scratch_base`. Счётчики `a,b` и `c,d` относятся соответственно к снятию спереди и сзади из L/R. В начале пары `k<9` имеем `a+b=c+d=k`. Actual проекции :1014–1025 совпадают с доменом `actual_pair_step`: `(S+a,S+9+b,D+k)` и `(S+8-c,S+N-1-d,D+N-1-k)`. Четыре source указателя остаются в bounds, две цели различны, disjoint от S и от прежних записей в D. В порядке `(byte, индекс на входе merge)` up выбирает меньший фронт, на tie левый, то есть ранг k. Down выбирает больший задний, на tie правый, то есть ранг `N-1-k`. Каждый проход по своему фронту продолжает снимать глобальные ранги в принятом направлении. Низкие и высокие ранги не пересекаются за девять пар, поэтому суммарное потребление не превышает длину ни одной половины. У N19 это устанавливает предпосылки odd Check для единственного остатка, включая случай `c=9`.

Обе безусловные копии пары на :885 и :918 и копия центра на :1034 пишут живые байты из S. Индукция по write set и семантика этих записей дают initialized `D[0..N]` при `uninit/validity OFF`. Для :425 `size_of::<u8>()=align_of::<u8>()=1`, `N*1` равно 18 или 19, не превышает `isize::MAX` и ёмкость 32. `D` получен из отдельного живого stack allocation `MaybeUninit<[u8;32]>` на :383/:423. `S` получен из активного эксклюзивного slice на :388 и сохраняет его provenance после временного reborrow merge. Обе области выровнены, `D[0..N]` readable, `v[1..1+N]` writable. Отдельные живые allocations дают disjointness, независимо от значений. :425 следует сразу за normal return merge, а helper продолжает с cover только после возврата сети. Этот аргумент переносит применимость copy-back и frame на полный байтовый домен без сопоставления промежуточных решений битовой и байтовой трасс. [Actual copy-back](/root/verify-rust-std-rev2-n18-n19-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:425) · [Pinned intrinsic](/root/verify-rust-std-rev2-n18-n19-consumer-w14/library/core/src/ptr/mod.rs:587) · [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

## Exact roster и anchors

Префикс exact selector `slice::sort::shared::smallsort::verify::rev2_n18_n19_consumer::`. Все четыре корня имеют stock kind `Proof`, unwind36. Положительные передают независимые младшие 18 или 19 бит `kani::any::<u32>()`. Все корни используют произвольные внешние байты V34 и отдельный q. Порча `v[1] ^= 1` стоит после covers и до тех же assertions. Общий на каждой длине assert требует каноничность и маску `LOW_N ^ (LOW_N >> popcount(input))`. q-frame и V34 frame проверяются отдельно. [Корни](/root/verify-rust-std-rev2-n18-n19-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n18_n19_consumer.rs) · [Frozen request](/root/kani-rev2-n18-n19-consumer-control-w14/ch8-cal1/CI-REQUEST.json)

| Слот · суффикс selector | Ожидаемый нативный исход | Вход · ожидаемая маска до и после инверсии |
| --- | --- | --- |
| `N18-ACTUAL-BITS` · `n18_actual_bits` | `VERIFIED`, exit 0 | Все 2¹⁸ |
| `N18-WITNESS-CORRUPT` · `n18_witness_corrupt` | `FAILED`, exit 1, один failure на общем посте | `0x0000_0201` · `0x0003_0000` → `0x0003_0001` |
| `N19-ACTUAL-BITS` · `n19_actual_bits` | `VERIFIED`, exit 0 | Все 2¹⁹ |
| `N19-WITNESS-CORRUPT` · `n19_witness_corrupt` | `FAILED`, exit 1, один failure на общем посте | `0x0003_ffff` · `0x0007_fffe` → `0x0007_ffff` |

| Корни | Метки и regular координаты |
| --- | --- |
| Оба N18 | Префикс `REV2_N18_ACTUAL_`. `AFTER_COPY_BACK` :46:5, `MIXED_INPUT` :47:5, `Q_FRAME` :51:5, `V34_FRAME` :52:5, `CANONICAL_SORTED_POPCOUNT` :54:5. Exact native функция `check_n18::<false>` или `check_n18::<true>`. |
| Оба N19 | Префикс `REV2_N19_ACTUAL_`. `AFTER_COPY_BACK` :66:5, `MIXED_INPUT` :67:5, `RIGHT_FULL_SHIFT` :69:5, `ODD_LEFT_REMAINDER` :71:5, `Q_FRAME` :82:5, `V34_FRAME` :83:5, `CANONICAL_SORTED_POPCOUNT` :85:5. Exact native функция `check_n19::<false>` или `check_n19::<true>`. |
| Только N19 positive | `REV2_N19_ACTUAL_ODD_RIGHT_REMAINDER_LEFT_REVERSE_SENTINEL` :74:5. При `0x0000_01ff` слева девять единиц и справа десять нулей. Все девять down берут слева, `c=9`, `left_rev=S-1`. :1027 использует только wrapping-переход обратно к S. Up берёт девять справа, поэтому :1032–1036 выбирают правый остаток. |
| Все четыре | `CAL1 q actual comparator executed` на `cal1_model.rs:28:9` в actual `KeyLess<u8>::call_mut`. |

Для `RIGHT_FULL_SHIFT` все девять бит правого префикса равны 1, rel9 равен 0. На :722–731 сохранённый ноль сдвигает все девять единиц, затем drop :362 заполняет первый правый байт. При `0x0003_ffff` упорядоченный левый ряд состоит из единиц, правый из нуля и девяти единиц. Up берёт правый ноль и восемь левых единиц, down снимает девять правых единиц на tie, остаётся одна левая единица для `D[9]`. Covers фиксируют вход и достижение post-return. Привязка к actual курсорам и сдвигу следует из pinned исходника.

Ожидаются 3/3, 3/3, 6/6 и 5/5 обязательных covers в порядке roster. Valid positive требует regular `SUCCESS` на трёх assertions, stock `COMPLETED/SUCCESS`, согласованные агрегаты и достигнутые stock cover IDs. В обоих отрицательных roots q и frame имеют `SUCCESS`, stock terminal `COMPLETED/FAILURE`, а единственная `FAILURE` в обоих каналах имеет один и тот же ID класса `assertion`, свою метку, файл/строку и exact regular helper. Числовой суффикс ID сверяется после нативного прогона. Safety, overflow и unwind не могут дать дополнительный отказ. Positive copy anchors на `ptr/mod.rs:587:14` обязательны для обеих длин:

- `ptr::copy_nonoverlapping::<u8>.precondition_instance.1/.2/.3` с disjoint/readable/writable descriptions.
- Тот же префикс у `.safety_check.1/.2` для выравнивания и `.arithmetic_overflow.1` для длины в байтах.

Группы сохраняются в `result_evidence.mandatory_anchors.regular_properties` в receipt и projection, с ID, статусом, описанием и location. Projection сохраняет `stock.terminal`, failure и cover buckets, totals и regular свойства. RFC 0015 даёт агрегат успешных checks, который сверяется с regular. Grouped ID охватывает вызовы данного intrinsic, а доходимость именно :425 следует из `AFTER_COPY_BACK` и исходникового порядка. [Сверка и проекция](/root/kani-rev2-n18-n19-consumer-control-w14/ch8-cal1/results.py:213) · [Прецедент N32](REV2-N32-ADMISSION.md#привязка-строки)

## Идентичности и исторические опоры

| Роль | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Вход задания g0 | `8c588134dd150149a079ec54fbe0f5f3396bdaf1` | `98e4de815064250d10480689b004d4c98eec81e6` | `16a63a161753bcfd3aefc4c0648b18cdb16ddaed` |
| [Std candidate](/root/verify-rust-std-rev2-n18-n19-consumer-w14) · `work/rev2-n18-n19-consumer-w14` | `a6f189eecbee57fe7517547bf7461c9dd2897e27` | `4f149dce6a6a5663eb55cc526a880474aac7ca16` | `86ea7aa5b773888e52f9fb78fda38d5cbff9ea61` |
| [Control](/root/kani-rev2-n18-n19-consumer-control-w14) · `work/rev2-n18-n19-consumer-control-w14` | `33db7a6351c4549098c52ce0e245fd072eb2152f` | `fa8268a81c4a8d260a71f18f936387a374ef57fe` | `9882b587d310eba6dba6f93b95b5523853a990af` |
| [Review-trigger](/root/kani-rev2-n18-n19-consumer-trigger-w14/control) · detached, local ref `review/rev2-n18-n19-consumer-trigger-w14` | `419854dda560b383d3d00d3da65d1f4fb263fd28` | `fa8268a81c4a8d260a71f18f936387a374ef57fe` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`. Будущее внешнее значение `CH8_REV2_N18_N19_CONSUMER_TRIGGER_TREE` для exact control tree равно `fa8268a81c4a8d260a71f18f936387a374ef57fe`. `pins`, `sources` и `finish` берут его из окружения. Gate проверяет fork `Tiramisu-Cake/kani`, push, exact ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, точный payload SHA, clean detached checkout и sole parent. `sources` и `finish` также сверяют admission receipt, upload открывается после успешных pins и finish. [Workflow](/root/kani-rev2-n18-n19-consumer-control-w14/.github/workflows/ch8-q-pilot.yml) · [Gate](/root/kani-rev2-n18-n19-consumer-control-w14/ch8-cal1/request.py)

| Вход | SHA-256 |
| --- | --- |
| [Frozen request](/root/kani-rev2-n18-n19-consumer-control-w14/ch8-cal1/CI-REQUEST.json) | `98715ff7da68525c8d5202e1f822572289ed8e86a0f40e9e932fb7a2a34dd3bc` |
| Canonical roster, JSON с сортированными ключами и разделителями `(",", ":")` | `aada22e820df20a466df9cb91215b15f3d3c78ad117ab620009c43e21d22e137` |
| [Std overlay bundle](/root/kani-rev2-n18-n19-consumer-control-w14/ch8-cal1/std-overlay.bundle), 28 906 байт | `e0556e307dde0e214fd1a35cc6566bbf227a27fd6bfa2f249b3884b452be01c4` |

| Источник в Std candidate | Git blob |
| --- | --- |
| `smallsort.rs`, тот же на FIX3, N32 и опорах N18/N19 | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `verify/cal1_model.rs`, тот же на этих пинах | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` |
| `verify/rev2_provider_cost.rs`, FIX3 byte leaf | `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` |
| `verify/rev2_n18_n19_providers.rs`, шесть опор | `9f5f22527656fd0b9b6afa879d7b8bb7574ff5c3` |
| `ptr/mod.rs`, тот же на Std CI-base, N32 и опорах | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `verify/rev2_n18_n19_consumer.rs` | `c152d19a34dc98765b70b1b62768f926fc6f9c4c` |
| `verify.rs` | `cb39e15f9a798b6947c587404ffba14f7cc30999` |
| `library/core/Cargo.toml` | `043bd584f386f98c5085174ef8bc8d985f620942` |

Опоры N18/N19 взяты из run `45749463113`, Ubuntu X64, attempt 1, trigger `7e2c97ed014c4d28abd7e22ed31e9dd960d4db20`, tree `3df8288611361bb173f727e2271d8e71985abdcc`, Std `86ea7aa5b773888e52f9fb78fda38d5cbff9ea61` / tree `63b199cc33052d6390fd0fdaa2b5c36962545fc4`. FIX3 leaf берётся из run `45661535099`, attempt 1, trigger `8d0f94a36606df5660eaf70818c44007859e05df`, Std `32129c149a15fb1b60a7314e738f3cb466d076e5` / tree `1b0cc32c571b370178e64f2b8c79773d2ce27051`. У опор общий stock tool и профиль OB12/unwind36. В run опор consumer cfg отсутствовал. У FIX3 были только CAL1, CAL2 и provider-cost cfg. Связанные runtime/model blobs оставались теми же при включении cfg последующих модулей. [FIX1 GO](REV2-N18-N19-FIX1-GO.md) · [Опорный индекс N18/N19](/root/ch8-artifacts/run-45749463113/ch8-rev2-n18-n19-providers-Linux-X64-45749463113-1/index.json) · [FIX3 index](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/index.json)

Все семь опор имеют `VERIFIED`, exit 0. Сверены размеры и SHA-256 членов receipt/projection по двум индексам. SHA-256 индекса N18/N19 `065a9d8c2738117b36101eb7f3dcb5c8e568506c79b90b7953d561ae49d39504`, FIX3 `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be`. Ниже ID даны с опущенным общим префиксом модуля опор, координаты относятся к файлу этого модуля. [Нативные свойства опор](REV2-N18-N19-PROVIDERS-RESULTS-ANALYSIS.md#что-закрыто-по-рёбрам)

| Слот | Regular anchors и режим |
| --- | --- |
| `S9-B01-L09-BITS`, `S9-B10-L10-BITS` | Plain Proof. `s9_b01_l09_bits.assertion.1/.2/.3` :16:5/:17:5/:18:5 и `s9_b10_l10_bits.assertion.1/.2/.3` :28:5/:29:5/:30:5. Порядок, popcount, q и V34 frame. Covers 4/4 у каждого. |
| `S13-SWAP-LEAF`, `S9-B10-SWAP` | Check `swap_if_less` в `rev2_provider_cost.rs` и `rev2_n18_n19_providers.rs`. `s13_swap_leaf.assertion.1/.14/.19` :159:5/:160:5/:166:9 и `s9_b10_swap.assertion.13/.14/.19` :87:5/:92:5/:94:9. Min/max и frame, FIX3 ensures и `memcpy/memmove.assigns.1/.2`. Covers 6/6 и 5/5. |
| `N19-INSERT-RIGHT-BYTES` | Plain Proof. `n19_insert_right_bytes.assertion.1/.2/.3/.4` :116:5/:120:5/:124:5/:125:5. Numeric order, порог и оба frame, 4/4 covers. |
| `M18-M19-PAIR-STEP` | Check `actual_pair_step`. Курсоры `actual_pair_step::{closure#2}::{closure#0}.assertion.8/.13` :172:9/:182:9, геометрия `m18_m19_pair_step.assertion.2–4` :222:5/:226:5/:230:5, значения и frame `.17–20` :275:5–278:5. `memcpy.assigns.1/.2`, grouped copy preconditions обеих копий, пять unwind и 21/21 covers. |
| `M19-ODD-CENTER` | Check локальной транскрипции `actual_odd_center`. `m19_odd_center.assertion.1–3/.13` :352:5/:356:5/:360:5/:384:5, центр и курсоры/frame `.18–22` :399:5/:400:5/:404:5/:408:5/:409:5. Modifies `D[9]`, `memcpy.assigns.1/.2`, grouped copy preconditions, четыре unwind, 3/3 covers. Домен Check включает `c=9`. Отдельный cover входа, который ведёт к этому sentinel в actual сети, относится к новому positive. |

| Слот | SHA-256 receipt | SHA-256 projection |
| --- | --- | --- |
| `S13-SWAP-LEAF` | `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c` | `3f81b2c134cdba1348d9720fafb5569dbc37195693e47485c8bb1b80fe28d596` |
| `S9-B01-L09-BITS` | `41e3435e50904c0cd683a7503a05d4428418557b3bfeddee95242d97c59551e3` | `46478975751c93569d9d1d0c681a9d623b2414db7129a1668e4ba05962649e48` |
| `S9-B10-L10-BITS` | `9fb9b0d517ef57b5e97ded7b21c0c19a4159bf8600afc218de304aa99998570e` | `be0f531216d217430763c47c4a0aba23d949a603535bdbd93db0845f84116678` |
| `S9-B10-SWAP` | `1add96613803158e98660efa5d7224b2036e62342c0fd4883893ca39a4e52f74` | `1403c326be86c505c644baa092c9424bef8c6813a54ff69f22a27d25b1814eba` |
| `N19-INSERT-RIGHT-BYTES` | `a6d386a32a14189a07b1c0f21769117064f6e9e9bbd207e1202e5eb0dfc2a38e` | `eece22966825ab785110b7968da99154e752567d0545bb5a877c6cf630c39333` |
| `M18-M19-PAIR-STEP` | `87a8c5263ef89d7c9f100856c4c987a1001fe06ab6102c448006a264a80429fb` | `3fd6c17114f50c2aa44969e481d3320125f1081fbc08549cb1a58b3ad51d838f` |
| `M19-ODD-CENTER` | `9181b95c28e3e1eb50c64a7d7b731fbe3a2b5e900f9016160a035fab9be4ee1e` | `876259149f3c77299e8d94263be2b50fcdb1fc452b762d226fa1e2763cd6e6a6` |

Прецедент grouped copy на N32 относится к run `45710831239`, Std `b93859fb447a39c0c8c7d854f70dedf9a47b263f` / tree `562a2fac5ed349a9fc09097789d0816f200c3819`. У `N32-ACTUAL-BITS` SHA-256 receipt `537dd962d7f178cedb670cb5e9bd39c0dd6b8109924c818a16dfe9d6a9dd46b4`, projection `de43bc30f4aa576973709a0b22a39a5716f890b222ad676cea4ac2c62200f269`. Шесть grouped IDs и `AFTER_COPY_BACK` задают форму ожидаемой привязки. Результаты N18/N19 должны появиться на своих exact корнях. [Допуск N32](REV2-N32-ADMISSION.md#привязка-строки)

## Профиль и окна

Одна job `ubuntu-24.04`, stock Kani, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwind, undefined-function и assertion-reach включены. Uninit/validity выключены. Корни исполняют actual функции, plain Proof без stubs, Replace, новых loop contracts и assumptions о порядке половин. Cfg-off сохраняет унаследованные флаги `kani_smallsort_cal1`, `kani_smallsort_cal2_merge_mask`, `kani_smallsort_rev2_provider_cost`, `kani_smallsort_rev2_s13_binding`, `kani_smallsort_rev2_s13_geometries`, `kani_smallsort_rev2_n32_consumer`, `kani_smallsort_rev2_n32_composite`, `kani_smallsort_rev2_n17`, `kani_smallsort_rev2_n18_n19_providers`. Cfg-on добавляет `kani_smallsort_rev2_n18_n19_consumer`. Discovery сравнивает kind/selector/file, сохраняет унаследованный инвентарь и требует ровно четыре новых plain Proof. Preflight FIX1 сохраняет rustc/launcher и другие первые version lines, compile witness core со всеми флагами и начальные диагностики при отказе. [Runner](/root/kani-rev2-n18-n19-consumer-control-w14/ch8-cal1/run.py)

| Стадия | Бюджет | Отсечка от epoch |
| --- | ---: | ---: |
| Setup с preflight и discovery | 50:00 | 50:00 |
| Четыре exact слота | 13:40 | 63:40 |
| Финальная аттестация | 2:00 | 65:40 |
| Finish | 5:00 | 70:40 |
| Upload | 7:00 | 77:40 |
| Резерв | 9:00 | 86:40 |
| Job timeout | | 100:00 |

Latest starts по roster `50:00`, `53:25`, `56:50`, `60:15`. На каждый слот выделено 180 с cold wall, 10 с reap, 5 с receipt и 10 с launch headroom. Внешние таймауты pins/prepare/measure/finish/upload составляют 8/51/18/6/8 мин. Внутренний measure ограничен меньшим из общего окна и 16:45 от начала шага, включая аттестацию, 5 с на measurement journal и 60 с на ранний старт и identity gate. Измерения изолируют cwd, cold Cargo/Kani targets, tmp и export. Группа ограничена 4 GiB с резервом 2 GiB, VT до 120 с, проекция до 4 MiB, артефакт до 96 MiB. Сохраняются VT, cold wall, RSS группы и CBMC, CNF, фаза, native anchors и контроль публикации. Для RSS действует оговорка FIX1 об учёте Linux TID. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md) · [Классификация](/root/kani-rev2-n18-n19-consumer-control-w14/ch8-cal1/report.py:107)

Runner пишет атомарный checkpoint с process outcome и reap до parsing. Receipt deadline является минимумом из конца слота и `supervisor_return + 5s`; последняя секунда резервируется на commit. Отложенная запись сохраняет late и исходный exit. Неподтверждённый reap останавливает остаток очереди. `pair_status` для каждой N требует оба exact совпавших нативных исхода, полные и своевременные receipts и проекции, профиль и успешную финальную аттестацию. Timeout, RSS, нарушенный deadline и неполнота оставляют соответствующую пару `OPEN`. Общий `CONSUMERS_WITHIN_PROFILE` требует обе пары и сохраняет `proof_credit=NONE`.

## Локальная проверка и открытые условия

- Rust visibility проверена по областям видимости `small_sort_network`, `KeyLess` и `crate::kani`; вызовы, метки и cfg сверены со source и request. Diff от provider Std содержит новый закрытый модуль, его cfg и lint-декларацию. Удаление двух cfg-вставок восстанавливает старые registry и manifest побайтно. Runtime и действующие контракты совпадают с provider Std побайтно. `rustfmt --check` выполнен указанным nightly с `use_small_heuristics=Max`, `skip_children=true,reorder_modules=false` сохраняют унаследованный порядок registry. Проверены `git diff --check`, YAML, `bash -n` всех run-блоков и разбор встроенного Python.
- Bundle проверен на отдельной bare shallow-базе depth 2 через локальный Git transport, без alternates. До импорта overlay отсутствовал. Проверены `bundle verify`, единственный advertised HEAD, `unbundle` и chain из десяти commit/tree/sole-parent с проверкой layout. HEAD базы, refs и shallow boundary сохранились. Std, control и review-trigger используют sparse worktrees.
- Офлайн сверены 25 пар sort9 и три конкретных входа, включая девять сдвигов для `0x0003_ffff` и правый центр с `c=9` для `0x0000_01ff`. Синтетика проверяет exact discovery и trigger gate, wrong N и координаты, потерю `AFTER_COPY_BACK` или odd cover, grouped anchors, sole failure и лишние safety/overflow/unwind failures, late/partial receipt и остановку после потери reap.
- Полный блок `pins` из workflow выполнен локально на exact review-trigger за 99,204 с. Каждый составной тест использовал одну шкалу для связанных чтений, включая поздние проверки `clocks`, `finish`, latest start и публикацию. Последовательность обычная → 60 → 1 → 5 с сохранена из FIX1. Четыре watchdog по 90+5 с и 45 с на pins занимают до 425 с из 480 с.
- На старте monotonic 1 с exact review-trigger прошёл `pins` и `finish`. Финальный индекс содержал четыре `NOT_STARTED`, размеры и SHA-256 членов совпали. `pins`, `sources` и `finish` отклонили старый FIX1 tree и подменённый payload SHA.

| Шкала | Полный suite | Время |
| --- | ---: | ---: |
| Обычная | 111/111 | 24,802 с |
| Старт с 60 с | 111/111 | 24,190 с |
| Старт с 1 с | 111/111 | 23,674 с |
| Старт с 5 с | 111/111 | 24,281 с |

Пакет сдаётся на независимое ревью. Открыты нативная компиляция и discovery, фактические ID и статусы новых корней, сверка grouped properties copy-back на обеих длинах, ресурсы, финальная аттестация и независимый допуск. Отдельный GO остаётся у владельца. Новых запусков Cargo, rustc, Kani, CBMC или CI, push и изменений Actions variables в этом этапе не было.

## Офлайн-смета следующего пакета N20/N21

При `m=10` обе длины берут слева `v[1..11]`. Справа base 11, `v[11..21]` для N20 и `v[11..22]` для N21. Слева перенести S9 с len9 на len10, сохраняя base 1 и расписание. Справа нужны exact S9 bits на len11 и byte leaf на base 11 с переносом на len10. Левый driver проверяет rel9 / abs10. Правый проверяет rel9 / abs20 у обеих длин и rel10 / abs21 у N21, с отдельными covers N20 и N21. Далее grouped pair для `m=10` и локальный центр N21 с `D[10]`, обеими сторонами остатка и `c=10`. Copy-back использует 20 или 21 байт и тот же внешний аргумент после заполнения D.

Оценка на опоры — 1–2 инженерных дня офлайн и 6–7 слотов. При той же полосе один пакет занимает 93:30–96:55 из 100:00. Пара `m=9` дала 91,73 с VT и первую CNF 346 076 / 1 972 867. Начать с adjacent `m=10` и проверить общий VT ≤120 с. Если потребуется разделить геометрии или up/down с общим frame и roster вырастет до восьми слотов, 100:20 уже выходит за окно, поэтому нужна ещё одна job в отдельном пакете. После принятия опор остаётся отдельный consumer-пакет на четыре exact корня. Текущий roster ограничен N18/N19. [План N18–N31](REV2-N18-N31-PLAN.md) · [Замер пары](REV2-N18-N19-PROVIDERS-RESULTS-ANALYSIS.md)
