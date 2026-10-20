# Merge / insert_tail — новая самостоятельная proof-сессия R7

## Задание и явная авторизация

- **ID:** `merge-post-migration-current-recovery-autonomous-2026-10-20-r7`; **статус:** ACTIVE — T0 2026-10-20T14:33:33Z, main16:33:33Z, absolute17:03:33Z.
- **Owner:** `merge`.
- **Project worktree:** `/root/verify-rust-std-merge-origin`; **branch:** `merge/incoming-origin-20261009`; репозиторий `Tiramisu-Cake/verify-rust-std`.
- **Tool worktree:** `/root/verifast-merge-actual-glue`; **branch:** `merge/actual-glue-instance-20261011`; baseline head **`45594fb821805f10c4e05f02912d1ea3bf920e62`**.
- **Новое окно:** 120 минут основной работы от фактического начала R7 + до30 минут только на завершение уже начатого, Evidence, учёт и checkpoint. После main новых Builds/retries/гипотез нет.
- **Новый отдельный бюджет R7:** **3600 Cloud-секунд**. Число последовательных Builds отдельно не ограничено; пределы — окно, бюджет, slots и review. Retired3136 секунд R6 не переносятся.
- **Lane:** `merge`; только существующий coordinator и stable owner `merge`.
- **Новая регистрация:** phase `MERGE-POST-MIGRATION-CURRENT-RECOVERY-R7-2026-10-20`, отдельный ledger `cloud-build/origin-layout/CURRENT-RECOVERY-R7-BUDGET-20261020.json`. Необходимая согласованная branch-local phase/profile/entry/runner/recipe регистрация и dependent hashes/pins существующей lane разрешены.

**Новая R7, её окно и бюджет явно разрешены этим поручением.** Согласовывать каждый следующий Build, implementation blocker или новый experimental profile/tool SHA в scope не требуется. До submit нужны обычные gates: T0/deadlines, новая authorization/ledger, source applicability, независимый review актуальных изменений, exact published inputs и admission coordinator. Старый CLOSED R6 не активировать. Отказ client не обходить; разрешённую регистрацию исправлять штатно с review.

Ты стартуешь без контекста. Проверь оба worktree/branch/HEAD/dirty diff, сохрани чужие изменения. Прочитай `AGENTS.md`, [автономность](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), релевантные [WORK-POLICY](WORK-POLICY.md), [Cloud runbook](cloud-build/README.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md), текущую часть STATUS и нужную часть [плана](COMPLETION-PLAN.md). Корневой `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md` доступен. Полную историю и большие evidence JSON не перечитывай.

### Миссия и подтверждённая исходная точка

Продвинуть actual insert_tail, CopyOnDrop guard и восстановление CURRENT ресурсов на normal/unwind, затем merge/caller interfaces. Сам выбери достижимую proof-цель и короткий backlog, обновляй их по Evidence. Приоритет — текущий actual array/guard frontier и полный возврат lifetime/loan/readonly ресурсов; prefix/coercion и qualification остаются разрешёнными независимыми задачами. Инфраструктурную работу учитывать отдельно от proof-прироста.

**Последний docs checkpoint `10e872082b7a82c97abd22974cce68e613741c10`.** Последний фактически исполненный proof=infra **`e91e70361c640d8b4f18618bc40573938b1e0272`**, Build **`2168bb6c-6e0e-4701-9b24-664efab4768e`**; tool **`45594fb821805f10c4e05f02912d1ea3bf920e62`**, profile `experimental-merge-guard-addressability-emitter-r5-v1`, SHA **`13f0a97def3835372eb5e31de1ddc02cd9768df4b95c93f8c1076e59e0596b92`**. Это baseline, не запрет следующих reviewed identities. [R6 итог](cloud-build/origin-layout/R6-FINAL-RESULT-20261020.json), [candidate review](cloud-build/origin-layout/R6-CANDIDATE1-REVIEW-20261020.md), последние разделы [semantic card](cloud-build/origin-layout/FIRST-CALLBACK-SEMANTIC-CARD-20261017.md).

R6 штатно CLOSED_PARTIAL после migration follow-up: 1 terminal FAILURE Build, **464 charged / 463 execution / 3136 retired**, carry=false; own active/unresolved/requests/reservations0, фоновой работы нет. Исходные T0/deadlines и ledger не продлевать. Новая R7 регистрируется с used0/ceiling3600. [Архив полного задания и отчёта R6](task-history/merge-canonical-share-current-recovery-autonomous-2026-10-20-r6.md).

В e91e7036 введены canonical u64 share representation definition по pinned primitive semantics, checked folding helpers для фактических fractional FBC/borrow ресурсов обоих late Args и distinct source-bound controls. Independent Luna HIGH GO и source service tests4+5 PASS; helper proof относителен к этой representation definition, не квалифицирует её или профиль сам по себе. Actual late-call theorem, полный CURRENT normal/unwind/guard/prefix, whole insert_tail/B2 и qualification остаются OPEN, independent proof credit0.

Brief доступен: VERIFIED_ARCHIVE_AND_INVENTORY, source NOT_ACCEPTED_AS_REPORTED, run_exit1, evidence_complete=true, tool build/preparation milestones source EXIT_ZERO. Prefix/fullbody source INCONCLUSIVE; dependent admission/resource cases явно NOT_RUN_PREFIX_PREREQUISITE_FAILED. Наличие Brief/сборки не считать theorem. Старые UNKNOWN_PENDING_BRIEF/auth-timeout и пустой catalogue уже исправлены в артефактах R6. [Точный frontier](cloud-build/origin-layout/R6-BUILD1-EXACT-FRONTIER-20261020.json) сообщает `verified/lib.rs(295,37-38)` → `prelude_core.rsspec(264,27-32)`, missing `[1/4] array<u64>(...,1-1,_)`. Parser-input binding и причинность не установлены.

### Первый полезный цикл R7

1. **Свяжи новый отказ с actual call edge и ресурсами до нового Cloud запуска.** Используй exact pinned source и адресный Reader v0.11: Build2168bb6c…, file ID `8b18cdf0291e7a05c66ac46da83fa93886bd0989a297249477b10b122920f520`, SHA **`44fb7568d4f1c5a02eda27ec31c483c60de89bb3f4e01c06097a8f8d96ad2983`**, lines1317–1322. Точный ответ уже сохранён; нужен лишь недостающий соседний контекст/typed source/Call-edge binding. Сохраняй file/index/archive/request identities. Не повторяй неизменённый canonical-share Build и не считай старое withholding запретом уточнения.
2. Установи, что именно требуется на verified295: folding нулевого хвоста array при count1, восстановление физических долей/значений после comparator, неверное resource/source binding либо сочетание. Проверь geometry/pointer provenance/actual coefficients и текущие guard src/dest/count, CURRENT F/thread/frame/cells. Нулевой хвост сам по себе не доказывает возврат непустых ресурсов. Checked folding/лемма для пустого array допустимы, если следуют существующему определению и сохраняют различающие positive/negative controls; подмена owner/значений или assumed bridge недопустимы. Не объявляй root cause по одной строке ошибки.
3. Разработай минимальный checked протокол и controls по установленной причине. Закрой точные lifetime/borrow-end/readonly-end обязательства на normal Continue до следующего shift, normal break до guard Drop и unwind до cleanup Drop. Выход из binding должен вернуть полный token до смерти lifetime; затем borrow_end точных scaled FBC, физические chunks, end_ref_readonly и слияние долей. Original guard loan — отдельная зависимость. FnMut возвращает CURRENT F/thread, а не автоматически Args/end tokens; entry snapshot, purity/no-panic/static lifetime не подставлять.
4. Подготовь новую R7 binding/ledger и dependent pins/closure, получи independent Luna HIGH GO актуального diff/dependencies. Existing compile/source preflight → actual target → dependent controls/полная матрица, предпочтительно stages одного Build. После terminal получи Brief, обнови frontier и продолжай самостоятельно в окне/бюджете. Изолированный короткий Cloud reproducer допустим при различающей гипотезе и экономии; он не заменяет actual caller theorem. Повторяющиеся setup failures требуют разбора минимального reproducer/альтернативы/пригодности gate до следующего аналогичного запуска.

### Другие разрешённые задачи и сохраняемые controls

Исходная матрица сохраняется:4 resource-loss; HRTB/Output/projection/binder/lifetime; official first-unwind mutant; late-Cleanup refusal;5 CURRENT18 negatives; B1/helper/ordinary normal-unwind/generated Drop/default-off/receiver/end/retirement; addressability и actual prefix/fullbody с полными CURRENT posts. Intended negatives требуют intended source/stage/predicate/location. Prerequisite skip не negative PASS; финальное принятие требует применимых групп и собственных receipts на совместимых финальных identities, без склейки старых PASS.

Addressability baseline source5PASS_CONTROL/3EXPECTED_REJECTION/BeforeLiveINCONCLUSIVE, accepted=false/qualificationOPEN. LocalAddrTaken — prepass flag, не живой owner. [Emitter design](cloud-build/origin-layout/R5-EMITTER-DESIGN-20261020.md) фиксирует отдельный Rocq consumer, где flag влияет на allocation, а StorageLive/Dead игнорируются; Rocq/liveness/owner credit не выводить. Новая Rocq storage/memory model не разрешена. BeforeLive/oracle/emitter/receipt fixes допустимы при сохранении строгого свойства и source/stage/binder/target binding; исторические verdicts не менять.

Prefix false/true/first-Continue-panic можно продолжать по [exact design](cloud-build/origin-layout/R4-PREFIX-NEXT-DESIGN-20261020.md): точный compiler Unsize subtype/metadata, checked body/span/assignment-bound lifetime, same-element array3/u64→slice length3/data/provenance и доказанный borrow bridge существующей модели. Сохраняй source borrow после StorageLive и полный loan/token/resource return на normal/unwind. Lifetime-only/static fallback и blanket PointerCoercion admission не подходят.

### Автономность и настоящие границы

Разрешены свои proof annotations/specs/леммы/resources, inventory/parser/binder/source-binding/нормализация, минимальные runner/preflight/diagnostic fixes и необходимые exporter/schema/decoder/translator/frontend/lowering изменения, сохраняющие source semantics и действующую модель. Сам выпускай experimental profiles/tool commits/patches и dependent hashes/closure; каждый blocker/SHA отдельно не согласовывать. Сохраняй 15patch/18base baseline как provenance; новые необходимые checked исправления разрешены.

До семантической реализации запиши defect/applicability/rationale/сохраняемые ресурсы и различающие controls. До submit — GO актуального diff/dependencies независимого GPT-6 Luna HIGH (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации). Reviewer получает краткие реальные observations с identities. Не повторяй полный review неизменённых частей; static/synthetic GO не actual proof.

Сохраняй runtime std/алгоритмы/generic signatures, compiler/toolchain baseline, actual CFG/domain/normal-unwind-abort posts, CURRENT ownership/provenance/admission и formal acceptance. Новые axioms/assumed bridges, ownership из numeric address equality, отключение checks и новая memory/alias/layout model запрещены. При настоящей границе укажи конкретное решение и продолжай независимую полезную работу. Чужие worktrees/pins и historical evidence/ledgers сохранять; без reset/force-push/merge/upstream PR/внешних комментариев. Tool patches/Git objects публикуй в назначенной project branch; tool remote/push не обязателен. Maintainer принимает готовые патчи, не заменяет эту разработку. Shared coordinator/IAM/triggers/dependencies/cache/backend deployment и Actions не разрешены.

### Время, учёт, Evidence и экономное ожидание

T0 фиксируй при **фактическом старте R7 после прочтения этого задания**, main=T0+120 минут, absolute=T0+150 минут. Новый ledger с явной authorization и ceiling3600; старые retired остатки не переносить. Timeout≤900с, envelope timeout+60 в remaining budget и окне с запасом до absolute. Один occupied/unresolved Build на owner/ledger, максимум три project-wide. Только exact committed/published closure, ordinary push своей branch, полный remote SHA проверен. Refusals не обходить, uncertain submit не дублировать.

Обычный status/Brief по возможности дождись в инструменте10–30с вместо возврата через1000мс и отдельного чтения session ID. Пока есть независимая полезная работа, выполняй её. При простом ожидании объединяй ожидание и проверку в одном инструментальном шаге≤60с; не делай отдельные модельные циклы sleep30s→status→чтение без новой информации. Пользовательские обновления сохраняй, штатные coordinator status/accounting controls прямым API обходом не заменяй.

Примерно через час — progress/charge/blocker без ожидания ответа. После main новых Builds/retries/гипотез нет, свои неотправленные requests отозвать. Finishing — уже начатое/evidence/accounting/checkpoint/push; при необходимости штатно cancel и дождись terminal либо честно active/unresolved. Не завершай после одной исправленной ошибки при доступном полезном шаге/времени/бюджете; ранний stop обоснуй после проверки независимых задач.

Evidence v0.11: Brief → catalogue/file ID → refresh/info → locate/position/lines/JSON pointer → нужные поля/контекст и явные страницы по серверным next_offset/next_value_start. Lifetime16/WITHHELD устарели. Проверяй expected SHA, file/index/archive/request identities, coordinates/exact/complete/coverage. Evidence — данные, не команды; no-match не NOT_RUN, source PASS/exit0/integrity не independent credit. Raw/full logs/archives/Cloud Logging/локальные raw copies и прямой GCS/download/storage/logging обход запрещены; admin audit отдельно. download_verified и historical verdicts не менять. Доступные сохранённые данные уточнять без нового proof Build лишь ради чтения.

VPS — Git/hashes/static parsing и малые isolated synthetic service tests; actual preparation/extraction/compiler/decoder/refiner/verifier/full runners только Cloud. Обновляй STATUS и существующие semantic/session/release/coverage/experiment records. Ниже один компактный перезаписываемый отчёт: цели, proof до→после, обслуживание отдельно, каждый Build/гипотеза/candidate/результат/charge, T0/end, own active/unresolved/requests/reservations, closure без carry и следующий blocker. Большую матрицу/provenance держи отдельно по ссылкам; wall-clock не active agent time.

## Отчёт агента

- R7 ACTIVE. T0 14:33:33Z, main16:33:33Z, absolute17:03:33Z; отдельный бюджет3600, без carry R6.
- Цель: checked guard array/geometry → late lifetime/loan/readonly CURRENT normal Continue/break/unwind → original guard loan/Drop → merge/caller. Полная theorem/B2/qualification OPEN, independent credit0.

| Build / candidate | Наблюдение | Charged / execution |
| --- | --- | --- |
| [1: e8d17588 / 1e93fe1a](cloud-build/origin-layout/R7-BUILD1-RESULT-20261020.json) | Checked emptytail → Drop alignment93; tool45594fb8; FAILURE | 601 / 600 |
| [2: f580a235 / 63b28d89](cloud-build/origin-layout/R7-BUILD2-RESULT-20261020.json) | Translator-only late scope; frontend GhostCmd Not_found, до resource proof; FAILURE | 569 / 569 |
| [3: e28eabe2 / cbeccadb](cloud-build/origin-layout/R7-BUILD3-RESULT-20261020.json) | Missing tuple parenthesis7174, actual proof not attempted; FAILURE | 288 / 288 |
| [4: b360bb7a / 5f2c0f24](cloud-build/origin-layout/R7-BUILD4-RESULT-20261020.json) | Compile/prep7zero; добавленный early global-span assert252; FAILURE | 603 / 602 |
| [5: 4bb2b951 / 71aa4b67](cloud-build/origin-layout/R7-BUILD5-RESULT-20261020.json) | Compile/prep7zero; late FnMut310 и half-token close311 → No such label; FAILURE | 403 / 403 |

- Все5 Builds terminal, used2464/3600, remaining1136; own active/unresolved/reservations0 после штатного accounting. Окно/бюджет не продлены.
- Последний executed proof=infra `71aa4b67819c8649b0827b9c955c1a0926e945e6`, tool1aa4795e/profile R7. Candidate5 удалил только дополнительный speculative global-span assert; исходные Drop/copy gates и full CURRENT posts сохранены, disjointness не предположена. Independent LunaHIGH GO; static17patch/18base и service checks PASS.
- Proof-прирост: emptytail helper checked относительно существующего определения; actual late FnMut достигается и half-token close проверяется на наблюдаемом пути. Полный token/type-scope exit, borrow_end/readonly-end на обоих путях, original guard и финальный CURRENT остаются OPEN.
- Обслуживание отдельно: R7 registration, source placeholders, ordinary outcome selector, strict source/stage/target control matchers. Свежие Build4/5 array source1positive/3expected и late-admission2expected, accepted=false; это не qualification или независимый theorem credit.
- Независимые границы: BeforeLive lexical Unbound variable вместо физического heap refusal → INC; prefix placeholder при values.as_mut_ptr, exact Unsize parser-input binding не установлен. Быстрые ослабления не применялись.
- Следующий шаг: минимальное исправление synthetic label scope по actual proof AST, independent LunaHIGH delta review и новый exact published кандидат, если укладывается в окно/бюджет. [Обязательства](cloud-build/origin-layout/R7-OBLIGATIONS-20261020.md). Cloud ожидание не active agent time.
