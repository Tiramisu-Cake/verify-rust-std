# REV2 · диагностический пакет `u64` N14–N17

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE` · Item 2.** Пакет содержит полноширинный шаг вставки, сквозной битовый N17 и по одному контролю порчи на длину. Он готов к независимому ревью исходников, привязок и Control. Отдельный GO координатора нужен перед публикацией и запуском. Compile preflight, фактический discovery и нативные исходы остаются открытыми. [Задание w13](REV2-U64-N14-N17-TASK.md) · [Утверждённый допуск N13](REV2-U64-N13-ADMISSION.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Worktrees и пины

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n14-n17-w13), `work/rev2-u64-n14-n17-std-w13` | `53e733666ede6b256c84498a6dd350f1e84dddfb` | `b1d2c899753acd6e137e9c10e153270f30a65846` | `4d6dd509956dff820a596ff1af9c0aae347aca26` |
| [Control](/root/kani-rev2-u64-n14-n17-control-w13), `work/rev2-u64-n14-n17-control-w13` | `e51c10547ddd19f1f63ec324cd1ee31fbf0c57c9` | `fe9dfbd9a9670cc435190210578d68fa7e363f4e` | `ed62c6a5c94bc2b676d2b9cdb698fcbc7dc3ad79` |
| [Review-trigger](/root/kani-rev2-u64-n14-n17-trigger-w13-final/control), detached, ref `review/rev2-u64-n14-n17-trigger-w13` | `7939187d40749281fb69f480172c9cc08650c246` | `fe9dfbd9a9670cc435190210578d68fa7e363f4e` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std FIX1 base tree — `b0dc6d628690b7bc58225e2f60503ed4f8ae32b3`, Control FIX1 base tree — `71b1cbd433b47a9ccc6a26ef33aa1f8e2c6c9a7b`. Загрузочная база Std bundle — `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Bundle объявляет только Std `HEAD` и содержит 22 проверенных ребра commit/tree/sole parent от загрузочной базы. Stock Kani — `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`.

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n14-n17-control-w13/ch8-cal1/CI-REQUEST.json) | `6bf1706f6f3ebb958bd7795b33ff24a07b2796088187b1414044b87b1b929b5e` |
| Exact roster, канонический JSON | `1e76eb9fb3386a1b1649152c4a1dc18764f4ae9ea316730dcb8fcbf925af055d` |
| Source bindings, канонический JSON | `36c08ae35032db55e739bcd0a2c2060e7f6ac14c9f92ca36bd932aa88b93f692` |
| [std-overlay.bundle](/root/kani-rev2-u64-n14-n17-control-w13/ch8-cal1/std-overlay.bundle), 60 067 байт | `fbac6f36fd0f91394166d8d52ae402ce013f3b8a83060e881bfbcb319fe75680` |

| Исходник | Git blob |
| --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `verify/rev2_u64_n14_n17.rs` | `0a23131ac174f4f7b6793823e49336c69397091f` |
| `verify/rev2_u64_n13.rs` с `pub(super)` | `47c129a11d6cd0d0adce0be450b91eca84a25c0c` |
| `verify/rev2_u64_n13.rs` в исторической привязке FIX1 | `6658b28d64647aa6e11c5bee3c71a135f09b2a6c` |
| `smallsort/verify.rs` | `b033355451a93e58866ba2038a69386da947b613` |
| `core/Cargo.toml` | `4494836165c05638f1f0cb1705e2bc9e7b128ee8` |

Std delta состоит из нового модуля, его регистрации и check-cfg, а также видимости `u64_less`. Удаление добавленного `pub(super) ` побайтно восстанавливает исторический blob N13. Тело, function item и cover `9:5` сохранены. Гейт нового модуля требует флаги N13 и N14–N17 внутри существующего `cfg(kani)`. Это делает зависимость компаратора явной, а комбинацию «только новый флаг» оставляет без новых корней. Удаление двух новых строк регистрации и строки check-cfg восстанавливает прежние файлы. Runtime и контракты побайтно совпадают со Std FIX1. [Гейт исходников](/root/kani-rev2-u64-n14-n17-control-w13/ch8-cal1/request.py)

## Полноширинный шаг вставки

Корень берёт произвольный инициализированный `[u64; 34]`. Снимок `before` содержит исходные значения. При `S=&v[1]`, `13≤r≤16` и `x=before[1+r]` предусловия проверяют числовой порядок префикса `v[1..1+r]` и разбиение относительно `x`. Для `j<p` требуется `before[1+j]≤x`, для `p≤j<r` требуется `x<before[1+j]`. У любого отсортированного префикса и любого `x` элементы `≤x` составляют начальный отрезок. Его длина и есть единственный `p∈0..=r`, включая пустой и полный отрезок. При наличии равных элементов место вставки находится после них. Хвост, frame и значения в полном диапазоне `u64` сохраняют произвольность. [Предусловия](/root/verify-rust-std-rev2-u64-n14-n17-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n14_n17.rs:9)

Actual `insert_tail::<u64,_>` вызывается на `S` и `S.add(r)` из живого среза `v[1..2+r]`. Проверяемый пост отображает относительный `j<p` в прежний `j`, `j=p` в `x`, а `p<j≤r` в прежний `j−1`. Прежние `r` элементов встречаются по одному разу в том же порядке, дополнительно встречается `x`. Вместе с разбиением эта карта даёт порядок и точные кратности, включая дубликаты. Отдельный frame проверяет `v[0]` и все `v[i]` для `2+r≤i<34`. Каждое равенство сравнивает одно полное слово. [Actual вызов и посты](/root/verify-rust-std-rev2-u64-n14-n17-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n14_n17.rs:34)

При `p=r` компаратор на `smallsort.rs:706` даёт false и ветка на `:707` возвращается без сдвига. При `0<p<r` каждый из `r−p` правых элементов сдвигается, после чего `:731` останавливается на предшественнике `≤x`. У cover `AFTER_EQUAL` выражение `before[p]==x` проверяет абсолютный индекс предшественника, относительный `p−1`. Для `r=16,p=0` выполняются 16 сдвигов, включая последний перенос из `begin`, и выход по `:725`. Четыре covers `REL13..REL16` проходят под теми же предпосылками. Cover компаратора срабатывает внутри actual function item. Итоговый cover расположен после обоих постов. [Ветки вставки](/root/verify-rust-std-rev2-u64-n14-n17-w13/library/core/src/slice/sort/shared/smallsort.rs:701)

| Safety-группа | Исходная координата | Связь с операцией |
| --- | --- | --- |
| `shift` | `smallsort.rs:722:13` | Перенос одного `u64` из `sift` в соседний `gap_guard.dst`. Адреса различаются на 8 байт, обе области выровнены и находятся внутри V34. `:723` передвигает зазор в `sift`. |
| `gap_fill` | `smallsort.rs:362:13` | `CopyOnDrop::drop` переносит одно слово из отдельного живого `tmp` в конечный зазор. `:715–716` читают хвост в `tmp` и создают guard с `len=1`. |
| `ptr_wrapper` | `core/src/ptr/mod.rs:587:14` | Общая нативная координата intrinsic для `ptr::copy_nonoverlapping::<u64>`. |

Инициализация следует из actual чтения хвоста и последовательности записей. Внутри цикла читается ещё инициализированный предшественник, сдвиг заполняет текущий зазор, guard заполняет последний зазор из инициализированного `tmp`. Ранний возврат сохраняет исходную инициализацию. Этот аргумент по исходнику учитывает `uninit=OFF`. Control требует успешные нативные группы выравнивания src/dst, размера в байтах, непересечения, читаемости и записываемости. В receipt отдельно сохраняются regular ID, класс, статус и нативная координата. ID на общей координате wrapper сохраняют общую атрибуцию даже при пустых списках двух caller-координат. Конкретные ID и то, выдаст ли Kani отдельные caller-координаты, устанавливаются на прогоне. [Обёртка ptr](/root/verify-rust-std-rev2-u64-n14-n17-w13/library/core/src/ptr/mod.rs:587) · [Привязка в проекции](/root/kani-rev2-u64-n14-n17-control-w13/ch8-cal1/results.py)

## Композиция на четырёх длинах

На `small_sort_network` для N14–N17 условие `len<18` истинно, регион имеет длину `N` и базу B01. Guard `region.len()>=13` на `smallsort.rs:395` и внутренний guard S13 на `:601` допускают actual вызов на `:396`. База `:605`, 45 пар `:612–656` и тот же `u64_less` совпадают с N13. `U64-N13-SWAP` даёт min/max и frame для каждой пары, включая хвост N14–N17. Для каждого порога `t` отображение `x≥t` коммутирует с min/max, поэтому `U64-N13-S13-BITS` переносит порядок на полные слова. Сохранение значений в каждой паре даёт кратности, а frame каждой пары оставляет все позиции вне rel0..12 прежними. [Допуск N13](REV2-U64-N13-ADMISSION.md#перенос-на-полные-u64-и-фактический-маршрут) · [Actual S13](/root/verify-rust-std-rev2-u64-n14-n17-w13/library/core/src/slice/sort/shared/smallsort.rs:597)

Вызов driver на `:405` получает offset 13 и ту же базу. На `:759–761` его `v_end=S.add(N)`, `tail=S.add(13)`. На `:764` указатель шага равен `S.add(r)`, на `:767` он продвигается на один. Префикс длины `r` перед каждым шагом отсортирован предыдущей опорой, следующий элемент сохранился по frame. Поэтому для текущего префикса применим единственный `p` из полноширинного шага. Лист использует живой префикс того же backing, а диапазон записей выводится из базы и указателя шага. После последнего шага `tail==v_end`, `:407–408` возвращают управление до merge и copy-back. [Actual driver](/root/verify-rust-std-rev2-u64-n14-n17-w13/library/core/src/slice/sort/shared/smallsort.rs:742) · [Ветка сети](/root/verify-rust-std-rev2-u64-n14-n17-w13/library/core/src/slice/sort/shared/smallsort.rs:386)

| Длина | Actual вставки и длины отсортированных префиксов | Конечная область и неизменный внешний frame | Контроль `mask 1` |
| --- | --- | --- | --- |
| N14 | rel13, длины 13 → 14, `v_end=&v[15]` | `v[1..15]` численно отсортирован с исходными кратностями, сохранены `v[0]` и `v[15..34]` | `0x2000 → 0x2001` |
| N15 | rel13–14, длины 13 → 14 → 15, `v_end=&v[16]` | `v[1..16]` численно отсортирован с исходными кратностями, сохранены `v[0]` и `v[16..34]` | `0x4000 → 0x4001` |
| N16 | rel13–15, длины 13 → 14 → 15 → 16, `v_end=&v[17]` | `v[1..17]` численно отсортирован с исходными кратностями, сохранены `v[0]` и `v[17..34]` | `0x8000 → 0x8001` |
| N17 | rel13–16, длины 13 → 14 → 15 → 16 → 17, `v_end=&v[18]` | `v[1..18]` численно отсортирован с исходными кратностями, сохранены `v[0]` и `v[18..34]` | `0x10000 → 0x10001` |

Полноширинные выводы таблицы условны на принятие общей нативной опоры и рёбер. Сквозной helper использует const `N` и фиксированный режим порчи от каждого корня. N17 positive отображает 17 независимых битов в полные `0u64/1u64`, с произвольными внешними словами. Общий пост сверяет скалярный frame, каноничность каждого выходного слова и маску `low ^ (low >> popcount(input_mask))`. Для `mask 1` S13 переносит единицу на rel12, затем каждый нулевой хвост вставляется при `p=r−1` и сдвигает единицу на одну позицию вправо. Cover `SHIFT_THROUGH_LAST_INSERT` проверяет достижимость этого входа, а связь с каждой вставкой следует из исходника. После actual возврата контроль меняет `v[1] ^= 1u64` перед общим оракулом. Изменяется младший бит выходной маски, каноничность и frame сохраняются. [Общий helper](/root/verify-rust-std-rev2-u64-n14-n17-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n14_n17.rs:94)

## Exact roster и координаты

Префикс каждого exact selector — `slice::sort::shared::smallsort::verify::rev2_u64_n14_n17::`. Все шесть — plain Proof, `copy_back=false`, без Check и Replace. Координаты корней относятся к `core/src/slice/sort/shared/smallsort/verify/rev2_u64_n14_n17.rs`.

| Слот | Суффикс exact selector | Root | Ожидаемые исход и exit | Latest start |
| --- | --- | --- | --- | --- |
| `U64-N14-N17-INSERT-STEP` | `u64_n14_n17_insert_step` | `9:1` | `VERIFIED`, 0 | 55:00 |
| `U64-N17-ACTUAL-BITS` | `u64_n17_actual_bits` | `62:1` | `VERIFIED`, 0 | 58:25 |
| `U64-N17-WITNESS-CORRUPT` | `u64_n17_witness_corrupt` | `68:1` | `FAILED`, 1 | 61:50 |
| `U64-N14-WITNESS-CORRUPT` | `u64_n14_witness_corrupt` | `74:1` | `FAILED`, 1 | 65:15 |
| `U64-N15-WITNESS-CORRUPT` | `u64_n15_witness_corrupt` | `80:1` | `FAILED`, 1 | 68:40 |
| `U64-N16-WITNESS-CORRUPT` | `u64_n16_witness_corrupt` | `86:1` | `FAILED`, 1 | 72:05 |

| Native label | Класс | Line:column и function |
| --- | --- | --- |
| `REV2_U64_N13_COMPARATOR_CALLED` | cover | `9:5`, `rev2_u64_n13.rs` и `rev2_u64_n13::u64_less` у всех шести |
| `REV2_U64_INSERT_REL13`, `REV2_U64_INSERT_REL14`, `REV2_U64_INSERT_REL15`, `REV2_U64_INSERT_REL16` | cover | `25:5`, `26:5`, `27:5`, `28:5` |
| `REV2_U64_INSERT_NO_SHIFT`, `REV2_U64_INSERT_INTERIOR`, `REV2_U64_INSERT_MAX_SHIFT`, `REV2_U64_INSERT_AFTER_EQUAL` | cover | `29:5`, `30:5`, `31:5`, `32:5` |
| `REV2_U64_INSERT_EXACT_MAPPING`, `REV2_U64_INSERT_V34_FRAME` | assertion | `50:5`, `56:5` |
| `REV2_U64_INSERT_RETURNED_AFTER_POSTS` | cover | `57:5` |
| `REV2_U64_ACTUAL_MIXED_INPUT`, `REV2_U64_ACTUAL_INPUT_INVERSION`, `REV2_U64_ACTUAL_SHIFT_THROUGH_LAST_INSERT`, `REV2_U64_ACTUAL_RETURNED` | cover | `102:5`, `103:5`, `105:5`, `109:5` |
| `REV2_U64_ACTUAL_V34_FRAME`, `REV2_U64_ACTUAL_CANONICAL_OUTPUT` | assertion | `118:5`, `125:5` |
| `REV2_U64_N14_ACTUAL_SORTED_POPCOUNT`, `REV2_U64_N15_ACTUAL_SORTED_POPCOUNT`, `REV2_U64_N16_ACTUAL_SORTED_POPCOUNT`, `REV2_U64_N17_ACTUAL_SORTED_POPCOUNT` | assertion | `129:13`, `132:13`, `135:13`, `138:13` |

Для меток `INSERT` native function — полный selector корня вставки. Для `ACTUAL` функция — тот же префикс с `check_network::<14>`, `::<15>`, `::<16>` или `::<17>` по слоту. Все 10 covers вставки и 5 covers каждого сквозного корня требуют `SATISFIED`. У каждого контроля требуется единственный `FAILURE` на его `SORTED_POPCOUNT` класса `assertion`, с совпадением regular/stock native ID. У остальных требуемых свойств ожидается `SUCCESS`. Гейт сверяет terminal verdict и exit, stock ID по доступным статусам и счётчики успешных checks. Все выведенные unwind assertions должны иметь `SUCCESS` при stock `unwinding=ON`. Отсутствие отдельных unwind properties допустимо после разрешения границ движком. [Exact roster и координаты](/root/kani-rev2-u64-n14-n17-control-w13/ch8-cal1/CI-REQUEST.json) · [Native гейт](/root/kani-rev2-u64-n14-n17-control-w13/ch8-cal1/results.py)

## Control и часы

Один job `ubuntu-24.04`, 100 мин. CBMC 6.11.0, CaDiCaL, OB12, unwind36, реальные тела с `--no-assert-contracts`. Safety, overflow, unwinding, undefined-function и assertion-reach включены, uninit и validity выключены. CWD каждого слота, targets и tmp разделены. `KANI_JOBS=1`, `CARGO_TARGET_DIR=$slot/cargo-target`, `TMPDIR=TMP=TEMP=$slot/tmp`. В `RUSTFLAGS` все флаги из frozen roster в заданном порядке, последним `--cfg=kani_smallsort_rev2_u64_n14_n17`. [Сборка argv и окружения](/root/kani-rev2-u64-n14-n17-control-w13/ch8-cal1/run.py)

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Prepare выполняет cfg-on compile preflight первым после сборки и аттестации stock tool и checkout overlay. Preflight использует те же `-Z` и `--no-assert-contracts`, добавляет `--no-codegen --only-codegen --quiet` и отдельный `--target-dir`. Предел 180 с, первые структурированные rustc diagnostics сохраняются при отказе. Discovery требует неизменные cfg-off записи по виду, selector, file и targets, закреплённые прежние Check targets, пустой `targets` у plain и ровно шесть новых plain поверх 97 исторических REV2. [Workflow](/root/kani-rev2-u64-n14-n17-control-w13/.github/workflows/ch8-q-pilot.yml)

| Стадия | Абсолютная граница от monotonic epoch | Внешний timeout |
| --- | --- | --- |
| Prepare | 54:00 | 56 мин |
| Входной gate measure | до 55:00 и до 60 с от входа | в measure |
| 6 окон по 205 с | latest starts из roster, конец 75:30 | measure 25 мин, внутренний 23:35 |
| Финальная аттестация | 77:30 | в measure |
| Finish и upload-gate | cutoff 82:25, finish до 5 мин от входа | 6 мин и 1 мин |
| Upload | до 89:30 | 7 мин |
| План с резервом 6 мин | 95:30 | job 100 мин |

Профиль слота требует VT ≤120 с, group RSS ≤4 GiB и cold wall ≤180 с. Supervisor держит системный резерв 2 GiB, 10 с на reap, 5 с на receipt и 10 с launch headroom. Измерение запускается в пределах absolute latest start, при раннем входе внутренний таймер может сдвинуть latest starts раньше. Перед проекцией атомарно сохраняется checkpoint нативного процесса и reap. При неподтверждённом reap оставшиеся слоты останавливаются. Deferred receipt журналируется и повторно пишется в ограниченном окне finish с исходным признаком опоздания. Caps проекции и артефакта 4/96 MiB. Linux sampler может недоучесть RSS при смене TID после выхода главного потока.

`CH8_REV2_U64_N14_N17_TRIGGER_TREE` ожидает tree Control `fe9dfbd9a9670cc435190210578d68fa7e363f4e`. `pins`, `sources` и `finish` проверяют fork `Tiramisu-Cake/kani`, push attempt 1, exact ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, совпадение SHA HEAD, `GITHUB_SHA` и `event.after`, единственного parent и чистого detached checkout. `sources` и `finish` сверяют admission receipt от `pins`. Успешный finish открывает upload-gate до общего cutoff. Local review-trigger содержит `[skip ci]`. Отдельное решение GO определяет публикуемый trigger. [Прецедент GO N13](REV2-U64-N13-GO.md)

`U64_N14_N17_WITHIN_PROFILE` требует ровно шесть ожидаемых исходов, `MATCHED`, полные опубликованные проекции и covers, соблюдение лимитов, своевременные receipts, reap и своевременную аттестацию `COMPLETE`. Наблюдаемый исход хранится отдельно от проекции. Неполная проекция положительного исхода даёт `INCOMPLETE` с сохранённым `observed_outcome`, а профиль роли остаётся `OPEN`. [Отчёт](/root/kani-rev2-u64-n14-n17-control-w13/ch8-cal1/report.py)

## Локальная сверка

- Rust visibility, cfg, побайтный runtime/contract diff и восстановление исторического blob N13 сверены статически. Прошли rustfmt `1.11.0-nightly (7189d39d9c 2026-10-22)` с сохранением порядка регистраций, TOML, YAML с уникальными ключами, восемь `bash -n`, 15 Python AST и `git diff --check`. Использован доступный локальный formatter. Компиляция закреплённым toolchain остаётся за Ubuntu preflight.
- Shallow depth 2 без alternates прошёл `bundle verify/list-heads/unbundle`; HEAD, refs и shallow boundary сохранены. Проверены 22 commit/tree/parent, 24 текущих blobs с их историческими привязками, 406 текстовых и 340 нативных якорей. Отклонены 52/52 сдвига столбца новых нативных координат и четыре отдельные подмены failure-метаданных.
- Офлайн-модель на извлечённых 45 actual парах S13 проверила все 131 072 битовые маски N17. Для каждой длины воспроизведены ожидаемая маска до и после порчи и один сдвиг на каждую actual вставку. Модель вставки проверила 12 100 сочетаний отсортированного префикса и вставляемого значения из `{0, 1, 2^63, u64::MAX}` с `r=13..16`, обе границы `p`, внутреннее равенство на каждой длине, точный пост, кратности и frame.
- Синтетический detached trigger принял `pins` при +2 с, `sources` при +30 с, `finish` при +4900 с, `upload-gate` при +4945 с и `upload-check` при +5370 с. Смещение на 0,01 с за cutoff, чужое дерево, payload, fork/ref/attempt и изменённый admission receipt отклонены. Локальная симуляция `sources` проверила чистые Git-пины и bundle, используя пропуск submodule-проверки только в синтетическом вызове. В индексе сверены 10 членов и шесть ролей `NOT_STARTED`/`OPEN`.
- `test_supervisor.py` в Control и review-trigger имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. На чистом финальном detached review-trigger последовательно прошли 127/127 тестов на обычной и на каждой из свежих шкал 1/5/60 с. Время 35,392 / 33,787 / 35,588 / 34,654 с соответственно. Синтетика покрывает extra selector/target, отсутствующий или сдвинутый anchor, второй отказ, неверный exit, late receipt, выход за профиль, потерю reap/attestation и позднюю публикацию.
- Std, Control и review-trigger имеют author и committer `Tiramisu-Cake <igkharin@gmail.com>`. Локальные действия ограничены Git, форматированием, статическими проверками и синтетикой. Cargo, rustc, Kani, CBMC, CI, push и обновление Actions variables отсутствуют.

## Открытые роли

- При отсечке insert-step полноширинный перенос остаётся открыт для всех четырёх длин. Нативная диагностика должна показать фазу и стоимость. Раздельные `r` с тем же постом возможны после отдельного решения.
- При отсечке битового N17 его сквозная роль остаётся открытой, даже при успешных составных опорах и контроле N17. Достаточность этих опор для отдельного допуска N17 решается офлайн с сохранением native исхода.
- Неполная проекция или поздний receipt оставляют соответствующую роль открытой. Потеря reap оставляет дальнейшие слоты `NOT_STARTED`. Потеря или опоздание финальной аттестации блокирует общий диагноз `WITHIN_PROFILE`. Контроль каждой длины остаётся самостоятельным свидетельством чувствительности оракула.
