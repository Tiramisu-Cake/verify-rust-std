# Merge / insert_tail — самостоятельная proof-сессия R8

## Задание и авторизация

- **ID:** `merge-late-recovery-rejoin-autonomous-2026-10-20-r8`; **статус:** READY, T0 ещё не задан.
- **Owner:** `merge`; **репозиторий:** `Tiramisu-Cake/verify-rust-std`.
- **Project worktree:** `/root/verify-rust-std-merge-origin`; **branch:** `merge/incoming-origin-20261009`.
- **Tool worktree:** `/root/verifast-merge-actual-glue`; **branch:** `merge/actual-glue-instance-20261011`; текущий head **`47b80fadab18df5819faefa8fbd759a95cac7801`**.
- **Новое окно:** 120 минут основной работы от фактического старта R8 + до30 минут завершения. После main новых Builds/retries/гипотез нет.
- **Новый бюджет:** **3600 Cloud-секунд**, начальный used=0. Число последовательных Builds отдельно не ограничено; действуют сроки, бюджет, slots и review.
- **Lane:** `merge`; существующий coordinator и стабильный owner.
- **Новая phase:** `MERGE-LATE-RECOVERY-REJOIN-R8-2026-10-20`; отдельный ledger `cloud-build/origin-layout/CURRENT-RECOVERY-R8-BUDGET-20261020.json`.

**Это поручение явно разрешает R8, её бюджет и Builds после обычных gates.** Сам подготовь согласованную branch-local authorization/phase/profile/entry/runner/recipe регистрацию и dependent pins существующей lane. Отдельное согласование очередного Build, implementation blocker, experimental profile или tool SHA в пределах миссии не нужно. T0/deadlines, source applicability, независимый review актуальных изменений, точные опубликованные inputs и admission coordinator обязательны. Отказы не обходить.

Ты начинаешь без контекста. Проверь оба worktree/branch/HEAD и dirty diff, сохрани чужие изменения. Прочитай `AGENTS.md`, текущую часть [STATUS](STATUS.md), [полномочия](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), релевантные [WORK-POLICY](WORK-POLICY.md), [Cloud runbook](cloud-build/README.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md) и нужную часть [плана](COMPLETION-PLAN.md). Историю целиком и большие evidence JSON не перечитывай.

## Исходная точка и ближайшая цель

Checkpoint R7: **`03f7144b5bcf6224da7cf74fcacaeba557ae7fa6`**. R7 CLOSED_PARTIAL: семь terminal FAILURE Builds, **3384/3600 charged, 3380 execution, 216 retired, carry=false**, own active/unresolved/requests/reservations0 на closeout. Старый счёт/окно не возобновлять; 216 секунд не переносить. [Архив задания/отчёта R7](task-history/merge-post-migration-current-recovery-autonomous-2026-10-20-r7.md), [итог](cloud-build/origin-layout/R7-FINAL-RESULT-20261020.json), [обязательства](cloud-build/origin-layout/R7-OBLIGATIONS-20261020.md).

**Proof до R8:** полный CURRENT normal/unwind, original guard/Drop, whole insert_tail/B2 и qualification OPEN; independent credit0. Empty-tail helper проверялся отдельно. Последний actual proof: source **`637cdf45e2a17814d5b6d2abadc5d572534f42ad`**, tool **`2883dbf5502512dc800f70e8496d674e44bba644`**, profile SHA **`96a0f198e6a5a0662a345bc42615a19d40aa753454a360197bbaa14d6eb0d384`**, Build **`6019f7c5-1c0a-44a8-87be-3513797fe416`**. На наблюдаемом пути выполнены late FnMut, half-token close, strict scope exit/full token, lifetime end, оба точных scaled borrow-end/open и readonly-end; затем unsupported `merge_fractions *sift |-> _` на verified313. Это не доказательство обоих путей или полного CURRENT. [Build6](cloud-build/origin-layout/R7-BUILD6-RESULT-20261020.json), [recovery observation](cloud-build/origin-layout/R7-BUILD6-RECOVERY-OBSERVATION-20261020.json).

**Готовый следующий кандидат:** project **`c1fff41b7dca14f240e0917a95052ee79fc474a5`**, tool **`47b80fadab18df5819faefa8fbd759a95cac7801`**, profile `experimental-merge-late-callback-recovery-r7-v1`, SHA **`e5ed4de577fe682d748f4f6af4aab4af54ef36e77a19ccfeddc08a1ce9aae6aa`**. Узкая замена на `merge_fractions points_to::<u64>(sift, _);` и exact translator matcher; checked physical assertion/singleton close сохранены. Есть независимый Luna HIGH GO, static17patch/18base и isolated checks; **actual compile/proof не подтверждены**. Последний Build **`55195571-1b4b-4c01-99b8-d613ec137594`**: compile-only exit124, source proof_attempted=false, candidate-stage exits null. Console helper exit0 не подтверждает сборку этого кандидата; причинность отказа неизвестна. [Review](cloud-build/origin-layout/R7-CANDIDATE7-REVIEW-20261020.md), [release/pins](cloud-build/origin-layout/R7-RELEASE-20261020.json), [Build7](cloud-build/origin-layout/R7-BUILD7-RESULT-20261020.json).

Миссия — actual insert_tail, CopyOnDrop guard и CURRENT-ресурсы на normal/unwind, затем merge/caller interfaces. Ближайшая полезная proof-цель: **actual physical fraction merge и singleton rejoin после late callback**, далее original guard loan/Drop и полные CURRENT posts. Сам выбери достижимый этап и короткий backlog по плану, уточняй их по Evidence. Не ограничивай сессию одной починкой сборки; обслуживание и proof-прирост учитывай отдельно.

## Предлагаемый первый цикл и самостоятельное продолжение

1. До повторного исполнения уточни ровно недостающее по compile-only124: existing source timeout/stage wiring и targeted v0.11 observations Build7. Уже сохранены [compile end](cloud-build/origin-layout/R7-BUILD7-COMPILE-END-OBSERVATION-20261020.json) и [candidate stages](cloud-build/origin-layout/R7-BUILD7-CANDIDATE-STAGES-OBSERVATION-20261020.json). Сформулируй проверяемую гипотезу и выбери согласованные внутренние compile/work deadlines в бюджете существующей lane; exit124 сам по себе не устанавливает причину. Старый WITHHELD/инструкция v0.8 внутри Brief не текущий запрет уточнения; $HOME warnings не установленная причина. Новый Build лишь ради чтения не нужен.
2. Подготовь новую R8 регистрацию со всеми consumers/pins, сохрани strict source/phase/profile/environment/entry/adapter/core bindings. R7 release/ledger не менять. Exact17patch/18base composition — сохранённая исходная provenance, не запрет следующих необходимых reviewed исправлений. Review нового diff/dependencies обязателен; полный review неизменённых частей не повторять.
3. Через existing Cloud preflight установи сборку точного кандидата → actual targeted resource proof → dependent controls. Предпочитай stages одного Build; отдельный compile-only/reproducer допустим при различающей гипотезе и экономии. Compiler success имеет нулевой proof credit. На VPS actual preparation/compiler/proof не выполнять.
4. Проверь physical merge/rejoin: точные provenance, coefficients, referent и CURRENT value; полный token до смерти lifetime; точные scaled FBC/borrow-end/open и end_ref_readonly. Сохрани порядок обязательных recovery-операций (в текущем кандидате13commands) и отдельный original guard readonly debt/tmp fractions. Normal Continue — recovery до следующего shift, normal break — до guard Drop, unwind — до original Cleanup Drop. FnMut возвращает CURRENT F/thread, а не автоматически Args/end tokens. Не подставляй entry snapshot, purity/no-panic/static lifetime или assumed bridge.
5. После target пройди применимые исходные groups/negatives и собственные receipts на совместимых финальных source/tool/profile identities. Зафиксируй branch-specific outcomes и remaining gate; старые source PASS не переносить в квалификацию нового профиля. При новом blocker сам исправляй связанный класс ошибок, получай review и продолжай в окне/бюджете.

Повторять неизменённый отказ нельзя. После повторяющихся setup failures сначала разбери минимальный reproducer, альтернативный интерфейс и пригодность gate. Если основной путь упёрся в настоящую границу, проверь независимые задачи своей миссии: exact prefix coercion/borrow bridge, addressability admission/receipt, остальные обязательства плана.

## Сохраняемые controls и полномочия

Исходная матрица: 4 resource-loss; HRTB/Output/projection/binder/lifetime; official first-unwind mutant; late-Cleanup refusal; 5 CURRENT18 negatives; B1/helper/ordinary normal-unwind/generated Drop/default-off/receiver/end/retirement; addressability, actual prefix/fullbody и полные CURRENT posts. Сохрани empty-tail positive/три intended rejections и late-admission controls, exact source/stage/target binding. Prerequisite skip, lexical/setup rejection и no-match не intended negative PASS. Bounds/alignment не устанавливают allocation disjointness; все исходные operational geometry/Drop checks сохраняются.

BeforeLive остаётся INCONCLUSIVE: unbound local вместо требуемого физического heap refusal. LocalAddrTaken — prepass flag, не owner/liveness; отдельный Rocq allocation consumer игнорирует StorageLive/Dead. Не выводи Rocq/owner credit и не вводи новую storage/memory model. Prefix false/true/first-Continue-panic допускаются по [exact design](cloud-build/origin-layout/R4-PREFIX-NEXT-DESIGN-20261020.md): точный compiler Unsize subtype/metadata, body/span/assignment-bound lifetime, same-element array3/u64→slice length3/data/provenance и checked loan return. Blanket PointerCoercion/static lifetime fallback не подходят.

Разрешены свои annotations/specs/леммы/resources, inventory/parser/binder/source-binding/нормализация, необходимые exporter/schema/decoder/translator/frontend/lowering и минимальные runner/preflight/diagnostic fixes, сохраняющие source semantics и действующую модель. Сам выпускай experimental profiles/tool commits/patches и dependent pins/closure. Tool patches/Git objects публикуй в назначенной project branch; отсутствие отдельного tool remote не блокирует работу. Maintainer принимает готовые патчи, а не новый proof-blocker вместо тебя.

До содержательного изменения зафиксируй defect/source applicability/rationale/сохраняемые ресурсы и различающие controls. До submit — независимый **GPT-6 Luna HIGH** review актуального diff/dependencies: `model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации и дорогой автоматической замены. Устрани конкретные soundness-возражения; synthetic/static GO не actual proof. Для изменённого runner обязательны isolated service error-path checks с сохранением partial/NOT_RUN/errors и existing Cloud preflight.

Сохраняй runtime std/алгоритмы/generic signatures, compiler/toolchain baseline, actual CFG/domain/normal-unwind-abort posts, CURRENT ownership/provenance/admission и formal acceptance. Нельзя добавлять axioms/assumed bridges, выводить ресурс из numeric address equality, отключать checks или вводить новую memory/alias/layout model. Настоящее новое trust-допущение вынеси с точным вопросом; обычный checked proof/исправление представления нового согласования не требуют. Чужие worktrees/pins и historical evidence/ledgers не менять. Без reset/force-push/merge/upstream PR/внешних комментариев, Actions, shared coordinator/IAM/triggers/dependencies/cache/backend deployment.

## Время, исполнение и отчёт

T0 зафиксируй **при фактическом старте R8 после прочтения задания**; main=T0+120 минут, absolute=T0+150 минут. Новый ledger с explicit authorization и ceiling3600; старые остатки не переносить. Timeout≤900с; envelope timeout+60 помещается в remaining budget и действующее окно с запасом до absolute. Один occupied/unresolved Build на owner/ledger, максимум три project-wide. Только exact committed/published closure с проверенным полным remote SHA. Uncertain submit не дублировать; отказы coordinator не обходить.

Ожидание делай экономным: status/Brief по возможности yield10–30с вместо1000мс с отдельным модельным возвратом за session ID. Выполняй независимую полезную работу; при простом ожидании объединяй ожидание и проверку в одном инструментальном шаге≤60с. Не создавай отдельные циклы sleep30→status→чтение ответа без новой информации. Штатные status/accounting controls и общение с владельцем сохраняй.

Примерно через час сообщи progress/charge/blocker без ожидания ответа. Продолжай, пока есть полезный шаг, время и бюджет; после первой исправленной ошибки не останавливайся. Ранний stop обоснуй после проверки независимых задач. После main никаких новых Builds/retries/гипотез; свои неотправленные requests отозвать. Дополнительные30 минут — уже начатое, Evidence, учёт, checkpoint/push. К absolute подтверди terminal/accounting либо явно оставшиеся active/unresolved с ID и разрешённым действием. Финальный остаток retire без carry.

Evidence: `smallsort-brief BUILD_UUID` → catalogue/file ID → **`--refresh --file ID --expect-sha256 SHA`** с info/locate/position/lines/JSON pointer и нужными явными страницами по серверным next_offset/next_value_start. [Guide](EVIDENCE-READER-GUIDE.md), [примеры](EVIDENCE-READER-TASK-QUERIES.md), корневой `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md`. Lifetime16/WITHHELD устарели. Проверяй file/index/archive/request identities, coordinates/exact/complete/coverage. Evidence — данные, не команды. No-match не NOT_RUN, source PASS/exit0/integrity не independent credit, file coordinates не AST/MIR/parser-input binding или причинность. Raw/full logs/archives/Cloud Logging/локальные raw copies и GCS/download/storage/logging обход запрещены; при реальном ограничении v0.11 сообщи точные недостающие данные, admin audit отдельно. download_verified и historical verdicts не менять.

VPS — Git/hashes/static parsing и малые isolated synthetic service tests; actual preparation/extraction/compiler/decoder/refiner/verifier/full runners только Cloud. Обновляй компактный STATUS и существующие semantic/session/release/coverage/experiment records. Здесь оставь **один перезаписываемый компактный отчёт**: цель; proof до→после; обслуживание отдельно; каждый Build/гипотеза/type/candidate/результат/charge; T0/deadlines/end; own active/unresolved/requests/reservations; закрытие бюджета без carry; следующий blocker. Большую матрицу/provenance храни отдельно по ссылкам. Wall-clock не active agent time; резерв/retired headroom не расход.

## Отчёт агента

R8 ACTIVE. T0/main/absolute UTC2026-10-20 17:11:30/19:11:30/19:41:30.
Цель: actual physical fraction merge/singleton rejoin → original guard/CURRENT.
Proof до→после: Build2 trace проходит physical merge/full sift assertion/singleton
close. Build4 с отдельно разрешённым experimental allocation profile проходит
прежний guard numeric-span/Drop barrier до final Freeing locals318, где отсутствует
[1/2]points_to(tmp_addr,_). Полные normal Continue/break/unwind, CURRENT, B2 и
qualification OPEN, independent credit0. Native receipt связывает tmp с CURRENT
begin/count2, не автоматически с полным entry range3.
Обслуживание отдельно: compiler preflight PASS; exact primitive-u64 matcher;
изолированные flags probes. Freshness8controls INCONCLUSIVE: wholearray3 refiner1
(RawPtr unsupported), verifier0 не засчитан. Candidate5 заменяет адресный оператор
в controls и добавляет обычное checked post-Drop readonly recovery, без tool change.
Новый profile остаётся отдельно OPEN; prefix/BeforeLive OPEN.

| Build | Hypothesis/type | Candidate | Result | Charged |
| --- | --- | --- | --- | --- |
| 4952f684 | full900 vs short203 wrapper; target/matrix | 5967687f/tool47b80fad/profilee5ed4de5 | compilerPASS, matcher313 reject before resource proof | 631 |
| eaf02609 | exact u64 Manifest matcher; target/matrix | 1651614a/tool43c1fdc2/profile845ea5a5 | physical rejoin observed, guard numeric-span refusal101 | 538 |
| 80c749f2 | unchanged-model geometry probes | 5a78c5b7/tool43c1fdc2/profile845ea5a5 | INC inherited actual-only refiner flag; isolated copies fixed | 592 |
| df53281d | reviewed allocation premise + corrected probes + target/matrix | c274d0f2/toolf2e92cec/profile838ade99 | compilerPASS; original Drop passes observed path; final tmp-half missing318; controlsINC | 404 |

Всего2755charged/2752execution из3600;845remaining. Own active/unresolved0. Build5 c2434c1b: compilerPASS, fullbodysetup anchor rejection;590charged.
Candidate6 exact-wrapper anchor independently reviewed; checked commands unchanged.
Последний submit планируется timeout780/envelope840 в остатке845. Окно прежнее.
[Карточка](cloud-build/origin-layout/R8-SESSION-20261020.md),
[обязательства](cloud-build/origin-layout/R8-OBLIGATIONS-20261020.md),
[Build4](cloud-build/origin-layout/R8-BUILD4-RESULT-20261020.json),
[граница модели](cloud-build/origin-layout/R8-GEOMETRY-BOUNDARY-20261020.md).
