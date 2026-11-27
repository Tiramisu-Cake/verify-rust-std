# REV2 · полноширинные опоры сети u64 N26–N32

**`READY_FOR_REVIEW` · FIX1 · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.** Один локальный Ubuntu-пакет содержит восемь plain Proof для правых половин и десять exact Check для merge. R1 дал `GO_WITH_NITS` с исправлениями до запуска. Действующие пины в разделе FIX1. Нативный preflight, discovery и результаты N26–N32 входят в будущий прогон после отдельного GO и очереди координатора. [Ревью R1](REV2-U64-N26-N32-PROVIDERS-REVIEW.md#r1) · [Задание](REV2-U64-N26-N32-PROVIDERS-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## FIX1

| Роль и checkout | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Control FIX1](/root/kani-rev2-u64-n26-n32-providers-fix1-control-w13) · `work/rev2-u64-n26-n32-providers-fix1-control-w13` | `f50d86dffac4c1265797189511feaec8bba9d09b` | `dcccfc903bb1953d2184282c5fc1da5067e6f6bb` | `a068b3ac3b6d75b8897ff9af193ac09b0b02c5f3` |
| [Review-trigger FIX1](/root/kani-rev2-u64-n26-n32-providers-fix1-trigger-w13/control) · detached | `68aa2e4b93417e5383a50fb412edc2bfd9970bc5` | `dcccfc903bb1953d2184282c5fc1da5067e6f6bb` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Tree pin `CH8_REV2_U64_N26_N32_PROVIDERS_TRIGGER_TREE` для FIX1 — `dcccfc903bb1953d2184282c5fc1da5067e6f6bb`. Std `72bb79d26dd495d0461c6e6d3c05d21c2d1b1878` / tree `c513d0ec1a137457add28b2b9ee9c47ac23642d3`. Профиль, часы, exact selectors и Check targets приведены ниже.

| Вход FIX1 | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n26-n32-providers-fix1-trigger-w13/control/ch8-cal1/CI-REQUEST.json) | `3d97d7898abc2e77cbeb9f5431672aa2b361f6e90cef65b1ca2d74f643699043` |
| Exact roster, канонический JSON | `5b12d12a4d8c131a1477c2e083444473fba248bae26ecc4aa38e0d153ddf0ae3` |
| Source bindings, канонический JSON | `9fd4a201951ab0fd799474fe935e20300fac5478d78c2b52ad67d03e1ff71b95` |
| [Std bundle](/root/kani-rev2-u64-n26-n32-providers-fix1-trigger-w13/control/ch8-cal1/std-overlay.bundle), 74 875 байт | `d9b308422fdb10153ea07b4a953b46467edccca5b2b208e8ee1799412919a38f` |
| [Workflow](/root/kani-rev2-u64-n26-n32-providers-fix1-trigger-w13/control/.github/workflows/ch8-q-pilot.yml) | `ed86dbb9298fb5daa35b3896ec24683f026c5fc32aae0eadfc865f0b9ad98029` |

- У Check N27/N29/N31 `copy_sites` указывает вызовы в `rev2_u64_n26_n32_providers.rs` на `1018:9`, `1104:9`, `1190:9` соответственно. `transcribes` хранит координату actual `smallsort.rs:1034:13` как ссылку на исходник транскрипции. Source gate сверяет локальный вызов в теле exact цели. Синтетические receipts, записанные штатным путём, сохраняют эту структуру в `checked_write_set` и относят нативные свойства к проверяемой обёртке и typed copy.
- Восстановлен gate layout от `b09c6f22bfbd1ce8eb6afccf96df6b9a2ad3c54b` до `a1335f8e11960150afda1d00d60c72b4362e3cec`. Четыре swap-слота описывают один `swap_if_less` на точном срезе с `0≤a<b<13` и скалярным frame остальных 32 слов. Удалена неиспользуемая `target_name`. В тестах смещённого поста и чужой специализации восстановлено точное ожидание `MISMATCHED`.
- Прошли 131/131 Python-тестов в штатном режиме и на свежих монотонных шкалах 1/5/60 с, последовательно. Source gate отклонил подмену локальной координаты на actual, сдвинутую строку и неверное `transcribes`. Повторно сверены layout, нативные координаты, 131 историческая запись discovery и 18 синтетических добавлений. Blob `ch8-cal1/test_supervisor.py` — `df63a457c3adf648d360f3d559d5d40ef00a9427`.
- Shallow checkout глубины 2 принял bundle. YAML, восемь `bash -n`, `git diff --check` и локальный trigger gate прошли. Неверные tree, SHA, attempt и payload отклонены. Upload gate сверил пины и инвентарь и отклонил изменённый receipt. Локальные Control и review-trigger содержат `[skip ci]`.

## Форма пары и предыдущий прогон

В `45967622962/1` получены 13/13 `VERIFIED/MATCHED` и аттестация `COMPLETE`. При m=11/12 четыре PAIR Check заняли 55,189–61,381 с VT и 91,246–97,855 с cold wall. Пик CBMC до 923 888 KiB, первая CNF около 379 тыс. переменных и 2,46 млн дизъюнктов. S13 B13 L13 bits занял 47,782 с VT при 2 576 460 KiB группового RSS. SHA-256 индекса `ee6471da3ec55c4aad35f38d0757c4c92b5934ba89405f11feddf6ee1c42d05b`. [Сводка](/root/ch8-artifacts/run-45967622962/ch8-rev2-u64-n22-n25-providers-Linux-X64-45967622962-1/SUMMARY.md) · [Сверка входов](REV2-U64-N22-N25-CONSUMER-HANDOFF.md#нативные-опоры-из-459676229621)

У m=13–16 сохранена одна exact пара с символьными `k,a,c` и литеральными N/m. Сначала измеряются m=16, обе m=15 и S13 B17. При угрозе cold wall или другой отсечке сопоставить конечную фазу, первую CNF и расход времени и памяти. Первое разбиение — отдельные up с `k,a` и down с `k,c`. У обоих остаются actual тело, полноширинный компаратор, курсоры и tie, общий неизменный источник и собственная ячейка D. Символьная адресация формирует основную CNF и при ограничении диапазона k сохраняется. Разбиение требует новой заморозки, расписания и независимого ревью. [R1 по прежней форме](REV2-U64-N22-N25-PROVIDERS-REVIEW.md#r1)

## Замороженные входы R1

| Роль и checkout | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n26-n32-providers-w13) · `work/rev2-u64-n26-n32-providers-std-w13` | `72bb79d26dd495d0461c6e6d3c05d21c2d1b1878` | `c513d0ec1a137457add28b2b9ee9c47ac23642d3` | `a1335f8e11960150afda1d00d60c72b4362e3cec` |
| [Control](/root/kani-rev2-u64-n26-n32-control-w13) · `work/rev2-u64-n26-n32-providers-control-w13` | `a068b3ac3b6d75b8897ff9af193ac09b0b02c5f3` | `1f91e3aa4cfa3cdced3d97944214b018cda3772d` | `9e95965f30f40a4dea9532bd04330b0d68537769` |
| [Review-trigger](/root/kani-rev2-u64-n26-n32-trigger-w13/control) · detached | `0bb712a1ea3058809fb24fdcfac944fb187d7b72` | `1f91e3aa4cfa3cdced3d97944214b018cda3772d` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Задание закреплено на g0 `bd6bf381a6e0c7df9abe07ee3944da1db9346349`. Деревья баз Std и Control N22–N25 — `a04025df1dddb1668c12219307c943a23ee9382a` и `6b9a8245426143527186a7095e8fbf5623578527`. Bundle объявляет один `HEAD` и 27 последовательных overlay-коммитов поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`.

Значение tree pin `CH8_REV2_U64_N26_N32_PROVIDERS_TRIGGER_TREE` для снимка R1 — `1f91e3aa4cfa3cdced3d97944214b018cda3772d`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n26-n32-trigger-w13/control/ch8-cal1/CI-REQUEST.json) | `fcf327b2332b3f9f66a256168f6613a42b241f827d8281c71656d70ca4e0b6cc` |
| Exact roster, канонический JSON | `69ac41f4fa18fa5eb75f92f863de26daee4be5a71e9fc1183d534e28f5328f66` |
| Source bindings, канонический JSON | `91004524019983307f2a8571fbef9454a2778900e4d9dee43a716bcd3711a309` |
| [Std bundle](/root/kani-rev2-u64-n26-n32-trigger-w13/control/ch8-cal1/std-overlay.bundle), 74 875 байт | `d9b308422fdb10153ea07b4a953b46467edccca5b2b208e8ee1799412919a38f` |
| [Workflow](/root/kani-rev2-u64-n26-n32-trigger-w13/control/.github/workflows/ch8-q-pilot.yml) | `ed86dbb9298fb5daa35b3896ec24683f026c5fc32aae0eadfc865f0b9ad98029` |

| Std blob | Git object |
| --- | --- |
| `library/core/Cargo.toml` | `8bda60979d86d7e8f647ed5ca88a07d4bfe5c6c6` |
| `core/src/slice/sort/shared/smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `smallsort/verify.rs` | `c20481383c42c8e28d3211aa880db4807cd1718c` |
| `verify/rev2_u64_n26_n32_providers.rs` | `63ae781c61900737b33f6c5f17a2a45a2e6d767d` |
| `verify/rev2_u64_n13.rs` | `47c129a11d6cd0d0adce0be450b91eca84a25c0c` |
| `verify/rev2_u64_n22_n25_providers.rs` | `e5b3d622a4d2b873df49368cb1e49e060d6a85f5` |

В `cfg(kani)` новый модуль требует `kani_smallsort_rev2_u64_n26_n32_providers` и cfg модуля `kani_smallsort_rev2_u64_n13`, откуда берётся прежний `pub(super) u64_less`. Побайтно сверены actual runtime, контракты и существующие модули. Вычитание новой строки check-cfg и двух строк регистрации восстанавливает оба прежних blobs. [Модуль](/root/verify-rust-std-rev2-u64-n26-n32-providers-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n26_n32_providers.rs)

## Exact roster и нативные якоря

Префикс exact selectors и Check targets `slice::sort::shared::smallsort::verify::rev2_u64_n26_n32_providers::`. Все строки ожидают `VERIFIED`, exit 0, `MATCHED`, достижение всех covers и `copy_back=false`. К 131 исторической записи cfg-on добавляет восемь plain Proof с пустыми targets и десять ProofForContract с единственной точной целью. Колонка Root указывает атрибут proof, колонка Check — атрибут цели и строку `modifies`. Проверка stock сравнивает `target_fn` с суффиксом цели из таблицы, discovery связывает полное имя цели и source file.

| Слот | Суффикс selector, Root | Check target, attr / modifies | Посты / covers | Latest start |
| --- | --- | --- | ---: | --- |
| `U64-N32-PAIR-STEP` | `u64_n32_pair_step`, 935:1 | `actual_pair_step_n32`, 888:1 / 894:5 | 8 / 10 | 55:00 |
| `U64-N31-PAIR-STEP` | `u64_n31_pair_step`, 832:1 | `actual_pair_step_n31`, 785:1 / 791:5 | 8 / 10 | 58:25 |
| `U64-N30-PAIR-STEP` | `u64_n30_pair_step`, 729:1 | `actual_pair_step_n30`, 682:1 / 688:5 | 8 / 10 | 61:50 |
| `U64-S13-B17-L16-BITS` | `u64_s13_b17_l16_bits`, 200:1 | Plain Proof | 3 / 4 | 65:15 |
| `U64-S13-B17-SWAP` | `u64_s13_b17_swap`, 233:1 | Plain Proof | 3 / 5 | 68:40 |
| `U64-N29-PAIR-STEP` | `u64_n29_pair_step`, 626:1 | `actual_pair_step_n29`, 579:1 / 585:5 | 8 / 10 | 72:05 |
| `U64-N28-PAIR-STEP` | `u64_n28_pair_step`, 523:1 | `actual_pair_step_n28`, 476:1 / 482:5 | 8 / 10 | 75:30 |
| `U64-N27-PAIR-STEP` | `u64_n27_pair_step`, 420:1 | `actual_pair_step_n27`, 373:1 / 379:5 | 8 / 10 | 78:55 |
| `U64-N26-PAIR-STEP` | `u64_n26_pair_step`, 317:1 | `actual_pair_step_n26`, 270:1 / 276:5 | 8 / 10 | 82:20 |
| `U64-N31-ODD-CENTER` | `u64_n31_odd_center`, 1197:1 | `actual_odd_center_n31`, 1163:1 / 1169:5 | 8 / 4 | 85:45 |
| `U64-N29-ODD-CENTER` | `u64_n29_odd_center`, 1111:1 | `actual_odd_center_n29`, 1077:1 / 1083:5 | 8 / 4 | 89:10 |
| `U64-N27-ODD-CENTER` | `u64_n27_odd_center`, 1025:1 | `actual_odd_center_n27`, 991:1 / 997:5 | 8 / 4 | 92:35 |
| `U64-S13-B16-L16-BITS` | `u64_s13_b16_l16_bits`, 138:1 | Plain Proof | 3 / 4 | 96:00 |
| `U64-S13-B16-SWAP` | `u64_s13_b16_swap`, 171:1 | Plain Proof | 3 / 5 | 99:25 |
| `U64-S13-B15-L15-BITS` | `u64_s13_b15_l15_bits`, 76:1 | Plain Proof | 3 / 4 | 102:50 |
| `U64-S13-B15-SWAP` | `u64_s13_b15_swap`, 109:1 | Plain Proof | 3 / 5 | 106:15 |
| `U64-S13-B14-L14-BITS` | `u64_s13_b14_l14_bits`, 14:1 | Plain Proof | 3 / 4 | 109:40 |
| `U64-S13-B14-SWAP` | `u64_s13_b14_swap`, 47:1 | Plain Proof | 3 / 5 | 113:05 |

У pair курсоры up/down проверяет Check closure. В столбце постов по порядку идут read, write, disjoint, up value, down value, frame. Порядок covers — up left/right, down left/right, up/down tie, k first/last, return.

| N | Курсоры up/down | Посты harness | Covers harness |
| --- | --- | --- | --- |
| N26 | 298:9 308:9 | 326:5 330:5 334:5 359:5 360:5 361:5 | 362:5 363:5 364:5 365:5 366:5 367:5 368:5 369:5 370:5 |
| N27 | 401:9 411:9 | 429:5 433:5 437:5 462:5 463:5 464:5 | 465:5 466:5 467:5 468:5 469:5 470:5 471:5 472:5 473:5 |
| N28 | 504:9 514:9 | 532:5 536:5 540:5 565:5 566:5 567:5 | 568:5 569:5 570:5 571:5 572:5 573:5 574:5 575:5 576:5 |
| N29 | 607:9 617:9 | 635:5 639:5 643:5 668:5 669:5 670:5 | 671:5 672:5 673:5 674:5 675:5 676:5 677:5 678:5 679:5 |
| N30 | 710:9 720:9 | 738:5 742:5 746:5 771:5 772:5 773:5 | 774:5 775:5 776:5 777:5 778:5 779:5 780:5 781:5 782:5 |
| N31 | 813:9 823:9 | 841:5 845:5 849:5 874:5 875:5 876:5 | 877:5 878:5 879:5 880:5 881:5 882:5 883:5 884:5 885:5 |
| N32 | 916:9 926:9 | 944:5 948:5 952:5 977:5 978:5 979:5 | 980:5 981:5 982:5 983:5 984:5 985:5 986:5 987:5 988:5 |

Посты центра идут в порядке read, write, disjoint, selected source, value, left end, right end, frame. Порядок covers — левый, правый, sentinel, return.

| N | Call site копии | Посты | Covers |
| --- | --- | --- | --- |
| N27 | 1018:9 | 1034:5 1038:5 1042:5 1060:5 1061:5 1062:5 1066:5 1070:5 | 1071:5 1072:5 1073:5 1074:5 |
| N29 | 1104:9 | 1120:5 1124:5 1128:5 1146:5 1147:5 1148:5 1152:5 1156:5 | 1157:5 1158:5 1159:5 1160:5 |
| N31 | 1190:9 | 1206:5 1210:5 1214:5 1232:5 1233:5 1234:5 1238:5 1242:5 | 1243:5 1244:5 1245:5 1246:5 |

У bits посты canonical, sorted popcount, frame и covers mixed, inversion, return. У swap посты min, max, frame и covers greater, less, equal, return.

| База и роль | Посты | Covers |
| --- | --- | --- |
| B14 swap | 66:5 67:5 72:5 | 57:5 58:5 59:5 73:5 |
| B14 bits | 37:5 38:5 43:5 | 25:5 26:5 44:5 |
| B15 swap | 128:5 129:5 134:5 | 119:5 120:5 121:5 135:5 |
| B15 bits | 99:5 100:5 105:5 | 87:5 88:5 106:5 |
| B16 swap | 190:5 191:5 196:5 | 181:5 182:5 183:5 197:5 |
| B16 bits | 161:5 162:5 167:5 | 149:5 150:5 168:5 |
| B17 swap | 252:5 253:5 258:5 | 243:5 244:5 245:5 259:5 |
| B17 bits | 223:5 224:5 229:5 | 211:5 212:5 230:5 |

`REV2_U64_N13_COMPARATOR_CALLED` на `rev2_u64_n13.rs:9:5` принадлежит `rev2_u64_n13::u64_less` и обязателен для pair, bits и swap. У pair два поста курсоров относятся к closure собственной Check-цели. Обязательны exact stock `target_fn`, `single_top_level_call`, `no_recursive_call` на атрибуте, scoped `memcpy.assigns.1/.2` на builtin 46/47 и шесть успешных групп `ptr::copy_nonoverlapping::<u64>` на `ptr/mod.rs:587:14`. Pair вызывает actual копии `smallsort.rs:885:9` и `:918:9`. У центра собственный site в таблице воспроизводит `:1034:13`.

У восьми bits/swap ожидаются пять успешных групп `ptr::copy::<u64>` на `ptr/mod.rs:682:9` и шесть `ptr::copy_nonoverlapping::<u64>` на `:587:14`, связанные с actual `smallsort.rs:517:9` и `:518:9`. Первая копия допускает совпадение ячеек. Вторая переносит слово из отдельного tmp. Для всех корней требуются `SUCCESS` всех выведенных unwind и stock unwinding ON. Exact function, source location, status и return cover связывают grouped свойства с исполнениями. [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

## Переиспользуемые нативные опоры

У пяти строк `VERIFIED/MATCHED`, exit 0, полные проекции и covers, своевременные receipts, подтверждённые sampler/reap и итоговая аттестация `COMPLETE`. Сверены размеры и SHA-256 receipt/projection по опубликованным bounded индексам. Префикс исторических selectors `slice::sort::shared::smallsort::verify::`.

| Run/attempt · слот | Selector и посты | Covers | SHA-256 receipt / projection |
| --- | --- | ---: | --- |
| `45919454859/1` · `U64-N13-SWAP` | `rev2_u64_n13::u64_n13_swap`, attr 13:1, fn 15:1, 35:5, 36:5, 42:5 | 5/5 | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| `45919454859/1` · `U64-N13-S13-BITS` | `rev2_u64_n13::u64_n13_s13_bits`, attr 45:1, fn 47:1, `check_s13::<false>` 79:5, 86:5, 87:5 | 4/4 | `c3ca8085ba45dc01aed62164c46e46ca7d307b3c5544a150c5b72ce63f5bf560` / `9eca670c5f5854ff679a613e2c374df929c0a86e4dd9d5fbcbe05155958d1da5` |
| `45933888115/1` · `U64-INSERT-REL13` | `rev2_u64_n14_n17_fix1::u64_insert_rel13`, attr 13:1, fn 15:1, `check_insert::<13>` 69:5, 75:5 | 6/6 | `fecb9cbd6806997e1fe122a1ae744b507b5739e6441e142c5c4d6bea3b002099` / `eb991572a24721ec4fc05312872ceeeca3ea5080c2ff684f1340b7cac86f3db8` |
| `45933888115/1` · `U64-INSERT-REL14` | `rev2_u64_n14_n17_fix1::u64_insert_rel14`, attr 19:1, fn 21:1, `check_insert::<14>` 69:5, 75:5 | 6/6 | `edf1a43b5daba77d9d3ebd1066041ca5112f5cedb7333cbbee935b19afac9100` / `53bf38c78c2314fb11a7429f30b6286b489e00759a8f0033c947ccd5e5ff4a5c` |
| `45933888115/1` · `U64-INSERT-REL15` | `rev2_u64_n14_n17_fix1::u64_insert_rel15`, attr 25:1, fn 27:1, `check_insert::<15>` 69:5, 75:5 | 6/6 | `e123a1f34f425a157eb977801e43781417fca28f37b60bd7bc3c0d701c314933` / `4148c468785e207f323bbe0e3778c2bb369a4a4f98e922116c5737cb6ecfc552` |

| Run | Index SHA-256 | Std commit / tree | Trigger commit / tree |
| --- | --- | --- | --- |
| `45919454859/1` | `6d7e603aa2fe26dd62c0f41725d664bf726be89836c16c35efbe641f3a0661f9` | `4d6dd509956dff820a596ff1af9c0aae347aca26` / `b0dc6d628690b7bc58225e2f60503ed4f8ae32b3` | `8ac984fb143be092d88b69dca47cf97bd149e239` / `71b1cbd433b47a9ccc6a26ef33aa1f8e2c6c9a7b` |
| `45933888115/1` | `50ba454bc3106f76ea6cb83717280fb6f13cb4c5d6b67ad6d41bdfa3a0ea14e3` | `fe8444d175ec1630155b886d54ce527ebbb6c415` / `fe97d2dd54b5c1ec27479b6332e0285bfe267588` | `0477f73bae6ce2b09c6520aa6ebf9a12423173b5` / `b4bf21f6578d30d40f66fd296af4258b6b0bc390` |

Исторические triggers имеют sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, профиль stock Kani и прежний `proof_credit=NONE`. Actual `smallsort.rs` и `ptr/mod.rs` совпадают с обоими Std. N13 blob `6658b28d64647aa6e11c5bee3c71a135f09b2a6c` отличается от текущего только видимостью `pub(super)` у `u64_less`. FIX1 использует текущий blob компаратора и свой исторический harness blob `6ef2b2b503347f2e31532bdd2e79d7e82bb02ffe`. Его три мономорфизации переиспользуются через закреплённые receipts на actual `insert_tail`. [N13 и индексы](REV2-U64-N13-ADMISSION.md#нативная-сверка) · [FIX1 и индексы](REV2-U64-N14-N17-ADMISSION.md#сверка-обоих-прогонов)

## Геометрии и внешние рёбра половин

Вход — живая инициализированная `V=[u64;34]`, активный `v[1..1+N]`, `S=&v[1]`, отдельная живая `MaybeUninit<[u64;32]>` на 256 байт с базой D. Размер слова и выравнивание по 8 байт на Ubuntu X64. `smallsort.rs:395–416` выбирает actual S13 на обеих половинах и вызывает `insertion_sort_shift_left` с offset 13.

| N, m | Левая половина и вставки B01 | Правая половина и вставки | Merge |
| --- | --- | --- | --- |
| 26, 13 | `v[1..14]`, N13 exact, ∅ | `v[14..27]`, B14 L14→L13, ∅ | 13 пар |
| 27, 13 | `v[1..14]`, N13 exact, ∅ | `v[14..28]`, B14 L14, rel13 | 13 пар и D[13] |
| 28, 14 | `v[1..15]`, N13 L13→L14, rel13 | `v[15..29]`, B15 L15→L14, rel13 | 14 пар |
| 29, 14 | `v[1..15]`, N13 L13→L14, rel13 | `v[15..30]`, B15 L15, rel13→14 | 14 пар и D[14] |
| 30, 15 | `v[1..16]`, N13 L13→L15, rel13→14 | `v[16..31]`, B16 L16→L15, rel13→14 | 15 пар |
| 31, 15 | `v[1..16]`, N13 L13→L15, rel13→14 | `v[16..32]`, B16 L16, rel13→14→15 | 15 пар и D[15] |
| 32, 16 | `v[1..17]`, N13 L13→L16, rel13→14→15 | `v[17..33]`, B17 L16, rel13→14→15 | 16 пар |

У B01 используются два N13 receipts. На каждой правой базе собственные bits и swap входят в замороженный roster нативных опор. Внешние переносы длины B01 13→14/15/16 и B14 14→13, B15 15→14, B16 16→15 сохраняют B, guard `len≥13`, расписание и frame. Для каждого из B=1,14,15,16,17 соответствующая пара `i-j` на `smallsort.rs:612–656` читает и пишет слова `v[B+i]`, `v[B+j]` с адресами `8(B+i)`, `8(B+j)` от базы V. Фактический порядок 45 вызовов:

```text
0-12 1-10 2-9 3-7 5-11 6-8 1-6 2-3 4-11 7-9 8-10 0-4 1-2 3-6 7-8
9-10 11-12 4-6 5-9 8-11 10-12 0-5 3-8 4-7 6-11 9-10 0-1 2-5 6-9 7-8
10-11 1-3 2-4 5-6 9-10 1-2 3-4 5-7 6-8 2-3 4-5 6-7 8-9 3-4 5-6
```

Bits оставляет 21 произвольное слово во frame, включая хвост среза, и проверяет все 8192 битовых комбинации префикса. Полноширинный swap проверяет min/max и frame остальных 32 слов при `0≤a<b<13`. Для любого порога `t:u64` отображение `word>t` переводит scalar min/max в AND/OR. Каждый шаг actual расписания коммутирует с этим отображением. Если в полном выходе есть инверсия `x>y`, порог `t=y` дал бы битовую инверсию. Каждый обмен сохраняет мультимножество двух слов и остальные ячейки, поэтому вся последовательность сохраняет полные кратности. Это внешнее ребро от bits и swap к полноширинному отсортированному префиксу. [Пороговый перенос N13](REV2-U64-N13-ADMISSION.md#перенос-на-полные-u64-и-фактический-маршрут)

Литеральные B01/R опоры применяются на левой половине в порядке таблицы. R1 принял следующие девять адресных переносов для правых половин при отсортированном префиксе, инициализированном tail и 8-байтовом выравнивании. Максимальный регион B17/R15 — `v[17..33]`. Нативные предпосылки новых половин и составной допуск остаются открыты. Интервалы в таблице включают обе границы. [Ревью R1](REV2-U64-N26-N32-PROVIDERS-REVIEW.md#r1)

| Ребро | Сдвиг | Исходные индексы V → целевые | Зависимые N | Ревью исходников |
| --- | ---: | --- | --- | --- |
| B01 rel13 → B14 rel13 | 104 B | 1…14 → 14…27 | 27 | Условно принято |
| B01 rel13 → B15 rel13 | 112 B | 1…14 → 15…28 | 28, 29 | Условно принято |
| B01 rel14 → B15 rel14 | 112 B | 1…15 → 15…29 | 29 | Условно принято |
| B01 rel13 → B16 rel13 | 120 B | 1…14 → 16…29 | 30, 31 | Условно принято |
| B01 rel14 → B16 rel14 | 120 B | 1…15 → 16…30 | 30, 31 | Условно принято |
| B01 rel15 → B16 rel15 | 120 B | 1…16 → 16…31 | 31 | Условно принято |
| B01 rel13 → B17 rel13 | 128 B | 1…14 → 17…30 | 32 | Условно принято |
| B01 rel14 → B17 rel14 | 128 B | 1…15 → 17…31 | 32 | Условно принято |
| B01 rel15 → B17 rel15 | 128 B | 1…16 → 17…32 | 32 | Условно принято |

Для каждого ребра `1+j ↔ B+j` при `0≤j≤R` сопоставляет две инстанциации геометрии V34. Все адреса лежат в соответствующей живой половине и сохраняют выравнивание. Перед шагом префикс rel0…R−1 упорядочен, x=tail произволен, p равно числу слов префикса `≤x`. Actual `insert_tail` на `:701–735` начинает с `sift=tail−1` и сравнивает x с тем же логическим предшественником через полный `u64_less`. При раннем возврате сохраняется весь регион. В цикле `:722` переносится одно слово из `B+j` в соседний gap `B+j+1`, у которых непересекающиеся 8-байтовые области. Guard `sift==begin` на `:725` сохраняет свою истинность при j=0 и ограничивает decrement. Отдельный `tmp` на `:715` и `CopyOnDrop<u64>` на `:362` заполняют последний gap из непересекающегося источника. Строгий компаратор завершает сдвиг после равных. Пост даёт прежнее слово rel j при j<p, x при j=p и прежнее слово rel j−1 при j>p. Вне rel0…R слова сохраняются. Значит следующий шаг получает отсортированный префикс и прежний tail.

Точный driver `:742–769` начинает с `tail=B+13`, последовательно выполняет литералы до `B+L−1` и останавливается при `tail==end=B+L`. При L13 равенство выполняется сразу. R1 providers u64 N22–N25 дал GO_WITH_NITS и выделил B12/B13 rel9–11 как внешние рёбра. Независимое R1 consumer w15 приняло все шесть переносов, включая rel11, где опорой были B01 rel11 и сдвиг адресов. Каждое новое B/R использует такой же сдвиг от собственной литеральной B01 опоры. R2 для u8 N26–N31 отдельно приняло структурный перенос B17→B14/B15/B16. Если на ревью композиции возникнет возражение к конкретному ребру, его B/R из таблицы задаёт отдельный малый пакет, а зависимые длины остаются открыты. [Providers R1](REV2-U64-N22-N25-PROVIDERS-REVIEW.md#r1) · [Consumer R1 w15](REV2-U64-N22-N25-CONSUMER-REVIEW.md#r1) · [Аналог u8](REV2-N26-N31-HALVES-REVIEW.md)

## Пары, центр и внешний вывод о заполнении scratch

Инициализация курсоров actual `:1014–1020` даёт `(S,S+m,D)` для up и `(S+m−1,S+N−1,D+N−1)` для down. При `0≤k<m` и `0≤a,c≤k` положим `b=k−a`, `d=k−c`. Up читает `S+a`, `S+m+b` и пишет `D[k]`. У выбранного источника курсор двигается на +1. Down читает `S+m−1−c`, `S+N−1−d` и пишет `D[N−1−k]`. У выбранного источника курсор двигается на wrapping −1. Up берёт min с приоритетом левой стороны при равных, down берёт max с приоритетом правой. Следующие D-курсоры — `D+k+1` и `D+N−2−k`. Обе scoped записи относятся к отдельной scratch, разрыв индексов `N−1−2k` не меньше 1 на чётных и 2 на нечётных N. Все четыре читаемых слова инициализированы, находятся в своих половинах и остаются неизменны. Следующие forward курсоры лежат в `S+[0,m]`, `S+[m,N]`, reverse — в `S+[−1,m−1]`, `S+[m−1,N−1]` с включёнными концами. Sentinel `S−1` возникает в расчёте следующего курсора и в конце, чтения проходят внутри половин.

| N | Состояния пары | Пишутся половины D | Центр и состояния |
| --- | ---: | --- | --- |
| 26 | 819 | `[0,13)`, `[13,26)` | ∅ |
| 27 | 819 | `[0,13)`, `[14,27)` | D[13], 27 |
| 28 | 1015 | `[0,14)`, `[14,28)` | ∅ |
| 29 | 1015 | `[0,14)`, `[15,29)` | D[14], 29 |
| 30 | 1240 | `[0,15)`, `[15,30)` | ∅ |
| 31 | 1240 | `[0,15)`, `[16,31)` | D[15], 31 |
| 32 | 1496 | `[0,16)`, `[16,32)` | ∅ |

После вставок отсортированные половины — два возрастающих потока по ключу `(значение, индекс в S после вставок)`. Forward независимо выбирает первые k рангов, reverse — последние k. До начала пары каждый обход потребил только k<m слов, так что оба кандидата этого обхода существуют. Порядок вызовов `:1023–1024` сохраняет источник и выбирает разные ранги k и N−1−k. Кандидат одного обхода может быть ранее просмотрен или потреблён другим. При чётном N после m пар из каждого потока потреблены все ранги, поэтому `a+c=b+d=m`. Тогда `left=S+a=left_rev.wrapping_add(1)` и `right=S+m+b=right_rev.wrapping_add(1)`, то есть обе проверки `:1042` проходят.

При нечётном N после m пар имеем `a+b=c+d=m`. Если остался левый, `a=0…m−1`, `(b,c,d)=(m−a,m−1−a,1+a)`. Если правый, `a=0…m`, `(b,c,d)=(m−a,m−a,a)`. Это все `2m+1` состояния. В одноклеточном Check `left_end=left_rev.wrapping_add(1)` и `right_end=right_rev.wrapping_add(1)` отражают `:1027–1028`. Сравнение `left<left_end` выбирает левый тогда и только тогда, когда там один остаток. Копируется полное слово из `S+a` или `S+2m−a` в D[m], то есть ранг m. При c=m, a=0 левый reverse sentinel переходит в S без чтения. Посты фиксируют адрес источника, слово, оба курсора на своих ends и V34 frame. В чётном и нечётном случае `D[0..N]` заполнен ровно один раз до чтения на `:425`. При uninit OFF это внешний вывод из последовательности записей, с нативными предпосылками из будущего прогона. Copy-back/frame и контроль фактической сети на каждой длине составляют будущий consumer-пакет.

## Ubuntu job и границы

Одна job `ubuntu-24.04` X64, 140 мин. Stock Kani и CBMC 6.11.0/CaDiCaL, OB12, unwind36. Включены safety, overflow, unwinding, undefined-function, assertion-reach. Uninit и validity OFF. Actual тела Original, десять exact обёрток Check, без stubs, Replace и loop contracts. Каждый корень получает отдельные холодные CWD, Cargo/Kani targets, tmp и export. `KANI_JOBS=1`, 25 cfg в порядке roster, opt-in пакета последний. Профиль на корень 120 с VT, 180 с cold wall, 4 GiB группового RSS с резервом 2 GiB для ОС. Linux sampler может недоучитывать память при смене TID.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

| Этап | Абсолютная граница от старта job | Внешнее окно |
| --- | --- | --- |
| Prepare, ранний compile preflight и оба discovery list | 54:00 | 56 мин |
| Identity gate | 55:00 | внутри measure |
| 18 слотов по 205 с | 116:30 | measure 66 мин, внутреннее 64:35 |
| Аттестация | 118:30 | внутри measure |
| Finish и upload-gate | 123:25 | до запуска зарезервированного upload |
| Завершение upload | 130:30 | 7 мин |
| План с резервом 6 мин | 136:30 | job 140 мин |

У каждого слота 180 с cold wall, 10 с reap, 5 с receipt и 10 с запаса на запуск. Prepare сохраняет первые ошибки rustc из preflight до cfg-off/on list. Исход и факт reap атомарно сохраняются до проекции. Неподтверждённый reap блокирует следующие слоты. Сохраняются bounded retry, 4 MiB на projection и 96 MiB на артефакт. Диагноз `U64_N26_N32_PROVIDERS_WITHIN_PROFILE` требует 18 `VERIFIED/MATCHED`, все ожидаемые covers, полные проекции, своевременные receipts, валидный sampler, подтверждённый reap и аттестацию `COMPLETE`. Индекс и сводка связывают фазу, первую CNF, VT, cold wall, RSS группы/CBMC и доступную PSS с каждым слотом. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)

Для `pins`, `sources`, `finish` и `upload-gate` независимая переменная `CH8_REV2_U64_N26_N32_PROVIDERS_TRIGGER_TREE` задаёт дерево Control. Identity требует `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, чистый detached HEAD, тот же `GITHUB_SHA` и payload `after`, sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Перед upload сверяются admission receipt, индекс и хэши. После ревью очередь и изменения переменной остаются у координатора.

## Офлайн-валидация R1

- Закреплённый `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max` выполнен до заморозки координат, затем пройден `--check`. Сверены TOML, видимость Rust-имён, cfg, 18 proof attributes, source blobs и побайтная Std-дельта из трёх файлов.
- Bits setup и сбор поста по 13 итераций. Frame bits, swap и source по 34 итерации, с запасом на завершающую проверку при unwind36. `count_ones` имеет ширину 16, range/contains скалярны, snapshots фиксированы на 272 байтах. Массивы сравниваются пословно. В stock `library/kani_core/src/arbitrary.rs:31–68,125–131` `[u64;34]` использует `u64::any_array` через `any_raw_array`. Actual S13 — 45 прямых вызовов, swap/Drop/up/down/центр без циклов. Внешний driver выполняет две итерации presort, до трёх вставок на половину, до 15 сдвигов и один Drop на вставку, 13–16 пар и до одной записи центра. Write set Check имеет два назначения у пары, одно у центра. Для compiler/DFCC-развёрток остаётся обязательным контроль всех выведенных stock unwind.
- Сверены 45 прямых пар с actual кодом и все 8192 битовых маски на каждой из пяти баз. Перебраны все адресные состояния таблицы и построен вход для каждого состояния центра. Модель сдвигов прошла 31 872 случая на 12 литеральных B/R, включая повторы, 0, `2^63` и `u64::MAX`. Ранговая модель прошла 8192 детерминированных входа на каждую N с проверкой точного порядка индексов и концов.
- Shallow checkout CI-base глубины 2 принял bundle и подтвердил 27 overlay-коммитов, точный HEAD/tree и sole prerequisite. Нативные якоря и все 18 строк roster сверены с закреплённым Std. Синтетический discovery принял 131 реальную унаследованную запись из bounded discovery `45967622962/1` и 18 добавлений, отклонил подмены selector/target и добавление contract target к plain Proof.
- Python suite прошёл последовательно, 130/130 в штатном режиме и 130/130 на каждой свежей шкале 1/5/60 с. Синтетика отклонила утрату свойства любого из двух typed-copy семейств, scoped assigns и return cover, неверный stock target, задержку receipt, отсутствие подтверждённого reap или аттестации и выход за publication cutoff. Blob `ch8-cal1/test_supervisor.py` — `df63a457c3adf648d360f3d559d5d40ef00a9427`.
- YAML разобран, все восемь shell-блоков прошли `bash -n`. Detached trigger принят при точных tree, SHA, payload и sole parent. Отклонены подмены tree, `GITHUB_SHA`, номера attempt и payload `after`. Гейт индекса повторно подтвердил четыре входных SHA-256 и инвентарь и отклонил изменённый receipt.
- `git diff --check` прошёл для Std, Control, review-trigger и handoff. У локальных коммитов author и committer `Tiramisu-Cake <igkharin@gmail.com>`, сообщения содержат `[skip ci]`. Валидация офлайн, запуск CI и изменения Actions variables входят в отдельную стадию координатора.
