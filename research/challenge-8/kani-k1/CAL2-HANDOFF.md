# CAL2 · диагностический пакет SmallSort для pr752

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. Пакет содержит независимые jobs Ubuntu и macOS. Фактические discovery, свойства и ресурсные результаты CAL2 имеют статус `UNKNOWN`. [Задание](CAL2-TASK.md) · [Разбор CAL1](CAL1-RESULTS-ANALYSIS.md)

## FIX1

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. Исправлены три замечания Round 1. Дельта для ревью — `7393c84144..cd987bae7c`. [Задание FIX1](CAL2-FIX-TASK.md) · [Round 1](CAL2-REVIEW.md#round-1-independent)

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Control FIX1 | `cd987bae7c35e7a5ba7de540488b58e9a2e26120` | `19420792d055b068bbfc80b05d1826c957fe9c31` | `7393c841446064bffc9d8b1d13a4d68db83cb8f1` |
| Trigger `local/cal2-fix1-trigger-review` | `7572c48869196484135158878d058a17d9c520e7` | `19420792d055b068bbfc80b05d1826c957fe9c31` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Std overlay CAL2 | `043a1f19f9d36eb1666979f97b8e7e483ab41c5e` | `1361a0da67b9bd21fc7c77a941582d0fd17b9a8d` | `080a0104159fd04b6764a24f8538a97588f6612e` |

| Файл | SHA-256 |
| --- | --- |
| `CI-REQUEST.json` | `5b0fd89dfd2933c3b2768240c99b3b00d0770ec6004b763244ac00d6a3d25a9c` |
| `std-overlay.bundle` | `747bed56fb2c137caf90dadc52802b42406840f9240dda3f58a370a33662a481` |

Request и bundle совпадают с Round 1 побайтно. Control и trigger имеют один tree. Оба коммита используют `[skip ci]`.

- Отказ старта потока PSS даёт `pss_kib=null` и `PROBE_START_FAILED` с текстом ошибки до 300 символов в каждом receipt Linux measure. Четыре A/B-слота продолжают записывать RSS из штатного census. Инъекция отказа вызвала все шесть слотов с прежними параметрами guard и позволила завершить аттестацию в синтетическом сценарии.
- Layout guard читает Git blobs и сравнивает manifest побайтно после удаления двух точных строк cfg. Лишняя пустая строка и удаление последнего LF отклоняются. Закреплённый overlay `043a1f19f9` проходит.
- При `TIMEOUT` или `RSS_LIMIT` и неполном либо отсутствующем export обязательный receipt сохраняет `resolved_unwind` из полной verbose-строки CBMC после точного маркера селектора. `resolved_unwind_source` указывает `NATIVE_CBMC_COMMAND`, поток `stdout` и номер строки. Stock-значение имеет приоритет. Fallback действует в singleton и `batch-jobs1`, где команда привязывается к селектору по порядку stdout. При неоднозначности или отсутствии наблюдения unwind остаётся неизвестным.

- Полный локальный suite `python3 -B -m unittest discover -q` прошёл, **82/82**. Проверены обе отсечки, неизвестный unwind при неоднозначном выводе, обе мутации manifest и отказ старта потока PSS на входе `measure`. Darwin проверен синтетически.
- Нативные `rss-stop`, `pid-race` и `churn` прошли с `sampler_valid=true` и `reaped=true`. `rss-stop` дал `RSS_LIMIT` и `SIGTERM` при 63 608 KiB и cap 24 576 KiB. `pid-race` завершился `EXITED` с 6 пропущенными PID-записями. `churn` завершился `EXITED` за 182,37 с с 608 валидными census, 0 пропущенных сэмплов и 110 пропущенными PID-записями. Созданы 643 потомка, пик 73 368 KiB при cap 163 840 KiB.
- Прошли `git diff --check`, `git bundle verify` и импорт на shallow std base без записи refs. Сверены хэши, ancestry, tree, layout и guard на checkout нового trigger с синтетическим push event. Подмены SHA, ref и attempt отклонены. YAML и 12 shell-шагов прошли статическую проверку. Cargo, rustc, Kani, CBMC, CI и push не запускались.

## Замороженные входы

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Control CAL1 R7 | `0012750e1a3bbb7977fe0149e565b6b6dcd7c3c8` | `c3228f13f1e3ca71fca1a4147bdb10e61cdfa428` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Control CAL2, detached HEAD | `7393c841446064bffc9d8b1d13a4d68db83cb8f1` | `80fa0a23cac7f0dde952deea145c70e2fbba9f84` | `0012750e1a3bbb7977fe0149e565b6b6dcd7c3c8` |
| Локальный trigger `local/cal2-trigger-review` | `4834030d3991ded4bbdf3f88327f2800543cddd7` | `80fa0a23cac7f0dde952deea145c70e2fbba9f84` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Std base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| Std overlay CAL1 | `080a0104159fd04b6764a24f8538a97588f6612e` | `96f95b8082983b57f203b0e3e12151552dba0f76` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Std overlay CAL2, detached HEAD | `043a1f19f9d36eb1666979f97b8e7e483ab41c5e` | `1361a0da67b9bd21fc7c77a941582d0fd17b9a8d` | `080a0104159fd04b6764a24f8538a97588f6612e` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |

| Файл | SHA-256 |
| --- | --- |
| `CI-REQUEST.json` | `5b0fd89dfd2933c3b2768240c99b3b00d0770ec6004b763244ac00d6a3d25a9c` |
| `std-overlay.bundle` | `747bed56fb2c137caf90dadc52802b42406840f9240dda3f58a370a33662a481` |

Bundle рекламирует единственный `HEAD` overlay CAL2 и требует std base. Импорт добавляет два overlay-объекта commit с соответствующими деревьями и blobs. Guard сверяет SHA-256, ancestry, оба overlay tree, точные lint-декларации в manifest и единственную смену выбора наблюдателя. Runtime SmallSort, cfg-off и штатный workflow std совпадают с базой после снятия опциональных добавлений CAL1. [Request](/root/kani-cal1-control-w11/ch8-cal1/CI-REQUEST.json) · [Bundle](/root/kani-cal1-control-w11/ch8-cal1/std-overlay.bundle) · [Guard](/root/kani-cal1-control-w11/ch8-cal1/request.py)

Оба jobs проверяют fork `Tiramisu-Cake/kani`, событие `push`, точный ref `refs/heads/uninit-ci/ch8-q-pilot-v1` и attempt `1`. Checkout берёт `github.sha`. Guard требует совпадения SHA с `after` в payload и единственного родителя указанного выше. Разрешение workflow ограничено `contents: read`. Директива `[skip ci]` в локальном trigger подавляет push workflow. Dispatch требует отдельного решения координатора и trigger с тем же проверенным tree и sole parent, пригодного для запуска. [Workflow](/root/kani-cal1-control-w11/.github/workflows/ch8-q-pilot.yml) · [GitHub Actions](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)

## Геометрия и профиль

- S13 использует тот же Check `sort13_optimal`, `[u8;34]` с `v[1..14]`, независимый `q: u8`, `KeyLess<u8>`, 45 реальных swaps, unwind 36, q-post, q/V34 frame и исходные covers. Нормализованные argv отличаются значениями `--object-bits 12` и `--object-bits 11`. Оба плеча имеют одинаковый cfg и окна.
- В N32 `merge_capture` по умолчанию выбирает `Below`. `kani_smallsort_cal2_merge_mask` выбирает существующий `merge_target_mask`, а post вызывает существующий `merge_matches_mask`. При `b = # { x < q }` компактный post сравнивает `x < q` с `i < b` для каждого `i` от 0 до 31. Mask сравнивает биты `x >= q` с `((1_u64 << 32) - (1_u64 << b)) as u32`. При `b=0` это `0xffffffff` и все позиции `>=q`. При `b=32` это `0x00000000` и все позиции `<q`. При `b=13` это `0xffffe000`, позиции 0–12 ниже q, позиции 13–31 не ниже q. Таким образом совпадает предикат для всех `b∈[0,32]`. N25 и остальные длины сохраняют прежнюю Mask. Оба N32 плеча проверяют `bidirectional_merge` с реальными `merge_up/down` и проверкой конечных курсоров, численно упорядоченными половинами `v[1..33]`, независимым q и `MaybeUninit<[u8;32]>` по offset 0. Requires, assigns, q-frame, V34 source frame и covers CAL1 совпадают. Diff std ограничен выбором наблюдателя и декларацией cfg.
- N8/N9 сохраняют full-value oracle, внешний frame, unwind 40 и пять covers на корень. Receipt отмечает для каждого совпадение с исходом CAL1 `VERIFIED` с 5/5, а итоговая сводка показывает отклонения. Последующий независимый слот допускается после валидной очистки и при доступном окне. [Корни CAL1](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1.rs) · [Merge observer](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs) · [N8/N9](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_direct.rs)

На job приходится один stock build. Измерения используют `verify-std -Z unstable-options -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing --no-assert-contracts`, точные `--harness` с `--exact`, stock CaDiCaL, CBMC 6.11.0, штатные safety, reachability, overflow и unwind. Uninit и validity выключены. Каждый слот получает свежий cwd и отдельные Cargo target, Kani target и JSON export. В receipt попадают фактические argv, cfg, jobs, OB и resolved unwind из доступного stock export. Index и setup связывают runner, пины, версии и проверки чистоты. [Сбор команд и аттестация](/root/kani-cal1-control-w11/ch8-cal1/run.py)

| Ubuntu, порядок | Exact selector после `slice::sort::shared::smallsort::verify::` | OB | Окно, с |
| --- | --- | ---: | ---: |
| `NET-U8-N08` | `cal1_direct::cal1_net_u8_n08` | 12 | 300 |
| `NET-U8-N09` | `cal1_direct::cal1_net_u8_n09` | 12 | 300 |
| `S13-N13-OB12` | `cal1::nm_sort13_left_len13` | 12 | 1080 |
| `S13-N13-OB11` | `cal1::nm_sort13_left_len13` | 11 | 1080 |
| `MERGE-N32-BELOW-OB12` | `cal1::mw_merge_n32` | 12 | 780 |
| `MERGE-N32-MASK-OB12` | `cal1::mw_merge_n32` | 12 | 780 |

На Ubuntu шесть singleton `--jobs=1` суммарно занимают 72 мин окон. Номинальный cap 10 GiB, резерв 2 GiB. На macOS сохранены 11 singleton CAL1 с OB12, cfg CAL1 и суммой окон 139 мин. Оба batch по 600 с получают одну фиксированную пару N8/N9, сначала с незаданным `KANI_JOBS` и `-j`, затем `KANI_JOBS=1 --jobs=1`. Допуск требует завершённых singleton с полными результатами, суммы wall с запасом 30 с и суммы пиков в пределах 80% effective batch cap. Job macOS допускается независимо от прогресса Ubuntu. [Frozen roster](/root/kani-cal1-control-w11/ch8-cal1/CI-REQUEST.json) · [Допуск batch](/root/kani-cal1-control-w11/ch8-cal1/run.py)

В Darwin только cfg-on `list_one` на overlay и cfg-off `list_one` на base получают 7 340 032 KiB. Build, preflight, singleton и batch получают 5 767 168 KiB. Effective cap равен `min(nominal, available − reserve)` с резервом 1 310 720 KiB. У обоих list есть phase, admission memory, nominal/effective cap, status и первопричина сбоя. Cfg-on сверяет 11 уникальных регистраций CAL1 и двух провайдеров. Cfg-off выполняется на точном base. Сценарий партиций использует по одной регистрации каждого селектора, вклад Ubuntu считает по OB12 и Below. Общий дедлайн setup составляет 45 мин, latest start требует окно и 10 с headroom до 202-й минуты. Внутри слота выделены 10 с на TERM/KILL/reap и 5 с на фиксацию. До 204-й минуты идёт итоговая аттестация, затем 12 мин на финализацию/upload и 9 мин резерва до границы job 225 мин. [Discovery и часы](/root/kani-cal1-control-w11/ch8-cal1/run.py)

## Поля измерений и отсечки

| Свидетельство | Поля |
| --- | --- |
| Исход | `outcome`, `reason`, `censored`, supervisor `stop_reason`/ `primary_stop_reason`, exit/signal, sampler и reap. `VERIFIED`/ `FAILED` требуют согласованного терминала и stock export. Выход OB11 с сообщением CBMC `too many addressed objects` получает `OBJECT_BITS_EXHAUSTED`. |
| Тайминг | Wall, VT с источником, compile/Symex/SSA/SAT при наблюдении, последняя фаза и её время, covers и resolved config. Отсечённое окно остаётся censored. |
| RSS и PSS | Пик группы и RSS CBMC из его census, отдельный пик суммы CBMC RSS, последний валидный RSS-сэмпл, фаза и время, счётчики cadence. Сэмпл хранит `cbmc_count`, per-PID RSS и start identity. PSS относится к одному выбранному CBMC PID из того же census, учитывает результат чтения и задержку. При отсутствии PSS на пике сохраняется ближайший валидный RSS/PSS-сэмпл со своим временем. |
| Native CNF | Первая точная пара variables/clauses в каждом потоке, до семи последующих пар, байтовая и строковая координаты, фаза, native timestamp при наличии. Явные cover/reachability markers и последующие записи сохраняют свой контекст. Число для начального solve остаётся `null`, если атрибуции недостаточно. Префикс, отсутствие маркера и неполная строка различаются. Также сохраняются Symex, SSA, SAT, VCC и terminal. |
| Предельные и частичные состояния | `RSS_LIMIT`, `TIMEOUT`, `LIVE_MEMORY_PRESSURE`, `LIVE_MEMORY_RESERVE`, `NOT_STARTED` с причиной или `NOT_RUN` для недопущенного batch. Недостоверная очистка останавливает последующие слоты и итоговые tool probes. Именные receipts сохраняются при ошибке setup. |

PSS читает точный ключ `Pss:` из `smaps_rollup`, проверяет start identity по обе стороны чтения и допускает один незавершённый запрос на Linux job с интервалом от 1 с. Ошибка, смена PID, просрочка и недоставленный результат дают `null` с причиной. Supervisor пользуется прежним групповым RSS и pressure и не ждёт PSS. Публикуются до 128 строк серии плюс отдельные ключевые записи с числом пропусков. Ограничения 4 MiB на проекцию и 96 MiB на job сохраняются. В обязательных receipts остаются компактные метрики даже после снятия optional projection или timeline. Index сохраняет run/attempt, platform, trigger SHA/tree и SHA-256 членов. Полные логи и dumps остаются рабочими файлами runner. [RSS и PSS](/root/kani-cal1-control-w11/ch8-cal1/telemetry.py) · [Native metrics](/root/kani-cal1-control-w11/ch8-cal1/native_metrics.py) · [Публикация](/root/kani-cal1-control-w11/ch8-cal1/report.py)

В A/B сводках показаны оба набора условий допуска, включая effective cap, начальный available и давление. Их различия ограничивают сравнение. PSS выбранного CBMC оставляет PSS группы неизвестным. Выборочный RSS сохраняет caveat CAL1 о смене TID после завершения лидера. Ориентиры 120 с VT, 180 с cold wall, 4 GiB на singleton, 10 GiB для Linux jobs=2 и 5 GiB для Darwin jobs=1 имеют статус `ADVISORY`. [Связь с CAL1](CAL1-RESULTS-ANALYSIS.md#рабочие-ориентиры-времени-и-памяти)

## Локальная проверка

- `python3 -B -m unittest discover -q` в `ch8-cal1` — 78 тестов. Darwin проверен синтетически. Сценарии включают mutation checks request, roster и normalized argv, две discovery-стадии с ограничением available, Linux setup/cutoff и независимый допуск Mac, latest start, отсутствие запуска после недостоверной очистки, same-sample RSS, задержку/лимит PSS, CNF из префикса и сохранность обязательных A/B метрик при усечении.
- `git diff --check`, разбор workflow PyYAML и `bash -n` для 12 развёрнутых shell-шагов. Отдельный shallow checkout std base принял `git bundle verify` и `unbundle` без записи refs. Сверены layout, хэши, ancestry, идентичность trigger и exact push metadata. Подмена SHA, ref и attempt отклонена.
- Нативные локальные `stress_supervisor.py rss-stop`, `pid-race` и `churn` сохранили подтверждённые sampler и reap. RSS-stop завершился по `RSS_LIMIT` при 66 812 KiB и cap 24 576 KiB. PID race завершился `EXITED` с отслеженным пропуском PID. Churn завершился `EXITED`, exit 0, за 182,40 с с 608 валидными сэмплами и нулём пропущенных сэмплов. Пик RSS составил 73 472 KiB при cap 163 840 KiB, во время census пропущено 107 PID-записей.
- Пакет, trigger и записи g0 подготовлены локально. CI, push, Cargo, rustc, Kani и CBMC не запускались.

[Независимое ревью](CAL2-REVIEW.md)
