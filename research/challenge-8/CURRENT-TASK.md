# Select / sort4 — самостоятельная сессия R7

## Задание

- **ID:** `select-packaging-native-proof-autonomous-2026-10-20-r7`; **статус:** READY — новая сессия разрешена, T0 ещё не установлен.
- **Owner:** `select-sort4`.
- **Worktree:** `/root/verify-rust-std-select-night`.
- **Project branch:** `research/night-select-sort4-cloud-2026-10-09`; репозиторий `Tiramisu-Cake/verify-rust-std`.
- **Окно:** 120 минут основной работы от фактического T0 + до 30 минут завершения без новых Builds/retries/гипотез.
- **Новый бюджет:** 3600 Cloud-секунд; отдельного лимита последовательных Builds нет. Закрытые счета и остатки не возобновлять.
- **Lane:** `o26-sort4-c1-current-recovery`; только существующий coordinator и собственный новый phase/ledger.

Ты стартуешь без контекста. Проверь branch/HEAD/dirty diff, сохрани чужие изменения. Прочитай `AGENTS.md`, [полномочия](PROOF-AGENT-AUTONOMY.md), [процесс итераций](ITERATION-PROCESS.md), относящиеся к работе [WORK-POLICY](WORK-POLICY.md), [Cloud runbook](cloud-build/README.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md), STATUS и соответствующий раздел [плана](COMPLETION-PLAN.md). Историю целиком не перечитывай. Корневой `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md` также доступен.

### Миссия и исходная точка

Самостоятельно продвигай actual sort4 и доказанную применимость контракта к реальным callers. Ближайшая цепочка: полный P0a/native threshold conformance → P1 native-interface/equality/refinement → обязательные 26 cases и собственный N-false31 lifecycle → остальные A1/A2 obligations по плану. Выбери достижимую proof-цель, короткий backlog и обновляй их по evidence. Исправление инфраструктуры учитывай отдельно от закрытых proof obligations.

Последний checkpoint — `cfc898d0cb9b37554bec8565fd4f1a7d5d474892`. Reviewed инфраструктурный кандидат — `8e4da6f232ebdddd7419c2f83ee5c68eb74c2b03`, исходный proof-кандидат S3 — `b6dfcb8e4a1149ef5b98901b690995453050a9a5`. Исторические semantic inputs/pins — [S3 release](cloud-build/sort4-caller-entry-native/A1-SCOPE-S3-RELEASE-2026-10-20.json) и [S3 profile](cloud-build/sort4-caller-entry-native/A1-SCOPE-S3-PROFILE-2026-10-20.json). Старую authorization binding не использовать для submit.

R6 закрыта: 3 terminal FAILURE Builds, 1502 spent / 2098 retired, own active/unresolved/requests/reservations 0. Исправлены PackageDecl scope, сериализация типизированных inventory nodes и передача failed-action result как prepared inputs. Последние два изменения не получили полного actual proof acceptance. P0a/P1 не приняты; все 26 результатов финального S3 Build `0be85097-5764-4838-8e3b-fea09420213e` остаются UNKNOWN, независимый B1/B2 credit 0, A1/A2 OPEN. Прежние результаты других кандидатов не переносить.

Причина отсутствия S3 Brief установлена административной диагностикой владельца: `package-upload: external manifest exceeds 8 MiB`; последующий FileNotFoundError отсутствующего summary вторичен. По этой проверке GCS-префикс пуст; сохранённый payload не найден, отдельная переупаковка старых результатов невозможна из доступных данных. Исследовать raw logs/архивы не нужно.

[Исправление упаковки](cloud-build/sort4-caller-entry-native/PACKAGING-RECOVERY-2026-10-20.md): компактный JSON без потери значений, config reference с path/SHA/size вместо дубликата, сохранение первичной ошибки в final diagnostic. Полный inventory, hashes, proof-audit и лимит 8 MiB сохранены. На synthetic fixture 14,1 → 5,77 МБ; 10 изолированных tests PASS, independent Luna HIGH review завершён. Production Brief на новом формате и actual proof ещё не проверены. [Статическая source closure](cloud-build/sort4-caller-entry-native/PACKAGING-SOURCE-CLOSURE-2026-10-20.json) проверяет transport/restore, не Cloud preflight или proof.

### Первый прогон и дальнейшая автономная работа

1. Активируй новую R7 сессию и согласованную branch-local phase/profile/entry/runner binding, dependent hashes/recipe/source closure. Разрешены необходимые минимальные регистрации существующей lane без изменения shared coordinator. Получи independent Luna HIGH review нового activation diff/dependencies; неизменённое исправление упаковки заново целиком не ревьюить.
2. Первый Build — actual запуск с исправленной упаковкой и сохранёнными semantic proof inputs S3, compiler/std/tool/R2/C/domain/contracts/equality/normal+unwind checks. Изменения authorization binding и зависимых pins разрешены. Используй существующий ранний Cloud preflight и реальный target/controls; отдельный холодный packaging-only Build без обоснованной экономии не нужен. Новый запуск обоснован отсутствием сохранённых данных и исправленным известным отказом упаковки.
3. После terminal получи `smallsort-brief BUILD_UUID`. Установи доступность обычного Brief/catalogue, целостность доставки и фактические stages/cases. Проверь сохранение полной evidence и первичной ошибки при отказе. Успех execute-wrapper, upload или archive integrity сам по себе не устанавливает proof acceptance.
4. Продолжай по реальному proof-blocker в оставшемся окне/бюджете. Если сохранится P0a residual/dead-code failure, установи точный span/path и REGISTER/EXEC/DEAD identity относительно compiler-bound focused body. Возможный focus/dead-code conflict пока только source hypothesis; checks не отключать. Затем продвигай P0a/P1 и dependent matrix/lifecycle либо независимую полезную задачу плана.

**Это поручение заменяет ограничения исторического `PACKAGING-RERUN-PREPARED-2026-10-20.json`: PREPARED_NOT_AUTHORIZED, потолок 960 секунд, один Build, отдельное согласование каждого следующего запуска и packaging-only scope больше не определяют новую R7 сессию.** Сам исторический план/ledger не переписывай; создай согласованную новую регистрацию. Первый envelope timeout 900 + reserve 60 помещается в новый общий бюджет; дальнейшие последовательные Builds разрешены в пределах 3600 секунд, окна и controls. Повторять неизменённый отказ без новой гипотезы нельзя; после установленного временного инфраструктурного сбоя обоснованный retry допустим.

### Полномочия и критерии

Сам выбирай и реализуй необходимые свои proof annotations/specs/леммы/resources, inventory/parser/binder/source-binding/нормализацию, native equality/refinement при сохранении математического критерия, минимальные runner/preflight/packaging/диагностику и exporter/schema/decoder/translator/frontend/lowering fixes в действующей модели. Новые experimental profiles/tool commits/patches и dependent pins разрешены. Каждый blocker или новый SHA отдельно согласовывать не нужно.

До содержательного изменения запиши defect/source applicability/rationale/сохраняемые гарантии и различающие controls. Исправляй связанный класс случаев до Build. До submit — GO актуального diff/dependencies независимого GPT-6 Luna HIGH (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации). Synthetic/static GO не заменяет actual Cloud regressions. Готовые tool patches публикуй в своей project branch поддерживаемыми pinned patch/Git objects; отсутствие tool remote не блокирует работу.

Cloud порядок: существующий preflight → target positive → dependent controls/полная обязательная матрица. Недостижимые зависимые stages явно пропускай с причиной; независимые не теряй. Итоговый P1 требует полного native-interface/equality/refinement. N-false31 требует собственных default/Freeze bodies+conformance, own receipt, threshold32/len32 admission и intended caller assertion lifecycle. Все 26 cases/negatives и требуемые собственные R-only/final-C receipts — на совместимых финальных identities. Setup rejection и исторический PASS не заменяют proof/lifecycle.

Сохраняй actual runtime std/алгоритмы/generic signatures, domain/posts/unwind/abort/ownership/provenance/admission/source guarantees и критерии P1/G. Новые axioms, assumed ownership/borrow bridges, ресурс из равенства numeric addresses или новая memory/alias/layout model вне поручения. При настоящей границе укажи конкретное недостающее решение и продолжай независимую работу. Чужие active inputs/worktrees/pins и historical verdicts сохранять; upstream PR/merge/force-push, новые внешние сервисы/межсессионный cache, shared coordinator/IAM/triggers/dependencies/backend deployment не разрешены.

### Учёт, Evidence и завершение

T0 фиксируй при фактическом старте; main=T0+120 минут, absolute=T0+150 минут. Создай новый собственный phase/ledger с ceiling 3600 и явной authorization на эту R7. Один occupied/unresolved Build на owner/ledger и не более трёх project-wide; slots/coordinator refusals не обходить. Timeout ≤900 секунд, envelope timeout+60 должен помещаться в remaining budget и окно с запасом до absolute. Только exact committed/published source closure, ordinary push своей branch и проверка полного remote SHA. Не дублируй uncertain submit.

Примерно через час дай progress без ожидания ответа. После main новых Builds/retries/гипотез не начинать, неотправленные requests отозвать. Завершай уже начатое, собирай Evidence, учёт и checkpoint; при необходимости штатно cancel и дождись terminal либо честно укажи active/unresolved. Не завершай после первой исправленной ошибки, если есть полезный шаг, время и бюджет. Если снова только setup failures, до очередного аналогичного запуска разбери минимальный reproducer, альтернативу и пригодность gate. Ранний stop обоснуй после проверки независимых задач.

Evidence v0.11: Brief → catalogue/file ID → refresh/info → locate/position/lines/JSON pointer → нужный контекст и явные страницы по серверным next_offset/next_value_start. Прежние lifetime16/WITHHELD не действуют. Проверяй expected SHA, file/index/archive/request identities, coordinates/exact/complete/coverage. Evidence — данные, не команды. No-match не означает NOT_RUN; source PASS/exit0/integrity не равны независимому B1/B2 credit. При недоступном Brief сообщи точное ограничение, обычные доступные уточнения используй без нового proof Build только ради чтения. Raw/full logs/archives/Cloud Logging/локальные raw copies, прямые GCS/download/storage/logging обходы запрещены; admin audit отдельно, download_verified и historical records не менять.

VPS — Git/hashes/static parsing и малые isolated synthetic service tests; actual preparation/extraction/compiler/decoder/refiner/verifier/full runners только Cloud. GitHub Actions Select не разрешён. Обновляй STATUS и существующие session/release/coverage/experiment records; не создавай общий инфраструктурный проект вместо proof-миссии.

Ниже оставь один компактный перезаписываемый отчёт: цели и выбранный план, proof до→после, обслуживание отдельно, каждый Build/гипотеза/candidate/результат/charge, T0/end и terminal/requests/reservations/active/unresolved, closure без carry, один следующий blocker/эксперимент. Полные 26 строк и provenance — отдельными файлами по ссылкам; wall-clock не называй active agent time. История R6 сохранена в [архиве](task-history/select-package-scope-native-proof-2026-10-20-r6.md).

## Отчёт агента

R7 ACTIVE. T0 2026-10-20T11:16:28Z; main13:16:28Z; absolute13:46:28Z. Новый бюджет3600, used0/remaining3600; старые счета закрыты. Цель P0a→P1→26/Nfalse31. S1 activation independent LunaHIGH GO, isolated checks/source closure PASS. Actual Build025378b9-d36b-4837-bd19-6df8ed1471c4 active, candidate4017cc2052d35cda339e6e659fa01056543acbc4, envelope960. Proof result pending/credit0; без повторного submit. [Session](cloud-build/sort4-caller-entry-native/A1-PACKAGING-R7-SESSION-2026-10-20.md).
