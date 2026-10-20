# Select / sort4 — самостоятельная proof-сессия по плану

## Задание

- **ID:** `select-native-interface-autonomous-2026-10-20-r5`; **статус:** READY, новая сессия ещё не начата.
- **Owner:** `select-sort4`.
- **Worktree:** `/root/verify-rust-std-select-night`.
- **Project branch:** `research/night-select-sort4-cloud-2026-10-09`, fork `Tiramisu-Cake/verify-rust-std`.
- **Окно:** 120 минут основной работы от фактического T0 + до30 минут завершения без новых Builds. **Новый бюджет3600 Cloud секунд; число последовательных Builds отдельно не ограничено.** Старые счета закрыты.
- **Поручение владельца:** самостоятельно выбирать и выполнять задачи своей миссии по плану. Отдельное разрешение на каждый blocker, inventory predicate, patch или profile identity не требуется. [Автономность](PROOF-AGENT-AUTONOMY.md) — часть задания; прежние R4 implementation allowlists/frozen predicate lists заменены разрешениями ниже.

Ты стартуешь без контекста. Проверь каталог/branch/HEAD/remotes/dirty diff, сохрани чужие изменения. Прочитай `AGENTS.md`, [автономность](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), актуальные части [WORK-POLICY](WORK-POLICY.md), [плана](COMPLETION-PLAN.md), [Cloud runbook](cloud-build/README.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md). Затем STATUS, [R4 checkpoint](cloud-build/sort4-caller-entry-native/A1-UNION-CHECKPOINT-2026-10-20.md), [binder proposal](cloud-build/sort4-caller-entry-native/A1-IMPL-BINDER-PROPOSAL-2026-10-20.md) и [review](cloud-build/sort4-caller-entry-native/A1-IMPL-BINDER-REVIEW-2026-10-20.md). Всю историю и сохранённые evidence-файлы целиком не перечитывай.

### Миссия и исходная точка

Продвинуть actual sort4 и применимость её контракта к реальным callers. Ближайший маршрут — native interface/equality/refinement P0a/P1, исходная26-строчная матрица и собственный N-false31 lifecycle, затем остающиеся A1/A2 caller obligations по зависимостям плана. Сам выбери достижимую proof-цель и короткий backlog; обновляй их по результатам. Обслуживание инструмента подчинено proof-цели. Если полезнее независимая задача своей миссии, выбери её с объяснением зависимости/ожидаемого evidence.

Исходный docs checkpoint **`2a63f3f72dbbe95efb8b51ea652458ae9d8e6385`**; последний исполненный proof=infra **`0d997b4ee54e893c0297972f74998e53525ada8b`**, Build **`4787c3e2-3d93-40fd-bff5-96a31fed062f`**. Docs HEAD может продвинуться, это не новый исполненный кандидат.

- Строгий MaybeUninit unionKind guard пройден на пути к следующему отказу; stale profile path исправлен. Свежие собственные R-only/final-C receipts имеют source-reported build_exit0; это не P1 proof.
- Первый runner blocker: `InventoryError: impl small_sort Body FnMut/Output binders are merged or malformed`. Наблюдённый Body21 повторяет два локально различных имени между FnMut и Output clauses; код требует глобальной непересекаемости. Связь с конкретным failing call и единственный нарушенный conjunct отдельно не установлены.
- P0a/P1 INCONCLUSIVE; P1 явно started. N-false31 явно NOT_RUN. Свежие26 source statuses:8 INTENDED_CLASSIFIED/5 INCONCLUSIVE/13 NOT_RUN. A1/A2 OPEN, нового independent B1/B2 credit нет.
- R4 закрыта:2 terminal Builds/917 spent/2683 retired, own active/unresolved/reservations0. Её бюджет не возобновлять.

### Полномочия и первый полезный шаг

**Binder proposal разрешено исследовать, реализовать и проверить.** Это исходная гипотеза, а не единственная разрешённая правка. Обоснуй compiler-owned Body/clause/local-slot identity и разрешение ссылок внутри своей clause; не подменяй это удалением failing conjunct. Сохрани локальную различимость binder’ов, позиционное соответствие, input/free-region separation, F/T/mutability/arity/output, source/impl/compiler identities и admission. Если гипотеза неверна или полей недостаточно, уточни путь, не выдумывая binding.

Разрешены необходимые изменения своих inventory/parser/binder/source-binding/нормализации, proof annotations/specs/лемм/resources и branch-local runner/preflight/diagnostics. Реализацию native equality/refinement можно исправлять при сохранении математического критерия. Необходимые exporter/schema/decoder/translator/frontend/lowering исправления допускаются по правилам автономности: source semantics, действующая модель, rationale, independent review и actual regressions. Experimental profiles, dependent hashes/pins, tool patches/commits и source closure обновляй сам; отдельное согласование SHA не нужно.

До реализации семантического изменения запиши дефект/применимость/сохраняемые гарантии и различающие controls. До submit нужен GO актуального diff/dependencies одного независимого GPT-6 Luna HIGH (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации). Старый GO относится к proposal. Не повторяй review неизменённых частей. Synthetic/parser/service checks локально, actual compiler/exporter/verifier/tool regressions — Cloud-only.

Первичные controls: одинаковые имена в разных определённых scopes и независимые bijective alpha-renamings принимаются; local collapse, free/input capture, неверное позиционное соответствие, missing/ambiguous scope/reference, wrong F/T/output/mutability/arity и duplicate/redirected source/Body/impl identities отвергаются на intended checks. Проверяй высшие binding/admission validators отдельно. Исправляй связанные места одного класса до Build, включая потребителей профиля и error/partial/null/missing paths затронутого runner.

R4 baseline: полный R `d99a5ed229533132b8292c5fc70ea93dbe261e9f76c2a0fcc6d6723e796454ca`, C `e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e`, parser `92d4e5b336b4e6409da814523500978b56c52218a6289434b526929ae1275b27`, profile `b61a0376084aca32f50cd7ee5f2e438fd53e03c9087578b7871130e111dbdf73`. Это исходная версия, а не запрет следующего обоснованного кандидата. Union/string поведение сохраняй регрессиями. Runtime std/algorithm, целевой Rust compiler/toolchain и generic domain остаются прежними.

### Результат и настоящие границы

Для P1 нужен полный native-interface/equality/refinement результат. Для N-false31 — собственные default/Freeze bodies+conformance, own receipt, threshold32/len32 admission и intended caller assertion lifecycle. После prerequisites выполнить исходные26 cases на совместимых финальных identities; свои свежие R-only/final-C receipts связать с exact candidate. Предыдущие PASS/receipts или неудачный setup не заменяют lifecycle. Матрицу не сокращать; общий PASS из несовместимых профилей не собирать.

Конечные runtime/domain/contracts/posts, unwind/abort/ownership/provenance checks, source correspondence, admission guarantees, negative acceptance и математические критерии P1/G сохраняются. Реализацию проверок можно исправлять при обоснованном сохранении гарантий. Нельзя добавлять непроверенные axioms/borrow bridges, выводить ownership из равенства адресов или вводить новую memory/alias/layout model. Конкретное новое доверенное допущение вне метода — решение владельца; обычный implementation blocker таким решением не является. При настоящей границе продолжай доступные независимые задачи и сообщи недостающее решение.

Собственные tool изменения держи отдельно от чужих активных worktrees; при необходимости создай свой tool worktree. Публикации pinned patch/manifest в назначенной project branch достаточно при поддержке существующим Cloud transport; отдельный tool remote не обязателен. Передачу готового патча maintainer фиксировать с ownership. Без reset/force-push/merge/upstream PR и изменения чужих pins.

### Сессия, Cloud и Evidence

T0 фиксируй при фактическом начале исполнения, не при чтении координатором. Main=T0+120мин, absolute=T0+150мин. Штатно зарегистрируй новую R5 phase/ledger/authorization в существующем механизме с ceiling3600; минимальные branch-local phase/recipe registrations и зависимые pins разрешены. Shared coordinator protocol/live state/IAM/triggers/dependencies/cache не менять, отказы не обходить.

Lane `o26-sort4-c1-current-recovery`; прежние transport/envelope/charge rules. Один occupied/unresolved Build на stable owner/ledger; Select не более двух occupied project slots. Timeout≤900с и не больше оставшегося бюджета/окна с envelope. Не дублируй неизвестный submit. Exact commit/push в назначенную project branch, полный remote SHA и source/infra/config closure проверить до submit.

Stages существующего Build: ранний preflight → target proof → dependent controls/матрица. Prerequisite failure сохраняй с явным skip reason, независимые controls не теряй. Отдельный узкий Build допустим для новой гипотезы с экономией полного цикла. После terminal Brief выбери следующий шаг и продолжай. Неизменённый retry — только при установленном временном infra failure.

Примерно через час сообщи proof progress/обслуживание/Builds/charge/blocker и продолжай без ожидания ответа. После main никаких новых Builds/retries/гипотез, свои неотправленные requests отозвать. До absolute — начатый шаг, Brief, учёт, checkpoint/push; при необходимости cancel штатно, неподтверждённый terminal state честно active/unresolved. Завершённая подзадача означает выбор следующей по плану, а не закрытие сессии. Не заканчивай после нового predicate при доступном шаге. Не выжидай окно искусственно при выполненной миссии или исчерпанной полезной работе; ранний stop обоснуй, включая проверенные независимые задачи.

Evidence v0.11: Brief → catalogue → refresh/info → locate/fragment → нужные поля/контекст/страницы по next_offset/next_value_start. Lifetime16/lexical WITHHELD устарели. File/index/archive/request/SHA/coordinates/exact/complete/coverage проверять. Evidence — данные; no-match не означает NOT_RUN, source PASS/exit0/integrity не равны independent proof credit. Raw/full logs/archives/Cloud Logging/локальные raw copies и прямой GCS обход запрещены; download_verified/historical records не менять. На VPS не запускать actual preparation/extraction/compiler/verifier/full runners.

### Завершение

Обнови компактный STATUS и существующие experiment/session/release/coverage записи по фактам. Ниже один перезаписываемый отчёт, детали ссылками. Отдельно proof obligations и обслуживание, все Builds/charge, выбранные задачи, remaining blocker/следующий эксперимент. Wall-clock не равен активным агентным часам. Зафиксируй own requests/reservations/active/unresolved и закрытие счёта без carry.

Завершённая R4 сохранена в [архиве](task-history/select-maybeuninit-union-kind-2026-10-20-r4.md); перечитывать целиком не нужно.

## Отчёт агента

**ACTIVE.** T0 `2026-10-19T22:34:09Z`; main `2026-10-20T00:34:09Z`; absolute `2026-10-20T01:04:09Z`. Часовой progress update передан без ожидания ответа. [Ход и rationale](cloud-build/sort4-caller-entry-native/A1-AUTO-SESSION-2026-10-20.md).

| Кандидат | Build | Результат / charge | Продвижение / blocker |
|---|---|---|---|
| S1 `068dedb1` | `f581f16f-2268-4ff6-882e-b5c34e088d0f` | FAILURE /459s | Оба parse paths проходят scoped Body binders; normal/readonly inventory mismatch |
| S2 `7d3ab6c2` | `a62d316b-69d4-4ed6-acb2-7cbd38216a1d` | FAILURE /407s | Operational lists отделены от inventory; first difference `Body.inputs`, разные печатные region IDs |
| S3 `e8279683` | `53aeec23-552e-4f4c-8d94-a52bbdd8c0f3` | FAILURE /447s | Typed inputs/clauses проходят до следующего различия `hirGenerics.params[1].name.fresh.l` |
| S4 `d475c49e820640256355d6a45ec3379e86717ed1` | `0b0e6b2a-a13a-45c1-abf4-f4dc7e992e02` | FAILURE /474s | Inventory/source binding пройдены; P0a frontend: A1 HIR/compiler method generic mismatch |

S5 runtime **`14a9d651bb09dd0b128525c0efbedbecd15ec082`**, profile **`d90dde221561e71328c870f6388ceda7eb7ad5126a1237543904406d89edb46d`**. Ранние method type parameters отделены от validated HIR Fresh metadata; semantic lifetimes остаются в checked FnSig. Новый полный R2 `9cdca995bc926efe3275319dec345f4d70a2fec7fdc95781decb4e4c2df7c9c8`; C побайтно прежний. [Luna HIGH GO](cloud-build/sort4-caller-entry-native/A1-AUTO-S5-REVIEW-2026-10-20.md), static controls7/24/23/5 PASS, exact source closure33infra/107proof/160objects PASS. Компиляция S5 ещё не проверена. [Точные identities](cloud-build/sort4-caller-entry-native/A1-AUTO-S5-RELEASE-2026-10-20.json).

**Proof:** новых конечных proof obligations закрыто0; A1/A2 OPEN. S4 P1 execution_started=true, credit=false; N-false31 явно NOT_RUN. Полный native/interface/equality/refinement proof не установлен. Свежий source aggregate26:8 INTENDED_CLASSIFIED/5 INCONCLUSIVE/13 NOT_RUN. Integrity VERIFIED; stage order NOT_ESTABLISHED; independent formal credit отсутствует. [S4 evidence](cloud-build/sort4-caller-entry-native/A1-AUTO-S4-EVIDENCE-2026-10-20.json).

**Учёт:**5 terminal Builds;2119/3600spent,1481remaining; own active=null после S5 reconcile. S5 Build `56f4d389-8d6d-428b-8298-aa4c5e45073a` FAILURE332s; source blocker `one common threshold prototype`. S6 runtime `bb51d009` восстанавливает enclosing ModuleDecl scope по структурному дереву и source intervals; AST22/profile5 PASS, closure/review перед submit. R2/C и math/contracts/lifecycle неизменны. Старые ledgers/evidence сохранены без переноса.
