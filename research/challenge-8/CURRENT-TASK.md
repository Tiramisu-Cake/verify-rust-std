# Select / sort4 — текущее задание

## Задание

- **ID:** `select-p0a-parser-compatibility-2026-10-19-r2`; **статус:** READY, исполнение ещё не начато.
- **Owner:** `select-sort4`.
- **Worktree:** `/root/verify-rust-std-select-night`.
- **Project branch:** `research/night-select-sort4-cloud-2026-10-09`, fork `Tiramisu-Cake/verify-rust-std`.
- **Разрешение:** новая сессия по поручению владельца: 120 минут работы + до 30 минут завершения, **3600 Cloud секунд** по принятому новому процессу. Число последовательных Builds не ограничено в пределах времени и счёта. Старые счета закрыты.

Ты стартуешь без контекста. Проверь worktree/branch, HEAD и dirty diff; сохрани чужие изменения. Прочитай `AGENTS.md`, [WORK-POLICY](WORK-POLICY.md), [ITERATION-PROCESS](ITERATION-PROCESS.md), [Cloud runbook](cloud-build/README.md) и [краткий guide v0.9](EVIDENCE-READER-GUIDE.md). Полный справочник нужен только для конкретной неясности. Всю историю задания перечитывать не требуется.

### Цель и исходная точка

**Устранить конкретный P0a parser blocker с сохранением строгой проверки входа, получить новый результат P0a и перейти к полному P1 native-interface/equality gate.** После prerequisites выполнить обязательную 26-строчную матрицу, включая собственный N-false31 lifecycle. Диагностику и сборку учитывать отдельно от закрытых proof obligations.

Последний docs checkpoint: `428cb3da`; последний исполненный source/infra: `6f3abaa45b97345cf467a7fc24a8b7d39ab09af7`; Build: `87df47e4-002b-432c-bc87-56612136b448`. Docs HEAD не считать исполненным кандидатом.

Прочитай [последний отчёт v0.9](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-READER-V09-2026-10-19.md), соседний JSON только для нужных provenance/селекторов, и [R5 manifest](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R5-RELEASE-2026-10-18.json). Установлено:

- Собственные R-only/final-C build stages exit 0 и свежий R-only reference receipt подтверждены предыдущим Reader-чтением; P1 equality acceptance из этого не следует.
- Все 26 source statuses: **8 INTENDED_CLASSIFIED / 5 INCONCLUSIVE / 13 NOT_RUN**. R2–R7 явно классифицированы, gate=true, proof_credit=false; повторно запрашивать их не нужно.
- P0a начал execution: source-constructor `InventoryError: decoded VfMir parse failed: invalid quoted string at byte 9362`. P1 INCONCLUSIVE, N-false31 NOT_RUN; A1/A2 открыты, нового formal credit нет.
- `parser_input_binding=NOT_ESTABLISHED`, `causal_status=UNKNOWN`: неизвестны normal/readonly вызов, точный вход/SHA, преобразование и реальный литерал. Синтетический escape не является диагнозом реального отказа.
- Выполнены восемь targeted-запросов старого Build; остаток общей квоты неизвестен. Переиспользовать готовые ответы.

### Работа в этой сессии

1. **Разобрать минимальный reproducer по исходникам.** Начальные места в `cloud-build/sort4-caller-entry-native/`: `a1-synthetic-inputs.py::_string`, `a1-compiler-inventory.py::_find_vfmir/observe`, `a1-focus-backend.py` вокруг чтения normal/readonly MIR. Проверить pinned формат decoder output и преобразования до парсера. Python str index, ошибочно названный byte, не переносить на UTF-8 byte offset.
2. **Использовать существующее evidence.** Сохранённые результаты → Reader → нужный refresh с exact SHA. Не угадывать файл для позиции 9362. Если binding отсутствует в старом evidence, зафиксировать предел; повтор одинакового запроса его не создаст. При необходимости подготовить компактный admin request, без raw fallback.
3. **Разрешена минимальная диагностика своего parser/runner.** При отказе сохранять normal/readonly вызов, относительный путь и SHA исходных байтов, SHA точного parser input и явные преобразования, Unicode/UTF-8 координаты, исключение и короткий безопасный фрагмент с лимитом размера. Использовать существующие summary/diagnostic artifacts, доступные через Brief/Reader. Сохранять исходный отказ/partial progress; missing/null/error не превращать в успех. Полные dumps и новый отчётный сервис не нужны.
4. **Если старое evidence не позволяет восстановить вход**, разрешён узкий Cloud preflight нового диагностического кандидата в существующей lane для воспроизведения P0a и проверки обработки ошибки. Это адресное исключение данной сессии к запрету нового Build только ради недостающей диагностики. Не повторять прежний неизменённый полный Build и не читать старый raw archive. Результат нового отказа должен быть доступен компактным интерфейсом. Диагностический запуск не даёт proof credit.
5. **После установления реального литерала разрешено узкое исправление строкового декодирования** в служебном `a1-synthetic-inputs.py`, обоснованное точной грамматикой pinned decoder output. До реализации записать semantic rationale, допустимые escape/Unicode/byte случаи, влияние на identities и отрицательные controls. Декодирование обязано сохранять точное значение; malformed/неподдержанные случаи отвергаются. Запрещены permissive fallback, eval, игнорирование errors, потеря символов и нормализация, склеивающая identifiers. Если формат неоднозначен, подготовить конкретный proposal и остановить зависимое исправление.
6. **Проверять целевой путь рано.** Parser/source-binding preflight → P0a → достижимые P1 и обязательные gates по зависимостям. Разрешён минимальный branch-local preflight режим существующей lane с точными closure/pins. Ранний отказ сохраняется с причиной пропуска зависимых случаев; независимые controls остаются. Для итогового acceptance нужна вся исходная матрица на совместимых финальных identities и собственные требуемые receipts.

Продолжай после обычных исправимых ошибок в scope без нового разрешения. Объединяй связанные исправления по evidence; повтор без новой гипотезы допустим только при подтверждённом временном infra failure. Если получена лишь диагностика, следующий шаг — точный parser fix. Новая архитектура или изменение proof semantics вне описанной строковой совместимости требуют отдельного решения.

### Границы и проверки

- Scope: описанные parser compatibility, error reporting, минимальные runner/preflight fixes и зависимые profile/source/service pins. До submit — независимый review нового diff: **GPT-6 Luna HIGH**, `model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`; без вложенной делегации и дорогой замены. Передай diff, pinned формат, invariants и tests; нужен GO. При недоступности reviewer подготовь всё остальное и сообщи blocker.
- R/C tool patches сохранить побайтно: R `d99a5ed229533132b8292c5fc70ea93dbe261e9f76c2a0fcc6d6723e796454ca`, C `e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e`. Toolbase, 43 pre-R patches, compiler, exporter и decoder — по R5 manifest без изменения. Новый профиль связывает только разрешённые изменения. Проверка применения патчей не равна компиляции.
- Не менять kernel/translator/refiner, memory/alias model, std runtime, generic domain, contracts, shape/identity/source-binding/admission predicates, P1 equality, negative acceptance или guards/лимиты парсера. Исследование и конкретный proposal вне scope допустимы, реализация требует решения владельца.
- На VPS только static checks и малые изолированные synthetic service/parser tests. Проверить подтверждённые классы literals, malformed escapes, quotes/backslashes, Unicode, усечения и прежние валидные случаи; для диагностики — normal/readonly, partial/null/missing/error. В Git только допустимый минимальный fixture, без raw logs. Полный preparer, actual extraction, compiler/decoder/refiner/verifier и Cargo — Cloud-only.
- До Build: GO, подходящие checks, точные committed proof/infra SHAs, source closure и новые pins. Commit/push в назначенную project branch разрешены, полный remote SHA проверить. Сохранять чужие изменения; без reset/force-push/merge/upstream PR. Tool branch не требуется. Coordinator/IAM, новые lanes и межсессионный cache не менять.

### Окно, учёт и Evidence

При фактическом начале запиши T0, main=T0+120 минут, absolute=T0+150 минут; штатно зарегистрируй новую phase/ledger. **3600 секунд — новый отдельный Cloud ceiling** по conservative charge/reservation правилам. Старые 2115 spent/16845 retired не переносить. Это выдача запланированного бюджета первого цикла нового процесса и замена безлимитного Cloud-счёта прежнего задания. Свою сессию регистрировать штатно, shared live state вручную не менять.

Timeout Build ≤900 секунд и не больше доступного бюджета/окна с envelope. Один occupied/unresolved Build на owner; для Select сохраняется более строгое ограничение ≤2 занятых project slots. Не обходить отказ coordinator и не повторять неизвестный submit. Примерно через час сообщить target progress, Builds/charge и blocker, затем продолжать в scope. После T+120 новых Builds/гипотез/отложенных dispatch нет; продление только для уже начатого шага, evidence, учёта и публикации. Последний запуск планировать до absolute deadline; при необходимости cancel через coordinator, unresolved честно отразить.

После terminal Build: `/usr/local/bin/smallsort-brief`, **Brief → Reader → узкий refresh → admin audit при оставшемся пробеле**. Refresh разрешён обычному агенту; 16 общих резервирований на Build, ошибки тоже могут расходовать их. Соблюдать [v0.9 guide](EVIDENCE-READER-GUIDE.md), expected SHA, координаты/coverage/provenance/cache reuse. Полные/raw logs, архивы, Cloud Logging и локальные копии не читать/не скачивать. Не ставить `download_verified` и не переписывать исторические verdicts/ledgers. Exit 0 и archive integrity не равны formal acceptance.

Обнови компактный STATUS, существующие session/experiment/release документы и **один перезаписываемый отчёт ниже**. Новые отчёты в конец этого файла не добавлять. На закрытии зафиксируй и опубликуй результат; после закрытия работа требует нового задания. История сохранена в [архиве](task-history/select-sort4-ocaml-buildability-2026-10-18-r1.md), читать её целиком не нужно.

## Отчёт агента

- **Статус:** IN_PROGRESS. T0 `2026-10-19T16:06:59Z`, main `19:36:59Z`, absolute `20:06:59Z`; end —.
- **Исходный checkpoint:** docs `e29c28972b96158d01f54193da0498cb5813f676`; executed source `6f3abaa45b97345cf467a7fc24a8b7d39ab09af7`. Branch/worktree проверены; исходные owner policy edits сохранены.
- **Обязательство до → после:** P0a parser9362 → диагностика готовится; P1 INCONCLUSIVE, N-false31 NOT_RUN, matrix8/5/13; A1/A2 открыты, formal credit0.
- **Диагноз/гипотеза:** старые8targeted responses не связывают input; повтор старого запроса не поможет. Новый P0a preflight сохранит actual normal/readonly/path/rawSHA/inputSHA/transform/coordinates/decoder cause/192-character window без изменения parser grammar и predicates.
- **Review/проверки:** подготавливаются; submit до GO запрещён.
- **Builds:** нет. Cloud0/3600, active/reservations нет собственных.
- **Следующий шаг:** synthetic error-path checks, Luna HIGH review, committed closure, опубликованный diagnostic preflight.
- **Подробности:** [session card](cloud-build/sort4-caller-entry-native/A1-PARSER-SESSION-2026-10-19.md).
