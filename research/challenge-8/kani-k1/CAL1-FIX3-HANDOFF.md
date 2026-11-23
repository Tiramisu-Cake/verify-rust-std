# CAL1 · FIX3 · исчезновение PID при сборе RSS

`READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. GO пятого раунда относился к прогону 45268412731 на FIX2. В его receipt ранняя компиляция overlay завершилась с кодом 0 за 36,69 с. Cfg-on discovery остановился за 759,47 с в `goto-cc` с `SAMPLER_ERROR`, `ProcessLookupError [Errno 3]`, PSI `full avg10=0.0` и `reaped=true`. Receipt не указывает, на какой операции с PID произошёл сбой. Discovery и результаты harnesses на FIX3 имеют статус `UNKNOWN`. [Задание FIX3](CAL1-FIX3-TASK.md) · [Ревью FIX2](CAL1-REVIEW.md#пятый-раунд--fix2--2026-11-24) · [Setup receipt](/root/ch8-artifacts/run-45268412731/ch8-cal1-Linux-X64-45268412731-1/setup.json) · [Error receipt](/root/ch8-artifacts/run-45268412731/ch8-cal1-Linux-X64-45268412731-1/error.json)

## Идентичность пакета

| Объект | SHA или SHA-256 |
| --- | --- |
| Control FIX3 | `5dd6140e7aa9225d4c1014b957bb2c65bba6c7aa` |
| Control tree | `4cf6be61fff1988b22bf7f504e553361352f55d9` |
| Единственный parent control | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Control FIX2 для сравнения | `c93b068fcc2bc7e1e9b723d6d4ad72743e520ddc` |
| Overlay commit | `080a0104159fd04b6764a24f8538a97588f6612e` |
| Overlay tree | `96f95b8082983b57f203b0e3e12151552dba0f76` |
| Frozen request SHA-256 | `bd375fc094fc0c63f913efcc05278ea45fa0851b4285f367a5403ce77e078647` |
| Std bundle SHA-256 | `27cb6c5fc420ba32f1b9266d3c7d66451e176a63a0ba2ba70a74405c39472d61` |

Diff к FIX2 состоит из `ch8-cal1/supervisor.py`, `ch8-cal1/test_supervisor.py` и `ch8-cal1/stress_supervisor.py`. Frozen request и bundle побайтно совпадают с FIX2. Bundle объявляет overlay commit как `HEAD`. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py) · [Тесты](/root/kani-cal1-control-w11/ch8-cal1/test_supervisor.py) · [Стресс-сценарий](/root/kani-cal1-control-w11/ch8-cal1/stress_supervisor.py)

## Аудит чтений и сигналов

| Место | Гонка и исход | Проверка |
| --- | --- | --- |
| Linux `_linux_table`, открытие каталога PID | PID исчезает после перечисления `/proc`. `FileNotFoundError`, `ProcessLookupError` и `OSError` с `ESRCH` пропускают одну запись. Сбой перечисления `/proc` даёт ошибку всего census. | Синтетические ошибки на открытии каталога и при общем перечислении. `pid-race` завершает и собирает настоящий дочерний процесс после перечисления. |
| Linux `_linux_pid_record`, `stat`, `cmdline`, `status` | Каждый файл открывается относительно одного дескриптора каталога PID. При исчезновении запись пропускается целиком. Дескриптор удерживает привязку к исходному процессу при переиспользовании номера. Ошибка доступа и ошибка разбора доступны вызывающему коду. | Все три вида ошибок на каждом из трёх чтений, замена каталога между `stat` и `cmdline`, `EACCES` и невалидный `stat`. |
| `_tree`, `_owned_live`, `_default_sample` | Отсутствующая запись не попадает в RSS. Обход продолжает поиск по группе, присутствующим записям и живым потомкам с известным `start_id`. Изменение `start_id` у известного PID вызывает ошибку до включения записи в RSS или адресной отправки сигнала. | После выпадения PID сохранены соседний процесс и его потомок вне группы. В выпавшем и следующем снимках сумма ровно 60 KiB. Проверен повторно использованный PID вне группы. |
| `_signal_group` | Группа может исчезнуть между census и `killpg`. `ESRCH` означает отсутствие адресата. Отказ доступа проходит в диагностику cleanup. Признак владения группой берётся из живого direct child или census её участников. | Синтетические `ESRCH` и `EPERM`, нативный TERM при `RSS_LIMIT`, существующий TERM/KILL-тест. |
| `_signal_owned`, первая и повторная сверка | Валидный census без цели или с её zombie-записью завершает попытку. Несовпадение `start_id` запрещает сигнал по старой записи. После `pidfd_open` повторный census проверяет цель перед `pidfd_send_signal`. Ошибка общего census передаётся cleanup. | Синтетически проверены отсутствие после открытия pidfd, смена `start_id` до и после открытия и ошибка повторного census с `ESRCH`. |
| `_signal_owned`, системные вызовы | `ESRCH` при `pidfd_open`, `pidfd_send_signal` или адресном `kill` завершает попытку. Другие ошибки уходят в диагностику cleanup. pidfd закрывается и при ошибке. Darwin и Linux без Python API pidfd используют существующий `kill` после сверки `start_id`; между сверкой и вызовом остаётся окно. | Синтетические исчезновение и отказ сигнала, закрытие pidfd, успешная отправка. Существующий нативный тест на потомка, сменившего группу. |
| `_shutdown`, первый, повторные и финальный census | Все census, включая сверки перед адресным сигналом, учитывают пропуски PID. Cleanup продолжает проверять живых потомков после TERM и KILL. Для `reaped=true` требуются собранный direct child и валидный финальный census с пустым списком живых принадлежащих запуску процессов. | Пропуски при cleanup отражаются в receipt. Ошибка финального census после exit 0 даёт `REAP_UNVERIFIED`, `remaining_processes=null`. Существующие тесты проверяют обнаружение и остановку живых потомков. |
| Darwin `_darwin_table`, системная память и PSI | Общий `ps -axww` остаётся единственным источником PID на Darwin. Отсутствие цели в валидном снимке ожидаемо. Таймаут, ошибка запуска, ненулевой код выхода, пустой и невалидный общий снимок передаются как ошибки. Чтения `/proc/meminfo`, PSI и Darwin memory probes сохраняют исходную диагностику. | Синтетические Darwin-снимки и ошибки `ps`, тесты ошибок Linux PSI и Darwin memory probes. |

`sample_pid_records_skipped` считает пропущенные PID-записи при измерении. `cleanup_pid_records_skipped` считает их в census cleanup и при сверках перед сигналом. Счётчики учитывают события чтения в глобальном `/proc`, включая чужие записи, пропущенные до установления принадлежности. Отсутствие PID в новом валидном снимке и `ESRCH` самого вызова сигнала не добавляют запись. `samples_missed` сохраняет учёт целых сэмплов и задержек cadence. [Документация Linux procfs](https://docs.kernel.org/6.12/filesystems/proc.html#process-specific-subdirectories) · [Исключения Python](https://docs.python.org/3/library/exceptions.html#ProcessLookupError) · [Документация `pidfd_open`](https://man7.org/linux/man-pages/man2/pidfd_open.2.html)

## Локальные проверки

Все команды Python запускались из `/root/kani-cal1-control-w11/ch8-cal1` под Linux x86-64 6.8, Python 3.12.3.

```sh
python3 -B -m unittest discover -v
python3 -B stress_supervisor.py churn
python3 -B stress_supervisor.py rss-stop
python3 -B stress_supervisor.py pid-race
```

Прошли все 58 тестов `unittest discover` за 11,24 с. Длительные процессы запускались отдельными командами. Все три нативных сценария завершились с `sampler_valid=true`, `reaped=true`, `remaining_processes=[]` и пустым `cleanup_errors`.

| Сценарий | Длительность | Исход и exit | Валидные / пропущенные сэмплы | Пик RSS / cap, KiB | Пропущенные PID-записи, измерение / cleanup |
| --- | ---: | --- | ---: | ---: | ---: |
| `churn` | 182,43 с | `EXITED`, 0 | 608 / 0 | 85 876 / 163 840 | 143 / 1 |
| `rss-stop` | 1,05 с | `RSS_LIMIT`, −15 (`SIGTERM`) | 3 / 0 | 66 656 / 24 576 | 3 / 1 |
| `pid-race` | 1,13 с | `EXITED`, 0 | 4 / 0 | 17 540 / 98 304 | 2 / 3 |

- `churn` создал 643 потомка. Два worker-процесса собрали по 320 короткоживущих дочерних процессов с длительностью сна 15–55 мс. Третий потомок затронул 24 576 KiB и удерживал их 4 с при интервале сэмплов 0,3 с. Его собственный VmRSS был 38 904 KiB. Одновременно работали максимум шесть процессов вместе с корнем. В первом заходе лимит сценария 98 304 KiB сработал при суммарном пике 111 500 KiB. Для завершившегося прогона лимит сценария поднят до 160 MiB с учётом суммирования общих страниц, а импорт `unittest.mock` перенесён в `pid-race`. Объём затронутой памяти и схема дерева прежние.
- `rss-stop` затронул 48 MiB. Минимум `MemAvailable` составил 1 216 596 KiB при резерве 65 536 KiB. TERM и reap прошли при `pressure=CLEAR`.
- `pid-race` синхронизировал выход и сбор настоящего дочернего процесса тестового сценария после перечисления `/proc` и до открытия записи PID. Файловое чтение оставалось нативным. Счётчик измерения отразил пропуск, cadence сохранил все сэмплы.

Проверки Darwin выполнены синтетически на Linux. Они покрывают разбор `ps`, отсутствие цели, пустой и невалидный снимок, таймаут, отказ запуска и ненулевой exit `ps`, отправку обычного сигнала и ошибки memory probes. Локальной среды Darwin не было.

Сверены `git diff --check`, единственный parent, автор и committer, SHA-256 request и bundle, overlay commit и tree. `git bundle verify` на overlay checkout прошёл. Локальный guard принял синтетическое событие с SHA FIX3 и отклонил несовпадающий `GITHUB_SHA`. CI, push и локальные Cargo, rustc, Kani и CBMC не запускались.
