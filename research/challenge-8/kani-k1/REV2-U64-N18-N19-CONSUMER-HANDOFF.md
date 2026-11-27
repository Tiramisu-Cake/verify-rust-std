# REV2 · сквозные проверки u64 N18/N19

**`READY_FOR_REVIEW` · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Подготовлены два сквозных битовых Proof фактической сети, два различающих post-return контроля и две локальные проверки точной копии с frame. Независимое ревью и отдельный GO предшествуют запуску. Нативная компиляция, discovery, исходы и ресурсы шести слотов открыты. [Задание стадии](REV2-U64-N18-N19-CONSUMER-TASK.md)

## Worktrees и замороженные входы

| Роль и checkout | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n18-n19-consumer-w15) · `work/rev2-u64-n18-n19-consumer-std-w15` | `099f0c438c08e7870dd8df513a8cf7a993c39e47` | `f2076c5316f670a9ae14f383546a6afdee325666` | `c8eefae4c8073cff31e5576b372d5105b52797a1` |
| [Control](/root/kani-rev2-u64-n18-n19-consumer-control-w15) · `work/rev2-u64-n18-n19-consumer-control-w15` | `d15d3c49f57740f89686a90ce17814e3fe54919a` | `27ae39f1a845f473cac270ec20ecdfbb47bd7559` | `44aa6a2273588502083e47e204730dd67e0fba51` |
| [Review-trigger](/root/kani-rev2-u64-n18-n19-consumer-trigger-w15/control) · detached · `review/rev2-u64-n18-n19-consumer-trigger-w15` | `7debf5a70e0361d678731f4f986ba1008960e621` | `27ae39f1a845f473cac270ec20ecdfbb47bd7559` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std FIX1 base tree `4f9687a4edccf69ef86ee8b4c2e01de9b3517539`, Control FIX1 base tree `74f90d62acda5157906272454ec9d6c4bb9819db`. Bundle начинается от CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655` и объявляет один `HEAD`. В цепочке 25 overlay-коммитов. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n18-n19-consumer-trigger-w15/control/ch8-cal1/CI-REQUEST.json) | `18dbcbde6348c981312016f27237373ce8467a3fb26ab1192a42a4f97a5c8aa2` |
| Exact roster, канонический JSON | `aeb4cfe5158c6588601ae94c59182e83a4998f53a0a62dd737d2eab0114b2514` |
| Source bindings, канонический JSON | `d804b49dd41323126274c9add0be844ac3be19db508ff25862461b2a97d2cbde` |
| [Std bundle](/root/kani-rev2-u64-n18-n19-consumer-trigger-w15/control/ch8-cal1/std-overlay.bundle), 67 174 байта | `3dee3db66bc336b456837e4bb402aba218a5c17177a2c3da687da4e630b29c24` |
| [Workflow](/root/kani-rev2-u64-n18-n19-consumer-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) | `3dab9d22447fc26a53069b19fc8fd48160655566e87b767dce5fb5c2af9a11f6` |

Для будущего GO независимый pin `CH8_REV2_U64_N18_N19_CONSUMER_TRIGGER_TREE` получает tree из строки review-trigger. `pins`, `sources` и `finish` требуют чистый detached checkout в `control`, fork `Tiramisu-Cake/kani`, событие push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, совпадение HEAD, `GITHUB_SHA` и payload `after`, указанный sole parent и утверждённый tree. Upload-gate повторяет admission и сверяет trigger из индекса с сохранённым receipt. Индекс `smallsort-rev2-u64-n18-n19-consumer-artifact-v1` связывает request, roster, bindings, bundle и хэши членов. [Гейт Control](/root/kani-rev2-u64-n18-n19-consumer-trigger-w15/control/ch8-cal1/run.py)

## Exact roster и нативные метки

Все корни plain `Proof`, `unwind(36)`, `copy_back=true`. Полный selector получается добавлением суффикса к `slice::sort::shared::smallsort::verify::rev2_u64_n18_n19_consumer::`. Координаты в таблице относятся к [новому модулю](/root/verify-rust-std-rev2-u64-n18-n19-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n18_n19_consumer.rs) с Git blob `8918ca0206d3f0af9aa25c788052749db0b618fc`.

| Слот | Exact selector suffix | Root | Ожидаемый исход | Успешные assertions / covers | Latest start |
| --- | --- | ---: | --- | ---: | ---: |
| `U64-N19-ACTUAL-BITS` | `u64_n19_actual_bits` | 15:1 | VERIFIED / 0 | 3 / 5 | 55:00 |
| `U64-N19-WITNESS-CORRUPT` | `u64_n19_witness_corrupt` | 26:1 | FAILED / 1 | 2 / 4 | 58:25 |
| `U64-N18-ACTUAL-BITS` | `u64_n18_actual_bits` | 32:1 | VERIFIED / 0 | 3 / 3 | 61:50 |
| `U64-N18-WITNESS-CORRUPT` | `u64_n18_witness_corrupt` | 38:1 | FAILED / 1 | 2 / 3 | 65:15 |
| `U64-N19-COPY-BACK-FRAME` | `u64_n19_copy_back_frame` | 44:1 | VERIFIED / 0 | 3 / 1 | 68:40 |
| `U64-N18-COPY-BACK-FRAME` | `u64_n18_copy_back_frame` | 50:1 | VERIFIED / 0 | 3 / 1 | 72:05 |

| Метка или группа | Класс и привязка |
| --- | --- |
| `REV2_U64_N13_COMPARATOR_CALLED` | cover `rev2_u64_n13::u64_less`, 9:5 в `rev2_u64_n13.rs`, blob `47c129a11d6cd0d0adce0be450b91eca84a25c0c` |
| `REV2_U64_ACTUAL_MIXED_INPUT`, `AFTER_COPY_BACK` | covers 66:5 и 73:5 в `check_actual_bits::<19>` и `::<18>` |
| `REV2_U64_N19_ACTUAL_NINE_SHIFT_INPUT` | cover 68:9 в `check_actual_bits::<19>`, у обоих N19 |
| `REV2_U64_N19_ACTUAL_ODD_RIGHT_REMAINDER_LEFT_REVERSE_SENTINEL` | cover 17:5 в `u64_n19_actual_bits` |
| `REV2_U64_ACTUAL_V34_FRAME`, `REV2_U64_ACTUAL_CANONICAL_OUTPUT` | assertion 82:5 и 91:5 в `check_actual_bits::<N>`, успех во всех четырёх сквозных корнях |
| `REV2_U64_N18_ACTUAL_SORTED_POPCOUNT`, `REV2_U64_N19_ACTUAL_SORTED_POPCOUNT` | assertion 94:9 и 96:9 в `check_actual_bits::<18>` и `::<19>`. успех positive, единственный `FAILURE` соответствующего контроля |
| `DEST_EQUALS_SOURCE`, `SOURCE_PREFIX_FRAME`, `V34_FRAME` | assertion 124:5, 125:5, 131:5 в `check_copy_back::<19>` и `::<18>` |
| `AFTER_COPY_BACK_FRAME` | cover 132:5 в `check_copy_back::<19>` и `::<18>`, после всех постов |

Оба positive охватывают все входные маски длины N. Helper устанавливает активные слова в 0/1 и сравнивает выходную маску с `low ^ (low >> popcount(input))`. Каноничность каждого полного слова и внешний frame проверяются отдельно. В обоих контролях фактическая сеть на :72:5 возвращается до `AFTER_COPY_BACK` и до порчи :75:9. Маски свидетелей заданы литералами в roots. `u64_less` сравнивает полные слова оператором `<`. Регистрация зависит от нового флага и флага N13 внутри `cfg(kani)`. Std добавляет новый модуль, регистрацию в `verify.rs` (blob `3cdbc142a71ebd597571823f317b7d957b4f6a26`) и check-cfg в `core/Cargo.toml` (blob `6f9dc10d14fb305f8017887ad481c8169d5a4619`). Совпадение с файлами базы после удаления cfg-вставок проверено побайтно.

Для всех шести слотов обязательны успешные grouped properties `ptr::copy_nonoverlapping::<u64>.safety_check.1/.2`, `.arithmetic_overflow.1` и `.precondition_instance.1/.2/.3` на `core/src/ptr/mod.rs:587:14`, blob `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6`. В сквозных корнях эта группа охватывает выведенные экземпляры копий обмена, вставки, merge и последней копии. Исходные координаты и возврат из actual сети связывают группу с последней копией. В локальном корне единственный целевой вызов закреплён на :115:14, а три скалярных поста проверяют записанные и сохранённые слова. Regular сверяет function, class, file, line, column, статусы и метки. stock сверяет роль Proof, профиль, итог, агрегаты успешных checks и ID достигнутых covers и единственного контрольного отказа. Все выведенные unwind properties должны иметь `SUCCESS` при stock `unwinding=ON`. [Сопоставление нативных каналов](/root/kani-rev2-u64-n18-n19-consumer-trigger-w15/control/ch8-cal1/results.py) · [Правило grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

## Исходные опоры

Опорный Std checkout `/root/verify-rust-std-rev2-u64-n18-n19-w15`, commit `c8eefae4c8073cff31e5576b372d5105b52797a1`, tree `4f9687a4edccf69ef86ee8b4c2e01de9b3517539`.

| Исходный файл | SHA-256 | Нужные координаты |
| --- | --- | --- |
| `library/core/src/slice/sort/shared/smallsort.rs` | `2fa108b8624d7888eee369c207ea2ac9b01911cac0a1808a0bc93351e980ee17` | цикл регионов и dispatch 385–417. sort9 538–578. `CopyOnDrop` gap-fill 351–365, copy по 362:13. `insert_tail` 701–735, driver 742–769. actual copy-back 423–426, call 425:9. merge-up copy 883–888. merge-down copy 916–921. merge 1014–1045, 9 итераций в 1022, odd center 1030–1036, сравнение cursors 1042. |
| `library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n18_n19.rs` | `e5054cdaa4e46c976c6c0502ee246cf574e6eb76376cdc0918a8165fd7dbbedb` | source frame 222–227. pair checks 64–225. odd center 230–314. insertion check 316–354. sort9 bit checks 356–396. B10 swap check 401–425. |

Опубликованный `source.json` run `45938919685/1` закрепляет git blobs `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` для `smallsort.rs` и `4ea168fc664f9f4733a80082af9cdd441f06a2ed` для модуля опор. оба совпали с read-only `git hash-object` в закреплённом checkout. Опорный source receipt помечен `native_coordinates_checked=true`. Хэши receipt/projection взяты из `members` опубликованных индексов.

Actual `len_div_2=9`: левая область `v[1..10]`, правая `v[10..19]` для N18 и `v[10..20]` для N19. Цикл регионов `:394–417` вызывает sort9 на обеих половинах. Guard одинаково проходит. у B10 совпадают база и rel0..8. Для N18 правая область длины 9, для N19 — 10, но sort9 читает те же rel0..8. Только N19 затем вставляет abs19 один раз: dispatch `:405`, insertion driver `:742–769`, offset 9.

## Исторические native-роли

Индексы сообщают `attestation=COMPLETE`. Индекс FIX1 N18/N19 имеет SHA-256 `7b1e589aaf491a38f2e5232411ee734793e73f79e08d5e6c956d9669544fc202`, индекс N13 FIX1 имеет SHA-256 `6d7e603aa2fe26dd62c0f41725d664bf726be89836c16c35efbe641f3a0661f9`. Историческая схема индекса опор N18/N19 сохраняет имя `smallsort-rev2-u64-n14-n17-artifact-v1`. Роли определены по run/attempt, pins, roster и member hashes. В колонке «Исходник» P означает `rev2_u64_n18_n19.rs` blob `4ea168fc664f9f4733a80082af9cdd441f06a2ed`, S означает `smallsort.rs` blob `0b77c3dbb3b767ba35281a2a686aa477ff1344c5`, N13 означает FIX1 `rev2_u64_n13.rs` blob `6658b28d64647aa6e11c5bee3c71a135f09b2a6c`. [Допуск N13](REV2-U64-N13-ADMISSION.md) · [FIX1 опор N18/N19](REV2-U64-N18-N19-HANDOFF.md#fix1--устранение-замечания-r1)

| Run/attempt и роль | Длины | Исходник и native anchors | Результат | Receipt SHA-256 | Projection SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `45919454859/1`, `U64-N13-SWAP` (B01) | 18, 19 | Plain B01 min/max/frame N13:35:5, 36:5, 42:5. S:488:1, 517:9, 518:9 | `VERIFIED/MATCHED`, exit 0, unwind 36, covers 5/5 | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` | `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| `45938919685/1`, `U64-N18-PAIR-STEP` | 18 | Check `actual_pair_step_n18` P:15:1, 21:5. курсоры 43:9, 53:9. полные слова/frame 104–106:5. S:885:9, 918:9 | `VERIFIED/MATCHED`, exit 0, unwind 36, covers 10/10 | `5545c3c65cc2b28ee54e2d9ce8a689f03ef970acade85e8a2efdecf9f34c6903` | `697d9ccf4e046202726eab8968da7cdd876de4f805ecc37529dd0ad32d1623e1` |
| `45938919685/1`, `U64-N19-PAIR-STEP` | 19 | Check `actual_pair_step_n19` P:119:1, 125:5. курсоры 147:9, 157:9. полные слова/frame 208–210:5. S:885:9, 918:9 | `VERIFIED/MATCHED`, exit 0, unwind 36, covers 10/10 | `3b65ca74a6528e22f3887c5984489f96e6eb387f9e6c72e4b6a67fd616204974` | `7d08bf51855afd9f63cb38670652076d9bf8f2fe54e3937836807f96a325dca5` |
| `45938919685/1`, `U64-N19-ODD-CENTER` | 19 | Check `actual_odd_center_n19` P:230:1, 236:5. typed copy 257:9. адрес, слово, курсоры и frame 299/300/301/305/309:5. S:1027–1042 | `VERIFIED/MATCHED`, exit 0, unwind 36, covers 4/4 | `a61c318e23dec5c730be6ab6adc5e86a7e1f2943750c21a21fa879b0b4decc0e` | `52b516e11943e768fbcd7324a507af020d63091779e6f95e6cd41f3f1809b5` |
| `45938919685/1`, `U64-N19-INSERT-RIGHT` | 19 | Plain точный пост и frame P:347:5, 352:5. S:722:13, 362:13, 764:13 | `VERIFIED/MATCHED`, exit 0, unwind 36, covers 5/5 | `cb006967310f0f7b1d383055ff54f85ea12fa7a1475bddad924685ab340456cc` | `33175f1faf076f67fced1d2fd24c45776de6cb9d089457a0f81e0f5d8b6198b3` |
| `45938919685/1`, `U64-S9-B01-L09-BITS` | 18, 19 | Plain `check_sort9_bits::<1, 9>` P:389:5, 390:5, 395:5. S:538–578 | `VERIFIED/MATCHED`, exit 0, unwind 36, covers 4/4 | `f7d5bf7f80cf4eca3f1f000f4f92a5e760ca4c036cfee1e68a426b66fbc9f4b1` | `417dd157952fb184de5affd6dc2a4f5a2732615955253c10234464bf0c01959f` |
| `45938919685/1`, `U64-S9-B10-L10-BITS` | 18, 19 | Plain `check_sort9_bits::<10, 10>` P:389:5, 390:5, 395:5. S:538–578 | `VERIFIED/MATCHED`, exit 0, unwind 36, covers 4/4 | `e16475a8d835e7e1ca543d5c702bcf308b624a3c53c9d080d381fb0f49b808e2` | `a37ae7df1cbd28514d1e63a9784146d3b036c3eaecfbeae5b6f3a72917d47320` |
| `45938919685/1`, `U64-S9-B10-SWAP` | 18, 19 | Plain B10 min/max/frame P:418:5, 419:5, 424:5. S:488:1, 517:9, 518:9 | `VERIFIED/MATCHED`, exit 0, unwind 36, covers 5/5 | `e08dabec536d6167606b761a90a6b721aa3036926d27a5beb4b5f72ec1f8613d` | `2083050800949d0949d9dd9279375ea81046f4e3775b46a6b66567c08a1129df` |

[Индекс N13 FIX1](/root/ch8-artifacts/run-45919454859/ch8-rev2-u64-n13-Linux-X64-45919454859-1/index.json) · [Индекс N18/N19 FIX1](/root/ch8-artifacts/run-45938919685/ch8-rev2-u64-n18-n19-Linux-X64-45938919685-1/index.json)

### Числовой порядок и кратности в половинах

N13 B01 swap и bit roles sort9 на B01/B10 закрепляют те же 25 пар адресов. Для порога `t`:

- `[min(x,y) ≥ t] = [x ≥ t] AND [y ≥ t]`;
- `[max(x,y) ≥ t] = [x ≥ t] OR [y ≥ t]`.

Поэтому min/max над полными u64 совпадают с битовым comparator на каждом пороге. Сохранение числа единиц `C(t)` на всех порогах сохраняет кратность значения `t` как `C(t)-C(t+1)` (для `u64::MAX` — `C(MAX)`). Скалярный frame swap сохраняет полные слова вне rel0..8. N18 использует B10 len9. N19 — B10 len10 и отдельный допуск точной вставки abs19. Вставка помещает tail за равными элементами и переносит его ровно один раз.

### Девять пар actual merge и возврат

На каждой из 9 итераций `smallsort.rs:1022` actual `merge_up` и `merge_down` сравнивают полные u64. Up выбирает левый источник при равенстве, down — правый. поэтому снимаются разные низкий и высокий ранги. Pair roots проверяют значения, точные read/write адреса, курсоры, раздельные записи и source frame. Ранговая индукция упорядочивает записи по `(полное значение, индекс после вставки)`. Перед парой k up уже снял k младших рангов, down снял k старших. Для непустой половины оба кандидата являются крайними доступными рангами. Для исчерпанной половины прямой кандидат уже взят сверху, обратный уже взят снизу. Валидность обоих адресов при k≤8 следует из размеров половин и локальных Check. Оба кандидата исчерпанной половины уступают оставшимся рангам из другой половины при соответствующих up/down сравнениях. Поэтому девять пар пишут ранги k и N−1−k в разные ячейки D. [Индукция опор](REV2-U64-N18-N19-HANDOFF.md#ранговая-индукция-до-записи-d)

Пусть `S` — начало активного среза, `(a,b)` — число up-чтений слева/справа, `(c,d)` — down-чтений слева/справа. После 9 пар actual forward cursors равны `(S+a, S+9+b)`, reverse cursors — `(S+8-c, S+N-1-d)`, их one-past ends — `(S+9-c, S+N-d)`. Для N18 эти множества рангов покрывают обе половины, поэтому `a+c=9` и `b+d=9`. Отсюда `S+a=S+9−c` и `S+9+b=S+18−d`. Для N19 один остаток даёт либо `9−a−c=1` и `10−b−d=0`, либо `9−a−c=0` и `10−b−d=1`. В первом случае `left<left_end`, odd center копирует `S+a` и инкрементирует left. Во втором center копирует `S+9+b` и инкрементирует right. В обоих случаях становятся равны обе пары указателей на `:1042`. При `c=9` адрес `S−1` возникает через wrapping. `wrapping_add(1)` приводит его к S.

| Трасса | После пар и cursor equality |
| --- | --- |
| N18, `0x201`: `(a,b,c,d)=(8,1,1,8)` | forward `(S+8,S+10)`. reverse `(S+7,S+9)`. ends `(S+8,S+10)`. Итак `left == left_end` и `right == right_end`. |
| N19, `0x3ffff`: `(8,1,0,9)` | до центра forward `(S+8,S+10)`, reverse `(S+8,S+9)`, ends `(S+9,S+10)`. Остаток слева: центр копирует `S+8`, затем forward `(S+9,S+10)` совпадает с обоими ends. |
| N19, `0x1ff`: `(0,9,9,0)` | до центра forward `(S,S+18)`, reverse `(S−1,S+18)`, ends `(S,S+19)`. `S−1` получается wrapping-арифметикой и используется как sentinel. Остаток справа: центр копирует `S+18`, затем forward `(S,S+19)` совпадает с ends. |

N18 полностью заполняет `D[0..18]`. N19 пары заполняют крайние 18 выходов, а odd center записывает единственный оставшийся ранг в `D[9]`. Все directional и center копии типизированы как копии одного элемента (`count=1`). Это условие для чтения всего результата. отдельный новый copy-back root всё ещё должен связать последнюю копию и frame.

## Три проверенные трассы расписания

Офлайн-сверка на Python воспроизвела буквальную сеть из 25 comparator calls (`:553–577`), строгие сдвиги `insert_tail` (`:701–735`) и фактический выбор источников/курсоров up/down (`:883–888`, `:916–921`, `:1014–1045`). На трёх входах совпали конечные маски, popcount, счётчики, источник центра и курсоры возврата.

| N / входная маска | После sort9 и вставки | Counts после пар `(a,b,c,d)` | Odd center и возврат | Результат |
| --- | --- | --- | --- | --- |
| 19 / `0x3ffff` | Левая сеть `[1×9]`. правая сеть видит `[1×9]`, tail `0`. Вставка `p=0` сдвигает девять слов rel17→18 … rel9→10. итог `[1×9,0,1×9]`. | `(8,1,0,9)` | Центр — левый `S+8`. возврат `(S+9,S+10)`. | Маска `0x7fffe`, popcount 18, `[0,1×18]`. При порче `v[1] ^= 1` получится `0x7ffff`. |
| 19 / `0x1ff` | Левая сеть `[1×9]`. правая сеть видит `[0×9]`, tail `0`. Вставка `p=9`, сдвигов нет. | `(0,9,9,0)` | Центр — правый `S+18`. возврат `(S,S+19)`. | Маска **`0x7fc00`**, popcount 9, `[0×10,1×9]`. Этот вход используется в cover positive N19. |
| 18 / `0x201` | Каждая сеть выдаёт `[0×8,1]`. вставки нет. | `(8,1,1,8)` | Центра нет. возврат `(S+8,S+10)`. | Маска `0x30000`, popcount 2, `[0×16,1,1]`. При порче `v[1] ^= 1` получится `0x30001`. |

## Runtime и unwind 36

| Runtime узел | Фактическая граница и unwind-поверхность |
| --- | --- |
| Регионы `smallsort.rs:394–417` | Две половины для N18/N19, по одному вызову sort9. |
| Сеть `:553–577` | 25 явно записанных `swap_if_less`. Rust-цикла нет. Условный swap копирует одно типизированное значение. |
| Вставка `:761–768`, `:718–734` | N18: после presort9 шагов хвоста нет. N19: один внешний tail-step. максимум 9 сдвигов `copy_nonoverlapping::<u64>(..., ..., 1)`. Последний gap-fill через `CopyOnDrop::drop`, `smallsort.rs:362:13`. Для `p=0` — девять сдвигов, для `p=9` — ни одного. |
| Merge `:1022–1025` | Ровно `len/2=9` итераций. Up и down делают по одной типизированной копии `count=1` за итерацию (`:885`, `:918`). N19 добавляет одну копию центра (`:1034`). |
| Cursor check и последняя копия | `:1042` проверяет оба конца. На пути успешного возврата последняя actual копия `:425` записывает 18×8 либо 19×8 байтов из scratch в активный срез. Точный consumer root отдельно связывает этот вызов и frame. |
| Выведенные свойства typed intrinsic | Для `ptr::copy_nonoverlapping::<u64>` требуются `.safety_check.1/.2`, `.arithmetic_overflow.1`, `.precondition_instance.1/.2/.3` на `core/src/ptr/mod.rs:587:14`. Исторические grouped sites: `smallsort.rs:885:9`, `:918:9`, odd wrapper `rev2_u64_n18_n19.rs:257:9`. `count=1`. Исторические pair/odd роли сообщают успех выведенных unwind checks при unwind36. Consumer task требует такой же typed group для copy-back. |
| Копии и сравнения | В handoff зафиксирована модель CBMC 6.11 typed memcpy через `array_copy` / `array_replace`. swap `ptr::copy` переносит одно значение. Новые проверки сравнивают скалярные u64, `memcmp` в них не используется. Это исключает ранее найденную N13 развёртку `memcmp` на 160 байтов для этих сравнений. |

## Copy-back и конечный frame

После сравнения обоих курсоров на `smallsort.rs:1042:9` merge возвращает полностью записанный префикс scratch. Вывод об инициализации этого префикса опирается на начальное состояние и точные write sets при `uninit=OFF`. Последний actual вызов на `smallsort.rs:425:9` копирует `len=N` из того же `stack_array` в `v_base`. После копии функция возвращается. Объекты `[u64;34]` и `MaybeUninit<[u64;32]>` живут раздельно, занимают 272 и 256 байтов, `size_of::<u64>()=align_of::<u64>()=8`.

| Длина | Последняя копия от scratch до V34, байты | Frame V34 | Локальный слот |
| --- | --- | --- | --- |
| N19 | `D[0..152)` → `V34[8..160)` | `v[0]`, `v[20..34]` | `U64-N19-COPY-BACK-FRAME` |
| N18 | `D[0..144)` → `V34[8..152)` | `v[0]`, `v[19..34]` | `U64-N18-COPY-BACK-FRAME` |

В каждом локальном корне независимый произвольный `[u64;N]` задаёт снимок значений префикса. Цикл `:107–110` записывает эти N слов в отдельный scratch32. Перед единственным typed copy `:115:14` цель берётся из точного активного среза произвольного V34. Посты поэлементно проверяют равенство назначения источнику, сохранность инициализированного префикса и внешний V34 frame. Байты scratch за N остаются вне чтений. В actual сети sort9 меняет только выбранные позиции каждой половины, вставка меняет только правую активную область, merge пишет в отдельный scratch, последняя копия пишет только в активный срез. Объединение write sets сохраняет внешний frame для обеих длин.

`actual_pairs.N19/N18` и `copy_back_frames.N19/N18` в отчёте начинают со статуса `OPEN`. Сквозная пара требует совпавших исходов positive и соответствующего контроля в лимитах. Для локальных копий действуют те же требования native, receipt, sampler, reap и attestation на их собственных слотах. Отсечка или выход за VT сохраняет измеренный исход и оставляет сквозную пару открытой. Составной допуск при отсечке разбирается отдельно после принятия конкретного контроля, локальной копии и рёбер половин, merge и фактического возврата. [Правило композиции](REV2-COMPOSITION-RULE.md)

## Циклы proof harness при unwind 36

| Цикл или скрытая операция | N18 | N19 | Верхняя граница |
| --- | ---: | ---: | --- |
| `check_actual_bits` :60, запись активных битов | 18 | 19 | 19 итераций, 20 проверок диапазона |
| `check_actual_bits` :79, внешний хвост frame | 15 | 14 | 15 итераций, 16 проверок диапазона. `v[0]` сравнивается отдельно |
| `check_actual_bits` :86, каноничность и маска | 18 | 19 | 19 итераций, 20 проверок диапазона |
| `check_copy_back` :107, запись префикса | 18 | 19 | 19 итераций, 20 проверок диапазона |
| `check_copy_back` :119, назначение и исходный префикс | 18 | 19 | 19 итераций, 20 проверок диапазона |
| `check_copy_back` :128, внешний хвост frame | 15 | 14 | 15 итераций, 16 проверок диапазона. `v[0]` сравнивается отдельно |
| Символьные `[u64;N]`, `[u64;34]` | 0 | 0 | В закреплённом Kani `Arbitrary<[T;N]>` вызывает `T::any_array`. Специализация `u64` в `library/kani_core/src/arbitrary.rs:33–45,68,125–132` идёт через `any_raw_array` и `AnyRawHook` в `src/lib.rs:533–546` |
| `count_ones` на u32 | 0 | 0 | `Ctpop` в stock Kani выдаёт CBMC `popcount`, без исходного цикла |
| Снимок V34, операции среза и указатели | 0 | 0 | Снимок копирует значение массива. RangeBounds проверяет границы. шаг итератора диапазона продвигает один индекс. Типизированные копии и scalar equality разобраны в таблице runtime |

Максимум явного цикла с терминальной проверкой составляет 20 для harness и 10 для runtime. Число итераций относится к отдельному циклу. Все сравнения данных используют отдельные `u64`, что исключает `memcmp` массивов/срезов, включая 144/152-байтовый активный префикс и 112/120-байтовый внешний хвост. Проверка сгенерированных unwind properties остаётся обязательной при нативном прогоне.

## Ubuntu job, argv и сроки

Один `ubuntu-24.04` job с таймаутом 100 мин. Stock CBMC 6.11.0/CaDiCaL, OB12, unwind36 из атрибутов корней. Включены memory safety, overflow, unwinding, undefined-function и assertion reach. Uninit и validity выключены. Вызовы Original с `--no-assert-contracts`, plain без stubs, Replace и loop contracts. Ранний compile preflight сохраняет версии и первые rustc diagnostics, затем discovery проверяет 110 исторических записей REV2 и шесть новых plain Proof. Сравнение cfg-off/on сохраняет весь прежний инвентарь с kind, selector, file и targets. У всех plain `not targets`.

```text
<tool>/scripts/kani verify-std
  -Z unstable-options -Z function-contracts -Z mem-predicates -Z float-lib
  -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing
  --no-assert-contracts --harness <exact-selector> --exact --jobs=1
  --output-format=regular -Z export-json --export-json <slot>/export.json
  --verbose --target-dir <slot>/kani-target <std>/library
  --cbmc-args --object-bits 12
```

Изолированные cold CWD, Cargo/Kani targets, tmp и export на слот. На измерение даётся до 120 с VT, 4 GiB group RSS и 180 с cold wall с резервом 2 GiB. Пишутся phase, VT, CNF, RSS группы и CBMC, PSS у пика либо ближайший измеренный. Sampled RSS относится к наблюдённым снимкам и может пропустить короткий пик при смене Linux TID. Projection cap 4 MiB, artifact cap 96 MiB. [Workflow](/root/kani-rev2-u64-n18-n19-consumer-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) · [Runner](/root/kani-rev2-u64-n18-n19-consumer-trigger-w15/control/ch8-cal1/run.py)

| Граница от epoch | Время | Ограничение |
| --- | ---: | --- |
| Prepare и exact discovery | 54:00 | Внешний timeout 56 мин |
| Measure gate | 55:00 | 60 с на gate |
| Конец шести окон | 75:30 | По 205 с, включая 180 с cold wall, 10 с reap, 5 с receipt, 10 с launch headroom |
| Финальная аттестация | 77:30 | 2 мин. measure внутри 23:35, снаружи 25 мин |
| Finish и upload admission | 82:25 | Абсолютная отсечка с резервом 5 с на запуск upload |
| Конец upload | 89:30 | Upload до 7 мин, затем проверка абсолютного времени |
| План с резервом | 95:30 | 6 мин резерва внутри таймаута job |

Процессный outcome и reap сохраняются атомарно до проекции. Receipt использует меньший из остатка окна и 5 с после возврата supervisor, включая последнюю секунду для записи. Bounded retry сохраняет исход отсечки и метку поздней записи. После отсечки следующий слот допускается в его окно при подтверждённом reap. Неполная проекция, потеря sampler или reap, поздний receipt и незавершённая аттестация оставляют роль открытой. Перед upload сверяются admission receipt, схема индекса, pin входов и инвентарь членов.

## Локальная валидация

- Pinned `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt` версии `1.12.0-nightly (65ce8611fe 2026-11-18)` с `--edition 2024 --config use_small_heuristics=Max` применён до freeze строк и столбцов. Сверены Rust visibility, check-cfg и `cfg(kani)`, побайтное восстановление исходных registry и manifest, отсутствие дельты runtime и контрактов. Прошли `rustfmt --check`, `git diff --check`, разбор YAML, `bash -n` всех run-блоков и синтаксис Python.
- Bare shallow Std-база depth 2 через локальный Git transport без alternates приняла bundle. Проверены единственный `HEAD`, 25 commit/tree/sole-parent, 26 source blobs, exact source и native coordinates. HEAD базы, refs и shallow boundary сохранились.
- Три офлайн-трассы проверили расписание 25 пар sort9, сдвиги, выбор центра, конечные курсоры и маски. Синтетика проверила отказ при неверной схеме индекса, чужом tree/payload, лишнем selector/target, потере typed copy, odd и return anchors, втором failure, cap/VT, late receipt, потере reap/attestation и поздней публикации.
- `test_supervisor.py` сохраняет Git blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Suite выполнен последовательно из exact review-trigger на обычной шкале и свежих шкалах 1, 5, 60 с.

| Шкала monotonic | Suite | Время |
| --- | ---: | ---: |
| Обычная | 130/130 | 37,655 с |
| Свежая со старта 1 с | 130/130 | 40,151 с |
| Свежая со старта 5 с | 130/130 | 39,771 с |
| Свежая со старта 60 с | 130/130 | 40,837 с |

Блок workflow `pins` с четырьмя suites занял 161,241 с из 480 с. На exact detached trigger и shallow clone depth 2 локально прошли `pins`, `finish`, `upload-gate` и `upload-check`. Сформированы шесть синтетических `NOT_STARTED` receipts. Обе подмены tree/payload отклонены `pins`, `sources`, `finish` и `upload-gate`. Нативная compile preflight и discovery остаются проверками будущего авторизованного run.

Локальные коммиты с `[skip ci]` записаны от `Tiramisu-Cake <igkharin@gmail.com>`. Новых запусков Cargo, rustc, Kani, CBMC или CI, push и изменений Actions variables в этой стадии не было.
