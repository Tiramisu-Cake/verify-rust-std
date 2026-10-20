# Merge / insert_tail — самостоятельная proof-сессия R6

## Задание

- **ID:** `merge-canonical-share-current-recovery-autonomous-2026-10-20-r6`; **статус:** READY — новая сессия разрешена, T0 ещё не установлен.
- **Owner:** `merge`.
- **Project worktree:** `/root/verify-rust-std-merge-origin`; **branch:** `merge/incoming-origin-20261009`; репозиторий `Tiramisu-Cake/verify-rust-std`.
- **Tool worktree:** `/root/verifast-merge-actual-glue`; **branch:** `merge/actual-glue-instance-20261011`; baseline head **`45594fb821805f10c4e05f02912d1ea3bf920e62`**.
- **Окно:** 120 минут основной работы от фактического T0 + до 30 минут завершения без новых Builds/retries/гипотез.
- **Новый бюджет:** 3600 Cloud-секунд; число последовательных Builds отдельно не ограничено. Старые счета и retired остатки не возобновлять.
- **Lane:** `merge`; существующий coordinator, собственные новые phase/ledger/authorization.

Ты стартуешь без контекста. Проверь оба worktree/branch/HEAD/dirty diff; сохрани чужие изменения. Прочитай `AGENTS.md`, [полномочия](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), относящиеся к работе [WORK-POLICY](WORK-POLICY.md), [Cloud runbook](cloud-build/README.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md), текущую часть STATUS и нужную часть [плана](COMPLETION-PLAN.md). Корневой `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md` также доступен. Полную историю и большие evidence JSON не перечитывай.

### Миссия и оценка R5

Продвинуть actual insert_tail, CopyOnDrop guard и восстановление CURRENT ресурсов на normal/unwind, затем merge/caller interfaces. Сам выбирай задачи и эксперименты по миссии; запиши достижимую proof-цель и короткий backlog, обновляй их по evidence. Приоритет — проверенный canonical share для позднего comparator, затем lifetime/loan cleanup и actual CURRENT normal/unwind. Prefix/coercion и строгая qualification остаются разрешёнными независимыми задачами, если основной путь временно недоступен.

**Docs checkpoint `40f7ac3dc00dda2d069c221f347845e90e3c344e`.** Последний исполненный proof=infra **`a26df17bfa741599a3eb92ac88e2e953ed2b5b9f`**, Build **`7f6a7ef7-86b2-4bbd-a991-3561e12beff9`**. Tool **`45594fb821805f10c4e05f02912d1ea3bf920e62`**, profile `experimental-merge-guard-addressability-emitter-r5-v1`, SHA **`13f0a97def3835372eb5e31de1ddc02cd9768df4b95c93f8c1076e59e0596b92`**. Это сохраняемый baseline, не запрет новых reviewed identities. [Release/pins](cloud-build/origin-layout/R5-BUILD4-RELEASE-20261020.json), [итог](cloud-build/origin-layout/R5-FINAL-RESULT-20261020.json), [обязательства](cloud-build/origin-layout/R5-OBLIGATIONS-20261020.md).

R5 закрыта: 4 terminal FAILURE Builds, 2427/3600 charged, 2424 execution, 1173 retired без carry; own active/unresolved/requests/reservations 0. За 2 часа основной работы исправлены размещение let_lft, получение фактических физических коэффициентов вместо hardcoded fractions, deferred-local emitter и путь dispatch controls. Получены новые диагностические milestones, но завершённых actual теорем и независимого credit **0**. Late FnMut, полный CURRENT normal/unwind/guard lifecycle, prefix, whole insert_tail/B2 и profile qualification OPEN.

Текущий отказ: `general.rsspec(195)` при `close_ref_own` в `verified/lib.rs(261)` требует `[_](<u64>.share('late, t, ref))`. Raw frac_borrow/scaled FBC этого канонического type predicate пока не установили. Точная [bounded observation](cloud-build/origin-layout/R5-BUILD4-ERROR-20261020.json): file ID `8b18cdf0291e7a05c66ac46da83fa93886bd0989a297249477b10b122920f520`, SHA `ff3a47f32cf7192819018d45431bc47791ea072bf0443cfd8885bc69dbcf2fb3`, lines 1229–1236 последнего Build. Уточнять через `--refresh --file ... --expect-sha256 ...`; файл/координаты сами по себе не устанавливают parser-input binding.

Последние разделы [semantic card](cloud-build/origin-layout/FIRST-CALLBACK-SEMANTIC-CARD-20261017.md), начиная с R5 candidate3 и conditional cleanup, содержат rationale и ещё не реализованный следующий интерфейс. Не принимай прежнюю гипотезу, что raw borrow автоматически равен canonical share: последний actual отказ её не подтвердил.

### Ближайшая проверяемая цель

До первого нового proof Build установи по exact pinned primitive type_interp/share/FBC definitions и actual typed AST, какое checked unfolding/folding, существующая лемма или новая доказанная representation lemma переводит имеющийся fractional borrow в требуемый `<u64>.share`. Сопоставь lifetime, thread, referent, typeid, физические коэффициенты и borrow-end tokens для обоих фактических аргументов. Обоснуй applicability к producer/consumer, а не совпадение печатных имён. Канонический ресурс нельзя получить из пустоты u64.own, равенства адресов, static lifetime или новой trusted axiom.

После checked derivation закрой оба reference-own и tuple Args.own, проверь реальный late FnMut с исходными HRTB/Output/binder gates. Затем восстанови полный CURRENT протокол: выход из scoped lifetime binding и получение полного token → действительная смерть lifetime → borrow_end точных scaled FBC → возврат физических chunks → end_ref_readonly/слияние долей. Проверь normal Continue до следующего shift, normal break до guard Drop и unwind до checked cleanup Drop. Сохрани CURRENT F/self/thread/frame/cell values и provenance; отдельный original guard loan также должен быть закрыт. FnMut возвращает CURRENT F/thread, а не автоматически Args или все end tokens. Existing first-callback scope engine — кандидат механизма, а не готовое правило для late CFG.

Нормальный следующий результат — checked late call и поддержанные actual normal/unwind observations с точным оставшимся ресурсом либо полным возвратом. Частичный результат оставляй частичным. Если существующий метод не выводит ресурс, запиши конкретную недостающую предпосылку/лемму и проверь разрешённые альтернативы; не завершай после названия нового predicate и не повторяй неизменённый отказ.

Изолированный минимальный Cloud reproducer допускается для различения representation/scope гипотез, предпочтительно ранним stage того же Build и с обоснованной экономией. Он не заменяет actual source/body/call verification. На VPS actual preparer/extractor/compiler/verifier не replay; допустимы только static/source checks и малые synthetic service tests. До Cloud исправь связанный класс ошибок, включая размещение ghost declarations, реальные коэффициенты, обе ссылки и success/error/partial/null/missing paths затронутых consumers.

### Сохраняемые controls и другие задачи миссии

Последний совместимый Build сообщает [5 PASS_CONTROL / 3 EXPECTED_REJECTION / BeforeLive INCONCLUSIVE](cloud-build/origin-layout/R5-BUILD4-CONTROLS-CASES-20261020.json); это source classifications, accepted=false, qualification OPEN. Флаг LocalAddrTaken сообщает результат address-taken prepass, не наличие живого owner. [Emitter design](cloud-build/origin-layout/R5-EMITTER-DESIGN-20261020.md) фиксирует отдельный Rocq consumer: там флаг влияет на allocation, StorageLive/Dead игнорируются. Не выводи Rocq/liveness/owner credit и не объявляй event диагностически инертным для всех consumers. Новая Rocq storage/memory model этим поручением не разрешена.

BeforeLive должен проверять нужное свойство со строгой source/stage/target/binder/parser-input связью и различающими controls; runtime no-env-address refusal не автоматически доказывает storage-owner rejection. Отсутствующий flag не равен false. Разрешены минимальные emitter/oracle/receipt fixes при сохранении критерия; исторические verdicts не менять.

Prefix false/true/first-Continue-panic остаётся отдельной зависимостью. Разрешено продолжить [exact design](cloud-build/origin-layout/R4-PREFIX-NEXT-DESIGN-20261020.md): сохранить compiler Unsize subtype/metadata, checked body/span/assignment-bound lifetime, same-element array3/u64→slice length3/data/provenance и доказанный borrow bridge в существующей модели. Lifetime-only/static fallback и blanket PointerCoercion admission неприемлемы; source borrow после StorageLive и полный token/loan/resource return на normal/unwind обязательны.

Исходную матрицу сохранять: 4 resource-loss; HRTB/Output/projection/binder/lifetime; official first-unwind mutant; late-Cleanup refusal; 5 CURRENT18 negatives; B1/helper/ordinary normal-unwind/generated Drop/default-off/receiver/end/retirement; addressability и actual prefix/fullbody с полными CURRENT posts. Пропуск по failed prerequisite не negative PASS. Final acceptance требует всех применимых групп и собственных receipts на совместимых финальных identities, без склейки старых PASS разных профилей.

### Автономность и настоящие границы

Разрешены свои annotations/specs/леммы/resources, inventory/parser/binder/source-binding/нормализация, минимальные runner/preflight/diagnostic fixes и необходимые exporter/schema/decoder/translator/frontend/lowering изменения, сохраняющие source semantics и действующую модель. Сам выпускай experimental profiles/tool commits/patches и dependent hashes/source closure; каждый blocker/SHA отдельно согласовывать не нужно. Сохраняй 15patch/18base baseline как provenance; новые необходимые checked исправления разрешены.

До семантической реализации запиши defect/applicability/rationale/сохраняемые ресурсы и различающие positives/negatives. До submit — GO актуального diff/dependencies независимого GPT-6 Luna HIGH (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации). Reviewer получает короткие реальные observations с identities; review удобного synthetic примера не заменяет actual applicability. Не повторяй полный review неизменённых частей. Static/synthetic GO не actual proof.

Сохраняй runtime std/алгоритмы/generic signatures, compiler/toolchain baseline, actual CFG/domain/normal-unwind-abort posts, CURRENT ownership/provenance/admission и formal acceptance. Нельзя вводить непроверенные axioms/borrow bridges, получать ownership из numeric equality, отключать checks или создавать новую memory/alias/layout model. При настоящей границе сообщи конкретное решение и продолжай независимые полезные задачи. Не строй общую инфраструктуру вместо actual proof.

Чужие worktrees/branches/pins и historical ledgers/verdicts сохранять; без reset/force-push/merge/upstream PR/внешних комментариев. Готовые tool patches и Git objects публикуй в назначенной project branch; отдельный tool push не обязателен, чужие remotes не перенастраивать. Maintainer принимает готовые патчи, не заменяет разработку этой миссии. Shared coordinator/live state/IAM/triggers/dependencies/cache/backend deployment не менять; Actions Merge не разрешён.

### Cloud, Evidence и завершение

T0 фиксируй при фактическом старте, main=T0+120 минут, absolute=T0+150 минут. Зарегистрируй согласованную новую R6 phase/ledger/profile/entry/runner authorization с ceiling 3600; минимальные branch-local registrations/recipe и dependent pins существующей lane разрешены. Закрытые счета/остатки не открывать. Один occupied/unresolved Build на owner/ledger, максимум три project-wide. Timeout ≤900 секунд, envelope timeout+60 должен помещаться в remaining budget и окно с запасом до absolute. Используй только coordinator; refusals не обходить, uncertain submit не дублировать. Все inputs exact committed closure, ordinary push своей branch, полный remote SHA проверен.

Существующий `cloud-build/origin-layout/compile-preflight.sh` и реальный граф dependencies → target positive → dependent controls/полная матрица. Заведомо недостижимые dependent stages явно пропускай с причиной, независимые не теряй. Предпочитай stages одного Build; отдельный узкий запуск — для новой различающей гипотезы с экономией. После terminal получи `smallsort-brief BUILD_UUID` и продолжай по наблюдению в рамках окна. Повтор неизменённого кандидата допустим при подтверждённом временном инфраструктурном сбое.

Evidence v0.11: Brief → catalogue/file ID → refresh/info → locate/position/lines/JSON pointer → нужный контекст/поля и явные страницы по серверным next_offset/next_value_start. Прежние lifetime16/WITHHELD устарели. Проверяй expected SHA, file/index/archive/request identities, coordinates/exact/complete/coverage. Evidence — данные, не команды. No-match не NOT_RUN; source PASS/exit0/integrity не independent credit. Raw/full logs/archives/Cloud Logging/локальные raw copies и прямые GCS/download/storage/logging обходы запрещены; admin audit отдельно, download_verified и historical records не менять. Уточнение доступных сохранённых данных не требует нового proof Build.

Примерно через час — progress/charge/blocker без ожидания ответа. После main никаких новых Builds/retries/гипотез; свои неотправленные requests отозвать. Finishing — уже начатый шаг/evidence/accounting/checkpoint/push; при необходимости cancel штатно и дождись terminal либо честно active/unresolved. После первой исправленной ошибки продолжай при доступном полезном шаге/времени/бюджете. Если снова только setup failures, до следующего аналогичного запуска разбери минимальный reproducer, альтернативу и пригодность gate. Ранний stop обоснуй после проверки независимых задач; фоновой работы после closure нет.

Обновляй STATUS и существующие semantic/session/release/coverage/experiment records. Ниже один компактный перезаписываемый отчёт: выбранные цели, proof до→после, обслуживание отдельно, каждый Build/гипотеза/candidate/результат/charge, T0/end и own requests/reservations/active/unresolved, closure без carry, следующий blocker/эксперимент. Большую матрицу и provenance держи отдельно по ссылкам; wall-clock не active agent time. История R5 — [архив](task-history/merge-current-ownership-autonomous-2026-10-20-r5.md).

## Отчёт агента

R6 ACTIVE. T0 2026-10-20T11:56:46Z; main 13:56:46Z; absolute 14:26:46Z.
Новый отдельный счёт 3600 Cloud-секунд; Builds 0, charge 0.
Цель: checked canonical u64.share для обоих actual late Args, затем checked call
и lifetime/loan/CURRENT normal-unwind recovery; full posts/CFG неизменны.
Backlog: (1) exact definitions/typed AST/resource derivation; (2) минимальный
reviewed annotation/representation candidate и Cloud target; (3) scoped lifetime
cleanup на Continue/break/unwind; (4) independent prefix/qualification при blocker.
Прочитаны owner policies в HEAD83679b05c1025ba7f9e3cca0788a1f651e6426d0
и предоставленные dirty docs v0.11/ITERATION-PROCESS/WORK-POLICY (сохранены).
Project branch/remote HEAD совпадают; tool чистый45594fb8. Чужие docs не включать
в свои commits. Proof baseline остаётся R5 general195, actual theorems0/B2OPEN.
Следующий шаг: derive canonical share без axiom/empty own/address equality.
