# Офлайн-анализ первой кампании q-пилота

**Run `44834820115`, attempt 1. `RESEARCH_ONLY`, `proof_credit=NONE`.** P-1 и оба swap-контроля дали ожидаемые terminal verdicts. P-2, P-3, P-4 и P-5c были запущены и прерваны без итогового инвентаря. Текущая кодировка не прошла gate пилота. На следующую кампанию предлагаю одну замену в verification model: представлять пороговый вектор маской `u32` с фиксированными защищёнными смещениями. Это сохранит точный пост вставки и уберёт DP `at_least` без изменения тела сортировки или контрактной области записи.

## 1. Привязка результатов

Проверены только объявленные ограниченные файлы fork-артефакта из Git на `8b13284e73`, сверены [сводка координатора](run-44834820115/SUMMARY.md), [GO с поправкой workflow](PILOT-GO.md), ledger на `04f6c780e8` и [чек-лист](PILOT-ANALYSIS-CHECKLIST.md). В первоначальном run `44834533774` job не стартовал. Здесь используется исправленный trigger из дополнения к GO, а ledger сохраняет ссылку на прежнее дерево в описании первой попытки.

| Объект | Подтверждённая идентичность |
| --- | --- |
| Run | `44834820115`, attempt `1`, `push`, `refs/heads/uninit-ci/ch8-q-pilot-v1` |
| Control | Trigger `0bf2794faa624e8d9adb9be1990e96beca6cd104`, tree `dece392fb5695adbb93abef5e8f509dd26a30b1b`, sole parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7` |
| Control request / workflow SHA-256 | `505600d7b8a74cf7ee2d2bf89f0a6951e06d2c32cef9648fd222940765d07a6d` / `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f`. Оба пересчитаны из Git объекта trigger. |
| std | `5544e01921d5c67c21d4ab919e8f76b43f884d92`, tree `551a7300bb76807dc80efd56f9e1603e19706c84` |
| Tool | `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |
| Индекс | [`q-pilot-raw.json`](run-44834820115/raw/q-pilot-raw.json), 461 053 байта, SHA-256 `748fbd59d3d63a91e2791b48db20d6c3a4b0903e0c47b5b343d087b2d8ec6a7f` |

У всех 21 членов сверены заявленные пути, размеры и SHA-256 сохранённых байтов. Всего 5 270 110 байт с индексом. Truncation нет, размеры ниже 16/1/8 MiB и 256 MiB суммарно. `snapshot_after_reap=true`, child shutdown, supervisor containment и удаление temp записаны для семи корней. Записи запуска содержат UTC и монотонные start/end, у каждого отдельные Kani/Cargo target paths. Job и сбор наблюдений завершились штатно, включая запись об исходных exit codes. Это статус обвязки.

Все семь exact singleton selectors, порядок и normal/mutant cfg совпадают с request. В export каждого корня установлен `matched_count=1`, schema `0.1.0`, clean tool `0aac…`, `x86_64-unknown-linux-gnu`, Kani 0.68.0, CBMC 6.11.0. Набор `c-ffi`, `export-json`, `float-lib`, `function-contracts`, `mem-predicates`, `stubbing`, `unstable-options` совпадает с argv. Запрошены unwind36 и object-bits12, memory safety, overflow, unwinding и reachability checks включены. `assert_contracts=false` соответствует `--no-assert-contracts`. Этот флаг сохраняет явные Check/Replace приоритетными на пине. Terminal exports дают `resolved_solver=cadical` и `resolved_unwind=36`, в доступных SAT-записях указан CaDiCaL 3.0.0. Loop contracts, quantifiers, uninit/valid-value instrumentation отсутствуют в профиле.

## 2. Итоги семи корней

RSS — sampled PGID VmRSS из `child`, с возможным превышением между опросами. Child wall включает сборку std и завершение процесса. VT — native verification time из terminal export. Незавершённый VT и длительность компиляции отдельно не восстанавливались. Setup receipt сообщает 351,692 с, сумма семи child — 1158,276 с, это отдельные интервалы от календарного времени job.

| Корень | Exit / причина | Child, с | RSS, GiB | Native verdict / VT, с |
| --- | --- | ---: | ---: | --- |
| P-1 swap | `0`, EXITED | 69,225 | 1,885 | `SUCCESS` / 36,525 |
| P-2 sort13 | `−15`, SIGTERM, `rss_cap` | 94,706 | 6,000 | `UNKNOWN`, export `INCOMPLETE` |
| P-3 insert_tail | `−15`, SIGTERM, `timeout` | 600,568 | 5,514 | `UNKNOWN`, export `INCOMPLETE` |
| P-4 network17 | `−15`, SIGTERM, `rss_cap` | 112,128 | 6,095 | `UNKNOWN`, export `INCOMPLETE` |
| P-5a false OR, q:any | `1`, EXITED | 42,815 | 1,838 | `FAILURE` / 10,137, назначенное свойство |
| P-5b false OR, q=0 | `0`, EXITED | 41,053 | 1,837 | `SUCCESS` / 9,032, фиксированный q |
| P-5c порча результата | `−15`, SIGTERM, `rss_cap` | 197,781 | 6,078 | `UNKNOWN`, export `INCOMPLETE` |

### Завершённые свойства и контроли

Сверены все 1069 записей regular `RESULTS`…`SUMMARY`: уникальные ID и непрерывные ordinals, stock totals, SUCCESS count, поимённые buckets U/FAILURE/covers, assert ID/class/status/description для failed и unsupported. Полные property IDs, статусы и координаты остаются в `raw/<корень>/stdout.log`, диапазоны указаны ниже. Stock агрегирует SUCCESS в счётчик. Пропуск координаты сохраняется как пробел в source binding соответствующего свойства.

| Корень / строки `RESULTS`…`SUMMARY` | Checks `SUCCESS / U / FAILURE` | Covers `SATISFIED / U` | Согласование ролей |
| --- | ---: | ---: | --- |
| P-1, 2839–4708 | 359 / 4 / 0 = 363 | 10 / 0 | Check `swap_if_less`, `swap_post` на `smallsort.rs:460` SUCCESS. `P1_ACTIVE`, `P1_SWAP_QPOST`, `P1_Q_FRAME`, `P1_FRAME` SUCCESS. Достигнуты base0/base20, равные индексы, split, taken/untaken, q=0/q=255, `P1_Q_ABSENT` на паре и useful return. |
| P-5a, 2807–4551 | 339 / 4 / 1 = 344 | 4 / 0 | Check того же target под mutant cfg. `P5_SWAP_SPLIT_THRESHOLD` SATISFIED на `sorting_q_controls.rs:23` до вызова swap на строке 30. Обе границы base и полезный возврат SATISFIED. `P5_SWAP_ACTIVE` и q/byte frame SUCCESS на оставшейся достижимой части. |
| P-5b, 2795–4539 | 336 / 8 / 0 = 344 | 3 / 1 | Check mutant с q=0. Назначенный пост SUCCESS, обе границы base и полезный возврат SATISFIED. Неиспользуемый split cover и четыре проверки его выражения остались в инвентаре со статусом UNREACHABLE. |

Во всех трёх terminal exports есть ровно один manual `ProofForContract` с `target_fn=swap_if_less`, пустыми `stubs` и `verified_stubs` и `should_panic=false`. Режим Check следует из метаданных и `contracts.rs:569–584` на пине Kani. Requires входят как assumptions, отдельные SUCCESS для каждой такой clause здесь не требуются. Post и frame подтверждены штатным инвентарём. У P-5a ровно одна native `FAILURE`, класс `assertion`, `smallsort.rs:461:1`, описание `swap_false_or_post(old(swap_capture(...)), ...)`. Точный ID:

```text
slice::sort::shared::smallsort::swap_if_less::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>::{closure#2}.assertion.1
```

Этот же ID в normal cfg P-1 имеет иной source site и `swap_post`. Поэтому связываем отказ одновременно по cfg, полному ID, строке и выражению. Для P-5b все байты удовлетворяют `x>=0`, false-OR лемма на этом поддомене истинна. Правило офлайн-анализа даёт `Q_DOMAIN_NOT_UNIVERSAL` для связи `{0}` → `all_u8`. Дополнительно все три контроля исключены из множества провайдеров.

В каждом terminal инвентаре четыре `unwind` и четыре `unsupported_construct`, все со статусом SUCCESS. Последние относятся к `is_inbounds`, `same_allocation`, `caller_location` и внешней panic-функции. Нет ERROR/UNKNOWN/UNDETERMINED и exported verification warnings. Общие четыре U: два `usize::abs_diff`, `is_aligned_to` и `fmt::Arguments::from_str`. По одному `pair.unreachable.1` в каждом корне записан со статусом SUCCESS и координатой `lib.rs:0:0`. Суффикс ID не является статусом, происхождение этого site отдельно не квалифицировалось. У P-5b ещё четыре U в проверках индексов/сложения из выключенного split cover. Общей политики приёмки U/нулевой координаты отсюда не выводим.

### Незавершённые зависимости

P-2, P-3, P-4 и P-5c имеют точный selector и initial export после сборки std. Поля native harness kind/stubs/properties, terminal roles, `Q_ABSENT`, U/unsupported/unwind и cover outcomes для них остаются `UNKNOWN`. Нельзя присвоить SAT-сообщения из редукции конкретным cover ID. `INCOMPLETE` совместим с завершёнными промежуточными solver calls и не даёт terminal root verdict.

По исходникам цепочка P-1 → P-2 покрывает все 45 пар base1 окна первых 13 байтов V34. P-2 проверяет actual sort13 на `V34[1..18]` с frame `V34[14..18]`, `Replace swap_if_less`. P-4/P-5c на том же V34/base1/N17 вызывают actual network и insertion loop, используют уникальный набор `{sort13_optimal, insert_tail}`. При `n<18` возврат предшествует merge. Actual loop вызывает четыре вставки с tails13–16, входящие в 1–16 P-3, под тем же порогом и q-монотонным Pre. P-3 Check actual `insert_tail` не использует verified stubs. Эти связи установлены на уровне harness, контрактов и наблюдаемых путей символьного исполнения. Terminal mode/property binding не установлен для четырёх остановленных корней. В Replace caller Pre являются assertions, `old` вычисляется до havoc, а ensures вводятся как assumptions. P-1 поддерживает только локальный шаг. P-2 и P-3 пока не предоставляют завершённых результатов для P-4/P-5c. `P5C_CORRUPT_QPOST` не наблюдался в итоговом инвентаре.

## 3. Где растёт формула

Ниже первое напечатанное число variables/clauses. Шаги и VCC — счётчики symex и simplification, их нельзя переводить в число SAT-клауз по постоянному коэффициенту. Значения получены из объявленных bounded stdout на `8b13284e73`. Логи не содержат профиля SAT-формулы по Rust-выражениям или выделениям памяти.

| Корень | Symex, с | Steps / assignments removed | VCC исходно → после упрощения | SSA convert, с | Первая CNF / последняя наблюдаемая точка |
| --- | ---: | ---: | ---: | ---: | --- |
| P-1 | 0,662 | 29 166 / 17 430 | 2 156 → 536 | 0,411 | 136 839 / 1 406 948, terminal verdict |
| P-2 | 36,929 | 620 151 / 446 330 | 45 905 → 6 351 | — | stdout:3718 `Runtime Postprocess Equation`. RSS cutoff, CNF не напечатана. |
| P-3 | 16,754 | 630 481 / 471 683 | 28 960 → 7 395 | 7,945 | stdout:4505 2 189 578 / 29 598 666. Последняя строка 4623 `Running propositional reduction`. |
| P-4 | 65,128 | 1 512 225 / 1 144 398 | 79 324 → 14 950 | 8,140 | stdout:7242 `Runtime Post-process: 0.217367s` после начала reduction. RSS cutoff, CNF не напечатана. |
| P-5a | 0,565 | 23 459 / 13 915 | 1 960 → 436 | 0,381 | 107 637 / 1 302 607, terminal verdict |
| P-5b | 0,502 | 23 244 / 13 815 | 1 948 → 423 | 0,363 | 104 898 / 1 279 928, terminal verdict |
| P-5c | 59,952 | 1 453 540 / 1 096 312 | 75 919 → 14 825 | 7,753 | stdout:7161 3 782 392 / 25 794 977. Два SAT, RSS cutoff после строки 7171 `Running propositional reduction`. |

На P-3 видны 20 завершённых SAT-вызовов. Из первых четырёх solver calls самый долгий занял 14,867 с. Максимум по всем 20 — 49,279 с, их сумма 256,815 с, сумма decision-procedure timings 268,095 с. Остаток child wall включает непоказанную работу до и после этих записей. Последняя строка фиксирует границу наблюдения, точное время последующей редукции или решения неизвестно. У P-5c два напечатанных solver timings 0,456 и 14,403 с. У P-2/P-4 даже такое измерение отсутствует. Поэтому простой пересчёт нового cap по предполагаемому «оставшемуся SAT» не обоснован.

### Captures и `old`: подтверждённое размножение работы

`sorting_q_model.rs:87–101` читает весь active span и строит `[bool;17]` через `for i in 0..len`. Перед ним `readable_at`, две проверки доступа к fat slice и проверка диапазона длины. `insert_pre` вызывает тот же capture и проверяет монотонность префикса после чтения всей области. `insert_post` заново вызывает capture, затем сравнивает массивы и читает `before.bits[len-1]`. В `smallsort.rs:620–632,639–680` длина выводится из указателей, в `requires` и `modifies` есть отдельные обращения к этому вычислению. Макросы Kani Check/Replace сохраняют `old` после requires и до тела/havoc. Это вычисление включено в формулу даже для предположенного поста. Модель `old` сохраняет биты и q как значения. Она не копирует весь V34 на каждом callee.

У P-3 на `sorting_q_model.rs:97` в stdout пять последовательностей `iteration 1…35`, всего **175** строк. Это согласуется с отдельным capture в harness, capture для Check Pre, `old(capture)`, capture после actual body для ensures и capture в повторной проверке harness post. В P-4 и P-5c по **12×35=420** строк `span`: по три вычисления Pre/old/post на каждый из четырёх Replace `insert_tail`. `len<=17` проверяется в модели, но при символической длине в результате сравнения указателей CBMC всё равно разворачивает до границы 36. Это счётчик развёрток, включая отсеиваемые пути. Он не означает 35 доступов к памяти на конкретном входе.

Сравнение индексов тоже размножается. Общий `Iterator::try_fold` на `iterator.rs:2509` печатает 175/466/450 развёрток в P-3/P-4/P-5c. К этой строке сводятся и проверки постов, и covers, поэтому её нельзя целиком отнести к одной функции. У P-3 actual shift loop (`smallsort.rs:698`) тоже печатает 35 итераций. В harness ещё два цикла от символического `tail`, 35+35 строк, и `Q_ABSENT` на динамическом срезе, 35 строк. Ограничение спецификации 17 элементами не материализуется автоматически как предел развёртки. В терминальных корнях на frame V34 видно ровно 34 шага. Уменьшение общего unwind с 36 до 17 заденет этот frame и actual/инструментальные циклы.

### DP `at_least`: подтверждённая квадратичная часть, предел её объяснения

`sorting_q_model.rs:104–120,242–262` вычисляет `at_least` в массиве из 18 bool с вложенным обратным циклом. На n=13 это 91 обновление, на n=17 — 153. P-2 вызывает функцию дважды: target harness и `old(prefix_capture)` в Check sort13. В P-4/P-5c — target harness N17 и `old(prefix_capture)` в Replace sort13 N13. В stdout на внутреннем цикле строки 250 — ровно **182** в P-2 и **244** в каждом N17 consumer. К ним добавляются формирование `target` и сравнение через `zip/all`, независимо от массива из четырёх байтов хвоста. На конкретных длинах DP разворачивается до 13/17, а не до 35. DP даёт проверяемый источник лишней работы, но P-3 строит 29,6 млн клауз вообще без DP и без `stub_verified`. Оптимизация только DP его не адресует.

### Havoc, writeset и V34: разные слои

В Check инструментирует запись в разрешённый `modifies` actual body. Даже P-1 без DP и без verified stubs имеет 219 `pointer_dereference` checks, семь `assigns` и четыре unwind checks. Те же числа классов есть в P-5a/P-5b. В post/old простого swap вспомогательный `pair` дважды использует `readable_at`, проверки offset, allocation и dereference (`sorting_q_model.rs:80–84,124–132,139–163`). Есть отдельный snapshot и assertion в P-1 harness. Формула P-1 1,41 млн клауз показывает масштаб pointer/contract baseline. Из этого числа нельзя выделить отдельно цену копии V34 или wrapper. P-5b при константном q всё равно даёт около 1,28 млн клауз. Это наблюдение согласуется со значительным остатком инструментирования, но корни различаются и по assertions/covers.

В P-2 на 45 точных pair calls Replace проверяет исходные raw-pointer Pre, вычисляет old pair и два thin havoc из `modifies`, затем предполагает AND/OR пост. Нет `span` и slice havoc. Существенные повторяющиеся части pointer/safety/contract wrapper присутствуют даже при замене DP. Их доля в RSS и шагах неизвестна.

В N17 Replace `sort13_optimal` меняет 13 байтов, а Replace `insert_tail` — spans длины 14, 15, 16, 17 (`smallsort.rs:551–553,663–680`). На tool pin `Replace::Modifies` вызывает `write_any`, compiler выбирает thin/slice модель, `write_any_slice` делает `fill_with(T::any)`. В P-4/P-5c stdout указывает **153** развёртки `slice/mod.rs:4255` в специализации `fill_with::<u8::any>`: 13+4×35. Семантический объём разрешённых записей по исходным spans — 13+14+15+16+17=75 байтовых позиций с повторами между вызовами. 153 отражает расширение циклов, не объём фактической записи. В P-3 на actual сдвиге инструментирование write set и alias/read guards остаются без этого механизма Replace.

Полный `let before=v` и frame V34 нужны для внешних байтов, хвоста sort13, covers и неизменного домена. Это 34 шага на корень, а не 34×45. Frame может удерживать память в SSA и мешать slicing. Логи не изолируют его вклад. Нельзя заменить byte frame одним случайным canary, сократить backing или исключить `modifies` ради измерения. Пороговая маска описывает только функциональные биты. Havoc, provenance, проверка указателей и frame байтов остаются на прежних местах.

## 4. Кампания 2: одна замена представления

Наиболее локальный общий патч — `sorting_q_model.rs`: заменить только массивы пороговых битов в span/prefix/target на owned `u32`, bit `i` соответствует `value[i]>=q`. Скан длин 0–17 задать 17 константными смещениями, каждое чтение `begin.add(i)` или `values[i]` внутри `if i < len`. Можно расширить короткий макрос на литеральные смещения. Сохранить общий guard допустимой длины, проверки последнего адреса и fat slice, inactive dispatch, валидность snapshot, q и фактическую длину. Нули за пределами len обязательны. У sort13 отдельно сохранить четыре исходных байта хвоста. Меняются типы model helpers, их места вызова могут оставить те же локальные переменные с выводом типа. Swap pair и его оба mutants оставляем как есть.

Эквивалентность на прежних входах проверяется формулами ниже. `M(n)=(1_u32<<n)-1` при `0<=n<=17`. Проверки корректности длины должны предшествовать вычислению `len-1`, shift и чтениям. `count_ones` на `u32` имеет lowering через `ctpop` → `arg.popcount()` в `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs:760–772` на `0aac16ef`. Это поддержка операции по исходнику, размер получаемой схемы ещё предстоит измерить.

- **Order-stat.** Для входной маски `B` и `c=B.count_ones()` прежний DP требует `bit[k]=(c >= n-k)`. Это в точности `M(n) ^ M(n-c)` с единицами на последних c позициях. На тех же входных и выходных длинах сравнить всю упакованную выходную маску с этим target. Для буквальной эквивалентности прежнему `zip` у общего helper сравнивать с `target & M(values.len())`. Сохранить прежние guards длины и q-frame. При `n=0` обе маски нулевые, при `c=0` или `c=n` крайние случаи следуют из той же формулы.
- **Insert Pre.** У префикса `P=B & M(len-1)` нет соседнего перехода 1→0 тогда и только тогда, когда `((P << 1) & M(len-1) & !P)==0`. Это та же проверка каждого соседнего бита префикса, без требования численной отсортированности.
- **Insert post.** При `len>=2`, прежних valid/equal len/q checks и последнем бите `b` сравнить `after` с `before` при `b=1` и с `(before<<1)&M(len)` при `b=0`. Маска сохраняет прежнее позиционное равенство каждого бита и условие нуля в начале. Вывод не зависит от q-монотонности и не требует нового assume. Pre, post, covers всех tails и q-absent, duplicate harness assertions, safety checks, byte frame, actual calls и `modifies` остаются. Native control P-5c по-прежнему меняет бит для `[0;17],q=1`, записывая 255.

**Оценка эффекта по наблюдаемой структуре.** Удаляются 182/244 DP updates с динамическими индексами в пользу двух popcount и построения двух target masks в P-2 и N17. Точки сравнения `x>=q` остаются для каждого элемента и каждого оценивания Pre/old/post. В span пять сканов P-3 и двенадцать сканов каждого N17 root будут иметь максимум 85 и 204 защищённых позиции соответственно вместо 175 и 420 наблюдаемых unwinding шагов тела `span` (около 51% меньше для этого участка). Отдельные итераторные проверки битов уступают место нескольким scalar operations. Фиксация смещений уменьшает динамический доступ к backing через индекс и исключает массивную индексацию порогового snapshot. Каждая загрузка и её safety obligation сохраняются, когда элемент действительно входит в span.

Это оценка кодировки, без оценки процента от 29,6 млн клауз. Большие части останутся: 45 pair Replace в P-2, четыре slice havoc в N17 и actual sift/CopyOnDrop и pointer guards в P-3. При другой схеме solver время может меняться немонотонно. Ожидаю меньшие symex expression/VCC и меньшую нагрузку на SSA/reduction, особенно у N17 consumers со множественными сканами. P-2 может по-прежнему уткнуться в RSS из-за пары/контрактов, P-3 может по-прежнему достигнуть cap на actual sift или SAT. Логи первой кампании не показывают, какой выигрыш достаточен для fit.

Для проверки подготовить один reviewed candidate с этой заменой под тем же tool, roots, argv, unwind36, V34, 600 с и 6 GiB. До запуска сверить граничные `len=0,1,2,17`, q=0/255, короткое замыкание перед чтением, отсутствие bits выше активной длины, старую и новую семантику масок и сохранение всех контрольных меток. Не менять cap и кодировку одновременно. Сравнивать по корням числа unwinding по site, program steps/VCC, первые CNF counts, фазу cutoff, sampled RSS и полный inventory. У P-2/P-4 baseline CNF отсутствует, улучшение там можно оценить по первой напечатанной CNF или terminal результату, а также steps и RSS. Повтор ожидаемых P-1/P-5a/P-5b и P-5c с единственным `P5C_CORRUPT_QPOST` необходим для сигнала. Цель P-2 и P-4 остаётся child≤300 с, все positives с covers. Если остаются ранние cutoff, следующим отдельным вопросом профилировать pair pointer guards на P-2 и slice havoc на N17. Не экстраполировать размер формулы N17 на N32.

Кампания 2 остаётся предложением для отдельной реализации, ревью и GO. Кампания 1 ограничена exact byte доменом, OFF и геометрией V34. Merge/panic на маршрутах со слиянием, UB/ON, другие T/F и длины, qualification и независимый B1/B2 credit остаются открытыми.
