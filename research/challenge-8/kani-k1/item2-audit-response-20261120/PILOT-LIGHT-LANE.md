# Исследовательская дорожка q-пилота

Основание — решения владельца в [NEXT-STAGE.md](NEXT-STAGE.md) на
`543d32cccc81c9ff71752642caeb11a6ade74733`. Ниже спецификация для реализации и ревью.
Запуск требует отдельного GO координатора на проверенные commits и запроса с семью корнями.

## Workflow и runner

Добавить отдельный `.github/workflows/ch8-q-pilot.yml` в fork `Tiramisu-Cake/kani`.
Точка отсчёта control — `65a9ea656a4b5f1e66f7b31eceffb5eefeba7541`, tree
`09938d27a127351f5c51b6c9f451602d797a1c0f`. Workflow S4P3 в этом дереве обслуживает
`uninit-ci/ch8-s4p-*`. Новый workflow слушает только push в `uninit-ci/ch8-q-pilot-v1` в
указанном fork, с `permissions: contents: read`, одним job на `ubuntu-24.04` и существующей
группой сериализации `ch8-s2-fork` с `cancel-in-progress: false`. Эта группа дополняет учёт
запусков у координатора. Она не резервирует слот и не заменяет GO.

Выбор отдельного workflow обусловлен тем, что `ch8-s2.yml` и `s4p3_campaign.py` привязаны
к прежним cfg, inventory и приёмочному пакету. В новом каталоге `ch8-q-pilot-control/`
держать `CI-REQUEST.json`, `run.py` и `test_run.py`. Из наследуемого `ch8-s1-control/`
использовать `s3_runtime.supervise` для ownership/reap/cleanup и внешних лимитов,
`runner.execute` для child, output caps и bounded capture, `runner.group_memory_budget`
для headroom. Compile monitor следует интерфейсу `poll`/`finish` из `runner.CompileMonitor`
с проверкой initial-export marker. Исходный класс привязан к старому `REQUEST_PATH`, поэтому
q-runner записывает собственные identities и request hash. Переиспользовать порядок setup/build stock tool из S4P3
(`.github/actions/setup` из tool checkout и `check_package.build`). У нового `run.py` свой
фиксированный argv и reader native export с проверками по схеме пина. Старые dispatch,
профили, collectors и admission rules остаются в прежних файлах.

Workflow сверяет request, HEAD/tree и зависимости, вычитывает std и tool по полным SHA,
проверяет их чистоту и собирает tool один раз на runner. Точный tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.
Kani CLI следует форме `build_argv` из прежнего runner: `verify-std`, один `--harness`,
`--exact`, `--jobs=1`, `--default-unwind 36`, `--harness-timeout 600s`, `--output-format=regular`,
`--no-assert-contracts`, `-Z unstable-options`, `function-contracts`, `mem-predicates`,
`float-lib`, `c-ffi`, `stubbing`, `-Z export-json` и `--export-json` с полным путём,
`--cbmc-args --object-bits 12`.
CaDiCaL по умолчанию, без solver override. Loop contracts, quantifiers, uninit и validity OFF.
На пине `contract_mode` выбирает Check/Replace прежде Assert/Original. Макрос Replace
проверяет requires и допущением вводит ensures после havoc. Проверить эти режимы и покрытие
их обязательных ролей по фактическому export. Сверять даже при `--no-assert-contracts`.

Порядок — P-1, P-2, P-3, P-4, P-5a, P-5b, P-5c. Каждый root получает отдельные process,
target и export paths под runner temp. Cfg из закрытого списка запроса, без произвольных
аргументов из workflow inputs. Сборка `verify-std` входит в время child. Setup checkout и
tool build ограничены 1800 с вместе, build ≤900 с. На root сохранить compile ≤180 с,
child ≤600 с, внешний slot ≤720 с. Для семи roots это 4200 с суммарного child и 5040 с
слотов. Сохранить campaign ≤6900 с, outer ≤7500 с, step ≤7560 с, phase ≤8100 с, job ≤180 мин.
Local RSS cap ≤6 GiB и outer ≤12 GiB с запасом 2 GiB по прежней схеме. Записать nominal и
effective caps по доступной памяти/ограничению cgroup, а также область sampled RSS.
Stdout ≤16 MiB, stderr ≤1 MiB, export ≤8 MiB на root, результат кампании
≤256 MiB. Runner резервирует время следующих слотов и остановки. Если лимит не допускает
следующий root или нарушены identity/containment, сохраняет уже завершённые записи и
выставляет оставшимся `NOT_RUN` с причиной. Обычный завершённый отрицательный контроль
или локальный cutoff не отменяет остальные roots в пределах бюджета и чистой остановки.

## Record исследования

Один версионированный `q-pilot-results.json` в bounded artifact. Записывать атомарно после
setup и каждого root. На ранней ошибке workflow выдаёт итоговую запись с состоянием setup
и оставшимися `NOT_RUN`, если producer успел запуститься. Отсутствие artifact само по себе
оставляет итог `UNKNOWN`. Формат минимального record:

| Блок | Обязательные поля |
| --- | --- |
| Campaign | Схема `ch8-q-pilot-results-v1`, профиль `ch8-q-pilot-v1`, `RESEARCH_ONLY`, `proof_credit=NONE`, run ID/attempt/ref/event, trigger SHA/tree/parent, SHA-256 request/workflow, std/tool commits и trees, OS/версии, setup status/exit/time, лимиты, stop reason. |
| Root identity | ID и полный selector, cfg, domain ID и q-domain, invocation ID, argv и выбранный solver из config, target/export identity (путь в invocation и digest), один native harness с kind/contract target/verified stubs и фактическими flags. |
| Lifecycle | `NOT_RUN`, `COMPLETE`, `PARTIAL`, `MISSING` или `INVALID` на соответствующей стадии, исходные exit/signal, ошибка/timeout/cutoff и cleanup status, monotonic child wall, compile marker upper и native VT при наличии, sampled RSS с областью измерения. Неизмеренное поле — явный `null` с причиной. |
| Inventory | Для complete export сохранить native status и все структурированные properties, включая ID/class/status/location, сообщения, covers, U/unsupported/unwind и диагностические предупреждения. Указать финальность, количество и согласование с native export. Без полной структуры помечать partial/unknown, не достраивать строки. |
| Control | Ожидание, назначенная property, фактическое совпадение `MATCH/MISMATCH/UNKNOWN` с причиной. Для P-5b — native SUCCESS отдельно от синтетического отказа qualification по `q_domain={0}`. |

Stock export на этом пине агрегирует SUCCESS. Для полного property inventory подавать
regular stream в существующий `rich_evidence.RegularEvidence` во время child, связать записи
с тем же export по exact selector, ID, статусам и totals. Не полагаться на итоговые числа
без списка properties. Сохранить отсутствующие координаты как `null`, ошибки сверки и
неоднозначность обязательных ролей явно. Не переносить прежние source-location exceptions.

В artifact входят только структурированные наблюдения и короткая ограниченная диагностика
ошибки. Полные raw logs/archives не нужны. Отдельного intake, metadata exceptions,
переписывания U и admission в этой дорожке нет. `COMPLETE` обозначает завершённость
записи. Для meaningful PASS нужны native verdict, обязательные roles/covers и совпадение
контролей. Результаты потребителей учитываются как диагностические с явными связями с
P-1/P-2/P-3. Qualification провайдеров и proof credit требуют отдельной приёмочной стадии.

## До запуска

1. Воркер фиксирует source и control commits, cfg, exact root/role map, provider domains,
   hashes и результаты offline checks из [PILOT-IMPL-TASK.md](PILOT-IMPL-TASK.md).
2. Независимый ревьюер сверяет точные commits и зависимости, spec domains, runtime diff,
   limits и error paths по [PILOT-REVIEW-TASK.md](PILOT-REVIEW-TASK.md). Локально выполнить
   синтетический preflight нового runner с исходами success/error/timeout/partial/missing/null/
   wrong-type/NOT_RUN, identity mismatch и сохранением original exits и cleanup receipt.
   При изменении реализации этим же набором проверить delta. Предыдущие 389 тестов полного
   конвейера не являются gate для нового профиля. Native registration и compile проверяются
   первым разрешённым exact invocation, общей `kani list` кампании не требуется.
3. Координатор сверяет входы после review, получает пригодный к fetch точный source SHA,
   проверяет, что trigger ref свободен, связывает будущий триггер с reviewed control tree
   и тем же sole parent. До одного trigger push нужны отдельный GO, строка ledger и окно на
   полный envelope. Проверить SHA/ref/workflow/job/attempt сразу после старта. Каждая новая
   попытка требует своего review/GO/ledger. GCB не входит в этот маршрут. При выборе GCB
   нужен отдельный coordinator request в пределах выделенного владельцем бюджета.

Предлагаемый исследовательский сигнал — все четыре positives и три control outcomes
установлены, P-2/P-4 завершаются с child ≤300 с каждый. При cutoff или неподходящем домене
сначала разобрать этот случай. Расширение монолитной N-матрицы остаётся закрыто до gate.
