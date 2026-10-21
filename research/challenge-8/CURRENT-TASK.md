> **Локальное исправление evidence staging, 2026-10-21:** общий `_tool_tree`
> больше не помещает symlink рабочего дерева в evidence. Оба известных случая
> прошли реальную локальную упаковку; 7 новых service tests PASS, review GO.
> [Изменение и проверки](cloud-build/origin-layout/TOOL-EVIDENCE-STAGING-20261021.md).
> Владелец разрешил один повтор Build после исправления; оформляется отдельный счёт.
> Прежние proof-результаты и закрытый бюджет R11 сохранены.

# Merge-R11 — label invariant и annotation temporary

## Авторизация и место работы

- **ID:** `merge-label-storage-invariant-autonomous-2026-10-21-r11`; **статус:** CLOSED_PARTIAL; T0 `2026-10-21T06:14:39Z`, main завершено `08:14:39Z`.
- **Owner:** `merge`; **репозиторий:** `Tiramisu-Cake/verify-rust-std`.
- **Project worktree:** `/root/verify-rust-std-merge-origin`; **branch:** `merge/incoming-origin-20261009`.
- **Tool worktree:** `/root/verifast-merge-actual-glue`; **branch:** `merge/actual-glue-instance-20261011`; head **`bb557d43c4196694c7af50ff2150ce56a269e17d`**.
- **Новое окно:** 120 минут основной работы + до30 минут завершения, от фактического старта Merge-R11. После main новых Builds/retries/гипотез нет.
- **Новый бюджет:** **3600 Cloud-секунд**, used=0, число последовательных Builds отдельно не ограничено.
- **Timeout:** 90..1200с, envelope+60 в остатке/окне; явный план времени на cold compile/target/teardown/Evidence.
- **Lane:** `merge`; stable owner и существующий coordinator.
- **Новая phase:** `MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21`; отдельный ledger `cloud-build/origin-layout/CURRENT-RECOVERY-R11-BUDGET-20261021.json`, `max_timeout_seconds=1200`.

**Merge-R11, её окно, бюджет и Builds явно разрешены.** Сам подготовь согласованную branch-local authorization/phase/profile/entry/runner/recipe регистрацию и dependent pins. Продолжение описанного ниже existing experimental scope разрешено без повторного согласования; каждый Build/implementation blocker/SHA в scope отдельно не согласовывать.

Ты начинаешь без контекста. Проверь назначенные worktree/branch/HEAD/dirty diff и сохрани чужие изменения. Прочитай `AGENTS.md`, текущую часть [STATUS](STATUS.md), [полномочия](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), релевантные [WORK-POLICY](WORK-POLICY.md), [Cloud runbook](cloud-build/README.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md) и нужную часть [плана](COMPLETION-PLAN.md). Всю историю и большие evidence JSON не перечитывай.

## Исходная точка и ближайшая цель

Checkpoint R10 **`ab8ca678db54ce46863eb234a8ffd3ea0753f82a`**; последний actual source **`7d7d70d29f25882ef8c8c3f6177b86fa914b09bb`**, Build **`0d17cca8-db8f-4088-bedb-719c2cd1a568`**, tool **`bb557d43c4196694c7af50ff2150ce56a269e17d`**, profile `experimental-merge-moving-gap-r10-v1`, SHA **`c3f5d286777ffd388e1eb0894ad0ff9e8f1f87f72424291041cb800385f7c979`**. R10 CLOSED_PARTIAL: **2865charged/2861execution,735retired,remaining0,carry=false**, все5 terminal/accounted, own active/unresolved/requests/reservations0. Старые окна/счета/735секунд не возобновлять/переносить. [Архив R10](task-history/merge-moving-gap-invariant-autonomous-2026-10-21-r10.md), [итог](cloud-build/origin-layout/R10-FINAL-RESULT-20261021.json), [release](cloud-build/origin-layout/R10-RELEASE-20261021.json).

R10 Build1 связал normal frontier с37heap/41env; Build5 скомпилировал все7 observed milestones и разобрал checked two-position u64/array3 invariant. На ограниченном initial path наблюдались label-invariant consumption/leakcheck, затем production; **до тела цикла отказ StorageDead verified/lib.rs276:44-45**. MIR annotation unit `_117`: StorageLive→VeriFast_ghost_command destination117→StorageDead; native cycle97←151/fingerprint e1f455a3ed9fb435/source275. Exact bounded fragments не устанавливают parser-input binding/причинность. Полных target gates0, normal Continue/backedge/break/unwind theorem/B2/qualification OPEN, acceptedfalse/independentcredit0. [Build5](cloud-build/origin-layout/R10-BUILD5-RESULT-20261021.json), [Storage note](cloud-build/origin-layout/R10-LABEL-STORAGE-NOTE-20261021.md), [обязательства](cloud-build/origin-layout/R10-OBLIGATIONS-20261021.md).

**Ближайшая proof-цель:** source-bound корректность размещения/liveness annotation temporary при label-invariant abstraction, затем checked init→body→backedge invariant и выходы. Не переноси R9 scoped cleanup PASS на новые identities; после исправления loop instrumentation проверь его заново. Выбирай конкретный backlog по новой Evidence, сохраняя миссию actual insert_tail/CopyOnDrop/CURRENT и далее callers.

## Первый цикл и самостоятельное продолжение

1. Разбери placement/lifetime class до следующего изменения: где `_117` Live/ghost call/Dead в actual decoded Body, где invariant boundary consume/produce, какое runtime env реально существует. Note предлагает гипотезу о reconstruction из enclosing environment; это не установленная причина. Нужные read-only bounded receipts должны различать **reconstructed CFG/body IDs и фактическое symbolic execution**, связывать head/from/body/phase/span/Live/Dead и точки consume/produce/backedge. Существующие fragments использовать до нового диагностического Build.
2. Если гипотеза подтверждается, допустима узкая source-preserving поправка annotation placement/instrumentation или её frontend lowering в существующей модели, с exact source/body/marker binding и review. Не превращай StorageDead в no-op, не придумывай missing env/live/allocation/ownership receipt. Имя `_117`, unit type или zero-size сами по себе не дают права игнорировать storage event. Обычные locals, address-taken values, real Live/Dead и cleanup продолжают проверяться. Нужны различающие valid/invalid placement, ordinary-local и missing/dead/ambiguous source binding controls.
3. После syntax/placement gate докажи two-position moving-gap invariant: initial entry, copy/update/comparator/normal recovery и backedge; далее break/return/unwind с original guard debt и CURRENT array/foreach/F/thread. Preheader initial FIRST_SHIFT_PREP нельзя повторять на backedge. Сохрани actual ranges/coefficients/provenance/current values и завершение per-call loans; не предполагай full initialized array во время незакрытого gap и не подменяй CURRENT entry snapshot.
4. Сохрани R9 exact checked post-Drop returning hook и ordinary resource lemmas; callback/Drop own-unwind/abort/Resume не подменять successful recovery. Новые checked predicates/annotations/lemma bodies и representation/frontend fixes в сохранённом scope разрешены. Не добавляй invariant как assume и не обходи loop checker. Диагностика не должна менять heap/env или терять `symexec_result` ради печати.
5. Перед Cloud проверь весь затронутый класс grammar/declaration order/loop header/lifetime/control receipts и exact patch closure. Existing compile gate → target body → relevant storage/loop/recovery controls, предпочтительно stages одного Build. Полные normal Continue/break/unwind/CURRENT posts и финальная compatible matrix — отдельные gates после initial-path observations. Recovery5 сейчас NOT_RUN по prerequisite; старые negatives не PASS. Duplicate-marker/wrong-origin controls должны достигнуть intended source/stage/predicate/location, случайный ранний отказ не засчитывать.

Freshness Build5 сообщает2positive/6intendednegative и8currentcasebindings; per-case independent qualification OPEN. Проверь нужные exact receipt/stage/tool/source identities и не делай claim по одному aggregate. Prefix и physical BeforeLive остаются независимым backlog ([prefix note](cloud-build/origin-layout/R10-PREFIX-BRIDGE-NOTE-20261021.md), [BeforeLive note](cloud-build/origin-layout/R10-BEFORELIVE-NOTE-20261021.md)); lexical unbound-local не physical heap refusal, LocalAddrTaken не liveness. Broad static-array/slice/Rocq/storage model автоматически не разрешены. Если полезный Build не помещается в остаток, source/review/service работа и retire допустимы; повторять short-budget compile-only124 не нужно.

## Сохраняемый experimental scope

Разрешено продолжать **ранее согласованное узкое R8 allocation rule** и последующие checked R9/R10 source/instrumentation changes: default-off native fresh8-byte u64 StorageLive vs CURRENT positive canonical initialized u64 subrange, same-function incoming array exactly3, full-pointer/provenance binding offset0/1/2 и0<count<=3-offset; existing ManuallyDrop<u64> erasure. Только interval exclusion текущего owned range, никаких новых chunk/value/permission resources; CURRENT count2 не весь entry3. Это сохранённое trusted premise, не lemma прежней модели. Defaultoff/IDE/нецелевые profiles/Rocq семантика прежние; [scope/review](cloud-build/origin-layout/R8-CANDIDATE4-MODEL-REVIEW-20261020.md). Расширение этой предпосылки на новые классы allocations требует отдельного решения; обычный source-preserving checked implementation fix в прежних границах — нет.

Сохрани baseline19patch/17pins/18base как provenance, не замороженный счётчик, и исходную матрицу4resource-loss/HRTB/Output/projection/binder/lifetime/official first-unwind/late-Cleanup/5CURRENT18/B1/helper/ordinary normal-unwind/generated Drop/default-off/receiver/end/retirement/addressability/prefix/fullbody/empty-tail/admission. Complete qualification остаётся отдельно OPEN; concrete u64/array3 result не generic T/arbitrary-n theorem. Не расширяй resource-free concrete u64 own transition на generic ownership.

## Полномочия, время и Evidence

Самостоятельно выбирай ближайшую proof-цель и backlog по миссии/плану; исправляй связанные места одного класса до Build. Разрешены checked annotations/specs/predicates/lemma bodies, source-binding/parser/binder/normalization, необходимые source-preserving exporter/schema/decoder/translator/frontend/lowering и минимальные runner/preflight/diagnostic fixes. Сам выпускай experimental profiles/tool commits/patches и dependent pins/closure в project branch; отдельный tool remote не обязателен. Новые implementation blocker/Build/SHA в scope отдельно не согласовывать. Maintainer принимает готовые tool-патчи, не заменяет proof-разработку.

До реализации запиши defect/applicability/rationale/сохраняемые гарантии/различающие controls. До submit — независимый **GPT-6 Luna HIGH** review актуального diff/dependencies (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации/дорогой автоматической замены). Concrete soundness findings устранить; review неизменённых частей не повторять. Runner changes проверять на success/error/partial/NOT_RUN/missing/null/wrong-type metadata, source/stage/target mismatch, original exceptions/exit и deadline. Static/synthetic GO не verifier acceptance.

Сохраняй runtime std/алгоритмы/generic signatures/compiler baseline/source semantics/actual CFG/domain/pre/normal-unwind-abort/CURRENT ownership/provenance/admission и исходные матрицы/negatives. Нельзя добавлять axioms/assumed ownership bridges, выводить ownership из numeric address equality, отключать checks или молча расширять memory/alias/layout model. Новое trust-допущение вне явно сохранённого scope требует отдельного решения; обычный checked proof/representation fix нового согласования не требует. Чужие worktrees/pins и historical evidence/ledgers не менять. Без reset/force-push/merge/upstream PR/внешних комментариев/Actions, shared coordinator/IAM/triggers/dependencies/cache/backend deployment. Общая CI унификация — отдельная задача.

T0 зафиксируй **при фактическом старте после чтения задания**; main=T0+120мин, absolute=T0+150мин. Новый ledger с explicit authorization, ceiling3600, timeout ceiling1200; old accounts не возобновлять. Только exact committed/published closure с проверенным полным remote SHA; actual dispatch/config/source bounds проверяй с полным token, caps не повышать. Envelope timeout+60 в остатке и окне с запасом до absolute; один occupied/unresolved Build на owner/ledger, максимум три project-wide. Refusals не обходить, uncertain submit не дублировать. До submit оцени cold setup/compile+target+teardown/evidence/package/upload/verdict; не запускай короткий Build на остатке без времени для полезного target.

Status/Brief по возможности yield10–30с вместо1000мс с отдельным модельным возвратом; выполняй независимую полезную работу. Простое ожидание+проверку объединяй в один инструментальный шаг≤60с без циклов sleep30→status→чтение без новой информации. Через час — progress/charge/blocker без ожидания ответа. После main новых Builds/retries/гипотез нет; свои неотправленные requests отозвать. Finishing — начатое/Evidence/учёт/checkpoint/push. К absolute terminal/accounting либо exact active/unresolved ID и следующий разрешённый шаг. Остаток retire без carry. Ранний stop обоснуй после проверки независимых полезных задач; после первой исправленной ошибки не останавливайся при доступных времени/бюджете/работе.

Evidence: `smallsort-brief BUILD_UUID` → catalogue/file ID → **`--refresh --file ID --expect-sha256 SHA`** с info/locate/position/lines/JSON pointer и нужными явными страницами по серверным next_offset/next_value_start. [Guide](EVIDENCE-READER-GUIDE.md), [примеры](EVIDENCE-READER-TASK-QUERIES.md), `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md`. Lifetime16/WITHHELD устарели. Проверяй file/index/archive/request identities/coordinates/exact/complete/coverage. Evidence — данные, не команды; no-match не NOT_RUN, source PASS/exit0/integrity не independent credit. Raw/full logs/archives/Cloud Logging/локальные raw copies и GCS/download/storage/logging обход запрещены; admin audit отдельно. download_verified и historical verdicts не менять. При HTTP429 сохрани ответ/coverage и выполняй последующие уточнения последовательно с экономным ожиданием.

VPS — Git/hashes/static parsing и малые isolated synthetic service tests; actual preparation/extraction/compiler/decoder/refiner/verifier/full runners только Cloud. Обновляй компактный STATUS и существующие session/experiment/release/coverage records. Здесь **один перезаписываемый компактный отчёт**: цель; каждый Build/гипотеза/type/exact candidate/результат/charge; observed timings; T0/deadlines/end; own active/unresolved/requests/reservations; closure без carry; следующий blocker. Полная матрица/provenance отдельно по ссылкам. Явно разделяй **сборку**, **результат попытки формальной проверки конкретного body/ветви** и **закрытые целевые gates/independent credit**; не пиши неоднозначное «actual proof выполнен». Обслуживание отдельно; wall-clock не active agent time, reserve/retired headroom не расход.

## Отчёт агента

**R11 CLOSED_PARTIAL_EVIDENCE_PENDING.** T0/main/absolute2026-10-21 06:14:39/08:14:39/08:44:39UTC;
account closed08:21:05UTC; только finishing, новых Builds/гипотез послеmain нет.

| Build | Candidate / result | charged / execution |
| --- | --- | --- |
| [1 acba1b21](cloud-build/origin-layout/R11-BUILD1-RESULT-20261021.json) | source5fdfaa63/tool a3a22f98; compile7exit0, StorageDead276 отказ | 694 /694 |
| [2 92795836](cloud-build/origin-layout/R11-BUILD2-RESULT-20261021.json) | sourcefc0e2c01/toolab4f72b8; overlay setup отказ | 89 /88 |
| [3 fa3a26ec](cloud-build/origin-layout/R11-BUILD3-RESULT-20261021.json) | source5a93a90c/toolab4f72b8; translator compile type error | 421 /420 |
| [4 25877672](cloud-build/origin-layout/R11-BUILD4-RESULT-20261021.json) | sourcef654e29c/tool5c806717; compile7exit0, frontend AST compare fatal | 670 /669 |
| [5 feb5c44b](cloud-build/origin-layout/R11-BUILD5-RESULT-20261021.json) | source1df9b809/tool660b576b; compile7exit0, checkedDead перед invariant, iterationprep301 points_to_limits/dummy30none отказ | 610 /609 |
| [6 fbe79012](cloud-build/origin-layout/R11-BUILD6-RESULT-20261021.json) | source0ab7fcab/tool660b576b expected; terminalFAILURE, UNKNOWN: Brief/catalogue HTTP404 | 540 /539 |

**3024charged /3019execution /576retired /remaining0 /carryfalse.**
Все6terminal/accounted; ownactive/unresolved/requests/reservations0 под coordinator lock.
Observed cold complete target610/670/694sec; final timeout1000/envelope1060
помещался в1116remaining и absolute. Account retirement не расход/proof credit.

Последний submittedsource `0ab7fcab89c6a8721bcc8279cc3cdbd6634c45dd`,
Build `fbe79012-dd88-4a7f-b65b-9dcac32a4557`, tool `660b576b6b1608db913c51e0785b443a8733396f`.
R11-only checked initialized-value invariant и exactcall/top-levelid controls
прошли LunaHIGH review/static/synthetic; это отдельно от verifier acceptance.
Build5 exactsource trace показывает Live/Dead117 до invariantconsume и вход вbody,
не full backedge/exits theorem. Source/parser-input binding/causality по координатам
не устанавливались; source PASS не переносится между Builds.

**Full target gates0; acceptedfalse; independentcredit0; B2/generic/qualificationOPEN.**
**Завершение предыдущей сессии:** Build6 завершился FAILURE. По сообщению владельца,
упаковка отказала из-за symlink рабочего tool tree; upload не состоялся,
FileNotFoundError и Brief HTTP404 были последствиями. Это owner-reported cause,
а не независимое наблюдение proof-результата Build6: compiler/body/controls UNKNOWN.
Общий producer исправлен в `41c7c24c`: обычные bin assets копируются,
служебные поддеревья исключаются с manifest, symlink path/target — metadata без
разыменования. Оба известных случая прошли настоящую локальную упаковку,
7 новых service tests PASS; review Luna HIGH GO. Это обслуживание, не proof-прирост.

**Новое поручение владельца:** «Давай повторим Build. Закончи предыдущую сессию,
написав отчет в current-task.md». Разрешён один повтор того же proof-кандидата
после исправления evidence, timeout1000/envelope1060, отдельный новый счёт без
возобновления R11/переноса retired576. Новая phase `MERGE-R11-EVIDENCE-RETRY-2026-10-21`, T0 `09:02:57Z`, main
`09:32:57Z`, absolute `09:47:57Z`; fresh ceiling1060, max1 Build.
[Новый счёт](cloud-build/origin-layout/R11-RETRY-BUDGET-20261021.json),
[inputs](cloud-build/origin-layout/R11-RETRY-INPUTS-20261021.json).
Регистрация прошла независимый Luna HIGH review GO; 7 новых phase tests,
реальная локальная упаковка и полный static source/patch/pin/recipe preflight PASS.
Перед dispatch оба SHA будут привязаны к одному опубликованному reviewed commit
в новом live ledger под coordinator lock. Build ещё не отправлен.
Новые proof-гипотезы и семантические изменения в повтор не входят.
Исходные tmp debt/CURRENT/F/thread/array/R9 returning hook и narrow R8 premise
сохранены; StorageDead/invariant/resource checks не ослаблены. Address-taking и
source-named unit empirical negatives остаются OPEN/NOT_RUN; прежняя полная
матрица, prefix/physical BeforeLive и normal/unwind exits — отдельные gates.

[Итог](cloud-build/origin-layout/R11-FINAL-RESULT-20261021.json),
[release](cloud-build/origin-layout/R11-RELEASE-20261021.json),
[coverage](cloud-build/origin-layout/R11-OBLIGATIONS-20261021.md),
[Reader](cloud-build/origin-layout/R11-READER-COVERAGE-20261021.md).
Final ledger/docs checkpoint не является новым proof Build; immutable built inputs
сохранены в source0ab7fcab:R11-INPUTS. R10/historical accounts и чужие dirty files не менялись.
