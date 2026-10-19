# Merge / insert_tail — текущее задание и отчёт агента

## Порядок работы с этим файлом

- Это единая точка передачи текущего задания между владельцем, координатором и агентом merge / insert_tail. Задание отражает прямое разрешение владельца; наличие файла не разрешает повторно открывать завершённую сессию.
- Координатор обновляет раздел «Задание». Исполнитель сохраняет его содержание и заполняет раздел «Отчёт агента» в этом же файле при начале, существенном результате и завершении.
- Здесь хранится компактный отчёт со ссылками. STATUS, существующие experiment/session cards, release manifests и ledger сохраняют свои назначения. Не создавать второй подробный журнал запусков и не вставлять сюда полные Brief или логи.
- Перед следующим заданием координатор читает отчёт, сохраняет завершённую редакцию файла в `task-history/<ID-задания>.md`, затем обновляет задание и очищает шаблон отчёта. Уже существующий архив не перезаписывать; сохранять Git-историю.
- Один исполнитель владеет изменениями результата. Координатор не переписывает файл во время активной сессии без согласования. Исполнитель фиксирует и публикует финальный файл в назначенной project branch.

## Задание

- **ID:** `merge-first-comparator-2026-10-18-r1`.
- **Статус выдачи:** READY; начало новой сессии фиксирует исполнитель.
- **Owner:** `merge`.
- **Project worktree / branch:** `/root/verify-rust-std-merge-origin`, `merge/incoming-origin-20261009`.
- **Tool worktree / branch:** `/root/verifast-merge-actual-glue`, `merge/actual-glue-instance-20261011`.

### 1. Цель и исходное состояние

Продвинуть существующую кампанию первого фактического comparator call в actual insert_tail: установить normal false/true и первый Continue-panic с восстановлением полных CURRENT ресурсов, проверить обязательные negatives и отдельно получить full-body diagnostic. Исправление сборки уже дало результат; не повторять его как самостоятельную цель.

Последний опубликованный docs checkpoint: `431f43f5`. Последний Build: `e3252f3a-1034-405e-bc15-d406b79f20ed`, terminal FAILURE. Точные source identities и история — в [FINAL-CHECKPOINT](cloud-build/origin-layout/FINAL-CHECKPOINT.md) и [TYPE-FIX identities](cloud-build/origin-layout/TYPE-FIX-IDENTITIES-20261018.json). Если HEAD продвинулся, изучи новые изменения; не откатывай его автоматически и не путай docs HEAD с исполненным source SHA.

По последнему обновлению Brief, сообщённому владельцем:

- `translator-build: exit 0`; exporter, decoder, console, refiner и tracked-md-compile также exit 0. Гипотеза исправления сборки для данного кандидата подтверждена.
- Ordinary normal/unwind smoke — source-reported PASS.
- Положительные helper и generated Drop caller классифицированы как bounded fragment PASS.
- Для первого comparator нет поддерживаемых записей: normal false/true, первый panic, prefix/full-body не установлены. Это НЕ означает NOT_RUN.
- Aggregate INCONCLUSIVE; причина общего FAILURE неизвестна. Сообщения о `$HOME` не установлены как причина.
- B2 остаётся открытым. Успешный refiner exit сам по себе не доказывает проверку целевого first-unwind edge.

Получить актуальный Brief обычным интерфейсом; записать его версию/provenance. Добавить уточнение к STATUS/checkpoint: прежний недостаток translator receipt уже устранён, а сведения о первом comparator всё ещё ограничены. Исторические отчёты и исходные Brief не переписывать. Не запрашивать снова уже полученное подтверждение сборки.

### 2. Первая задача: выяснить, что происходит с целевой кампанией

Без чтения raw evidence проследи точный pinned source path: profile selection → runner entrypoint → first-callback campaign → case invocation → aggregate/compact receipts → packaging для Evidence Brief. Начальные ориентиры:

- [FIRST-CALLBACK semantic card](cloud-build/origin-layout/FIRST-CALLBACK-SEMANTIC-CARD-20261017.md);
- [first-callback.py](cloud-build/origin-layout/first-callback.py);
- [admission controls](cloud-build/origin-layout/first-callback-admission-controls.py);
- [provider-overlays.py](merge/cloud-build/provider-overlays.py);
- [overnight runner](merge/overnight/run.sh).

Разделяй четыре возможности: source не вызывает кампанию; кампанию блокирует ранний выход; результаты не сохраняются/не упаковываются; результаты не представлены интерфейсом Brief. Исходники устанавливают возможный flow, но не доказывают, какой путь выполнился в старом Build.

Если Brief не даёт нужных фактов о старом запуске, сформулируй компактный запрос на отдельно разрешённый admin audit: first-comparator case IDs, execution status, failing stage/predicate, identities и причина общего FAILURE, если установлена. Такой запрос не разрешает самому читать raw evidence и не блокирует независимый source review и подготовку разрешённых исправлений.

Не правь `$HOME`, classifier или proof по догадке. Если обнаружен конкретный source defect в dispatch/runner/сохранении результатов, зафиксируй его и исправь в разрешённых границах. Для будущих запусков сохраняй компактные machine-readable receipts через существующие supported schemas и reporting path: case identity, stages/exits, source/profile binding, verdict/provenance, причина пропуска/отказа. Не подменяй неизвестный результат успешным и не изобретай новый интерфейс, который Brief не читает.

Не меняй централизованный Brief service, IAM или общий coordinator. Дефект только в представлении уже существующего evidence требует исправления отчётности/аудита, а не повторной дорогой верификации. Новый Build с конкретным исправлением runner проверяет новый кандидат; он не восстанавливает задним числом неизвестные результаты старого.

### 3. Разрешённая автономность

В основном окне самостоятельно повторяй: Brief/source diagnosis → конкретная гипотеза → минимальное исправление → статические проверки/review → обновлённые pins и публикация → Cloud Build → оценка результата.

Разрешены без отдельного согласования после каждого blocker:

- исправления proof annotations и восстановления ресурсов первого comparator в рамках существующих проверяемых правил и исходного semantic card;
- минимальные исправления сборки, source selection, campaign dispatch, runner и сохранения компактных результатов в своих файлах;
- семантически нейтральные исправления реализации существующего first-callback tool-профиля, например типизации; сам факт принадлежности к старому patch chain не разрешает новое доверенное правило;
- согласование зависимых pins, source closure и служебная регистрация этой сессии штатным механизмом.

Для каждого изменения до реализации запиши rationale, exact source applicability и затронутые gates в существующей card. Не останавливай сессию после обычного исправимого setup/proof blocker; продолжай при наличии времени и разрешённого следующего шага.

Заморожены compiler/dependencies, runtime std/алгоритм, kernel, memory/alias/layout model, prelude и trusted semantics translator/refiner. Новые правила HRTB, unwind routing, AST rewrites, широкая интеграция профиля I, generic T/ZST/arrays redesign и изменение late Cleanup требуют отдельного решения. Не ослабляй predicates ради прохождения теста.

Выход за scope верни владельцу как конкретный вопрос с evidence и вариантами; продолжай независимую работу внутри scope. Отсутствие ответа не даёт разрешения на расширение.

### 4. Точный proof target и обязательные controls

Сохрани домен semantic card: actual source insert_tail, конкретный u64 и исходная трёхэлементная обёртка, generic `F: FnMut(&u64, &u64) -> bool` с допустимыми effects/panic. Не заменяй callback чистым или непаникующим и не выдавай ограниченный домен за unrestricted std proof.

Обязательные результаты первого call:

| Путь | Что требуется |
| --- | --- |
| Normal false | Исходный early Return с полными CURRENT array/owners/F, thread/type/lifetime и caller-frame ресурсами |
| Normal true | Все исходные три ячейки и CURRENT ресурсы восстановлены перед original tail.read/guard construction |
| Первый panic | Закрыты временные reference fractions/tokens и borrows, завершён локальный lifetime, восстановлены array3/owners/F/frame; сохранён original Continue |
| Call admission | Реальные compiler FnMut/Output clauses, binder identity/order, substitutions и HRTB связаны с первым фактическим call; флаг регистрации не является доказательством |
| Official refinement | Положительно установлен first-edge Continue comparison; mutation к иному unwind action отвергнута именно нужной проверкой |

Source-linked prefix имеет явный cut перед tail.read и остаётся частичной теоремой. Full-body diagnostic сохраняет runtime statements и полные конечные normal/unwind posts; отдельно сообщает реально установленную достигнутую границу. Prefix PASS не означает full insert_tail PASS.

Сохрани resource-loss negatives, CURRENT F/cell ownership controls, HRTB/binder/Output/projection/lifetime controls и отказ применения first-call механизма к late Cleanup. Negative засчитывается только на intended stage/predicate/location; ранний setup/admission failure не заменяет resource rejection.

Сохрани обязательные B1 regressions, helpers, ordinary normal/unwind, generated Drop caller/admission/default-off, receiver/end/retirement controls. Bounded helper PASS не переносится автоматически на первый callback или B2. Late Cleanup → guard Drop → Resume остаётся отдельной незакрытой обязанностью. Даже закрытие первого callback само по себе не закрывает B2: shift/gap, loop, late panic, actual cleanup/Drop и caller posts остаются отдельными.

### 5. Identities, preflight, review и публикация

Исходный кандидат:

| Артефакт | Identity |
| --- | --- |
| Tool commit | `52ba7e2506af993007675269111a24d15406d58b` |
| Profile scope | `experimental-merge-first-callback-u64-v1` |
| Profile SHA-256 | `84949dd9b08e6eb867b9f17b3d2149dcd41b44f219bcc369e2970bf5eca90a3f` |
| First-callback patch SHA-256 | `df08af37966ef28a9667dd8b50e45afa2e14ecf9d716e78765e2233820a64bd3` |
| Translator SHA-256 | `be517cc54213ee350a0dfd6e892d2affb4bfa7d2c2a42e40232a4872bd83cc9f` |
| Исполненные proof/infra | `59a3dcaed3f3061a551fec00fd0c503a52043405` |

Сохрани исправление закрытого типа `first_fnmut_calls` и предыдущее исправление pin run.sh. Если tool не меняется, не создавай новый tool commit/profile identity ради номера сессии. Если разрешённое изменение влияет на identity, пересчитай только зависимые значения и явно свяжи старое/новое с фактическими байтами.

Все 18 строгих base hash checks сохраняются. Изменение ожидаемого хеша допустимо только для обоснованно изменённого pinned input; не вводи wildcard или autoaccept. Проверь полный ordered patch chain, реконструированный source, все profile source hashes, recipe inputs и closure/config. Исторические manifests не переписывать.

Локально допустимы Git, hashes, статическая проверка применения патчей/синтаксиса и малые изолированные служебные тесты по WORK-POLICY. Компиляция, decoder generation, source extraction, proof runners, refiner/verifier и установка build dependencies на VPS запрещены; toolchain выполняется в Cloud.

Перед Build с новым code/proof/runner diff нужен независимый reviewer: `model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации. Передай точный diff, контекст, invariants и acceptance criteria. Reviewer возвращает компактный GO/blockers по изменению и затронутым зависимостям; неизменённые части не перечитывать без причины. Более дорогие модели без отдельного разрешения запрещены. Невозможность такого review сообщить явно.

Статический GO не даёт proof credit. Чистое обновление отчёта не требует повторного code review. Каждый новый Build должен иметь опубликованный exact project/infra source и воспроизводимый кандидат.

Tool commit остаётся в локальной назначенной ветке. Публикуй полный патч/цепочку, base/tool SHAs, hashes и pins через project branch. Существующий source closure должен доставлять все байты кандидата, а не только недоступный SHA. Не создавай fork, не пушь в upstream, не меняй транспорт и не публикуй upstream PR. Чужие worktrees, commits и локальные изменения сохраняй.

### 6. Сессия 120 + 30 минут и Cloud Build

Это новое разрешение заменяет для данной сессии прежние ограничения «один Build / 960 Cloud seconds» и остановку после каждого исправимого blocker.

- Зафиксируй T0 при фактическом начале исполнения; main deadline = T0 + 120 минут, absolute deadline = T0 + 150 минут. Создание этого файла не запускает отсчёт.
- В основном окне количество последовательных Builds не ограничено. Отдельного суммарного потолка 960/3600 Cloud seconds для этой сессии нет; весь фактический расход учитывается через coordinator.
- Timeout одного Build ≤ 900 секунд. Существующий v3 coordinator: максимум три project-wide occupied queued/running/unresolved slots, один на stable owner/ledger; дополнительно соблюдай более строгие применимые ограничения, если они установлены. Не занимай несколько owner slots и не меняй общую capacity.
- Последняя сессия `567/960`, `393 retired`, предыдущие `333/960`, `627 retired` и `103/960`, `857 retired` остаются CLOSED. Историю и остатки не переносить.
- Зарегистрируй новую authorization/phase/deadlines штатным способом. Если client требует конечный числовой ceiling, зарегистрируй достаточное техническое представление временного окна с учётом reservation/rounding, сохрани расчёт. Не возвращай скрыто старый лимит 960 секунд. Это не разрешение выйти за deadline. Если штатного способа нет, сообщи конкретный blocker; не обходи отказ и не правь live ledger/coordinator вручную.
- Сохраняй unresolved-dispatch handling, exact inputs и accounting. Не отправляй дубликат при неизвестном ответе API. Изменение общего протокола, IAM, Actions/triggers не разрешено.
- Следующий Build проверяет конкретное изменение/гипотезу. Не повторяй неизменённый запуск без подтверждённого временного инфраструктурного сбоя. Неполный Brief сам по себе не основание для нового Build.
- Примерно через час сообщи краткий прогресс, число Builds, расход и blocker; ответа для продолжения в scope не требуется.

После T+120 новые Builds запрещены, включая retries и отложенные dispatch requests; штатно сними собственные ещё не отправленные запросы. Дополнительные 30 минут — завершение уже запущенного Build, Brief, учёт, освобождение собственных reservations, checkpoint и публикация отчёта. Новые эксперименты/гипотезы не начинать.

Планируй последний запуск с запасом для завершения. Если собственный Build рискует выйти за T+150, своевременно запроси отмену через coordinator и проверь terminal state. Если подтверждения к deadline нет, сохрани active/unresolved ID и факт cancel request; не удаляй reservation вручную и не заявляй ложное закрытие. Заверши сессию к T+150 без обещания фонового продолжения.

Успешная сборка и отдельный fragment PASS не завершают текущую цель. Если целевые first-comparator obligations и controls установлены раньше срока, заверши сессию с отдельным full-body frontier; не расширяй автоматически работу на поздний cleanup или интеграцию профиля.

### 7. Evidence Brief

После terminal Build используй `smallsort-brief BUILD_UUID`. Submit/status/cancel, slots и accounting — только через существующий coordinator.

Запрещено читать/скачивать полные Build/verifier logs, raw GCS evidence archives и Cloud Logging, включая локальные копии. Не обходи интерфейс через `control.py download`, `gcloud storage cp`, `gcloud logging read`, `gcloud builds log`, connectors или другие пути.

Если Brief отсутствует, неполон или недостаточен, укажи недостающие конкретные поля и запроси отдельно разрешённый admin audit. Самостоятельный raw audit не разрешён. Можно повторно получить обновлённый Brief без нового Build.

`VERIFIED_ARCHIVE_AND_INVENTORY` подтверждает целостность, не formal acceptance. Различай source-reported PASS, bounded fragment PASS, independent proof credit, B1 и B2. Не выставляй `download_verified` из Brief и не переписывай старые evidence/ledger records.

Не превращай отсутствующую запись в NOT_RUN, успешный stage exit в target proof или ожидаемый negative exit в причину общего FAILURE. Причинность, stage order и exact source binding должны иметь отдельное evidence. Synthetic service tests подтверждают работу служебного кода, не доказательство.

### 8. Завершение и отчёт

Обнови STATUS, существующие checkpoint/experiment/session документы и раздел ниже. Зафиксируй и опубликуй итог в назначенной project branch. Полные логи, raw evidence и generated build output не коммить.

Отчёт должен содержать все Builds и их цели, точные identities, новый установленный результат, ограничения Brief, первый оставшийся blocker, общий расход, собственные active/unresolved requests/reservations и конкретный следующий шаг. Полная таблица first-comparator obligations/controls может быть отдельным компактным артефактом со ссылкой здесь. Не ограничивай отчёт общим «Build FAILURE» или «сборка PASS».

## Отчёт агента

Задание `merge-first-comparator-2026-10-18-r1` завершено с незакрытыми proof obligations. Owner merge; назначенные project/tool branches сохранены.

### Сессия и checkpoint

- T0 `2026-10-18T19:04:30Z`; main deadline `21:04:30Z`; absolute `21:34:30Z`. Во время приостановки диалога окно истекло. Фактическое завершение учёта/Brief/docs по «Продолжим»: `2026-10-19T05:41:03.073779+00:00`; новых экспериментов после окна нет.
- Phase `MERGE-FIRST-COMPARATOR-R1-2026-10-18`; ledger `cloud-build/origin-layout/FIRST-COMPARATOR-R1-BUDGET-20261018.json` CLOSED. 4terminal/accounted Builds, суммарно2333Cloud seconds. Own active/unresolved/reservations нет, readyrequest отозван штатно; foreign state не менялся. Technical ceiling18960 был представлением времени для клиента, не разрешённым spend budget; остаток закрыт без carryover. Исторические567/333/103 и retired393/627/857 не менялись.
- Политики WORK-POLICY/COMPLETION-PLAN и Evidence Brief revision2026-10-17 (`584891be`) прочитаны; исходный раздел задания выше побайтно сохранён.

### Изменения и identities

1. Исправлен stale compatibility source pin: exact profile-scoped mapping v8→e232… и first-callback→d20a…; strict source/binary checks и default constructors сохранены. Added supported case classification/dispatch receipts; ранний B1matched gate сохранён. Старый e325 causeUNKNOWN; не выводился из source defect.
2. Нейтральный tool marker fix: сохранён реальный scope end, добавлен Noop с уже валидированным marker location; strict lookup сохранён. Tool52ba7e25→2a507868/profile84949dd9→566457f4.
3. После отдельного одобрения владельца20:02Z exactCURRENT18 AST recovery связывает реальные возвращённые cell values/owners, собирает array/foreach существующим foreach_append. Tool2a507868→08d6a578; profile566457f4→82973e1e. Posts/resources/CFG/kernel/model/prelude не ослаблены;5newstrictadmission negatives.
4. Последний proof-only кандидат:6checkedlength/drop facts перед callback lifetime. Tool/profile/patch не менялись.

| Последняя identity | Точное значение |
| --- | --- |
| Published proof=infra source | `a0f3b7da95ad90e64ae5ef0efcda687431696133` |
| Local tool commit | `08d6a578e00d902cb9c99aad8d6ae2020c7d728a` |
| Profile | `experimental-merge-first-callback-u64-v1` |
| Profile SHA256 | `82973e1eb17f4383b02310611cee3f023f4aa5f0a619f228838674d85e41be59` |
| First callback patch SHA256 | `4aa84aa536e98bb3a728a966fb5159e3d66cbec844cfb6700e571ed7a57920e9` |
| Translator SHA256 | `2ff7b16f326f06da6f53f6ea9227c09de441dd2ac1ab7d7f3aa5c247d6c17de5` |
| Immutable closure SHA256 | `99b8452518b453e6572bfa919fab829603749caada00b2e8131a8baf712a0d16` |

R1-SINGLETON-RELEASE-20261018.json:434176bytes/146parts/106proofpaths; all14patches deliver full source matching localtool08d6a578. Compiler nightly2026-09-25/f7575a9d unchanged. All18strictbasechecks inclrun.sh ae0aa063… preserved. Tool upstream not pushed; project branch publishes exact full patchchain. Исторические manifests/Brief/verdicts сохранены.

### Локальные проверки и независимый review

7syntheticCURRENT/service tests +4priorR1service tests PASS;14orderedpatches applied/16reconstructedfiles equaltool/14profilepins/18basepins PASS_STATIC_ONLY. No local compiler/extraction/refiner/verifier. Independent reviewer GPT-6 Luna High, fork none, без вложенной делегации; final singleton GO in R1-SINGLETON-REVIEW-20261018.json. StaticGO не proof credit. Уточнение classifier для5newnegatives требует exactexit1/intendedguard/location и отвергает timeout/launch/fatal; старые controls не удалены.

### Все Builds и результаты

| UUID | proof=infra / release | Гипотеза и результат | Charge |
| --- | --- | --- | --- |
| `2f7ba4a0-1c94-4c05-a33f-0a959a340b06` | `762932d3` / R1-RELEASE | compatibility/dispatch; FAILURE, campaign reached, translator List.find Not_found | 528s |
| `b4c78447-2c45-4548-98e9-18d00bf86132` | `251a83ad` / R1-MARKER-RELEASE | markerNoop; FAILURE, firstcall reached, missingown(entryxshead) | 579s |
| `e7b74165-b8ac-4d40-b541-396540104e08` | `e87f0d09` / R1-CURRENT-RELEASE | ownerapprovedCURRENTrejoin; FAILURE, secondforeach missingtailchunk | 598s |
| `5f668cd9-fb34-4570-ad1c-4b97abbb36d0` | `a0f3b7da` / R1-SINGLETON-RELEASE | singletonfacts; FAILURE20:45:53Z, distinctprefix/fullbodyfrontiers below | 628s |

Все запускались с полной обязательной матрицей, timeout900, без дублей/unchangedretry; последний закончился до maindeadline. Обработка результатов использует исключительно smallsort-brief и разрешённый derived Reader receipt/index, без raw evidence.

### Последний evidence и оставшийся blocker

- Brief **v6**, Processor0.7.0, receipt/index SHA linkage проверен; R1-BUILD4-* сохраняют исходный Brief, provenance и bounded derived observations. Brief SHA2075eda4…; indexSHA60c851a0…. VERIFIED_ARCHIVE_AND_INVENTORY — целостность, не принятие proof.
- Translator/exporter/decoder/console/refiner builds, tracked-md preparation/compile: individual observed exit0. Сборочная гипотеза подтверждена для данного кандидата, отдельно от proof.
- Prefix/fullbody: sourceexact/HRTB/localContinue/official-first qualifier sourceTrue; exporter/decode/refinement0,VF1. Actualfirstcall observedsourceTrue. Это необходимые admission observations, не доказательство всех obligations.
- **Первый текущий blocker prefix:** `verified/lib.rs(214,17-23): Placeholders are not allowed here`. Separate source-linked prefix остаётся INCONCLUSIVE. Точный statement не выведен Processor: diagnosticlineWITHHELD; Reader доступен.
- **Отдельный fullbody blocker:** `verified/lib.rs(203,42-48): No matching heap chunks: points_to<u64>(tail0, _)`; boundedcontext/referenceSHA сохранены. Source actual_read_lineTrue, shift/update/lateFalse; выполнение tail.read/guard успешно не доказано. Прежний foreach blocker пройден на этих наблюдаемых путях.
- Normalfalse / normaltrue / firstContinuepanic: joint sourceflagFalse; отдельные успешные branchreceipts не установлены. Полное CURRENT восстановление/F/frame не заявляется доказанным.
- Fourresource-loss negatives и admissiongroup: **source explicitNOT_RUN_PREFIX_PREREQUISITE_FAILED**. HRTB/binder/Output/projection/lifetime controls, first-edge mutant, lateCleanup refusal и5CURRENT controls не получают intendednegative credit.
- B1 selectedDrop sourceall_matchedTrue, receiver/end/retirement4sourceEXPECTED_CONTROL; ordinarynormal/unwindsmokesourcePASS; helper/Drop positives boundedfragments. Generated admission/defaultoff nested details не извлечены Processor; parentmatched не переносится в genericproof.
- Whole-Build causeUNKNOWN, stageorderNOT_ESTABLISHED, lastcompletedUNKNOWN; присутствие отдельного sourcecausalrecord неизвестно. Readerindex доступен; это не Readertransportfailure. Полная матрица и attribution: [R1-OBLIGATIONS](cloud-build/origin-layout/R1-OBLIGATIONS-20261018.md).
- **B2 OPEN**, нового independent proofcredit нет. LateCleanup→Drop→Resume и полныйshift/gap/loop/callerposts не закрыты. Никакие старые results автоматически на новыйprofile не перенесены; download_verified не выставлялся.

### Следующий шаг

В новом явно разрешённом временном окне сначала статически сопоставить prefix214 placeholder с pinnedtemplates и подготовить минимальное annotation correction с прежними posts, review и sourcepreflight. Отдельно восстановить доступ к tail для fullbody без потери CURRENT ownership; не расширять trustedmatcher автоматически. Если точный prefixstatement нельзя восстановить статически, нужен отдельно разрешённый boundedadminaudit толькоBuild5f668cd9: verifiedprefix214±4/sourceSHA; для общейпричины — causalreceipt/failedcommand/exit, если есть. Rawfallback/newBuildрадиreporting запрещены. Текущее окно не перезапущено сообщением «Продолжим».

Итоговый файл и относящиеся записи фиксируются и публикуются отдельным docscheckpoint; егоSHA — commit, содержащий эту финальную редакцию. Sourceкандидат остаётся a0f3b7da, отдельно от docsHEAD.
