# C3a: типы swap и функциональная корректность trait-входов

Дата: 28–29.10.2026 (MSK). Исходная точка: `beeafe7eda`, runtime и лейн от `0f5ad96dd9`.
Рабочая ветка: `experiment/kani-k1-c3types-20261028`.

## Область и исходные отзывы

Выполнены два выбранных направления из TASK-C3A, с приоритетом правок планировщика.
Это не закрытие всех замечаний Challenge 8. Прочитаны только тексты отзывов
feliperodri: [#576, 16 августа](https://github.com/model-checking/verify-rust-std/pull/576#pullrequestreview-4947412389),
[#576, 12 сентября](https://github.com/model-checking/verify-rust-std/pull/576#pullrequestreview-5188053006),
[#678, 13 сентября](https://github.com/model-checking/verify-rust-std/pull/678#pullrequestreview-5188832758).
Получение — GitHub API `/pulls/576/reviews` и `/pulls/678/reviews`; код PR и их ветки не открывались.
Сортированность и перестановка — разные обязательства. Safety, reachability и число Drop
не засчитываются как функциональная корректность.

## Инвентарь до изменений

Пути ниже относительно `library/core/src/slice/sort/shared/smallsort/`.
«Ordinary» здесь означает наличие в исходном наборе без `kani_smallsort_controls`,
а не новое подтверждение выполнения этих старых гармоник в C3a.

Шесть определений `small_sort` в `../smallsort.rs`:

| Тело | Определение | Выбор |
|---|---|---|
| S0 | Stable blanket default, строка 37 | !Freeze: insertion/fallback, порог 16 |
| S1 | Stable Freeze, строка 55 | general с переданным scratch, порог 32 |
| U0 | Unstable blanket default, строка 82 | !Freeze: fallback, порог 16 |
| U1 | Unstable Freeze, строка 97 | передача управления Freeze-trait; отдельной сортировки нет |
| F0 | Unstable Freeze default, строка 124 | general при `48*size <= 4096`, иначе fallback |
| F1 | Unstable Freeze+Copy, строка 157 | network, иначе general, иначе fallback по size/swap |

| Старое семейство | Типы и длины ordinary | Реальный вход, маршрут и тела | Утверждения / границы |
|---|---|---|---|
| `network::network_correctness_*` (`verify/network.rs:911–957,1023–1099`) | u8 N0..17; u64 N0..14, N15..17 opt-in | Unstable trait → U1 → F1 → network | Сортированность для всех перечисленных N. Полное мультимножество непосредственно в harness только N0..8; выше — структурная перестановка сети + отдельные проверки insertion, не цельная машинная теорема trait-маршрута. |
| `merge::general_stable_sorted_permutation_*` (`verify/merge.rs:808–978`) | u64 N0..12 и 16; u8 N0..13 и 16; остальные N13..15 opt-in по типу | bool: Stable trait S1 → general либо прямой general helper | Сортированность + полное value-probe мультимножество u8/u64. `bidirectional_merge` заменён verified stub; sort4/insertion реальные. |
| `correct::sorted_permutation_general_stable_u8_n14/n15` (`verify/correct.rs:149–199`) | u8 N14/15; u64 N15 opt-in | bool: Stable trait S1 либо прямой general | Сортированность + полное value-probe мультимножество; verified stubs insertion и merge; scratch 48. |
| `merge::fallback_sorted_permutation_*` (`verify/merge.rs:849–995`) | u8/u64 N0..7 и отдельно u8 N8; остальные реальные варианты N8..16 opt-in | Прямой fallback helper, **не trait-вход** | Сортированность + value-probe мультимножество, реальные тела insertion. |
| `correct::sorted_permutation_fallback_*` (`verify/correct.rs:7–57`) | u64 N8..16; u8 N9..16 | Прямой fallback helper, **не trait-вход** | Сортированность + value-probe мультимножество; verified stub insertion, включая ограничения переноса allocation-locality. |
| `network::network_safety_unstable_u64_n0_to17` (`verify/network.rs:74–104`) | u64 N0..17 | Прямой Freeze trait F1 → network | Произвольный читающий компаратор: safety/возврат, без correctness. |
| `network` type/length safety matrix (`verify/network.rs:220–430`) | В том числе DropValue(u8), размеры/ZST; Drop N0/1/2/7/8/15/16/17/31/32 | Stable/Unstable trait; Drop S1/U1/F0 | Safety и normal return. Для DropValue нет sortedness, permutation или drop-count assertion. |
| `merge::drop_route_properties`, PERM (`verify/merge.rs:1003–1220`) | opt-in DropTaggedValue: direct fallback/insertion N2/4/8; general/stable N2/4/8/16 | Stable S1 либо direct helpers, не весь unstable trait | Произвольный comparator. PERM сохраняет только число тегов; sibling считает N деструкторов. Нет сортированности или мультимножества полных (key,tag). |
| `network` mutating Cell (`verify/network.rs:526–624,1248–1295`) | Cell<TaggedKey>, N2..4 для теговых свойств; safety-матрица до 16 | Stable S0 / Unstable U0 и insertion helper | Компаратор меняет key. Сохраняются теги, есть cover перемещения; сортированность и полные значения не проверяются. |
| `assembly::safety_stable_unit_*` (`verify/assembly.rs:180–207`) | () N1/2/7/8/16/17/31/32 | Stable S1 | Safety/возврат; нет явных correctness assertions. |

Таким образом, перед правкой не было «сортированность + полное логическое мультимножество»
для Cell с неизменяющим компаратором и для Freeze non-Copy через trait-входы.
Прямой `UnstableSmallSortFreezeTypeImpl` имел safety-проверку, но не отдельный correctness oracle.
Cell<i32> отдельно представлен контрактом `swap_contract_cell_i32_n2`
(`verify/network.rs:1014`), не whole-sort correctness или dispatch safety matrix.

## Предикат swap

В существующую `smoke::predicate_efficient_swap_type_matrix` добавлены `u16=true`
и `[u8;9]=false`; имя и прежние элементы матрицы сохранены.
Вывод из `library/core/src/slice/sort/shared/smallsort.rs:953–955`:
`has_efficient_in_place_swap<T>() = size_of::<T>() <= 8`;
`size_of::<u16>()=2`, `size_of::<[u8;9]>()=9`, поэтому соответственно true и false.
Это проверка данной эвристики на типах, не generic-T theorem о поведении сортировки.

## Новые оракулы

`verify/types.rs` содержит `LogicalByte`, `Cell<u8>` и `#[repr(transparent)] DropKey(u8)`
с пустым `impl Drop`, без Copy и без interior mutability. Наличие Drop запрещает Copy
и отличает специализацию от Copy-типов; новые свойства счётчиков деструкторов не заявляются.
Компаратор читает `.get()`/поле
и сравнивает строгим `<`, не меняя аргументы. Каждое содержимое входа — произвольный u8.
Снимки — массивы логических u8, поэтому нет чтения padding или копирования non-Copy объектов.
Единственное значимое поле DropKey проверяется полностью; Cell проверяется по содержащемуся значению.
Произвольная проба u8 и равенство чисел её вхождений выражают мультимножество всех значений,
включая повторы. Нет assumptions на выход, verified/manual stubs или отсечения panic-путей.

Каждый `trait_properties<T,N>` недетерминированно выбирает Stable либо Unstable trait.
Для Cell это S0 и U0; для DropKey — S1 и U1→F0→general, так как `1*48 <= 4096`.
Scratch для stable — 48 элементов MaybeUninit. Пороги — Cell 16, DropKey general 32.
У всех нетривиальных N есть covers возврата после обоих assertions, несортированного входа
и одинаковых первых двух ключей; отдельно covers обоих trait-входов и выбранных длин.
При N0/N1 требования несортированности/повторов неприменимы.

Имена ниже имеют префикс `slice::sort::shared::smallsort::verify::types::`.

| Гармоника | Тип | Точные длины | Маршрут/тела | Итог |
|---|---|---|---|---|
| `sorted_permutation_traits_fallback_cell_u8_n0_to2` | Cell<u8> | 0,1,2 | Stable S0 и Unstable U0; insertion/fallback | ordinary |
| `sorted_permutation_traits_fallback_cell_u8_n7` | Cell<u8> | 7 | Stable S0 и Unstable U0; insertion/fallback | ordinary, 98.85 с |
| `sorted_permutation_traits_fallback_cell_u8_n7_to9` | Cell<u8> | 7,8,9 | Stable S0 и Unstable U0; insertion/fallback | opt-in, групповой timeout |
| `sorted_permutation_traits_general_drop_u8_n0_to2` | DropKey(u8) | 0,1,2 | Stable S1 и Unstable U1→F0; general | ordinary |
| `sorted_permutation_traits_general_drop_u8_n7_to9` | DropKey(u8) | 7,8,9 | Stable S1 и Unstable U1→F0; general, переход sort4 при N8 | opt-in, доказано за 349.69 с |

Opt-in controls (`cfg(kani_smallsort_controls)`):

- `control_sorted_permutation_traits_cell_drop_n0_to2`: тот же оракул на реальных trait-входах обоих типов, все N0/1/2;
- `reject_logical_sortedness_cell_n2`: реальный unstable sort [2,1], затем обмен результата;
  мультимножество сохранено, ожидается провал конкретно `output[i - 1] <= output[i]`;
- `reject_logical_permutation_drop_n2`: реальный unstable sort [1,0], затем замена второго значения
  нулём. [0,0] остаётся отсортированным; ожидается провал `count(input, probe) == count(output, probe)`.

Это контролируемые повреждения результата с общим оракулом; они проверяют способность
различить два класса ошибок, а не доказывают обнаружение любого runtime-мутанта.

## Измерения и бюджет

Только `k1g.sh`, `gcb-e2-standard-4`, kind measurement, agent k1-merge, 10 минут/гармоника,
jobs=1, swap off. Локально не запускались rustc/cargo/Kani/CBMC.
Предварительная оценка перед выбором длин: старые modular fallback N8/N9 с verified insertion
в сборке `1e932304-105e-4f26-9556-e3b9c2b63dde` занимали 53.36/57.61 с;
N16 — 243.74 с (u8) / 300.74 с (u64). Это другой домен и stubs, не прогноз результата
реального Cell/Drop. Потому первый пакет — N0/1/2 и переход 7/8/9, четыре гармоники.

Резерв measurement-сборки: `$0.0135 * (30 + 10*H)`.
Первый H=4: $0.945. Лимит задания — $1.50 и три сборки; продолжение только после учёта
фактического расхода завершённых сборок и резерва следующей.
Начальный общий ledger: 63 builds, used $36.7575, unfinished reserve $0; общий cap $43.96.
Это общий проектный ledger, а не расход C3a.
Промежуточный ledger перед завершением первого опыта: 66 builds, used $36.9870,
reserve $0.9450. Два других завершённых запуска объясняют рост общего used на $0.2295;
эту разницу C3a не присваивает.

`k1g.sh` допускает только буквы в имени ветки между `kani-k1-` и датой;
имя задания `c3types` не проходит regex. Для dispatch опубликован alias
`experiment/kani-k1-ctypes-20261028` на том же commit. Основная ветка задания не переименована,
лейн не менялся, submission-ветки не затронуты. Отказ проверки имени сборку не создал.

### Сборка 1 — `2f10637a-a1d4-420f-ab5c-7eae9ecb8d97`

Commit `8003d40abe12b3cfdc48729f060fd0a3214e6be6`, request `c3a-types-priority1-01`.
Cloud Build FAILURE, но summary COMPLETE: это завершённый опыт с неуспехом gate,
не сбой раннера. `expectation_met=false`, `measurement_ok=false`, Kani exit 1.

| Гармоника (суффикс types::) | Результат | Время гармоники в summary | Checks failed/total | Covers |
|---|---|---|---|---|
| `sorted_permutation_traits_fallback_cell_u8_n0_to2` | SUCCESS | 40.57603 с | 0/573 | 14/18 |
| `sorted_permutation_traits_fallback_cell_u8_n7_to9` | TIMEOUT | лимит 600 с | нет результата | нет результата |
| `sorted_permutation_traits_general_drop_u8_n0_to2` | SUCCESS | 53.581898 с | 0/739 | 14/18 |
| `sorted_permutation_traits_general_drop_u8_n7_to9` | SUCCESS | 349.6911 с | 0/738 | 18/18 |

У N0/N1 четыре зарегистрированных covers несортированности/повторов неприменимы:
по два для каждого N. Проверки корректности прошли, но эти covers были unreachable.
В `3d98d6d` cover-функция для нетривиальных входов вызывается только на N>=2;
для N0/N1 она вообще не инстанцируется. Нет уменьшения домена или assertions.
Второй опыт повторяет проверку всех малых длин с обоими типами и исправленными covers.

Cell N7/8/9 перенесён в opt-in из-за timeout; Drop N7/8/9 — из-за 349.69 > 300 с.
Доказательство Drop N7/8/9 с полным оракулом установлено первым опытом, но в ordinary
это семейство не допускается. Групповой timeout Cell не доказывает ни одну из этих длин.

Память всего verify-прогона (включая компиляцию core): max RSS 2,263,336 KiB,
wall 18:37.15; максимальная измеренная сумма RSS 2,528,440 KiB (2.41 GiB).
`peaks`: cbmc 1,494,552 KiB (1.43 GiB), first/last 68..1114 с;
kani-driver 2,263,336 KiB (2.16 GiB), 0..1116 с;
kani-compiler 1,811,928 KiB, 2..64 с. Swap off, sampled every 2 с.

Привязка по времени: ограниченный `log-grep` показывает последовательность
Cell N7/8/9 (timeout) → Cell N0/1/2 → Drop N0/1/2 → Drop N7/8/9.
При первом появлении cbmc на 68 с выполнялось семейство Cell N7/8/9;
сумма 600+40.576+53.582+349.691 с согласуется с концом окна 1114 с.
Однако интерфейс сохраняет один пик на **имя команды**, без PID или времени пика.
Поэтому 1,494,552 KiB — общая верхняя граница пика cbmc каждой из четырёх гармоник,
а не четыре измеренных индивидуальных пика; аналогично driver — один общий процесс.
Точное распределение пиков между гармониками недоступно. Bound относится к наблюдавшимся
процессам штатного sampler; исчезнувший между сэмплами процесс может не попасть в статистику. Лейн ради него не менялся,
сырые логи/архивы не читались. Для всех четырёх общий верхний bound ниже 4 GiB;
у двух больших семейств запрет ordinary обусловлен временем, не памятью.

Ledger после завершения: 67 builds, used $37.3380, reserved $0.9450
(новая чужая незавершённая сборка). Приращение used от предыдущего снимка $0.3510
соответствует 26 минутам по $0.0135. Резерв второй сборки H=4 — $0.9450;
расход первого + резерв второго = $1.2960 <= $1.50.

### Сборка 2 — `5682e806-3426-46e8-b29b-edd12689ab95`

Commit `98e64f381316668eef694602974070d203332e47`, request `c3a-types-controls-02`,
controls=true. Cloud Build FAILURE, summary COMPLETE, Kani exit 1.

| Гармоника | Результат | Время | Failed/total | Covers |
|---|---|---|---|---|
| `types::control_sorted_permutation_traits_cell_drop_n0_to2` | SUCCESS | 234.58368 с | 0/885 | 23/23 |
| `types::reject_logical_sortedness_cell_n2` | FAILED | 0.6500462 с | 1/227 | 0/1 |
| `types::reject_logical_permutation_drop_n2` | FAILED | 2.5928304 с | 1/390 | 0/1 |
| `smoke::predicate_efficient_swap_type_matrix` | SUCCESS | 0.17181155 с | 0/12 | 12/12 |

Положительный контроль доказал исправленный helper малых длин для обоих типов,
со всеми зарегистрированными covers. В отрицательных контролях упало по одной assertion
именно в `types.rs:56` (sortedness) и `types.rs:58` (multiset), без иных провалов.
Однако вместо пользовательских строк сообщений Kani выдал
`This is a placeholder message; Kani doesn't support message formatted at runtime`.
Поэтому `expect_check` не совпал: `expectation_met=false`, `measurement_ok=false`,
несмотря на SUCCESS обоих положительных элементов и правильные строки отрицательных провалов.
Не выдаём этот gate за принятый.

В следующем library-коммите `bda4bf3` убраны только пользовательские сообщения assertions;
**выражения условий не менялись**. Теперь fingerprint — само конкретное выражение,
а не общий placeholder. Третий опыт проверяет совпадение этих fingerprint.

Память: max RSS 1,810,036 KiB, wall 5:21.94; sampled sum RSS 1,919,096 KiB (1.83 GiB).
Cbmc peak 1,405,192 KiB (1.34 GiB), 82..320 с; kani-driver 321,572 KiB (0.31 GiB),
0..320 с; kani-compiler 1,810,036 KiB, 2..76 с. Swap off, интервал 2 с.
Порядок из ограниченного `log-grep`: smoke → permutation-negative → sortedness-negative
→ положительный контроль N0/1/2. Первое наблюдение cbmc на 82 с относится к началу
этих коротких проверок; пик не имеет timestamp/PID и индивидуально не атрибутируется.
Для каждой строки таблицы применим общий наблюдавшийся максимум cbmc 1.34 GiB,
не отдельный измеренный индивидуальный пик. Исчезнувший между сэмплами процесс
может не попасть в статистику; это ограничение штатного sampler, не новый memory trace.

Ledger после второго опыта: 68 builds, used $37.6620, reserved $0.
Приращение $0.3240 включает наш второй и ранее чужой незавершённый запуск;
по этому интерфейсу их стоимости не разделяются. Консервативно считаем **всю** эту
разницу расходом C3a: суммарно не более $0.3510+$0.3240=$0.6750.
Никакие исторические ledger-записи не изменены.

`check-tooling` для сборки 1 завершился exit 0: пул k1-standard4 и все lane files
совпадают с `0f5ad96dd907ba06a30deb19e35fb746ea0bc72a`, все пять SHA-256 из summary совпали.

### Сборка 3 — `15520ad3-83e4-4d1b-b881-bd6554537c1d`

Commit `51f76623440cf1147792da40fcfc1b28f6b46178`, request `c3a-types-exact-controls-cell7-03`, controls=true.
Последний разрешённый запуск: два точных отрицательных контроля и отдельный
`sorted_permutation_traits_fallback_cell_u8_n7` (Cell N7, S0/U0).
Drop N8 отдельно отложен: приоритет последнего пакета — приёмка обязательных контролей
и меньшая проверка первого приоритетного типа Cell.
Резерв H=3: $0.8100; консервативная сумма расхода и резерва $1.4850 <= $1.50.
Результат Cell N7 не наследуется из timeout-группы: он проверяется отдельно.
Cloud Build SUCCESS, summary COMPLETE, `expectation_met=true`, `measurement_ok=true`.
Kani exit 1 ожидаем из-за двух заданных отрицательных результатов.

| Гармоника | Результат | Время | Failed/total | Covers |
|---|---|---|---|---|
| `types::reject_logical_sortedness_cell_n2` | FAILED, ожидаемый check принят | 0.3972972 с | 1/227 | 0/1 |
| `types::reject_logical_permutation_drop_n2` | FAILED, ожидаемый check принят | 1.4221903 с | 1/390 | 0/1 |
| `types::sorted_permutation_traits_fallback_cell_u8_n7` | SUCCESS | 98.845856 с | 0/414 | 5/5 |

Единственные failed checks — `assertion failed: output[i - 1] <= output[i]` на `types.rs:56`
и `assertion failed: count(input, probe) == count(output, probe)` на `types.rs:58`.
Таким образом, каждый контроль падает на конкретной ожидаемой assertion, не на UB,
unwinding assertion или посторонней ошибке. Нулевой cover после ложной assertion в
отрицательных контролях ожидаем; положительные covers полностью выполнены.
Cell N7 имеет достижимые возврат, несортированный вход, повторяющиеся ключи и оба trait-входа.

Память: max RSS 1,721,800 KiB, wall 2:33.38; sampled sum RSS 1,934,928 KiB (1.85 GiB).
Cbmc peak 225,124 KiB (0.21 GiB), 52..152 с; kani-driver 176,348 KiB (0.17 GiB),
0..152 с; kani-compiler 1,721,800 KiB, 2..48 с. Swap off, интервал 2 с.
Ограниченный `log-grep` даёт порядок: permutation-negative → sortedness-negative → Cell N7.
Первое появление cbmc на 52 с связано с началом отрицательных контролей, а основная
длительность приходится на Cell N7 (98.85 с). Пик не содержит PID/timestamp:
225,124 KiB — общий наблюдавшийся максимум для этих трёх гармоник, а не три точных пика.
Он ниже 4 GiB и позволяет применить предварительный фильтр ко всему пакету.

`check-tooling` третьей сборки: exit 0, правильный пул, все lane files и пять SHA-256
равны базе `0f5ad96dd907ba06a30deb19e35fb746ea0bc72a`.

Cell N7 допущена в ordinary в `d7c2309`: снят только cfg-gate самой гармоники и её
макроса, исправлен комментарий о статусе. Проверенные условия, данные, comparator,
тела trait-методов, solver и unwind не менялись. Дополнительный прогон после снятия
гейта не выполнялся: тело уже проверено с controls=true, а cfg ограничен proof-модулями.

Финальный ledger: 69 builds, used $37.7700, reserved $0.
Третья сборка — единственный новый запуск после снимка 68 builds без резервов;
приращение $0.1080 соответствует восьми минутам по цене лейна.
Консервативный итог C3a: $0.3510 + <=$0.3240 + $0.1080 = **не более $0.7830**.
Это верхняя оценка с включённым чужим расходом во втором приращении, не точный счёт биллинга.
Использованы ровно три сборки; последующий dispatch не выполнялся.

## Границы результата

Приоритет 2 не добавлялся: `u128` должен идти через F1→general
(`size=16 > 8`, `16*48=768 <= 4096`), `[u64;11]` через F1→fallback
(`size=88`, `88*48=4224 > 4096`). Это иные ветви Copy-специализации,
и Drop F0→general их не доказывает. Бюджет/три запуска были направлены на первый приоритет,
исправление неприменимых covers и обязательную точную приёмку отрицательных контролей.
Удалённые в C2 дубли safety не восстанавливались.

Выборочные точки не равны покрытию диапазона. Точное новое покрытие и остаток:

| Тип, маршрут и валидный порог | Ordinary | Дополнительно доказано opt-in | Нет функционального доказательства в C3a |
|---|---|---|---|
| Cell<u8>, S0/U0 fallback, 16 | 0,1,2,7 | нет иных длин; timeout группы не даёт доказательства N8/9 | 3..6, 8..16 |
| DropKey(u8), S1/U1/F0 general, 32 | 0,1,2 | 7,8,9 | 3..6, 10..32 |

Для ordinary Drop не покрыты все длины 3..32, включая доказанные только opt-in 7/8/9.
В частности, не установлены Cell N15/16 и Drop N15/16/17/31/32, включая переход sort8.
Не добавлялись непроверенные гармоники на эти размеры. Причина остановки — ограничение
на три сборки и выбранная очерёдность; это не утверждение о невозможности в Kani.
Отдельно открыты корректность 17..32, insertion произвольной длины, generic-T и компараторы,
uninit, aliasing, unwind и условные композиционные доказательства.
Три trait-метода по-прежнему без correctness requires/ensures: здесь обычные harness asserts,
не новые `proof_for_contract` на small_sort. Drop-счётчики старого набора не расширялись.

300 с / 4 ГиБ — предварительный фильтр, не доказательство пригодности для autoharness CI:
там jobs=3 и есть macOS с 7 ГБ. Общий max RSS прогона не равен одновременной памяти CI.
Ограничения атрибуции пиков указаны для каждого запуска выше. Решение об ordinary
учитывает три новых небольших harnesses и отказ от двух тяжёлых групп, а не общий max RSS
сборки. Для Cell N7 наблюдавшиеся cbmc/driver — 0.21/0.17 GiB; сценарная оценка трёх
таких cbmc + одного driver — около 0.80 GiB. Для совместного малого контроля двух типов
аналогичная оценка по сборке 2 — `3*1.34+0.31=4.33 GiB`; это расчёт по компонентам,
не измерение одновременной памяти или доказанный верхний bound для jobs=3/macOS.
Общего CI-прогона и macOS-замера не было. Пригодность всего набора для CI организаторов
не установлена; ordinary здесь не означает успешную проверку их полного pipeline.
Timeout описывает предел конкретного опыта, не невозможность доказательства в Kani.
Shutdown раннера в П-6 имеет неустановленную причину; OOM остаётся гипотезой.

## Проверка и перенос

Изменения library закоммичены отдельно от research; все коммиты имеют `[skip ci]`.
Library-коммиты по порядку переноса: `a111a473a3`, `3d98d6dd6b`, `854083b299`,
`bda4bf3`, `d7c2309`. Коммиты 854083b и bda4bf3 вместе оставляют только измеренную Cell N7;
отдельный кандидат Drop N8 в итоговый набор не вошёл.

Итоговый формат: **exit 0**, указанным TASK-C3A rustfmt, edition 2024, конфигурация C2:

```sh
/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml library/core/src/slice/sort/shared/smallsort.rs
```

Строки в изменённых Rust-файлах <=100; `git diff --check` — exit 0.
Отдельные тесты rustc/cargo/Kani/CBMC локально не запускались.
Runtime-код, старые тела гармоник, contracts/domains/assumptions/stubs сохранены,
кроме явно разрешенного дополнения матрицы swap.

## Строки для таблицы критериев отзывов PR

| Criterion | Suggested PR-table text |
|---|---|
| Efficient-swap type coverage | The existing predicate matrix now includes u16 (true) and [u8; 9] (false), derived from size_of::<T>() <= 8, alongside the existing ZST/Cell/Drop cases; the expanded matrix passed Kani. This is a concrete type matrix, not a generic-T theorem. |
| Genuine correctness on trait inputs | Real stable/unstable trait-entry harnesses prove sortedness and full logical-value multiset preservation for Cell<u8> at {0,1,2,7} and Freeze non-Copy DropKey(u8) at {0,1,2}. An opt-in Drop proof additionally covers {7,8,9} in 349.69 s; coverage up to thresholds 16/32 remains open. |
