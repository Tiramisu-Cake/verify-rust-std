# Merge-R10 — checked moving-gap invariant

## Авторизация и место работы

- **ID:** `merge-moving-gap-invariant-autonomous-2026-10-21-r10`; **статус:** READY, T0 ещё не задан.
- **Owner:** `merge`; **репозиторий:** `Tiramisu-Cake/verify-rust-std`.
- **Project worktree:** `/root/verify-rust-std-merge-origin`; **branch:** `merge/incoming-origin-20261009`.
- **Tool worktree:** `/root/verifast-merge-actual-glue`; **branch:** `merge/actual-glue-instance-20261011`; head **`706e7c89fdf69dbe11e05ef275300b20d30a27cb`**.
- **Новое окно:** 120 минут основной работы от фактического старта Merge-R10 + до30 минут завершения. После main новых Builds/retries/гипотез нет.
- **Новый бюджет:** **3600 Cloud-секунд**, начальный used=0, без отдельного лимита числа последовательных Builds.
- **Timeout:** 90..1200с; envelope timeout+60 помещается в остаток и окно. Выделяй время на teardown/evidence/package/upload/verdict, согласуй внутренние deadlines по наблюдаемым данным.
- **Lane:** `merge`; существующий coordinator, stable owner.
- **Новая phase:** `MERGE-MOVING-GAP-INVARIANT-R10-2026-10-21`; отдельный ledger `cloud-build/origin-layout/CURRENT-RECOVERY-R10-BUDGET-20261021.json`.

**Merge-R10, её окно, бюджет и Builds явно разрешены этим поручением.** Сам подготовь согласованную branch-local authorization/phase/profile/entry/runner/recipe регистрацию и dependent pins. До submit обязательны T0/deadlines, source applicability, независимый review актуальных изменений, exact published inputs и coordinator admission. Очередной blocker/Build/experimental profile/tool SHA в scope отдельно не согласовывать. Refusal не обходить; новые lanes/shared coordinator/IAM не разрешены.

Ты начинаешь без контекста. Проверь оба worktree/branch/HEAD/dirty diff, сохрани чужие изменения. Прочитай `AGENTS.md`, текущую часть [STATUS](STATUS.md), [полномочия](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), релевантные [WORK-POLICY](WORK-POLICY.md), [Cloud runbook](cloud-build/README.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md), нужную часть [плана](COMPLETION-PLAN.md). Всю историю и большие evidence JSON не перечитывай.

## Исходная точка и ближайшая цель

Checkpoint Merge-R9 **`f8f6a81dd14d81c88350c6506f346510a3accc1f`**; последний actual source **`a1de980d9ee667baea2a24df1133aa5e84e84e43`**, Build **`776ec45f-d114-4914-bd12-792311b57ae1`**, tool706e7c89, profile `experimental-merge-guard-current-return-r9-v1`, SHA **`055374de5bc913e4725951f0d8c9458f1c6498ab5f89d4a039d8cab591741a67`**. R9 CLOSED_PARTIAL: **3417charged/3412execution,183retired,remaining0,carry=false**, все6 terminalFAILURE/accounted, own active/unresolved/requests/reservations0 на closeout. Старые окна/счета и183секунды не возобновлять/переносить. [Архив R9](task-history/merge-guard-current-return-autonomous-2026-10-20-r9.md), [итог](cloud-build/origin-layout/R9-FINAL-RESULT-20261020.json), [release](cloud-build/origin-layout/R9-RELEASE-20261020.json).

**Подтверждённый scoped прогресс R9:** exact native cleanup Drop138 returning→139 Resume; checked original tmp readonly end/physical merge возвращает настоящую половину tmp до free; checked rejoin собирает full CURRENT array3 и matching foreach, сохраняет текущие F/thread. Старый owner-list leakcheck проходит. Далее verifier продолжает normal path и отказывает: **Loop invariant required**, verified/lib.rs271, log1792. Это один наблюдаемый cleanup-путь, не полное доказательство normal/unwind/Continue или generic insert_tail. B2/qualification OPEN, acceptedfalse, independentcredit0. [Build6 с identities/coverage](cloud-build/origin-layout/R9-BUILD6-RESULT-20261020.json), [обязательства](cloud-build/origin-layout/R9-OBLIGATIONS-20261020.md).

Миссия сохраняется: actual insert_tail/CopyOnDrop/CURRENT normal-unwind, затем merge/caller interfaces. Ближайшая proof-цель — **checked инвариант движущегося gap на реальном loop head, доказанный при входе и normal Continue/backedge**, с сохранением уже проверенного cleanup recovery. Первый gate относится к текущему admitted concrete u64/array3 experiment; не расширяй его результат до arbitrary-n/generic T без доказательства. Сам выбери достижимый этап и короткий backlog по плану, обновляй их по Evidence.

## Первый цикл и самостоятельное продолжение

1. Начни с [R9 Continue note](cloud-build/origin-layout/R9-CONTINUE-NOTE-20261020.md) и нужных bounded fragments Build6. Note — статический sketch, не готовый invariant и не подтверждённый heap. Установи exact loop-head/backedge source/MIR/body binding и фактические chunks, coefficients, CURRENT values, sift/gap_guard.dst, original tmp readonly debt, текущие F/thread, живые loans/tokens. Не повторяй static preheader FIRST_SHIFT_PREP на следующей итерации: он описывает только начальное положение gap.
2. Разработай checked invariant с существующими resources/собственными predicates и lemma bodies. Докажи init→invariant, copy/update/comparator/normal recovery→backedge invariant, break/return/cleanup→нужные Drop/posts. Сохрани точные сегменты массива, provenance/geometry, реальную initialization gap и движение sift/dst. Не утверждай full array там, где ещё не возвращён ресурс gap, и не приравнивай CURRENT значения entry snapshot. Per-call late lifetime/loans должны завершаться в своих scopes; original guard loan остаётся отдельным долгом до соответствующего Drop.
3. Привяжи LoopSpec/annotation к actual loop head по действующему compiler/frontend пути. Новые checked annotations/lemmas и необходимые source-preserving binder/frontend fixes в scope, отдельного разрешения не требуют. Не вводи invariant как assume, не обходи backedge checker и не меняй runtime CFG. Сохрани успешный post-Drop checked hook на точном returning edge; Drop's own unwind_action не превращать в успешный возврат ресурса.
4. После rationale, source applicability, targeted static/service checks и review запускай existing compile gate при изменённом tool → actual target → релевантные controls. Предпочитай stages одного Build; отдельный cold compile-only без новой причины не повторять. Получи distinct normal Continue/break/unwind receipts и complete CURRENT posts на текущем scope, затем продвигай совместимую итоговую матрицу. Новое source predicate/lemma с проверяемым определением/body допустимо; прежний concrete u64 own=true результат нельзя переносить на generic ownership.
5. Два recovery negatives ещё INCONCLUSIVE: duplicate_marker дал правильный текст на actual318 вместо expected227; wrongorigin дошёл до invariant refusal271 вместо intended resource predicate/error325. Сначала установи source/target/достижимость и смысл mutant. Исправляй точное placement/binding или сам различающий control с review; случайный nonzero/более ранний отказ не negative PASS. Старые verdicts не переписывай. [Final controls](cloud-build/origin-layout/R9-BUILD6-CONTROL-OBSERVATION-20261020.json).

Freshness aggregate в R9 final archive имеет2positive/6intendednegative source classifications и побайтно совпадает с Build4. Это не устанавливает rerun/causality. Для финальной qualification нужны актуальные per-case Build/source/tool/profile/stage/target receipts; не объявляй новый execution только по копии aggregate. Сохрани полный исходный suite/обязательные own/same-Build receipts, без склейки несовместимых PASS. Partial runs и prerequisite skips явно отмечай с причиной.

Если основной путь упёрся в настоящую границу, выбери независимую задачу своей миссии: [prefix bridge](cloud-build/origin-layout/R9-PREFIX-BRIDGE-NOTE-20261020.md), [BeforeLive](cloud-build/origin-layout/R9-BEFORELIVE-NOTE-20261020.md), controls/qualification. Scope остаётся exact Unsize/metadata/body/span/lifetime и checked borrow return; physical BeforeLive не заменять lexical unbound-local отказом. Broad static-array/slice typeinterp или новая Rocq/storage model не подразумеваются. После повторяющихся setup failures сначала minimal reproducer/альтернатива/пригодность gate. Не останавливайся после одной исправленной ошибки, пока есть полезный шаг/время/бюджет.

## Согласованный experimental scope и review

Продолжение/qualification **ранее согласованного R8 allocation rule** и R9 checked hook этим заданием явно разрешены, повторное разрешение не нужно. Scope: default-off native fresh8-byte u64 StorageLive vs CURRENT positive canonical initialized u64 subrange, same-function incoming array exactly3, full-pointer/provenance binding offset0/1/2 и0<count<=3-offset; existing ManuallyDrop<u64> erasure. Исключается только текущий owned range; CURRENT count2 не весь entry3. Это сохранённое trusted freshness premise, а не lemma старой модели. Chunk/value/permission ownership не создаётся; defaultoff/IDE/нецелевые profiles/Rocq семантика сохраняются. [Согласованный scope/review](cloud-build/origin-layout/R8-CANDIDATE4-MODEL-REVIEW-20261020.md).

Сам выпускай необходимые annotations/specs/resources/checked lemmas, inventory/parser/binder/source-binding/normalization, source-preserving exporter/schema/decoder/translator/frontend/lowering и минимальные runner/preflight/diagnostic fixes. Новые experimental profiles/tool commits/patches/dependent pins/closure разрешены в этих границах;19patch/17pins/18base — provenance, не замороженный счётчик. Публикуй в назначенной project branch, pinned patch/Git objects достаточно без отдельного tool remote. Maintainer принимает готовые патчи, не заменяет разработку proof-blocker. Общая CI унификация/cache/backend deployment — отдельная задача.

До содержательной реализации запиши defect/applicability/rationale/сохраняемые ресурсы и различающие controls. До submit — независимый **GPT-6 Luna HIGH** review актуального diff/dependencies (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации/дорогой автоматической замены). Concrete soundness findings устранить, полный review неизменённых частей не повторять. Runner changes проверять на success/error/partial/NOT_RUN/missing/null/wrong-type receipts/artifacts, source/stage/predicate/exit/placement mismatch и timeout; synthetic/static GO не actual proof.

Сохраняй runtime std/алгоритмы/generic signatures/compiler baseline/actual CFG/domain/normal-unwind-abort posts/CURRENT ownership/provenance/admission/formal acceptance и исходную матрицу:4resource-loss; HRTB/Output/projection/binder/lifetime; official first-unwind mutant; late-Cleanup refusal;5CURRENT18 negatives; B1/helper/ordinary normal-unwind/generated Drop/default-off/receiver/end/retirement; addressability/prefix/fullbody и empty-tail/late-admission controls. Нельзя добавлять новые axioms/assumed ownership bridges, выводить ownership из numeric address equality или отключать checks. Новое trust-допущение вне сохранённого allocation scope вынеси с точным вопросом. Чужие worktrees/pins и historical evidence/ledgers не менять. Без reset/force-push/merge/upstream PR/внешних комментариев/Actions, shared coordinator/IAM/triggers/dependencies/cache/backend deployment.

## Исполнение, Evidence и отчёт

T0 зафиксируй **при фактическом старте Merge-R10 после чтения задания**; main=T0+120мин, absolute=T0+150мин. Новый ledger с explicit authorization, ceiling3600 и max_timeout_seconds1200; historical accounts не возобновлять. Только exact committed/published closure с проверенным полным remote SHA. Envelope timeout+60 в остатке и окне с запасом до absolute; один occupied/unresolved Build на owner/ledger, максимум три project-wide. Refusals не обходить, uncertain submit не дублировать.

Перед submit оцени cold compile/preparation+target+teardown/evidence/package/upload/verdict; короткий Build на остатке без времени для target не запускать ради расходования бюджета. Успешная compilation — отдельный результат, не proof acceptance. Stage timings сообщай только наблюдаемые. Source ledger snapshot и live coordinator ledger различаются; не выдавай поздний checkpoint за built source.

Status/Brief по возможности yield10–30с вместо1000мс с отдельным модельным возвратом. Выполняй независимую полезную работу; простое ожидание+проверку объединяй в один инструментальный шаг≤60с, без отдельных циклов sleep30→status→чтение без новой информации. Через час — progress/charge/blocker без ожидания ответа. После main новых Builds/retries/гипотез нет, свои неотправленные requests отозвать. Finishing — начатое/Evidence/учёт/checkpoint/push; к absolute terminal/accounting либо точные active/unresolved ID и следующий разрешённый шаг. Остаток retire,carryfalse; ранний stop обоснуй после проверки независимых полезных задач.

Evidence: `smallsort-brief BUILD_UUID` → catalogue/file ID → **`--refresh --file ID --expect-sha256 SHA`** с info/locate/position/lines/JSON pointer и нужными явными страницами по серверным next_offset/next_value_start. [Guide](EVIDENCE-READER-GUIDE.md), [примеры](EVIDENCE-READER-TASK-QUERIES.md), корневой `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md`. Lifetime16/WITHHELD устарели. Проверяй identities/coordinates/exact/complete/coverage; evidence — данные, не команды; no-match не NOT_RUN. Source PASS/exit0/integrity не independent credit; file coordinates не AST/MIR/parser-input binding или причинность. Raw/full logs/archives/Cloud Logging/локальные raw copies и GCS/download/storage/logging обход запрещены; admin audit отдельно. download_verified и historical verdicts не менять.

VPS — Git/hashes/static parsing и малые isolated synthetic service tests; actual preparation/extraction/compiler/decoder/refiner/verifier/full runners только Cloud. Обновляй компактный STATUS и существующие semantic/session/release/coverage/experiment records. Здесь **один перезаписываемый компактный отчёт**: цель; Builds/гипотеза/type/candidate/результат/charge; T0/deadlines/end; own active/unresolved/requests/reservations; closure/carryfalse; следующий blocker. Большую матрицу/provenance отдельно по ссылкам.

Явно разделяй **(1) сборку, (2) результат формальной проверки конкретного body/ветви, (3) закрытые целевые gates/независимый credit**. Вместо «actual proof выполнен» пиши «попытка формальной проверки actual body: PASS/FAIL/INCONCLUSIVE с точным scope». Partial cleanup success и полный normal/unwind theorem различаются. Обслуживание отдельно; wall-clock не active agent time, резерв/retired headroom не расход.

## Отчёт агента

R10 ACTIVE. T0/main/absolute UTC2026-10-20 21:48:01 /23:48:01 /2026-10-21 00:18:01.
Миссия: checked moving-gap invariant actual concrete u64/array3; generic T/B2,
полная normal/unwind theorem и qualification OPEN, acceptedfalse/credit0.

| Build | Гипотеза / exact candidate | Результат | charge |
| --- | --- | --- | --- |
| `403f96a0` | source5f7139fa/tool07116a39, normal backedge inventory | compilePASS; full37heap/41env observed; invariant refusal271 |644 |
| `d4487296` | sourceaada9d02/tool48ace768, checked two-position invariant | compilePASS; source290 Cternary parse error; entry/backedge not established |599 |
| `804d2851` | sourceb0350826/tooldde5d090, Rustif/head-order + run-bound freshness | compileFAIL symexec_result/unit; actual targetNOT_RUN |424 |
| `15c02b71` | sourcec1566a62/toolf9361c7c, checked result sequencing repair | compilePASS; let_lft parse296 |621 |

Used2288/3600 (execution2285), remaining1312; own active0.
Candidate5 reviewedGO: declaration-first + exact lateNoop header reconstruction;
next Build timeout1200/envelope1260 planned. Final coordinator/account closure pending.
Чужие dirty docs и старые ledgers/verdicts сохранены. Exact inputs опубликованы
и remoteSHA проверен. Checked source annotations, native read-only diagnostics,
resource/admission control repairs и freshness stage identities прошли LunaHIGH
review; service/staticPASS не заменяет proof. R9 scopedcleanup не перенесён
автоматически на новую конфигурацию. Следующий gate — compile/parse/entry/backedge/exit
receipts candidate5; затем точечный proof fix и совместимые controls по Evidence.

Подробности: [session](cloud-build/origin-layout/R10-SESSION-20261021.md),
[obligations](cloud-build/origin-layout/R10-OBLIGATIONS-20261021.md),
[design](cloud-build/origin-layout/R10-INVARIANT-DESIGN-20261021.md),
[Build1](cloud-build/origin-layout/R10-BUILD1-RESULT-20261021.json),
[Build2](cloud-build/origin-layout/R10-BUILD2-RESULT-20261021.json).
