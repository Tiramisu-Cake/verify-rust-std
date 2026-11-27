# REV2 · составной consumer u64 N20/N21

**`READY_FOR_REVIEW` · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Пакет содержит два контроля фактической сети с порчей после возврата и две локальные проверки copy-back и frame. Для инициализированного `[u64;34]` кандидат на исследовательский допуск связывает нативные опоры и внешний вывод о числовом порядке, кратностях входных слов и неизменности внешних слов при нормальном возврате из `small_sort_network::<u64, _>(&mut v[1..1+N], &mut u64_less)`. Независимое ревью и отдельный GO обязательны перед запуском. [Задание](REV2-U64-N20-N21-CONSUMER-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Замороженные входы

| Роль и checkout | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15) · `work/rev2-u64-n20-n21-consumer-std-w15` | `97b1df7b0a26e821f5b204c22ce291da5d123d55` | `78b555dea0ef04e81c28c461cdcfeed6cab23086` | `b09c6f22bfbd1ce8eb6afccf96df6b9a2ad3c54b` |
| [Control](/root/kani-rev2-u64-n20-n21-consumer-control-w15) · `work/rev2-u64-n20-n21-consumer-control-w15` | `c2bcb3744b88f666e006fe4397f37cc83b21b5ba` | `23841cd660808a5a0238e6056aa61a87d72c1d15` | `c4da71875efe80ebcfe78094afe6889a902d2da5` |
| [Review-trigger](/root/kani-rev2-u64-n20-n21-consumer-trigger-w15/control) · detached · `review/rev2-u64-n20-n21-consumer-trigger-w15` | `9b30a6c866beefbe0b0a2d54d5e919a959c8da55` | `23841cd660808a5a0238e6056aa61a87d72c1d15` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Задание закреплено в g0 на `f16a69904a1a47059266fb343dc11c588ed4ffac`. Деревья исходных Std и Control providers соответственно `a784a8d12b2d7439233385ffa25f512e4f2c623b` и `0d0857a039e5ffa263414952de49b716e3371c25`. Bundle объявляет один `HEAD` и добавляет 26 overlay-коммитов к CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` (tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`). Stock Kani закреплён на `9834c96ce90ff57d8495416530b080dc3d52ce25` (tree `938e9932cb2127239afb4f093f6302652c053398`).

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n20-n21-consumer-trigger-w15/control/ch8-cal1/CI-REQUEST.json) | `c15c3f98dee99c26c2e28cd2bb8a4cd1218c5d168d2fabb652a7f41c7977a9fa` |
| Exact roster, канонический JSON | `43480e47b5af7e9038983cdaaa7531695ac6b5958f2fa831df9a883be655345a` |
| Source bindings, канонический JSON | `b4d9130b09b94520080f55818de1f7f83085d7bef9cadf342d164b223258da18` |
| [Std bundle](/root/kani-rev2-u64-n20-n21-consumer-trigger-w15/control/ch8-cal1/std-overlay.bundle), 69 364 байта | `6640b24091126d924f97b8da8a891814be6f1bb8738f2eaba37301a9dae3ed49` |
| [Workflow](/root/kani-rev2-u64-n20-n21-consumer-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) | `755cf484d9c58628c9647be024d037e86e6ee7aa1a28004f2ad5991bf484be11` |

Независимый pin `CH8_REV2_U64_N20_N21_CONSUMER_TRIGGER_TREE` для будущего GO получает дерево review-trigger. `pins`, `sources`, `finish` и `upload-gate` сверяют чистый detached HEAD, fork `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, единственного parent и совпадение HEAD с `GITHUB_SHA` и payload `after`. `sources` и `finish` сопоставляют admission receipt. Перед upload проверяются admission receipt, trigger в индексе, четыре хэша входов, request и инвентарь членов. Схема индекса `smallsort-rev2-u64-n20-n21-consumer-artifact-v1`. [Гейты](/root/kani-rev2-u64-n20-n21-consumer-trigger-w15/control/ch8-cal1/run.py)

## Exact roster и native anchors

Все четыре корня plain `Proof`, `unwind(36)`, `copy_back=true`, OB12, targets пусты. Discovery сравнивает cfg-off и cfg-on, сохраняя kind, selector, файл и targets 118 исторических REV2 записей и добавляя четыре plain Proof. Новый cfg `kani_smallsort_rev2_u64_n20_n21_consumer` включается последним в списке из 24 флагов и зависит от `kani_smallsort_rev2_u64_n13` внутри `cfg(kani)`. Флаг N20/N21 providers остаётся включённым в обоих list. [Регистрация](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify.rs:309)

| Слот / exact selector | Root | Ожидаемый исход / exit | Успешные посты / covers | Latest start |
| --- | ---: | --- | ---: | ---: |
| `U64-N21-WITNESS-CORRUPT` · `slice::sort::shared::smallsort::verify::rev2_u64_n20_n21_consumer::u64_n21_witness_corrupt` | 15:1 | FAILED / 1 | 4 / 3 | 55:00 |
| `U64-N20-WITNESS-CORRUPT` · `slice::sort::shared::smallsort::verify::rev2_u64_n20_n21_consumer::u64_n20_witness_corrupt` | 21:1 | FAILED / 1 | 4 / 3 | 58:25 |
| `U64-N21-COPY-BACK-FRAME` · `slice::sort::shared::smallsort::verify::rev2_u64_n20_n21_consumer::u64_n21_copy_back_frame` | 27:1 | VERIFIED / 0 | 3 / 1 | 61:50 |
| `U64-N20-COPY-BACK-FRAME` · `slice::sort::shared::smallsort::verify::rev2_u64_n20_n21_consumer::u64_n20_copy_back_frame` | 33:1 | VERIFIED / 0 | 3 / 1 | 65:15 |

| Метка | Функция и координата | Требование |
| --- | --- | --- |
| `REV2_U64_N13_COMPARATOR_CALLED` | `rev2_u64_n13::u64_less`, 9:5 | SATISFIED в обоих контролях |
| `REV2_U64_ACTUAL_MIXED_INPUT`, `AFTER_COPY_BACK` | `check_witness_corrupt::<N>`, 45:5 и 49:5 | SATISFIED. Actual вызов 48:5 |
| `REV2_U64_ACTUAL_BEFORE_CORRUPT_CANONICAL_OUTPUT`, `REV2_U64_ACTUAL_BEFORE_CORRUPT_SORTED_POPCOUNT` | `check_witness_corrupt::<N>`, 51:5 и 52:5 | SUCCESS до порчи 54:5 |
| `REV2_U64_ACTUAL_V34_FRAME`, `REV2_U64_ACTUAL_CANONICAL_OUTPUT` | `check_witness_corrupt::<N>`, 56:5 и 58:5 | SUCCESS после порчи |
| `REV2_U64_N20_ACTUAL_SORTED_POPCOUNT` | `check_witness_corrupt::<20>`, 60:9 | Единственный FAILURE в N20 |
| `REV2_U64_N21_ACTUAL_SORTED_POPCOUNT` | `check_witness_corrupt::<21>`, 62:9 | Единственный FAILURE в N21 |
| `DEST_EQUALS_SOURCE`, `SOURCE_PREFIX_FRAME`, `V34_FRAME` | `check_copy_back::<N>`, 111:5, 112:5 и 115:5 | SUCCESS после typed copy 102:14 |
| `AFTER_COPY_BACK_FRAME` | `check_copy_back::<N>`, 116:5 | SATISFIED после всех постов |

Regular сверяет функцию, класс, файл, строку, столбец и статус каждого якоря. Во всех слотах требуются шесть SUCCESS grouped IDs `ptr::copy_nonoverlapping::<u64>.safety_check.1/.2`, `.arithmetic_overflow.1`, `.precondition_instance.1/.2/.3` на `core/src/ptr/mod.rs:587:14` и SUCCESS всех выведенных свойств unwind при stock `unwinding=ON`. Stock сверяет exact Proof, профиль, достигнутые cover IDs, итоги проверок и тот же ID единственного FAILURE класса assertion в каждом контроле. Успешные regular IDs сверяются с числами successful checks в stock export. Связь группы с конкретным исполнением см. в правиле координатора. [Проектор](/root/kani-rev2-u64-n20-n21-consumer-trigger-w15/control/ch8-cal1/results.py) · [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

## Опоры и привязка к исходникам

| Исходник | Git blob в Std consumer | Привязка |
| --- | --- | --- |
| [smallsort.rs](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs) | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` | Совпал во всех трёх опорных run и Std consumer. Перечень 25 пар `553–577`, swap `488–519`, insertion driver `742–769`, shift `722:13`, gap-fill `362:13`, up/down copy `885:9` и `918:9`, merge `1014–1045`, copy-back `425:9`. |
| [ptr/mod.rs](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/ptr/mod.rs:587) | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` | Совпал во всех run. Typed copy groups на 587:14. |
| [rev2_u64_n13.rs](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n13.rs:8) | `47c129a11d6cd0d0adce0be450b91eca84a25c0c` | Run N13 имел blob `6658b28d64647aa6e11c5bee3c71a135f09b2a6c`. Проверенная побайтная дельта меняет видимость `u64_less` на `pub(super)`. Тело `a < b` и якоря остались с теми же координатами. |
| [rev2_u64_n18_n19.rs](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n18_n19.rs:356) | `4ea168fc664f9f4733a80082af9cdd441f06a2ed` | B01/L09 bit sort9. |
| [rev2_u64_n20_n21.rs](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n20_n21.rs) | `5af7b8f629e6b218c5c4ccb7672aa5754fb9fecb` | B11 sort9 и swap, три вставки, pair Checks и odd center. |
| [rev2_u64_n20_n21_consumer.rs](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n20_n21_consumer.rs) | `23d593988ce9890ff60178e176c3ae2fb63f1d94` | Четыре новых plain roots. |
| `verify.rs`, `core/Cargo.toml` | `c85a4b693f20874af2cf38b5b057d650de525ba4`, `1a6a6a581d633f5d2bde7013203ed54396b3f764` | Побайтная дельта из регистрации и check-cfg. |

| Опорный run | Std commit / tree | SHA-256 индекса | Сверенные члены |
| --- | --- | --- | ---: |
| [45919454859/1](/root/ch8-artifacts/run-45919454859/ch8-rev2-u64-n13-Linux-X64-45919454859-1/index.json) | `4d6dd509956dff820a596ff1af9c0aae347aca26` / `b0dc6d628690b7bc58225e2f60503ed4f8ae32b3` | `6d7e603aa2fe26dd62c0f41725d664bf726be89836c16c35efbe641f3a0661f9` | 17 |
| [45938919685/1](/root/ch8-artifacts/run-45938919685/ch8-rev2-u64-n18-n19-Linux-X64-45938919685-1/index.json) | `c8eefae4c8073cff31e5576b372d5105b52797a1` / `4f9687a4edccf69ef86ee8b4c2e01de9b3517539` | `7b1e589aaf491a38f2e5232411ee734793e73f79e08d5e6c956d9669544fc202` | 29 |
| [45946532451/1](/root/ch8-artifacts/run-45946532451/ch8-rev2-u64-n20-n21-Linux-X64-45946532451-1/index.json) | `b09c6f22bfbd1ce8eb6afccf96df6b9a2ad3c54b` / `a784a8d12b2d7439233385ffa25f512e4f2c623b` | `e9ed86f4712bb3d6307b4b8be309bd8c3fb934d8a0457a2c26155bc6a1199410` | 32 |

Для нужных опор сверены полный roster, exact selector, Check target или plain Proof, размеры и хэши членов индекса, native assertion locations/statuses и cover IDs. Все используемые опоры имеют `VERIFIED/MATCHED`, exit 0 и аттестацию run `COMPLETE`. Общий профиль опор закрепляет stock Kani, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, прежние `-Z`, `uninit/validity=OFF`. В таблицах ниже суффикс selector получается из ID в нижнем регистре с заменой дефисов на подчёркивания. Префикс задаётся модулем опоры после `slice::sort::shared::smallsort::verify::`. Хэши в каждой строке идут в порядке receipt SHA-256, projection SHA-256. [Координаты опор N20/N21](REV2-U64-N20-N21-HANDOFF.md#roster-и-нативные-координаты) · [Опора B01](REV2-U64-N13-ADMISSION.md)

### Рёбра N20

| Ребро | Предпосылки, режим и вывод на фактических вызовах | Нативные опоры и хэши |
| --- | --- | --- |
| Левая половина `v[1..11]` | Произвольные слова B01, rel0–8. Sort9 на abs1–9, native каноничность, маска и frame на `rev2_u64_n18_n19.rs:389/390/395:5`. Swap B01 min/max/frame на `rev2_u64_n13.rs:35/36/42:5`, сужение `b<13` до `b<9`. Перенос L09→L10 сохраняет произвольное abs10. Rel9 вставляет abs10 в отсортированные abs1–9. Точное отображение/frame на `rev2_u64_n20_n21.rs:132/141:5`. Записи замкнуты в `v[1..11]`. Результат упорядочен и сохраняет кратности. | `U64-S9-B01-L09-BITS` (4/4 covers)<br>`f7d5bf7f80cf4eca3f1f000f4f92a5e760ca4c036cfee1e68a426b66fbc9f4b1`<br>`417dd157952fb184de5affd6dc2a4f5a2732615955253c10234464bf0c01959f`<br>`U64-N13-SWAP` (5/5 covers)<br>`91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11`<br>`48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc`<br>`U64-B01-INSERT-REL9` (6/6 covers)<br>`2bbaf726683c45083a304ef9c63286b315a71381568d4ed652b1af081bafb668`<br>`3b3ed2f328bd7e0a13a3eccd1387913e27ff6b3e83febad94394a5d6cc825cee` |
| Правая половина `v[11..21]` | Полные слова B11, rel0–8. Native bit post/frame на `rev2_u64_n20_n21.rs:37/38/43:5`, swap min/max/frame на `:66/67/72:5`. Перенос L11→L10 сохраняет guard и все доступы rel0–8. Исключённое abs21 остаётся в том же V34 и за пределами чтений sort9. Rel9 на `:132/141:5` вставляет abs20. Записи замкнуты в `v[11..21]`. Результат упорядочен и сохраняет кратности. | `U64-S9-B11-L11-BITS` (4/4 covers)<br>`8ad93744bfc2021b7fcb6d85e8142ddae70184634a717d57c1cccd241dc84b8f`<br>`a8bb7325ba400b6993062aba8250d519bf964e011c2a0e4faec5c919fdb8ab06`<br>`U64-S9-B11-SWAP` (5/5 covers)<br>`74c2538696912deb8c6e1a2b820810c672aed341844843920141e1628f7882f2`<br>`8c8bd1daa54d01294ae6c782564a36d846095513ef52b458fdfbfa7bad9934f9`<br>`U64-B11-INSERT-REL9` (6/6 covers)<br>`b75cabbd682c71556ef02073a68680e5ea57461643bb104188ab75fecb1776a2`<br>`fb4d448ec979f980c3a9c246b08bb5b11c197983034a500a5ba079e9ecec4a45` |
| Merge и курсоры | Две упорядоченные половины по 10, separate D32, `k=0..9`. Check `actual_pair_step_n20` на `rev2_u64_n20_n21.rs:153:1` и `:159:5` закрепляет два назначения D и source frame. Успешные cursor posts `:181/191:9`, read/write/disjoint/value/frame `:209/213/217/242/243/244:5`. Копии actual `885:9` и `918:9`. После десяти пар записаны все `D[0..20]` в ранговом порядке и обе пары cursor ends совпадают. | `U64-N20-PAIR-STEP` (10/10 covers)<br>`6616fc4d9dc9fd24c8c595481e8fe8cdad6b1f4ecc27e8032e3e307542b1e315`<br>`e053e86fd17584b0623b183188da6153d4603565ad197382988b0b1312d96e10` |
| Copy-back и frame | После merge `D[0..20]` инициализирован по внешнему выводу. Actual `425:9` копирует 160 байтов из D в V34 по байтовому диапазону `[8,168)`. Локальная копия `102:14` проверяет равенство, сохранность префикса и frame `v[0]`, `v[21..34]`. Actual возврат закреплён контрольным cover. | `U64-N20-COPY-BACK-FRAME` и `U64-N20-WITNESS-CORRUPT` в замороженном roster. Native receipts и projections открыты. |

### Рёбра N21

| Ребро | Предпосылки, режим и вывод на фактических вызовах | Нативные опоры и хэши |
| --- | --- | --- |
| Левая половина `v[1..11]` | Произвольные слова B01, rel0–8. Sort9 на abs1–9, native каноничность, маска и frame на `rev2_u64_n18_n19.rs:389/390/395:5`. Swap B01 min/max/frame на `rev2_u64_n13.rs:35/36/42:5`, сужение `b<13` до `b<9`. Перенос L09→L10 сохраняет произвольное abs10. Rel9 вставляет abs10 в отсортированные abs1–9. Точное отображение/frame на `rev2_u64_n20_n21.rs:132/141:5`. Записи замкнуты в `v[1..11]`. Результат упорядочен и сохраняет кратности. | `U64-S9-B01-L09-BITS` (4/4 covers)<br>`f7d5bf7f80cf4eca3f1f000f4f92a5e760ca4c036cfee1e68a426b66fbc9f4b1`<br>`417dd157952fb184de5affd6dc2a4f5a2732615955253c10234464bf0c01959f`<br>`U64-N13-SWAP` (5/5 covers)<br>`91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11`<br>`48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc`<br>`U64-B01-INSERT-REL9` (6/6 covers)<br>`2bbaf726683c45083a304ef9c63286b315a71381568d4ed652b1af081bafb668`<br>`3b3ed2f328bd7e0a13a3eccd1387913e27ff6b3e83febad94394a5d6cc825cee` |
| Правая половина `v[11..22]` | Полные слова B11, rel0–8. Native bit post/frame на `rev2_u64_n20_n21.rs:37/38/43:5`, swap min/max/frame на `:66/67/72:5`. Геометрия exact L11. Rel9 вставляет abs20 и сохраняет abs21, давая предусловие для rel10. Rel10 вставляет abs21. У обеих вставок точное отображение/frame на `:132/141:5`. Записи замкнуты в `v[11..22]`. Результат упорядочен и сохраняет кратности. | `U64-S9-B11-L11-BITS` (4/4 covers)<br>`8ad93744bfc2021b7fcb6d85e8142ddae70184634a717d57c1cccd241dc84b8f`<br>`a8bb7325ba400b6993062aba8250d519bf964e011c2a0e4faec5c919fdb8ab06`<br>`U64-S9-B11-SWAP` (5/5 covers)<br>`74c2538696912deb8c6e1a2b820810c672aed341844843920141e1628f7882f2`<br>`8c8bd1daa54d01294ae6c782564a36d846095513ef52b458fdfbfa7bad9934f9`<br>`U64-B11-INSERT-REL9` (6/6 covers)<br>`b75cabbd682c71556ef02073a68680e5ea57461643bb104188ab75fecb1776a2`<br>`fb4d448ec979f980c3a9c246b08bb5b11c197983034a500a5ba079e9ecec4a45`<br>`U64-B11-INSERT-REL10` (6/6 covers)<br>`28abbf68a45a302c446e7e6342036220e118656b1068832a7fe7acbc81a0a511`<br>`87abe31094d26c4a10c5b01cb255597648486e6f5262a80065859ba2d943fd95` |
| Merge и курсоры | Отсортированные половины 10+11, separate D32, `k=0..9`. Check `actual_pair_step_n21` на `rev2_u64_n20_n21.rs:256:1` и `:262:5`. Курсоры `:284/294:9`, прикладные и функциональные посты `:312/316/320/345/346/347:5`. Actual копии `885:9` и `918:9`. Check `actual_odd_center_n21` на `:359:1` и `:365:5` воспроизводит actual `1027–1036` с typed copy на `:386:9`. Посты адреса, одного слова, двух концов и frame на `:402/406/410/428/429/430/434/438:5`, covers обеих сторон, sentinel и return на `:439–442:5`. Десять пар и центр пишут `D[0..21]` в ранговом порядке. | `U64-N21-PAIR-STEP` (10/10 covers)<br>`61dde0ca7230af83adb149e71570462b17d5ca68234badfd2125c41b9043bbb1`<br>`a73dd7983947df415f9dffb9b64a8c8fa1819dcaa9aa52df9b4eb440a418f3cd`<br>`U64-N21-ODD-CENTER` (4/4 covers)<br>`f5c6944aeae0594f27992c0f80e0ffb2135fc475bd84d3b2b9cab738a1bc7069`<br>`e57ea4b2c467a614b6650a535e57ca597e6e9b1271c7ab9dfdb6fd5de39a376d` |
| Copy-back и frame | После merge `D[0..21]` инициализирован по внешнему выводу. Actual `425:9` копирует 168 байтов из D в V34 по байтовому диапазону `[8,176)`. Локальная копия `102:14` проверяет равенство, сохранность префикса и frame `v[0]`, `v[22..34]`. Actual возврат закреплён контрольным cover. | `U64-N21-COPY-BACK-FRAME` и `U64-N21-WITNESS-CORRUPT` в замороженном roster. Native receipts и projections открыты. |

### Половины и полноширинный пост

Обозначим `S=&v[1]`, `D` — начало отдельного scratch. Цикл `smallsort.rs:394–417` выбирает sort9 при длине региона 10 или 11. Сеть использует те же 25 упорядоченных пар с индексами rel0–8 и тот же `u64_less` для каждой пары. Изменение длины при фиксированной базе сохраняет истинность guard `len>=9` и все рабочие адреса. У левого переноса слово abs10 произвольно и сохраняется всеми swap. У правого сужения до L10 abs21 в V34 сохраняется и никогда не читается сетью. Swap B01 и B11 задают полноширинные min/max и frame двух адресов.

Для порога `t` проекция `[word >= t]` коммутирует с каждым min/max как AND/OR. Поэтому каждая пороговая маска полной сети равна результату той же bit-сети на соответствующей входной маске. Нативный битовый пост для всех 512 масок даёт каноническую отсортированную маску и сохраняет число единиц `C(t)`. Инверсия `x > y` оставила бы 1 перед 0 при `t=x`. Кратность значения `t < u64::MAX` равна `C(t)−C(t+1)`, а для `u64::MAX` равна `C(u64::MAX)`. Каждый min/max также сохраняет локальное мультимножество пары.

Для `R=9/10` tail `x=v[B+R]` вставляется в отсортированный префикс длины `R`. Число его элементов `<=x` даёт единственное `p`. Нативный пост оставляет элементы с `j<p`, пишет `x` на `p` и переносит исходный `j−1` в `j` при `p<j<=R`. Это сохраняет порядок и полное мультимножество. Driver передаёт фактические begin и tail по очереди, начиная с offset 9. Для правой N21 первое отображение сохраняет следующее полное tail-слово и замыкает предусловие для второго. Actual shift и gap-fill используют типизированные копии одного слова. Их anchors сверены на `722:13` и `362:13`. [Опоры вставок](REV2-U64-N20-N21-HANDOFF.md#вставки)

### Десять пар, остаток и конечная копия

Ранг каждого слова — `(полное значение, индекс после вставок)`. В каждой половине ранги возрастают строго. На равных значениях up выбирает левый источник, а down правый. Значит, они снимают меньший и больший ранг из своих кандидатов. Перед каждой парой `0<=k<10` прямой обход потребил `a+b=k`, обратный `c+d=k`. В каждом из этих двух обходов обе половины ещё содержат кандидата, поскольку их длина не меньше 10. Actual адреса чтения относительно S равны `a,10+b` для up и `9−c,N−1−d` для down. Первые два принадлежат соответственно диапазонам `0..9` и `10..19`, последние два диапазонам `0..9` и `N−10..N−1`, включительно. Адреса записей `D[k]` и `D[N−1−k]` различны и лежат в отдельном D32. Check проверяет эти предусловия на фактических up/down, точные значения, приращения курсоров и frame источника.

Индукция отдельно по каждому обходу даёт ранги `0..9` в прямом порядке и `N−1..N−10` в обратном. Эти множества раздельны даже при совпадении значений, поэтому ни один ранг не копируется дважды. Первые десять и последние десять записей имеют точные непересекающиеся выходные диапазоны. Ранги в каждом выходном диапазоне возрастают по индексу назначения.

После пар forward равны `(S+a,S+10+b)`, reverse `(S+9−c,S+N−1−d)`, а после `wrapping_add(1)` концы равны `(S+10−c,S+N−d)`. Для N20 полное ранговое покрытие даёт `a+c=b+d=10`. Тогда `a=10−c` и `10+b=20−d`, и обе проверки `:1042` проходят.

Для N21 один ранг остаётся между обходами. Если он слева, `a+c=9` и `b+d=11`. Сравнение `left < left_end` истинно, центр копирует `S+a` в `D[10]`, а после инкремента `a+1=10−c` и `10+b=21−d`. Если остаток справа, `a+c=10` и `b+d=10`. Сравнение ложно, центр копирует `S+10+b`, затем `a=10−c` и `10+b+1=21−d`. При `c=10` reverse слева равен `S−1` после wrapping. `wrapping_add(1)` возвращает S. Sentinel не разыменовывается. N21 Check подтверждает оба адресных случая, cursor posts и отдельный cover sentinel. Две ветки actual центра на `:1027–1036` совпадают с Check по условию, чтению, записи и продвижению курсоров.

Десять пар и, для N21, центр дают запись каждого слова `D[0..N]` из инициализированного S. Это внешний вывод при `uninit=OFF`. После `:1042` actual `:425:9` копирует `count=N` в `v[1..1+N]` и возвращается. Аллокации V34 и scratch32 живые и раздельные, размеры 272/256 байтов, выравнивание 8. Диапазоны копии от начала аллокаций составляют `[0,160)` → `[8,168)` для N20 и `[0,168)` → `[8,176)` для N21. Slot локальной копии заранее записывает независимые произвольные N слов в scratch и выполняет единственный `ptr::copy_nonoverlapping::<u64>` той же геометрии. Остаток scratch не читается. Объединение write sets sort9, вставок, отдельного scratch и последней копии сохраняет внешний frame. Cover возврата из actual сети и исходный порядок вызовов связывают grouped copy properties с `:425` при полном unwind. Cover локального корня стоит за тремя постами и относится к единственному typed copy. [Фактический runtime](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:367)

## Контрольные трассы

Фиксированный `0x0000_0401` ставит единицы на S+0 и S+10. На каждой половине фактические 25 пар двигают единицу по rel0 → rel3 → rel8. Левая вставка и первая правая делают по одному сдвигу. Вторая правая N21 делает ещё один. Каждая отсортированная половина заканчивается единицей. Колонки up/down перечисляют смещения читаемых слов от S в порядке десяти пар.

| Длина | Up | Down | Центр и конечные курсоры | До → после порчи |
| --- | --- | --- | --- | --- |
| N20 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 10 | 19, 9, 18, 17, 16, 15, 14, 13, 12, 11 | `(a,b,c,d)=(9,1,1,9)`. Forward и reverse ends совпадают на `(S+9,S+11)`. | `0x000c_0000 → 0x000c_0001` |
| N21 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 10 | 20, 9, 19, 18, 17, 16, 15, 14, 13, 12 | `(a,b,c,d)=(9,1,1,9)`. До центра forward `(S+9,S+11)`, reverse ends `(S+9,S+12)`. Ветка справа читает `S+11`, после инкремента оба равенства проходят. | `0x0018_0000 → 0x0018_0001` |

После actual возврата оба корня вычисляют один и тот же оракул по исходному popcount и применяют `observe_bits` до и после `v[1] ^= 1u64`. До порчи проходят каноничность и ожидаемая маска. После порчи каноничность и V34 frame проходят, а маска расходится с ожидаемой ровно в младшем бите. Остаток слева и wrapping sentinel принадлежат отдельному Check с covers. Фиксированный свидетель N21 проходит правый остаток. [Контроль](/root/verify-rust-std-rev2-u64-n20-n21-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n20_n21_consumer.rs:37)

## Проверка unwind 36

| Цикл или операция | N20 | N21 | Привязка |
| --- | ---: | ---: | --- |
| Инициализация битового входа | 20 | 21 | `0..N` на consumer :39, `u32` shift и конверсия в одно `u64`. |
| Каноничность и маска, каждый из двух вызовов | 20 | 21 | `0..N` на consumer :69. Два отдельных обхода на :50 и :57. |
| Скалярный V34 frame | 34 | 34 | `0..34` на consumer :79 даёт максимум 35 проверок диапазона. Сравнения `u64 == u64` выполняются на индексах 0 и `i>N`, всего 14/13. |
| Запись scratch prefix | 20 | 21 | `0..N` на consumer :94 с одной typed записью. |
| Чтение copy-back и source prefix постов | 20 | 21 | `0..N` на consumer :106 с двумя скалярными сравнениями на итерацию. |
| Presort regions | 2 | 2 | `smallsort.rs:394–417`, первый регион у S, второй у S+10. |
| Sort9 | 0 | 0 | По 25 явно записанных swap на регион, guard и leaf без цикла. |
| Insertion driver | 1 слева, 1 справа | 1 слева, 2 справа | `offset=9`, `len=10/11`, tail идёт до one-past на `:762–768`. |
| Тело actual `insert_tail` на вызов | ≤9 | ≤9 для rel9, ≤10 для rel10 | `:718–734`, sift убывает от `tail−1` до begin. Для свидетеля каждый вызов делает один сдвиг. |
| Merge pairs | 10 | 10 | `0..(N/2)` на `:1022`, up/down без цикла и с `count=1`. Центр N21 содержит один typed copy. |
| Symbolic arrays и popcount | 0 | 0 | Kani `Arbitrary<[T;N]>` делегирует `T::any_array`, специализация `u64` через `any_raw_array` в `library/kani_core/src/arbitrary.rs:33–45,68,125–132`. CTPOP `u32` скомпилирован как CBMC popcount. |
| Снимок, slices и typed copies | 0 | 0 | Снимок копирует значение массива. Индексация проверяет границы, `Range::next` делает скалярный шаг. `memcpy` моделируется `array_copy/array_replace`. Сравнения массивов и срезов, которые приводят к `memcmp`, отсутствуют. |

Литеральные специализации N20/N21 и размеры V34/D32 ограничивают все явные циклы. Наибольшая граница 34 итерации и 35 проверок диапазона укладывается в unwind36. Native SUCCESS всех выведенных unwind properties остаётся условием принятия слота.

## Ubuntu job, argv и сроки

Одна `ubuntu-24.04` X64 job с пределом 95 мин. Stock Kani использует CBMC 6.11.0/CaDiCaL, OB12, unwind36. Safety, overflow, unwind, undefined-function и assertion-reach ON. Uninit и validity OFF. Все четыре роли без stubs, Replace и loop contracts. CWD, Cargo/Kani targets, tmp и export отдельные и холодные для каждого слота. `KANI_JOBS=1`, `CARGO_TARGET_DIR=$slot/cargo-target`, `TMPDIR=TMP=TEMP=$slot/tmp`. Точный порядок 24 cfg зафиксирован в roster.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Prepare собирает закреплённый tool и выполняет cfg-on compile preflight до обоих list. Preflight использует `verify-std` с теми же verify `-Z` без export-json, `--no-assert-contracts --no-codegen --only-codegen --quiet --target-dir "$preflight/kani-target" "$std/library"`, отдельный предел 180 с и запись первых rustc diagnostics при отказе. Затем дважды выполняется `"$tool/scripts/kani" list -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing "$std/library" --std --format json` с изолированными каталогами и с новым cfg выключенным/включённым. [Frozen runner](/root/kani-rev2-u64-n20-n21-consumer-trigger-w15/control/ch8-cal1/run.py:345)

| Стадия | Граница от старта job | Окно |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Measure identity gate | 55:00 | До 60 с от входа в measure |
| Четыре последовательных слота | 68:40 | По 205 с, включая cold 180 с, reap 10 с, receipt 5 с, запас старта 10 с |
| Финальная аттестация | 70:40 | Measure 16:45 внутренний, 18 мин внешний |
| Finish и upload-gate | 75:35 | 6 и 1 мин внешние |
| Upload | 82:40 | 7 мин |
| План с резервом 6 мин | 88:40 | 95 мин job |

На корень 120 с VT, 4 GiB группового RSS и 180 с cold wall. Резерв ОС 2 GiB. Ведутся VT, cold wall, group/CBMC RSS, доступные PSS, последняя фаза и первая CNF. Суммирование RSS в Linux неатомарно, разделяемые страницы могут учитываться дважды, а смена TID может редко дать недоучёт. До проекции сохраняется checkpoint исхода и reap. При неподтверждённом reap следующие слоты пропускаются. Повтор записи receipt ограничен и сохраняет признак опоздания. Caps составляют 4 MiB на projection и 96 MiB на артефакт.

`U64_N20_N21_COMPOSITE_WITHIN_PROFILE` требует четырёх `MATCHED`, полных своевременных receipts/projections, обязательных covers, подтверждённых sampler/reap, соблюдения трёх лимитов и своевременной аттестации `COMPLETE`. `witness_controls` и `copy_back_frames` показывают статусы для каждой длины. Диагноз относится к нативным слотам. Внешние рёбра и исследовательский допуск рассматриваются на ревью. [Отчёт](/root/kani-rev2-u64-n20-n21-consumer-trigger-w15/control/ch8-cal1/report.py)

## Локальная валидация

- Закреплённый `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max` применён до заморозки координат. SHA-256 бинарника `0cb21861860ae07c03b7097b099ea3e28dfb3857a9b09acce0df6b165f25cc70`. Для registration diff сверены форматированные виды базы и overlay. Проверены видимость, check-cfg, побайтное восстановление registry/manifest после снятия добавлений, побайтное совпадение runtime и контрактов, TOML, YAML, восемь блоков `bash -n`, Python syntax и `git diff --check`.
- Локальный bare shallow checkout depth 2 без alternates проверил и распаковал bundle. HEAD, refs и shallow boundary сохранились. Source gate проверил 26 пар commit/tree/parent, 27 source blobs, 668 координат и точные Check/Proof anchors. В этой симуляции полная recursive identity submodules была заменена заглушкой.
- Сверены реальные 25 пар, все 512 масок на B01/L09, B01/L10, B11/L11 и B11/L10, три модели вставки (12 012, 12 012 и 18 018 случаев) и 385 cursor-геометрий для каждой длины. Перебраны 184 756 и 352 716 ранговых чередований и все 21 состояния odd center. Отдельно проверены обе трассы свидетелей. Исторические 10 projections пересопоставлены с regular/stock и сохранёнными хэшами.
- Exact detached review-trigger принял `pins`, `finish`, `upload-gate` и `upload-check` на синтетическом payload и дал ровно четыре `NOT_STARTED` receipts. Подменённые tree/payload отклонены `pins/sources/finish/upload-gate`. Подменённый admission receipt отклонён `sources/finish/upload-gate`. Check пропустил upload до отсечки и отклонил его после +4960,01 с. Пропуск гейта после +4535,01 с отклонён.
- Синтетика проверила чужие selector/kind/file/target, потерю post/copy/return anchor и unwind, второй FAILURE, выход за профиль, late receipt, потерю reap/attestation, подмену схемы или inventory и позднюю публикацию. Blob `test_supervisor.py` в Control и trigger равен `df63a457c3adf648d360f3d559d5d40ef00a9427`.

| Шкала monotonic | Suite | Время |
| --- | ---: | ---: |
| Обычная | 129/129 | 55,649 с |
| Свежая со старта 1 с | 129/129 | 45,963 с |
| Свежая со старта 5 с | 129/129 | 42,415 с |
| Свежая со старта 60 с | 129/129 | 42,621 с |

Четыре suites из exact review-trigger выполнены последовательно за 193,769 с вместе с `pins`, в пределах 480 с. Std, Control, review-trigger и g0 записаны от `Tiramisu-Cake <igkharin@gmail.com>` с `[skip ci]`.

Открытые предпосылки стадии: независимое ревью композиции и проверка стыковки оснований, отдельный GO координатора, нативная recursive identity в Ubuntu, cfg-on compile preflight/discovery, реальные исходы, ресурсы и аттестация четырёх слотов. Локальная подготовка выполнена без Cargo, rustc, Kani, CBMC, CI, push и изменения Actions variables.
