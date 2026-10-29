# План проверки SCOPE — НЕ ВЫПОЛНЕН

Объект: library-коммит `c8fce2febdb97e73ab13ebe5d58d026a1e036087` на основе точной
библиотеки `e9655515`. Последующие documentation-only commits допустимы только при проверке
идентичности library tree. Текущая сессия не запускала builds и не резервировала CI.

## Проверки и критерии

1. На том же SHA выполнить компиляцию/codegen и `kani list --format json` с ordinary cfg и
   отдельно с `RUSTFLAGS="--cfg kani_smallsort_controls"`. Не использовать не поддерживаемый
   `kani list --harness`. Сохранить SHA, pin Kani/CBMC, toolchain, cfg, flags и фактические inventories.
   Сопоставить standard/contract harness names с manifest.tsv: ordinary116, controls423.
   Источник этих чисел — Python forecast, поэтому расхождения расследовать, не подгонять фактический list.
   Если ZST contract блокирует codegen, отметить blocker отдельно: FAILED counterexample это не заменяет.
2. Compile/PASS ordinary и PASS280 opt-in проверять отдельно от FAILED26. Применять существующий
   selected lane с controls=false/true и явным exact списком; PASS переводится в request `SUCCESS`.
   Результат каждой выбранной гармоники обязателен, TIMEOUT/NOT_RUN/MISSING_RESULT/runner error не PASS.
   Старый deferred ZST-contract остаётся отдельной диагностикой; он не часть PASS/FAILED gate.
3. Полный ordinary std: все четыре партиции на **Linux и macOS**, то есть8 jobs, с существующими
   organizer script/pin/flags и worker indexes1..4. Считать партиции заново по фактическому
   inventory всего std: уменьшение SmallSort меняет границы, старое имя partition не является evidence.
   Не подменять этот этап selected SmallSort. Текущий workflow ограничивает Linux partition jobs2;
   macOS использует свой существующий default. Эти режимы не смешивать с autoharness jobs3.
4. Полный `kani_autoharness` на **Linux и macOS**, включая остальные std manual и automatic
   harnesses с оригинальными include/exclude, unwind1000, jobs3, timeout10m/harness, terse и
   failure propagation через tee/gzip. GCB Linux emulation — существующий C3c `kind=autoharness`,
   empty explicit harness list и whole-job budget; selected list не эмулирует весь job.
   GCB Linux не заменяет macOS acceptance. Не менять workflow ради этого SCOPE.
5. Opt-in на том же library tree: выполнить **все280** positive extensions, включая68 прежних
   opt-in positives и212 перенесённых; отдельно26 negative controls и deferred diagnostic.
   Expected FAILED принимать только при локализованном предусмотренном нарушении свойства.
   Запуск всего controls cfg с единым ожиданием SUCCESS ошибочен. Для old stub callers сохранять
   статус conditional composition: прохождение не закрывает allocation-locality transfer автоматически.
6. Covers audit: для всех перенесённых212 proofs их прежние covers должны присутствовать при controls;
   для сохранённых116 — при ordinary. Проверять SAT/UNSAT/unreachable по применимости, не только
   overall SUCCESS: runner не отвергает unreachable covers автоматически. Отдельно C3a N0/1
   applicability fix, пять Cell N7 covers, type matrix12, normal-return dispatch и all-offsets20.
   E не применён, поэтому source-diff должен содержать лишь item cfg. Если вводятся C3c splits/E
   позднее, нужны новый union map, helpers и отдельный повторный migration audit.
7. Contract audit: отсутствие ordinary `stub_verified` подтвердить раскрытыми атрибутами.
   Проверить exact type/comparator/N/allocation/begin/end для standalone proofs. Для opt-in
   `correct`/`merge` не объявлять разрешёнными gaps begin0/shifted17/exact-N/scratch48 из-за
   одного ordinary callee proof. Положительные/отрицательные contract controls сверить отдельно.
8. Для ordinary и autoharness собрать per-name VT, wall/start/stop/thread, memory PID+model
   attribution, driver/CBMC/cgroup simultaneous peaks и OOM status. Пересчитать сумму/max/число>120,
   четыре UNKNOWN C3a, число одновременных тяжёлых proofs. Не складывать независимые RSS maxima.
   Все8 partitions и оба autoharness должны завершиться; source audit этого не доказывает.

## Команды воспроизведения, только для будущего удалённого запуска

`reproduction_commands.py --manifest {ordinary,extended-positive,controls-failed}` печатает
exact-name команды для одного списка; сам ничего не выполняет. Он очищает worker vars, поэтому
organizer partition mode не перехватывает selected список. Controls cfg задаётся лишь двум opt-in
спискам, ordinary очищает RUSTFLAGS. На удалённом runner нужно предварительно воспроизвести pin/setup
и именно указанный SHA. Выходы FAILED26 собирать по одному, не прерывая серию на первом ожидаемом fail.
Для эффективности допустим один selected request на chunk с теми же exact именами/ожиданиями.
Deferred ZST не добавлять в positive список для получения зелёного общего результата.

## Время и стоимость, $0,0135 за оплачиваемую минуту GCB

Изменённый состав не измерен. GCB wall, стоимость всего плана и Mac wall **UNKNOWN**.
Рабочая известная Mac сумма3583,3 с +4UNKNOWN — не GCB wall и не billable minutes.
Калибровки C3a нет. Для прочих оставшихся семей также нельзя автоматически применять один r.
Исторические inventory/setup занимали около49 мин; это ориентир накладных расходов,
не обязательная добавка к каждому cached invocation.

Ниже **плановые envelopes**, не прогноз прохождения и не разрешение отправки:

| Будущая часть | Предлагаемый envelope | GCB стоимость envelope |
|---|---:|---:|
| Codegen/inventory двух cfg | 2×60 мин | $1,62 |
| Диагностика8 известных>120 +4C3a, memory/covers | 90 мин | $1,215 |
| Полный Linux autoharness C3c | timeout300 мин, work270 | максимум$4,05 |
| Один Linux ordinary partition job | 300 мин | максимум$4,05; четыре job максимум$16,20 |
| Positive opt-in:7 chunks по40 имён | 7×210 мин | максимум$19,845 |
| FAILED26 отдельно | 150 мин | максимум$2,025 |
| Deferred unsupported diagnostic | 60 мин | максимум$0,81 |

Первые четыре строки нельзя назвать ожидаемой длительностью; полный std runtime не выводится из
SmallSort VT. При40 proofs/chunk, jobs3 и10 мин/case идеальная верхняя граница proof scheduling
`ceil(40/3)×10 =140 мин`; envelope210 оставляет70 мин на setup/list/дополнительные действия,
но внешние setup/compiler stalls всё равно могут сорвать его. 7chunks×40 =280 positive proofs.
Для FAILED26 идеальная timeout-граница `ceil(26/3)×10=90 мин`, envelope150 включает60 setup.
По аналогии116 ordinary proofs дают `ceil(116/3)×10=390 мин` только для capped selected
proof schedule, а не прогноз полного autoharness, не обещание completion и не достаточный
single-build budget существующего300-минутного lane. Для отдельной selected диагностики нужны chunks.

Итого перечисленные **Linux/GCB envelopes =3390 мин, $45,765** при четырёх partition jobs;
это намеренно консервативный резерв полного плана, не заявленная цена новой попытки и не открытый бюджет.
Mac4 partition +autoharness jobs требуют отдельного ресурса/тарифа: ставку GCB к ним не применять.
Часть setup может быть общей/cached; после первых измерений пересчитать envelopes с сохранением
реальных coordinator/owner/slot ограничений будущего этапа. П-6 история и C3c PARTIAL не дают права
писать «новый состав доказан» до выполнения указанных проверок.
