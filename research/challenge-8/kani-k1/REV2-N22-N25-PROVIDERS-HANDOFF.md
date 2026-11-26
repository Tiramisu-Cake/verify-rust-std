# REV2 · опоры N22–N25 в форме FIX3

**READY_FOR_REVIEW · `go=NOT_GRANTED` · `proof_credit=NONE`.** Подготовлен локальный пакет из 12 последовательных слотов для одной Ubuntu 24.04 job. Домен — инициализированный V34, реальные `u8/KeyLess<u8>` с числовым `<` и независимый `q: u8`. Для нативного прогона требуется отдельное ревью и GO. Сквозные корни, copy-back и контроли N22–N25 входят в следующий пакет. [Задание](REV2-N22-N25-PROVIDERS-TASK.md) · [Допуск N20/N21](REV2-N20-N21-ADMISSION.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Пины пакета

| Роль и локальный worktree | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Задание g0 | `1ca7aa88ae7aaa21fdd5bdb28f84534992bf4fed` | `880970e8679fdf5608cad4d6f2a95a7052021d90` | `3b4d609a5c8ffb1399b49c3aa5aeea49fab4666f` |
| HEAD g0 на входе, допуск N20/N21 | `91b6c112c107c996ac56c5aeab5ee88d3d83bbf2` | `7a5fe140c711b8b56ca6ee7aafc516eadd507d7a` | `1ca7aa88ae7aaa21fdd5bdb28f84534992bf4fed` |
| Std base | `000e6c4bf6ef0436e83e745618c077d988543169` | `c79edb9b6caf4734907f31590b782f2698b7e647` | `f72f4303bacfff4706b20268a87b2a1031a8ee0b` |
| [Std](/root/verify-rust-std-rev2-n22-n25-providers-w14) · detached sparse | `518fa4563e05b7d3ec8c109aedef53f81edf321d` | `45a05343556e3cf689a64f99f8d9d31124e752b4` | `000e6c4bf6ef0436e83e745618c077d988543169` |
| Control base | `2404b83ff5adcc969939764f405670c00c0bfcaa` | `510af47eeb2689e8e27a20b44e881f5f624f00cf` | `8e1603eef95407eaf03bb592266d7513540682f8` |
| [Control](/root/kani-rev2-n22-n25-providers-control-w14) · work/rev2-n22-n25-providers-control-w14 | `59c9e1f2f99759738b60ba715bb061cda8320f0d` | `66c618e23e858ec95e74fa142472c98eb28efd18` | `2404b83ff5adcc969939764f405670c00c0bfcaa` |
| [Review-trigger](/root/kani-rev2-n22-n25-providers-trigger-w14/control) · detached, ref review/rev2-n22-n25-providers-trigger-w14 | `92a51f837d3fe48beb7a796f5b3a92f654f71114` | `66c618e23e858ec95e74fa142472c98eb28efd18` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Ожидаемая независимая Actions variable `CH8_REV2_N22_N25_PROVIDERS_TRIGGER_TREE=66c618e23e858ec95e74fa142472c98eb28efd18` передаётся как `REV2_N22_N25_PROVIDERS_TRIGGER_TREE`. `pins`, `sources` и `finish` проверяют этот tree, clean detached checkout, sole parent, `Tiramisu-Cake/kani`, `refs/heads/uninit-ci/ch8-q-pilot-v1`, push attempt 1 и равенство HEAD, `GITHUB_SHA` и payload `after`. `sources` и `finish` сверяют исходный trigger receipt. `sources` проверяет все объекты цепочки overlay, восстанавливает предыдущие cfg-off blobs и сверяет пины источников. `finish` повторяет source/coordinate gate при наличии успешного source receipt. Принятый `ch8-cal1/test_supervisor.py` в control и trigger имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427`.

Std CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`. Bundle объявляет только `HEAD` с prerequisite Std CI-base.

| Вход | SHA-256 |
| --- | --- |
| [Frozen request](/root/kani-rev2-n22-n25-providers-control-w14/ch8-cal1/CI-REQUEST.json) | `482d10cdee0842dd13c6fe3406b08fc80d0bbcfe8972a8f44a4858c53c1ace48` |
| Canonical JSON roster, sorted keys и разделители `(",", ":")` | `7c720517f5b8973a2d879c8041f4670c84b4d4981baef4c20dc23a24c60c90d5` |
| [Std overlay bundle](/root/kani-rev2-n22-n25-providers-control-w14/ch8-cal1/std-overlay.bundle), 44,032 байт | `7fa92c87d708b33f9fdd8eadc518b1dc9d117ab1e6c5445b48d0f88d018091a0` |
| Canonical JSON source bindings | `64dcf53b07abdaa9cbfff59e5f7addb532bcdfc7f1fd9eaf67fe6700922c5bba` |

## Exact roster

Каждый selector имеет префикс `slice::sort::shared::smallsort::verify::rev2_n22_n25_providers::`. Ожидается `VERIFIED`, exit 0, `MATCHED`, весь список обязательных covers и anchors.

| № | Slot | Selector после префикса | Kind и цель | Обязательные covers | Latest start |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | `S9-B12-L12-BITS` | `s9_b12_l12_bits` | PLAIN_PROOF | 4 | 50:00 |
| 2 | `S9-B12-SWAP` | `s9_b12_swap` | Check `swap_if_less` | 5 | 53:25 |
| 3 | `S9-B13-L12-BITS` | `s9_b13_l12_bits` | PLAIN_PROOF | 4 | 56:50 |
| 4 | `N22-PAIR-FIXED` | `n22_pair_fixed` | Check `actual_pair_step_n22` | 10 | 60:15 |
| 5 | `N23-PAIR-FIXED` | `n23_pair_fixed` | Check `actual_pair_step_n23` | 10 | 63:40 |
| 6 | `N23-ODD-CENTER` | `n23_odd_center` | Check `actual_odd_center_n23` | 4 | 67:05 |
| 7 | `N24-PAIR-FIXED` | `n24_pair_fixed` | Check `actual_pair_step_n24` | 10 | 70:30 |
| 8 | `N25-PAIR-FIXED` | `n25_pair_fixed` | Check `actual_pair_step_n25` | 10 | 73:55 |
| 9 | `N25-ODD-CENTER` | `n25_odd_center` | Check `actual_odd_center_n25` | 4 | 77:20 |
| 10 | `INSERT-B01-L12-BYTES` | `insert_b01_l12_bytes` | PLAIN_PROOF | 8 | 80:45 |
| 11 | `INSERT-B12-L12-BYTES` | `insert_b12_l12_bytes` | PLAIN_PROOF | 8 | 84:10 |
| 12 | `INSERT-B13-L12-BYTES` | `insert_b13_l12_bytes` | PLAIN_PROOF | 8 | 87:35 |

Профиль — CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, safety/overflow/unwind/undefined-function/assertion-reach ON, uninit/validity OFF. Пакет применяет actual функции и обёртки только в verification cfg. Std delta добавляет модуль, его регистрацию и check-cfg. Actual runtime, существующие контракты и библиотеки исторических опор побайтно совпадают с принятым Std.

## Геометрии и рёбра

В рассматриваемых caller-геометриях `S=&v[1]` задаёт начало переданного среза. Actual `small_sort_network` вычисляет `m=N/2` и получает `S` через `v.as_mut_ptr()`. Первая половина начинается в S, вторая в `S+m` и имеет длину `N-m`. Выбор sort13/sort9 и вызов insertion driver происходят для каждого среза отдельно. При L13 driver получает offset 13 и его цикл не выполняется (`tail == v_end`). [Actual dispatch](/root/verify-rust-std-rev2-n22-n25-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:385)

| N, m | Source | Левая половина | Правая половина | Pair / odd |
| --- | --- | --- | --- | --- |
| 22, 11 | `v[1..23]` | `v[1..12]`, S9 B01, B01/L11 prefix | `v[12..23]`, S9 B12/L11 и INSERT B12/L11 через перенос L12→L11 | `N22-PAIR-FIXED`, D[k]/D[21-k], k=0..10 |
| 23, 11 | `v[1..24]` | `v[1..12]`, S9 B01, B01/L11 prefix | `v[12..24]`, exact S9 B12/L12 + B12 swap + INSERT B12/L12 | `N23-PAIR-FIXED`, D[k]/D[22-k], k=0..10, и `N23-ODD-CENTER` в D[11] |
| 24, 12 | `v[1..25]` | `v[1..13]`, S9 B01 + INSERT B01/L12 | `v[13..25]`, exact S9 B13/L12 + prior B13 swap + INSERT B13/L12 | `N24-PAIR-FIXED`, D[k]/D[23-k], k=0..11 |
| 25, 12 | `v[1..26]` | `v[1..13]`, S9 B01 + INSERT B01/L12 | `v[13..26]`, exact prior S13 B13/L13 bits и swap | `N25-PAIR-FIXED`, D[k]/D[24-k], k=0..11, и `N25-ODD-CENTER` в D[12] |

Sort9 использует guard `len>=9`, один base pointer и 25 сравнительных пар между rel0 и rel8. Поэтому B01/L09 переносится на B01/L11 и L12, а B12/L12 на B12/L11 при том же base и guard. Адреса хвоста rel9–11 отсутствуют в расписании. Новые S9 корни оставляют произвольный хвост и внешний frame без изменений. Исторический FIX3 B01 swap и S13 B13 swap покрывают `a<b<13` на своих bases, включая все нужные S9 пары с `b<9`. Actual comparator читает только аргументы. Для каждого порога t проекция `[byte>=t]` переводит min/max пары в AND/OR, поэтому битовый oracle упорядоченного popcount переносится по расписанию на числовой порядок девяти байтов и сохраняет все кратности. N25 справа использует свою exact S13 геометрию. [Actual sort9](/root/verify-rust-std-rev2-n22-n25-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:538) · [Actual sort13](/root/verify-rust-std-rev2-n22-n25-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:597)

Каждый byte driver предполагает только числовой порядок первых девяти байтов. Три plain Proof вызывают actual `insertion_sort_shift_left` с offset 9 и полным произвольным хвостом. Пост включает порядок всего среза, `count(byte<q)`, q/V34 frame и covers normal return, no-shift и full-shift на rel9, 10 и 11. Так как actual сравнение не зависит от q, при фиксированном входе можно брать все пороги, с кратностью b<255 из `C(b+1)-C(b)`, а 255 из `L-C(255)`.

Для L11 первый хвостовой адрес равен `base+9`, end равен `base+11`. Граница L12 равна `base+12`, так что только длинный путь запускает rel11. Инвариант перед шагом r — `[0,r)` упорядочен и содержит исходные кратности префикса, `[r,L)` содержит исходные байты. Actual `insert_tail` читает predecessor и tail. При необходимом сдвиге сохраняет tail в отдельный tmp и переносит соседнюю ячейку `sift` в дыру `sift+1`, затем `CopyOnDrop` заполняет последнюю дыру из tmp. Каждый одноэлементный перенос имеет свой initialized source и writable destination, непересечение следует из соседних различных адресов либо из отдельного tmp. Нижнюю границу защищает `sift == begin`. Чтения и записи ограничены `[0,r]`. Индукция сохраняет порядок, кратности и frame на r=9, затем r=10, независимо от rel11. Таким образом, короткие actual рёбра B01 для N22/N23 и B12 для N22 ограничены верхней целью rel10 и заканчиваются там при собственном one-past-end. Итог после третьей вставки L12 может менять ранние ячейки, поэтому перенос опирается на первые две actual итерации. [Actual insert_tail](/root/verify-rust-std-rev2-n22-n25-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:701) · [Actual driver](/root/verify-rust-std-rev2-n22-n25-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:742)

Четыре отдельных Check фиксируют `N,m` и весь диапазон `0<=k<m`. При `a+b=c+d=k` up получает `(S+a,S+m+b,D+k)`, down — `(S+m-1-c,S+N-1-d,D+N-1-k)`. Четыре read offsets лежат в соответствующих инициализированных половинах. Новые цели записи лежат в отдельном writable `MaybeUninit<[u8;32]>`. `k<N-1-k<N`. Check проверяет точные тройки курсоров, min/max с выбором left для up tie и right для down tie, source/q frame и modifies только обеих целей. Harness читает только эти две записанные ячейки. Native gate требует выбранный Check instance, `memcpy.assigns.1/.2` и шесть grouped `ptr::copy_nonoverlapping::<u8>` anchors `ptr/mod.rs:587:14` с exact Location/Status. Повторные копии связываются с группой через конкретные source calls, утверждения о курсорах и covers после actual возврата. Grouped property ID относится к группе вызовов. [Actual up/down](/root/verify-rust-std-rev2-n22-n25-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:862) · [Правило grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

Два odd Check используют терминальные счётчики `a+b=c+d=m` и остатки `(m-a-c,N-m-b-d)` из `{(1,0),(0,1)}`. Обёртки воспроизводят actual `wrapping_add(1)`, проверку `left<left_end`, single-byte copy из выбранного адреса в D[m], продвижение выбранного курсора и оба равенства end guard. При `c=m` левый reverse sentinel равен `S-1` и используется для получения `left_end=S`. Копия читает правый остаток. Обе ветки, post-copy и sentinel имеют отдельные covers. [Actual odd branch](/root/verify-rust-std-rev2-n22-n25-providers-w14/library/core/src/slice/sort/shared/smallsort.rs:1027)

## Исторические опоры

Индексы и члены структурированных receipts/projections сверены по размеру и SHA-256. Во всех четырёх слотах native outcome `VERIFIED`, exit 0, stock tool совпадает и итоговая аттестация завершена. Proof credit нового пакета остаётся `NONE`.

| Run | Std commit / tree | SHA-256 индекса |
| --- | --- | --- |
| [45661535099](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/index.json) | `32129c149a15fb1b60a7314e738f3cb466d076e5` / `1b0cc32c571b370178e64f2b8c79773d2ce27051` | `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be` |
| [45688753097](/root/ch8-artifacts/run-45688753097/ch8-rev2-s13-geometries-Linux-X64-45688753097-1/index.json) | `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a` / `ff2563b5867b8327b95db909262ddf80e3ed9c03` | `e575daf8b20bab3c3023b8809e61cc21ea1a4bf9be85153d572368e6bbf663b7` |
| [45749463113](/root/ch8-artifacts/run-45749463113/ch8-rev2-n18-n19-providers-Linux-X64-45749463113-1/index.json) | `86ea7aa5b773888e52f9fb78fda38d5cbff9ea61` / `63b199cc33052d6390fd0fdaa2b5c36962545fc4` | `065a9d8c2738117b36101eb7f3dcb5c8e568506c79b90b7953d561ae49d39504` |

| Slot · run | SHA-256 receipt | SHA-256 projection |
| --- | --- | --- |
| `S13-SWAP-LEAF` · 45661535099 | `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c` | `3f81b2c134cdba1348d9720fafb5569dbc37195693e47485c8bb1b80fe28d596` |
| `S13-B13-L13-BITS` · 45688753097 | `f672c1152444500e7e80d233dfc3401c2ea9eabd25bb5f9a54fd759163efcd94` | `9a888efb0e5c88aa685743bed8de273eeb2457b03e270af5a62a59a3f270eb2b` |
| `S13-B13-L13-SWAP` · 45688753097 | `e936c63e821f880d80527a7ce22ed78842e100bb11f6d9178fda0f4501b8982a` | `17f8dda9bf3f7199f7142fadadfdd6d31aef7030f480f164a888d982999240b8` |
| `S9-B01-L09-BITS` · 45749463113 | `41e3435e50904c0cd683a7503a05d4428418557b3bfeddee95242d97c59551e3` | `46478975751c93569d9d1d0c681a9d623b2414db7129a1668e4ba05962649e48` |

## Окна job и receipts

| Шаг | Внутренняя граница от monotonic epoch | Внешний таймаут |
| --- | --- | ---: |
| Старт, checkout control, pins, checkout Std/Kani, sources, setup action | В составе общего окна setup. Pins до 45 с собственной проверки, sources до 120 с, обе проверки не позже 49:00. Четыре последовательных suite внутри pins, watchdog 90+5 с на каждый. | 1 / 2 / 8 / 5 / 4 / 3 / 15 мин |
| `prepare` | До 49:00, включая нативный overlay compile preflight до 180 с, затем exact discovery. К 50:00 зарезервированы 60 с для measure input gate. | 51 мин |
| `measure` | 44:05 от входа, до 60 с входной gate, 12×205 с слоты, 120 с аттестация и 5 с журнал. Слоты ограничены 91:00, аттестация 93:00. | 46 мин |
| `finish` | До 5:00 от входа и не позже epoch+98:00. | 6 мин |
| `upload` | До 7:00, абсолютная граница 105:00 с 5 с запаса на переход к upload. Отдельные проверки допуска и завершения сверяют epoch. | 7 мин, проверки по 1 мин |
| Резерв плана и граница job | До 114:00 и 120:00 соответственно. | 120 мин на job |

Slot stride 205 с складывается из cold wall 180, reap 10, receipt 5 и launch headroom 10. Ранний setup позволяет запустить первые слоты раньше, сохраняя полное окно. При позднем входе gate по-прежнему ограничен 60 с и не сдвигает абсолютные latest starts. Слот с истёкшим окном помечается отдельно, последующие сохраняют свои окна. У каждого слота свой CWD, Cargo/Kani targets, TMPDIR и export. При неподтверждённом reap следующие слоты получают `PROCESS_CLEANUP_COULD_NOT_BE_VERIFIED`. До проекции атомарно сохраняется disposition/reap checkpoint. Receipt и retry ограничены по времени, поздняя публикация сохраняет наблюдение без допуска. Projection cap 4 MiB, artifact cap 96 MiB. Group RSS cap 4 GiB и Ubuntu reserve 2 GiB. Linux group RSS может недоучесть память при смене worker TID. Receipt сохраняет native anchors ID/Location/Status, phase/CNF, VT/wall, group и CBMC RSS, sampler/reap и covers. Итоговая аттестация повторяет tool и overlay identities. `PROVIDERS_WITHIN_PROFILE` требует все 12 exact, timely complete, uncensored слоты в профиле, VT≤120 с и завершённую в своём окне аттестацию.

Compile preflight запускается до discovery в предусмотренном workflow и при ошибке сохраняет первые rustc diagnostics как данные. Оба stock JSON list сверяют наследуемый инвентарь. Cfg-on delta содержит ровно 12 записей. Для Check discovery сверяет exact selector, kind и файл, а также resolved object `contracts[].function`/файл по harness association. Terminal gate сверяет lexical `ProofForContract.target_fn` из pinned stock Kani и exact concrete instance через regular ID и stock contract symbol.

## Источники и координаты

| Source на Std HEAD | Git blob |
| --- | --- |
| `library/core/src/slice/sort/shared/smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `library/core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `library/core/Cargo.toml` | `c7674269cff9a76c7e92fd0591275e852b2da753` |
| `library/core/src/lib.rs` | `55ac6c8aea35124efa0b68d9ea6d58af66535273` |
| `library/core/src/slice/sort/shared/smallsort/verify.rs` | `358cc626f40865b0053f311cd33e5944a06f9de0` |
| `library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` |
| `library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs` | `d3c2a137f7332d79e7ce8596a517fd8b5f2dbe19` |
| `library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs` | `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` |
| `library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_geometries.rs` | `c403b343270752fb03fc087a101b55d8dc20a7ab` |
| `library/core/src/slice/sort/shared/smallsort/verify/rev2_n18_n19_providers.rs` | `9f5f22527656fd0b9b6afa879d7b8bb7574ff5c3` |
| `library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_providers.rs` | `c88c3a1240181b0949be7cd7154de20ff83304b3` |
| `library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_pair_fixed.rs` | `b8580df3448e100d7ecb0811ebba0f14041ad412` |
| `library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_consumer.rs` | `a82bbf483c1d445dbdd6dacf4b5b12f3ac8dd7eb` |
| `library/core/src/slice/sort/shared/smallsort/verify/rev2_n22_n25_providers.rs` | `8af3e2cc28c73407a3544151112ddf65c7f491fc` |

Координаты даны как `line:1-based byte column`. Литеральные токены всех actual anchors закреплены в [source_bindings](/root/kani-rev2-n22-n25-providers-control-w14/ch8-cal1/CI-REQUEST.json) и проверяются на pinned blobs. Label, exact file/line/column/function, Check target и grouped properties для каждой строки записаны в том же request в `roster[].native_evidence.coordinates` и `roster[].check_evidence`.

| Actual source | Координаты в `smallsort.rs` |
| --- | --- |
| Scratch, split, guards, left/right creation, sort/insert calls, merge/copy-back | `383:27, 385:5, 386:5, 389:5, 391:31, 395:9, 396:13, 398:11, 399:13, 405:9, 416:27, 424:9, 425:9` |
| Swap и sort9 guard/первая и последняя пары | `488:1, 503:27, 538:1, 542:5, 553:9, 577:9` |
| Sort13 guard/первая и последняя пары | `597:1, 601:5, 612:9, 656:9` |
| Gap repair и insertion | `362:13, 701:1, 706:9, 715:9, 722:13, 725:13, 730:13, 731:13, 742:1, 759:9, 761:9, 764:13, 767:13` |
| Merge helpers и one-byte copies | `862:1, 883:9, 885:9, 895:1, 916:9, 918:9` |
| Merge split, cursor setup и pair calls | `965:1, 1002:5, 1014:9, 1015:9, 1018:9, 1019:9, 1020:9, 1022:9, 1023:34, 1024:46` |
| Odd wrapping ends, branch, selected byte, copy, cursor updates, final guard | `1027:24, 1028:25, 1031:9, 1032:13, 1033:13, 1034:13, 1035:13, 1036:13, 1042:9` |

Actual comparator cover `cal1_model.rs:28:9`, числовой `<` в FnMut на строке 29. Grouped copy/move anchors — `ptr/mod.rs:587:14` и `ptr/mod.rs:682:9`. Actual specialize dispatch для `u8: FreezeMarker+CopyMarker` вызывает `small_sort_network` на `smallsort.rs:220:13`. Двенадцать наборов native labels содержат 166 вхождений, включая actual comparator. [Provider-модуль](/root/verify-rust-std-rev2-n22-n25-providers-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n22_n25_providers.rs)

## Локальные проверки

- Std проверен на точность cfg/видимости и byte-for-byte runtime/contracts diff. Двенадцать roots имеют explicit attributes. Профиль проверен отдельно для plain Proof и Check. Rustfmt прошёл на новом модуле и registry с `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max`. Для registry добавлены `skip_children=true,reorder_modules=false`.
- Независимый локальный shallow bare import без alternates проверил unbundle, единственный advertised HEAD, prerequisite, 15 commit/tree/sole-parent и exact cfg layouts. Исходные refs и shallow boundary сохранились. Сверены 65 actual source и 166 native label координат. Сдвиг каждого столбца на +1 проверен отдельно и отклонён. YAML разобран с запретом дублированных ключей, `bash -n` прошёл для восьми shell blocks. AST проверка прошла для 15 Python-файлов, проверка затенения импортов прошла для runner/request/report/results.
- Офлайн-сверка actual расписаний проверила 512 битовых префиксов sort9 и 8192 sort13. Проверены все 506/506/650/650 pair offset tuples для N22/23/24/25, 23/25 терминальных odd tuples и sentinel.
- Синтетика проверила точные roster/selector/kind/file/Check objects, compile diagnostics и cfg delta, обязательные covers и native coordinates, grouped copy anchors, late/deferred/partial receipts, reap и сроки. В точном блоке pins финального trigger suite прошли последовательно на обычной шкале и 60/5/1 с, по 114 тестов каждый. Время suite — 26.270 / 26.971 / 26.550 / 26.183 с, всего pins — 108.359 с.
- Synthetic push прошёл pins и finish, результат `PROVIDERS_OPEN` с 12 `NOT_STARTED`, проверены 15 членов индекса. Все 14 негативных проверок отклонили подмены tree, старую переменную, чужой payload SHA или изменённый trigger admission receipt. `git diff --check` прошёл для Std, control, trigger относительно sole parent и handoff.

Нативный compile preflight, cfg discovery и все 12 новых terminal receipts ожидают отдельного GO. Коммиты локальные, с `[skip ci]`, автор Tiramisu-Cake. Push, CI, изменения Actions variables и локальные запуски cargo, rustc, Kani и CBMC отсутствуют.
