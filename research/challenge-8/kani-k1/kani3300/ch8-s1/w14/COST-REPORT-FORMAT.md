# R8 cost-report format v1 — будущие S-прогоны

Это спецификация отчёта, **не dispatch request/GO**, не изменение organizer workflow.
`cost-report.template.json` — пустой экземпляр для одной ОС/пары baseline-new.
Нужны экземпляры Ubuntu и macOS; jobs1 prototype отдельно от actual organizer parallelism.
Missing/null/unsupported означает UNKNOWN; fields с пустыми списками не означают zero-cost PASS.

## Связка run / arm / root

Для каждой запланированной попытки: campaign/stage/unique dispatch ID, owner GO reference,
ledger/reserve/attempt ordinal, run/job IDs+URLs, original exits и infrastructure outcome.
Infra failure расходует credit; нет автоповторов или выбора лучшего из нескольких attempts.
Не расходовать старый18 budget как автоматическое разрешение новых14 S dispatch.

Пара arms **baseline/new на одном exact новом upstream Kani pin** и совместимых organizer
flags/CBMC/solver/runner images/resources/jobs. Baseline — старая235 suite на named source
с только явно задокументированной необходимой pin-compatibility адаптацией. New — retained old
roots плюс все новые qualified leaves/consumers; replacements имеют отдельный review/map.
Исходный cd355b0b run остаётся historical reference, не matched arm нового pin.
Если baseline невозможно выполнить без semantic изменения — mismatch/UNKNOWN, нужен явный review;
не объявлять два разных scope одним matched run.

Обязательные identities: exact std commit/library tree, tool commit/binary identity,
workflow/script/config/recipe hashes, full argv/env **как данные**, flags/panic stub/extra-UB,
selected root manifest sha256, ordered full organizer manifest+shard boundaries, source body,
PFC target, contract/model version, Original/Replace mode, T/F, symbolic lengths и geometry.
Новый accepted root требует body+requires/caller/control qualification; diagnostic с
assumed summary не входит в accepted proof inventory. Его ресурсы видны отдельно, не теряются.

## Таблицы

1. **Per-root TSV**: arm/run/job/shard, exact root/body/contract/model, T/F/domain/topology/
   initialized+writable ranges, property, qualification, ordinary/control/diagnostic,
   original driver/backend exits, status, expected failure check (controls), required/satisfied
   covers, Kani VT, root elapsed, phases, measurement status и evidence reference.
2. **Process resources**: driver/backend/checker/compile wall и peaks по phase где доступны;
   `root_process_tree_rss_peak_bytes` — peak суммы **одновременно живых** driver/backend/
   descendants данного root. Указать method/platform/sample period/доступность детей/coverage.
   Общий driver, обслуживающий несколько roots, не распределять произвольно между ними:
   дляsingle-root aggregate использовать изолированный jobs1 arm или явно shared attribution.
   `max(child_RSS)` и сумма разных во времени maxima не заменяют aggregate.
3. **Per-shard**: ordered manifest hash, all/SmallSort/qualified/control/diagnostic counts,
   summed SmallSort VT, full shard verify elapsed, setup/compile elapsed, whole job elapsed,
   synchronized aggregate RSS, actual observed concurrency, OOM/kill/timeout/skip statuses.
4. **OS summary**: sum ordinary SmallSort VT (retained+new leaves+consumers, каждый physical
   root occurrence один раз), max root VT и root elapsed, worst shard и longest elapsed,
   full workflow elapsed, sum runner elapsed, measured jobs2/16GiB peak/reserve,
   controls и diagnostics cost отдельно. Если workflow повторно проверяет тот же root в
   partition и autoharness, хранить обе execution populations; не складывать их как один VT
   baseline. All-CI cost/runner-seconds при этом включает оба фактических исполнения.
5. **Delta/gates**: same-mode baseline/new ratios per OS, retained/removed/added roots,
   replacement map coverage и scope exceptions. Ordinary inventory должен совпасть
   с compiler inventory и selected job targets; unexpected skip — не PASS.

## Условия R8

| Проверка | Вычисление / правило |
|---|---|
| Matched total cost | `new.sum_ordinary_smallsort_VT / baseline.sum_ordinary_smallsort_VT <= 1`, отдельно OS/mode; без смешения jobs3 autoharness/jobs2 partitions |
| Historical absolute objective | сравнить с опубликованными ≈7802s/10534s; unrounded historical reference7801.879658047/10534.459671914s. Не создавать FAIL от округления10534; явные deviations/owner exceptions |
| Root time ceiling | `VT<=600s/root` в сопоставимой historical метрике; root elapsed и timeout scope отдельными полями. Backend-only timeout не устанавливает full-root fit. Не увеличивать timeout ради PASS |
| RSS design target | single-root aggregate driver+backend descendants≤`6*2^30`bytes; goal status отдельно. Не объявлять измеренным по backend peak |
| Jobs2/16GiB fit | actual concurrent run `jobs=2`, `MemTotal`/cgroup limit вbytes, synchronized process aggregate+whole-host/cgroup used/available minimum, измеренный OS reserve>0, noOOM/kill/swap-thrashing/timeout; числовой planned reserve фиксируется перед run |
| macOS fit | actual organizer parallelism (historical autoharness3, partition default) на фактическом runner; 7GB host не считается16GiB; при changed jobs separate explicit configuration/delta |
| Shard/elapsed | worst shard + full elapsed обязательны, per-shard delta и fit job/deadline/resource envelope. Lower total не доказывает critical-shard fit; отсутствие измерения → UNKNOWN |
| Proof/coverage | все retained+new ordinary qualified, required controls calibrated, no assumed-summary credit, matching source/type/F/domain/geometry; никакого урезания required safety/negatives |

600s VT и600s полного root elapsed нельзя незаметно отождествлять: если available organizer
telemetry сообщает толькоVT, root elapsed остаётся UNKNOWN. Отдельный hard ceiling полного
root elapsed здесь не вводится; для его fit использовать заранее названный runner/job envelope.
RSS≤6GiB — проектная цель, а measured concurrent fit — отдельный обязательный gate.
Miss target → REVIEW с конкретной памятью/запасом; pass одногоroot не даёт jobs2 PASS.
Сумма2×6GiB — capacity estimate, **не измеренный** fit16GiB.
GitHub specs16GB сохранять в исходных единицах; actual host bytes служат источником проверки
16GiB premise. Не переименовывать фактический15.xGiB host в16GiB без раскрытия/решения.

Gate values: PASS / FAIL / UNKNOWN / REVIEW. Общий R8 PASS допускается только при известных
обязательных числах, matched identities, полной qualified coverage и подтверждённых fit gates;
goal deviations/explicit owner exceptions раскрываются. UNKNOWN/NOT_RUN/timeout/infra-failure,
обычный skip, нулевые measurements и отсутствие roots не превращаются вPASS.
Historical report содержит UNKNOWN RSS/root wall и потому сам R8 не закрывает.

## Evidence receipts

Хранить units/method/coverage, original exits и references к разрешённым bounded summaries.
Для Cloud использовать coordinator и Evidence Brief: terminal Brief→catalogue→pinned file ID→
точное поле/страница. Для существующего GitHub — metadata/curated summary или ограниченная
HTTP206 выборка с range/identity; не полный raw log/archive. Parse mismatch, missing/null,
wrong-type, explicit NOT_RUN и source-stage-target mismatch раскрывать, не синтезировать успех.
Этот документ не меняет runner: instrumentation/service error-path checks готовятся и ревьюятся
отдельным владельцем CI, если для замеров понадобится runner patch.
