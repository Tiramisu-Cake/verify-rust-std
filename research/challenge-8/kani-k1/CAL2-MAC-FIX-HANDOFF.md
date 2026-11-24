# CAL2 · исправление Darwin census и подготовка повтора macOS

## FIX4 · проверки снимка и выход на границе бюджета

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`.

1. В пределах бюджета валидный снимок проходит проверки давления, резерва и суммарного RSS живых участников группы до выбора исхода по статусу direct child. Если в снимке нет live-записи direct child, `poll()` отличает временный пропуск от подтверждённого выхода. При подтверждённом выходе снимок с живым потомком доходит до проверок. Регрессия с первым снимком 50 KiB и потомком 175 KiB при cap 100 KiB даёт `RSS_LIMIT` с пиком 175 KiB. Варианты с давлением и недостаточным резервом подтверждают приоритет соответствующих ограничений. Свежий снимок после повтора проходит те же проверки, в том числе после таймаута `ps`.
2. Если оставшийся бюджет census исчерпан, supervisor повторно проверяет статус direct child. Синтетическая пауза с 0,790 до 0,801 с при `stop_at=0,800` с и доступном с 0,795 с статусе даёт `EXITED` с прежним пиком 50 KiB. Если child ещё жив, тот же сценарий даёт `SAMPLER_ERROR`. В обоих случаях дополнительный `ps` после исчерпания бюджета отсутствует.

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Control FIX4 | `7572d0b50c67e8f5d5aa1376936d3d2345a6ee51` | `6496aa3d9fd84e02ee3d1afe74d195d89c3f7505` | `7cd3929f69f41f8dde76082f21b748fb552fb046` |
| Локальный review-trigger, `local/cal2-mac-fix4-trigger-review` | `09cb47a896f779994851859478f4e1929e76fb20` | `6496aa3d9fd84e02ee3d1afe74d195d89c3f7505` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Применение patch к `7cd3929f69` во временном Git index воспроизвело общий tree. SHA-256 patch `22d97d7079fc3728460042c792af48c7e084aa72a55253b9e25ef799be9e0ea7`. [Задание FIX4](CAL2-MAC-FIX4-TASK.md) · [Ревью Round 3](CAL2-MAC-FIX-REVIEW.md#round-3-diff-fix3) · [Diff FIX4](CAL2-MAC-FIX4.patch)

Полный `timeout 120s python3 -B -m unittest discover -q` на Linux с Python 3.12.3 прошёл, 103 теста за 14,250 с. Нативный Linux `rss-stop` дал `RSS_LIMIT`, пик 67 440 KiB при cap 24 576 KiB, `sampler_valid=true`, `reaped=true`, `remaining_processes=[]`, `cleanup_errors=[]`. `git diff --check` прошёл для рабочей копии control, дельты FIX4 и diff trigger от его родителя. Darwin проверен синтетически. CI, push, Cargo, rustc, Kani и CBMC не запускались.

Следующее ревью блокируют открытые пункты FIX4, регрессии относительно FIX2 и ослабление RSS-стопа, проверок давления или резерва либо подтверждения очистки. Снимки `ps` и проверки статуса выхода разделены во времени. Остальные гонки на границах планировщика фиксируются в receipts как ограничения диагностического прогона.

## FIX3 · единичный пропуск direct child

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`.

Следующее ревью охватывает пункт 3 Round 2 и diff `eaa02a0286..7cd3929f6`. Patch воспроизводит общий tree control и локального trigger при применении к `eaa02a0286` во временном Git index. SHA-256 patch `1c686e1e5ab59555a1033093afb3fec47a2d27816e4ef47ab4cc63faba60c07e`. [Задание FIX3](CAL2-MAC-FIX3-TASK.md) · [Ревью Round 2](CAL2-MAC-FIX-REVIEW.md#round-2-diff-fix2) · [Diff FIX3](CAL2-MAC-FIX3.patch)

Если census вернул снимок без live-записи direct child, а `poll()` ещё не получил статус выхода, supervisor учитывает пропуск и сразу переходит к общему пути одного повтора. Валидный снимок требуется для обновления пика RSS, счётчика успешных сэмплов и отметки последнего RSS. Вызов `ps` ограничен 1,0 с, остатком до `stop_at` и остатком 2,0 с от последнего валидного RSS или запуска child. Свежий снимок с child проходит guards. Повторный пропуск или исчерпание бюджета дают `SAMPLER_ERROR`, если повторная проверка ещё не видит статус выхода после пропуска. При подтверждённом выходе supervisor возвращает `EXITED` и сохраняет предыдущий пик. Receipts отдельно учитывают `ps_missing_child` и `ps_timeouts`.

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Control FIX3 | `7cd3929f69f41f8dde76082f21b748fb552fb046` | `b6705a8145d410de573d66be769548a869af3d32` | `eaa02a02867ab600e23060aef32ba2c17749b8ec` |
| Локальный review-trigger, `local/cal2-mac-fix3-trigger-review` | `a2e5bdc67a5c05ccdaddacafb9bc91458c5854e6` | `b6705a8145d410de573d66be769548a869af3d32` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

`timeout 120s python3 -B -m unittest discover -q` на Linux с Python 3.12.3 прошёл, 101 тест за 14,459 с. Синтетический Darwin покрывает стартовый пропуск, публикацию статуса выхода во время повтора, проверку свежего RSS, два пропуска в одной серии и обе границы бюджета. Нативный Linux `rss-stop` дал `RSS_LIMIT`, пик 67 328 KiB при cap 24 576 KiB, `sampler_valid=true`, `reaped=true`, `remaining_processes=[]`, `cleanup_errors=[]`. `git diff --check` прошёл для рабочей копии, diff FIX3 и diff trigger от его родителя. CI, push, Cargo, rustc, Kani и CBMC не запускались.

## FIX2 · три блокирующих замечания

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`.

Следующее ревью ограничено diff `526c2760b1..eaa02a0286` в трёх Python-файлах. Применение приложенного diff к `526c2760b1` во временном Git index воспроизвело общий tree control и review-trigger. [Задание FIX2](CAL2-MAC-FIX2-TASK.md) · [Независимое ревью](CAL2-MAC-FIX-REVIEW.md) · [Diff FIX2](CAL2-MAC-FIX2.patch)

1. После сбоя раннего Darwin census финальный снимок после сбора direct child проверяет живых участников исходного PGID вместе с ранее наблюдавшимися потомками. Живой участник PGID или отсутствие валидного финального снимка дают `REAP_UNVERIFIED`. Адресные сигналы после reap по-прежнему требуют ранее наблюдавшийся PID и совпадающий start identity. Регрессия воспроизводит TERM, который завершает лидера и оставляет ранее неизвестный PID 11 в группе.
2. Оба нативных теста сохраняют настоящий `ps`, окно 8 с, проверки готовности потомка и TERM/KILL. При своевременных сэмплах ожидается `TIMEOUT`. На Darwin тесты допускают `SAMPLER_ERROR` после хотя бы одного валидного сэмпла только для таймаута census или его повторной попытки у `stop_at`. Управляемые часы воспроизводят пять сэмплов по 0,70 с с последним бюджетом 0,50 с и вариант с усечённым бюджетом retry. Боевая политика дедлайна прежняя.
3. Darwin census без записи о живом direct child даёт `SAMPLER_ERROR` и `sampler_valid=false`. Снимок не засчитывается, не обновляет бюджет наблюдения и сохраняет предыдущий пик, включая `null` до первого валидного сэмпла. Регрессии охватывают первый census, пропуск после валидного RSS, retry и снимок, в котором виден только участник группы.

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Control FIX2 | `eaa02a02867ab600e23060aef32ba2c17749b8ec` | `9eeeaa580d555cf2190382edbc2f77457382144d` | `526c2760b1e009593336bc2f295ded9851547337` |
| Локальный review-trigger, `local/cal2-mac-fix2-trigger-review` | `c954f901abe134f40539069e0a7c186b1c452518` | `9eeeaa580d555cf2190382edbc2f77457382144d` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Файл | SHA-256 |
| --- | --- |
| `CAL2-MAC-FIX2.patch` | `5ed33e76fdca49bc2ef1f0cf14a4ffe9cf0b6772d2d6befa7e64ee4be9cd53f7` |
| `CI-REQUEST.json` | `5b0fd89dfd2933c3b2768240c99b3b00d0770ec6004b763244ac00d6a3d25a9c` |
| `std-overlay.bundle` | `747bed56fb2c137caf90dadc52802b42406840f9240dda3f58a370a33662a481` |

Сверка Git подтвердила идентичность workflow, request, bundle, overlay, Ubuntu-профиля, roster и расписания с исходным control. `git diff --check` прошёл для control и review-trigger. Коммиты используют `[skip ci]` и автора `Tiramisu-Cake <igkharin@gmail.com>`.

Полный `python3 -B -m unittest discover -q` под `timeout 120s` на Linux с Python 3.12.3 прошёл, 97 тестов за 13,996 с. Нативный Linux `rss-stop` вернул `RSS_LIMIT`, пик 66 804 KiB при cap 24 576 KiB, `sampler_valid=true`, `reaped=true`, `remaining_processes=[]` и `cleanup_errors=[]`. Darwin-ветви проверены синтетически. Нативный Darwin suite и длительность раннего self-test ожидают согласованного запуска на macOS. CI, push, Cargo, rustc, Kani и CBMC не запускались.

## Исходный handoff Darwin

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`.

В run 45307150788 macOS остановился на раннем self-test до setup и discovery. По ledger два нативных теста дедлайна получили `SAMPLER_ERROR` из-за таймаута общего `ps`. Кандидат даёт один немедленный повтор в пределах исходного окна. [Задание](CAL2-MAC-FIX-TASK.md) · [Разбор CAL2](CAL2-RESULTS-ANALYSIS.md) · [Исходный handoff](CAL2-HANDOFF.md)

## Коммиты и входы

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Исходный control FIX1 | `cd987bae7c35e7a5ba7de540488b58e9a2e26120` | `19420792d055b068bbfc80b05d1826c957fe9c31` | `7393c841446064bffc9d8b1d13a4d68db83cb8f1` |
| Локальный control | `526c2760b1e009593336bc2f295ded9851547337` | `5de0c998f531cfaed7d7b5ab6c440c126824e91e` | `cd987bae7c35e7a5ba7de540488b58e9a2e26120` |
| Локальный trigger для review, `local/cal2-mac-fix-trigger-review` | `bbc55d6ae84108d5c66ed1fc18cf16ffa0346e97` | `5de0c998f531cfaed7d7b5ab6c440c126824e91e` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Std overlay CAL2 | `043a1f19f9d36eb1666979f97b8e7e483ab41c5e` | `1361a0da67b9bd21fc7c77a941582d0fd17b9a8d` | `080a0104159fd04b6764a24f8538a97588f6612e` |

| Файл | SHA-256 |
| --- | --- |
| `CI-REQUEST.json` | `5b0fd89dfd2933c3b2768240c99b3b00d0770ec6004b763244ac00d6a3d25a9c` |
| `std-overlay.bundle` | `747bed56fb2c137caf90dadc52802b42406840f9240dda3f58a370a33662a481` |
| `CAL2-MAC-FIX.patch` | `3c4491b5c2a07257bbb29e949efd8fae764fb13cf9bd3765ae64527fa7507f31` |

Применение приложенного diff к FIX1 во временном Git index воспроизвело tree control и review-trigger. Сверка с FIX1 подтвердила идентичность frozen request, bundle, std overlay, профиля Ubuntu, argv, roster и расписания. Все новые локальные коммиты используют `[skip ci]` и автора `Tiramisu-Cake <igkharin@gmail.com>`. [Diff от FIX1](CAL2-MAC-FIX.patch) · [Frozen request](/root/kani-cal1-control-w11/ch8-cal1/CI-REQUEST.json) · [Bundle](/root/kani-cal1-control-w11/ch8-cal1/std-overlay.bundle)

## Учёт процессов и очистка

- Только таймаут общего Darwin census `ps -axww -o pid=,ppid=,pgid=,rss=,stat=,lstart=,comm=` открывает повтор. Каждый вызов получает до 1,0 с, ограниченных `stop_at` и 2,0 с с последнего валидного RSS или запуска child. Census сохраняет `LC_ALL=C`, проверку кода возврата и строгий разбор. Ошибка запуска, ненулевой exit, пустой или повреждённый snapshot и ошибка источника памяти сразу останавливают sampler. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py)
- На первом таймауте сохраняется прежний пик RSS и проверяются живые pressure и reserve. Если оба guard пройдены, supervisor сразу повторяет census и проверяет свежий RSS теми же guards и cap. Повторный таймаут, исчерпание окна без свежего сэмпла и выход child до подтверждённого восстановления дают `SAMPLER_ERROR` и `sampler_valid=false`. При открытом пропуске pressure и reserve могут остановить child своими причинами с `sampler_valid=false`. Обычный дедлайн с подтверждённым наблюдением даёт `TIMEOUT`. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py)
- В `child.darwin_census` попадают лимиты, счётчики таймаутов и восстановлений, причина и фактический лимит последнего таймаута и максимальный интервал без валидного RSS, включая начало и конец наблюдения. В `samples_missed` число успешных сэмплов вычитается из большего из числа попыток и числа плановых отсчётов, поэтому один потерянный вызов и совпавший пропуск cadence учитываются один раз. Cadence измеряется по времени завершения валидных сэмплов, целевой интервал 0,3 с. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py) · [Проверки receipts](/root/kani-cal1-control-w11/ch8-cal1/test_run.py)
- В пределах штатных 5 с TERM и 5 с KILL/reap ранний census перед TERM получает до 0,25 с. Повторные, финальный census и сверка PID/start перед адресным сигналом получают до 1,0 с каждый в пределах своей фазы и общего дедлайна. В KILL зарезервированы последние 1,0 с на финальный census и до 0,05 с перед ними на сбор child. Таймаут оставляет состав группы неизвестным. До reap direct child разрешён сигнал закреплённой группе. После reap используются только ранее наблюдавшиеся PID со сверкой start identity. `reaped=true` требует успешного финального census. `REAP_UNVERIFIED` хранит исходную причину и блокирует следующие слоты и финальные tool probes. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py) · [Переход между слотами](/root/kani-cal1-control-w11/ch8-cal1/run.py)

## Повтор macOS после GO

- Один job на `macos-latest`, attempt 1, с точным push gate `Tiramisu-Cake/kani` и `refs/heads/uninit-ci/ch8-q-pilot-v1`, checkout `github.sha` и `contents: read`. Self-test и проверка control имеют лимит 2 мин. Job ограничен 225 мин, setup целиком 45 мин, compile preflight до 180 с. Граница слотов на 202-й минуте с условием latest start и запасом 10 с. Внутри окна слота 10 с на cleanup и 5 с на receipt. Итоговая аттестация до 204-й минуты, затем 12 мин на финализацию и публикацию и 9 мин резерва. Лимиты публикации 4 MiB на проекцию и 96 MiB на job. [Workflow](/root/kani-cal1-control-w11/.github/workflows/ch8-q-pilot.yml) · [Лимиты](/root/kani-cal1-control-w11/ch8-cal1/request.py)
- После build обязательны cfg-on compile preflight и оба `kani list`, cfg-on на overlay и cfg-off на std base. Затем 11 singleton с OB12 в прежнем порядке, 139 мин окон. Следуют два batch N8/N9 по 600 с с исходным допуском, сначала `-j`, затем `--jobs=1`. Допуск использует полные итоги обоих singleton, сумму wall с запасом 30 с и сумму их пиков в пределах 80% effective cap batch. Выводы macOS привязываются к реально достигнутым фазам. [Frozen roster](/root/kani-cal1-control-w11/ch8-cal1/CI-REQUEST.json) · [Setup и допуск batch](/root/kani-cal1-control-w11/ch8-cal1/run.py)

| Фаза | Номинальный cap | Live reserve |
| --- | --- | --- |
| Только cfg-on и cfg-off `kani list` | 7 GiB · 7 340 032 KiB | 1,25 GiB · 1 310 720 KiB |
| Build, compile preflight, 11 singleton и два batch | 5,5 GiB · 5 767 168 KiB | 1,25 GiB · 1 310 720 KiB |

При допуске effective cap равен `min(nominal, available − reserve)`. Фактический trigger создаёт координатор после отдельного GO с указанным tree и единственным parent, без метки пропуска CI. Текущая стадия завершена локально. CI, push, Cargo, rustc, Kani и CBMC не запускались.

## Проверки

- `python3 -B -m unittest discover -q` на Linux с Python 3.12.3 прошёл, 94 теста за 14,022 с. Darwin-ветви выполнены синтетически с управляемыми монотонными часами и фактическим кодом supervisor. Проверены медленный валидный `ps`, одиночный таймаут и восстановление, проверка cap свежего RSS, повторный таймаут, отсутствие первого валидного сэмпла, границы stop и gap, выход child, счётчики, pressure/reserve, ошибки формата, exit, запуска и memory probe. Cleanup проверен с временным и финальным таймаутом, границами TERM/KILL, привязкой группы и переиспользованием PID. Receipts покрывают прерванный запущенный слот и `NOT_STARTED`, включая блокировку последующих слотов после `REAP_UNVERIFIED`. [Darwin fixtures](/root/kani-cal1-control-w11/ch8-cal1/test_darwin_supervisor.py) · [Проверки receipts](/root/kani-cal1-control-w11/ch8-cal1/test_run.py)
- Два нативных теста дедлайна и остановки потомков прошли на Linux. На Darwin оба продолжат использовать настоящий `ps`. Для них выделено до 8 с на тест, включая по 2 с TERM/KILL. Потомок отмечает готовность после установки обработчика TERM. Нативный Linux `rss-stop` дал `RSS_LIMIT`, пик 67 224 KiB при cap 24 576 KiB, `sampler_valid=true`, `reaped=true`, `remaining_processes=[]` и `cleanup_errors=[]`. Darwin runner локально недоступен. Первой нативной Darwin-проверкой станет ранний self-test согласованного повтора. [Нативные тесты](/root/kani-cal1-control-w11/ch8-cal1/test_supervisor.py) · [RSS-stop](/root/kani-cal1-control-w11/ch8-cal1/stress_supervisor.py)
- `git diff --check` прошёл. PyYAML подтвердил единственный macOS job с теми же 11 развёрнутыми шагами и gate. `bash -n` прошёл у шести shell-шагов. Локальная проверка YAML gate приняла один точный push и отклонила пять вариантов. `run.py pins` в отдельном checkout review-trigger подтвердил commit, tree, parent и пины на точном synthetic push и отклонил девять вариантов, включая совпадающий tree с неверным parent. [Workflow](/root/kani-cal1-control-w11/.github/workflows/ch8-q-pilot.yml) · [Trigger guard](/root/kani-cal1-control-w11/ch8-cal1/request.py)
- Независимый воркер Luna High проверил diff политики census/reap, нативные тесты раннего self-test, workflow gate и идентичность профиля Ubuntu и std overlay. Блокирующих замечаний нет.
