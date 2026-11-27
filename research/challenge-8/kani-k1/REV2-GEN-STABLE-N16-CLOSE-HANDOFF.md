# REV2 · general/stable N16 CLOSE

**READY_FOR_REVIEW · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Актуальные пины и проверки находятся в разделе [FIX1](#fix1). Пакет R1 получил NO-GO. [Ревью R1](REV2-GEN-STABLE-N16-CLOSE-REVIEW.md)

Локальный пакет содержит две левые опоры, три литеральных правых fill и два различающих контроля фактических trait-маршрутов. Следующие этапы требуют независимого ревью и отдельного GO координатора. Нативная компиляция cfg-on и результаты семи слотов остаются открытыми. [Задание](REV2-GEN-STABLE-N16-CLOSE-TASK.md) · [Правило составного допуска](REV2-COMPOSITION-RULE.md)

## Пины пакета

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-gen-stable-n16-close-w13) | `a7df430f35dca8e0a6372fe8410229277974194a` | `cac68fdb2a6e45ce9166f37783ee2aa390d38bcf` | `5a8702f59ae309b8069d380b1e3887fd48c2564b` |
| [Control](/root/kani-rev2-gen-stable-n16-close-control-w13) | `8a7094b777061721cfcf8c7848aa55c3f901b709` | `0fb7318d0dec44515633594baffb810dd4f04609` | `bcf4fd366d1fc3fe4e045bb8c6f3b54189a92435` |
| [Review-trigger, detached](/root/kani-rev2-gen-stable-n16-close-trigger-w13/control) | `74dfd5283a6f4a576634d34ace3ce6ad921d8a7d` | `0fb7318d0dec44515633594baffb810dd4f04609` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Основание g0 `fa8731df9e0b44849f771313a446685048eb6b6f`, ветка `experiment/kani-k1-kani3300g0-20261111`. Базовые деревья Std FIX1 и Control FIX1 соответственно `76ff14e1811ae4115aa1aeef2ae42986d21d3c50` и `981944277c90a3ed6d9667967d8ed2494109ee4e`. Bundle объявляет один `HEAD`: 31 линейный overlay-коммит поверх `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-n16-close-trigger-w13/control/ch8-cal1/CI-REQUEST.json) | `bbfebcaef8e4fd9e04f1693cecf4e766ec4207581164a0cbcb6748a789e44291` |
| Exact roster, канонический JSON | `0701391f3495aefc7215367d522c7759aa66d937d3de97156dd151bf3111b85b` |
| Source bindings, канонический JSON | `79e709d432951fc98996ffdacb40c7a68f12aaed3d6c33635e975aa0fad262c2` |
| [Std bundle](/root/kani-rev2-gen-stable-n16-close-trigger-w13/control/ch8-cal1/std-overlay.bundle), 86 360 байт | `3e518a27d2cbb27afe53e828b0d03e429695a51d692464ee5161969a664908c6` |

Независимый pin `CH8_REV2_GEN_STABLE_N16_CLOSE_TRIGGER_TREE=0fb7318d0dec44515633594baffb810dd4f04609`. Gated stages `pins`, `sources`, `prepare`, `measure`, `finish` и `upload-gate` связывают чистый detached HEAD с `GITHUB_SHA`, payload `after`, sole parent и деревом для push в `Tiramisu-Cake/kani` на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1. Перед upload повторно сверяются admission receipt, индекс и его члены. Схема индекса `smallsort-rev2-gen-stable-n16-close-artifact-v1` связывает четыре SHA-256 и входные пины. [Workflow](/root/kani-rev2-gen-stable-n16-close-trigger-w13/control/.github/workflows/ch8-q-pilot.yml)

## Exact roster и координаты

Все selectors используют префикс `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::close::`. Все семь корней имеют `kind=Proof`, пустые targets и Replace, `copy_back=false`. Cfg-off содержит 171 управляемую историческую запись, cfg-on — те же 171 плюс семь. Сравнение полного списка сохраняет kind, selector, source и targets. [Модуль Std](/root/verify-rust-std-rev2-gen-stable-n16-close-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_gen_stable_n16_pilot.rs:757)

| Слот | Суффикс selector | Root / local actual call | Успешные посты и covers в модуле | Ожидание / exit | Latest start |
| --- | --- | --- | --- | --- | --- |
| `GEN-N16-S8-L32-FULL` | `gen_n16_s8_l32_full` | 763:5 / 780:9 | Посты 821–826; covers 827–829 и `u64_less` | `VERIFIED` / 0 | 55:00 |
| `GEN-N16-WIDE-S4-L48` | `gen_n16_wide_s4_l48` | 832:5 / 853:9 | Посты 881–884, 896; covers 897–899 и `wide_less` | `VERIFIED` / 0 | 58:25 |
| `GEN-N16-WIDE-FILL-R48-REL7` | `gen_n16_wide_fill_r48_rel7` | 902:5 / copy 949:13, insert 950:13 | Посты 965–967; covers 971–974 и `wide_less` | `VERIFIED` / 0 | 61:50 |
| `GEN-N16-WIDE-FILL-R48-REL6` | `gen_n16_wide_fill_r48_rel6` | 977:5 / copy 1023:13, insert 1024:13 | Посты 1039–1041; covers 1045–1048 и `wide_less` | `VERIFIED` / 0 | 65:15 |
| `GEN-N16-WIDE-FILL-R48-REL5` | `gen_n16_wide_fill_r48_rel5` | 1051:5 / copy 1096:13, insert 1097:13 | Посты 1112–1114; covers 1118–1121 и `wide_less` | `VERIFIED` / 0 | 68:40 |
| `GEN-N16-WIDE-WITNESS-CORRUPT` | `gen_n16_wide_witness_corrupt` | 1196:5 / 1207:9 | До порчи 1211–1214, 1218; после 1228–1230; covers 1208, 1222 и `wide_less` | `FAILED` / 1 на 1234:9, `GEN_N16_WIDE_STABLE_EQUAL_KEYS` | 72:05 |
| `GEN-N16-STABLE-U64-WITNESS-CORRUPT` | `gen_n16_stable_u64_witness_corrupt` | 1138:5 / 1149:9 | До порчи 1153–1155, 1159–1160; после 1164–1167; covers 1150 и `u64_less` | `FAILED` / 1 на 1168:9, `GEN_N16_STABLE_U64_MULTIPLICITY` | 75:30 |

Scalar post/cover строки таблицы имеют колонку 9. Общие компараторы `wide_less` и `u64_less` закреплены соответственно на `rev2_gen_stable_n16_pilot.rs:35:5` и `rev2_u64_n13.rs:9:5`. Для каждого слота обязательны шесть grouped properties `safety_check.1/.2`, `arithmetic_overflow.1`, `precondition_instance.1/.2/.3` на `ptr/mod.rs:587:14`. Инстанс `ptr::copy_nonoverlapping::<u64>` применяется к S8 и stable witness, а у остальных `ptr::copy_nonoverlapping::<slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::Wide>`. Все выведенные unwind properties должны иметь `SUCCESS` при stock unwinding ON. [Замороженные bindings](/root/kani-rev2-gen-stable-n16-close-trigger-w13/control/ch8-cal1/CI-REQUEST.json)

Actual copy sites для S4 находятся на `smallsort.rs:832–835:9`, для merge на `885:9` и `918:9`. S8 использует обе группы. Три локальные fill copies имеют `transcribes` на `329:17`; actual вставка соответствует `330:17`, а копии сдвига и заполнения gap находятся на `722:13` и `362:13`. Wide witness проходит actual S4, fill и merge, stable witness — S8 и merge. В контролях regular projection и stock export должны согласовать ID единственного `FAILURE`, класс `assertion`, файл, строку и метку. Regular дополнительно сверяет колонку и функцию. [Actual Std](/root/verify-rust-std-rev2-gen-stable-n16-close-w13/library/core/src/slice/sort/shared/smallsort.rs)

| Исходник | Git blob |
| --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `rev2_u64_n13.rs` | `47c129a11d6cd0d0adce0be450b91eca84a25c0c` |
| `verify.rs` | `10e8612240fa99cfd5c6e2c4b1908450f4d15f3a` |
| `rev2_gen_stable_n16_pilot.rs`, CLOSE cfg/модуль на 757–758 | `ed2ec0c492317e0981a4267fbbe4d34daecb9bce` |
| `core/Cargo.toml`, CLOSE check-cfg на 77 | `fd19229c39faffe5ca09ca9635538bda7e39004a` |

## Профиль и часы

Одна job `ubuntu-24.04` X64, 110 мин. Stock CBMC 6.11.0, CaDiCaL, OB12, unwind36, jobs=1. Safety, overflow, unwinding, undefined-function и assertion-reach включены. Uninit и validity выключены. Каждый слот имеет 120 с VT, 180 с cold wall, 4 GiB group RSS, резерв ОС 2 GiB. Каталоги CWD, Cargo target, Kani target, tmp и export изолированы по слоту. У cfg-on 29 флагов в порядке request. У cfg-off опущен последний флаг CLOSE.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12

"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --no-codegen --only-codegen --quiet \
  --target-dir "$preflight/kani-target" "$std/library"

"$tool/scripts/kani" list -Z function-contracts -Z mem-predicates -Z float-lib \
  -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing "$std/library" --std --format json
```

Cfg-on compile preflight имеет предел 180 с, идёт до двух list и сохраняет первые rustc diagnostics при сбое. [Runner](/root/kani-rev2-gen-stable-n16-close-trigger-w13/control/ch8-cal1/run.py)

| Стадия | Дедлайн от старта job | Лимит |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Identity gate | 55:00 | До 60 с со входа в measure |
| Семь слотов | 78:55 | 205 с на слот, включая 180 cold wall, 10 reap, 5 receipt и 10 запаса старта |
| Финальная аттестация | 80:55 | Measure 27:00 внутренний, 29 мин внешний |
| Finish и upload-gate | 85:50 | Внешние 6 и 1 мин, 5 с запаса старта upload |
| Upload | 92:55 | Внешние 7 мин |
| План с резервом 6 мин | 98:55 | Job 110 мин |

`GEN_STABLE_N16_CLOSE_WITHIN_PROFILE` требует 7/7 `MATCHED` по ожидаемым исходам, полных своевременных receipts/projections и covers, подтверждённых sampler/reap, всех ресурсных лимитов и своевременной аттестации `COMPLETE`. Runner фиксирует исход и reap перед проекцией, сохраняет cutoff при ошибках проекции, ограничивает повтор записи receipt дедлайном и сохраняет отметку late. Следующий слот блокируется без подтверждённого reap. Caps составляют 4 MiB на проекцию и 96 MiB на публикацию. Отчёт сохраняет фазу, первую CNF, VT, cold wall, group и CBMC RSS, доступный CBMC PSS у пиков либо ближайших выборок. Неатомарная выборка Linux при смене TID может занизить RSS. [Отчёт](/root/kani-rev2-gen-stable-n16-close-trigger-w13/control/ch8-cal1/report.py)

## Исторические опоры

Оба опубликованных индекса имеют `job_status=success`, `proof_credit=NONE` и аттестацию `COMPLETE` до её дедлайна. Сверены SHA-256 и размеры всех 26 и 14 членов, канонические хэши roster и bindings, точные Std/tool commit и tree в аттестациях, receipt roots и projection selectors. У семи успешных ролей завершены regular projection и stock export, `VERIFIED/MATCHED`, exit 0, sampler/reap подтверждены, receipt своевременен. Сверены обязательные regular ID, Location, status, typed-copy инстансы, stock cover IDs, сверка Check targets и флаги того же профиля OB12, unwind36, CaDiCaL, stock Kani и CBMC 6.11.0.

| Run/attempt | Trigger commit / tree | Std commit / tree | SHA-256 индекса |
| --- | --- | --- | --- |
| `46054351048/1` | `9e57088dade0aa932b83bca98d97fe02ae4963f5` / `9021966b36dcbbf0a7f36d9065bd0dae580a4e98` | `14a5a7322a050c7d5028054acc5825172d43c14c` / `bf379fc6b403e9caa51e549cc53956d66549ef3c` | `3e856c127e21aebd3e37a9a8a909b36aba2e922cd22b6e1066a80139d9ecd7d9` |
| `46064575550/1` | `6dedf7dd6260d84cd38933e6a326b30bacd54791` / `981944277c90a3ed6d9667967d8ed2494109ee4e` | `5a8702f59ae309b8069d380b1e3887fd48c2564b` / `76ff14e1811ae4115aa1aeef2ae42986d21d3c50` | `2416346b0df8101878d9a73051dc1fb0330d593151a108151ffd2ca79ffeed9a` |

[Индекс пилота](/root/ch8-artifacts/run-46054351048/ch8-rev2-gen-stable-n16-pilot-Linux-X64-46054351048-1/index.json) · [Индекс FIX1](/root/ch8-artifacts/run-46064575550/ch8-rev2-gen-stable-n16-pilot-fix1-Linux-X64-46064575550-1/index.json)

SHA-256 `source_bindings` пилота и FIX1 соответственно `04e5df7a92044846d54bb6efa8fe5869a1392e9f03b05f4c6d0a4d9a8198bddd` и `33318eebbe632b9afee1719c1db4b83523733171482bfcf6cf581f2e4913db76`. `attestation.json` соответственно `66bf2c277b6dd5144f9637302ca23e90a62992dbb9d8edc4e1ae0438e0c27bd9` и `5791bb760d37a8e11096db5c6fdb47bb6c5abf4b84ac4d400d3056afe1dc7fa5`. Исторические blobs модуля `027b71ea2726e8a89047da497a9b297455448be5` и `fc42d3e4977443e4a01e0bdf4394ba2303d17e0f`. У обоих run совпадают runtime, `ptr/mod.rs`, компаратор u64 и registry с текущими blobs из таблицы. Исходник модуля каждого run входит точным байтовым префиксом в текущий модуль.

Префикс каждого selector и target ниже — `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::`. Для plain строк targets пусты. Все хэши относятся к `slots/<ID>/receipt.json` и `slots/<ID>/projection.json` в соответствующем индексе.

| ID | Selector → Check target | Посты и covers | SHA-256 receipt / projection | VT / cold wall, с |
| --- | --- | --- | --- | ---: |
| `GEN-N16-S8-R32-FULL` | `gen_n16_s8_r32_full` | Порядок, независимый probe кратностей, две отсортированные tmp-четвёрки, V и D frame; 4/4. Полный домен u64. | `e6d2ddd7b9b0f4fac0db412c103d39685bcf7caf36a35b6c3b53b2633edd4869` / `e6b9e402251cf18b807c0da5a914a2119bee159d9002dfe9fd8458c58bc140dd` | 61.478 / 104.168 |
| `GEN-N16-S8-R32-BITS` | `gen_n16_s8_r32_bits` | Те же посты; 4/4. Диагностический 0/1 домен. | `e2b9e1f9e199f5cb88b03554edd63916510620b862201492931f431ef5f3203d` / `0de643c8e9db7c96db422a82e867dd244f8f0ece24f41abe55ef8b1d521b495c` | 37.174 / 79.564 |
| `GEN-N16-WIDE-S4-R48` | `gen_n16_wide_s4_r48` | Порядок, полные записи по меткам, устойчивость при равных ключах, оба frame; 4/4. | `3d8448f0f8ec6ef634f18071f20cd9a5c5065a397c21b8f50e0538db13208db9` / `62c95aaf1d179adaf463f0d45b5e58fd847ae4e4142a1ce9af913d64690469e1` | 34.052 / 76.557 |
| `GEN-N16-WIDE-FILL-R48-REL4` | `gen_n16_wide_fill_r48_rel4` | Exact upper bound и оба frame; 5/5. | `5134e96c2fdd82e54ee30a10de0795a1f78a76941ad3c7c61ff025c87d90b0c6` / `4883344f80da25c213bf9c877f0c423ef06757873fe52de2bb96f9820ca41c7e` | 19.990 / 62.452 |
| `GEN-N16-U64-S32-MERGE-PAIR` | `gen_n16_u64_s32_merge_pair` → `actual_merge_pair_u64_s32` | Два шага с read/write/disjoint, курсорами и полными словами, оба frame; 10/10. | `153bf3a1dcffaa20dbb86aa983d7ade7106402584ee55d791af4591de86788cd` / `cda81210372d1f81ed8f9fcb8d14f0d0896dfeb9581b07fd910b911792256e8a` | 93.489 / 140.479 |
| `GEN-N16-WIDE-S48-MERGE-UP` | `fix1::gen_n16_wide_s48_merge_up` → `fix1::actual_merge_up_wide_s48` | Read/write/disjoint, курсоры, полная запись и оба frame; 7/7. CNF 883 260 / 4 011 218. | `45f3d9c98add57fdd6cd7c6e7e3a273eb9453f650a87d81d6160922d78acd9c7` / `4a3759c0085caff2e371210d9a8a2afeed76444bbc40cf52246d861ba3177c5e` | 59.657 / 94.546 |
| `GEN-N16-WIDE-S48-MERGE-DOWN` | `fix1::gen_n16_wide_s48_merge_down` → `fix1::actual_merge_down_wide_s48` | Read/write/disjoint, курсоры, полная запись и оба frame; 7/7. CNF 865 296 / 3 976 467. | `cc2436b89f44ada198137159349e287b6453e8a3276763f6fdcb7aa8ae3252bf` / `70eaedaae5b4e7bac236bde2daf4c2a7278fcad4fabad17c15f27417b61aec90` | 60.613 / 97.249 |

Точные matched anchors лежат в `result_evidence.mandatory_anchors` проекции каждого Check и сопоставлены с historical `source.json`. Для u64 pair подтверждены `single_top_level_call` и `no_recursive_call` на 304:1. Для FIX1 Up и Down те же группы подтверждены на 561:5 и 658:5; у всех трёх Check присутствуют scoped `memcpy.assigns.1/.2`, шесть typed-copy свойств на `ptr/mod.rs:587:14` и успешные выведенные unwind. У исходного Wide pair с selector `gen_n16_wide_s48_merge_pair` и target `actual_merge_pair_wide_s48` статус `TIMEOUT/UNAVAILABLE` на 180 с. Композиция Wide опирается на два успешных FIX1 Check. [Исторические координаты и точные посты](REV2-GEN-STABLE-N16-PILOT-HANDOFF.md)

## Внешняя композиция нормального возврата

Домен обоих маршрутов — инициализированная живая V18, `S=v[1..17].as_mut_ptr()` и база отдельного живого scratch `D`. Терминальный пост включает порядок по компаратору, точные входные кратности полных записей и сохранение `v[0]`, `v[17]`. Для Wide он включает порядок тождеств записей с равными ключами. Ниже аргумент авторской стороны, условный на будущих положительных слотах и независимой сверке.

1. **Dispatch.** Stable Freeze `u64` с полным числовым `<` передаёт внешний uninit D32 на `smallsort.rs:81`. Проверка `:286` требует `N+16=32` элемента, а `:297–307` выбирает S8. Actual unstable `Wide` проходит forwarding `:134–139` в Copy+Freeze ветвь `:213–224`. У `Wide` `repr(C)`, три `u64`, размер 24, align 8, Copy+Freeze, `!has_efficient_in_place_swap` и `24×48=1152≤4096`. Поэтому `:221–222` выбирает private general, `:261–273` создаёт отдельный uninit D48, `:308–313` выбирает S4. Компаратор Wide читает только `key`.
2. **Инициализация u64.** На `:299` `sort8_stable(S,D,D+16,…)` читает `S[0..8]`. Два вызова S4 на `:850–851` полностью записывают `D[16..20]` и `D[20..24]` перед их первым чтением на `:857`. Merge внутри S8 пишет `D[0..8]`. У правого вызова `:300–305` те же операции над `S[8..16]`, tmp `D[24..28]` и `D[28..32]`, dst `D[8..16]`. В одной D32 четыре интервала попарно раздельны. Левый dst/tmp занимают байтовые `[0,64)` / `[128,192)`, правый — `[64,128)` / `[192,256)`. Frame каждой опоры сохраняет V18 и области другой опоры. Для каждой половины пост о кратности независимого полного `u64` probe действует для любого полного слова. `presorted_len=8` даёт пустые fill-диапазоны `8..8`.
3. **Инициализация Wide и перенос fill.** S4 на `:310–311` независимо читает `S[0..4]` и `S[8..12]` и инициализирует `D[0..4]` и `D[8..12]`. Правый шаг при литеральном `R=4,5,6,7` читает `S[8+R]`, копирует всю запись в writable uninit `D[8+R]` и вызывает `insert_tail(D+8,D+8+R,…)`. Входной префикс `D[8..8+R]` инициализирован и упорядочен. При `p = count(old.key ≤ x.key)` точный пост имеет `old[j]` для `j<p`, `x` на `p` и `old[j−1]` для `j>p`, сравнивая три поля. Новый хвост инициализирован. Frame фиксирует V18, включая следующий источник, и scratch вне `D[8..9+R]`. Для левых rel4–7 `S[8+j] ↔ S[j]`, `D[8+j] ↔ D[j]`, сдвиг −192 байта в каждой из двух аллокаций. Сохраняются выравнивание, bounds, раздельность V/D, порядок и расстояния внутри префикса, условие `sift==begin` и строгие сравнения. Копия на `:329` полностью пишет tail перед чтением. В теле `insert_tail` `:705–731` `tmp` является отдельным объектом, gap убывает от tail и копия сдвига идёт между разными соседними ячейками. `Drop` gap guard копирует целую запись из tmp в gap. Поэтому перенос применим в обоих аллоцированных диапазонах и сохраняет остальной D. После двух цепочек из четырёх шагов инициализирован весь `D[0..16]`.
4. **Перенос от канареек и от меток.** S8 читает только активные слова V и уже записанные tmp, S4 — только свои четыре входные записи V. Fill читает одну исходную запись V, затем только инициализированные prefix и tail данной половины либо отдельный tmp. Merge читает кандидатов только из `D[0..16]`. В локальных измерениях frame-канарейки читаются оракулом после вызова, в частности оба Wide Check читают `D[16..48]` для frame. Для actual `uninit OFF` записи и наблюдаемый результат зависят только от указанных read-областей. Остальные ячейки сохраняются покомпонентными write set и могут оставаться uninit. Для Wide S4 локальная метка `j` соответствует исходной позиции `j` или `8+j`. В S4, fill и merge числовое сравнение читает только ключ, каждый copy перемещает всю запись. Замена специальных меток и payload произвольными значениями сохраняет ветвления и перестановку исходных идентичностей. Тождество ведётся по исходной позиции. У каждого fill вставка после равных сохраняет их накопленный порядок. До merge обе половины упорядочены по `(key, исходная позиция)`.
5. **Индукция по рангам.** На `:342–346` `bidirectional_merge` читает две половины из D и пишет в S. На входе в итерацию `k=0…7` поддерживаем `a+b=c+d=k`, где `a,b` — счётчики прямого обхода, а `c,d` — обратного. Основание `k=0`: все счётчики нулевые. Все четыре счётчика не превосходят `k<8`, поэтому `D[a]`, `D[8+b]`, `D[7−c]`, `D[15−d]` читаемы, а цели `S[k]` и `S[15−k]` раздельны. Exact u64 pair и композиция Wide up→down применимы к этим адресам. Up сохраняет D, а down принимает V18 с уже записанным up. Срезы каждого обхода рассматриваются независимо в фиксированном D. Up выбирает следующий минимум с tie-left, down — следующий максимум с tie-right. Все левые исходные позиции меньше правых, поэтому tie-правила совпадают с выбором минимума и максимума в полном порядке `(key, исходная позиция)`. На шаге получаем ранги `k` и `15−k`. Перемещение единственного выбранного курсора каждого обхода устанавливает равенства для `k+1`. На восьми шагах диапазоны рангов `[0,8)` и `[8,16)` исчерпывают 16 различных исходных позиций и заполняют каждую ячейку S ровно один раз.
6. **Курсоры и возврат.** Из полного потребления каждой из двух восьмёрок следует `a+c=b+d=8`. Тогда `left=D+a=D+(8−c)=left_rev.wrapping_add(1)` и `right=D+8+b=D+8+(8−d)=right_rev.wrapping_add(1)`. На `:1042` проверка проходит, нечётное завершение пусто для N16. `mem::forget(drop_guard)` на `:347` завершает нормальный путь без восстановительной копии. Merge frame и frame листьев сохраняют обе крайние записи V18. Для u64 пост наблюдает полные значения и их кратности. Для Wide получены полные записи и устойчивость по исходной позиции.
7. **Различающие контроли.** Stable witness вызывает actual trait с uninit D32. После `AFTER_STABLE_N16_RETURN` каноничность, порядок, восемь единиц и frame проверяются до `v[8] ^= 1u64`. Потом маска `0xff80`, порядок, каноничность и frame сохраняются, а число единиц 9 вместо 8. Wide witness проходит S4 и четыре вставки на обеих половинах, затем merge. После `AFTER_WIDE_N16_RETURN` успешные assertions проверяют порядок, каждую полную запись по метке, устойчивость, точную пару и frame. Затем меняются целые `v[6]`, `v[7]` с ключом 0 и метками 7 и 9. Успешные assertions до точки порчи доминируют над наблюдением порчи, а после перестановки проходят порядок ключей, records-by-tag и frame. Каждый контроль имеет фиксированный активный вход и произвольный V18 frame. Covers подтверждают достижимость фактического компаратора и возврата, у Wide также отличимых равных записей.

| Зависимый маршрут | Обязательство | Открытый результат |
| --- | --- | --- |
| Stable u64, S8 → merge | Полный left S8 в геометрии D32, right FULL и exact pair уже измерены | `GEN-N16-S8-L32-FULL VERIFIED/MATCHED` с полными свойствами и covers в профиле |
| Wide unstable, S4 → fill → merge | Left S4, правые rel5–7, перенос левых rel4–7 и инициализация D48. Right S4, rel4 и Up/Down уже измерены | `GEN-N16-WIDE-S4-L48` и три fill `VERIFIED/MATCHED`. Независимая сверка переноса, read/write-областей и тождеств |
| Stable u64 actual witness | Вызов stable entry и один отказ кратностей после изменения | `GEN-N16-STABLE-U64-WITNESS-CORRUPT FAILED/MATCHED` на 1168:9 |
| Wide actual witness | Вызов unstable entry и один отказ стабильности после перестановки | `GEN-N16-WIDE-WITNESS-CORRUPT FAILED/MATCHED` на 1234:9 |
| Оба normal-return маршрута | Discovery, профиль, полные своевременные receipts/projections, reap, attestation; перенос от канареек, ранги, конечные указатели и frame | Нативная cfg-on компиляция и результат пакета. Независимое ревью композиции и решение координатора о допуске |
| Оба маршрута, паника / публикация | Восстановление при панике, область `stub_verified` и штатный CI pr752 | Отдельные panic evidence, Check/replacement proof и результаты точного штатного профиля по требованию владельца |

## Локальная валидация

- Применён и проверен rustfmt `nightly-2026-11-19 --edition 2024 --config use_small_heuristics=Max` до фиксации координат. SHA-256 бинарника `0cb21861860ae07c03b7097b099ea3e28dfb3857a9b09acce0df6b165f25cc70`. Проверены Rust-видимость ancestor traits и переиспользованных имён, TOML, YAML с уникальными ключами, восемь блоков `bash -n`, синтаксис Python и `git diff --check`. Удаление единственной строки check-cfg восстанавливает прежний manifest. Проверен точный байтовый префикс модуля и отсутствие изменений runtime, контрактов, registry и прочих модулей.
- Scratch48 frame/init использует литеральные интервалы не длиннее 32; frame helper правых fill получает const END 16, 15 или 14. Другие проходы ограничены V18, активными 16 или четвертью/половиной. Actual вставка имеет максимум 7 сдвигов, внутренний merge8 — четыре пары, внешний merge — восемь, fill — два прохода по четырём шагам. Наблюдатели используют скалярные сравнения слов и трёх полей записей, включая frame, без сравнения массивов или скрытого `memcmp`. Stock `any` для массива и typed `memcpy` унаследованы от пилота. Проверка сгенерированных unwind остаётся нативной.
- Диагностическая модель actual расписаний воспроизвела 256 входов S4, 256 битовых входов S8, 45/63/84/108 случаев для rel4/5/6/7 и 12 870 ранговых чередований. У Wide witness все четыре вставки каждой половины дали по два сдвига. Up записал метки `[1,3,4,5,6,7,9,11]`, down в порядке записи — `[10,8,2,0,15,14,13,12]`. У u64 подтверждён переход масок `0xff00 → 0xff80`. Эти случаи проверяют трассы и внешнюю аргументацию.
- Depth-2 Std checkout без alternates принял shallow bundle, сохранил исходный HEAD и shallow boundary. Source gate сверил цепочку из 31 commit/tree/parent, 30 текущих blobs, неизменные historical rosters и 1 150 литеральных координат. Подмена `transcribes` отклонена для каждого из трёх fill.
- На точном detached review-trigger с синтетическим push прошли `pins`, `sources`, `finish`, `upload-gate` и `upload-check`. В локальном `sources` рекурсивная submodule-проверка заменена проверкой чистых detached Std/tool с точными commit/tree. Синтетический `finish` создал семь `NOT_STARTED` receipts. Подмены tree, payload, схемы индекса, admission и индексированного receipt отклонены. Оба поздних upload-гейта отклонены.
- На том же trigger Python 3.12.3 последовательно прошёл четыре suite. Обычная шкала 139/139 за 57,618 с. Старт с 1 с — 139/139 за 57,399 с, с 5 с — 139/139 за 57,821 с, с 60 с — 139/139 за 62,977 с. Синтетика проверила discovery 171 → 178, неправильный kind/selector/source/Check target и точное `standard harness has a contract target` для исторического plain selector cfg-off и нового CLOSE plain selector cfg-on. Проверены потеря typed-copy/post/return, неверный unwind, чужой или второй отказ, неполная проекция, поздний receipt, потеря reap/attestation, несовпадение индекса и поздний upload.
- `test_supervisor.py` сохранил blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Пакет подготовлен локально без Cargo, rustc, Kani, CBMC, CI, push и изменения Actions variables. Все четыре итоговых коммита имеют `[skip ci]` и author/committer `Tiramisu-Cake <igkharin@gmail.com>`.

## FIX1

**READY_FOR_REVIEW · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.** Основание g0 `916655ee36bab21b8c388fd24ab3b1c8aa9cea77`. На строке 1085 корня `GEN-N16-WIDE-FILL-R48-REL5` цикл подсчёта позиции использует `0..5` для `old: [Wide; 5]`, максимальный индекс 4. В комментариях на строках 948, 1022 и 1095 транскрипция уточнена до `smallsort.rs:329`. Эти четыре строки составляют всю дельту Std от R1. [Ревью R1](REV2-GEN-STABLE-N16-CLOSE-REVIEW.md) · [Исправленный rel5](/root/verify-rust-std-rev2-gen-stable-n16-close-fix1-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_gen_stable_n16_pilot.rs:1085)

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std FIX1](/root/verify-rust-std-rev2-gen-stable-n16-close-fix1-w13) | `e8e8af6d3b4c77ce0ee25066e9c97b6df3fd222e` | `f48157264ed99a8bd5b5faa4c38709eef61c0b47` | `a7df430f35dca8e0a6372fe8410229277974194a` |
| [Control FIX1](/root/kani-rev2-gen-stable-n16-close-fix1-control-w13) | `ad7e2ba127919b463a395819c94a30225b844b90` | `8fff1fc16152df0c6febf8bac6729199a12407be` | `8a7094b777061721cfcf8c7848aa55c3f901b709` |
| [Review-trigger FIX1, detached](/root/kani-rev2-gen-stable-n16-close-fix1-trigger-w13/control) | `f546e8873c35e49a7113394c37d63ef9526f964e` | `8fff1fc16152df0c6febf8bac6729199a12407be` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-n16-close-fix1-trigger-w13/control/ch8-cal1/CI-REQUEST.json) | `c3049756a255b08e58d8def88cc626e338ca2f8ba3be8ea0533c79a58d634f9e` |
| Exact roster, канонический JSON | `0701391f3495aefc7215367d522c7759aa66d937d3de97156dd151bf3111b85b` |
| Source bindings, канонический JSON | `d320686c751aab6b376175f38a1b7bee2b9e9b10eeb48e131d495c9bff0bcfb7` |
| [Std bundle](/root/kani-rev2-gen-stable-n16-close-fix1-trigger-w13/control/ch8-cal1/std-overlay.bundle), 87 143 байта | `8668301c8ae16e69749462341b411e206b22bd8bb01b53b819ca6d1305ff05a7` |

Независимый pin FIX1 — `CH8_REV2_GEN_STABLE_N16_CLOSE_TRIGGER_TREE=8fff1fc16152df0c6febf8bac6729199a12407be`. Новый blob модуля `cfafc360819a4011590a8cf8624dd2f22d29b37e`. Bundle объявляет единственный `HEAD` и содержит 32 последовательных overlay-коммита поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`. Цепочка явно сверяет R1 перед FIX1. Проверены точный префикс до CLOSE и все 1 150 литеральных координат. Exact roster, аргументы, часы и исторические привязки из предыдущих разделов применяются к FIX1.

### Аудит индексов

| Корни и наблюдатели | Сверенные границы локальных массивов |
| --- | --- |
| Левый S8 | Frame V18 и его копии использует индексы 0–17. Пары исходных слов доходят до 8, dst до 7. Tmp читается в `D[16..20]` и `D[20..24]`. Scratch-frame с `8+i` и `24+i` при `i<8` доходит до 15 и 31 в D32. |
| Левый Wide S4 | Исходная четвёрка использует V18 индексы 1–4, пары результата и поиск меток используют D48 индексы 0–3. Frame D48 разбит на `4..32` и `32..48`. |
| Wide rel5, rel6 и rel7 | Для `R=5/6/7` массив `old` имеет ровно `R` элементов из `D[8..8+R]`. При `i∈1..R` допустимы `i−1` и `i`. Подсчёт по `0..R` даёт `0≤pos≤R`. При `j∈0..R+1` ветка `j<pos` допускает `old[j]`, ветка `j>pos` даёт `0≤j−1<R`, а ветка равенства берёт `x`. Чтение `scratch[8+j]` доходит до 13/14/15 соответственно. Инициализация и frame проверены в D48, включая `END=14/15/16`. |
| Stable u64 witness и `active_u64_mask` | Наполнение и маска используют индексы 1–16 в V18. Соседние сравнения имеют `i+1≤16`, сдвиг в маске имеет максимум 15. Фиксированные frame и индекс порчи лежат в V18. |
| Wide witness и его наблюдатели | `keys[i % 8]` даёт 0–7 для массива длиной 8. Соседние сравнения и поиск меток в активном V18 имеют максимум 16. `wide_v` и `wide_v_frame` используют 0–17. Индексы обмена 6 и 7 лежат в активном срезе. |

По исходнику сверены все 34 цикла семи корней и десять циклов пяти наблюдателей и инициализаторов. Три специализации scratch frame проверены отдельно. Новый source gate читает список элементов `old` и объявление D48 и сверяет шесть литеральных проходов в каждом fill. Он отклонил исходный R1 на rel5 с `old=5, scratch=48`. Регрессия проверяет для каждого из rel5/6/7 лишнюю итерацию подсчёта, неверное начало сравнения соседей, лишнюю итерацию поста и scratch-цикла и потерю элемента `old`. [Source gate](/root/kani-rev2-gen-stable-n16-close-fix1-trigger-w13/control/ch8-cal1/request.py) · [Синтетика](/root/kani-rev2-gen-stable-n16-close-fix1-trigger-w13/control/ch8-cal1/test_run.py)

### Валидация FIX1

- Rustfmt `nightly-2026-11-19` с `use_small_heuristics=Max`, `git diff --check`, YAML с уникальными ключами и восемь блоков `bash -n` прошли. `test_supervisor.py` имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427`.
- Depth-2 Std checkout без alternates принял bundle. На точном detached trigger синтетические `pins`, `sources`, `finish`, `upload-gate` и `upload-check` прошли с явной локальной заменой рекурсивной проверки submodules на проверку чистых detached Std/tool и их commit/tree. Проверены 30 blobs и семь `NOT_STARTED` receipts. Чужой tree, payload, `transcribes`, подмены индекса и receipt, поздний upload отклонены.
- Полный suite Python 3.12.3 прошёл последовательно на точном trigger. Обычная шкала 140/140 за 59,477 с, старт с 1 с 140/140 за 57,160 с, с 5 с 140/140 за 57,123 с, с 60 с 140/140 за 56,013 с.
- Нативная компиляция cfg-on и исходы семи слотов ожидают независимого ревью FIX1 и отдельного GO координатора. Локальная стадия выполнила только статические и синтетические проверки. CI, push и изменения Actions variables не выполнялись. Все четыре коммита FIX1 имеют `[skip ci]` и author/committer `Tiramisu-Cake <igkharin@gmail.com>`.
