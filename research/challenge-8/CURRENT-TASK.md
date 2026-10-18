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

Начато исполнение 2026-10-18T19:04:30Z. Новых Builds пока нет; исторические accounts закрыты и не используются.

### Сессия

- Статус: ACTIVE — R1 Build submitted; awaiting terminal/Brief.
- ID задания: `merge-first-comparator-2026-10-18-r1`.
- T0 / main deadline / absolute deadline (UTC): `2026-10-18T19:04:30Z` / `21:04:30Z` / `21:34:30Z`.
- Project/tool HEAD: `431f43f54060558330489dd9190bfc97ca31f55e` / `52ba7e2506af993007675269111a24d15406d58b`; Evidence Brief policy revision2026-10-17 / commit584891be. WORK-POLICY/COMPLETION-PLAN и current assignment приняты.
- Phase `MERGE-FIRST-COMPARATOR-R1-2026-10-18`, owner merge; новый отдельный ledger зарегистрирован. Только временное окно, без скрытого старого960s ceiling.
- Project clean, кроме предоставленного untracked CURRENT-TASK.md; назначенный tool clean на52ba7e25. Задание выше сохранено побайтно, другие worktrees не изменяются.

### Диагноз, изменения и review

- Актуальный Brief e3252f3a получен через smallsort-brief; v6 schema/Processor0.7.0 установлены через Reader receipt/index, SHA linkage проверен; provenance/time/SHA сохранены в R1-BASELINE-BRIEF-PROVENANCE-20261018.json. Все build milestones exit0; smoke и bounded positives source-reported PASS; first-comparator records отсутствуют, NOT_RUN не выводится.
- Flow прослежен до packaging. B1 matched gate предшествует first-callback.run. Найден stale compatibility source pin: gate требует e232… для любого профиля, выбранный профиль и exact tool blob требуют d20a…. Это source defect, не установленная runtime-причина старого Build. Штатный Reader index доступен; per-question source/Processor/Reader ограничения записаны в R1-BASELINE-INDEX-ASSESSMENT-20261018.md. Старый runtime cause UNKNOWN; raw audit не выполнялся.
- До реализации rationale/source applicability/gates записаны в FIRST-CALLBACK-SEMANTIC-CARD-20261017.md, раздел R1. План: profile-scoped strict hash mapping с сохранением v8, compact classification/dispatch receipts через существующие schemas. Ни tool/profile, ни trusted semantics не меняются.
- Project proof=infra `762932d3158f7c5dcab0294a2a6c815c3bcd1a19`, release `ab26b351`; tool52ba7e25/profile84949dd9/patchdf08af37 unchanged. R1-RELEASE-20261018.json:106proofpaths,14patches,432081byte immutable payload/145parts, SHA87a6b062…. Published exact source checked.
- Reporting-path follow-up reviewer: packaging всех payload подтверждён; поддержка Reader classifications вне /cases/ не установлена доступными исходниками. Receipt absence не заменяет execution evidence и не оправдывает новый Build только ради reporting.
- Статические проверки:14patches/16reconstructed files/14profilepins/18strictbasepins PASS;4synthetic service tests PASS. Независимый Luna High review GO, source hashes в R1-REVIEW-20261018.json; tool/profile unchanged.

### Запуски

| Build UUID | Точный кандидат / manifest | Изменение или гипотеза | Terminal status | Brief / установленный результат | Charge |
| --- | --- | --- | --- | --- | --- |

| `2f7ba4a0-1c94-4c05-a33f-0a959a340b06` | `762932d3` / R1-RELEASE-20261018.json | profile-scoped compatibility pin; full mandatory matrix + dispatch receipts | submitted | terminal/Brief pending | reserved960s |

Один Build; дубликаты не отправлялись. Результаты сопровождать provenance и ограничениями; полный Brief не вставлять.

### Итог evidence

- Tool buildability: —
- Ordinary normal/unwind smoke: —
- Helper/generated Drop bounded fragments и B1 regressions: —
- First actual FnMut/HRTB admission: —
- Normal false / normal true / first Continue-panic recovery: —
- Source-linked prefix / separate full-body frontier: —
- Official first-unwind comparison и mutant: —
- Resource-loss / HRTB / binder / late-Cleanup и остальные mandatory controls: —
- Подробная компактная таблица obligations/results/provenance: —
- B2 и formal credit: —
- Причина общего FAILURE, если установлена; иначе UNKNOWN: —
- Первый подтверждённый blocker / запрос на недостающее evidence: —

### Закрытие и следующий шаг

- Число Builds / общий Cloud charge / остаточные reservations: —
- Собственные active/unresolved IDs, отмены, requests и состояние ledger: —
- Время завершения UTC и причина окончания: —
- Source checkpoint / published docs checkpoint или отметка о последующем publication commit: —
- Непроверенные изменения и местонахождение кандидата: —
- Конкретный следующий шаг и требуется ли новое разрешение: —
