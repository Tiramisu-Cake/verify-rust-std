# CAL2 · исправление Darwin census и подготовка повтора macOS

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
