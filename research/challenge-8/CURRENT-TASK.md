# Select / sort4 — самостоятельная proof-сессия R9

## Задание и авторизация

- **ID:** `select-native-interface-proof-autonomous-2026-10-20-r9`; **статус:** READY, T0 ещё не задан.
- **Owner:** `select-sort4`; **worktree:** `/root/verify-rust-std-select-night`.
- **Репозиторий:** `Tiramisu-Cake/verify-rust-std`; **branch:** `research/night-select-sort4-cloud-2026-10-09`.
- **Новое окно:** 120 минут основной работы от фактического старта R9 + до 30 минут завершения. После main новых Builds/retries/гипотез нет.
- **Новый бюджет:** **3600 Cloud-секунд**, начальный used=0. Число последовательных Builds отдельно не ограничено; действуют бюджет, сроки, slots и review.
- **Lane:** `o26-sort4-c1-current-recovery`; существующий coordinator и стабильный owner.
- **Новая phase:** `SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9`; отдельный ledger `cloud-build/sort4-caller-entry-native/BUDGET-A1-NATIVE-INTERFACE-2026-10-20-R9.json`.

**Это поручение явно разрешает R9, её бюджет и Builds после обычных gates.** Сам подготовь согласованную branch-local authorization/phase/profile/entry/runner/recipe регистрацию и dependent pins. Отдельного согласования очередного Build, implementation blocker, experimental profile или tool SHA в пределах миссии не нужно. Coordinator admission, source applicability, независимый review актуальных изменений и точные опубликованные inputs обязательны. Отказы не обходить.

Ты начинаешь без контекста. Проверь worktree/branch/HEAD и dirty diff; сохрани чужие изменения. Прочитай `AGENTS.md`, текущую часть [STATUS](STATUS.md), [полномочия](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), релевантные [WORK-POLICY](WORK-POLICY.md), [Cloud runbook](cloud-build/README.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md) и нужную часть [плана](COMPLETION-PLAN.md). Историю целиком не перечитывай.

## Исходная точка и ближайшая цель

Checkpoint R8: **`e0866831f6a8f8a54de5f032f25f04a1c8fba274`**. R8 CLOSED: пять terminal FAILURE Builds, **3028/3600 spent, 572 unused, carry0**, own active/unresolved/requests/reservations 0 на closeout. Это история; R8 и её 572 секунды не возобновлять и не переносить. [Архив задания/отчёта R8](task-history/select-post-migration-native-proof-autonomous-2026-10-20-r8.md), [session](cloud-build/sort4-caller-entry-native/A1-POST-MIGRATION-R8-SESSION-2026-10-20.md), [учёт](cloud-build/sort4-caller-entry-native/A1-POST-MIGRATION-R8-CLOSEOUT-CONTROL-2026-10-20.json).

**Proof до R9:** формально закрытых obligations 0; independent B1/B2 credit 0; P1/A1/A2/own N-false31 lifecycle OPEN. В S3/S4 P0a/P0b имели source attestations body/conformance=true и verifier exit0 с сохранёнными normal/unwind posts. Это результаты тех кандидатов; перенос на новый набор inputs не установлен. Последний S5 остановился до target: R-only translator compilation exit2, `Unbound record field sized`; все 26 строк explicit source-reported NOT_RUN. [S4 evidence](cloud-build/sort4-caller-entry-native/A1-POST-MIGRATION-R8-S4-EVIDENCE-2026-10-20.json), [S5 evidence](cloud-build/sort4-caller-entry-native/A1-POST-MIGRATION-R8-S5-EVIDENCE-2026-10-20.json).

**Готовый следующий кандидат:** `8e46fbf4c603e9a0133d3024ce22e73958d73542` — четыре доступа в трёх строках квалифицированы `Ast.sized`, predicates/control flow сохранены. Есть localized independent Luna HIGH GO, 8 isolated profile/transport checks и exact closure PASS. **Actual compilation/export/extraction/verifier NOT_RUN.** [Compile-fix record и точные hashes](cloud-build/sort4-caller-entry-native/A1-POST-MIGRATION-R8-S5-COMPILE-FIX-NOT-RUN-2026-10-20.json), [native signature rationale](cloud-build/sort4-caller-entry-native/A1-POST-MIGRATION-R8-S5-INTEGRATION-RATIONALE-2026-10-20.md).

Миссия — actual sort4 и применимость контрактов к реальным callers. Ближайшая полезная proof-цель: **полный P1 native-interface/equality/refinement**, затем совместимые финальные 26 cases и собственный N-false31 lifecycle. Сам выбери достижимый этап и короткий backlog по плану, уточняй их по Evidence. Не ограничивай сессию одной починкой компиляции; обслуживание и proof-прирост учитывай отдельно.

## Предлагаемый первый цикл и самостоятельное продолжение

1. Проверь актуальность исправленного кандидата и source closure; не считай старый R8 render разрешением на R9. Подготовь новую регистрацию и все её consumers: transport/entry/adapter/core/focus-helper, phase/profile/environment, source-core identities. Старые release/ledger не редактируй. Применимость `Ast.sized` исправления уже разобрана; повторный полный review неизменённых частей не нужен, review нового diff и затронутых зависимостей обязателен.
2. Через существующий ранний Cloud preflight установи сборку точного R-only и final-C кандидата. Предпочитай stages одного Build: compile → target → dependent controls. Отдельный compile-only Build допустим, когда он проверяет различающую гипотезу и экономит кампанию; proof credit у него 0. На VPS actual compiler/proof preparation не выполнять.
3. После сборки продвигай P0a/P0b на новых совместимых identities и P1: exact compiler-bound native signature/contract, equality/refinement, actual MIR/HIR/Symbol binding, собственные требуемые R-only/final-C receipts. Сохрани native pre/normal/unwind posts и generic/lifetime/type applicability. Одинаковые hashes или найденные строки сами по себе не устанавливают AST/MIR/parser-input binding.
4. После target пройди обязательные 26 cases/negatives и own N-false31 lifecycle: собственные default/Freeze bodies+conformance, own receipt, threshold32/len32 admission и intended caller assertion. Проверяй точные stage/predicate/location. Итоговую матрицу собирай на совместимых финальных identities; ранние source PASS других кандидатов её не заменяют.

Сохрани восстановленную доставку Evidence: R8 S1 доставил canonical audit 1 871 496 байт и original-byte companion 22 940 413 байт с lossless/inventory controls. Это не устанавливает первичную причину старого R7 S2. Сохраняй strict profile guards, baseline→overlay→C source transitions, normal/unwind и focus/dead-code checks. Требуемые focus controls: selected-body dead-code negative, excluded-body positive, no-focus negative; setup failure вместо нужного dead-code predicate — INCONCLUSIVE. HIR/Symbol исправления требуют actual binding regressions.

При новом blocker сам выбирай минимальную проверяемую гипотезу, исправляй связанные места одного класса до Build. Не повторяй неизменённый отказ. После повторяющихся setup failures сначала разбери минимальный reproducer, альтернативный интерфейс и пригодность gate. Сохраняй independent cases, зависимые пропуски отмечай с причиной. Если основной путь упёрся в настоящую границу, проверь независимую полезную задачу своей миссии.

## Полномочия и границы

Разрешены свои proof annotations/specs/леммы/resources, inventory/parser/binder/source-binding/нормализация, native equality/refinement при сохранении математического критерия, необходимые exporter/schema/decoder/translator/frontend/lowering и минимальные runner/preflight/packaging/diagnostic исправления в действующей модели. Сам публикуй experimental profiles/tool commits/patches и dependent pins в назначенной project branch; отсутствие отдельного tool remote не блокирует pinned patch/Git-object передачу. Новый proof-blocker автоматически не передавай VeriFast maintainer: он принимает готовые патчи для интеграции.

До содержательного изменения зафиксируй defect/source applicability/rationale/сохраняемые гарантии и различающие controls. До submit получи независимый **GPT-6 Luna HIGH** review актуального diff/dependencies: `model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации и дорогой автоматической замены. Устрани конкретные soundness-возражения. Static/synthetic GO не actual proof. Для затронутого runner обязательны изолированные service error-path checks, сохранение partial/NOT_RUN/ошибок и existing Cloud preflight.

Сохраняй actual runtime std/алгоритмы/generic signatures, domain/posts/normal-unwind-abort, ownership/provenance/admission/source guarantees и критерии P1/G. Не добавляй axioms/assumed ownership bridges, не выводи ресурс из numeric address equality, не отключай checks и не вводи новую memory/alias/layout model. Настоящее новое trust-допущение вынеси с точным вопросом; обычный checked proof или исправление представления нового согласования не требуют. Чужие worktrees/pins и historical evidence/ledgers не менять. Без merge/force-push/upstream PR, внешних комментариев, Actions, shared coordinator/IAM/triggers/dependencies/cache/backend deployment.

## Время, исполнение и отчёт

T0 зафиксируй **при фактическом старте R9 после прочтения задания**; main=T0+120 минут, absolute=T0+150 минут. Новый ledger с explicit authorization и ceiling3600, старые остатки не переносить. Timeout≤900с; envelope timeout+60 помещается в remaining budget и действующее окно с запасом до absolute. Один occupied/unresolved Build на owner/ledger, максимум три project-wide. Только exact committed/published closure с проверенным полным remote SHA. Uncertain submit не дублировать; coordinator refusals не обходить.

Ожидание делай экономным: status/Brief по возможности yield10–30с вместо1000мс с отдельным модельным возвратом за session ID. Выполняй независимую полезную работу; при простом ожидании объединяй ожидание и проверку в одном инструментальном шаге≤60с. Не создавай отдельные циклы sleep30→status→чтение ответа без новой информации. Штатные status/accounting controls и общение с владельцем сохраняй.

Примерно через час сообщи progress/charge/blocker без ожидания ответа. Продолжай, пока есть полезный шаг, время и бюджет; не останавливайся после первой исправленной ошибки. Ранний stop обоснуй после проверки независимых задач. После main никаких новых Builds/retries/гипотез; свои неотправленные requests отозвать. Дополнительные30 минут — уже начатое, Evidence, учёт, checkpoint/push. К absolute подтверди terminal/accounting либо явно оставшиеся active/unresolved с ID и разрешённым действием. Финальный остаток retire, carry0.

Evidence: `smallsort-brief BUILD_UUID` → catalogue/file ID → **`--refresh --file ID --expect-sha256 SHA`** с info/locate/position/lines/JSON pointer и нужными явными страницами по серверным next_offset/next_value_start. [Guide](EVIDENCE-READER-GUIDE.md), [примеры](EVIDENCE-READER-TASK-QUERIES.md), корневой `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md`. Lifetime16/WITHHELD устарели. Проверяй identities/coordinates/exact/complete/coverage; no-match не NOT_RUN, source PASS/exit0/integrity не independent credit. Raw/full logs/archives/Cloud Logging/локальные raw copies и GCS/download/storage/logging обход запрещены. При реальном ограничении v0.11 сообщи точные недостающие данные; admin audit отдельно. download_verified и historical verdicts не менять.

VPS — Git/hashes/static parsing и малые isolated synthetic service tests; actual preparation/extraction/compiler/decoder/refiner/verifier/full runners только Cloud. Обновляй компактный STATUS и существующие session/experiment/release/coverage records. Здесь оставь **один перезаписываемый компактный отчёт**: цель; proof до→после; обслуживание отдельно; каждый Build/гипотеза/type/candidate/результат/charge; T0/deadlines/end; own active/unresolved/requests/reservations; закрытие бюджета без carry; следующий blocker. Полную26строчную матрицу/provenance храни отдельно по ссылкам. Wall-clock не равен active agent time; резерв/retired headroom не равен расходу.

## Отчёт агента

R9 ACTIVE. T0 **2026-10-20T17:07:04Z**, main **19:07:04Z**, absolute **19:37:04Z**. Новый бюджет3600, **905spent/2695remaining**, carry0. Исходные чужие dirty policy/evidence файлы сохранены; R8 не возобновлялась.

Цель: полный P1 native-interface/equality/refinement → совместимые26/own N-false31 lifecycle. Proof до→сейчас: **0→0 закрытых obligations, independent B1/B2 credit0**. P0a/P0b на новых S1 identities имеют source NATIVE_INTENDED_PASS body+conformance; это не independent credit.

S1 `2f7b5d56-f9b6-44d1-a1fd-89f7b79870a4`, mixed: qualified Ast.sized → R-only/finalC compile → P1. Candidate `c73930175ade6efffc82c6f70a5e2d803fdc872d`, terminalFAILURE, runexit124, **905с**. Brief VERIFIED_ARCHIVE_AND_INVENTORY/outer evidence complete true; source progress26:11INTENDED_CLASSIFIED/2INCONCLUSIVE/12NOT_RUN/1OBSERVED(R7), не полная финальная классификация. [Evidence](cloud-build/sort4-caller-entry-native/A1-NATIVE-INTERFACE-R9-S1-EVIDENCE-2026-10-20.json), [26rows/provenance](cloud-build/sort4-caller-entry-native/A1-NATIVE-INTERFACE-R9-S1-MATRIX-2026-10-20.json).

Обслуживание отдельно: новая R9 registration/exact published Git closure и actual buildability установлены как source claims; P1 R-only остановился на `compiler item body is not unique`, готовится reviewed body-presence selector. Независимо admission caller binding сообщает normal/readonly semantic mismatch — проверяется actual representation. Ownfalse31 body stage events VF0, receipt/callerassertion не достигнуты. Локально actual compiler/proof не запускались; existing Cloud preflight сохраняется.

Ownactive/unresolved0; S2 ещё не отправлен. [Session](cloud-build/sort4-caller-entry-native/A1-NATIVE-INTERFACE-R9-SESSION-2026-10-20.md). Следующее действие: source-applicable fixes с независимым Luna HIGH review/dependentpins, exactpublishedclosure, штатный Cloud.
