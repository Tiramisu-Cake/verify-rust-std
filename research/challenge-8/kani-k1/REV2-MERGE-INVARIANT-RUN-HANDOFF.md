# REV2 · пакет диагностики actual merge N32

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. Ревью допускает диагностическую пару после отдельного разрешения на точное дерево пакета. Компиляция, native binding, исходы и профиль ресурсов имеют статус `UNKNOWN`. [Независимое ревью Std](REV2-MERGE-INVARIANT-REVIEW.md) · [Handoff инварианта](REV2-MERGE-INVARIANT-HANDOFF.md)

## Идентичности

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| g0 review | `50aa46da5c6510266911af5833a794b9f0fb9554` | `f0b0b78bb495931fe9d202534a7919bca2cc9e35` | `01a578cc9ed84b18bc679573c6ea163782fa7c7c` |
| Control base S13 | `4beae2f1b03f6e88abd8dc673eb5a37b835f2dd3` | `c58dac28828becef22d4a3959be30f1b2204310a` | `0dcc435f7d3f7e73a7ae362445e385e1747cedc9` |
| Control merge | `765bc94c259ae5ee3d2da6ac346c1e44f7591345` | `2d174fdf1ab03db12560727416a84824af1b2689` | `4beae2f1b03f6e88abd8dc673eb5a37b835f2dd3` |
| Локальный review-trigger | `d124161f7df0cfd81c7e94dcc230b3caff2ef5b8` | `2d174fdf1ab03db12560727416a84824af1b2689` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Std positive | `59bab95385d17bb2968d1ce53bc9afffb85b3616` | `ad714e9b41713edb5da4424ce37457dc73265ea4` | `32129c149a15fb1b60a7314e738f3cb466d076e5` |
| Std step control | `0e01dba89a3ffb02c362b59d6454ca2ad43b0aca` | `89100303bef85458e35857aa860bf464c2e8b2a1` | `59bab95385d17bb2968d1ce53bc9afffb85b3616` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | — |

Control находится в `/root/kani-rev2-merge-invariant-control-w15`, ветка `work/rev2-merge-invariant-control-w15`. Локальный trigger закреплён в `refs/heads/review/rev2-merge-invariant-trigger-w15`. Отрицательный Std расположен в `/root/verify-rust-std-rev2-merge-invariant-control-w15`. Diff control для ревью берётся между указанными control base и commit, diff trigger — от его собственного parent. [Control workflow](/root/kani-rev2-merge-invariant-control-w15/.github/workflows/ch8-q-pilot.yml) · [Std control](/root/verify-rust-std-rev2-merge-invariant-control-w15/library/core/src/slice/sort/shared/smallsort.rs:1036)

| Вход | SHA-256 или идентичность |
| --- | --- |
| Frozen JSON | `210b1a4e2b361141a16fe705e839086b48e896a46b8934333a4b11cac349b914` |
| Канонический JSON roster | `9ffaf488c02754d61ad469e39f461353cc8060d21854701cc464cc0bacd61e6a` |
| Std bundle | `e9dede6ff871b6f82e88d7eafba7686ae0a5f98c1b5fd41f772b5e8cd1386325`, 18 049 bytes |
| Bundle prerequisite | `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655` |
| Bundle advertised ref | `0e01dba89a3ffb02c362b59d6454ca2ad43b0aca HEAD` |

Один импорт добавляет цепочку CAL1 → CAL2 → FIX3 → positive → step control в object store. Guard сверяет все деревья и родителей, затем восстанавливает cfg-off blobs FIX3 из positive и проверяет отдельную однострочную дельту control. В рабочей Std-копии runner выполняет preflight и один cfg-on discovery на positive. После подтверждённого reap он переключает этот checkout на negative и повторно проверяет его идентичность. Оба запуска используют отдельные каталоги cwd, target, tmp и export. [Frozen request](/root/kani-rev2-merge-invariant-control-w15/ch8-cal1/CI-REQUEST.json) · [Проверка layout](/root/kani-rev2-merge-invariant-control-w15/ch8-cal1/request.py)

## Пара и критерий

Оба слота выбирают один exact selector `slice::sort::shared::smallsort::verify::rev2_merge_invariant::m32_actual_merge_invariant`. Discovery требует одну регистрацию этого Proof и отклоняет лишние регистрации экспериментальных модулей. В обоих слотах действуют `kani_smallsort_cal1` и `kani_smallsort_rev2_merge_invariant`. Обычный cfg-off проверен статически по точным blobs. [Setup и discovery](/root/kani-rev2-merge-invariant-control-w15/ch8-cal1/run.py)

| Слот | Std | Ожидаемые нативные свойства |
| --- | --- | --- |
| `M32-NATIVE-INVARIANT` | Ревьюированный positive | Exit 0 и согласованный `VERIFIED`. Достигнутые base/step на actual merge, asserts геометрии, порогового поста и frame, covers actual компаратора, крайних q, mixed q, tie и normal return |
| `M32-STEP-CONTROL` | Однострочный control | Exit 1 и согласованный `FAILED`. База проходит. Единственный `FAILURE` — `loop_invariant_step` того же actual цикла. Определяющая дельта `&& kani::index != 1` в `Some` на строке 1036 различает переход `0 → 1`. Исходный `for` остаётся на строке 1044 |

Matcher сверяет регулярный вывод и stock export, включая точный selector и профиль, terminal/exit, класс, property ID, описание и координаты единственного failure. Base и step должны относиться к одному нативному loop ID в `bidirectional_merge`. Допустимы координаты 1029–1047 в точном `smallsort.rs`, поскольку macro expansion может привязать property к выражению invariant или rewritten head/latch. Номер свойства не фиксирован между сборками. Добавочный safety/unwind failure, неполная проекция, ложная база и отказ другого цикла исключают `MATCHED`. `loop_assigns` может быть недостижим без родительского write set. Применимые assigns, цели write set и actual stores сверяются отдельно по диагностике. [Сопоставление свойств](/root/kani-rev2-merge-invariant-control-w15/ch8-cal1/results.py)

Наблюдатель PATH включён только внутри измеряемых слотов и переадресует stock `goto-instrument` с прежними аргументами и exit/signal. На точном in-place DFCC вызове для ожидаемого harness он сохраняет digest обоих GOTO и ограниченные выдержки фактической функции до и после преобразования. В receipt есть выбранный символ, argv `--dfcc`, `--apply-loop-contracts`, `--loop-contracts-no-unwind`, `--disable-loop-contracts-side-effect-check`, тождество исполняемого файла и доступность каждого наблюдения. Pre-DFCC IR дополнительно проецирует части guard с `#spec_assigns` и `#spec_loop_invariant`. Каждое чтение GOTO ограничено 512 MiB и 1,5 с при хешировании. Каждый scan ограничен 32 MiB и 1,5 с. В артефакт входят хеши и компактный `loop-capture.json` с выбранными секциями, coverage и причинами пропусков. Оба прогона учитывают накладные наблюдателя в cold wall и RSS. Source/GOTO/loop-ID и footprint требуют отдельной сверки при ревью результата. Неполное наблюдение остаётся `UNKNOWN` для привязки и не повышает результат проверки. [Наблюдатель](/root/kani-rev2-merge-invariant-control-w15/ch8-cal1/loop_capture.py)

## Gate и бюджет

Для отдельного разрешения координатору потребуется закрепить Actions variable `CH8_REV2_MERGE_INVARIANT_TRIGGER_TREE=2d174fdf1ab03db12560727416a84824af1b2689`. Workflow передаёт её как `REV2_MERGE_INVARIANT_TRIGGER_TREE`. `pins` и `finish` вычисляют фактический `HEAD^{tree}` и сравнивают с этой переменной. Также проверяются `Tiramisu-Cake/kani`, push ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, `after` payload, единственный родитель и чистый detached checkout. Согласованные payload и trailer не разрешают дерево с несовпадающим независимым pin. `finish` повторно сверяет начальный receipt. Upload зависит от его успешного завершения. Значение Actions variable не выставлялось. [Проверка gate](/root/kani-rev2-merge-invariant-control-w15/ch8-cal1/request.py)

Ubuntu 24.04, stock Kani и CBMC 6.11.0/CaDiCaL, OB12, unwind 36, `--exact --jobs=1 --no-assert-contracts -Z loop-contracts`. Штатные safety/overflow/unwind ON, uninit/validity OFF. Пик sampled group RSS ≤4 GiB на слот, резерв Ubuntu ≥2 GiB, setup cap 10 GiB, VT ≤120 с для отбора. От общего monotonic epoch setup до 45:00, два слота с launch headroom до 51:50, аттестация до 53:50, finish/upload до 65:50, резерв до 74:50 при внешних 75 мин. Workflow ставит 45 мин для prepare, 55 для measure, 13 для finish и 7 для upload. Внутренний finish ограничен 720 с и абсолютным дедлайном. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md) · [Workflow](/root/kani-rev2-merge-invariant-control-w15/.github/workflows/ch8-q-pilot.yml)

В слоте 180 с cold wall, 10 с на TERM/KILL/reap и 5 с на receipt. Реальный исход child и reap атомарно сохраняются перед необязательной проекцией. У проекции абсолютная отсечка `start+194`, у финальной атомарной записи `start+195`. Задержка или прерывание записи позволяет повторить её за цепочкой слотов в ограниченном окне. Поздний receipt сохраняет исход, timestamps и отдельный `receipt_deadline_exceeded`. Неподтверждённый reap блокирует следующий слот. Полнота свидетельства, вердикт child и попадание в профиль различаются. Верхняя граница наблюдений составляет 4 MiB для projection и 96 MiB для артефакта. [Дедлайны и receipts](/root/kani-rev2-merge-invariant-control-w15/ch8-cal1/run.py) · [Финализация](/root/kani-rev2-merge-invariant-control-w15/ch8-cal1/report.py)

## Локальные проверки

- Финальный Python 3.12 suite прошёл 104/104 за 23,245 с на обычных часах и 104/104 за 23,573 с через shell-блок `pins` на exact shallow detached trigger со шкалой `time.monotonic() = 60 + elapsed`. Проверены разные Std trees в двух слотах, отсутствие лишних селекторов, посторонний safety failure, медленная проекция, поздний receipt и retry после ошибки записи, отсутствие reap и deadline `finish`. Ошибочный независимый pin отклонил `pins` и `finish` того же trigger. С верным pin оба entrypoint прошли, а синтетический finish вывел два `NOT_STARTED`. Промежуточный тест наблюдаемого потомка однажды вернул `REAP_UNVERIFIED`, затем целевой повтор и оба финальных suite прошли.
- YAML разобран с проверкой дубликатов, подтверждены одна job, ref, новая Actions variable и бюджеты. `bash -n` прошёл для всех шести `run`-блоков.
- `git bundle verify`, `list-heads` и `unbundle` прошли на bare shallow base глубины 2 с общим object store. Сверены требуемый base, advertised HEAD, commit/tree/parent пяти overlays, сохранение refs и точный source layout.
- `rustfmt --check` прошёл для обоих Std деревьев заданным `nightly-2026-11-19` с `use_small_heuristics=Max`, `skip_children=true,reorder_modules=false`. `git diff --check` прошёл для positive, step control, пакета, trigger и этого handoff.
- Использовались только статические проверки, Python-тесты и локальный Git. Cargo, rustc, Kani, CBMC, CI, push и публикация не выполнялись.
