# REV2 · стоимость провайдеров sort13 и merge N32

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`.

Пакет подготовлен локально по заданию из g0 `24bde98273a8c1be2aa9942f75dd99f9cf0c0144`. Файл задания сверен с этим коммитом побайтно. Compile preflight, discovery, исходы свойств и ресурсные измерения имеют статус `UNKNOWN` до первого согласованного прогона. [Задание](REV2-NETWORK-PROVIDERS-TASK.md) · [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)

## Ревизии и файлы для ревью

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Std base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| Std CAL1 | `080a0104159fd04b6764a24f8538a97588f6612e` | `96f95b8082983b57f203b0e3e12151552dba0f76` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Std CAL2 | `043a1f19f9d36eb1666979f97b8e7e483ab41c5e` | `1361a0da67b9bd21fc7c77a941582d0fd17b9a8d` | `080a0104159fd04b6764a24f8538a97588f6612e` |
| Std REV2 | `2dc2ca13fc12cf2c644faf982245740b20ca0f93` | `6b55a33da0ee7877caa06ca258ea1e43a1c4f0fb` | `043a1f19f9d36eb1666979f97b8e7e483ab41c5e` |
| Control REV2 | `bccbabf84d77fbc227862b5650baab506f3f580f` | `f6c3fde21f021e0821d7c8b9af1e3fe2c45fd58c` | `1b65866c1b037767d7ccf3262d05098ed9b2dc2b` |
| Локальный review-trigger | `0dd7dc95fff8f944b1250bb41fae8ae9b1161562` | `f6c3fde21f021e0821d7c8b9af1e3fe2c45fd58c` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |

- Std `rev2-network-providers-w11` от CAL2. [Worktree](/root/verify-rust-std-rev2-network-providers-w11) · [Diff от CAL2](/root/rev2-network-providers-review/std-from-cal2.patch) · [Четыре корня](/root/verify-rust-std-rev2-network-providers-w11/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs)
- Control `work/rev2-network-providers-control-w11` от Darwin FIX8. Локальный trigger находится в `local/rev2-network-providers-trigger-review`. [Worktree](/root/kani-rev2-network-providers-control-w11) · [Diff от FIX8](/root/rev2-network-providers-review/control-from-fix8.patch) · [Diff trigger от sole parent](/root/rev2-network-providers-review/trigger-from-sole-parent.patch)

| Файл | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-network-providers-control-w11/ch8-cal1/CI-REQUEST.json) | `7158ccd6a77adc7fcf77c8ac96de79b0bdb3387d02642251f071695e33be1090` |
| [std-overlay.bundle](/root/kani-rev2-network-providers-control-w11/ch8-cal1/std-overlay.bundle) | `13998042fc47aa31a6ded6384310c6b48c658b8612afd37aabd07a698184a8e4` |

Bundle требует `dab03cf510df5c35141cde49f1368b1242f5035e`, рекламирует один `HEAD` Std REV2 и содержит три последовательных overlay commit. Guard сверяет SHA-256, commit/tree/sole parent всей цепочки, список refs bundle и layout. Разрешённый push gate использует `Tiramisu-Cake/kani`, событие `push`, `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt `1` и `contents: read`. Checkout в `control` берёт `github.sha`. Валидатор сверяет SHA с `after` payload, реальный checkout с требуемым sole parent и tree с единственным `REV2-Control-Tree` в commit trailer. Для будущего trigger после GO зафиксированы tree `f6c3fde21f021e0821d7c8b9af1e3fe2c45fd58c` и sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Точное значение tree для сверки при допуске берётся из этой строки handoff. Локальный review-trigger, std и control используют авторство `Tiramisu-Cake <igkharin@gmail.com>` и имеют `[skip ci]` в сообщениях. [Workflow](/root/kani-rev2-network-providers-control-w11/.github/workflows/ch8-q-pilot.yml) · [Guard](/root/kani-rev2-network-providers-control-w11/ch8-cal1/request.py)

## Точный roster и домены

| Слот | Exact selector | Роль |
| --- | --- | --- |
| `S13-SWAP-LEAF` | `slice::sort::shared::smallsort::verify::rev2_provider_cost::s13_swap_leaf` | Check actual `swap_if_less`, stubs отсутствуют |
| `S13-PLAIN-BYTE` | `slice::sort::shared::smallsort::verify::rev2_provider_cost::s13_plain_byte` | Proof actual `sort13_optimal` с одним `stub_verified(swap_if_less)` |
| `M32-PLAIN-MASK` | `slice::sort::shared::smallsort::verify::rev2_provider_cost::m32_plain_mask` | Proof actual `bidirectional_merge`, `merge_up` и `merge_down`, stubs отсутствуют |
| `M32-PAIR-STEP` | `slice::sort::shared::smallsort::verify::rev2_provider_cost::m32_pair_step` | Check verification-only `actual_pair_step` с возвратом `()`, actual `merge_up` и `merge_down` |

- **Лист S13.** Произвольный initialized `[u8; 34]` с base 1 и независимым `q: u8`. Компаратор `KeyLess<u8>` сравнивает полные байты. Действующие safety preconditions и два тонких `modifies` targets сохранены. `old` читает два разрешённых байта. Post проверяет точные `min/max` и `q` frame, harness проверяет остальные 32 ячейки. Covers проверяют обе ветви, равенство в разных ячейках, mixed q, нормальный возврат и исполнение actual comparator.
- **Plain S13.** Тот же V34, `v[1..14]` и независимый q. Harness проверяет CAL2 presort geometry, числовой порядок, сохранение числа `<q` для произвольного q, q-frame и байты за пределами среза. В режиме Replace stock Kani проверяет preconditions листа на каждом вызове. Смысл восьми CAL2 input/return covers сохранён, actual comparator cover относится к листу. Исход plain при провале или отсечке листа остаётся условным. Область результата ограничена данным путём с одним Replace. Существующий Check `sort13_optimal` и его сводка сохраняют свою область.
- **Plain M32.** V34 с произвольными initialized половинами `[1..17]` и `[17..33]` в числовом неубывающем порядке. Pre порядка задан на входе fixture, применимость read/write/disjoint проверяется явно. Независимый q и отдельный `MaybeUninit<[u8; 32]>` scratch от offset 0. CAL2 Mask проверяет весь результат после 16 actual пар записей и прохождения реального финального cursor guard. Пары записывают `scratch[k]` и `scratch[31-k]` для каждого `k` от 0 до 15. Проверяются q/source V34 frame и CAL2 covers, включая cross-half tie и interleaving. Чтение scratch происходит после заполнения, область измерения ограничена чётным N32.
- **Шаг M32.** Та же V34 геометрия и scratch. При произвольном `0 ≤ k < 16` суммы левого и правого потребления равны `k` отдельно для up и down. Эти границы обеспечивают in-bounds для четырёх чтений и допускают общее исчерпание половины. Check задаёт два точных `modifies` targets, исполняет обе actual копии и проверяет обе тройки курсоров. Up при равенстве выбирает левый, down правый. Граничные `wrapping_sub` используются в проверке указателей. Harness читает только два записанных байта, сравнивает их с oracle и проверяет q/source frame. Covers включают обе стороны в каждом направлении, ties, `k=0`, `k=15` и нормальный возврат. Область леммы ограничена одним шагом. Применимость полного прохода к потребителю требует отдельной механической границы.

Статическая сверка `sort13_optimal` дала **45/45** подходящих call sites, **37** различных пар на этих сайтах и **78** пар во всём явно заданном домене `0 ≤ a < b < 13`. Значение 45 в задании соответствует числу call sites. Проверен порядок всех вызовов и отсутствие записей в backing из остального тела `sort13_optimal`.

```text
(0,12) (1,10) (2,9) (3,7) (5,11) (6,8) (1,6) (2,3) (4,11)
(7,9) (8,10) (0,4) (1,2) (3,6) (7,8) (9,10) (11,12) (4,6)
(5,9) (8,11) (10,12) (0,5) (3,8) (4,7) (6,11) (9,10) (0,1)
(2,5) (6,9) (7,8) (10,11) (1,3) (2,4) (5,6) (9,10) (1,2)
(3,4) (5,7) (6,8) (2,3) (4,5) (6,7) (8,9) (3,4) (5,6)
```

Все четыре корня требуют `kani` и одновременно `kani_smallsort_cal1`, `kani_smallsort_cal2_merge_mask`, `kani_smallsort_rev2_provider_cost`. Включение последних трёх cfg одинаково в compile preflight, единственном cfg-on list и четырёх измерениях. Roster сравнивает четыре exact selector и их категории Check/Proof, проверяя дубли и лишние регистрации REV2. Отсутствие новых регистраций вне cfg установлено статически по закрытому модулю и побайтовой сверке `verify.rs`. [Request](/root/kani-rev2-network-providers-control-w11/ch8-cal1/CI-REQUEST.json) · [Runner](/root/kani-rev2-network-providers-control-w11/ch8-cal1/run.py)

## Режим измерения и окна

Единственный job `ubuntu-24.04` разводит точные checkouts `control`, `std`, `tool` и state в `RUNNER_TEMP/ch8-rev2-provider-cost`. В setup выполняются один stock build, аттестация tool, cfg-on compile preflight с окном до 180 с и один cfg-on `kani list`. Setup наблюдается отдельно с унаследованным Ubuntu номиналом 10 GiB. Каждый singleton получает отдельный cwd, Cargo target, Kani target, tmp и JSON export, `--exact --jobs=1 --no-assert-contracts`, штатные safety/overflow/unwind, uninit и validity OFF, CBMC 6.11.0, stock CaDiCaL, OB12 и unwind 36. Для измерений номинал группы 4 194 304 KiB и резерв ОС 2 097 152 KiB. Effective cap учитывает доступную память при старте, live guard следит за резервом и давлением. [Workflow](/root/kani-rev2-network-providers-control-w11/.github/workflows/ch8-q-pilot.yml) · [Runner](/root/kani-rev2-network-providers-control-w11/ch8-cal1/run.py)

| Фаза | Бюджет | Конец от старта job clock |
| --- | ---: | ---: |
| Setup целиком | 45 мин | 45:00 |
| Четыре слота по 195 с + 10 с headroom на запуск | 13 мин 40 с | 58:40 |
| Итоговая аттестация | 2 мин | 60:40 |
| Финализация и upload | 5 + 7 мин | 72:40 |
| Резерв | 9 мин | 81:40 |
| Внешний предел job, включая ещё 8 мин 20 с запаса | 90 мин | 90:00 |

Внутри каждого окна 180 с cold wall, 10 с TERM/KILL/reap и 5 с на receipt. Короткая отсечка продолжает roster после подтверждённого reap и проверки следующего окна. `REAP_UNVERIFIED` и отказ supervisor блокируют последующие запуски и финальные tool probes. Метрики фиксируют момент окончания наблюдения отдельно от очистки. Проекции сохраняют фактические argv, cfg, OB, geometry, точную причину и фазу, symex/SSA/первую CNF либо причину её отсутствия, group/CBMC RSS до завершения процесса выдачи и PSS с координатами census. В регулярной проекции сохраняются exact ID, Location и status, в stock export сохраняются состояние, метаданные и failure/cover evidence. При частичном capture receipt держит доступные полевые свидетельства и явно указывает их охват. Компактные receipts переживают обрезку optional проекций и timelines. Лимиты составляют 4 MiB на проекцию и 96 MiB на job. Upload ограничен `artifact/`, полные логи и GOTO лежат в рабочем каталоге слота. [Супервизор](/root/kani-rev2-network-providers-control-w11/ch8-cal1/supervisor.py) · [Проекция результатов](/root/kani-rev2-network-providers-control-w11/ch8-cal1/results.py) · [Отчёт](/root/kani-rev2-network-providers-control-w11/ch8-cal1/report.py)

## Локальные проверки

- `rustfmt --check` прошёл для `smallsort.rs`, `smallsort/verify.rs` и `rev2_provider_cost.rs` с `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max --config skip_children=true,reorder_modules=false`. Дополнительные параметры ограничивают обход и сохраняют порядок унаследованных `mod`. `git diff --check` прошёл на std, control и trigger.
- Снятие opt-in атрибутов восстанавливает Git blob `smallsort.rs` побайтно до CAL2 и std base. Регистрация REV2 и одна lint-декларация снимаются до точных CAL2 blobs. Std diff содержит только четыре указанных layout path. Штатный std workflow побайтно совпадает с базой по дереву. Сверены четыре исходные регистрации, точные наборы именованных covers, 45 call sites, 16 пар scratch и границы всех независимых up/down счётчиков. `git bundle verify` и `unbundle` на shallow std base прошли с одним prereq/HEAD, проверенной ancestry и без создания refs. Три патча воспроизвели свои tree во временных Git index.
- `python3 -B -m unittest discover -q` на Linux, Python 3.12.3, прошёл **87/87** на detached review-trigger. Synthetic tests проверили exact roster, fork/event/ref/parent/tree, tool pin, cfg/OB/unwind, cap/deadline, раздельные cold paths, один список после preflight, partial receipt, exact ID/Location/status, заполнение отчёта на TIMEOUT/RSS_LIMIT и продолжение после reap. Проверены остановка после `REAP_UNVERIFIED`, отсутствие PSS при сбое sampler thread и VT порог листа. Native supervisor `rss-stop` дал `RSS_LIMIT`, `sampler_valid=true`, `reaped=true` и пик 67 792 KiB при синтетическом cap 24 576 KiB. `pid-race` завершился `EXITED` с `sampler_valid=true`, `reaped=true` и одним пропущенным PID. Darwin tests выполнены синтетически.
- PyYAML подтвердил одну Ubuntu job с точным gate и `bash -n` прошёл на шести shell steps. `run.py pins` на настоящем detached checkout принял синтетическое событие для точного trigger. Десять мутаций отклонены, включая другой event/ref/attempt, рассогласование SHA или payload, неверный sole parent при том же tree и неверное объявление tree. Cargo, rustc, Kani, CBMC, CI, push и публикация в этом этапе не запускались.

## Критерии после первого прогона

Завершённые корни оцениваются по `VT ≤120 с`, cold wall `≤180 с`, sampled group RSS `≤4 GiB`, полному результату и требуемым covers. Порог VT действует и для листа, и для диагностического шага. Совместный успех `S13-SWAP-LEAF`, `S13-PLAIN-BYTE` и `M32-PLAIN-MASK` в заданных пределах даёт основание для одного matched macOS прогона и измерения actual consumers. Он оставляет отдельными проверками N17, N18/19, правый sort13, odd merge, новые ширины и штатные партиции.

Если в пределах остаются только лист и пара шагов, текущий прямой путь не достигает лимита. Следующее исследование строится на двух направленных проходах с инвариантом курсоров и механической связью с actual циклом. Случаи 130–200 с остаются за пределами текущей приёмки. Любой дальнейший запуск требует независимого diff-ревью и отдельного GO. [Задание](REV2-NETWORK-PROVIDERS-TASK.md) · [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)
