# REV2 · составной граф и пакет copy-back/frame N31/N27/N29/N30

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** Item 2, w15. Один офлайн-пакет из четырёх Ubuntu singleton Proof. Новые нативные исходы ожидаются после независимого ревью и отдельного GO на один прогон в освободившейся очереди. [Задание](REV2-N27-N29-N30-N31-COMPOSITE-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Пины и worktrees

| Роль | Commit | Tree | Единственный parent нового коммита |
| --- | --- | --- | --- |
| База локального Std | `50609bb850c64080aedd74c00c9865dcae1ce74b` | `c2e93c566512c45179ab015b55835167eefc6191` | |
| [Std](/root/verify-rust-std-rev2-n26-n31-copy-back-w15), `work/rev2-n26-n31-copy-back-std-w15` | `ee9eccad17d08988300e5b9e9e18d821889cdc92` | `b242e0d68a9666e2f6c965656cb9b27c6475df4a` | `50609bb850c64080aedd74c00c9865dcae1ce74b` |
| База локального Control | `a02a710c0c1206459d924c7467c9092b6921c674` | `7a92427bc3e81e99016536ee6ef87dd761eb7f3a` | |
| [Control](/root/kani-rev2-n26-n31-copy-back-control-w15), `work/rev2-n26-n31-copy-back-control-w15` | `17d0184168945306f80352c70993c215bef40c92` | `16daa4eabbb186bd4822fbe79a3d56dfb74d89a7` | `a02a710c0c1206459d924c7467c9092b6921c674` |
| [Локальный detached review-trigger](/root/kani-rev2-n26-n31-copy-back-trigger-w15/control), ref `review/rev2-n26-n31-copy-back-trigger-w15` | `f922daa92ae449a9929950958d020411314126c1` | `16daa4eabbb186bd4822fbe79a3d56dfb74d89a7` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std base для загрузки bundle `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Handoff в [g0](/root/verify-rust-std-kani3300-g0) на `experiment/kani-k1-kani3300g0-20261111`. У Std, Control и review-trigger author и committer сверены перед заморозкой. Обе роли имеют `Tiramisu-Cake <igkharin@gmail.com>`. Все новые коммиты имеют `[skip ci]`.

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-n26-n31-copy-back-control-w15/ch8-cal1/CI-REQUEST.json) | `68289a93e8e1b3ec3617d53fb5f6eb7fbaa9714381d9d8699872731c4e89d249` |
| Roster, canonical JSON | `6206fc1d9f76cc8e84129c1aecb99e36ab8b38ddd41d7f9152a9a0591a82ecbd` |
| Source bindings, canonical JSON | `f43a446614cbc20a889b75bd2916ff14c7e559480138ae67935fa79065ff5acb` |
| [std-overlay.bundle](/root/kani-rev2-n26-n31-copy-back-control-w15/ch8-cal1/std-overlay.bundle), 57 590 байт | `2f3cc01614f61dd7fd7d4dcff9d17f324cd6a9ba405ff696601649247e94099e` |

Canonical JSON использует сортировку ключей и разделители `(",", ":")`. Исторические вложенные roster сохраняют прежние digests. У consumer SHA-256 `b6709c5d920e4ac4621fc10e6a4a3056a7fa7c52ca6b9ff8d399eb04e45129dc`. У merge SHA-256 `47cd94f3d07647f62ce26e0e0f1f8451545775e45d46f985a8f1759adbc059db`. Workflow подаёт независимую Actions variable `CH8_REV2_N26_N31_COPY_BACK_TRIGGER_TREE` в гейты `pins/sources/finish`. Замороженное ожидаемое значение — tree Control из таблицы. Проверяются fork `Tiramisu-Cake/kani`, push ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, `HEAD == GITHUB_SHA == payload.after`, `payload.deleted == false`, exact tree, sole parent, чистый detached checkout и совпадение admission receipt между гейтами. [Workflow](/root/kani-rev2-n26-n31-copy-back-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-n26-n31-copy-back-control-w15/ch8-cal1/request.py)

| Исходник | Git blob в Std |
| --- | --- |
| `rev2_n26_n31_copy_back.rs` | `d26abd90682186205ef82c9732291fc63f3d4124` |
| `smallsort/verify.rs` | `cfa6aa5daaceeccea4db89004f1637d4942bd62f` |
| `core/Cargo.toml` | `4f0003995123529e5099f0d59a7a688c696d24a8` |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` |
| `ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `rev2_n26_n31_consumer.rs` | `6d407f1df0f9d0d36f8cc3205a7c041a4c5bd4d5` |
| `rev2_n26_n31_halves.rs` | `92de2daf5b195e6340af59a8b9b7a1e0a22e8770` |
| `rev2_n26_n31_merge.rs` | `df670cd3a63cce01fe89f8a4fdf94353b849d805` |
| `rev2_merge_pair_fixed.rs` | `b8580df3448e100d7ecb0811ebba0f14041ad412` |

Дельта Std содержит новый модуль, его регистрацию под `cfg(kani_smallsort_rev2_n26_n31_copy_back)` в существующей области `cfg(kani)` и одну декларацию check-cfg. Вычитание новых деклараций восстанавливает blobs registry и manifest базы. Discovery проверяет только четыре новых `standard-harnesses` по exact selector/file поверх 90 исторических REV2 записей, карты `*_CHECKS` с target/file и отсутствие targets у plain Proof. Полный инвентарь cfg-off сравнивается с общей частью cfg-on по kind, selector, file и targets. Исторические consumer и merge roster используются для source/native bindings. [Discovery](/root/kani-rev2-n26-n31-copy-back-control-w15/ch8-cal1/run.py)

## Exact roster и нативные якоря

| Слот | Exact selector | Root | Последний старт от epoch |
| --- | --- | --- | --- |
| `N31-COPY-BACK-FRAME` | `slice::sort::shared::smallsort::verify::rev2_n26_n31_copy_back::n31_copy_back_frame` | `9:1` | 55:00 |
| `N27-COPY-BACK-FRAME` | `slice::sort::shared::smallsort::verify::rev2_n26_n31_copy_back::n27_copy_back_frame` | `15:1` | 58:25 |
| `N29-COPY-BACK-FRAME` | `slice::sort::shared::smallsort::verify::rev2_n26_n31_copy_back::n29_copy_back_frame` | `21:1` | 61:50 |
| `N30-COPY-BACK-FRAME` | `slice::sort::shared::smallsort::verify::rev2_n26_n31_copy_back::n30_copy_back_frame` | `27:1` | 65:15 |

У каждого `#[kani::proof]`, `#[kani::unwind(36)]`, `copy_back=true`, ожидание `VERIFIED`/exit 0. Helper `check_copy_back::<N>` из того же exact module получает независимые arbitrary `[u8; N]` и `[u8; 34]`, сохраняет снимок V34 до копии и записывает N байтов в отдельную живую scratch32. `scratch_base` получен через `MaybeUninit<[u8;32]>::as_mut_ptr()` и cast к `*mut u8`. `v_base` получен из `backing[1..1+N]`. Единственный вызов `ptr::copy_nonoverlapping::<u8>` на `46:14`. Чтение scratch ограничено инициализированным префиксом N. Rust bounds и две раздельные живые области следуют из конструкции. Размер и alignment `u8` равны 1. Корни plain, без `assume`, stubs, Replace и loop contracts. [Модуль](/root/verify-rust-std-rev2-n26-n31-copy-back-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_n26_n31_copy_back.rs)

| Native label | Координата в модуле | Покрываемый предикат в exact `check_copy_back::<N>` |
| --- | --- | --- |
| `DEST_EQUALS_SOURCE` | `55:5` | Конъюнкция `backing[1+i] == source[i]` для каждого `0≤i<N` |
| `SOURCE_PREFIX_FRAME` | `56:5` | Конъюнкция равенств каждого из N прочитанных scratch байтов исходному снимку |
| `V34_FRAME` | `62:5` | Равенство `backing[0]` и каждого байта `backing[1+N..34]` снимку до копии |
| `AFTER_COPY_BACK_FRAME` | `63:5` | Cover после целевой копии и трёх постов |

Ожидается ровно один native property ID на каждую из четырёх меток. Все три assertion стоят после своих полных конъюнкций, вне циклов. Лишний экземпляр или сдвиг exact function/file/line/column отклоняется. Gate требует `SUCCESS` у шести сгруппированных ID `ptr::copy_nonoverlapping::<u8>` на `core/src/ptr/mod.rs:587:14`. Это `.safety_check.1/.2`, `.arithmetic_overflow.1`, `.precondition_instance.1/.2/.3`. Единственный copy call, source-координата и достигнутый после него cover привязывают группу к целевому копированию. Подготовительные `ptr::write` и чтение префикса имеют свои роли. Все выведенные unwind properties требуют `SUCCESS` при подтверждённом stock unwind36. Gate сверяет regular и stock terminal, итоговые counts и доступные property IDs, включая ID `SATISFIED` cover. Stock RFC 0015 агрегирует успешные assertions. [Гейт результата](/root/kani-rev2-n26-n31-copy-back-control-w15/ch8-cal1/results.py) · [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

## Рёбра до фактического small_sort_network

Домен композиции — `small_sort_network::<u8, KeyLess<u8>>` на активном срезе живого инициализированного V34 с произвольными полными байтами и независимым `q:u8`. Пусть `S=&v[1]`, `m=N/2`. Все четыре N удовлетворяют входным guards `2≤N≤32`. Конструкция `smallsort.rs:383–391` даёт scratch32 и первую половину длины m. Для N31/N27/N29/N30 `no_merge=false`, оба региона проходят `:395` с `len≥13`, `:396` выполняет S13, `:405` — вставки с offset 13. Первый регион начинается в `v_base`, поэтому `:411` не завершает цикл. `:416` создаёт вторую половину `S+m` длины `N−m`, и после её вставок `:411` завершает цикл. [Actual маршрут](/root/verify-rust-std-rev2-n26-n31-copy-back-w15/library/core/src/slice/sort/shared/smallsort.rs:383)

| N | Первая итерация S13 → вставки, rel/abs и local end | Вторая итерация S13 → вставки, rel/abs и local end | Merge в D | Copy-back и внешний V34 frame |
| ---: | --- | --- | --- | --- |
| 31 | `v[1..16]`, B01 L17→L15, rel13–14 / abs14–15, end 16 | `v[16..32]`, B16/L16, rel13–15 / abs29–31, end 32 | `M31-PAIR-FIXED` ×15, `N31-ODD-CENTER` → D[15] | `count=31` → `v[1..32]` · `v[0]`, `v[32..34]` |
| 27 | `v[1..14]`, B01/L13, пусто, `tail=end=14` | `v[14..28]`, B14/L14, rel13 / abs27, end 28 | `N27-PAIR-FIXED` ×13, `N27-ODD-CENTER` → D[13] | `count=27` → `v[1..28]` · `v[0]`, `v[28..34]` |
| 29 | `v[1..15]`, B01 L17→L14, rel13 / abs14, end 15 | `v[15..30]`, B15/L15, rel13–14 / abs28–29, end 30 | `N29-PAIR-FIXED` ×14, `N29-ODD-CENTER` → D[14] | `count=29` → `v[1..30]` · `v[0]`, `v[30..34]` |
| 30 | `v[1..16]`, B01 L17→L15, rel13–14 / abs14–15, end 16 | `v[16..31]`, B16 L16→L15, rel13–14 / abs29–30, end 31 | `N30-PAIR-FIXED` ×15 | `count=30` → `v[1..31]` · `v[0]`, `v[31..34]` |

**S13.** Exact байтовые Check `swap_if_less::<u8,KeyLess<u8>>` дают min/max для каждой пары, q и frame. Левая опора `S13-SWAP-LEAF` сочетается с `S13-BASE1-BITS` для L13 или `S13-B01-L17-BITS` для L14/L15. Правая опора использует свой `S13-B{14,15,16}-SWAP` и соответствующий битовый корень. Guard в `smallsort.rs:601:5` выполняется на обеих половинах. Все 45 actual адресных пар `:612–656` после вычисления base `:605:18` читают и пишут только rel0–12. Сужение длины сохраняет guard, базу, расписание, эксклюзивный доступ и frame. Для каждого порога `t∈0..=255` отображение `P_t(x)=[x≥t]` переводит min/max в AND/OR. Нативные bit Proof устанавливают порядок и исходный popcount проекции. Убывание любой соседней пары байтов нарушило бы порядок для одного порога. Разности соседних пороговых счётчиков, с нулём для t=256, дают полные кратности. Хвост сохраняет входные значения до вставок. [Опоры половин](REV2-N26-N31-HALVES-ADMISSION.md#привязка-полного-байтового-домена)

**Вставки.** Принятые byte drivers `N32-INSERT-LEFT-BYTES` на B01/L16 и `N32-INSERT-RIGHT-BYTES` на B17/L16 имеют тот же тип, offset 13, существенные исходники и независимый q. Порядок, `count(<q)`, q/frame и возврат проверены нативно. Результирующие байты не зависят от q, значит счётчик для всех q вместе с длиной даёт полные кратности. При r=13 текущий префикс уже отсортирован. `smallsort.rs:759–767` сравнивает tail со своим `end=B+L`. `insert_tail` либо завершает шаг без записи (`:705–708`), либо сохраняет tail в отдельном tmp (`:715`) и переносит соседний инициализированный байт в следующую справа дыру (`:722`). Guard `:725–732` удерживает sift внутри `[B,B+r)`, `CopyOnDrop` на `:362:13` заполняет последнюю дыру из tmp. Write set ограничен `[B,B+r]` включительно. Пост шага даёт отсортированный префикс длины r+1 с прежними кратностями, неизменным хвостом и внешним frame. Перенос в B14/B15/B16 сохраняет относительные адреса, раздельность источника и назначения каждого копирования и меняет локальный end на значение из таблицы. Слева берутся первые 0/1/2 итерации соответствующей длины. Справа выполняются ровно 1/2/3 по таблице. Исторические covers подтверждают сдвиг rel13. 13 троек и хвост `2,1,0` дают офлайн-свидетеля сдвига на каждом позднем rel. Отдельные right insertion roots B14–B16 имеют `NOT_RUN`. Их рёбра обоснованы принятыми переносом и индукцией. Валидность чтения tmp и сдвига следует из инициализированного входа и фактических записей при uninit OFF. [Вставки и переносы](REV2-N26-N31-HALVES-HANDOFF.md#actual-вставки-и-решение-по-roster)

**Pair и odd.** Таким образом на вызове `smallsort.rs:424:9` обе половины численно отсортированы, имеют полные входные кратности, q и V34 вне активного среза сохранены. D — раздельный writable scratch32. Предпосылка `len_div_2 != 0` на `:1006` следует из всех четырёх N. Для k-й пары `:1022–1024` пусть a,b — количества из левой/правой половины, снятые снизу, c,d — сверху. До пары `a+b=c+d=k<m`, D уже содержит крайние k рангов с каждой стороны. Порядок `(byte, индекс в S после вставок)` согласован с tie-left в `merge_up` и tie-right в `merge_down`. Все четыре адреса читаются внутри соответствующих половин, поскольку a,b,c,d≤k<m. У исчерпанной половины forward-кандидат уже снят сверху и проигрывает минимуму, reverse-кандидат уже снят снизу и проигрывает максимуму. Пока остаются N−2k≥2 ранга, два выбора дают разные оставшиеся элементы. Exact pair Check связывает шаги, курсоры, safety, min/max, q/source frame и две записи `D[k]` и `D[N−1−k]` с `:885` и `:918`. Индукция сохраняет инвариант до k=m. [Нативная привязка merge](REV2-N26-N31-MERGE-ADMISSION.md#привязка-нативных-опор-к-actual-циклу)

После m пар `left=S+a`, `right=S+m+b`, `left_end=S+m−c`, `right_end=S+N−d` по `:1027–1028`. Разности равны остаткам `(m−a−c,N−m−b−d)`. У N30 обе нулевые. На нечётных N возможны `(1,0)` и `(0,1)`. В первом случае `:1032` выбирает left, во втором right. `:1034` записывает единственный оставшийся ранг m в D[m], `:1035–1036` продвигают ровно выбранный курсор. Если `c=m`, то `a=0,b=m,d=0`, левый reverse sentinel `S−1` применяется только в `wrapping_add(1)`, и читается `S+N−1` из правой половины. Следовательно, после пары/центра выполняются оба сравнения `left == left_end` и `right == right_end` на `:1042`, merge возвращается без ветки нарушения порядка. Каждая из N позиций D записана ровно один раз, source V34 и q сохраняются. Инициализация D — внешний вывод из write sets при uninit OFF. [Odd anchors и guards](REV2-N26-N31-MERGE-ADMISSION.md#привязка-нативных-опор-к-actual-циклу)

**Перенос к копии и конечный пост.** На `:425:9` `ptr::copy_nonoverlapping::<u8>` получает тот же тип и направление, живую отдельную scratch32 с полностью записанным префиксом N, `v_base=&v[1]` в живом V34, точный `count=N`, alignment 1 и непересекающиеся области. Ранговый пост D удовлетворяет arbitrary-byte pre нового корня, поскольку он принимает любой полностью инициализированный префикс N и любое исходное V34. После успешной проверки copy-root его побайтовое равенство перенесёт числовой порядок и полные кратности из D в `v[1..1+N]`. Frame вне этого среза следует из объединения write sets обеих половин, merge в D и копии в активный срез. q сохраняется на всём домене по принятым Half и Pair, телу `KeyLess<u8>::call_mut` (`cal1_model.rs:27–29` сравнивает `a<b` и выдаёт cover), отсутствию доступа к компаратору в odd center и в copy. Odd fixture `Q_FRAME` исключён из q-аргумента. [Actual копия](/root/verify-rust-std-rev2-n26-n31-copy-back-w15/library/core/src/slice/sort/shared/smallsort.rs:425) · [Композиция N32](REV2-N32-COMPOSITE-TASK.md#офлайн-привязка-и-решение-по-copy-back)

## Исторические нативные опоры

Сверены семь опубликованных индексов и размеры/SHA-256 36 выбранных receipt/projection. Все 18 опор дали `VERIFIED`, exit 0, полный stock `SUCCESS` и подтверждённый reap. Существенные source bindings и нативные роли взяты на их exact пинах. [Пины и координаты опор](REV2-N26-N31-CONSUMER-HANDOFF.md#исторические-нативные-опоры)

| Ребро / слот | Native ID-якорь | Receipt SHA-256 | Projection SHA-256 |
| --- | --- | --- | --- |
| `S13-SWAP-LEAF` | `s13_swap_leaf.assertion.1–3`, `.cover.1–5`, `call_mut.cover.1` | `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c` | `3f81b2c134cdba1348d9720fafb5569dbc37195693e47485c8bb1b80fe28d596` |
| `S13-BASE1-BITS` | `check_s13_base1::<false>.assertion.3/.6/.8/.9`, `.cover.1–3`, `call_mut.cover.1` | `66fbadf4bb9ef514bb367f35d50da6e2f421c17266aa3ca03f3228af12fd7ddd` | `33875cb4ad55dfa468410b6083fc3c92f50bf2b0359fe903c4013a62380a2bf2` |
| `S13-B01-L17-BITS` | `check_bits::<1,17,false>.assertion.5/.8/.11/.12`, `.cover.1–3`, `call_mut.cover.1` | `119b822970d1386f3d15e5edefefaf847d4ee63a5358610f0bd9e22880c63c79` | `6c37276170ebe94470fa4a1d17b92bc09e05e5ac6b66d22aadd21508f255696a` |
| `N32-INSERT-LEFT-BYTES` | `check_insertions::<1>.assertion.3–6`, `.cover.1–2`, `call_mut.cover.1` | `7cac457115063a8ffb3f46ff207c23f0361523a93c7d73395f6b7115639c4f4e` | `6b407b8d1f9e6ffa67786e07e06fd1a91e373f72527df8dd93bc9afbae0d3f40` |
| `N32-INSERT-RIGHT-BYTES` | `check_insertions::<17>.assertion.3–6`, `.cover.1–2`, `call_mut.cover.1` | `3bcb3d314501ddb8d35bfc01396bfba094b2a65cd8ade7e54f4763ceac1b6a84` | `0a7a7f482845d9f4609b9a83b1856b12cc81489146693e39ab48dc7cc2946c25` |
| `S13-B14-SWAP` | `swap_if_less::<u8,KeyLess<u8>>::{closure#2}.assertion.1`, `assert_swap_post::<14>.assertion.1` | `5df30e8896b69fb8131e34b1a6863bca4d60d34988c5def0e1c484c4f5a235b7` | `2108accffc6dff8117c1eac6cd615eba1c01095cf20a354de94fd89788d161a3` |
| `S13-B14-L14-BITS` | `check_bits::<14,14>.assertion.5/.8/.11/.12`, `.cover.1–3` | `390bbc1fd2f2660e48656ff54522f5fc5ab0d4738f50f44f4b2b1f14e640bb7e` | `833eab67b3aab06fb333fd2bd7c1817045df2122b22a8c58f981dcb0cd3bdd5a` |
| `S13-B15-SWAP` | `swap_if_less::<u8,KeyLess<u8>>::{closure#2}.assertion.1`, `assert_swap_post::<15>.assertion.1` | `17e49991b94b7e913ecb78b45035be07bb277d9fdd2361684c309f80004c38f1` | `a745ac861dfe32ee6242539a14aa5b3acb4d2e0be85b17b35675827168b18828` |
| `S13-B15-L15-BITS` | `check_bits::<15,15>.assertion.5/.8/.11/.12`, `.cover.1–3` | `d5861a93d0fbc65e1bc8e9c0206a9a5b0753dc4672bb80651fc22d8d14895f5b` | `1be1248b7de5ce66bc3687a50cae84e3f367189ceb289cc983b0ec75dc8b53a3` |
| `S13-B16-SWAP` | `swap_if_less::<u8,KeyLess<u8>>::{closure#2}.assertion.1`, `assert_swap_post::<16>.assertion.1` | `f80cfd703e427643364deecd187898f3a123bf9aaa2f42b204e9f2751723b5a9` | `d5dc5e926e13ae3dfbb29c2eff1c81bd3b51bd8607c32b5e27be20542ab38ed3` |
| `S13-B16-L16-BITS` | `check_bits::<16,16>.assertion.5/.8/.11/.12`, `.cover.1–3` | `97a7ed5967be72aeef86b59b79db2f491f818cfaff72240042f6fb0cd5bac48a` | `f1043e658ca2ecaadffa83eb5d1733fd4dd10230d8bc17104e5adb54a28d4254` |
| `N27-PAIR-FIXED` | `n27_pair_fixed.assertion.1/.2/.3/.10/.15–18`, `.cover.1–10` | `7791ceedba14562ceb01ba350793d06fec1a5716c5be7eae97047dfb6f2c4c38` | `9c3240db539bfdab83a5aff041a3d012035d9a5375edd65f79b1c641a057a94c` |
| `N29-PAIR-FIXED` | `n29_pair_fixed.assertion.1/.2/.3/.10/.15–18`, `.cover.1–10` | `7c9f6678b8b6ba98677ceb505d7b40fdb325b78f24a7751979ab7549436614df` | `858440f4422ed5b43cea473e630dc680bab1f72dad36dc2af6a1f734cd2d9a5e` |
| `N30-PAIR-FIXED` | `n30_pair_fixed.assertion.1/.2/.3/.10/.15–18`, `.cover.1–10` | `b040533d768b474b127edf64429db83b6b85e6aa91536be7077619ce9bd244a5` | `bfc36ef774cdfeb7f8e7f508c146f923dca48d00fc2f17052a2002d789a4e400` |
| `N27-ODD-CENTER` | `n27_odd_center.assertion.1/.2/.3/.13/.15/.18–23`, `.cover.1–4` | `219482289b26d670581a9bed774745c01039a873ed3240ae65c3cd27647a73a8` | `c396f50813f1d9f4ffeb111a585ce5dbcc49c1c6dc0c07c9784b3b6ec9c79490` |
| `N29-ODD-CENTER` | `n29_odd_center.assertion.1/.2/.3/.13/.15/.18–23`, `.cover.1–4` | `a5e54adbfc95a7dfa3974030da1bea6d492ecd41451fc696928126843fce6a46` | `afdbf8c0f1cdaacbf68c3e8151078ff13134652a82f66cad97a1107a2bd2d167` |
| `N31-ODD-CENTER` | `n31_odd_center.assertion.1/.2/.3/.13/.15/.18–23`, `.cover.1–4` | `898d35ebfe8f0ad52595c4dbfc7fe82e5c6ab37d1fc37ad5622945319e00f4c5` | `b5bad24884bf427be3eac32405f4ceb610c5b9c70492eb4b2980e017fa76d417` |
| `M31-PAIR-FIXED` | `m31_pair_fixed.assertion.1/.2/.3/.14–17`, `.cover.1–10`, actual cursor closure `.assertion.7/.10` | `e1e2e1842e37c1d1669ad322306ca72d4388759c86ac0fd308042bcf74f227a1` | `2a9c504abf5bba1fb27d2633a02de6912dd68f1469bccf9244711cebd60e2ca4` |

| Run / attempt | Опора | SHA-256 индекса |
| --- | --- | --- |
| [45846512615/1](/root/ch8-artifacts/run-45846512615/ch8-rev2-n26-n31-halves-Linux-X64-45846512615-1/index.json) | halves | `452059d4c406b9f75455ae00cdc1e68709f28874890a254374b35f5550a57d79` |
| [45861423438/1](/root/ch8-artifacts/run-45861423438/ch8-rev2-n26-n31-merge-Linux-X64-45861423438-1/index.json) | merge | `28799cedd217692c009f36282bf31d8ca2fc9c2ec15f29f86d822a1a5bc22222` |
| [45785063793/1](/root/ch8-artifacts/run-45785063793/ch8-rev2-merge-pair-fixed-Linux-X64-45785063793-1/index.json) | M31 pair | `ded8803087eab9aedcc2bfcda6dd1d5184fc6e6b640f796bd206a391fc313c06` |
| [45661535099/1](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/index.json) | B01 swap leaf | `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be` |
| [45676394046/1](/root/ch8-artifacts/run-45676394046/ch8-rev2-s13-binding-Linux-X64-45676394046-1/index.json) | B01/L13 bits | `bcb05483715c3b6067586c26059f2b341f84b6c3a6b5ba7018db0395258f89d6` |
| [45688753097/1](/root/ch8-artifacts/run-45688753097/ch8-rev2-s13-geometries-Linux-X64-45688753097-1/index.json) | B01/L17 bits | `e575daf8b20bab3c3023b8809e61cc21ea1a4bf9be85153d572368e6bbf663b7` |
| [45710831239/1](/root/ch8-artifacts/run-45710831239/ch8-rev2-n32-consumer-Linux-X64-45710831239-1/index.json) | N32 insertion drivers | `9145808434de22a0cc31f8f15630c7510e723dd870862cb06d59d5624ce7bfa6` |

При ревью pair сопоставить stock `ProofForContract` и regular вызовы `actual_pair_step_n27/n29/n30` в `rev2_n26_n31_merge.rs`. Их cursor assertions `.7/.10` имеют координаты `152:9/160:9`, `392:9/400:9` и `512:9/520:9` соответственно. У `M31-PAIR-FIXED` target `rev2_merge_pair_fixed::actual_pair_step_n31`, modifies `387:1`, cursor assertions `413:9/423:9` в проверяемой closure. Для odd centers N27/N29/N31 сверить `actual_odd_center_nN`, selected source `698:5/810:5/922:5` и посты значения, курсоров и write set. [Пины merge и M31](REV2-N26-N31-MERGE-HANDOFF.md#roster-и-нативная-привязка) · [Исторический M31](REV2-N26-N31-MERGE-HANDOFF.md#проверка-исторического-m31-pair-fixed)

## Исторические post-return controls

Проверен компактный опубликованный индекс run `45876456087/1` с trigger `7bf00f0dc63c8ab2507dc9250ad330903446836d` и SHA-256 `8a8ff1418e34add9ec0fab7a33967623f89350d0d71f4acc8f05944dc585590c`. Размер и SHA-256 каждого из 16 опубликованных receipt/projection совпадают с записью `members`. Std commit/tree `50609bb850c64080aedd74c00c9865dcae1ce74b` / `c2e93c566512c45179ab015b55835167eefc6191`. У `rev2_n26_n31_consumer.rs` Git blob SHA-1 `6d407f1df0f9d0d36f8cc3205a7c041a4c5bd4d5`, SHA-256 `abd07588deed4d1f2d2d5f1780c1ca1deadd492bfe59a00bfb7020eb67af0bef`. Git `hash-object` совпал с blob handoff.

| N | Positive receipt SHA-256 / bytes | Positive projection SHA-256 / bytes | Control receipt SHA-256 / bytes | Control projection SHA-256 / bytes |
|---:|---|---|---|---|
| 31 | `5be8e8bb454f609a1f2ab053caa81764d934c0c0119da70ea71a07401e17a2bc` / 33815 | `50244e6e891cf950beeb4f476318534999dc4bde5f7e3585da8006f09acf84f2` / 15953 | `80c0cbba38fd962ba7084a0e972ff7669fd9018f48e7e578f228b265925752f0` / 51402 | `8da0518c93caf8c35d277de0aec6a6b924ce59cb3a818d992d5901040df0b1f2` / 279261 |
| 27 | `5c3285d958dbbe228503ebd03c980bdbe9b757e9ef87f6b43b4a56dc870f5041` / 32376 | `155131b39526992589b0d79970da0a2258ea9b4f1cb8c7e3b5aa3aa3d539cc80` / 15168 | `2e5629b9971c89bab94205248beaae1cc542d98712f03c3d15296dd1d5d42df4` / 51441 | `d56dc2bf9f38ffc481f6d461aac2e1db18f11b55520ccd87f30c0977150078e0` / 279316 |
| 29 | `75b2ad27800aa9a99c66fcd9422ad511cbb52e3d83f3243addc69582e322a94e` / 34219 | `6076c686d6703b6bf243b3e22c9ef67c5aec57a4940c450240f96efa361b690b` / 15938 | `4440f796f008d4414dd25ac40552013afb206acbcc7999a0f6da5f6ceea25c8a` / 51913 | `75a7d845a7e00d3c69465ecbfbfaa999d97995b69ece4afb4e8598686f47e72d` / 279321 |
| 30 | `1e9822db70b57d58195e19c11b6edb657f10cf6faf79bd692be0be51f94f9510` / 30448 | `a0cba8afc9859afa59eee2f37dc402ce29e9988c65be27435c2bf8576c81a3ca` / 13871 | `7cc58862e184fe1ebdb53361dc8bd0eb03271e4aa7c618c8f43cfc127522a3a0` / 47971 | `9c6cbbb91d5cac152c0302cbe5c5d18aa34f172f89260db611d5719b47074c6f` / 274132 |

Префикс selector старых контролей — `slice::sort::shared::smallsort::verify::rev2_n26_n31_consumer::`, суффиксы `n31_witness_corrupt`, `n27_witness_corrupt`, `n29_witness_corrupt`, `n30_witness_corrupt`. У каждого контроля `FAILED` с exit 1 и полной проекцией (`complete=true`, `projection_status=COMPLETE`). Единственный native `FAILURE` — `check_nN::<true>.assertion.17`, метка `REV2_N<N>_ACTUAL_CANONICAL_SORTED_POPCOUNT` на `68:5`, `183:5`, `298:5`, `351:5` (N31/N27/N29/N30). q и V34 frame assertions `.assertion.12/.15` имеют `SUCCESS`. Cover `REV2_N<N>_ACTUAL_AFTER_COPY_BACK` выведен из того же `check_nN::<true>` как `.cover.1` / `SATISFIED`. Actual путь дошёл до возврата, затем `v[1]` меняется перед проверкой post-return canonical oracle.

Все четыре control projections содержат шесть успешных grouped copy IDs для целевого `ptr::copy_nonoverlapping::<u8>` в `ptr/mod.rs:587:14`. Это `.safety_check.1/.2`, `.arithmetic_overflow.1`, `.precondition_instance.1/.2/.3`. Index `expected_result` — `MATCHED`, observed `FAILED`. У N31/N27/N29 достигнуты все шесть назначенных covers из восьми выведенных. Две дополнительные метки относятся к positive input. У N30 достигнуты все пять covers. Поля `.12/.15` соответствуют `Q_FRAME`/`V34_FRAME`. Координаты actual, возврата, обоих frame и оракула — N31 `33:5/35:5/57:5/58:5/68:5`, N27 `148:5/150:5/172:5/173:5/183:5`, N29 `263:5/265:5/287:5/288:5/298:5`, N30 `325:5/327:5/340:5/341:5/351:5`.

| Positive | Indexed result | Первая CNF (`vars/clauses`, SAT) | Group peak RSS KiB / фаза | CBMC peak RSS KiB |
|---|---|---:|---|---:|
| N31 | `RSS_LIMIT`, projection incomplete, `UNAVAILABLE`, covers 0/7 | 1,443,043 / 2,736,430 | 4,282,080 / `UNKNOWN` (CBMC count 0) | 1,790,644 |
| N27 | `RSS_LIMIT`, projection incomplete, `UNAVAILABLE`, covers 0/7 | 1,247,250 / 2,371,488 | 4,350,184 / `UNKNOWN` (CBMC count 0) | 1,627,080 |
| N29 | `RSS_LIMIT`, projection incomplete, `UNAVAILABLE`, covers 0/7 | 1,343,014 / 2,551,186 | 4,301,468 / `UNKNOWN` (CBMC count 0) | 1,705,112 |
| N30 | `RSS_LIMIT`, projection incomplete, `UNAVAILABLE`, covers 0/5 | 1,394,762 / 2,657,187 | 4,202,664 / `UNKNOWN` (CBMC count 0) | 1,766,972 |

У positives последняя распознанная фаза процесса — `cbmc`, в регистрируемом stdout достигнута первая SAT CNF. Терминал, VT и нативное покрытие отсутствуют в опубликованном результате. Пик группы зафиксирован без CBMC в этом сэмпле. По имеющимся данным причина позднего пика и завершение solve остаются неизвестны. Прогон сохраняет `CONSUMER_PAIRS_OPEN` и `proof_credit=NONE`. [Индекс прогона](/root/ch8-artifacts/run-45876456087/ch8-rev2-n26-n31-consumer-Linux-X64-45876456087-1/index.json) · [Admission](REV2-N26-N28-ADMISSION.md#четыре-остановленных-корня)

| N | Входная контрольная маска | Маска после actual возврата → после XOR |
| ---: | --- | --- |
| 31 | `0x0000_8001` | `0x6000_0000` → `0x6000_0001` |
| 27 | `0x0000_2001` | `0x0600_0000` → `0x0600_0001` |
| 29 | `0x0000_4001` | `0x1800_0000` → `0x1800_0001` |
| 30 | `0x0000_8001` | `0x3000_0000` → `0x3000_0001` |

Каждый контроль проверяет чувствительность общего поста конкретного actual пути при порче после возврата. Маршрут проходит обе S13, перечисленные вставки и merge, затем копию, cover, XOR и канонический оракул. Нативный новый корень проверяет arbitrary-byte copy/frame на границе копии. Применимость к actual пути следует из таблицы рёбер. Исторические positive/control слоты исключены из измерительного roster. [Exact historical roster](REV2-N26-N31-CONSUMER-HANDOFF.md#exact-roster-и-native-anchors)

## Профиль и часы

Один job `ubuntu-24.04`, 90 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC 6.11.0 / CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwind, undefined-function и assertion-reach ON, uninit/validity OFF. На слот ≤120 с VT, ≤180 с cold wall, ≤4 GiB RSS группы, резерв 2 GiB. Каждый слот использует свои cold CWD, Cargo/Kani targets, TMPDIR и export. Ожидается запас за счёт короткой копии и проверок frame. Измеренный расход появится в receipts. [Профиль базы](REV2-N26-N31-CONSUMER-HANDOFF.md#профиль-и-часы)

| Стадия | Граница от monotonic epoch | Внешний timeout |
| --- | --- | --- |
| Prepare с ранним compile preflight и discovery | 54:00, preflight до 180 с с первыми структурированными ошибками | 56 мин |
| Входной gate measure | 55:00 и до 60 с от входа | В составе measure |
| Четыре окна и финальная аттестация | 4×205 с, конец слотов 68:40, аттестации 70:40, внутренний measure 16:45 | 18 мин |
| Finish и upload-gate | Общий cutoff 75:35, внутренний finish ≤5:00 от входа | 6 мин и 1 мин |
| Upload и общий план | Конец upload 82:40, план 88:40 с резервом 6 мин | Upload 7 мин, job 90 мин |

205 с = 180 с cold wall + 10 с reap + 5 с receipt + 10 с launch headroom. Сохраняются checkpoint исхода с reap до проекции, запись времени receipt и bounded retry в finish. Late receipt остаётся вне профиля. После неподтверждённого reap следующие слоты получают `PROCESS_CLEANUP_COULD_NOT_BE_VERIFIED`. Лимиты проекции/артефакта 4/96 MiB. Linux RSS группы может недоучитывать память при смене worker TID. [Часы и измерение](/root/kani-rev2-n26-n31-copy-back-control-w15/ch8-cal1/run.py)

`COPY_BACK_FRAME_WITHIN_PROFILE` требует четыре exact `VERIFIED`/exit 0/`MATCHED`, полные проекции и timely receipts, sampler/reap, все лимиты и своевременную аттестацию `COMPLETE`. Иной исход даёт `COPY_BACK_FRAME_OPEN` с состояниями каждой длины. Офлайн после привязки отдельно решается исследовательский допуск каждой длины. Область pr752 и `stub_verified` оформляется отдельно по правилу композиции. [Гейт отчёта](/root/kani-rev2-n26-n31-copy-back-control-w15/ch8-cal1/report.py) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Локальная сверка и независимое ревью

- Сверены видимость `crate::kani`, `crate::ptr` и `crate::mem::MaybeUninit` под `cfg(kani)`, реализация `Arbitrary` для массивов на пине Kani, ровно четыре plain roots и bounds/pointer lifetimes. Runtime и все прежние helpers побайтно совпадают с базой. Прошли pinned rustfmt `nightly-2026-11-19` с `use_small_heuristics=Max`, `git diff --check`, YAML без дубликатов, `bash -n` для 8 блоков и разбор 15 Python AST.
- Clean bare shallow Std depth 2 без alternates прошёл `bundle verify/list-heads/unbundle`. Единственный объявленный ref — HEAD кандидата. Prerequisite — Std CI-base. HEAD, refs и shallow boundary сохранены. Сверены 20 троек commit/tree/sole-parent, 21 source blob с historical mappings, 289 текстовых и 266 native координат. Отклонены одиночные сдвиги столбца каждого native anchor и целевого copy call.
- Офлайн-модель сверила 45 actual пар с `SWAP_PAIRS` и перебрала 8192 битовых входа S13. Для merge сверены 978 пар упорядоченных битовых половин, включая 31/27/29 терминальных конфигураций N31/N27/N29 и 16 конфигураций N30. Проверены разные ранги, полный D и оба равенства guard. Полнобайтовый вывод опирается на пороговый аргумент и ранговую индукцию выше.
- Из опубликованного discovery `45876456087/1` взяты 90 исторических записей. Добавление четырёх синтетических plain Proof даёт ровно 94. Синтетика отклоняет неправильные tree/payload, прежнюю Actions variable вместо новой, лишние selectors/targets, смещённые координаты, потерю каждого поста, любого из шести copy ID и post-return cover. Также проверены несовпадающие regular/stock свойства, late receipt, cap/VT, отсутствие reap/attestation и общий finish/upload cutoff.
- `test_supervisor.py` сохранён с blob `df63a457c3adf648d360f3d559d5d40ef00a9427` в Control и trigger. На чистом shallow detached review-trigger проверены синтетический `pins` и последовательный suite 123/123 на обычной и свежих шкалах 1, 5, 60 с за 31,712 / 32,731 / 31,833 / 32,021 с. Синтетические `finish`, `upload-gate`, `upload-check` прошли. Индекс подтверждает 4 `NOT_STARTED`, 4 `OPEN` и размеры/SHA-256 7 членов. Диагноз синтетики `COPY_BACK_FRAME_OPEN`.

Локальная работа ограничена Git, статикой, офлайн-моделью и Python/shell синтетикой. Cargo, rustc, Kani, CBMC, CI и push не запускались. Actions variables не менялись.

До copy-back открытой предпосылки в текущей сверке не выявлено. При независимом ревью проверить exact исходники и роли в таблицах, две итерации S13, диапазоны вставок и локальные end, применимость Pair/Center к actual курсорам, оба guard `:1042`, отсутствие разыменования sentinel и полноту D. Сверить перенос на `:425:9`, q/V34 write sets, старые post-return controls и точные координаты свойств новых корней. Переносы длины и базы, ранговая индукция и вывод об инициализации при uninit OFF остаются внешними шагами. Отдельные B14–B16 insert roots имеют `NOT_RUN`. Независимое ревью и GO предшествуют нативным receipts четырёх новых корней.
