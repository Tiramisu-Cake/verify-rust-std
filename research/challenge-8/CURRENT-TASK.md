# Select / sort4 — текущее задание и отчёт агента

## Порядок работы с этим файлом

- Это единая точка передачи текущего задания между владельцем, координатором и агентом Select / sort4. Задание ниже отражает прямое разрешение владельца в разговоре; само наличие файла не разрешает повторно открывать завершённую сессию.
- Координатор обновляет раздел «Задание». Исполнитель сохраняет его содержание и заполняет раздел «Отчёт агента» в этом же файле при начале, существенном результате и завершении работы.
- Здесь хранится компактный отчёт со ссылками. Существующие STATUS, experiment/session cards, release manifests и ledger остаются своими источниками данных; этот файл их не заменяет. Не помещать сюда логи или полные dumps Brief.
- Перед следующим заданием координатор читает отчёт, сохраняет завершённую редакцию этого файла в `task-history/<ID-задания>.md`, затем обновляет задание и очищает шаблон отчёта. Если архив уже существует, его не перезаписывать. Сохранять также Git-историю.
- Один исполнитель владеет изменениями результата. Координатор не переписывает файл во время активной сессии без согласования. После завершения исполнитель фиксирует и публикует файл в назначенной project branch.

## Задание

- **ID:** `select-sort4-ocaml-buildability-2026-10-18-r1`.
- **Статус выдачи:** READY; начало новой сессии фиксирует исполнитель.
- **Owner:** `select-sort4`.
- **Worktree:** `/root/verify-rust-std-select-night`.
- **Project branch:** `research/night-select-sort4-cloud-2026-10-09`.

### 1. Цель и исходное состояние

Устранить ошибки компиляции текущего R-кандидата без изменения его семантики, получить собственный успешный R-only reference receipt, затем проверить финальный C-кандидат и существующую полную 26-строчную матрицу. Сборку, результаты отдельных gates и formal credit учитывать раздельно.

Исходный terminal checkpoint: `e3837f41`; точные ранее исполненные proof/infra identities находятся в [checkpoint](cloud-build/sort4-caller-entry-native/A1-OCAML-TYPE-CHECKPOINT-2026-10-18.md) и [release manifest](cloud-build/sort4-caller-entry-native/A1-OCAML-TYPE-RELEASE-2026-10-18.json). Если HEAD продвинулся, сначала установи состав новых изменений; не откатывай его автоматически и не путай docs HEAD с исполненным source SHA.

Последний Build: `7987e81f-cfc9-435b-8078-996cf7d2ae27`. По обновлённому Brief, сообщённому владельцем:

- translator:6884: actual `D.rvalue`, expected `string`; pinned source соответствует паттерну `D.Ref r` внутри `check_type`;
- R-only native-reference build завершился с exit 2;
- разобраны 102/102 stage records, без пропусков; отдельная запись `console-build: exit 0` не устанавливает успешную сборку именно нового R-only кандидата;
- порядок стадий остаётся неизвестным;
- все 26 строк — source-reported `NOT_RUN`; formal credit отсутствует;
- устранение прежних ошибок `D.Type` и `unused_mut` отдельно не подтверждено.

Получение expected type больше не требует административного аудита. Получи актуальный Brief обычным интерфейсом, сохрани компактную ссылку/provenance и добавь уточнение к текущему STATUS/checkpoint, не переписывая исторический Brief и прежние наблюдения. Полнота разбора stage records не означает полноты proof evidence.

### 2. Разрешённая автономность и границы

В основном окне самостоятельно повторяй цикл: Brief → гипотеза → минимальное исправление → статические проверки/review → новые pins и опубликованный кандидат → Cloud Build → оценка результата.

После каждого compiler blocker новое разрешение не требуется, пока исправление относится к:

- ошибкам компиляции/типизации в текущем R-кандидате;
- минимальным связанным исправлениям сборочного сопряжения и согласованности pins;
- служебной регистрации именно этой разрешённой сессии через существующий механизм, без изменения общего протокола coordinator.

Необходимость каждого изменения объясняй в существующей experiment/session card. До следующего Build проверяй связанные места и объединяй обоснованные исправления одного класса. Не делай механический рефакторинг всего translator.

Без отдельного решения нельзя менять trusted semantics, kernel, memory/alias model, prelude/refiner rules, контракты, admission predicates, compiler/dependency versions, C-патч или семантику G-gates. Нельзя сокращать матрицу, ослаблять negatives, normal/unwind posts, ownership/leak/refinement checks или сужать исходный generic domain. Runtime std и алгоритм не менять.

Если для продвижения нужно выйти за эти границы, представь конкретный вопрос владельцу и продолжай полезную независимую работу в scope. Отсутствие ответа не даёт нового разрешения. Не закрывай сессию после обычной исправимой compiler ошибки.

### 3. Первое исправление и обзор связанных мест

Проверь pinned определения decoder и вызывающие стороны `check_type`. Основной кандидат:

```ocaml
let rec check_type scope (ty : D.ty) =
```

В ветке `D.Adt` проверь необходимость аннотации аргумента:

```ocaml
List.iter (fun (arg : D.generic_arg) ->
  match arg.D.kind with
  ...
) adt.substs
```

Это направление исправления, а не доказанный компилятором результат. Не подгоняй функцию под `D.rvalue` или `string`: ожидаемый тип установи по назначению, pinned определениям и всем использованиям.

Проведи source review добавленного текущим R-патчем OCaml-кода на неоднозначные record labels, одноимённые конструкторы и промежуточные match results без достаточного type context. Дополнительные точечные аннотации разрешены при обосновании выбранного типа. Сохрани match arms, условия отказа, порядок обхода, regions и binder identities.

Сохрани два прежних удаления `unused_mut` и аннотацию `D.generic_arg_kind` в `normalize_required_arg`. Не выдавай сохранение исправления за подтверждение его компиляции.

### 4. Кандидат, identities и публикация

Исходные identities для сравнения:

| Артефакт | SHA-256 |
| --- | --- |
| Полный R-патч | `e7ef10e7d532670482741fa108b5faa5b605f1697875e042ce25f1cc81ce4cb6` |
| C-патч, сохранить побайтно | `e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e` |
| Profile | `e8afe608713051e5e6f1e9191095846887c47d635980d4a5aac0be7888331de0` |
| R-after / C-before translator | `7b9ae6bfcc056cf5b1ade002c867157a36cc992535d2baf40b9dd10203c433c3` |
| C-after translator | `72f4f0b83d3c565edde5c9bbb688ac12a6d21ce94d149fff37c22a5555ac639d` |

Разрешено обновлять полный R и все действительно зависимые patch/profile/source/service identities. Прежняя фиксация identities снимается только в разрешённой области. R-before, exporter, compiler, decoder и 43 pre-R patches сохраняются.

Перед каждым Build:

1. Проверь diff относительно предыдущего кандидата и сохранность не затронутых pins.
2. Восстанови исходники статически: закреплённая база → pre-R → новый полный R → неизменённый C. Это проверка применения патчей, не запуск compiler/source extractor.
3. Пересчитай полный R hash и R-after/C-before/C-after. Хеш overlay не заменяет хеш полного R.
4. Проверь source closure/config и точную привязку будущего Build к кандидату.
5. Зафиксируй и опубликуй source/infra checkpoint в назначенной project branch, проверь remote SHA.

Отдельная удалённая tool branch не обязательна, если существующий source closure доставляет полный исправленный source с проверяемой идентичностью. Не создавай fork, не публикуй в upstream и не меняй транспорт самостоятельно. Если существующий транспорт не доставляет кандидат, зафиксируй конкретный blocker до submit.

Сохраняй чужие и ранее существовавшие правки, включая локальные Evidence Brief docs. Не коммить их случайно вместе с кандидатом, не делай reset/force-push и не меняй чужие worktrees.

### 5. Review и локальная проверка

Для первоначального исправления и последующих изменений кода используй одного независимого reviewer: `model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`. Передай ему точный diff, pinned контекст, границы и ожидаемый компактный GO/blockers. Вложенная делегация запрещена. Более дорогие модели не разрешены.

Reviewer проверяет типизацию, связанные места, отсутствие семантических изменений, R/C composition, pins и gates. Повторный review охватывает новый diff и затронутые зависимости; неизменённые части повторно не исследовать без причины. До submit нужен GO для действующего изменения кода; чистое обновление отчёта повторного code review не требует. Если Luna недоступна, сообщи ограничение; не заменяй её более дорогим агентом автоматически.

Локально допустимы чтение/правки, Git, hashes, статический разбор, проверка применения патчей и малые изолированные служебные тесты по WORK-POLICY. Compiler, decoder generation, source extraction, proof runners, refiner и verifier выполняются только в Cloud. Не устанавливать build/verifier dependencies на VPS.

### 6. Окно, учёт и Builds

Это новое разрешение владельца заменяет для данной сессии прежние ограничения «один Build / 960 Cloud seconds» и остановку после каждого нового compiler blocker.

- Зафиксируй T0 при фактическом начале исполнения, main deadline = T0 + 120 минут, absolute deadline = T0 + 150 минут. Не считай временем начала момент создания этого файла.
- В первые 120 минут количество последовательных Builds не ограничено; отдельного суммарного потолка 960/3600 Cloud seconds для этой сессии нет. Все расходы учитывать через coordinator.
- Timeout одного Build ≤ 900 секунд. Один occupied/unresolved Build на stable owner/ledger. Для этого направления сохраняется более строгое ограничение не более двух занятых проектных Build-слотов, даже если общий coordinator поддерживает три.
- Исторический счёт `405/960`, `555 retired`, а также предыдущие `433/960`, `527 retired` и остальные закрытые счета не менять; остатки не переносить.
- Новую авторизацию/phase/deadlines зарегистрируй штатным способом. Если client требует конечный числовой ceiling, используй предусмотренный механизм регистрации лимита, достаточного для всего разрешённого окна и его reservation/rounding правил; явно запиши расчёт. Не возвращай скрыто старый лимит 960 секунд. Это техническое представление временной авторизации, а не продление окна. При отсутствии штатного способа сообщи конкретный blocker; не обходи отказ и не меняй live ledger/общий coordinator вручную.
- Сохраняй слоты, reservations, точные inputs, charge rules и unresolved-dispatch handling. Не создавай owner aliases, не сбрасывай историю, не дублируй submit при неизвестном ответе API.
- Каждый следующий Build проверяет конкретное изменение или обоснованную гипотезу. Повтор неизменённого кандидата допустим только при подтверждённом временном инфраструктурном сбое. Недостаток Brief сам по себе не основание для нового Build.
- Примерно через час дай короткое обновление о результате, числе Builds, расходе и blocker; продолжение в scope не требует ответа владельца.

После T+120 новые Builds не отправлять, включая retries и отложенные dispatch requests. Штатно сними собственные ещё не отправленные запросы. Дополнительные 30 минут предназначены для завершения уже запущенного Build, Brief, accounting, освобождения собственных reservations, checkpoint и публикации отчёта. Не начинай новые эксперименты или гипотезы.

Планируй последний запуск так, чтобы успеть завершить мониторинг и учёт до T+150. Если собственный Build рискует выйти за абсолютный deadline, своевременно запроси отмену через coordinator и проверь terminal state. Если terminal confirmation к deadline нет, честно зафиксируй активный/unresolved ID и запрос отмены; не удаляй reservation вручную и не заявляй ложное закрытие. Сессия заканчивается к T+150, без обещания фонового продолжения.

### 7. Что должен проверять Build

Сохраняй существующую полную проверочную конфигурацию:

1. Новый R-only exporter/console и собственный reference receipt.
2. Финальный C-кандидат.
3. Неизменённые 26 строк, полный P1 и own-pair N-false31 lifecycle с установленным порядком выдачи/использования receipts.

Не сокращай запуск до compilation-only. Старый reference receipt не заменяет новый. Если setup останавливает downstream gates, отрази фактическую полноту evidence. После исправления сборки не объявляй A1/A2 закрытыми автоматически. Если новая ошибка проверки требует изменения вне разрешённого scope, подготовь диагноз и запрос владельцу.

Цель достигнута только при достаточном evidence для заявленного результата. Успешная сборка — промежуточный результат. Если вся цель достигнута раньше срока, заверши сессию без лишних запусков.

### 8. Evidence Brief — обязательный интерфейс

После terminal Build используй `smallsort-brief BUILD_UUID`. Статус, отмена, слоты и учёт — через существующий coordinator.

Не читай и не скачивай полные Build/verifier logs, raw GCS evidence archives и Cloud Logging, включая уже имеющиеся локальные копии. Не обходи Brief через `control.py download`, `gcloud storage cp`, `gcloud logging read`, `gcloud builds log`, connectors или другие пути.

Если Brief отсутствует/неполон/недостаточен, перечисли нужные поля и запроси отдельно разрешённый административный аудит. Raw fallback не разрешён. Обновлённый Brief можно получить повторно обычным интерфейсом без повторного Build.

Различай source claims, corroborated diagnostics, исполненные gates, B1 bounded evidence и B2 full-target proof. `VERIFIED_ARCHIVE_AND_INVENTORY` подтверждает целостность, не proof acceptance. Не устанавливай `download_verified` по Brief и не переписывай исторические evidence/ledger records.

Неизвестный результат не превращать в PASS или NOT_RUN. Последний допустим при соответствующем evidence с указанием source provenance. Нулевой exit без привязки к конкретному кандидату/стадии не закрывает его gate; порядок стадий не выводить из количества разобранных records.

### 9. Обязательное завершение

Обнови STATUS и существующие checkpoint/experiment/session документы. В разделе ниже оставь компактный самодостаточный отчёт с точными ссылками на подробности. Зафиксируй и опубликуй его в назначенной project branch. Полные логи и generated build output не коммить.

Обязательно перечисли все Builds этой сессии, identities кандидатов, цель каждого запуска, результат Brief, общий расход, состояние собственных requests/reservations, первый оставшийся blocker и конкретный следующий шаг. Отдельно отрази R-only receipt, финальный C, 26 строк, P1, N-false31 и A1/A2. Если сборка пройдена, но proof evidence недостаточен, скажи это прямо.

## Отчёт агента

### Сессия

- Статус: ACTIVE — исходники и служебная регистрация, первый Build отправлен.
- ID задания: `select-sort4-ocaml-buildability-2026-10-18-r1`.
- T0: `2026-10-18T18:59:16Z`; main deadline `20:59:16Z`; absolute deadline `21:29:16Z`.
- Исходный project HEAD/remote: `e3837f4110f8713d00ba2e0f4bb7284b578831ae`. Прочитаны branch-local WORK-POLICY/STATUS и локальная owner Evidence Brief policy 2026-10-17; существующие незакоммиченные policy/docs сохраняются.
- Owner `select-sort4`. Новая регистрация с отдельным ledger готовится; старые счета405/555 и433/527 закрыты и не меняются.
- Обнаружены семь изменённых tracked policy/docs и untracked EVIDENCE-BRIEF.md, CURRENT-TASK.md. CURRENT-TASK.md включается в публикацию по этому поручению; остальные не коммитятся.

### Изменения и review

- По pinned source `check_type` вызывается только с `D.decode_ty`/полями ref/slice/tuple, ADT substitutions и generic argument Type, следовательно параметр — `D.ty`; у ADT.substs элементы `D.generic_arg`. Готовятся две локальные аннотации. Arms, отказы, обход и regions/binders сохраняются.
- Обзор остальных R-added OCaml мест выполняется. Два удаления unused_mut и прежняя D.generic_arg_kind сохраняются; их успешная компиляция пока не утверждается.
- R1: полный R `d99a5ed229533132b8292c5fc70ea93dbe261e9f76c2a0fcc6d6723e796454ca`; R-after/C-before `ffacadc74de9dded1e50e9b9a71f75a905cf97c7c823427cf7044494e87d052d`; C-after `a11741f096eb2e1808cadcb8a49eeeb33117630ae6c141d0202af22b14a9b8c3`. C побайтно прежний. [Source check](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R1-SOURCE-CHECK-2026-10-18.json).
- Регистрация новой phase `SORT4-A1-OCAML-BUILDABILITY-2026-10-18-R1`, owner/ledger отдельно. Технический ceiling18960=9000wall+9000rounding headroom+960reservation; deadlines ограничивают сессию, число последовательных Builds не ограничено. Служебные6 synthetic checks PASS. Обзор R-added OCaml завершён; других обоснованных неоднозначных мест не найдено. Luna HIGH review **GO**; committed closure/config **PASS**. Точный proof/infra`ff7fbd1daa9b89f74ec79c313ad27f6bd80f5b53`, release[R1](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R1-RELEASE-2026-10-18.json).

### Запуски

| Build UUID | Точный кандидат / manifest | Изменение или гипотеза | Terminal status | Brief / установленный результат | Charge |
| --- | --- | --- | --- | --- | --- |
| `92524a3d-fec8-4e74-a902-271f791e8bb7` | `ff7fbd1daa9b89f74ec79c313ad27f6bd80f5b53` / [R1 release](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R1-RELEASE-2026-10-18.json) | Две expected-type аннотации, полный R-only→C→26 | FAILURE | [Brief](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R1-BRIEF-2026-10-18.md): R-only и final-C exit0; P0a unclosed delimiter, original/lib.rs156 | 415s |
| `ae9fd22f-a143-4a4f-9d7c-2911ec1ad042` | `28cd86597b07e6c2726cf1c391cfdfbd28997a98` / [R2 release](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R2-RELEASE-2026-10-18.json) | Два delimiter fix в fixture, R/C прежние; полный R-only→C→26 | FAILURE | [R2 Brief](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R2-BRIEF-2026-10-18.md): tool stages exit0, P0a unknown feature internal_features | 401s |
| `20180c22-c6e9-49d5-9819-1e88aa703d35` | `5651bd99099a102de077c241139fb48235e8c326` / [R3 release](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R3-RELEASE-2026-10-18.json) | Удалён unsupported feature из fixtureheader; полный R-only→C→26 | FAILURE | [R3 Brief](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R3-BRIEF-2026-10-18.md): R/C stages exit0, runner KeyError positive_cases | 421s |
| `729160af-7f20-4a8a-b238-cc8aa077cc35` | `864fe65f21b5ca381b9417726e7f509453de91ae` / [R4 release](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R4-RELEASE-2026-10-18.json) | Tagged success/error-result wiring, predicates прежние; полный R-only→C→26 | FAILURE | [R4 Brief](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R4-BRIEF-2026-10-18.md): namedR/C exit0, runner KeyError path | 433s |

Отправлен первый Build; source/infra/release опубликованы до submit, remoteSHA подтверждён. [Refreshed baseline Brief](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-BASELINE-BRIEF-7987E81F-2026-10-18.md): actualD.rvalue/expectedstring,102/102 records; исходный Brief сохранён. Expected-type admin audit больше не нужен, прежние unknowns не повышены.

### Итог evidence

R1: R-only и final-C named stages exit0; own reference receipt требуется pinned flow между ними, но его содержимое/hash отдельно не раскрыты Brief. P0a normal/readonly/refinement exit1; proof outcome не установлен. Остальные26/P1/N-false31 UNKNOWN, поскольку Brief не содержит per-row verdicts; неизвестное не превращается в NOT_RUN.
A1/A2 OPEN, formal credit отсутствует.

### Закрытие и следующий шаг

Сессия активна,2Builds/415s accounted +960s reserved. Следующий шаг — минимальное исправление синтаксической сборки fixture: OBSERVER_SUFFIX не закрывает функцию observer. Подготовка review и нового полного Build в разрешённом scope; R/C не меняются.

### Ход работы — R1 terminal и R2 гипотеза

- R1 успешно прошёл обе named tool-build стадии; compiler blocker6884 не останавливает новую сборку. Полнота receipt evidence ограничена Brief.
- Статическое чтение `_observer`: signature открывает функцию, guard открывает loop/if; P0c и N-false31 suffix закрывают только if/loop. Отсутствует финальная `}` функции, затем следует исходный P1 caller. Это согласуется с unclosed delimiter; точная причинность нескольких Cloud failures пока UNKNOWN.
- R2: добавить только завершающую скобку в оба suffix literals как минимальный syntax/build-assembly fix. Assertions/cuts/target functions/source std/C/G/матрица не меняются. Source extractor/fixture constructor локально не запускался.

- R2 подготовлен: два delimiter literal fix, статический AST/literal разбор PASS без запуска construct/extractor; повторная43pre-R/R/C source-only реконструкция PASS, R/C иcompiler/decoder/exporter неизменны. Profile`e8ee4cd419549931f52085252811fa0016320fd1bef31bb227da416091eecf8c`; helper`5fe5e65c8150ca583b37e7458b1da504ed46668da0a8413390e9f183f0d755d3`. Зависимые pins обновлены;6служебных checks PASS, exact-diff Luna HIGH **GO**, committed closure/config **PASS**. R2proof/infra`28cd86597b07e6c2726cf1c391cfdfbd28997a98`; [release](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R2-RELEASE-2026-10-18.json).

- R2 Build`ae9fd22f-a143-4a4f-9d7c-2911ec1ad042` отправлен после публикации`da099c42`; config`06fe4403335574cef498ae2576a4067a16dc35fd1941867e0cbad412989242a4`; terminal evidence pending.

- R2 terminal: обе named tool stages exit0; P0a compiler unknown feature`internal_features`,original/lib.rs1:53. Новый R3 удаляет только неподдерживаемый feature entry из fixtureheader, без allow-lint/check изменений. R/C/compiler/decoder прежние. Reconstructed43pre-R/R/C PASS; review/closure pending.

- R3 reviewed exactdiff **GO**, committed closure/config **PASS**: source/infra`5651bd99099a102de077c241139fb48235e8c326`, sourcepayload`b983837d2e8551da2fe0f1cd521998d1e859bc15049a6df1bdb6115a6b14065e`,170substitutions. [R3 release](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R3-RELEASE-2026-10-18.json). Два terminal Builds,816s accounted,active/unresolved none перед следующим submit.

- R3 Build`20180c22-c6e9-49d5-9819-1e88aa703d35` принят после публикации`2fc75621`; config`2aea241075e39d448dad17e7a263c389922617203b0bdda6432d4b19ed43b7e1`;816s accounted +960reserved.

- R3 terminal: R/C named stages и отдельные export/decode exit0; wrapper KeyError`positive_cases`. R4 исправляет tagged success-record consumption и4связанных fallback selections. Proof/admission/receipt predicates неизменны; failedobservations остаются, независимые rows используют существующий partial progress. 6synthetic classifier cases и source-only43pre-R/R/C PASS. Ни run(), ни proof/compiler/constructor локально не вызывались. Exactdiff review/closure pending.

- R4 exact-diff Luna HIGH **GO**, committed closure/config **PASS**: source/infra`864fe65f21b5ca381b9417726e7f509453de91ae`,sourcepayload`af552c4ce77e97fdfcd2db39290ee9188dc166d876695089f864e31a283a4d01`;170substitutions. [R4 release](cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R4-RELEASE-2026-10-18.json).

- R4 Build`729160af-7f20-4a8a-b238-cc8aa077cc35` принят после публикации`8870728b`; config`5b9394f5c702c46ff9ee09026834587660e8fecf981a2768149abf1e3a8d0153`;1237s accounted+960reserved. Идентификатор получен тем же submit, повторной отправки не было.

### Промежуточный отчёт около T+60 минут

-4Builds отправлены,3terminal/1237Cloudseconds accounted; R4`729160af-7f20-4a8a-b238-cc8aa077cc35` ACTIVE с960reserve. Старые счета не менялись.
- R-only и финальный C named build stages exit0 в R1/R2/R3; это подтверждение сборочных stages, не proofacceptance. Own reference receipt contents/hash пока отдельно не доступны Brief.
- OCaml typecontext, fixture delimiters и unsupported feature исправлены; R4 исправляет service success/error discrimination. Все code diffs прошли Luna HIGH GO и committedclosure.
- Full26/P1/N-false31/A1/A2 пока не установлены. Продолжение в scope до20:59:16Z,absolute21:29:16Z; новых permissions/бюджета не добавлено.

- R4 terminal: namedR/C exit0, partialexport/decode0; runner`normal_entry["path"]` KeyError2082. Статический producer всегда включаетpath, но consumerdefaults{} проходят Mapping-only guard послеP0aerror. Исправление availability/dereferenceguard готовится, без подстановкиpath или повышенияfailedgate; 1670s accounted за4Builds.

- R5 объединяет string-path availability guards для partialMIR preparation/decoded/controls и Mapping guards дляnullable first/identity structures. 8synthetic parser cases PASS, все `_need` AST byte-equivalent;43pre-R/R/C source-only PASS. Никакой path/evidence/успех не подставлен; отсутствующие dependent inputs не исполняются и не получаютcredit, остальные строки продолжаются. Review/closure pending.
