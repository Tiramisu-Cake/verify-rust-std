# EXT X0 — кандидат базы, инвентарь и входы X6/X7

Дата: 2026-10-28. Интегратор X0, бумажный этап, Cloud **$0**.
Основание: `TASK-ext-x0.md`, EXT R2 §2–4.2, §5.1, §8 на
`a5091f26a110f2c9e0180e9b64ad91507ac9bd7b`.

## 1. Зафиксированный срез и смысл E_M

**Кандидат `S_M = ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad`.**
Приёмка ожидает финальный CI координатора, Actions run `40665992084`:
4×ubuntu-latest с `KANI_JOBS=2` и 4×macos-latest. В X0 его состояние
не опрашивалось; все итоговые платформенные клетки ниже оставлены
`TODO (coordinator, final CI)`. Этот документ не объявляет кандидата принятым.

Прочитанные источники (позднейшие изменения не подразумеваются):

| Источник | Pin и использование |
| --- | --- |
| `RESULT-w3-l1.md`, `W3-REQUIREMENTS.md`, `W3-DISCLOSURE-DRAFT.md` | `b6b480cc`; документы этапа D не изменяются |
| `RESULT-w3-l2.md` | `daf8d13ef1ec9ba67549727ce1fd08fda50d7dd1`; итог B, D-B4 и реестр builds |
| `MACOS-L1-8-2026-10-28.md` | `41659f9ff4f71bf4902da5d8c06ff90c1b8fa9c6`; только ранний `5c713131f8b92c629f0c16b68605ec2bf2547007` |
| Общие W3-RULES | `d5dc2c5fbf0da8210022112de12d25dce923934f`; task X0 строже: никаких сборок |
| REQUIREMENTS-INTERPRETATION §2 C4/F1–F3 | `73ed3906fa25fba9efed3e0669b0b6aeae377d91`; уточнение primitive/default-order остатка |
| Код всех таблиц/координат ниже | `S_M`, а не рабочее дерево X0 |

`E_M` — реестр **точных совместимых** клеток с историческим основанием,
а не множество всех функций с `#[kani::proof]`. Ни наличие source entry,
ни SUCCESS caller без callee prerequisite не дают proof credit. Здесь
независимо установлены текст исходников, cfg, состав и маршруты; результаты
Kani остаются **source-reported** по указанным RESULT, без нового запуска.
Не путать требования B1/B2 с уровнями bounded evidence/full proof B1/B2.

Интеграция проверила только три гармоники: build
`d19d306d-43ef-44dc-a79a-fd0c0a8049cf`, gate true, 3/3 SUCCESS,
covers 12/12, tooling BASE d5dc2c5f совпал. Это fallback u64 N8,
fallback u8 N9 и swap predicate; не все 21 L2 и не весь `S_M`.
Отказ `d111012e` остаётся TOOL_ERROR/NOT_RUN, не контрпример и не успех.

### 1.1. Исторические клетки E_M и границы переноса

| Свойство | Source-reported область | Основание / что не следует |
| --- | --- | --- |
| О1-А general, stable Freeze, network | u64, каждая N0..32; stable external scratch48; соответствующий non-Copy general/trait | W3-REQUIREMENTS Д1; arbitrary read-only comparator CD-2, cut только ord-violation; не все UB-категории |
| C3 safety | Представительные типы/длины таблицы §2.2; i32 обе trait-точки N0,1,2,15,16 | Д2/Д13; 143 прежние не-ZST клетки и 13 reachability — клетки/entries разных видов, не число всех гармоник |
| General/stable correctness | u64 N0..12 и16; u8 N0..16 | Д3/Д10; u8 N14/15 — D-B4, exact arrayN/scratch48; перенос bm на scratch48 аналитический, не новый машинный scratch proof |
| Network correctness | u64 N0..14; u8 N0..15 | Д3/Д4: N0..8 direct; выше — full-route sortedness и отдельная композиция перестановки сети/хвоста. Full-route multiset N10+ не заявлен |
| Fallback correctness | u64/u8 N0..16 | Д3/Д10: L2 добавил u64 N8..16 и u8 N9..16, все отдельные длины |
| B4 insertion safety | u64 N1..20, все допустимые offset1..N | Д2 + Д8: прежние N1..15 и L1-5 N13..20; это объединение, не новый X7 credit |
| О3 safety | `Cell<K13Tagged>` обе default-точки N0..16; insertion N1..20 все offset | Д2/Д8; не `Cell<i32>`, не функциональная сортировка изменяемых ключей |
| sort4 | u64 и `[u8;16]`, N4: strict contract и отдельный arbitrary ordinary proof | Д6, `d065eab6`; `[u8;85]` оба TIMEOUT600, вне E_M |
| swap/frame | u8/u64 exact `[T;N]`, N9..17, любые различные позиции; и прочие конкретные C3 K9s instances | Д4/Д7, точные allocations в инвентаре; не автоматический перенос в scratch48 |
| insert_tail shifted | u64 backing17, start1..15, tail=start+1..16, 120 регионов; start0 отдельно | Д4; иные backing allocations/типы не наследуют credit |
| L2 u8 prefix/scratch | backing17 prefix lengths2..17; backing48 starts0/6/7 lengths5..8 с frame | Д10, `6e32e784`/`be2555c0`; не произвольный scratch size/offset |
| Stable ZST | N1,2,7,8,16,17,31,32, ZST-aware comparator | Д13, `1e761350`; остальные ZST sorting клетки открыты |

Чистые correctness comparators `lt_u8/lt_u64` сравнивают ключ `x >> 1`:
полные значения символические, равные ключи с разными значениями разрешены.
Перестановка — равенство кратности произвольной полнобитной пробы; это не
редукция входа к 0–1. Drop — normal-return пары «счётчик + метки»,
fallback N2/4/8, general/stable N2/4/8/16; unwind ими не установлен.
Исторические Tagged N4/8, merge u64 N20/24 на32GB, U-1 unsupported и ZST
diagnostics не добавлены в обычный принятый слой E_M.

## 2. Точный остаток М

Состояния в этой таблице — перенос статусов W3-REQUIREMENTS на `b6b480cc`,
с раскрытием доменов, а не новый вердикт по требованиям. X6/X7 — пилоты,
ни один не обещает закрыть всю строку. «Следующая очередь» означает
**вне первой волны** и требует отдельного задания/бюджета.

| М-клетка | Незакрытая часть | Маршрут закрытия |
| --- | --- | --- |
| A1, E1 | Полный no-UB: uninit unsupported на9461e07a; aliasing не доказан; invalid values/immutable bytes ограничены фактической моделью. Нет полного SAFETY-домена всех целей/типов/длин | X8 supported tool + controls + actual scratch + принятый CI; X9 только после отдельной разморозки. Вне первой волны |
| A2 | Реальные callee во всех инстанциациях; `CopyOnDrop::drop` при unwind не исследован; выбранные тела не дают все типы/длины | X6 source binding для merge, X7 actual insertion; общий остаток X1/X9 и раскрытие unwind, вне первой волны |
| A3, A4 | Для каждого stub точные тип, comparator, длина, backing allocation, активный/вложенный регион, frame, no-alias и sorted-prefix/halves. R11 на отдельных нарушениях не доказывает все caller preconditions | X6/X7 только свои цепочки; X1 остальные. u64 GS13..15 scratch prerequisite отсутствует; scratch48 merge D-B4 аналитический |
| B1, B2, C4 (примитивы), E3 | General/stable u64 N13..15; general/stable обоих типов N17..32; network u64 N15..32 и u8 N16..32. Fallback u64/u8 до16 уже закрыт в точном домене | X6 — pilot merge16/20/24/(32), затем отдельное полное семейство; нижние GS/network пробелы X1/следующая очередь. Пилот не закрывает интервал |
| C4, точность типа/порядка | Другие primitive-инстанциации C3 (i32/u128) не имеют установленной полной route correctness; lt_u8/lt_u64 по x>>1 не равен default `<`. Full-route default-order credit не переносится автоматически из этих contract instances | X1 для недостающих primitive/default-order клеток; иные C3 — К. Вне первой волны; X6 rank-довод требует отдельной проверки и не меняет S_M задним числом |
| B4 | Safety insertion для любой N>20 и любого допустимого offset; u64 bounded1..20 уже есть. Не весь типовой/UB-домен даже внутри20 | X7 unbounded отдельно, X9 инвариант; первая X7 не добавляет B4 anylen |
| B5 до20 | Direct offset1 u8/u64 m17,18,19,20; остальные реальные network/регион/backing клетки по §2.1. Отдельный tail proof не сортирует весь insertion | X7 только четыре u8 клетки; direct18/19, u64 и прочая геометрия — следующая очередь |
| B6, F1 | sort4 `[u8;85]` N4 contract/arbitrary TIMEOUT600; полнота всех requires/ensures только в проверенных инстанциациях. Swap/frame для прочих backing/type/length не следует из K9s exactN | X1 выбранные недостающие клетки, вне первой волны; X6/X7 сохраняют R4 и дают только свои новые контракты |
| C2, C3 | Недостающие длины/ветви типовой safety-матрицы §2.2; ZST stable N0 и прочие невыбранные N, весь unstable/network и K9s; sort4 b85; i32 только пять длин, без i32 K9s | X1; ZST model X8, loop/source scope раскрытие; вне первой волны |
| D1 | Arbitrary bool safety не весь тип×длина insertion; volatile-модель неприменима к ZST без отдельного решения | X1/X8; X6 structural controls расширяют только свой домен; X7 pure order этого остатка не закрывает |
| D2 (М-часть) | Полная корректность normal-return merge/верхних маршрутов17..32; cut при ord-violation не является unwind-proof | X6 с отдельными sortedness/structural permutation и последующим полным набором; unwind — раскрытая В/К-часть, не скрытое М-усиление |
| F3 | Внутренние contract/harness пары неполны по типам/длинам/геометрии; приёмка такой формы комитетом не установлена | X6/X7 только свои пары, X1 остальное; решение по форме — владельцу/комитету |
| F5, G5 | Окончательная сверка итогового source с актуальным upstream, отсутствие ослабления main/runtime | Координатор перед подачей/X10; X0 не меняет library или tooling |
| G1, G2 | Полный ledger предпосылок/covers, отсутствие вакуумности на окончательном наборе. U-1 covers0 не засчитываются; ord cut сохраняется | X6/X7 новые controls/ledger; полный inventory/covers X10 и final CI |
| G3 | Финальный CI snapshot/trust ledger на S_M вместо старого5c713131 и выборки3 | Координатор final CI, X10 для каждой новой публикуемой волны |
| H1, H2, H4 | Полный принятый набор 4×ubuntu+4×macOS, whole-job time/memory/completeness; ранний p2 macOS swap756MB, p3 был14GB; GCB p2 неполон, p2/p4 дорогие | `TODO (coordinator, final CI)`; после расширений X10. measurement≤600с одного pilot этого не заменяет |
| I3 | Подача/лицензия/формулировка/два approval, человеческое решение о публикации | Владелец, вне X0 и proof первой волны; внешних действий X0 нет |

Допущения/раскрытые М-части также сохраняются: C1 допускает инстанциации
только в нашей трактовке, не generic proof; E2 не освобождает автоматически
от выразимых UB-категорий; E5 — отмеченная недостаточность SAFETY-комментария
`merge_down`, дополненная §4 ниже. F4 и I2 условны и неприменимы без
VeriFast/комбинации. B3 М-часть включается при расширении выше trait-порога;
такое расширение X5 вне первой волны. I1 (выбор одобренного Kani) закрыт,
но не означает приёмку набора. К/В-строки C5/D3/D4/D5/D6/E4/F2/G4/H3
не превращаются здесь в новые обязательные М.

### 2.1. B5 и геометрия, которые нельзя схлопнуть по длине

`D_B5,M` — реальные `route × type × m × offset × backing/region`,
где длина insertion-региона m≤20. Остальные допустимые offset — К.

| Реальное семейство | Точный домен | Остаток после E_M / первая волна |
| --- | --- | --- |
| Public direct insertion, ordinary cfg | u8/u64 m2..20, offset1; exact caller allocation | Fallback ≤16 даёт лишь совместимые клетки с обоснованным переносом route; direct17..20 открыты. X7 u8 m17 и20, не18/19 |
| Stable default/unstable fallback/selection remainder | m2..16, offset1; реальные типы/подсрезы caller | u8/u64 fallback0..16 принят, но arbitrary caller backing и все C3 не следуют; не весь selection caller верифицирован |
| Network no-merge | N=m2..8 offset1; m9..12 offset9; m13..17 offset13 | Full correctness u64≤14/u8≤15 с отдельной композицией; выше соответствующие пробелы. X7 u8 m16/o13 на backing16 |
| Network merge | N18..24: m=floor/ceil(N/2), o9; N25: left12/o9, right13/o13; N26..32: обе m13..16/o13 | Backing `[T;N]`, левая/правая половины раздельны; full-route correctness18..32 не установлена. X7 только левая N20: m10/o9 на backing20 |
| General/scratch | Прямой `insert_tail`, не insertion с offset4/8; starts0/floor(N/2), длины от presort+1 до длины половины, scratch≥N+16 | Доказанные scratch48 starts0/6/7, m5..8 u8 — узкое подмножество. Прочие starts/scratch sizes/types/lengths требуют отдельных callee/frame оснований; X6в обязан их перечислить |

Для nontrivial general N2..32 runtime проверяет scratch≥N+16
(`smallsort.rs:220–232`), а проверенный внешний scratch=48 — только один
допустимый размер. При N<2 ранний возврат предшествует проверке scratch.
Меньший достаточный scratch N+16, больший scratch, внутренние регионы
больших caller allocations не покрыты автоматически. Общие `&mut`-срезы
дают disjoint ownership на входе, но Kani proof/callee geometry всё равно
должна совпадать с конкретной инстанциацией.

### 2.2. Остаток C2/C3 в set-форме

Обозначения: `G={0,1,2,7,8,15,16,17,31,32}`,
`S={0,1,2,15,16}`, `U={8,9,12,13,17,18,31,32}`.
Дополнения ниже — ровно неустановленная полнота длин относительно
заявленного route threshold, а не требование доказать каждый Sized T.

| Тип | Source-reported safety выборка | Незакрытая полнота |
| --- | --- | --- |
| u64 | Отдельные О1 семейства обеих Freeze-ветвей, каждая0..32 | UB-категории E1 и иная геометрия; не новый пробел safety-длин |
| u8 | stable G; unstable network U | stable `[0..32]\\G`; network `[0..32]\\U` для этой типовой выборки |
| i32 | stable/unstable S | обе `[0..32]\\S`, i32 K9s symbolic-index N9..17 не установлен; пять N не дают correctness |
| u128, `[u8;16]`, `[u8;17]`, `[u8;85]`, Freeze !Copy Drop | stable/general G и unstable/general G | обе `[0..32]\\G`; у b85 отдельно sort4 N4 не принят |
| `[u8;86]` | stable/general G; unstable/fallback S | stable `[0..32]\\G`, fallback `[0..16]\\S`; stable не становится fallback |
| `Cell<i32>` | stable default/unstable fallback S | обе `[0..16]\\S`; О3 другой тип не заполняет эту строку |
| `()` | stable `{1,2,7,8,16,17,31,32}`; predicate accepted | stable дополнение в0..32; network/unstable все0..32 и K9s не приняты |

При ZST N≥18 network region loop не выходит: смещение ZST-указателя
оставляет адрес неизменным, поэтому условие выхода `region.as_ptr() !=
v_base` (`smallsort.rs:355`) не выполняется. N17 diagnostic не закрывает
network ZST. Stable sort, unstable sort и selection выходят раньше для
ZST; публично достижимый отказ не заявлен. Runtime исправление не входит
в X0/X6/X7. Это отдельный source/domain blocker сверх volatile-модели.

## 3. T/P/H/M и раскладка

Единицы памяти — GiB из байтов. `A[o]` — действующий VM/cgroup предел,
не мгновенная свободная память. Рекламные7/14/16GB не подставлены как GiB.
`P` — совокупный пик job с описанным методом, не максимум одного процесса.
`R_t=30мин` — предварительное решение X0 по §4.1, не лимит организаторов.
`R_m` не назначен без данных; если P включает ОС, повторно ОС не вычитать.
`H=360−T−R_t`; `M=A−P−R_m`. При неизвестном входе результат UNKNOWN.

### 3.1. Финальный кандидат S_M — заполняет координатор

Во всех восьми строках T/G/P/A/R_m: `TODO (coordinator, final CI)`.
Их нельзя заполнить ранними L1 или отдельными L2 measurements.

| ОС | p | jobs | T, мин | G, мин | P, GiB / метод | A; R_m, GiB | R_t, мин | H, мин | M, GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ubuntu | 1 | 2 | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | 30 provisional | UNKNOWN | UNKNOWN |
| ubuntu | 2 | 2 | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | 30 provisional | UNKNOWN | UNKNOWN |
| ubuntu | 3 | 2 | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | 30 provisional | UNKNOWN | UNKNOWN |
| ubuntu | 4 | 2 | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | 30 provisional | UNKNOWN | UNKNOWN |
| macOS | 1 | фактический -j: TODO | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | 30 provisional | UNKNOWN | UNKNOWN |
| macOS | 2 | фактический -j: TODO | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | 30 provisional | UNKNOWN | UNKNOWN |
| macOS | 3 | фактический -j: TODO | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | 30 provisional | UNKNOWN | UNKNOWN |
| macOS | 4 | фактический -j: TODO | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | TODO (coordinator, final CI) | 30 provisional | UNKNOWN | UNKNOWN |

### 3.2. macOS L1-8 — только ранний кандидат 5c713131

Run40603213401; Kani собран до timed verify, T ниже включает его сборку.
Все4 gate true/COMPLETE, каждый520/520 SUCCESS; список worker совпал.
Это source-reported данные `41659f9f`, не новый просмотр CI.

| p | SmallSort entries | T job, мин | Verify, мин | G | Max process RSS, GiB (не P) | Peak swap | Runner reported | H раннего, R_t30 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 | 39 | 32,7 | UNKNOWN | 3,27 | 0MB | 3CPU/7GB | 291мин |
| 2 | 261 | 108 | 104,4 | UNKNOWN | 3,98 | 756MB | 3CPU/7GB | 222мин |
| 3 | 0 | 23 | 20,1 | UNKNOWN | 4,83 | 0MB | 5CPU/14GB | 307мин |
| 4 | 73 | 123 | 117,0 | UNKNOWN | 2,84 | 0MB | 3CPU/7GB | 207мин |

P, A в байтах, R_m и M **UNKNOWN для всех4**. Отчёт описывает
`/usr/bin/time -l`/per-command RSS и ps sampler5с; сумма RSS12–17GiB
на macOS считает shared pages повторно и непригодна как P. Swap измерен
`sysctl vm.swapusage`. Положительный запас времени не устраняет swap p2
и отсутствие 7GB измерения p3. Разность округлённых T/verify не объявлена
точным G. Эти H не являются расходуемым запасом S_M.

### 3.3. GCB — калибровка старого состава, не ubuntu

Код SmallSort совпадал с5c713131, requests разные. Jobs2, swap0,
sampled sum RSS каждые2с; это process RSS proxy конкурентного/compile
пика, не доказанный физический P целого VM с ОС. Machine reported15,63GiB.

| p / build | Source | Факт | W verify-std incl compile | G оценка до первой проверки | Sum RSS sampled, GiB | Подготовка до verify отдельно |
| --- | --- | --- | --- | --- | --- | --- |
| 1 / b796ca7b-fa1c-4dd2-ba06-8b3fb22e18e7 | 1ba746138fb7b17b355166dc091f7b0bdd70ae7b | gate true,521/521 | 80:28 | ≈55,5мин | 5,11 | 409с |
| 2 / dbfe8043-e99e-49e0-a794-5e103e73f025 | 9d204ebfc497dd05d18290857151b4a537b3e724 | PARTIAL,gate false;501SUCCESS+2UNKNOWN+18missing из521 | UNPARSED; sampler318мин не точный W | ≈45,58мин | 13,16 | UNKNOWN |
| 3 / ef4345ad-8ebd-45cc-93ef-a33dbdc6b505 | 3796a1ac751be151931971d25a1281d85058f642 | gate true,521/521 | 65:19 | ≈43,73мин | 4,16 | 368с |
| 4 / aea9fcc6-b301-4f9c-a49a-a6858b34b0dc | 7281d216696e94182aeb9dedef91f407f30136f9 | gate true,519/519 | 285:15 | ≈50,05мин | 7,46 | UNKNOWN |

G — оценки по первому sampled goto-instrument, у Checking harness нет
timestamp. W не включает отдельную подготовку lane; поэтому W не выдан
за T целого job. Полные T_GCB, H_G и M_G остаются UNKNOWN; для p1/p3
известны лишь части подготовки, не гарантированный полный T. По §4.1
при появлении полного T_GCB разрешены условный proxy `H_G=330−T_GCB`
и сценарий `H_U_est=330−T_GCB/1,8`; это не измерения ubuntu и не гарантия
для нового solver/source. Для macOS коэффициент1,8 неприменим.
P2/P4 превысили внутренние240мин; соответственно6/7 завершённых SmallSort
гармоник были >600с. Успех partition не равнозначен measurement≤600с.

### 3.4. Перераскладка

Прежние Linux2082 entries делились521/521/521/519, macOS2080 —520×4;
разный target даёт разный глобальный список. В X0 `kani list` не запускался.
Добавление21 correct entries требует нового **полного target-specific**
списка координатора и штатного разбиения, а не прибавления21 к старому p2.
Инвентарь §6 — статический SmallSort-подсписок, не подмена полного std-list.
Для каждого расширения X10 пересчитает `Delta=T_new−T_base` и
`Share=max(0,Delta)/H` по каждой ОС/партиции; Q до измерения UNKNOWN.
Запас четырёх workers не суммируется, отдельные Q не складываются.
L2 sequential build peak8,78GiB нельзя делить на число гармоник или jobs.

## 4. Source-проверка X6

Пути в этом разделе: `library/core/src/slice/sort/shared/smallsort.rs`
(далее SS) и `smallsort/kani_k1/merge.rs` (далее KM), всё на `S_M`.

| Функция / source | Сигнатура и фактическая геометрия |
| --- | --- |
| smallsort.rs:777–807 `merge_up` | `unsafe fn<T,F:FnMut(&T,&T)->bool>(left_src:*const T,right_src:*const T,dst:*mut T,is_less:&mut F)->(*const T,*const T,*mut T)`. Читает оба source, `is_l=!less(right,left)`, копирует выбранный source, продвигает ровно один source и dst через add(1). Оба текущих source initialized/aligned/readable, dst writable/aligned и disjoint с копируемым значением; арифметика add(0/1) остаётся в allocation/one-past |
| smallsort.rs:810–840 `merge_down` | Та же сигнатура. При is_l копирует right, иначе left; выбранный source — wrapping_sub(1), dst — sub(1). Помимо чтения/записи нужен допустимый predecessor dst в его allocation. Writable singleton с dst на первом элементе недостаточен для non-ZST. Source wrapping-cursor может выйти за начало после потребления, но не разыменовывается в таком состоянии |
| smallsort.rs:865–945 `bidirectional_merge` | `unsafe fn<T:FreezeMarker,F:FnMut(&T,&T)->bool>(v:&[T],dst:*mut T,is_less:&mut F)`. len≥2, initialized source slice, dst valid for len writes и не overlap с source; halves floor(len/2)/ceil(len/2). Runtime верхнего предела32 нет; Kani-contract ограничен2..32 |

Source-курсоры между собой могут совпадать: shared reads сами по себе
не требуют source-source disjoint. Нельзя выводить ownership/provenance
из равенства числовых адресов. Comparator для функционального результата
чистый SWO; произвольный CD-2 read-only нужен отдельно для controls.
`FreezeMarker` smallsort.rs:852–853 отражает работу с временными копиями.

smallsort.rs:914–925 начинает left=src, right=src+h, left_rev=src+h−1,
right_rev=src+len−1, dst_front=dst, dst_back=dst+len−1. Выполняются
h пар up/down: назначения front0..h−1 и back len−1..len−h.
smallsort.rs:931–936 при odd len копирует оставшийся элемент в центральный dst[h],
выбирая left если left<left_rev.wrapping_add(1), иначе right; продвигает
именно выбранный курсор. smallsort.rs:927–943 вычисляет ends и пропускает нормальный
возврат только при обоих равенствах left/end и right/end. Без монотонных
шагов и связи каждой записи с выбранным source одних равенств недостаточно.

### 4.1. Контрактный путь без изменения runtime

У merge_up/down контрактов сейчас нет. Kani-only attrs
`cfg_attr(kani, requires/ensures/modifies)` допустимы технически по
существующим raw-pointer шаблонам smallsort.rs:695–700,747–756,859–864.
Для шага нужны readable current sources, writable output slot,
disjoint copy, корректная pointer arithmetic, modifies только dst[0],
post о результате tuple и копировании **старого выбранного значения**.
У generic `FnMut` может изменяться состояние comparator: frame одного dst
обоснован только на выбранном чистом/read-only comparator без таких
записей, не на всяком F; дополнительные эффекты требуют собственного frame.
`can_read/can_write` текущего слота сами по себе не устанавливают
допустимость predecessor/next pointer. Баз и длин у helper нет: контекст
allocation/индексов и frame надо хранить в kani-only predicates/обёртках
caller с известной геометрией. Нельзя молча усилить requires так, чтобы
исключить реальные допустимые call sites. Условия не должны повторно вызывать arbitrary comparator: выбранный source/результат берётся из actual события/tuple. При несогласованном comparator курсоры могут пересекать исходную границу половин, оставаясь внутри общей source allocation; нельзя исключить эти пути более сильным half-local requires ради mutant PASS. Поддержка конкретной формы
`old`/tuple/modifies и стоимость на pin пока UNKNOWN, не новый результат.

У bm уже requires len2..32, `k1_merge_dst_ok`, sorted halves, modifies
dst[..len], ensures sortedness **и probe permutation** (smallsort.rs:859–864;
smallsort/kani_k1/merge.rs:355 и далее). X6б sorted-only требует изолированного cfg/profile:
не ослаблять контракт S_M для прежних callers. Wrapper вызывает actual
body, не его копию; `proof_for_contract` проверяет выбранные clauses.
`stub_verified` разрешён лишь для доказанных типа/comparator/len/region;
u8 proof не разрешает u64 stub. Обычный `kani::stub` функции с контрактом
на этом pin ранее дал missing-contract-closure (L1 build ee1f96a2):
это риск instrumentation, не доказанная невозможность verified stubs.

### 4.2. Что реально исследует X6 и где STOP

| Подэтап | Source-доступный путь | Неустановленное / blocker gate |
| --- | --- | --- |
| а | Actual up/down tuple даёт cursor deltas; source-map smallsort.rs:800/833/934 и front/back/odd геометрия дают кандидата событий копирования | Нужна проверенная привязка наблюдения к каждой actual copy, written-once, value origin и отсутствие иных записей. Endpoint-only wrapper не видит внутренние события. Позитивное proof копии тела/непроверенной integer machine не принимается (копии-мутанты с source-map — отдельные отрицательные controls); при отсутствии метода STOP до дорогих измерений |
| б | Actual bm proof_for_contract на sorted-only, u64/u8 N16→20→24, затем gate32; R11 по одному на тип | Expressibility/modifies/old и применимость preconditions требуют preflight. Не повторять Tagged L2-1; TIMEOUT не время. Без gate а быстрый sorted PASS не даёт GO полной correctness |
| в | smallsort.rs:243–255 sort4/8, smallsort.rs:259–274 copy/tail, smallsort.rs:278–291 scratch→v merge; smallsort.rs:339–369 network→merge→copy; smallsort.rs:720–774 sort8 цепочка | Каждый callee имеет собственное permutation/frame/region основание. Перенос на иной scratch/полуподсрез не автоматический. Multiset всей памяти со scratch не сохраняется. Sorted-only stub не доказывает Kani permutation caller; отдельный source-bound довод review-ится отдельно |

Решение X0: X6 **осуществим как gated исследование**, не готовое proof.
Контракты одного шага полезны, но не заменяют source binding всего merge.
Два mutants (double-write и удалённый guard) обязательны: второй — на
несогласованном read-only comparator, без эквивалентного assume после
удаления guard. Under SWO удалённый guard может быть избыточен.
GO32 только при structural gate и прогнозе≤600с по измеренному росту;
прямой N24≤600с допускает ограниченное продвижение до24. Детали/смета —
[черновик X6](TASK-ext-x6.md), не выданный запуск.

## 5. Source-проверка X7

Все координаты ниже на `S_M`; SS/KM определены в §4.

| Запрошенная u8 клетка | Реальный вызов и условия | Геометрия / предел claim |
| --- | --- | --- |
| direct(17,1) | `stable/mod.rs:77–83`, `unstable/mod.rs:38–56`: ordinary public sort len≤20 после len<2/ZST exit вызывает insertion offset1 | Exact input backing17; не fallback trait при N17, его threshold16 |
| direct(20,1) | Те же public routes при len20 | Backing20; optimize_for_size/16-bit cfg отдельны и не включены |
| network(10,9) | smallsort.rs:142–169 u8 Freeze+Copy и size≤8 выбирает network threshold32; smallsort.rs:329–349 при внешнем N20 первая половина len10 проходит sort9, затем insertion offset9 | Region `[0..10]` в input backing20. Scratch32 smallsort.rs:327 — будущий merge destination, не backing этой половины. Правая `[10..20]` отдельно, credit не переносится |
| network(16,13) | Прямой unstable small-sort N16: no_merge=len<18, sort13, insertion всей длины16 с offset13 | Input backing16; top-level public sort N16 выбрал бы direct offset1. Это отдельный trait-вход, не public dispatch с тем же N |

Маршруты статически достижимы. Обычный public small sort N10/16/20
не даёт network-offset claim: сети вызываются через small-sort trait,
в том числе на подсрезах больших сортировок. Для X7 приняты конкретные
trait/region входы из таблицы; доказательство всей большой сортировки
в задачу не входит.

### 5.1. Узкий insertion contract и допустимый caller

smallsort.rs:655–660 задаёт Kani requires len2..17 и offset1/9/13 по длине,
а runtime smallsort.rs:666–688 принимает любой offset1..len. Поэтому
`stub_verified(insertion_sort_shift_left)` **несовместим** с direct17/20
offset1; нельзя добавить assume ложного requires или выдать этот stub
за actual путь. Но это не blocker самого маршрута: ordinary body при
штатном `--no-assert-contracts` можно проверять, используя verified stub
**только insert_tail**. Именно так existing `correct.rs:10–54`
проверяет fallback offset1 при N9..16 несмотря на узкий insertion contract.
Этот source-pattern обосновывает выбор дизайна, не предсказывает PASS20.
Если pin/профиль перестанет поддерживать этот путь — STOP с точной ошибкой;
переписанный цикл не даёт actual caller credit. Общие attrs без передачи
ownership не менять.

### 5.2. Insert_tail18..20 и более короткие регионы

smallsort.rs:601–610 и smallsort/kani_k1/merge.rs:305–329 требуют same-allocation begin/tail,
tail−begin≥1, writable inclusive region, initialized значения и sorted
prefix; modifies ограничен этим регионом, ensures sortedness и old/new
probe-count. Верхнего предела17 в `insert_tail` requires нет.
Для direct17 caller нужны tails1..16, для direct20 tails1..19:
требуются **все** регионы2..17/20 на соответствующих backing allocations.

Решение X0: до3 callee entries на backing18/19/20 могут выбирать
символический tail1..N−1, тем самым доказывать все prefix lengths2..N
и suffix-frame (шаблон `correct.rs:56–73`). Это совместимо с source
контрактом и не ограничивает tail только N−1. Но proof backing20 не
становится автоматически proof backing17 или16. Для network left20
нужен prefix m10 на backing20, tails9; для network16 — prefixes14..16
на backing16. Existing backing17 prefix proof и scratch48 proof
(`correct.rs:92–129`) — разные геометрии.

До dispatch составить таблицу покрытия этих backing/region/type/len:
либо source-bound/reviewed перенос (как явно отмеченный D-B4, не новая
машинная проверка), либо полнота конкретных proof_for_contract entries.
В рамках ≤3 entries допустим пересмотр их группировки с символическими
длинами/объектами, без потери клеток/cover. Если нужны дополнительные
entries/preflight, пересчитать cap и STOP при нехватке; не обещать
4 caller+3 callee как заведомо достаточную цепочку.

Для networkN20 не требуется ради одной левой клетки доказывать финальный
merge/правую половину всего N20. Scope результата — именно insertion
региона после реального sort9. Граница наблюдения должна быть привязана
к actual callsite (kani-only wrapper/contract summary с доказанными
premises); source-mapped обёртка может вызывать реальные sort9 + insertion
на том же input backing20/left-region, явно доказывая prefix premise;
это проверка данной цепочки callee и её соответствия callsite, не
динамический proof всего outer caller. Условный prefix-harness с
построением/обоснованным assume+cover помечается условным. Копия network
или переписанная петля insertion не заменяет actual тела. Если такое наблюдение недоступно, STOP/уточнение scope через координатора.

Четыре клетки не закрывают u64, direct18/19, правуюN20, halvesN25..32,
все offset или anylen B4. Смета ≤9 entries `(90+30)×0,0135=$1,62`
одним batch условна полнотой callee coverage и обоих controls; cap$2.
Подробности — [черновик X7](TASK-ext-x7.md), не выданный запуск.

## 6. Полный статический инвентарь source entrypoints

Инвентарь ниже выводится из исходников S_M без Kani/rustc/cargo/CBMC.
Корень подключения — `library/core/src/slice/sort/shared/smallsort.rs:978–980`;
модули — `smallsort/kani_k1.rs:7–15`. `mutations.rs` содержит тела
мутантов, но собственных proof entries нет; их вызывают assembly controls.
Имена макросов развёрнуты статически; line — invocation, для direct fn —
definition. Стандартный `kani list` не запускался. Ordinary означает
включение при `cfg(kani)` без opt-in controls/uninit; это source-ожидание,
которое координатор сверит с настоящим target list в final CI.

### 6.1. Сверка количества

Полная статическая развёртка: **625** proof entries, **355 ordinary** и **270 controls-cfg**. Все строки ниже относятся к кандидату S_M.

| Модуль | Всего | Ordinary | Controls-cfg |
| --- | ---: | ---: | ---: |
| `merge` | 191 | 114 | 77 |
| `network` | 315 | 206 | 109 |
| `assembly` | 18 | 13 | 5 |
| `correct` | 39 | 21 | 18 |
| `smoke` | 3 | 1 | 2 |
| `uninit` | 59 | 0 | 59 |
| `mutations` | 0 | 0 | 0 |

**Сверка:** L1 = 114 merge + 206 network + 13 assembly + 1 smoke = **334**; L2 correct = **21**; итог **355**, расхождение с RESULT W3-L1/L2 = **0**. Ранний macOS также сообщал261+73=334 SmallSort entries. Частичный GCB p2 не является полным инвентарём.

Классы ordinary: 177 safety и178 correctness. Это классификация проверяемых свойств в source, не статусы SUCCESS/FAILED. `control` означает любую исключённую diagnostic/retired/negative entry, включая положительные opt-in эксперименты; это не объявление всех270 отрицательными контролями. У всех270 дополнительный cfg — `kani_smallsort_controls`, у всех625 также действует родительский `cfg(kani)`. Отдельного `kani_smallsort_uninit` на этих proof items нет; U-1 требует uninit-флаг в запросе, один cfg его не включает.

Строка item — proof attribute для прямой функции либо macro invocation; соседняя колонка указывает generating macro. Полный путь — в заголовке модуля. Все контракты в колонке harness относятся к функциям `library/core/src/slice/sort/shared/smallsort.rs`. `N`, backing allocation, длина среза и длина активного региона различаются явно. `lt_u8/lt_u64` означают порядок по x>>1, а не default `<`.

### 6.2. Реестр по модулям

#### `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`

| Expanded entrypoint | Item line | Macro line | Harness / contract | Тип | N / домен | Вид | Проверяемое свойство / назначение | cfg |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `bm_u64_upto8` | 790 | — | `proof_for_contract(bidirectional_merge)` | `u64` | `N=2..8; by_len! invokes bm_len::<u64> for each N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_upto32` | 800 | — | `proof_for_contract(bidirectional_merge)` | `u64` | `N=2..32; by_len! invokes bm_len::<u64> for each N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insert_tail_u64_upto8` | 811 | — | `proof_for_contract(insert_tail)` | `u64` | `region N=2..8; by_len! invokes insert_tail_len::<u64> for each N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_len12` | 823 | — | `proof_for_contract(bidirectional_merge)` | `u64` | `N=12 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_len16` | 830 | — | `proof_for_contract(bidirectional_merge)` | `u64` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_len20` | 841 | — | `proof_for_contract(bidirectional_merge)` | `u64` | `N=20 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_len24` | 848 | — | `proof_for_contract(bidirectional_merge)` | `u64` | `N=24 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_len28` | 855 | — | `proof_for_contract(bidirectional_merge)` | `u64` | `N=28 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `toy_loop_contract` | 873 | — | `proof` | `[u64;32]` | `array N=32; symbolic loop bound n∈0..32` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_len32_plain` | 888 | — | `proof` | `u64, [u64;32]` | `N=32 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_len32_plain_sorted` | 913 | — | `proof` | `u64, [u64;32]` | `N=32 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64_len32` | 934 | — | `proof_for_contract(bidirectional_merge)` | `u64` | `N=32 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort4_u64` | 941 | — | `proof_for_contract(sort4_stable)` | `u64` | `N=4 exact [T;4]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `r11_control_bm_requires` | 950 | — | `proof` | `u64` | `N=4 exact; bidirectional_merge called on [6,0,2,4], deliberately unsorted first half` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort4_all` | 996 | — | `proof_for_contract(sort4_stable)` | `u8, u64, i32` | `N=4 exact [T;4]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort8_all` | 1011 | — | `proof_for_contract(sort8_stable)` | `u8, u64, i32` | `N=8 exact [T;8]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort4_i32` | 1026 | — | `proof_for_contract(sort4_stable)` | `i32` | `N=4 exact [T;4]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort4_b16` | 1033 | — | `proof_for_contract(sort4_stable)` | `[u8;16]` | `N=4 exact [T;4]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort4_b85` | 1040 | — | `proof_for_contract(sort4_stable)` | `[u8;85]` | `N=4 exact [T;4]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w3_sort4_arbitrary_u64` | 1095 | 1076 | `proof` | `u64` | `N=4 exact [T;4]; real sort4 arbitrary comparator, safety + full-value permutation` | safety | real sort4 body with arbitrary volatile-reading comparator; safety and full-value permutation; sortedness is not asserted | `ordinary` |
| `w3_sort4_contract_u64` | 1095 | 1076 | `proof_for_contract(sort4_stable)` | `u64` | `N=4 exact [T;4]; sort4_stable correctness contract` | correctness | proof_for_contract(sort4_stable): sortedness contract under strict comparator | `ordinary` |
| `w3_sort4_arbitrary_b16` | 1096 | 1076 | `proof` | `[u8;16]` | `N=4 exact [T;4]; real sort4 arbitrary comparator, safety + full-value permutation` | safety | real sort4 body with arbitrary volatile-reading comparator; safety and full-value permutation; sortedness is not asserted | `ordinary` |
| `w3_sort4_contract_b16` | 1096 | 1076 | `proof_for_contract(sort4_stable)` | `[u8;16]` | `N=4 exact [T;4]; sort4_stable correctness contract` | correctness | proof_for_contract(sort4_stable): sortedness contract under strict comparator | `ordinary` |
| `w3_sort4_arbitrary_b85` | 1098 | 1076 | `proof` | `[u8;85]` | `N=4 exact [T;4]; real sort4 arbitrary comparator, safety + full-value permutation` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w3_sort4_contract_b85` | 1098 | 1076 | `proof_for_contract(sort4_stable)` | `[u8;85]` | `N=4 exact [T;4]; sort4_stable correctness contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort8_i32` | 1114 | 1100 | `proof_for_contract(sort8_stable)` | `i32` | `N=8 exact [T;8]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort8_u64` | 1116 | 1100 | `proof_for_contract(sort8_stable)` | `u64` | `N=8 exact [T;8]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort8_b16` | 1118 | 1100 | `proof_for_contract(sort8_stable)` | `[u8;16]` | `N=8 exact [T;8]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insert_tail_int` | 1122 | — | `proof_for_contract(insert_tail)` | `i32 \| u64` | `region N=2..16; by_len! all const lengths, type selected nondeterministically` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insert_tail_bytes` | 1136 | — | `proof_for_contract(insert_tail)` | `[u8;16] \| [u8;85]` | `region N=2..16; by_len! all const lengths, array type selected nondeterministically` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u8` | 1165 | 1149 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=2..32 inclusive (by_len! dispatch instantiates bm_len::<T,N> for each length); generic input [T;N]; bidirectional_merge contract path; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_i32` | 1167 | 1149 | `proof_for_contract(bidirectional_merge)` | `i32` | `N=2..32 inclusive (by_len! dispatch instantiates bm_len::<T,N> for each length); generic input [T;N]; bidirectional_merge contract path; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_u64` | 1169 | 1149 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=2..32 inclusive (by_len! dispatch instantiates bm_len::<T,N> for each length); generic input [T;N]; bidirectional_merge contract path; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_b16` | 1171 | 1149 | `proof_for_contract(bidirectional_merge)` | `[u8;16]` | `N=2..32 inclusive (by_len! dispatch instantiates bm_len::<T,N> for each length); generic input [T;N]; bidirectional_merge contract path; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bm_b85` | 1173 | 1149 | `proof_for_contract(bidirectional_merge)` | `[u8;85]` | `N=2..32 inclusive (by_len! dispatch instantiates bm_len::<T,N> for each length); generic input [T;N]; bidirectional_merge contract path; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `general_i32` | 1253 | 1235 | `proof` | `i32` | `N=0..32 inclusive, one exact [T;N] per by_len! dispatch arm; arbitrary input; general_stable_len selected from invocation; sortedness + full-value probe-count comparison; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `general_u64` | 1255 | 1235 | `proof` | `u64` | `N=0..32 inclusive, one exact [T;N] per by_len! dispatch arm; arbitrary input; general_stable_len selected from invocation; sortedness + full-value probe-count comparison; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `general_b16` | 1257 | 1235 | `proof` | `[u8;16]` | `N=0..32 inclusive, one exact [T;N] per by_len! dispatch arm; arbitrary input; general_unstable_len selected from invocation; sortedness + full-value probe-count comparison; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `general_b85` | 1259 | 1235 | `proof` | `[u8;85]` | `N=0..32 inclusive, one exact [T;N] per by_len! dispatch arm; arbitrary input; general_unstable_len selected from invocation; sortedness + full-value probe-count comparison; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `general_u64_len32` | 1282 | 1264 | `proof` | `u64` | `N=32 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w1_control_a_must_fail` | 1312 | — | `proof` | `u64` | `N=4 exact source/destination; direct bidirectional_merge; arbitrary comparator; negative assertion control` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w1_control_a_panic_reachable` | 1335 | — | `proof` | `u64` | `N=4 exact source/destination; direct bidirectional_merge; arbitrary comparator; panic reachability control` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_c5_intrinsic_assume` | 1465 | — | `proof` | `u64` | `helper w2_c5_normal_merge(): fixed four-element merge output; volatile read then intrinsic assume check` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_c5_unchecked_add` | 1477 | — | `proof` | `u8` | `helper w2_c5_normal_merge(): N=4 u64 route; separate u8::MAX unchecked_add overflow control` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_c5_copy_nonoverlapping` | 1490 | — | `proof` | `u64` | `helper w2_c5_normal_merge(): N=4; copy_nonoverlapping src v to v+1 count=3 (overlapping regions)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_c5_ptr_add` | 1503 | — | `proof` | `u64` | `helper w2_c5_normal_merge(): N=4; pointer add offset 5, pointer value not dereferenced` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_control_a_assertion` | 1518 | — | `proof` | `u64` | `w1_merge_safety::<4>(); then scalar u64 false assertion` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_control_a_reachable` | 1528 | — | `proof` | `u64` | `w1_merge_safety::<4>(); assertion/reachability route at N=4` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_a_merge_u64_len32_safety` | 1546 | 1535 | `proof` | `u64` | `N=32 exact [u64;32]` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len2_safety` | 1547 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=2 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len3_safety` | 1548 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=3 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len4_safety` | 1549 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=4 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len5_safety` | 1550 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=5 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len6_safety` | 1551 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=6 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len7_safety` | 1552 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=7 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len8_safety` | 1553 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=8 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len9_safety` | 1554 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=9 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len10_safety` | 1555 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=10 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len11_safety` | 1556 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=11 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len12_safety` | 1557 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=12 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len13_safety` | 1558 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=13 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len14_safety` | 1559 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=14 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len15_safety` | 1560 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=15 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len16_safety` | 1561 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=16 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len17_safety` | 1562 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=17 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len18_safety` | 1563 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=18 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len19_safety` | 1564 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=19 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len20_safety` | 1565 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=20 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len21_safety` | 1566 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=21 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len22_safety` | 1567 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=22 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len23_safety` | 1568 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=23 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len24_safety` | 1569 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=24 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len25_safety` | 1570 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=25 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len26_safety` | 1571 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=26 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len27_safety` | 1572 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=27 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len28_safety` | 1573 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=28 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len29_safety` | 1574 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=29 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len30_safety` | 1575 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=30 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len31_safety` | 1576 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=31 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2_a_all_len32_safety` | 1577 | 1535 | `proof` | `u64, W1GeneralU64 (transparent !Copy u64)` | `N=32 exact [u64;N]; selector chooses direct general(u64), unstable trait(W1GeneralU64), or stable trait(u64,scratch48)` | safety | O1 safety checks with order-violation panic cut; no sortedness/permutation assertion | `ordinary` |
| `w2p2_bm_u64_len2to4` | 1607 | 1582 | `proof_for_contract(bidirectional_merge)` | `u64` | `N∈{2,3,4}, const-generic arm selected by len` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len2to4` | 1608 | 1582 | `proof_for_contract(bidirectional_merge)` | `u8` | `N∈{2,3,4}, const-generic arm selected by len` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_r11_u64` | 1641 | 1620 | `proof` | `u64` | `N=4 exact; fixed input [T;4]=[6,0,2,4], MaybeUninit<[T;4]> output; deliberate sorted-halves requires violation (first pair [6,0]); comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_r11_u8` | 1643 | 1620 | `proof` | `u8` | `N=4 exact; fixed input [T;4]=[6,0,2,4], MaybeUninit<[T;4]> output; deliberate sorted-halves requires violation (first pair [6,0]); comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_bm_u64_len5` | 1723 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=5 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len5` | 1724 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=5 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len6` | 1725 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=6 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len6` | 1726 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=6 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len7` | 1727 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=7 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len7` | 1728 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=7 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len8` | 1729 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=8 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len8` | 1730 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=8 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len9` | 1731 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=9 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len9` | 1732 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=9 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len10` | 1733 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=10 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len10` | 1734 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=10 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len11` | 1735 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=11 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len11` | 1736 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=11 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len12` | 1737 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=12 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len12` | 1738 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=12 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len13` | 1739 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=13 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len13` | 1740 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=13 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len14` | 1741 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=14 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len14` | 1742 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=14 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len15` | 1743 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=15 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len15` | 1744 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=15 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u64_len16` | 1745 | 1610 | `proof_for_contract(bidirectional_merge)` | `u64` | `N=16 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_bm_u8_len16` | 1746 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=16 exact [T;N]` | correctness | proof_for_contract(bidirectional_merge): merge sortedness/permutation contract | `ordinary` |
| `w2p2_gs_u64_len0` | 1747 | 1699 | `proof` | `u64` | `N=0 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len0` | 1748 | 1699 | `proof` | `u8` | `N=0 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len0` | 1749 | 1710 | `proof` | `u8 \| u64` | `N=0 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u64_len1` | 1750 | 1699 | `proof` | `u64` | `N=1 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len1` | 1751 | 1699 | `proof` | `u8` | `N=1 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len1` | 1752 | 1710 | `proof` | `u8 \| u64` | `N=1 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u64_len2` | 1753 | 1699 | `proof` | `u64` | `N=2 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len2` | 1754 | 1699 | `proof` | `u8` | `N=2 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len2` | 1755 | 1710 | `proof` | `u8 \| u64` | `N=2 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u64_len3` | 1756 | 1699 | `proof` | `u64` | `N=3 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len3` | 1757 | 1699 | `proof` | `u8` | `N=3 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len3` | 1758 | 1710 | `proof` | `u8 \| u64` | `N=3 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u64_len4` | 1759 | 1699 | `proof` | `u64` | `N=4 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len4` | 1760 | 1699 | `proof` | `u8` | `N=4 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len4` | 1761 | 1710 | `proof` | `u8 \| u64` | `N=4 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u64_len5` | 1762 | 1699 | `proof` | `u64` | `N=5 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len5` | 1763 | 1699 | `proof` | `u8` | `N=5 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len5` | 1764 | 1710 | `proof` | `u8 \| u64` | `N=5 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u64_len6` | 1765 | 1699 | `proof` | `u64` | `N=6 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len6` | 1766 | 1699 | `proof` | `u8` | `N=6 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len6` | 1767 | 1710 | `proof` | `u8 \| u64` | `N=6 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u64_len7` | 1768 | 1699 | `proof` | `u64` | `N=7 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len7` | 1769 | 1699 | `proof` | `u8` | `N=7 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len7` | 1770 | 1710 | `proof` | `u8 \| u64` | `N=7 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u64_len8` | 1771 | 1699 | `proof` | `u64` | `N=8 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len8` | 1772 | 1699 | `proof` | `u8` | `N=8 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len8` | 1774 | 1710 | `proof` | `u8 \| u64` | `N=8 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u64_len9` | 1775 | 1699 | `proof` | `u64` | `N=9 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len9` | 1776 | 1699 | `proof` | `u8` | `N=9 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len9` | 1778 | 1710 | `proof` | `u8 \| u64` | `N=9 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u64_len10` | 1779 | 1699 | `proof` | `u64` | `N=10 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len10` | 1780 | 1699 | `proof` | `u8` | `N=10 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len10` | 1782 | 1710 | `proof` | `u8 \| u64` | `N=10 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u64_len11` | 1783 | 1699 | `proof` | `u64` | `N=11 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len11` | 1784 | 1699 | `proof` | `u8` | `N=11 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len11` | 1786 | 1710 | `proof` | `u8 \| u64` | `N=11 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u64_len12` | 1787 | 1699 | `proof` | `u64` | `N=12 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len12` | 1788 | 1699 | `proof` | `u8` | `N=12 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len12` | 1790 | 1710 | `proof` | `u8 \| u64` | `N=12 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u64_len13` | 1792 | 1699 | `proof` | `u64` | `N=13 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u8_len13` | 1793 | 1699 | `proof` | `u8` | `N=13 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len13` | 1795 | 1710 | `proof` | `u8 \| u64` | `N=13 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u64_len14` | 1797 | 1699 | `proof` | `u64` | `N=14 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u8_len14` | 1799 | 1699 | `proof` | `u8` | `N=14 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_fallback_len14` | 1801 | 1710 | `proof` | `u8 \| u64` | `N=14 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u64_len15` | 1803 | 1699 | `proof` | `u64` | `N=15 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u8_len15` | 1805 | 1699 | `proof` | `u8` | `N=15 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_fallback_len15` | 1807 | 1710 | `proof` | `u8 \| u64` | `N=15 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_gs_u64_len16` | 1808 | 1699 | `proof` | `u64` | `N=16 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_gs_u8_len16` | 1809 | 1699 | `proof` | `u8` | `N=16 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2p2_fallback_len16` | 1811 | 1710 | `proof` | `u8 \| u64` | `N=16 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_fallback_u64_len8` | 1826 | 1815 | `proof` | `u64` | `N=8 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_fallback_u8_len8` | 1827 | 1815 | `proof` | `u8` | `N=8 exact [T;N]` | correctness | sorted output + full-value probe multiplicity (permutation), strict comparator | `ordinary` |
| `w2night_fallback_u8_len9` | 1829 | 1815 | `proof` | `u8` | `N=9 exact [T;N]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_k12a_bm_u8_len20` | 1834 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=20 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_k12a_bm_u8_len24` | 1836 | 1610 | `proof_for_contract(bidirectional_merge)` | `u8` | `N=24 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_drop_control_a` | 1962 | — | `proof` | `W2NightDrop` | `w2night_drop_run::<2,true,false,0>(); exact N=2 route control; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_drop_reachable` | 1974 | 1937 | `proof` | `W2NightDrop` | `N=2; upper general/stable; W2NightDrop; Drop reachability; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_drop_low2_count` | 1975 | 1937 | `proof` | `W2NightDrop` | `N=2; lower fallback; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_low2_perm` | 1976 | 1937 | `proof` | `W2NightDrop` | `N=2; lower fallback; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_low4_count` | 1977 | 1937 | `proof` | `W2NightDrop` | `N=4; lower fallback; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_low4_perm` | 1978 | 1937 | `proof` | `W2NightDrop` | `N=4; lower fallback; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_low8_count` | 1979 | 1937 | `proof` | `W2NightDrop` | `N=8; lower fallback; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_low8_perm` | 1980 | 1937 | `proof` | `W2NightDrop` | `N=8; lower fallback; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper2_count` | 1981 | 1937 | `proof` | `W2NightDrop` | `N=2; upper general/stable; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper2_perm` | 1982 | 1937 | `proof` | `W2NightDrop` | `N=2; upper general/stable; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper4_count` | 1983 | 1937 | `proof` | `W2NightDrop` | `N=4; upper general/stable; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper4_perm` | 1984 | 1937 | `proof` | `W2NightDrop` | `N=4; upper general/stable; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper8_count` | 1985 | 1937 | `proof` | `W2NightDrop` | `N=8; upper general/stable; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper8_perm` | 1986 | 1937 | `proof` | `W2NightDrop` | `N=8; upper general/stable; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper16_count` | 1987 | 1937 | `proof` | `W2NightDrop` | `N=16; upper general/stable; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper16_perm` | 1988 | 1937 | `proof` | `W2NightDrop` | `N=16; upper general/stable; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | safety | normal-return O2: tag multiplicity if PERM=true, Drop count=N otherwise; read-only arbitrary comparator; no sortedness/full-value permutation assertion | `ordinary` |
| `w2night_drop_upper24_count` | 1990 | 1937 | `proof` | `W2NightDrop` | `N=24; upper general/stable; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_drop_upper24_perm` | 1992 | 1937 | `proof` | `W2NightDrop` | `N=24; upper general/stable; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_drop_upper32_count` | 1994 | 1937 | `proof` | `W2NightDrop` | `N=32; upper general/stable; W2NightDrop; Drop count; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_drop_upper32_perm` | 1996 | 1937 | `proof` | `W2NightDrop` | `N=32; upper general/stable; W2NightDrop; identity tag multiplicity; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_drop_duplicate_tag_control` | 1999 | — | `proof` | `W2NightDrop` | `w2night_drop_run::<2,false,true,1>(); exact N=2 duplicate-tag control; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2night_drop_extra_drop_control` | 2008 | — | `proof` | `W2NightDrop` | `exact N=2 extra-drop control via w2night_drop_run helper; lower=fallback or insertion(offset1), upper=general or stable-Freeze(scratch48), by selector` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `ext_b4_u64_n16` | 2069 | 2058 | `proof` | `u64` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `ext_b4_u64_n17` | 2071 | 2058 | `proof` | `u64` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `ext_b4_u64_n18` | 2073 | 2058 | `proof` | `u64` | `N=18 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `ext_b4_u64_n19` | 2075 | 2058 | `proof` | `u64` | `N=19 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `ext_b4_u64_n20` | 2077 | 2058 | `proof` | `u64` | `N=20 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |

#### `library/core/src/slice/sort/shared/smallsort/kani_k1/network.rs`

| Expanded entrypoint | Item line | Macro line | Harness / contract | Тип | N / домен | Вид | Проверяемое свойство / назначение | cfg |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `swap_if_less_u8` | 35 | — | `proof_for_contract(swap_if_less)` | `u8` | `N=2 exact [T;2]; indices 0,1; swap/no-swap contract and unchanged frame` | correctness | proof_for_contract(swap_if_less): swapped pair and exact untouched-frame contract | `ordinary` |
| `swap_if_less_i32` | 40 | — | `proof_for_contract(swap_if_less)` | `i32` | `N=2 exact [T;2]; indices 0,1; swap/no-swap contract and unchanged frame` | correctness | proof_for_contract(swap_if_less): swapped pair and exact untouched-frame contract | `ordinary` |
| `swap_if_less_u64` | 45 | — | `proof_for_contract(swap_if_less)` | `u64` | `N=2 exact [T;2]; indices 0,1; swap/no-swap contract and unchanged frame` | correctness | proof_for_contract(swap_if_less): swapped pair and exact untouched-frame contract | `ordinary` |
| `r11_control_swap_if_less_requires` | 54 | — | `proof` | `u8` | `N=2 exact [u8;2]; calls swap_if_less at indices (1,1), deliberate requires violation` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_u8` | 105 | 83 | `proof_for_contract($f)` | `u8` | `Backing [T;17]; runtime len N..=17 with N=9; calls network on v[..len]; contract covers/sorts prefix N and harness checks unchanged suffix v[N..]; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_i32` | 107 | 83 | `proof_for_contract($f)` | `i32` | `Backing [T;17]; runtime len N..=17 with N=9; calls network on v[..len]; contract covers/sorts prefix N and harness checks unchanged suffix v[N..]; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_u64` | 109 | 83 | `proof_for_contract($f)` | `u64` | `Backing [T;17]; runtime len N..=17 with N=9; calls network on v[..len]; contract covers/sorts prefix N and harness checks unchanged suffix v[N..]; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_u8` | 111 | 83 | `proof_for_contract($f)` | `u8` | `Backing [T;17]; runtime len N..=17 with N=13; calls network on v[..len]; contract covers/sorts prefix N and harness checks unchanged suffix v[N..]; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_i32` | 113 | 83 | `proof_for_contract($f)` | `i32` | `Backing [T;17]; runtime len N..=17 with N=13; calls network on v[..len]; contract covers/sorts prefix N and harness checks unchanged suffix v[N..]; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_u64` | 115 | 83 | `proof_for_contract($f)` | `u64` | `Backing [T;17]; runtime len N..=17 with N=13; calls network on v[..len]; contract covers/sorts prefix N and harness checks unchanged suffix v[N..]; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_perm_stub_u8` | 203 | 178 | `proof` | `u8` | `Backing [T;17]; runtime len N..=17 with N=13; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; compare-exchanges stubbed through swap_if_less contract; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_perm_stub_i32` | 205 | 178 | `proof` | `i32` | `Backing [T;17]; runtime len N..=17 with N=13; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; compare-exchanges stubbed through swap_if_less contract; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_perm_stub_u64` | 207 | 178 | `proof` | `u64` | `Backing [T;17]; runtime len N..=17 with N=13; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; compare-exchanges stubbed through swap_if_less contract; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_perm_stub_u64` | 209 | 178 | `proof` | `u64` | `Backing [T;17]; runtime len N..=17 with N=9; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; compare-exchanges stubbed through swap_if_less contract; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_01_u8` | 212 | 126 | `proof_for_contract($f)` | `u8` | `Backing [T;17]; bits [u8;9] arbitrary; initialize v[..9] to values 0..=3 (keys 0/1), v[9..] arbitrary; runtime len 9..=17; call v[..len], unchanged suffix from N; comparator key x>>1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_01_i32` | 214 | 126 | `proof_for_contract($f)` | `i32` | `Backing [T;17]; bits [u8;9] arbitrary; initialize v[..9] to values 0..=3 (keys 0/1), v[9..] arbitrary; runtime len 9..=17; call v[..len], unchanged suffix from N; comparator key x>>1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_01_u64` | 216 | 126 | `proof_for_contract($f)` | `u64` | `Backing [T;17]; bits [u8;9] arbitrary; initialize v[..9] to values 0..=3 (keys 0/1), v[9..] arbitrary; runtime len 9..=17; call v[..len], unchanged suffix from N; comparator key x>>1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_01_u8` | 218 | 126 | `proof_for_contract($f)` | `u8` | `Backing [T;17]; bits [u8;13] arbitrary; initialize v[..13] to values 0..=3 (keys 0/1), v[13..] arbitrary; runtime len 13..=17; call v[..len], unchanged suffix from N; comparator key x>>1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_01_i32` | 220 | 126 | `proof_for_contract($f)` | `i32` | `Backing [T;17]; bits [u8;13] arbitrary; initialize v[..13] to values 0..=3 (keys 0/1), v[13..] arbitrary; runtime len 13..=17; call v[..len], unchanged suffix from N; comparator key x>>1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_01_u64` | 222 | 126 | `proof_for_contract($f)` | `u64` | `Backing [T;17]; bits [u8;13] arbitrary; initialize v[..13] to values 0..=3 (keys 0/1), v[13..] arbitrary; runtime len 13..=17; call v[..len], unchanged suffix from N; comparator key x>>1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_perm_u8` | 224 | 153 | `proof` | `u8` | `Backing [T;17]; runtime len N..=17 with N=9; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; real network body; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_perm_i32` | 226 | 153 | `proof` | `i32` | `Backing [T;17]; runtime len N..=17 with N=9; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; real network body; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort9_perm_u64` | 228 | 153 | `proof` | `u64` | `Backing [T;17]; runtime len N..=17 with N=9; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; real network body; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_perm_u8` | 230 | 153 | `proof` | `u8` | `Backing [T;17]; runtime len N..=17 with N=13; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; real network body; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_perm_i32` | 232 | 153 | `proof` | `i32` | `Backing [T;17]; runtime len N..=17 with N=13; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; real network body; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `sort13_perm_u64` | 234 | 153 | `proof` | `u64` | `Backing [T;17]; runtime len N..=17 with N=13; call network on v[..len]; full-width input; compare probe-count over first N and verify v[N..] unchanged; real network body; comparator invocation lt_*` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_inv_o1_u64` | 272 | — | `proof_for_contract(insertion_sort_shift_left)` | `u64` | `N=8 exact [u64;8]; insertion_sort_shift_left offset=1; insertion/insert_tail contract harness` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o1_u8` | 306 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `u8` | `Backing [T;8]; runtime len 2..=8; calls insertion_sort_shift_left(v[..len], offset=1); insertion region begins at offset 1 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o9_u8` | 308 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `u8` | `Backing [T;12]; runtime len 9..=12; calls insertion_sort_shift_left(v[..len], offset=9); insertion region begins at offset 9 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o13_u8` | 310 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `u8` | `Backing [T;17]; runtime len 13..=17; calls insertion_sort_shift_left(v[..len], offset=13); insertion region begins at offset 13 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o1_i32` | 312 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `i32` | `Backing [T;8]; runtime len 2..=8; calls insertion_sort_shift_left(v[..len], offset=1); insertion region begins at offset 1 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o9_i32` | 314 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `i32` | `Backing [T;12]; runtime len 9..=12; calls insertion_sort_shift_left(v[..len], offset=9); insertion region begins at offset 9 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o13_i32` | 316 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `i32` | `Backing [T;17]; runtime len 13..=17; calls insertion_sort_shift_left(v[..len], offset=13); insertion region begins at offset 13 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o1_u64` | 318 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `u64` | `Backing [T;8]; runtime len 2..=8; calls insertion_sort_shift_left(v[..len], offset=1); insertion region begins at offset 1 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o9_u64` | 320 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `u64` | `Backing [T;12]; runtime len 9..=12; calls insertion_sort_shift_left(v[..len], offset=9); insertion region begins at offset 9 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insertion_o13_u64` | 322 | 289 | `proof_for_contract(insertion_sort_shift_left)` | `u64` | `Backing [T;17]; runtime len 13..=17; calls insertion_sort_shift_left(v[..len], offset=13); insertion region begins at offset 13 (argument exact)` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `network_upto17_u8` | 360 | 328 | `proof` | `u8` | `Backing [T;17]; runtime len N=0..=17; calls UnstableSmallSortFreezeTypeImpl::small_sort on v[..len]; checks sortedness, full-value probe-count permutation of active prefix, and unchanged suffix v[len..]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `network_upto17_i32` | 362 | 328 | `proof` | `i32` | `Backing [T;17]; runtime len N=0..=17; calls UnstableSmallSortFreezeTypeImpl::small_sort on v[..len]; checks sortedness, full-value probe-count permutation of active prefix, and unchanged suffix v[len..]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `network_upto17_u64` | 364 | 328 | `proof` | `u64` | `Backing [T;17]; runtime len N=0..=17; calls UnstableSmallSortFreezeTypeImpl::small_sort on v[..len]; checks sortedness, full-value probe-count permutation of active prefix, and unchanged suffix v[len..]` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insert_tail_net_u8` | 433 | 401 | `proof_for_contract(insert_tail)` | `u8` | `Exact helper input [T;N] = kani::any() for each N=2..17; runtime selector dispatches len 2..17 to compile-time insert_tail_len::<T,N>; insert_tail call spans whole [begin,tail] region (tail=N-1).` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insert_tail_net_i32` | 435 | 401 | `proof_for_contract(insert_tail)` | `i32` | `Exact helper input [T;N] = kani::any() for each N=2..17; runtime selector dispatches len 2..17 to compile-time insert_tail_len::<T,N>; insert_tail call spans whole [begin,tail] region (tail=N-1).` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insert_tail_net_u64` | 437 | 401 | `proof_for_contract(insert_tail)` | `u64` | `Exact helper input [T;N] = kani::any() for each N=2..17; runtime selector dispatches len 2..17 to compile-time insert_tail_len::<T,N>; insert_tail call spans whole [begin,tail] region (tail=N-1).` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insert_tail_prefix_u64` | 443 | — | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; tail∈1..16; prefix region size 2..17; suffix frame` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `insert_tail_region_u64` | 464 | — | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start∈0..tail-1, tail∈1..16; arbitrary interior region and outside frame` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w1_network_o1_len17_u64` | 505 | — | `proof` | `u64` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w1_network_o1_nomerge_u64` | 545 | 526 | `proof` | `u64` | `N in {0,1,...,17}; independent const-generic arm, exact [u64;N]; actual unstable Freeze/network route, arbitrary CD-2 comparator` | safety | O1 no-merge safety and normal-return covers; no sortedness or permutation assertions | `ordinary` |
| `bandt0_8_u8` | 578 | 551 | `proof` | `u8` | `Backing [T;8]; runtime len N=0..=8 inclusive; small_sort operates on v[..len]; insertion from offset 1; no presort network prefix; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bandt0_8_i32` | 580 | 551 | `proof` | `i32` | `Backing [T;8]; runtime len N=0..=8 inclusive; small_sort operates on v[..len]; insertion from offset 1; no presort network prefix; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bandt0_8_u64` | 582 | 551 | `proof` | `u64` | `Backing [T;8]; runtime len N=0..=8 inclusive; small_sort operates on v[..len]; insertion from offset 1; no presort network prefix; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bandt9_12_u8` | 584 | 551 | `proof` | `u8` | `Backing [T;12]; runtime len N=9..=12 inclusive; small_sort operates on v[..len]; sort9 presort prefix [0..9), then insertion from offset 9; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bandt9_12_i32` | 586 | 551 | `proof` | `i32` | `Backing [T;12]; runtime len N=9..=12 inclusive; small_sort operates on v[..len]; sort9 presort prefix [0..9), then insertion from offset 9; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bandt9_12_u64` | 588 | 551 | `proof` | `u64` | `Backing [T;12]; runtime len N=9..=12 inclusive; small_sort operates on v[..len]; sort9 presort prefix [0..9), then insertion from offset 9; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bandt13_17_u8` | 590 | 551 | `proof` | `u8` | `Backing [T;17]; runtime len N=13..=17 inclusive; small_sort operates on v[..len]; sort13 presort prefix [0..13), then insertion from offset 13; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bandt13_17_i32` | 592 | 551 | `proof` | `i32` | `Backing [T;17]; runtime len N=13..=17 inclusive; small_sort operates on v[..len]; sort13 presort prefix [0..13), then insertion from offset 13; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `bandt13_17_u64` | 594 | 551 | `proof` | `u64` | `Backing [T;17]; runtime len N=13..=17 inclusive; small_sort operates on v[..len]; sort13 presort prefix [0..13), then insertion from offset 13; checks sortedness, active-prefix permutation, unchanged suffix; insert_tail also stubbed by verified contract` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `fixed8_u64` | 622 | 599 | `proof` | `u64` | `Backing [T;8] and exact runtime N=8; small_sort operates on full v[..]; checks sortedness and full-value probe-count permutation` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `fixed12_u64` | 624 | 599 | `proof` | `u64` | `Backing [T;12] and exact runtime N=12; small_sort operates on full v[..]; checks sortedness and full-value probe-count permutation` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `fixed17_u64` | 626 | 599 | `proof` | `u64` | `Backing [T;17] and exact runtime N=17; small_sort operates on full v[..]; checks sortedness and full-value probe-count permutation` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `fixedt8_u64` | 633 | — | `proof` | `u64` | `N=8 exact [u64;8]; real unstable trait/network, insert_tail verified stub off-path at this N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band0_8_u8` | 650 | 374 | `proof` | `u8` | `Backing [T;8]; runtime len N=0..=8 inclusive; small_sort operates on v[..len]; insertion from offset 1; no presort network prefix; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band0_8_i32` | 652 | 374 | `proof` | `i32` | `Backing [T;8]; runtime len N=0..=8 inclusive; small_sort operates on v[..len]; insertion from offset 1; no presort network prefix; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band0_8_u64` | 654 | 374 | `proof` | `u64` | `Backing [T;8]; runtime len N=0..=8 inclusive; small_sort operates on v[..len]; insertion from offset 1; no presort network prefix; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band9_12_u8` | 656 | 374 | `proof` | `u8` | `Backing [T;12]; runtime len N=9..=12 inclusive; small_sort operates on v[..len]; sort9 presort prefix [0..9), then insertion from offset 9; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band9_12_i32` | 658 | 374 | `proof` | `i32` | `Backing [T;12]; runtime len N=9..=12 inclusive; small_sort operates on v[..len]; sort9 presort prefix [0..9), then insertion from offset 9; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band9_12_u64` | 660 | 374 | `proof` | `u64` | `Backing [T;12]; runtime len N=9..=12 inclusive; small_sort operates on v[..len]; sort9 presort prefix [0..9), then insertion from offset 9; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band13_17_u8` | 662 | 374 | `proof` | `u8` | `Backing [T;17]; runtime len N=13..=17 inclusive; small_sort operates on v[..len]; sort13 presort prefix [0..13), then insertion from offset 13; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band13_17_i32` | 664 | 374 | `proof` | `i32` | `Backing [T;17]; runtime len N=13..=17 inclusive; small_sort operates on v[..len]; sort13 presort prefix [0..13), then insertion from offset 13; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `band13_17_u64` | 666 | 374 | `proof` | `u64` | `Backing [T;17]; runtime len N=13..=17 inclusive; small_sort operates on v[..len]; sort13 presort prefix [0..13), then insertion from offset 13; checks sortedness, active-prefix permutation, unchanged suffix` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w1_sort13_perm_fixed_u8` | 688 | — | `proof` | `u8` | `N=13 exact [u8;13]; sort13_optimal; full-value probe permutation` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `direct_sort9_u8` | 714 | — | `proof` | `u8` | `N=9 exact [u8;9]; real sort9_optimal; sortedness + full-value probe permutation` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `contract_sort9_u8_len9` | 727 | — | `proof_for_contract(sort9_optimal)` | `u8, [u8;9]` | `N=9 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `direct_network_len13_u8` | 749 | — | `proof` | `u8` | `N=13 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `direct_network_len17_u8` | 756 | — | `proof` | `u8` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k13_routes_0_8` | 913 | 876 | `proof` | `Cell<K13Tagged>` | `N∈{0,1,2,3,4,5,6,7,8}; exact K13 route/insertion helper instantiations` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k13_routes_9_16` | 915 | 876 | `proof` | `Cell<K13Tagged>` | `N∈{9,10,11,12,13,14,15,16}; exact K13 route/insertion helper instantiations` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k13_insertion_1_10` | 917 | 896 | `proof` | `Cell<K13Tagged>` | `N∈{1,2,3,4,5,6,7,8,9,10}; exact K13 route/insertion helper instantiations` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k13_insertion_11_20` | 919 | 896 | `proof` | `Cell<K13Tagged>` | `N∈{11,12,13,14,15,16,17,18,19,20}; exact K13 route/insertion helper instantiations` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k13_safety_all` | 926 | — | `proof` | `Cell<K13Tagged>` | `backing N=20; mode stable/unstable len 0..16, or direct insertion len 1..20 with offset 1..len` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k13_small_permutation` | 967 | — | `proof` | `Cell<K13Tagged>` | `len∈0..4; stable/unstable/insertion modes; reduced tagged permutation domain` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_control_a_assertion` | 1014 | — | `proof` | `u64` | `N=2 exact [u64;2]; unstable trait route with arbitrary comparator; deliberate false assertion` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_control_a_reachability` | 1027 | — | `proof` | `u64` | `N=18 exact [u64;18]; unstable trait route reaches merge normal return` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_network_o1_a_18_21` | 1062 | 1045 | `proof` | `u64` | `N∈18..21; exact u64 arrays; O1 safety-only route` | safety | normal-return and memory-safety checks under arbitrary comparator; no sortedness/permutation assertion | `ordinary` |
| `w2_network_o1_a_22_25` | 1063 | 1045 | `proof` | `u64` | `N∈22..25; exact u64 arrays; O1 safety-only route` | safety | normal-return and memory-safety checks under arbitrary comparator; no sortedness/permutation assertion | `ordinary` |
| `w2_network_o1_a_26_27` | 1064 | 1045 | `proof` | `u64` | `N∈26..27; exact u64 arrays; O1 safety-only route` | safety | normal-return and memory-safety checks under arbitrary comparator; no sortedness/permutation assertion | `ordinary` |
| `w2_network_o1_a_28_29` | 1065 | 1045 | `proof` | `u64` | `N∈28..29; exact u64 arrays; O1 safety-only route` | safety | normal-return and memory-safety checks under arbitrary comparator; no sortedness/permutation assertion | `ordinary` |
| `w2_network_o1_a_30_32` | 1066 | 1045 | `proof` | `u64` | `N∈30..32; exact u64 arrays; O1 safety-only route` | safety | normal-return and memory-safety checks under arbitrary comparator; no sortedness/permutation assertion | `ordinary` |
| `w2_control_a_quiet_assertion` | 1122 | — | `proof` | `u8` | `w2_network_o1_fixed::<2>(); then scalar u8 false assertion` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_k16_zst_stable` | 1133 | 1103 | `proof` | `()` | `N∈{0,1,2,7,8,15,16,17,31,32}; exact [T;N]; stable route` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_k16_zst_network_short` | 1135 | 1103 | `proof` | `()` | `N∈{8,9,12,13,17}; exact [T;N]; unstable/network/general route` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_k16_u8_stable_lo` | 1137 | 1103 | `proof` | `u8` | `N∈{0,1,2,7,8}; exact [T;N]; stable route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u8_stable_mid` | 1138 | 1103 | `proof` | `u8` | `N∈{15,16,17}; exact [T;N]; stable route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u8_stable_hi` | 1139 | 1103 | `proof` | `u8` | `N∈{31,32}; exact [T;N]; stable route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u8_network_short` | 1140 | 1103 | `proof` | `u8` | `N∈{8,9,12,13,17}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u8_network_merge` | 1141 | 1103 | `proof` | `u8` | `N∈{18,31,32}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u128_lo` | 1172 | 1148 | `proof` | `u128` | `N∈{0,1,2,7,8}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u128_mid` | 1173 | 1148 | `proof` | `u128` | `N∈{15,16,17}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u128_hi` | 1175 | 1148 | `proof` | `u128` | `N∈{31,32}; exact [T;N]; unstable/network/general route` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_control_a_quiet_merge_assertion` | 1180 | — | `proof` | `u8` | `w2_type_fixed::<u8,18,false>(); then scalar false assertion` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_k16_u8_stable_reach` | 1203 | 1191 | `proof` | `u8` | `N=17 exact [T;N]; stable trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u8_network_reach` | 1204 | 1191 | `proof` | `u8` | `N=18 exact [T;N]; unstable/general trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u128_stable_reach` | 1205 | 1191 | `proof` | `u128` | `N=17 exact [T;N]; stable trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u128_general_reach` | 1206 | 1191 | `proof` | `u128` | `N=17 exact [T;N]; unstable/general trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a16_lo` | 1212 | 1148 | `proof` | `[u8;16]` | `N∈{0,1,2,7,8}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a16_mid` | 1213 | 1148 | `proof` | `[u8;16]` | `N∈{15,16,17}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a16_n31` | 1214 | 1148 | `proof` | `[u8;16]` | `N∈{31}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a16_n32` | 1215 | 1148 | `proof` | `[u8;16]` | `N∈{32}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a16_stable_reach` | 1216 | 1191 | `proof` | `[u8;16]` | `N=17 exact [T;N]; stable trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a16_general_reach` | 1217 | 1191 | `proof` | `[u8;16]` | `N=17 exact [T;N]; unstable/general trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u128_n31` | 1219 | 1148 | `proof` | `u128` | `N∈{31}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_u128_n32` | 1220 | 1148 | `proof` | `u128` | `N∈{32}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a17_lo` | 1222 | 1148 | `proof` | `[u8;17]` | `N∈{0,1,2,7,8}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a17_mid` | 1223 | 1148 | `proof` | `[u8;17]` | `N∈{15,16,17}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a17_n31` | 1224 | 1148 | `proof` | `[u8;17]` | `N∈{31}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a17_n32` | 1225 | 1148 | `proof` | `[u8;17]` | `N∈{32}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a17_stable_reach` | 1226 | 1191 | `proof` | `[u8;17]` | `N=17 exact [T;N]; stable trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a17_general_reach` | 1227 | 1191 | `proof` | `[u8;17]` | `N=17 exact [T;N]; unstable/general trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_drop_lo` | 1244 | 1148 | `proof` | `W2Drop` | `N∈{0,1,2,7,8}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_drop_mid` | 1245 | 1148 | `proof` | `W2Drop` | `N∈{15,16,17}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_drop_n31` | 1246 | 1148 | `proof` | `W2Drop` | `N∈{31}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_drop_n32` | 1247 | 1148 | `proof` | `W2Drop` | `N∈{32}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_drop_stable_reach` | 1248 | 1191 | `proof` | `W2Drop` | `N=17 exact [T;N]; stable trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_drop_general_reach` | 1249 | 1191 | `proof` | `W2Drop` | `N=17 exact [T;N]; unstable/general trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_cell_nonfreeze` | 1256 | 1148 | `proof` | `Cell<i32>` | `N∈{0,1,2,15,16}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w3_k16_i32_freeze` | 1263 | 1148 | `proof` | `i32` | `N∈{0,1,2,15,16}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a85_lo` | 1265 | 1148 | `proof` | `[u8;85]` | `N∈{0,1,2,7,8}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a85_mid` | 1266 | 1148 | `proof` | `[u8;85]` | `N∈{15,16,17}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a85_n31` | 1267 | 1148 | `proof` | `[u8;85]` | `N∈{31}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a85_n32` | 1268 | 1148 | `proof` | `[u8;85]` | `N∈{32}; exact [T;N]; unstable/network/general route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a85_stable_reach` | 1269 | 1191 | `proof` | `[u8;85]` | `N=17 exact [T;N]; stable trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a85_general_reach` | 1270 | 1191 | `proof` | `[u8;85]` | `N=17 exact [T;N]; unstable/general trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a86_stable_lo` | 1272 | 1103 | `proof` | `[u8;86]` | `N∈{0,1,2,7,8}; exact [T;N]; stable route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a86_stable_mid` | 1273 | 1103 | `proof` | `[u8;86]` | `N∈{15,16,17}; exact [T;N]; stable route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a86_stable_n31` | 1274 | 1103 | `proof` | `[u8;86]` | `N∈{31}; exact [T;N]; stable route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a86_stable_n32` | 1275 | 1103 | `proof` | `[u8;86]` | `N∈{32}; exact [T;N]; stable route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a86_fallback` | 1276 | 1103 | `proof` | `[u8;86]` | `N∈{0,1,2,15,16}; exact [T;N]; unstable fallback route` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k16_a86_stable_reach` | 1277 | 1191 | `proof` | `[u8;86]` | `N=17 exact [T;N]; stable trait route; safety/normal-return witness` | safety | K16 trait/type route safety matrix; normal return and default Kani safety checks, no sortedness/permutation claim | `ordinary` |
| `w2_k11s_1_5` | 1339 | 1323 | `proof` | `u64` | `N∈{1,2,3,4,5}; exact [u64;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_k11s_6_10` | 1340 | 1323 | `proof` | `u64` | `N∈{6,7,8,9,10}; exact [u64;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_k11s_11_15` | 1342 | 1323 | `proof` | `u64` | `N∈{11,12,13,14,15}; exact [u64;N]; offset∈1..=N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_k11s_16_20` | 1344 | 1323 | `proof` | `u64` | `N∈{16,17,18,19,20}; exact [u64;N]; offset∈1..=N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_o3_routes_0_4` | 1420 | 1376 | `proof` | `Cell<K13Tagged>` | `N∈{0,1,2,3,4}; exact [Cell<K13Tagged>;N]; stable/unstable route selector` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_routes_5_8` | 1421 | 1376 | `proof` | `Cell<K13Tagged>` | `N∈{5,6,7,8}; exact [Cell<K13Tagged>;N]; stable/unstable route selector` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_routes_9_12` | 1422 | 1376 | `proof` | `Cell<K13Tagged>` | `N∈{9,10,11,12}; exact [Cell<K13Tagged>;N]; stable/unstable route selector` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_routes_13_16` | 1423 | 1376 | `proof` | `Cell<K13Tagged>` | `N∈{13,14,15,16}; exact [Cell<K13Tagged>;N]; stable/unstable route selector` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_insertion_1_5` | 1424 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{1,2,3,4,5}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_insertion_6_10` | 1425 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{6,7,8,9,10}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_insertion_11_15` | 1427 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{11,12,13,14,15}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_o3_insertion_16_20` | 1429 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{16,17,18,19,20}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_k11s_11_12` | 1432 | 1323 | `proof` | `u64` | `N∈{11,12}; exact [u64;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_k11s_13_15` | 1434 | 1323 | `proof` | `u64` | `N∈{13,14,15}; exact [u64;N]; offset∈1..=N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_o3_insertion_11_12` | 1435 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{11,12}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_insertion_13_15` | 1437 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{13,14,15}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_k11s_n13` | 1440 | 1323 | `proof` | `u64` | `N∈{13}; exact [u64;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_k11s_n14` | 1441 | 1323 | `proof` | `u64` | `N∈{14}; exact [u64;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_k11s_n15` | 1443 | 1323 | `proof` | `u64` | `N∈{15}; exact [u64;N]; offset∈1..=N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2_o3_insertion_n13` | 1444 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{13}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_insertion_n14` | 1445 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{14}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2_o3_insertion_n15` | 1447 | 1404 | `proof` | `Cell<K13Tagged>` | `N∈{15}; exact [Cell<K13Tagged>;N]; offset∈1..=N` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_cell_n16` | 1472 | 1451 | `proof` | `Cell<K13Tagged>` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_u64_n16` | 1472 | 1451 | `proof` | `u64` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_cell_n17` | 1474 | 1451 | `proof` | `Cell<K13Tagged>` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_u64_n17` | 1474 | 1451 | `proof` | `u64` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_cell_n18` | 1476 | 1451 | `proof` | `Cell<K13Tagged>` | `N=18 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_u64_n18` | 1476 | 1451 | `proof` | `u64` | `N=18 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_cell_n19` | 1478 | 1451 | `proof` | `Cell<K13Tagged>` | `N=19 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_u64_n19` | 1478 | 1451 | `proof` | `u64` | `N=19 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_cell_n20` | 1480 | 1451 | `proof` | `Cell<K13Tagged>` | `N=20 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_b4_u64_n20` | 1480 | 1451 | `proof` | `u64` | `N=20 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w3_b4_n15_g1` | 1517 | 1485 | `proof` | `u64` | `N=15 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n15_g1` | 1517 | 1485 | `proof` | `Cell<K13Tagged>` | `N=15 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n15_g2` | 1518 | 1485 | `proof` | `u64` | `N=15 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n15_g2` | 1518 | 1485 | `proof` | `Cell<K13Tagged>` | `N=15 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n15_g3` | 1519 | 1485 | `proof` | `u64` | `N=15 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n15_g3` | 1519 | 1485 | `proof` | `Cell<K13Tagged>` | `N=15 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n15_g4` | 1520 | 1485 | `proof` | `u64` | `N=15 exact; offsets=[13, 14, 15]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n15_g4` | 1520 | 1485 | `proof` | `Cell<K13Tagged>` | `N=15 exact; offsets=[13, 14, 15]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n16_g1` | 1521 | 1485 | `proof` | `u64` | `N=16 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n16_g1` | 1521 | 1485 | `proof` | `Cell<K13Tagged>` | `N=16 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n16_g2` | 1522 | 1485 | `proof` | `u64` | `N=16 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n16_g2` | 1522 | 1485 | `proof` | `Cell<K13Tagged>` | `N=16 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n16_g3` | 1523 | 1485 | `proof` | `u64` | `N=16 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n16_g3` | 1523 | 1485 | `proof` | `Cell<K13Tagged>` | `N=16 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n16_g4` | 1524 | 1485 | `proof` | `u64` | `N=16 exact; offsets=[13, 14, 15, 16]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n16_g4` | 1524 | 1485 | `proof` | `Cell<K13Tagged>` | `N=16 exact; offsets=[13, 14, 15, 16]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n17_g1` | 1525 | 1485 | `proof` | `u64` | `N=17 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n17_g1` | 1525 | 1485 | `proof` | `Cell<K13Tagged>` | `N=17 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n17_g2` | 1526 | 1485 | `proof` | `u64` | `N=17 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n17_g2` | 1526 | 1485 | `proof` | `Cell<K13Tagged>` | `N=17 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n17_g3` | 1527 | 1485 | `proof` | `u64` | `N=17 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n17_g3` | 1527 | 1485 | `proof` | `Cell<K13Tagged>` | `N=17 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n17_g4` | 1528 | 1485 | `proof` | `u64` | `N=17 exact; offsets=[13, 14, 15]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n17_g4` | 1528 | 1485 | `proof` | `Cell<K13Tagged>` | `N=17 exact; offsets=[13, 14, 15]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n17_g5` | 1529 | 1485 | `proof` | `u64` | `N=17 exact; offsets=[16, 17]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n17_g5` | 1529 | 1485 | `proof` | `Cell<K13Tagged>` | `N=17 exact; offsets=[16, 17]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n18_g1` | 1530 | 1485 | `proof` | `u64` | `N=18 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n18_g1` | 1530 | 1485 | `proof` | `Cell<K13Tagged>` | `N=18 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n18_g2` | 1531 | 1485 | `proof` | `u64` | `N=18 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n18_g2` | 1531 | 1485 | `proof` | `Cell<K13Tagged>` | `N=18 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n18_g3` | 1532 | 1485 | `proof` | `u64` | `N=18 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n18_g3` | 1532 | 1485 | `proof` | `Cell<K13Tagged>` | `N=18 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n18_g4` | 1533 | 1485 | `proof` | `u64` | `N=18 exact; offsets=[13, 14, 15, 16]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n18_g4` | 1533 | 1485 | `proof` | `Cell<K13Tagged>` | `N=18 exact; offsets=[13, 14, 15, 16]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n18_g5` | 1534 | 1485 | `proof` | `u64` | `N=18 exact; offsets=[17, 18]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n18_g5` | 1534 | 1485 | `proof` | `Cell<K13Tagged>` | `N=18 exact; offsets=[17, 18]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n19_g1` | 1535 | 1485 | `proof` | `u64` | `N=19 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n19_g1` | 1535 | 1485 | `proof` | `Cell<K13Tagged>` | `N=19 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n19_g2` | 1536 | 1485 | `proof` | `u64` | `N=19 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n19_g2` | 1536 | 1485 | `proof` | `Cell<K13Tagged>` | `N=19 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n19_g3` | 1537 | 1485 | `proof` | `u64` | `N=19 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n19_g3` | 1537 | 1485 | `proof` | `Cell<K13Tagged>` | `N=19 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n19_g4` | 1538 | 1485 | `proof` | `u64` | `N=19 exact; offsets=[13, 14, 15, 16]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n19_g4` | 1538 | 1485 | `proof` | `Cell<K13Tagged>` | `N=19 exact; offsets=[13, 14, 15, 16]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n19_g5` | 1539 | 1485 | `proof` | `u64` | `N=19 exact; offsets=[17, 18, 19]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n19_g5` | 1539 | 1485 | `proof` | `Cell<K13Tagged>` | `N=19 exact; offsets=[17, 18, 19]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n20_g1` | 1540 | 1485 | `proof` | `u64` | `N=20 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n20_g1` | 1540 | 1485 | `proof` | `Cell<K13Tagged>` | `N=20 exact; offsets=[1, 2, 3, 4]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n20_g2` | 1541 | 1485 | `proof` | `u64` | `N=20 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n20_g2` | 1541 | 1485 | `proof` | `Cell<K13Tagged>` | `N=20 exact; offsets=[5, 6, 7, 8]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n20_g3` | 1542 | 1485 | `proof` | `u64` | `N=20 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n20_g3` | 1542 | 1485 | `proof` | `Cell<K13Tagged>` | `N=20 exact; offsets=[9, 10, 11, 12]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n20_g4` | 1543 | 1485 | `proof` | `u64` | `N=20 exact; offsets=[13, 14, 15, 16]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n20_g4` | 1543 | 1485 | `proof` | `Cell<K13Tagged>` | `N=20 exact; offsets=[13, 14, 15, 16]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_b4_n20_g5` | 1544 | 1485 | `proof` | `u64` | `N=20 exact; offsets=[17, 18, 19, 20]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w3_o3_n20_g5` | 1544 | 1485 | `proof` | `Cell<K13Tagged>` | `N=20 exact; offsets=[17, 18, 19, 20]` | safety | insertion/route safety with arbitrary or mutating comparator; checks normal return/offset coverage, no sortedness or permutation claim | `ordinary` |
| `w2p2_k10_u8_0_2` | 1582 | 1566 | `proof` | `u8` | `N∈{0,1,2} exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_0_2` | 1583 | 1566 | `proof` | `u64` | `N∈{0,1,2} exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u8_3_4` | 1584 | 1566 | `proof` | `u8` | `N∈{3,4} exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_3_4` | 1585 | 1566 | `proof` | `u64` | `N∈{3,4} exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u8_n5` | 1587 | 1566 | `proof` | `u8` | `N=5 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n5` | 1588 | 1566 | `proof` | `u64` | `N=5 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u8_n6` | 1589 | 1566 | `proof` | `u8` | `N=6 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n6` | 1590 | 1566 | `proof` | `u64` | `N=6 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u8_n7` | 1592 | 1566 | `proof` | `u8` | `N=7 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n7` | 1593 | 1566 | `proof` | `u64` | `N=7 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u8_n8` | 1594 | 1566 | `proof` | `u8` | `N=8 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n8` | 1595 | 1566 | `proof` | `u64` | `N=8 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k9s_zst` | 1643 | 1631 | `proof_for_contract(swap_if_less)` | `()` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `w2p2_k9s_u8` | 1644 | 1631 | `proof_for_contract(swap_if_less)` | `u8` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k9s_u64` | 1645 | 1631 | `proof_for_contract(swap_if_less)` | `u64` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k9s_u128` | 1646 | 1631 | `proof_for_contract(swap_if_less)` | `u128` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k9s_a16` | 1647 | 1631 | `proof_for_contract(swap_if_less)` | `[u8;16]` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k9s_a17` | 1648 | 1631 | `proof_for_contract(swap_if_less)` | `[u8;17]` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k9s_a85` | 1649 | 1631 | `proof_for_contract(swap_if_less)` | `[u8;85]` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k9s_a86` | 1650 | 1631 | `proof_for_contract(swap_if_less)` | `[u8;86]` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k9s_drop` | 1651 | 1631 | `proof_for_contract(swap_if_less)` | `W2Drop` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k9s_cell` | 1652 | 1631 | `proof_for_contract(swap_if_less)` | `Cell<i32>` | `N=2 exact [T;2]; (0,1)/(1,0), swap/no-swap and frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2p2_k10_u8_n9` | 1655 | 1566 | `proof` | `u8` | `N=9 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n9` | 1656 | 1566 | `proof` | `u64` | `N=9 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u8_n10` | 1657 | 1566 | `proof` | `u8` | `N=10 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n10` | 1658 | 1566 | `proof` | `u64` | `N=10 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_perm_u8_n10` | 1688 | 1677 | `proof` | `u8` | `N=10 exact [T;N]; real insertion_sort_shift_left offset=9` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_perm_u64_n10` | 1689 | 1677 | `proof` | `u64` | `N=10 exact [T;N]; real insertion_sort_shift_left offset=9` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_u8_n11` | 1691 | 1566 | `proof` | `u8` | `N=11 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n11` | 1692 | 1566 | `proof` | `u64` | `N=11 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_perm_u8_n11` | 1693 | 1677 | `proof` | `u8` | `N=11 exact [T;N]; real insertion_sort_shift_left offset=9` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_perm_u64_n11` | 1694 | 1677 | `proof` | `u64` | `N=11 exact [T;N]; real insertion_sort_shift_left offset=9` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_u8_n12` | 1696 | 1566 | `proof` | `u8` | `N=12 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n12` | 1697 | 1566 | `proof` | `u64` | `N=12 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_perm_u8_n12` | 1698 | 1677 | `proof` | `u8` | `N=12 exact [T;N]; real insertion_sort_shift_left offset=9` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_perm_u64_n12` | 1699 | 1677 | `proof` | `u64` | `N=12 exact [T;N]; real insertion_sort_shift_left offset=9` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_u8_n13` | 1702 | 1566 | `proof` | `u8` | `N=13 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n13` | 1703 | 1566 | `proof` | `u64` | `N=13 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u8_n14` | 1706 | 1566 | `proof` | `u8` | `N=14 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n14` | 1707 | 1566 | `proof` | `u64` | `N=14 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_perm_u8_n14` | 1708 | 1677 | `proof` | `u8` | `N=14 exact [T;N]; real insertion_sort_shift_left offset=13` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_perm_u64_n14` | 1709 | 1677 | `proof` | `u64` | `N=14 exact [T;N]; real insertion_sort_shift_left offset=13` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_u8_n15` | 1712 | 1566 | `proof` | `u8` | `N=15 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n15` | 1714 | 1566 | `proof` | `u64` | `N=15 exact [T;N]; real unstable trait route` | control | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `kani_smallsort_controls` |
| `w2p2_k10_perm_u8_n15` | 1715 | 1677 | `proof` | `u8` | `N=15 exact [T;N]; real insertion_sort_shift_left offset=13` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_perm_u64_n15` | 1716 | 1677 | `proof` | `u64` | `N=15 exact [T;N]; real insertion_sort_shift_left offset=13` | correctness | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `ordinary` |
| `w2p2_k10_u8_n16` | 1719 | 1566 | `proof` | `u8` | `N=16 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n16` | 1721 | 1566 | `proof` | `u64` | `N=16 exact [T;N]; real unstable trait route` | control | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `kani_smallsort_controls` |
| `w2p2_k10_perm_u8_n16` | 1723 | 1677 | `proof` | `u8` | `N=16 exact [T;N]; real insertion_sort_shift_left offset=13` | control | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `kani_smallsort_controls` |
| `w2p2_k10_perm_u64_n16` | 1725 | 1677 | `proof` | `u64` | `N=16 exact [T;N]; real insertion_sort_shift_left offset=13` | control | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `kani_smallsort_controls` |
| `w2p2_k10_u8_n17` | 1728 | 1566 | `proof` | `u8` | `N=17 exact [T;N]; real unstable trait route` | correctness | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `ordinary` |
| `w2p2_k10_u64_n17` | 1730 | 1566 | `proof` | `u64` | `N=17 exact [T;N]; real unstable trait route` | control | real unstable trait output sortedness; full-value permutation asserted only for N<9; N>=9 is sortedness-only | `kani_smallsort_controls` |
| `w2p2_k10_perm_u8_n17` | 1732 | 1677 | `proof` | `u8` | `N=17 exact [T;N]; real insertion_sort_shift_left offset=13` | control | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `kani_smallsort_controls` |
| `w2p2_k10_perm_u64_n17` | 1734 | 1677 | `proof` | `u64` | `N=17 exact [T;N]; real insertion_sort_shift_left offset=13` | control | real insertion suffix full-value probe-count equality (permutation); no sortedness claim | `kani_smallsort_controls` |
| `w2night_k9s_u8_indices17` | 1766 | — | `proof_for_contract(swap_if_less)` | `u8` | `N=17 exact [T;17]; distinct symbolic in-bounds indices; both directions, swap/no-swap, network-final-position and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2night_k9s_u64_indices17` | 1772 | — | `proof_for_contract(swap_if_less)` | `u64` | `N=17 exact [T;17]; distinct symbolic in-bounds indices; both directions, swap/no-swap, network-final-position and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u8_n9` | 1788 | 1778 | `proof_for_contract(swap_if_less)` | `u8` | `N=9 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u8_n10` | 1789 | 1778 | `proof_for_contract(swap_if_less)` | `u8` | `N=10 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u8_n11` | 1790 | 1778 | `proof_for_contract(swap_if_less)` | `u8` | `N=11 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u8_n12` | 1791 | 1778 | `proof_for_contract(swap_if_less)` | `u8` | `N=12 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u8_n13` | 1792 | 1778 | `proof_for_contract(swap_if_less)` | `u8` | `N=13 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u8_n14` | 1793 | 1778 | `proof_for_contract(swap_if_less)` | `u8` | `N=14 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u8_n15` | 1794 | 1778 | `proof_for_contract(swap_if_less)` | `u8` | `N=15 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u8_n16` | 1795 | 1778 | `proof_for_contract(swap_if_less)` | `u8` | `N=16 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u64_n9` | 1796 | 1778 | `proof_for_contract(swap_if_less)` | `u64` | `N=9 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u64_n10` | 1797 | 1778 | `proof_for_contract(swap_if_less)` | `u64` | `N=10 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u64_n11` | 1798 | 1778 | `proof_for_contract(swap_if_less)` | `u64` | `N=11 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u64_n12` | 1799 | 1778 | `proof_for_contract(swap_if_less)` | `u64` | `N=12 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u64_n13` | 1800 | 1778 | `proof_for_contract(swap_if_less)` | `u64` | `N=13 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u64_n14` | 1801 | 1778 | `proof_for_contract(swap_if_less)` | `u64` | `N=14 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u64_n15` | 1802 | 1778 | `proof_for_contract(swap_if_less)` | `u64` | `N=15 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w3_k9s_u64_n16` | 1803 | 1778 | `proof_for_contract(swap_if_less)` | `u64` | `N=16 exact [T;N]; distinct symbolic in-bounds indices; branches and untouched frame` | correctness | proof_for_contract(swap_if_less): pair swap/no-swap and unchanged-frame facts, exact indices/domain | `ordinary` |
| `w2night_k8r_start15_u64` | 1839 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=15; tails {16}; region sizes {2}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start14_u64` | 1840 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=14; tails {15,16}; region sizes {2,3}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start13_u64` | 1841 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=13; tails {14,15,16}; region sizes {2,3,4}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start12_u64` | 1842 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=12; tails {13,14,15,16}; region sizes {2,3,4,5}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start11_u64` | 1843 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=11; tails {12,13,14,15,16}; region sizes {2,3,4,5,6}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start10_u64` | 1844 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=10; tails {11,12,13,14,15,16}; region sizes {2,3,4,5,6,7}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start9_u64` | 1845 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=9; tails {10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start8_u64` | 1846 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=8; tails {9,10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8,9}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start7_u64` | 1847 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=7; tails {8,9,10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8,9,10}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start6_u64` | 1848 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=6; tails {7,8,9,10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8,9,10,11}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start5_u64` | 1849 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=5; tails {6,7,8,9,10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8,9,10,11,12}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start4_u64` | 1850 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=4; tails {5,6,7,8,9,10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8,9,10,11,12,13}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start3_u64` | 1851 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=3; tails {4,5,6,7,8,9,10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8,9,10,11,12,13,14}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start2_u64` | 1852 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=2; tails {3,4,5,6,7,8,9,10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8,9,10,11,12,13,14,15}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_k8r_start1_u64` | 1853 | 1828 | `proof_for_contract(insert_tail)` | `u64` | `backing [u64;17]; start=1; tails {2,3,4,5,6,7,8,9,10,11,12,13,14,15,16}; region sizes {2,3,4,5,6,7,8,9,10,11,12,13,14,15,16}; sorted-prefix requires` | correctness | proof_for_contract(insert_tail): sorted-prefix precondition, shifted region correctness and prefix/suffix frame | `ordinary` |
| `w2night_o3_tags_n2` | 1893 | 1882 | `proof` | `Cell<K13Tagged>` | `N=2 exact [Cell<K13Tagged>;N]; tag multiplicity check` | correctness | O3 tag multiplicity preservation across exact Cell<K13Tagged> route | `ordinary` |
| `w2night_o3_tags_n3` | 1894 | 1882 | `proof` | `Cell<K13Tagged>` | `N=3 exact [Cell<K13Tagged>;N]; tag multiplicity check` | correctness | O3 tag multiplicity preservation across exact Cell<K13Tagged> route | `ordinary` |
| `w2night_o3_tags_n4` | 1895 | 1882 | `proof` | `Cell<K13Tagged>` | `N=4 exact [Cell<K13Tagged>;N]; tag multiplicity check` | correctness | O3 tag multiplicity preservation across exact Cell<K13Tagged> route | `ordinary` |
| `k15_mutant_existing_k10_presorted_len` | 1900 | — | `proof` | `u8` | `calls w2p2_k10_u8_n10(); exact N=10 inherited K10 normal-return witness` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |

#### `library/core/src/slice/sort/shared/smallsort/kani_k1/assembly.rs`

| Expanded entrypoint | Item line | Macro line | Harness / contract | Тип | N / домен | Вид | Проверяемое свойство / назначение | cfg |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `k15_mutant_swap` | 127 | 106 | `proof` | `u8` | `N=2 exact u8 array; shared positive check` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k15_swap` | 127 | 106 | `proof` | `u8` | `N=2 exact u8 array; shared positive check` | correctness | swap witness: sorted pair and two-element permutation | `ordinary` |
| `k15_insert` | 130 | 106 | `proof` | `u8` | `N=2 exact u8 array; shared positive check` | correctness | insert_tail witness: sorted pair and two-element permutation | `ordinary` |
| `k15_mutant_insert` | 130 | 106 | `proof` | `u8` | `N=2 exact u8 array; shared positive check` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k15_merge_up` | 133 | 106 | `proof` | `u8` | `source [u8;2], output MaybeUninit<u8>, one element consumed and pointers advanced` | correctness | merge_up witness: chosen value and exact source/destination pointer advancement | `ordinary` |
| `k15_mutant_merge_up` | 133 | 106 | `proof` | `u8` | `source [u8;2], output MaybeUninit<u8>, one element consumed and pointers advanced` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k15_merge_consumption` | 136 | 106 | `proof` | `u8` | `N=4 exact u8 array; shared positive check` | correctness | bidirectional_merge arbitrary-comparator witness: full-value probe multiplicity on normal return | `ordinary` |
| `k15_mutant_merge_consumption` | 136 | 106 | `proof` | `u8` | `N=4 exact u8 array; shared positive check` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k15_mutant_presorted_len` | 139 | 106 | `proof` | `u8` | `N=10 exact u8 array; shared positive check` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `k15_presorted_len` | 139 | 106 | `proof` | `u8` | `N=10 exact u8 array; shared positive check` | correctness | presorted_len regression witness: tenth zero is inserted | `ordinary` |
| `ci_zst_stable_1` | 159 | 143 | `proof` | `()` | `N=1 exact [();N]; scratch length 48` | safety | stable ZST smallsort normal return; Kani safety checks only | `ordinary` |
| `ci_zst_stable_2` | 160 | 143 | `proof` | `()` | `N=2 exact [();N]; scratch length 48` | safety | stable ZST smallsort normal return; Kani safety checks only | `ordinary` |
| `ci_zst_stable_7` | 161 | 143 | `proof` | `()` | `N=7 exact [();N]; scratch length 48` | safety | stable ZST smallsort normal return; Kani safety checks only | `ordinary` |
| `ci_zst_stable_8` | 162 | 143 | `proof` | `()` | `N=8 exact [();N]; scratch length 48` | safety | stable ZST smallsort normal return; Kani safety checks only | `ordinary` |
| `ci_zst_stable_16` | 163 | 143 | `proof` | `()` | `N=16 exact [();N]; scratch length 48` | safety | stable ZST smallsort normal return; Kani safety checks only | `ordinary` |
| `ci_zst_stable_17` | 164 | 143 | `proof` | `()` | `N=17 exact [();N]; scratch length 48` | safety | stable ZST smallsort normal return; Kani safety checks only | `ordinary` |
| `ci_zst_stable_31` | 165 | 143 | `proof` | `()` | `N=31 exact [();N]; scratch length 48` | safety | stable ZST smallsort normal return; Kani safety checks only | `ordinary` |
| `ci_zst_stable_32` | 166 | 143 | `proof` | `()` | `N=32 exact [();N]; scratch length 48` | safety | stable ZST smallsort normal return; Kani safety checks only | `ordinary` |

#### `library/core/src/slice/sort/shared/smallsort/kani_k1/correct.rs`

| Expanded entrypoint | Item line | Macro line | Harness / contract | Тип | N / домен | Вид | Проверяемое свойство / назначение | cfg |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `l2_fallback_u64_n8` | 36 | 24 | `proof` | `u64` | `N=8 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u64_n16` | 37 | 24 | `proof` | `u64` | `N=16 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u8_n9` | 38 | 24 | `proof` | `u8` | `N=9 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u8_n16` | 39 | 24 | `proof` | `u8` | `N=16 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u64_n9` | 42 | 24 | `proof` | `u64` | `N=9 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u64_n10` | 43 | 24 | `proof` | `u64` | `N=10 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u64_n11` | 44 | 24 | `proof` | `u64` | `N=11 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u64_n12` | 45 | 24 | `proof` | `u64` | `N=12 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u64_n13` | 46 | 24 | `proof` | `u64` | `N=13 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u64_n14` | 47 | 24 | `proof` | `u64` | `N=14 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u64_n15` | 48 | 24 | `proof` | `u64` | `N=15 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u8_n10` | 49 | 24 | `proof` | `u8` | `N=10 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u8_n11` | 50 | 24 | `proof` | `u8` | `N=11 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u8_n12` | 51 | 24 | `proof` | `u8` | `N=12 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u8_n13` | 52 | 24 | `proof` | `u8` | `N=13 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u8_n14` | 53 | 24 | `proof` | `u8` | `N=14 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_fallback_u8_n15` | 54 | 24 | `proof` | `u8` | `N=15 exact [T;N]; sortedness + full-value count; insert_tail verified stub` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_insert_tail_prefix_u8` | 56 | — | `proof_for_contract(insert_tail)` | `u8` | `backing [u8;17]; tail=1..16; region size 2..17; insertion contract and suffix frame` | correctness | proof_for_contract(insert_tail): prefix sortedness requires, output contract, suffix frame | `ordinary` |
| `l2_r11_insert_tail` | 76 | — | `proof` | `u8` | `N=3 exact [4,0,2]; insert_tail region tail=2, deliberately unsorted prefix requires control` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_insert_tail_scratch_u64` | 128 | 116 | `proof_for_contract(insert_tail)` | `u64` | `Scratch backing [T;48] (SMALL_SORT_GENERAL_SCRATCH_LEN=SMALL_SORT_GENERAL_THRESHOLD 32 + 16); start∈{0,6,7}; region len=5..8 inclusive, end-exclusive start+len≤15; insert_tail call spans start..start+len-1; verifies all cells outside that region unchanged` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_insert_tail_scratch_u8` | 129 | 116 | `proof_for_contract(insert_tail)` | `u8` | `initialized scratch [u8;48]; start∈{0,6,7}; len∈5..=8; outside-region frame` | correctness | proof_for_contract(insert_tail): scratch region contract and outside-region frame | `ordinary` |
| `l2_gs_u64_n15` | 166 | 155 | `proof` | `u64` | `N=15 exact [T;N]; stable/direct-general selector; sortedness + full-value count` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_gs_u8_n15` | 167 | 155 | `proof` | `u8` | `N=15 exact [T;N]; stable/direct-general selector; sortedness + full-value count` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_gs_u8_n14` | 169 | 155 | `proof` | `u8` | `N=14 exact [T;N]; stable/direct-general selector; sortedness + full-value count` | correctness | caller correctness: sorted output and full-value probe-count equality; real route with verified insertion stub(s) | `ordinary` |
| `l2_network_u64_n17` | 197 | 187 | `proof` | `u64` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_network_u8_n17` | 199 | 187 | `proof` | `u8` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_scratch_u64_kissat` | 206 | 116 | `proof_for_contract(insert_tail)` | `u64` | `Scratch backing [T;48] (SMALL_SORT_GENERAL_SCRATCH_LEN=SMALL_SORT_GENERAL_THRESHOLD 32 + 16); start∈{0,6,7}; region len=5..8 inclusive, end-exclusive start+len≤15; insert_tail call spans start..start+len-1; verifies all cells outside that region unchanged` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_scratch_u64_minisat` | 208 | 116 | `proof_for_contract(insert_tail)` | `u64` | `Scratch backing [T;48] (SMALL_SORT_GENERAL_SCRATCH_LEN=SMALL_SORT_GENERAL_THRESHOLD 32 + 16); start∈{0,6,7}; region len=5..8 inclusive, end-exclusive start+len≤15; insert_tail call spans start..start+len-1; verifies all cells outside that region unchanged` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_gs_u64_n13_kissat` | 210 | 155 | `proof` | `u64` | `N=13 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_gs_u64_n14_minisat` | 212 | 155 | `proof` | `u64` | `N=14 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_network_u64_n15_kissat` | 214 | 187 | `proof` | `u64` | `N=15 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_network_u64_n16_minisat` | 216 | 187 | `proof` | `u64` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_network_u64_n17_kissat` | 218 | 187 | `proof` | `u64` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_network_u8_n16_kissat` | 220 | 187 | `proof` | `u8` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_network_u8_n17_minisat` | 222 | 187 | `proof` | `u8` | `N=17 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_fallback_u64_n16_kissat` | 224 | 24 | `proof` | `u64` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_fallback_u64_n16_minisat` | 226 | 24 | `proof` | `u64` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_fallback_u8_n16_kissat` | 228 | 24 | `proof` | `u8` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `l2_sweep_fallback_u8_n16_minisat` | 230 | 24 | `proof` | `u8` | `N=16 exact fixed-length instance` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |

#### `library/core/src/slice/sort/shared/smallsort/kani_k1/smoke.rs`

| Expanded entrypoint | Item line | Macro line | Harness / contract | Тип | N / домен | Вид | Проверяемое свойство / назначение | cfg |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `w3_efficient_swap_c3` | 16 | — | `proof` | `u8, u64, u128, [u8;16], [u8;17], [u8;85], [u8;86], W3SwapDrop, Cell<i32>, ()` | `10 fixed type cases; expected predicate values; one cover per type` | correctness | documented efficient in-place-swap predicate values for ten representative types | `ordinary` |
| `ok` | 37 | — | `proof` | `u8, u64, u128, [u8;16], [u8;17], [u8;85], [u8;86], W3SwapDrop, Cell<i32>, ()` | `10 fixed type cases; expected predicate values; one cover per type` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `control_must_fail` | 47 | — | `proof` | `u8, u64, u128, [u8;16], [u8;17], [u8;85], [u8;86], W3SwapDrop, Cell<i32>, ()` | `10 fixed type cases; expected predicate values; one cover per type` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |

#### `library/core/src/slice/sort/shared/smallsort/kani_k1/uninit.rs`

| Expanded entrypoint | Item line | Macro line | Harness / contract | Тип | N / домен | Вид | Проверяемое свойство / назначение | cfg |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `z1_stable_0` | 108 | 95 | `proof` | `()` | `N=0 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_1` | 109 | 95 | `proof` | `()` | `N=1 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_2` | 110 | 95 | `proof` | `()` | `N=2 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_7` | 111 | 95 | `proof` | `()` | `N=7 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_8` | 112 | 95 | `proof` | `()` | `N=8 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_15` | 113 | 95 | `proof` | `()` | `N=15 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_16` | 114 | 95 | `proof` | `()` | `N=16 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_17` | 115 | 95 | `proof` | `()` | `N=17 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_31` | 116 | 95 | `proof` | `()` | `N=31 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_stable_32` | 117 | 95 | `proof` | `()` | `N=32 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_network_8` | 118 | 95 | `proof` | `()` | `N=8 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_network_9` | 119 | 95 | `proof` | `()` | `N=9 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_network_12` | 120 | 95 | `proof` | `()` | `N=12 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_network_13` | 121 | 95 | `proof` | `()` | `N=13 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_network_17` | 122 | 95 | `proof` | `()` | `N=17 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1f_stable_2` | 123 | 95 | `proof` | `()` | `N=2 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1f_stable_8` | 124 | 95 | `proof` | `()` | `N=8 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1f_stable_16` | 125 | 95 | `proof` | `()` | `N=16 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1f_stable_32` | 126 | 95 | `proof` | `()` | `N=32 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_from_fn_unit_2` | 127 | 95 | `proof` | `()` | `N=2 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_from_fn_unit_32` | 128 | 95 | `proof` | `()` | `N=32 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1f_stable_1` | 130 | 95 | `proof` | `()` | `N=1 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1f_stable_7` | 131 | 95 | `proof` | `()` | `N=7 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1f_stable_17` | 132 | 95 | `proof` | `()` | `N=17 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1f_stable_31` | 133 | 95 | `proof` | `()` | `N=31 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_stable_1` | 134 | 95 | `proof` | `()` | `N=1 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_stable_2` | 135 | 95 | `proof` | `()` | `N=2 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_stable_7` | 136 | 95 | `proof` | `()` | `N=7 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_stable_8` | 137 | 95 | `proof` | `()` | `N=8 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_stable_16` | 138 | 95 | `proof` | `()` | `N=16 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_stable_17` | 139 | 95 | `proof` | `()` | `N=17 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_stable_31` | 140 | 95 | `proof` | `()` | `N=31 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_stable_32` | 141 | 95 | `proof` | `()` | `N=32 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_network_8` | 142 | 95 | `proof` | `()` | `N=8 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_network_9` | 143 | 95 | `proof` | `()` | `N=9 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_read_unit` | 146 | — | `proof` | `()` | `single initialized ZST scalar; ptr::read; no array length domain` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_merge2_unit` | 155 | — | `proof` | `()` | `N=2 exact [();2] source/destination; bidirectional_merge with ZST-aware comparator` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_insert_tail_unit` | 166 | — | `proof` | `()` | `N=2 exact [();2]; insert_tail region length 2` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_sort4_unit` | 177 | — | `proof` | `()` | `N=4 exact [();4] source/destination; sort4_stable` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1n_swap_unit` | 187 | — | `proof` | `()` | `N=2 exact [();2]; swap_if_less indices 0,1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_volatile_unit` | 196 | — | `proof` | `()` | `single initialized ZST scalar; ptr::read_volatile; no array length domain` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_sort4_unit` | 205 | — | `proof` | `()` | `N=4 exact [();4] source/destination; sort4_stable` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_swap_unit` | 215 | — | `proof` | `()` | `N=2 exact [();2]; swap_if_less indices 0,1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_copy_unit` | 225 | — | `proof` | `()` | `N=2 exact [();2]; copies one element into scratch length 2` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_merge2_unit` | 235 | — | `proof` | `()` | `N=2 exact [();2] source/destination; bidirectional_merge` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_merge3_unit` | 248 | — | `proof` | `()` | `N=3 exact [();3] source/destination; bidirectional_merge` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `z1_insert_tail_unit` | 259 | — | `proof` | `()` | `N=2 exact [();2]; insert_tail region tail=1` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_general_8` | 324 | 312 | `proof` | `u64` | `N=8 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_general_16` | 325 | 312 | `proof` | `u64` | `N=16 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_general_32` | 326 | 312 | `proof` | `u64` | `N=32 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_network_18` | 328 | 312 | `proof` | `u64` | `N=18 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_network_32` | 329 | 312 | `proof` | `u64` | `N=32 exact array; route inferred from entry name` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_initialized_control` | 332 | — | `proof` | `u64` | `single MaybeUninit<u64> initialized with kani::any; volatile read control` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_uninitialized_control` | 343 | — | `proof` | `u64` | `single MaybeUninit<u64>::uninit(); deliberate volatile uninitialized read control` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_general_8_tail_uninit` | 372 | — | `proof` | `u64` | `helper uninit_general_tail::<0>(); fixed general N=8 tail diagnostic` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_general_8_tail_written` | 380 | — | `proof` | `u64` | `helper uninit_general_tail::<1>(); fixed general N=8 tail diagnostic` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_general_8_tail_written_raw` | 388 | — | `proof` | `u64` | `helper uninit_general_tail::<2>(); fixed general N=8 tail diagnostic` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_network_layout_tail_uninit` | 417 | — | `proof` | `u64` | `helper uninit_network_tail::<false>(); fixed network layout tail diagnostic` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |
| `u1_network_layout_tail_written` | 424 | — | `proof` | `u64` | `helper uninit_network_tail::<true>(); fixed network layout tail diagnostic` | control | opt-in/control/diagnostic harness; excluded by cfg from ordinary list | `kani_smallsort_controls` |

#### `library/core/src/slice/sort/shared/smallsort/kani_k1/mutations.rs`

Proof entries нет; модуль содержит вызываемые тела мутантов и подключён только при controls cfg.

Статическая проверка X0: 625 уникальных пар module/name; все625 item locations совпали с именем invocation или proof attribute в `git show S_M:path`. Для355 ordinary и270 excluded заполнены тип/домен/cfg/вид; исходниковая развёртка не заменяет target-specific `kani list` координатора.

## 7. Решения и передача

1. `S_M` сохраняется кандидатом; все final CI поля — координатору.
2. Остаток М не переименован в бонус; B4 bounded не превращён в anylen,
   sortedness не заменяет E3 permutation, source entry не равен evidence.
3. Решение по C4: исторические source-reported статусы сохранены, но
   инстанциацию `lt_u8/lt_u64` по ключу x>>1 не переименовываем в default `<`;
   обобщение по порядку требует самостоятельного source-bound довода.
4. X6 получает первый proof-slot после приёмки/выдачи; source-binding
   gate обязателен. X7 использует actual insertion body с проверенным tail,
   а не несовместимый insertion stub; геометрия callee — отдельный gate.
5. Общие файлы принадлежат интегратору/единственному назначенному владельцу.
   Черновики не выдают phase/window/новый cap и не занимают Cloud slots.
   При выдаче проверить `min(B_owner,B_lane) >= spent + reserved + B_finish_minimum + 18`;
   защищённые $10 X10 и отдельный macOS ресурс не расходуются пилотами.
6. В X0 созданы только этот baseline и два TASK; library, чужие документы,
   исторические evidence/ledger не изменяются. Clean room соблюдён:
   code/diffs/branches четырёх запрещённых PR не открывались.
7. Сборок/локальных proof-команд, внешних PR/issues/comments нет.
   Проверка X0 — source-only inventory, ссылки/таблицы, `git diff --check`
   и whitelist трёх файлов. Commit/push — в ветку X0 без force.

После review X0 координатор дополняет final CI и принимает S_M, выдаёт
отдельные задания с owner/phase/pin/budget/window. Следующий этап в этой
сессии не начинается.
