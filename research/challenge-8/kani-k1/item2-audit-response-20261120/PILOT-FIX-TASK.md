# Задание воркеру на исправление q-пилота

Решение координатора принимаю. Runner фиксирует то, что произошло при запуске. Оценка
свойств, контролей и применимости провайдеров проводится отдельно по офлайн-чек-листу.
Сбой конкретного корня допускает переход к следующему после подтверждённой очистки.
Дрейф входов или невозможность подтвердить остановку процессов затрагивают всю кампанию.
При таком сбое остановить запуски и сохранить доступные наблюдения. [Решение координатора](FIX-DIRECTION.md) · [Офлайн-чек-лист](PILOT-ANALYSIS-CHECKLIST.md)

## Закреплённые входы и выходы

Основания — `FIX-DIRECTION.md` на `b45f7567dc38143abd8edb5e324439b9817ba750` и вердикт
`CHANGES_REQUIRED` на `9a4f2af637aeada818e2ac58241e1f3a7d806ff7`. Полные прежние пины,
roster и перечисление затронутых замечаний даны в [ревью](PILOT-REVIEW.md) и [handoff реализации](PILOT-IMPL-HANDOFF.md).

| Вход | Worktree и ветка | Родитель исправления |
| --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `61d3f7c004b2edffc6ce9da454640def72691d5e`, tree `9303586b845bee4a0f7be9d847cb6f8fdfe496b9` |
| fork control | `/root/kani-ch8-q-pilot-control-v1`, `experiment/ch8-q-pilot-control-v1` | `ba32286ee4f370593a2c9f0d8834a12d473c82d7`, tree `53b372008b70704b15a404275f81fa078ed50034` |
| Kani tool | `/root/kani-upstream-ch8-s1`, только чтение | `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Перед записью сверить ветки, HEAD, trees и чистоту worktrees, включая untracked. При
расхождении сохранить чужие изменения и указать точный blocker. Сделать по одному
локальному коммиту std и control поверх указанных родителей. Сначала закрепить std SHA
для control request. Оба коммита с `[skip ci]`, автор и коммитер
`Tiramisu-Cake <igkharin@gmail.com>`, без `Co-Authored-By`.

## Std

Меняются два файла под `library/core/src/slice/sort/shared/smallsort/verify/`.

- В `sorting_q_controls.rs` перенести `P5_SWAP_SPLIT_THRESHOLD` в `exercise_false_or`
  после ограничения геометрии и до actual `swap_if_less`. Сохранить guard
  `cover_split_threshold` и `P5_SWAP_USEFUL_RETURN` после вызова. P-5b сохраняет q=0.
  Контракт `swap_false_or_post` и мутация P-5c с `P5C_CORRUPT_QPOST` остаются прежними.
- В `sorting_q_pilot.rs` добавить самостоятельные covers отсутствия q во входе по owned
  `before`. `P1_Q_ABSENT` проверяет оба сравниваемых входных байта, `P2_Q_ABSENT` —
  сортируемый префикс `V34[1..14]`, `P3_Q_ABSENT` — inclusive span `V34[1..1+len]`,
  `P4_Q_ABSENT` — `V34[1..18]`. Сохранить остальные covers. Новые predicates используют
  прежние допустимые индексы и unwind36. Отсутствие q проверяется через cover, входы
  по нему не фильтруются.

Сохранить принятые в ревью контракты, снимки, q-домен, модели, тела и сигнатуры std,
cfg-изоляцию и точные селекторы всех семи корней. Формулировки ролей и выводов теперь
хранятся в офлайн-чек-листе. В handoff дать актуальные пути и строки новых covers и
контрольных свойств.

## Control и граница ответственности

Менять только `.github/workflows/ch8-q-pilot.yml` и
`ch8-q-pilot-control/{CI-REQUEST.json,run.py,test_run.py}`. Оставить fork guard, точный
trigger ref `uninit-ci/ch8-q-pilot-v1`, один job, прежнюю сериализацию, read-only checkout
credentials и закреплённый setup tool. Отметить в новом request схему сбора сырых наблюдений,
std/tool identities, control parent и payload hashes, полные селекторы, cfg, argv и лимиты.
Сверять фактический control HEAD с trigger SHA и деревом проверенного пакета через цепочку
review → coordinator → same-tree trigger. Request фиксирует parent и хэши остальных файлов.
Фактическое дерево и хэш самого request записываются при запуске и сверяются с handoff
перед dispatch. Это исключает самоссылку на хэш собственного дерева.

- Удалить `check_config`, сопоставление native feature set, native mode/target/stubs gate,
  `role_inventory`, `contract_role_inventory`, `control_match`, q-domain gate, таблицы
  expected roles/sites/controls в request, `QCompileMonitor` и парсинг regular stream.
  Удалить также синтетические тесты этих классификаторов. Декларации успеха, `PASS`,
  `MATCH` и qualification не входят в результаты корней. Цель P-2/P-4 ≤300 с относится
  к офлайн-оценке. Пины, целостность payload и проверка формы входного request остаются
  механизмами запуска.
- Запускать P-1, P-2, P-3, P-4, P-5a, P-5b, P-5c по одному процессу и в этом порядке.
  Exact singleton argv и закрытые normal/mutant cfg сохраняются. Включать
  `kani_smallsort_q_controls` только для P-5a/b. Использовать `verify-std`, `--exact`,
  `--jobs=1`, unwind36, object-bits12, regular output и export, прежние флаги пина
  включая `-Z unstable-options` и `--no-assert-contracts`. Сохранять фактически переданный
  argv и cfg. Запрещены свободные workflow args и унаследованные переопределения флагов.
- `std_project` на пине читает CLI `--target-dir`. Передать ему явный уникальный каталог
  внутри root temp. `CARGO_TARGET_DIR`, если используется, тоже изолировать. Развести
  временные сборочные файлы и сохраняемые наблюдения, записать фактические пути и убрать
  созданные каталоги после reap. Проверять SHA/tree и чистоту std, tool и control с untracked
  при подготовке запуска. Сборка и синтетические проверки пишут во временное дерево либо
  в предусмотренные ignored build paths. В runner не отключать проверку untracked ради тестов.
- Переиспользовать `runner.execute` для child ≤600 с, включая компиляцию, и
  `s3_runtime.supervise` для ownership/reap и внешней очистки. При таймауте сохранять
  исходный exit/signal и фактический wall с cleanup отдельно от заданного лимита. Оставить
  штатный учёт sampled RSS и существующие лимиты памяти helpers, с пометкой области замера.
  Сохранить ограниченную сборку stock tool. Убрать marker и compile subcap, а также вложенные
  campaign/outer/step/phase deadlines и расчёты резерва на пакет оставшихся корней.
  Job имеет cap ≤180 мин. Для `NOT_RUN` при исчерпании бюджета использовать одну границу
  запуска, привязанную к job, с минимальным запасом на cleanup и загрузку артефакта.
  При hard stop, который прервал и upload, запись может отсутствовать. Нельзя выдавать этот
  случай за измеренный `NOT_RUN`.

## Сохраняемые наблюдения

Набор файлов внутри bounded fork artifact — `q-pilot-raw.json` и до трёх
объявленных файлов `stdout`, `stderr`, `export` на каждый корень. Caps на корень
соответственно 16 MiB, 1 MiB и 8 MiB. Общий предел 256 MiB включает index. Ограниченный
stdout сохранять в исходном порядке, без склейки head/tail, чтобы анализ мог разобрать
полный regular inventory при удачном захвате. Перед upload проверить размер, relative paths,
обычные файлы, отсутствие symlink и точное соответствие списка членов. Не включать рабочие
каталоги, traces из других путей или полные логи CI.

| Блок `q-pilot-raw.json` | Поля |
| --- | --- |
| Запуск | Схема `ch8-q-pilot-raw-v1`, run ID/attempt/event/ref, SHA/tree/parent control, SHA/tree std и tool, хэш request/workflow, setup receipt или причина его отсутствия, фактические ограничения, причина остановки, `proof_credit=NONE`. |
| Корень | ID, selector, cfg, argv, invocation ID и временные пути, start/end, монотонная длительность child, timeout/cutoff, исходные exit code и signal, отдельно exit worker, cleanup status child и supervisor, sampled RSS и scope при наличии. |
| Файл | Относительный путь члена, размер, SHA-256 сохранённых байтов, отметка cap/truncation, причина отсутствия или ошибка чтения. Malformed JSON можно отметить исходным исключением декодирования с типом и сообщением. Корректные JSON `null`, scalar, `INCOMPLETE`, `PARTIAL` и `COMPLETE` сохранять как данные для офлайн-разбора. |

Запись `started` должна появиться при фактическом запуске. Сохранять наблюдение о завершении
child до потенциально ошибочного чтения export. Отдельно атомарно фиксировать полученное
подтверждение от supervisor. Ошибка чтения, malformed export или превышение cap не
подменяют известные exit/signal и время. На oversize сохранить только разрешённые байты
с явной отметкой либо отсутствие файла с причиной. SHA относится к сохранённым байтам.
Setup receipt, если он есть, передаётся и в fallback. Fallback сохраняет различие между
запущенным, прерванным и не запущенным корнем. Промежуточный worker record без outer receipt
оставляет очистку неизвестной. После успешной очистки локальный сбой корня и любой его exit
не прерывают остальные корни. `NOT_RUN` с причиной выставлять только тем, чей запуск не
состоялся по известной причине. Исключения сохранять с исходным контекстом, не генерируя
итоговую полноту по exit или наличию файла.

## Проверки и передача

До передачи выполнить `git diff --check` на обеих дельтах, статически проверить cfg,
границы обоих std изменений, SHA/tree/parent, список файлов и workflow/request.
Проверить форматирование изменённых Rust-файлов имеющимся rustfmt в `--check`, если
он доступен. Native setup, compile, Kani, CBMC и CI в этой стадии отсутствуют.

Точечные синтетические проверки control используют stubbed executor или малые локальные
процессы. Пройти exact argv/cfg и изоляцию обоих target paths, wrong SHA/tree и untracked
checkout, timeout/cutoff и cleanup, сохранение исходного exit при malformed/missing export,
сохранение допустимых JSON `null` и значений иной формы как байтов, caps и хэши, продолжение
после сбоя с подтверждённой очисткой и `NOT_RUN` при исчерпании бюджета. Проверять через
путь, который пишет итоговый index, включая fallback с started, но без подтверждения
supervisor. Достаточен небольшой набор для оставшихся сервисных обязанностей. Cargo,
rustc, Kani, CBMC и скрипты аудитора локально не запускать.

Передать два полных SHA/tree/parent, worktrees и ветки, hashes request/workflow/runner,
обновлённый source map контролей, exact roster, пример формата raw index из синтетической
проверки или его схему и список фактически прошедших проверок. Статус `READY_FOR_DELTA_REVIEW`
либо `BLOCKED` с причиной, `native=NOT_RUN`, `GO=NOT_GRANTED`, `proof_credit=NONE`.
Следом независимый delta review. Публикация или запуск требуют отдельного GO координатора
на точный пакет и записи в ledger.
