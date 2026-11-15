# B3 — perf после переноса на новый upstream: запрос внешнему аудитору

2026-11-15. Координатор и планер. Это верификация корректности, не security-работа.
CI выполнялся в форке Tiramisu-Cake/kani; при подготовке этой редакции сборки и CI не запускались.
Upstream PR B3 не подан. Текущий PR-черновик: `kani3300/b3p/PR-UPSTREAM.md` @ t0 `da703d8310`;
его perf-абзац требует обновления по результатам ниже, сам PR-черновик этой редакцией не изменён.

## 1. Предмет и установленное расхождение

B3 обходит CBMC 6.11.0 invariant в `bits2expr`: typed copy padded union-arm с массивом нулевой ширины
может завершить CBMC abort. В padded physical wrapper полностью нулевой payload заменяется существующим unit-типом;
исходный logical type union-field сохраняется. Арм ненулевой ширины с ZST-массивом внутри остаётся вне этого обхода.
Это отдельный фикс, без Part 1 / MaybeUninit shadow-transfer изменений.

- На старой базе `bf9c58e662` у v1–v3 зарегистрирован успешный perf job каждой версии.
  Workflows в целом cancelled, поэтому «полный CI каждой версии зелёный» неверно.
- v4 `3d9a180938` переносит v3 на upstream `0aac16ef62`: executable Rust delta и новые тесты те же,
  изменён лишь комментарий. Между базами 13 upstream-коммитов.
- На v4 три perf jobs потеряли связь с раннером: две GitHub attempts одного run и отдельный парный run.
  Это **не три доказанных OOM и не три независимых измерения максимальной памяти**.
- На чистом `0aac16ef62` два полных perf control jobs успешны; последний запущен парой с v4 на одинаковой обвязке.
- Watchdog diagnostic отдельно остановил CBMC при низком MemAvailable; `s2n-quic-core` FAILED, остальные 14 тестов ok
  по сводке координатора. Watchdog изменяет выполнение и не является штатным perf-прогоном.

Вывод «B3 не влияет на perf, потому что формулы совпадают» не подтверждён. Наблюдается повторяемое различие исходов
main/v4 в этой небольшой выборке, но причинность, виновный harness и природа потери раннера пока не установлены.
Нужна оценка диагностического плана и достаточности будущих результатов для подачи PR, без заранее выбранного виновника.

## 2. Версии и точная граница изменения

| Версия / fork branch | Head | Upstream parent/base | Изменение |
|---|---|---|---|
| v1 `fix/zst-union-codegen` | `6db3c4dabd` | `bf9c58e662`, цепочка из 3 коммитов | tests → fix с `sizeof_in_bits` → перенос тестов в general expected |
| v2 `fix/zst-union-codegen-v2` | `83a413f9be` | `bf9c58e662`, 1 коммит | точный tree v1, только squash |
| v3 `fix/zst-union-codegen-v3` | `6e9e782024` | `bf9c58e662`, 1 коммит | решение по rustc layout вместо GOTO sizeof, recursive/edge tests |
| v4 `fix/zst-union-codegen-v4` | `3d9a180938` | `0aac16ef62`, 1 коммит | тот же fix/test patch, уточнён комментарий о CBMC |

Heads проверены по fork branch API; историю/patches — по Git. Локальная старая ветка `v3` может указывать на
не собиравшийся `495614a5ee`; это не проверенный fork v3 `6e9e782024` (исправлен cast `union_size as u64`).
Для аудита ориентироваться на SHA, не на локальное короткое имя ветки.
Свидетельство tree identity v1/v2: `b3p/TREE-CHECK.md`; внешний аудит v3: `b3p/AUDIT-EXTERNAL.md` @ t0 `e6fb9eb7ec`.

v3 и v4 каждый меняют 17 файлов (+437/−2): `codegen/typ.rs` и expected tests; workflows в этих коммитах не менялись.
Сравнение parent→head patches исключая index/номера строк показывает только изменение поясняющего комментария.
Это не равенство полного дерева или бинарника на разных upstream-базах.
Код v4 в `kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs`, `codegen_union`:

```rust
ctx.ensure_struct(struct_name, pretty_struct_name, |ctx, _| {
    let payload = if *padding == union_size as u64 { ctx.codegen_ty_unit() } else { ty.clone() };
    vec![DatatypeComponent::field(name, payload), pad.clone()]
})
```

Условие применяется внутри padded wrapper: размер поля и padding берутся из rustc layout; заменяется только
нулевой payload. Nonzero arms и all-ZST unions без padding не меняются. У обычного `MaybeUninit<T>::uninit: ()`
payload уже unit; нельзя без проверки считать все MaybeUninit новым изменённым shape.
Регрессионные входы: `tests/expected/zst-union-arm` и 7 single-harness edge/recursive каталогов.
Базовый probe [43626647584](https://github.com/Tiramisu-Cake/kani/actions/runs/43626647584), CI head `a81875c5ae`,
по сводке координатора подтверждает invariant без B3 на новом main; зелёный diagnostic workflow сам по себе
не доказывает успешную верификацию. Старые `RESULT-KANI-B3P.md`/`REVIEW.md` относятся к упаковке v2, не к perf v4.

## 3. Что изменилось между upstream-базами

`bf9c58e662..0aac16ef62`: 13 коммитов; `git diff --name-only` и `--shortstat` дают 131 файл (+4118/−208).
Список: #5058 async executor aliasing UB; #5152 tail calls; #5138 macOS CI; #5153 specialization default;
#5063 determine_targets; #5012 serde-saphyr; #5066 enum niche; #5092 show-properties parser;
#5134 loop contracts; #5057 validity initialization/projections; #5093 clause-depth arithmetic;
#5115 atomic stores/init tracking; #5154 RFC0015 tests.

В `codegen_cprover_gotoc` поменялись только `intrinsic.rs` и `rvalue.rs` (+9/−14):
удалено лишнее чтение старого atomic-store value и расширена константа niche arithmetic u64→u128.
Менялись также MIR transforms, output parsing и compiletest dependencies: это кандидаты для проверки пересечения
с workload, а не доказанные источники расхода. Не предполагаем, что experimental uninit/validity paths включены в perf.

При этом между обеими базами и v4 неизменны `tests/perf`, `scripts/kani-perf.sh` (blob `d2bb43fb97`),
`kani-dependencies`, `rust-toolchain.toml` и s2n submodule `be829a473881163369f7df4c739232ebbd1e7d27`.
Штатный perf job в `kani.yml` также тот же; изменена только macOS regression matrix.
Пины файлов не фиксируют runner image, полученные package versions, фактические solver binaries или ASLR/нагрузку хоста.

## 4. Run/source/обвязка и исходы

Все строки — perf job на `ubuntu-24.04`; nominal RAM 16 GB, фактические лимиты каждого раннера не сверены.
Длительности ниже — **wall time job по API**, включая setup/обнаружение потери связи, не время отдельного solver.

| Run | Tool source / CI head | Наблюдение |
|---|---|---|
| [43117729467](https://github.com/Tiramisu-Cake/kani/actions/runs/43117729467) | v1 `6db3c4dabd` | perf success, 44m20s; workflow cancelled |
| [43184599218](https://github.com/Tiramisu-Cake/kani/actions/runs/43184599218) | v2 `83a413f9be` | perf success, 39m41s; workflow cancelled |
| [43239475977](https://github.com/Tiramisu-Cake/kani/actions/runs/43239475977) | v3 `6e9e782024` | perf success, 44m05s; workflow cancelled |
| [43605511755 attempt 1](https://github.com/Tiramisu-Cake/kani/actions/runs/43605511755/attempts/1) | v4 `3d9a180938` | job failure + lost-runner annotation, 73m01s |
| [43605511755 attempt 2](https://github.com/Tiramisu-Cake/kani/actions/runs/43605511755/attempts/2) | v4 `3d9a180938` | job failure + та же annotation, 73m00s |
| [43620855491](https://github.com/Tiramisu-Cake/kani/actions/runs/43620855491) | v4 / `8498acecc3` | watchdog diagnostic, 34m01s; workflow success маскирует perf FAILURE |
| [43628958916](https://github.com/Tiramisu-Cake/kani/actions/runs/43628958916) | main `0aac16ef62` / `de44c9a6ac` | штатный perf control success, 42m31s |
| [43683645492](https://github.com/Tiramisu-Cake/kani/actions/runs/43683645492) | v4 / `e6380248717c` | paired perf + memory log; lost-runner annotation, 73m01s |
| [43683645556](https://github.com/Tiramisu-Cake/kani/actions/runs/43683645556) | main / `173b14553d50` | тот же paired recipe; success, 42m59s; 15/15 по сводке координатора |

Источник статусов/head/attempt/timestamps — GitHub Actions API; аннотации check runs всех трёх потерянных jobs
проверены отдельно. GitHub сообщает потерю связи и перечисляет CPU/memory/network среди возможных причин;
это не OOM receipt. В первой attempt perf step помечен failure спустя ≈27 min, а job закрыт спустя 73 min:
по этим 73 min нельзя заключить, сколько работал CBMC. В других lost jobs нет завершённого perf step.
История attempts v2/v3 содержит унаследованные успешные perf entries с одинаковыми временами; это не новые независимые замеры.
Также штатная обвязка имеет `nick-fields/retry@v4`, 180 min/attempt, max_attempts=2, job cap380 min;
число GitHub attempts не равно числу внутренних запусков perf script.

CI-only heads имеют parent соответствующего tool source; watchdog/control/formula heads меняют лишь workflows,
последняя пара — `.github/workflows/*` и `.github/perfpair/run.sh`.
У двух paired heads workflow blob `0934cf0da7` и monitor script blob `892cf73a61` **одинаковы**.
Monitor раз в 60 s печатает MemAvailable и RSS только крупнейшего процесса, сохраняет exit perf script;
это sparse samples, не per-process peak RSS. Последний v4 job не сохранил диагностический поток для сравнения.

Watchdog `8498acecc3` проверяет память каждые 5 s, убивает CBMC при MemAvailable<1500 **MiB**;
по сводке координатора kill случился при 833 MiB (t≈1640 s), `s2n-quic-core` FAILED, 14 остальных ok.
Его `... | grep ... || true` маскирует исходный exit — workflow success не означает perf PASS.
В main paired run минимум **сэмплированного** MemAvailable — 1805 MiB по сводке координатора.
Ранее приведённые ≈6.9/10.6 GB RSS — округлённые samples без исходных KiB в этой сводке, не установленные peaks;
на них количественное сравнение не строится. MemAvailable — память всего хоста, не RSS CBMC.

## 5. Что показывает уже проведённая formula-диагностика

Пара [main 43634544624](https://github.com/Tiramisu-Cake/kani/actions/runs/43634544624) /
[v4 43634541874](https://github.com/Tiramisu-Cake/kani/actions/runs/43634541874), CI heads `d3f17ff4bb` / `d6f928bf85`.
Это release build и отдельный `cargo kani --tests --output-format old` для s2n-quic-core с memory watchdog;
не полный compiletest perf job. Source workflows пары идентичны; script выводит grep-selected summaries,
а исходный cargo-kani exit лишь печатается. Успех jobs не заменяет разбор per-harness verdicts.
По опубликованной сводке координатора: 40 harness имеют одинаковые `size of program expression` и вердикты;
у 10 с in-process solver совпадают vars/clauses, для остальных эти counts отсутствуют;
`sync::spsc::tests::alloc_test` опускал MemAvailable ниже 1 GiB в обоих вариантах.
Число40 относится к фактическому инвентарю этой диагностики; «34 harness» в старом комментарии perf script — не инвентарь.

Равные размеры/числа не доказывают равенство GOTO/SSA/CNF, порядка clause/variable/solver calls или памяти solver;
не исключают разные временные allocations и вклад других процессов. Для 30 harness сравнения vars/clauses нет.
Watchdog мог прерывать работу, а scope/обвязка отличаются от полного perf. Нет парных per-harness peak RSS,
полного model comparison или измерения всех 15 perf-тестов. Поэтому результат не снимает наблюдение раздела4.

## 6. Вопросы аудитору, в порядке приоритета

1. Какой вывод допустим из трёх lost jobs v4 против двух успешных main controls с учётом shared run/внутренних retries,
   отсутствия OOM receipt и малого числа измерений? Какое минимальное дополнительное свидетельство отличит
   compiler/solver resource effect от runner/infrastructure variability?
2. Достаточен ли следующий matched diagnostic package (раздел7), что в нём убрать/добавить до запуска?
   Как сохранить данные и original exits при отказе, не превратив защитный watchdog в новый perf-оракул?
3. В каких реальных perf types B3 меняет physical wrapper? Нужен ли сначала bounded census нулевых union arms
   и изменённых GOTO symbols/byte operations? Обычный unit arm MaybeUninit уже имел unit representation;
   просьба проверить actual changed shapes, а не предполагать широкое изменение всех MaybeUninit.
4. Если sizes/vars/clauses равны, какие данные наиболее полезны: actual solver argv/version/seed, retained-model hashes,
   byte-extract/simplification statistics, object/type widths, clause order или allocation profile? Как сравнивать
   модели с разными checkout paths, не нормализуя смысловые различия?
5. Может ли B3 менять расход на codegen/GOTO conversion/preprocessing/solver при неизменных итоговых counts,
   либо наблюдение объясняется параллельной памятью cargo/compiletest/внешних solvers? Как локализовать фазу и процесс?
6. После локализации нужен ли factorial old/new upstream × без/с B3 на одном harness? Когда оправдана бисекция
   13 коммитов, и какие из них вообще достигаются в данном default perf profile?
7. Есть ли более узкий или ресурсно устойчивый вариант Kani-обхода с той же семантикой, если causal regression подтвердится?
   Или предпочтительнее отдельно решать обновление CBMC? Это варианты решения, не одобренные здесь изменения dependency/scope.
8. Что нужно подтвердить до ready-for-review PR; уместен ли пока Draft с точным раскрытием наблюдения?
   Как сформулировать perf в PR без «тот же formula size ⇒ нет регрессии», без ложного PASS и без заявления OOM как факта?
9. Какие stop criteria достаточны: проблема не воспроизведена под новым observer, offender не найден,
   matched regression подтверждена, либо результаты ограничены вмешательством watchdog? Какой вывод допустим в каждом случае?

## 7. Предложенный план диагностики — НЕ ЗАПУСКАЛСЯ, решение владельца отдельно

**D0, без CI.** Сохранить source/tree, CI patch/script hashes и run/attempt/job identities; проверить pins submodules,
actual release/profile, solver/checks/flags и отсутствие других source changes. Уточнить доступные receipts/artifacts,
единицы памяти и происхождение каждой цифры; недостающие данные обозначить UNKNOWN. Новые full CI matrices не нужны.

**D1, один согласованный matched пакет main/v4.** Чистые отдельные builds, один и тот же workflow/observer,
`RUST_TEST_THREADS=1`, штатные perf inputs/overlays/timeout2400 и solver/object-bits/checks. Записать runner image,
RAM/cgroup limits, compiler/runtime/solver versions+hashes, submodule identities, effective argv, actual invocations и exits.
Явно одна попытка на плечо для диагностики; не смешивать её с исходным retry recipe. Любые дополнительные повторы — отдельно.
Привязать timestamps к perf-test/harness и фазе: compile/codegen, goto/preprocess, symex, SAT conversion, solve;
мерить RSS каждого CBMC/внешнего solver и суммарную память process tree, а не только top process/MemAvailable.
Сохранять bounded per-test/harness exit/signal/time/peak-RSS и фазовые counters, небольшой append-only journal,
failure/timeout/watchdog reasons; `always()` artifacts и stdout summary. Не `grep|head` как единственное evidence,
не `|| true` вместо original exit. Cap/time/disk/резерв RAM и process-group termination согласовать до запуска;
watchdog остановка = INCOMPLETE для performance comparison, не штатный verifier FAIL или PASS.
Hard runner loss может уничтожить upload даже при always; это GAP. Observer не должен сам создавать сопоставимый расход памяти.

**D2, только найденный offender.** Повторить минимальный test/harness обеих версий в том же solver/profile;
получить bounded type/GOTO/model comparison и phased counters/hashes. Если B3 arm replacement достигается,
сопоставить changed type → byte operation → различающуюся фазу/пик; при необходимости диагностический counter в codegen,
не подмена семантики фикса. Проверять гипотезу, а не только число новых clauses.

**D3, только при различающем сигнале.** Old/new upstream × без/с B3 на минимальном workload, затем при нужде бисекция
13 upstream commits с фиксированными fixtures и обвязкой. Если сигнал неустойчив или типы/модель не различаются,
зафиксировать неопределённость и согласовать ограниченные повторения/инфраструктурную диагностику вместо бесконечного bisect.
Любая production правка — отдельный reviewed candidate и новая квалификация, не незаметное исправление v4.

## 8. Граница проверки этой редакции

Непосредственно проверены Git source/patches/branch heads, CI-only workflows, Actions job metadata и lost-runner annotations.
Числа 833/1805 MiB, 14/15, 40/10 и per-harness outcomes взяты из сводок координатора в t0 `66790cc7a8`/`da703d8310`;
raw logs/archives не загружались и эти числа независимо не пересчитывались. Их нельзя представлять как новый измеренный receipt.
Аудитору можно предложить другой план/механизм; приведённые гипотезы не ограничивают выводы.
