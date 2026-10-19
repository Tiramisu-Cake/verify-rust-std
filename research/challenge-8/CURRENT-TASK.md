# Merge / insert_tail — текущее задание

**ID:** `merge-first-comparator-2026-10-19-r2`. **Статус:** ACTIVE; сессия начата 2026-10-19T11:57:00Z.

Этот файл содержит только последнее задание и один актуальный отчёт. Исполнитель обновляет раздел «Отчёт агента» на месте, а не добавляет новые дневники/повторные отчёты в конец. Итог — не более одной страницы плюс таблица Builds и ссылки на существующие артефакты. Перед следующим заданием координатор сохраняет законченную редакцию отдельно и полностью заменяет этот файл. Архив предыдущей сессии: [r1](task-history/merge-first-comparator-2026-10-18-r1.md); читать его целиком без конкретной необходимости не нужно.

## 1. Цель и исходное состояние

Доказать source-linked prefix первого фактического comparator call: normal false, normal true и первый Continue-panic с полным CURRENT восстановлением; выполнить зависимые negatives/admission controls. Отдельно восстановить доступ к tail перед original tail.read в full-body diagnostic и установить следующую проверенную границу. Prefix не заменяет полный insert_tail; B2 остаётся открытым до всех его обязательств.

- Owner `merge`; project `/root/verify-rust-std-merge-origin`, branch `merge/incoming-origin-20261009`.
- Tool `/root/verifast-merge-actual-glue`, branch `merge/actual-glue-instance-20261011`.
- Docs checkpoint `4c744fc5`; последний исполненный proof=infra `a0f3b7da95ad90e64ae5ef0efcda687431696133`.
- Build `5f668cd9-fb34-4570-ad1c-4b97abbb36d0`: FAILURE; toolchain stages exit0. Prefix/fullbody exporter/decode/refinement exit0, verifier exit1. Это разные результаты, не formal acceptance.
- Prefix: `verified/lib.rs(214,17-23): Placeholders are not allowed here`.
- Fullbody: `verified/lib.rs(203,42-48): No matching heap chunks: points_to<u64>(tail0, _)` у tail.read; успешное выполнение read/guard ещё не доказано.
- Normal false/true/panic отдельно не доказаны; joint source flag false. Четыре resource-loss negatives и admission group имеют source-reported `NOT_RUN_PREFIX_PREREQUISITE_FAILED`.
- B1/helper/ordinary normal-unwind сохраняют ограниченные source-reported результаты. Причина общего FAILURE и порядок стадий не установлены; сообщения `$HOME` не считать причиной.

Последняя сессия CLOSED: 4 Builds / 2333 Cloud seconds; own active/unresolved/reservations отсутствовали по checkpoint. Исторические accounts не открывать. Новая сессия начинается по этому заданию, не задним числом.

## 2. Порядок работы

1. Проверь branch/HEAD/status и собственный coordinator state. Сохрани чужие изменения. Прочитай актуальные AGENTS, [Evidence Reader guide](EVIDENCE-READER-GUIDE.md), релевантные WORK-POLICY/runbook и [semantic card](cloud-build/origin-layout/FIRST-CALLBACK-SEMANTIC-CARD-20261017.md). Старые окна/budgets в card исторические; действует раздел 5 ниже.
2. Получи актуальный Brief последнего Build. Через catalogue/search и точечные fragments попробуй установить точный prefix statement214, его source hash, и контекст fullbody203. Используй реальный file ID из данного Build; не скачивай generated source целиком. Если отчёт старого формата или нужные данные не сохранены, укажи конкретное ограничение. Отсутствие фрагмента не означает NOT_RUN.
3. Сопоставь statement с pinned исходниками шаблонов `first-callback.py` / `actual-insert-tail-b2.py`. Допустим статический разбор; не запускай локально prepare/extractor/runner для генерации proof source. Выбери минимальную коррекцию placeholder на основании доказанного соответствия, а не одного номера строки. Не заменяй неизвестное значение произвольной константой и не удаляй assertion/post.
4. Для fullbody проследи физическое владение tail после CURRENT rejoin. Проверь гипотезу, что ячейка находится внутри восстановленного array predicate и перед read нужны существующие проверяемые split/open операции. Это гипотеза по исходникам, не установленный диагноз. Сохрани framed cells, CURRENT значения/owners/F и ресурсы обеих normal-веток и unwind.
5. После source preflight и review запускай полную кампанию; анализируй Brief/адресные Reader observations, исправляй следующий blocker внутри scope. Каждый Build проверяет конкретный новый кандидат/гипотезу. Не повторяй неизменённый запуск без подтверждённого временного инфраструктурного сбоя.

Если существенных фактов не хватает даже после адресных Reader-запросов, подготовь узкий запрос на административное дополнение проекции старого Build. Это не разрешает самому читать raw evidence. Продолжай независимую source/proof подготовку, где фактов достаточно; новый Build только ради недостающей отчётности запрещён.

## 3. Разрешённые изменения и invariants

Разрешаю самостоятельно исправлять proof annotations, placeholder binding и раскрытие/сборку уже имеющихся ресурсов в prefix/fullbody и связанном wrapper, используя существующие checked lemmas. Разрешены минимальные исправления своих runner/fixture/compact-result handling, pins и регистрации этой сессии. Перед изменением запиши гипотезу и затронутые obligations в существующей experiment card.

Сохрани уже одобренную [CURRENT18 recovery](cloud-build/origin-layout/R1-CURRENT-RECOVERY-DECISION-20261018.md): возвращённые значения получают реальные binders, а не приравниваются к entry xs. Не создавай ресурсы из предположений, numeric address equality или пустоты u64.own; физическое ownership ячеек обязательно. Проверяй реальные объявления pinned lemmas, включая foreach_append.

Tool/translator/refiner semantics и exact CURRENT18 matcher заморожены. Если proof-only изменение невозможно выразить без нового AST admission, сначала верни конкретный минимальный diff/proposal и требуемые controls владельцу; не расширяй matcher автоматически. Ранее разрешённое изменение уже входит в baseline, но не даёт общего разрешения на новые правила.

Не менять runtime std, generic signatures, compiler/dependencies, kernel, memory/alias/layout model, prelude, HRTB rules или unwind CFG. Не ослаблять contracts, assertions, ownership/leak/refinement checks. Не добавлять purity/no-panic или entry=CURRENT equality. Не переносить first Continue recovery на late Cleanup; поздний cleanup/Drop и интеграция профиля I вне текущего scope.

Домен: actual insert_tail, конкретный u64 и исходная array3 wrapper, generic F с допустимыми effects/panic. Source-linked prefix имеет прежний явный cut до tail.read; fullbody сохраняет runtime и полные исходные normal/unwind posts. Все три исхода первого callback должны восстановить array/owners, CURRENT F, thread/type/lifetime и caller frame; ни loan, ни lifetime не могут утечь.

Обязательны четыре resource-loss negatives, HRTB/Output/projection/binder/lifetime controls, official first-unwind mutant, late-Cleanup refusal и пять CURRENT18 admission negatives. Negative засчитывать только на intended stage/predicate/location. Сохрани B1, helper, ordinary normal/unwind, generated Drop/admission/default-off и receiver/end/retirement regressions. Не сокращай матрицу, чтобы получить зелёный aggregate.

## 4. Baseline, review и публикация

| Артефакт | Закреплённая identity |
| --- | --- |
| Tool | `08d6a578e00d902cb9c99aad8d6ae2020c7d728a` |
| Profile scope | `experimental-merge-first-callback-u64-v1` |
| Profile SHA-256 | `82973e1eb17f4383b02310611cee3f023f4aa5f0a619f228838674d85e41be59` |
| First-callback patch SHA-256 | `4aa84aa536e98bb3a728a966fb5159e3d66cbec844cfb6700e571ed7a57920e9` |
| Translator SHA-256 | `2ff7b16f326f06da6f53f6ea9227c09de441dd2ac1ab7d7f3aa5c247d6c17de5` |

Сверь [последний release manifest](cloud-build/origin-layout/R1-SINGLETON-RELEASE-20261018.json). Сохрани compiler nightly-2026-09-25/f7575a9d, 14-patch source closure, 18 strict base checks и прежний run.sh pin. Для proof/runner изменений обновляй зависимые source/config identities; не меняй tool/profile ради новой сессии. Ни wildcard, ни автоматическое принятие нового хеша не разрешены.

Перед новым code/proof/runner кандидатом нужен независимый review нового diff и затронутых dependencies: один `gpt-6-luna`, `high`, `fork_turns=none`, без вложенной делегации. Передай точный scope, invariants и ожидаемые проверки; нужен GO до submit. Не перечитывай неизменённое целиком без причины. Более дорогие модели не разрешены.

Локально — Git, hashes, статический разбор/применение патчей и малые изолированные synthetic service tests. Compiler, extraction, decoder generation, refiner/verifier и proof runners — только Cloud. Не устанавливай build dependencies. Проверь closure/config и опубликуй exact project/infra SHA до submit.

Tool branch остаётся локальной; полный pinned patch chain доставляется существующим source closure из project branch. Remote fork/tool push не нужен. Не менять transport, общий coordinator, IAM/Actions/triggers, не публиковать upstream и не трогать чужие worktrees/ledgers.

## 5. Новая автономная сессия: 120 + 30 минут

- T0 — фактическое начало исполнения. Main deadline T0+120 минут, absolute deadline T0+150 минут; запиши UTC в отчёте и session card. Истечение времени/пауза диалога не перезапускает окно.
- В основном окне число последовательных Builds не ограничено; прежние лимиты один Build / 960 или 3600 Cloud seconds не действуют для этой новой сессии. Расход полностью учитывается coordinator. Timeout отдельного Build ≤900 секунд.
- Сохраняй действующие project-wide slots и максимум один occupied/unresolved Build на stable owner/ledger. Регистрация phase/authorization/числового ceiling — штатным механизмом. Если client требует ceiling, явно обоснуй его как техническое представление временного окна с reservation/rounding; это не разрешение выйти за deadlines. Общий протокол/live ledger вручную не менять, отказы не обходить.
- До каждого submit сверяй main deadline. Не дублируй unresolved dispatch. Примерно через час дай короткий progress update и продолжай в scope без ожидания ответа.
- После T+120 новые Builds/retries/отложенные submissions запрещены. Отзови собственные неотправленные requests. Оставшиеся 30 минут — дождаться уже запущенного Build, получить evidence, закрыть учёт, сохранить/опубликовать checkpoint и отчёт; новые эксперименты не начинать.
- Планируй последний Build с запасом. При риске выхода за T+150 своевременно запроси cancel через coordinator. Если terminal confirmation нет, честно запиши active/unresolved ID и cancel request, не удаляй reservation и не заявляй ложное закрытие. Заверши сессию к absolute deadline, без обещания фонового продолжения.
- Все старые accounts/retired headroom остаются закрытыми. Если целевые prefix+controls закрыты раньше, установи разрешённый fullbody frontier и заверши без лишних запусков; полную late-cleanup миссию автоматически не открывай.

## 6. Evidence и критерий завершения

Используй установленный `/usr/local/bin/smallsort-brief`: Brief → адресные catalogue/search → JSON pointer/короткий text fragment. Следуй [guide](EVIDENCE-READER-GUIDE.md): coverage, file ID, index hash, pagination/provenance. Не читать полные/raw logs/archives/Cloud Logging или локальные копии, не собирать их по фрагментам. Недостаток сохранённой проекции → узкий запрос audit/перепроцессинга, без нового Build ради чтения.

Целостность, stage exit0, source flags, bounded fragments и independent proof credit различаются. Отсутствующая запись не означает NOT_RUN. Не выставляй download_verified по Reader, не переписывай исторические evidence/ledgers. Не назначай причину общего FAILURE без подтверждения.

Цель сессии закрыта, когда свежий source-linked prefix с полными posts и обязательные controls имеют достаточное evidence, а fullbody отдельно показывает результат tail.read и следующую подтверждённую границу. Отдельные normal false/true/panic claims должны иметь основания; успешный qualifier/trace их не заменяет. B2 не закрывать только по prefix или доступу к tail. При deadline/scope blocker сохрани частичный результат честно.

Обнови существующие STATUS/checkpoint/obligations и компактный отчёт ниже; зафиксируй/опубликуй в назначенной project branch. Не дописывай сюда старые отчёты, полный Brief или дневник каждой попытки. История/подробности остаются в артефактах и Git.

## Отчёт агента

- **Статус:** ACTIVE / частичный результат; ожидается точечное дополнение Reader для prefix214.
- **T0 / main / absolute UTC; phase / ledger:** 2026-10-19 11:57:00 / 13:57:00 / 14:27:00; `MERGE-FIRST-COMPARATOR-R2-2026-10-19`; [отдельный ledger](cloud-build/origin-layout/FIRST-COMPARATOR-R2-BUDGET-20261019.json).
- **Исходный HEAD / policy revision / сохранённые чужие изменения:** `4c744fc5b10dbbd489649782968cd099b76e48fc`; WORK-POLICY2026-10-10 + owner Reader2026-10-19 (исходные локальные правки). AGENTS/runbook/policy/Brief/CloudREADME/guide/task-history сохранены; чужие worktrees/closed accounts не менялись.
- **Исправления, identities, release/review:** только fullbody proof: binder CURRENT array, checked split(begin,2), open tail singleton перед original read. Runtime/posts/first-call markers/prefix неизменны. Tool `08d6a578`, profileSHA `82973e1e…`, patchSHA `4aa84aa5…`, translatorSHA `2ff7b16f…`, compiler pins frozen. [Exact release](cloud-build/origin-layout/R2-RELEASE-20261019.json), [Luna High GO](cloud-build/origin-layout/R2-REVIEW-20261019.json), [14patch/16files/14pins/18base staticPASS](cloud-build/origin-layout/R2-SOURCE-PREFLIGHT-20261019.json); 7existing+2new synthetic tests PASS, локальных proof/extraction запусков нет.

| Build UUID | Source/manifest и гипотеза | Terminal / ключевой результат Brief | Charge |
| --- | --- | --- | --- |
| c78529d0-f18b-4d13-9060-6517cde03cd5 | proof=infra `014c3238dcf386b58ab2b1304fce80c8f4c3ac0d`; CURRENT tail split/open | FAILURE12:14:38Z; fullbody next error207 unsupported address; prefix214 placeholder | 590s / execution589s |

- **Prefix normal false / normal true / first Continue-panic:** отдельно не установлены; joint sourceflagFalse, VF1. Exact statement214 ещё недоступен; speculative placeholder fix не сделан.
- **Fullbody tail.read / следующая граница:** прежний points_to blocker больше не наблюдается; trace readTrue, затем error207:49–52 “Taking the address of this expression is not supported.” у следующего original guard statement. Наблюдаемый путь, без whole-read/guard/fullbody theorem; shift/update/late traceFalse.
- **Negatives / regressions:** 4resource+admission group явно sourceNOT_RUN_PREFIX_PREREQUISITE_FAILED; HRTB/firstunwind/lateCleanup/CURRENT18 не зачтены. SelectedDrop и receiver sourceall_matchedTrue, helper bounded positive+3expected, smoke sourcePASS; nested projection ограничения сохранены.
- **Evidence provenance/coverage:** [Build1 result](cloud-build/origin-layout/R2-BUILD1-RESULT-20261019.json), [полная obligations-таблица](cloud-build/origin-layout/R2-OBLIGATIONS-20261019.md). Index `68182b14…`, archive verified, catalogue1281/content386; это integrity/source observations, не formal acceptance. OldBuild после ownerreprojection index `3e3e6bad…`, prefix sourceSHA `dd2e5689…` подтверждён preparation, но .rs unsupported/no fragment210; log bounded. [Точный запрос/ограничение](cloud-build/origin-layout/R2-BASELINE-READER-LIMIT-20261019.json). Raw fallback/download_verified нет; whole-Build causality UNKNOWN.
- **B2 / formal credit / blocker:** OPEN / нового независимого credit нет; prefix214 exact source/type binding ещё не установлен, отдельный fullbody frontier207.
- **Учёт:** 1Build/590s accounted, собственных active/unresolved/reservations нет; сессия AUTHORIZED, request только coordinator. Технический ceiling18960 — представление окна, не новый spend budget/carryover.
- **Время/причина окончания; checkpoint:** сессия продолжается; [STATUS](STATUS.md) обновлён, исходный кандидат опубликован.
- **Следующий шаг:** получить разрешённую bounded projection prefix210–218/sourcehash, сделать минимальный evidence-backed proof/wrapper fix и LunaHigh review перед новым Build; tool/matcher не расширять.
