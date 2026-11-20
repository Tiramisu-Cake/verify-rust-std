# Задание независимому ревьюеру q-пилота

## Цель

Провести независимое чтение локального кандидата q-пилота до решения о запуске. Проверить закреплённые версии исходников, инструмента и control, сохранение обычного поведения и границ безопасности, точные домены провайдеров и отрицательных контролей.

Это только source/control review. Ревьюер не запускает пилот, не выдаёт GO или qualification и не приписывает proof credit. Работа начинается из свежего контекста: verdict автора не считается свидетельством. Native результаты, если они появятся позже, остаются `NOT_RUN` в этом ревью.

## Зафиксированные inputs

- STD base: `7b31b060b90ce286e94547993f6a698c549bc5fa`
- Candidate branch: `experiment/ch8-q-pilot-v1`
- KANI tool: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Control base: `65a9ea656a4b5f1e66f7b31eceffb5eefeba7541`
- Control candidate добавляет `.github/workflows/ch8-q-pilot.yml` и файлы `ch8-q-pilot-control/`
- Локальная control-ветка: `experiment/ch8-q-pilot-control-v1`
- Будущий trigger ref: `uninit-ci/ch8-q-pilot-v1`

Сверить фактические commit/tree identities кандидатов и их баз с этими pins и с реализационным handoff в [PILOT-IMPL-TASK.md](PILOT-IMPL-TASK.md) и описанием lane в [PILOT-LIGHT-LANE.md](PILOT-LIGHT-LANE.md). Зафиксировать проверенные commit IDs. При несовпадении остановить оценку затронутой части как `BLOCKED`, не подменять входы.

Контекст постановки: [NEXT-STAGE.md](NEXT-STAGE.md), [RESPONSE-RU.md](RESPONSE-RU.md) §§2–3 и [SAT-CADICAL-RESULTS.md](SAT-CADICAL-RESULTS.md). Не читать предыдущий запрещённый аудит или raw CI evidence.

## Объём проверки

Проверить diff и связанные исходники/контрольные файлы по следующим пунктам:

1. **Scope и identity.** Изменён только согласованный source/control scope. Установлены точные базы, candidate commits, tool pin, workflow и control-file identities. В отчёте перечислены просмотренные файлы и commit IDs.
2. **Cfg и обычный путь.** Новый функциональный режим включается только через `kani_smallsort_q_pilot`, а отдельные мутации — только через `kani_smallsort_q_controls`. Обычный cfg сохраняет sorting bodies, generic signatures, CFG и исходные safety obligations. Нет случайного включения S2 count/assumed attrs, потери safety requires или взаимодействия cfg, дающего незащищённую конфигурацию.
3. **Runtime и q-модель.** Проверить, что runtime comparator/algorithm не читают q и не ветвятся по нему, а q используется только спецификациями. Для каждого позитивного provider q независимо и свободно выбирается как полный `u8`, сохраняется между вызовами и не фильтруется входами/assumptions. Проверить exact activation guards, owned pre-state captures, frame/modifies для q и данных, безопасные captures и отсутствие чтения неинициализированных значений. Для условного q-monotone Pre проверить, что он ровно тот же в provider и consumer.
4. **Providers и домены.** Сопоставить root names, атрибуты, реальные вызовы, геометрию, длины, `T/F`, Pre, frame и `q_domain` с §3 `RESPONSE-RU.md` и implementation task. В частности, проверить V34 и 45 пар для P-1, вызов sort13 на `v[1..18]` с frame хвоста для P-2, tails 1–16 и требуемые covers для P-3, а также один и тот же q и реальные insertion tails 13–16 в P-4. Не считать имя/регистрацию PFC доказательством исполнения или покрытия.
5. **Negative controls и gate.** Проверить, что P-5a — false-OR mutant с `q:any`, а P-5b отличается только `q=0`; gate обязан отвергать успешный фиксированный домен с `Q_DOMAIN_NOT_UNIVERSAL` и принимать корректную декларацию `all_u8` для P-1. Проверить, что P-5c портит выход harness-only путём после реального network body и имеет предусмотренный свидетель/порог. Убедиться, что controls изолированы от positive cfg и не могут стать providers.
6. **Runner/control invariants и ошибки.** Сверить lifecycle/caps helpers `s3_runtime.supervise`, `runner.execute`, проверку initial export и совпадение stock export с полным regular inventory. Проверить выделенный trigger/ref, singleton selection, раздельные cfg, identity, реальные caps, сохранение exit и cleanup при отказах. Оценить подготовленные автором синтетические результаты для timeout, partial/missing/null/wrong type, несовпадения identity и NOT_RUN. Убедиться, что при этих исходах исследовательский результат остаётся неопределённым, а record сохраняет причину.
7. **Граница вывода.** Универсальный по q пост даёт порядок и мультимножество в заявленном байтовом домене при выполнении связей с провайдерами. При одном фиксированном q из пороговой сводки следует только свойство индикаторов. Проверки merge/panic, UB, других типов, компараторов, длин и геометрий остаются за пределами пилота. Итог ревью фиксирует native invocation, performance и qualification как `NOT_RUN`.

Сверять точные имена roots, домены и expected outcomes с `RESPONSE-RU.md` §3 и `PILOT-IMPL-TASK.md`. Проверить, что `ch8-q-pilot-control/CI-REQUEST.json` соответствует source cfg и доменам в handoff, а runner сверяет тот же request.

## Ограничения

- Только чтение исходников, конфигурации, документации и уже подготовленных artifacts.
- Не запускать CI/build, workflow, tools, verifier, compiler, тесты, scripts, эксперименты или native roots.
- Не менять файлы, не создавать commit, не отправлять сообщения и не открывать внешние PR.
- Не читать предыдущий запрещённый audit или raw CI evidence. Если для проверки не хватает допустимого свидетельства, отметить пробел и оставить пункт `NOT_RUN` или `BLOCKED`.

## Результат ревью

Вернуть одно из решений: `APPROVE`, `CHANGES_REQUIRED` или `BLOCKED`. `APPROVE` означает только, что данный source/control diff прошёл перечисленное статическое review; это не разрешение запуска и не qualification.

В отчёте указать:

- решение и проверенные commit IDs;
- краткий итог по каждому из семи пунктов выше с путями и точными местами в файлах;
- для каждого замечания: наблюдаемое поведение, затронутый root/gate, требуемое исправление и основание из этого задания или связанных документов;
- перечень `NOT_RUN` для native proofs, control invocations и qualification. Отдельно указать, какие синтетические результаты автора были просмотрены;
- оставшиеся caveats и блокирующие неизвестные.

Не делать вывод `GO`, не запускать или бронировать lane и не менять ledger. Передать только review-результат владельцу/координатору.
