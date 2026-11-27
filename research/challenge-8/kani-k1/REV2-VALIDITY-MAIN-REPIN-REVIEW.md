# REV2 валидность · repin на nightly-11-21 · независимое ревью R1

**GO_WITH_NITS**, блокеров нет · ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26 · control `e4b3eced27aef7a926ae90b82a21411fcde24cc4` (tree `817a5db4e9eedc486148ec6018b9ce35685c0a93`), Kani `4caf097d845ae8b859a18c4327b3694efd6f743a`, Std merge `7f961eda87f25cf422b2f0a444c9ef7edf2296c9`, overlay `bc866f8dfa4ad517b2d67e2d3d812729d82d5148`, review-trigger `0650c59e24`, handoff g0 `4cce5ffaf5`.

## Неблокирующее

1. **Нестабильный унаследованный тест** `ch8-rev2-validity/test_supervisor.py:422` (`test_escaped_descendant_is_killed_by_its_owned_pid`): 2 падения из 7 прогонов suite под нагрузкой 3–7 (`REAP_UNVERIFIED != TIMEOUT`). Suite идёт в шаге `pins`; падение там переводит A/B в 30 `NOT_RUN`. Координатор: исправить до запуска (FIX2).
2. `test_sources.py:212-213` принимает любую ошибку git; нужен точный путь отказа «prerequisite … is missing».
3. `request.py:340`: проба `cat-file -e` с фиксированным `timeout=30` вместо дедлайна `sources`.
4. `kani-verifier` нет в `8c6dba5935`; часть diff-проверки по этому пути пуста (в handoff отмечено).

## Проверено

- Kani `4caf097d84`: один родитель `8c6dba5935`, единственная правка `rust-toolchain.toml` → blob `87c87010ed` (nightly-2026-11-21); `git diff 87c87010ed 8c6dba5935^` по compiler/driver/library пуст; полный промежуточный diff — `Cargo.lock`, `rust-toolchain.toml`, `action.yml`, `install_kissat.sh`.
- Std merge: родители pr752 `dab03cf510`, upstream `f94155ef29`; `merge-tree` воспроизводит tree, конфликтов нет (непересекающиеся пути 19 и 41); toolchain и пин Kani — blobs upstream. Дельта merge→overlay равна FIX1; файлы overlay побайтно равны `75ab1822ac`. Локальная ветка pr752 не тронута.
- Bundles: пять SHA-256, v2 с одним `HEAD`, prerequisites верные; импорт на двух shallow базах, checkout, fsck — PASS.
- Гейты и окна: `sources` до setup, фаза 0 на чистом merge без cfg, `phase0_block`; окна 30:00/49:30/79:30/119:30/121:30/133:30 при job 140 мин; таймауты шагов ≥ бюджетов; uninit OFF, OFF/ON отличаются только valid-value-checks.
- Trigger: новая `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE`, тот же tree, sole parent `467af9cb8d`; синтетика отклоняет старые tree/пин/bundle, nightly 11-23, перестановку родителей, чужие prerequisites, изменённый overlay, повреждённый bundle, ранний E0718.
- 109/109 (кроме флейка п. 1); YAML, `bash -n`, `git diff --check`, rustfmt; авторство Tiramisu-Cake, `[skip ci]`.

Не проверяемо локально: выдача GitHub `f94155ef29` по SHA, submodules в CI, сборка на 11-21, компиляция merge.

## R2 · FIX2

**GO_WITH_NITS**, блокеров нет · ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26 · control `bf4e1d882a6a7247a87a7dac5890738507eb4d06` (tree `6d51ab4ed08f87d01d9be5f783c63f751a08e3ac`, sole parent `e4b3eced27`), review-trigger `13e1ebf83ade3d25dbd6a4ee6d5e7b61c40ba8c2` (тот же tree, sole parent `467af9cb8d`), handoff g0 `5f6ed8542f`.

### Неблокирующее

1. `test_sources.py`, `test_upstream_probe_and_blob_reads_are_bounded_by_the_sources_deadline`: второй `assertEqual(calls, [])` после `git_blob` ничего не проверяет, потому что подменён только `subprocess.run`, а `git_blob` вызывает `check_output`. Отсутствие запуска доказывает сам `TimeoutError`, так как `bounded()` вычисляется до вызова. Поведение верное, утверждение избыточно.
2. `test_sources.py`, fetch-сценарий: срез `cmd[5::len(cmd)-6]` хрупок к изменению argv. Яснее проверять `cmd[5] == "fetch"` и `cmd[-1] == refspec`.
3. Stress-доказательства: `summary.txt` собран из логов после прогона, формат не совпадает с `printf` в `stress.sh`. Диапазон load 3,3–7,3 в файлах не зафиксирован. SHA в логах нет, привязка к `bf4e1d882a` косвенная, по времени. Все 24 `run-*.log` заканчиваются `Ran 110 tests … OK`.

### Проверено

- Дельта `e4b3eced27..bf4e1d882a` — один коммит, только `request.py`, `test_sources.py`, `test_supervisor.py`. `supervisor.py`, workflow, `CI-REQUEST.json`, bundles, overlay, fixture и roster не изменились. Trees и blob'ы совпадают с handoff. Авторство Tiramisu-Cake, `[skip ci]`.
- `test_supervisor.py` побайтно равен `df63a457`. Этот blob ревьюился вместе с тем же `supervisor.py` `151af5b128`. Escaped-descendant строже R1: timeline ровно TERM_DESCENDANT → KILL_DESCENDANT на один PID/start_id, `reaped=true`, пустые `remaining_processes` и `cleanup_errors`, `waitpid` −SIGKILL. Сигналы и census идут через настоящий код.
- `test_sources.py`: точный путь `^bundle prerequisite <sha> is missing$` при подменённом `ensure_upstream`; для неизвестного SHA ожидается `CalledProcessError` именно из `fetch`.
- `request.py`: `bounded()` бросает исключение до запуска процесса при исчерпанном дедлайне. Таймаут `git_probe` не превращается в «missing». Все вызовы на пути `sources` (`run.py:238-262`) передают deadline, фиксированных 30 с на этом пути не осталось.
- Suite: прогон ревьюера в копии `git archive` дал 110 тестов с одной ошибкой. Предположительная причина — `test_run.py:269` требует git-checkout. Координатор повторил прогон в чистом `git clone` с detached `bf4e1d882a` (tree `6d51ab4ed0`): **110/110 OK за 36,5 с**.

Не проверялось: `run.py pins`, `static_import.py`, повторный stress. Workflow не менялся.

Решение координатора: замечания 1–3 не влияют на запуск, повторный FIX не нужен. Пакет передаётся планеру на GO.

## R3 · FIX3

**NO-GO для запуска**, один блокер в фазе B. Сама дельта FIX3 корректна: гейт `unsupported_construct` и группы A приняты бы как GO_WITH_NITS. Ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26. Control `0a4f85d930e47ffad9062131e6f57c6bde5989e6` (tree `c5752243969498403dc09f21404030ab702523ee`), review-trigger `0aa3c3071c`, request SHA-256 `553e9cd8…0fcf3`, handoff g0 `d4b8210a80`.

### Блокер

**B1. Отрицательный контроль B почти наверняка даст MISMATCH** (`verdict.py:191-192`, `request.py:86-95,516`). Чтение B `validity_main.rs:111` (`*values.as_ptr()`) — такой же typed read `char` через сырой указатель, как в A. `check_values.rs` ставит на него две проверки без assume: `UntypedRead` (`:1054-1056,695-707`; `may_be_untyped` на любом `Deref`, `:656-659`) и `DerefValidity` (`:976-980,819-827,796-810`). Для `char` это один `ValidValueReq` (`:424-431`). Обе проверки получают FAILURE на одних и тех же путях (`transform/mod.rs:141`). Корни B группы не имеют, поэтому `vv_stable_char_n09_corrupt` ON уйдёт в MISMATCH, а положительные получат `read_binding=UNKNOWN`. Вывод по исходникам, прогоном не воспроизводился. Нужен FIX4 со структурным правилом для B, которое не требует знать ID заранее.

### Неблокирующее

1. `verdict.py:405-408`: ветка `guarded and not bound_complete → UNKNOWN` проверяется раньше positive/negative, поэтому реальный FAILURE при неподтверждённом профиле выдаётся как UNKNOWN. Это fail-closed, но с потерей информации. Сначала вычислять условия MISMATCH.
2. `verdict.py:50,171`: флаги CBMC проверяются по чёрному списку, `--depth`, `--unwindset`, `--no-assertions` и `--cover` не отсекаются. Риск низкий при фиксированном argv.
3. `verdict.py:35-40`: семейства `kani_same_allocation_guard` и untyped-guard сверяются только по тексту.
4. Группы A взяты из того же прогона, поэтому replay — проверка согласованности.

### Проверено

- Дельта — 6 файлов (`CI-REQUEST.json`, `request.py`, `run.py`, `verdict.py`, два теста). Остальное не изменилось.
- Trees, parent, авторство и `[skip ci]` в порядке. SHA-256 request совпадает, `load()` сверяет `read_groups`.
- Все координаты в исходниках Kani `4caf097d84` подтверждены. SUCCESS у `assert(false)` при включённых unwinding assertions означает недостижимость в пределах границ. Whitelist задан через `fullmatch`.
- Независимый офлайн-replay: **18/18 MATCH**. Контрфактические прогоны: без групп — 15/18, без профиля — 0/18 (UNKNOWN), с `--no-unwinding-assertions` — 0/18 (UNKNOWN).
- Unittest 119/119 OK.

NOT_RUN: Kani, CBMC, cargo, rustc, `run.py pins`, YAML, `bash -n`, фактическое поведение фазы B.

## R4 · FIX4

**GO_WITH_NITS**, блокеров нет, B1 из R3 закрыт. Ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26. Control `e2a3e6d48e98693074f51e93369917948f6790bf` (tree `f46e65c42c7ddb45a725569265b8dc7c0fd7a88a`, parent `0a4f85d930`), review-trigger `b0ce856748185bdfa3ac20969cbaa72f13841272` (тот же tree, sole parent `467af9cb8d`), request SHA-256 `bdd69de4e0245ad241b22b144a104fdb69256d6c2fb1620d26eda57ccf76a6a2`.

### Неблокирующее

1. Column 30 для `validity_main.rs:153` (`vv_sort8_char_n08`) выведен, прогоном не подтверждён. При расхождении положительный слот получит `read_binding=UNKNOWN`, MATCH сохранится.
2. MATCH отрицательного B зависит от того, что на `:111` будет ровно два validity-свойства. Исходники и A это подтверждают. Иначе получится fail-closed MISMATCH и потребуется FIX5, ложного MATCH не будет.
3. Чёрный список флагов CBMC неполный (`--symex-complexity-limit`). Риск низкий: argv закреплён, а `native_profile` ловит основные отключающие флаги.
4. Отрицательная ветка отвергает только `ERROR`, посторонний `UNDETERMINED` вне пары пропускается (`verdict.py:465`). Так было и до FIX4.

### Проверено

- Дельта — 5 файлов, в request изменился только ключ `read_structures`. Авторство, `[skip ci]`, trees и SHA request в порядке.
- Правило пары (`verdict.py:189-216,227-228,457-468,492-493`) не слабее задания. F предсказуема: у 1065 из 1065 свойств A префикс ID равен функции из location. Для `:111` это `…validity_main::stable_char_n09_body::<true>`. Пара на `:111` следует из исходников (`UntypedRead` + `DerefValidity`). Других validity-проверок в теле нет, MIR-инлайна нет.
- Columns: `:111` → 26, `:153` → 30, `check_coordinates` на overlay PASS.
- Порядок решений: guard-ветка срабатывает только при MATCH. Флаги ловятся и токеном, и в форме `=`.
- Независимый офлайн-replay A: 18/18 MATCH. Синтетика B: пара даёт MATCH; варианты с 1 или 3 свойствами, другим column, F, ID, типом, лишним FAILURE, без cover или с terminal SUCCESS дают MISMATCH.
- Unittest 121/121 OK.

NOT_RUN: Kani, CBMC, cargo, rustc, `run.py pins`, YAML, `bash -n`, фактическое поведение фазы B.

## R5 · FIX5

**NO-GO**, один блокер. Ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26.
- Control `fc3a0e654efe2076c5e9d0139ac6cd8d5b62eae2` (tree `e9b8b464573e3bb534df18c8ab86f2508366c6c5`, parent `e2a3e6d48e`).
- Overlay `fe3fe324bfccaf309b5c5e20ce28dccd7759b45c` (parent `bc866f8dfa`).
- Review-trigger `a41dcc74de`.
- Хэши request, roster и bundle совпадают.

### Блокер

**B1. `vv_network_nonzero_n10` ON почти наверняка даст MISMATCH.**
- n10 и n18 вызывают один экземпляр `small_sort_network::<NonZero<u8>, …>`. Проверка на приведении `smallsort.rs:423:28` ставится в тело функции независимо от длины (`check_values.rs:1114-1119`).
- При len=10 эта точка недостижима. На этом пине недостижимые emit-места выводятся как SUCCESS.
- Семейства `mutable cast` нет в `UNSUPPORTED_FAMILIES` (`verdict.py:25-40`), а у n10 нет pin. Поэтому свойство попадает в `blocking_unsupported` (`verdict.py:506-508`).
- Синтетика на настоящем `decide` дала MISMATCH. В `test_run.py:663-675` у n10 этого свойства нет, поэтому suite дефект не ловит.

Нужно точное допущение для n10 ON:
- ровно одно свойство: ID, функция, `:423:28`, описание `[NonZero<u8>; 32]`;
- статус только SUCCESS при подтверждённом unwind-профиле;
- синтетика и мутации.

### Неблокирующее

1. Холодный cap фазы A снижен с 45 до 30 с (`request.py:153-155`). Запас большой, максимум 0,95 с. **Координатор принимает.**
2. Ранговый домен `char` (`validity_main.rs:51-60`): положительные ON ловят nondet/uninit-чтения, но не перемешивание байтов. Оговорить в результатах.
3. Covers n18 (`validity_main.rs:224-231`) стоят до вызова, cover «split into two 9 element halves» тавтологичен. Переименовать или убрать.
4. Порядок импортов в overlay при edition 2021 был и в `bc866f8dfa`; с `style_edition=2024` файл чистый.
5. Шаблон типа probe, возможно, узок для «голого» `NonZero<u8>`. Влияет только на негейтящий probe.
6. У `cbmc_ignoring_warnings` нет флага полноты захвата.

### Проверено

- **Дельты.** Overlay: изменён только `validity_main.rs`, `smallsort.rs` не тронут, bundle в порядке. Control: 10 файлов, Kani и merge не изменились. Авторство в порядке.
- **Fixture.**
  - Указатель берётся до порчи и до чтения.
  - `bool` везде сравнивается через u8.
  - Corrupt — без функциональной проверки. n10 идёт по no-merge, n18 только ON.
  - Probe совпадают с разбором. `check_coordinates` PASS.
- **Гейт.** Pinned-классы строгие, общее правило unsupported не ослаблено.
- **Часы.** 8340 ≤ 8400 с.
- **Replay A:** 18/18 без изменений; B старых receipts без падений.
- **Suite:** 133/133 OK.

NOT_RUN: Kani, CBMC, cargo, rustc, `run.py pins`, `static_import`, YAML, `bash -n`, реальное поведение фазы B.

## R6 · FIX6

**GO_WITH_NITS**, блокеров нет, B1 из R5 закрыт без ослабления. Ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26.

Пины:
- control `1338213af771e2658a3f81a5f720be7765b7eb86`, tree `756dea4a28c9ae012881fe36aa1542d749c78fec`;
- overlay `4beda039e6a399f7d38de9cbe987973cd59d0bdd`, tree `400f0d8e4c`;
- review-trigger `379a15f3034c54ab64e413b361b728641acc81fe`, sole parent `467af9cb8d`.

Хэши request `ab4550ea…8c62`, roster `2747be36…81a4` и bundle `49f0fba0…795e` пересчитаны и совпадают.

### Неблокирующее

1. Bounded publish может не сохранить допущенное свойство в `native.properties` (`verdict.py:449`). Останутся ID в `observed.admitted_unreachable` и счётчик. Для аудита добавить координаты допущенных мест в `wanted_locations`.
2. `verdict._admitted_error` (`verdict.py:311-324`) не проверяет `negative`. Это закрыто только в request (`request.py:353`).
3. Отсутствие недостижимого `mutable cast` у char-корней выведено только статически, их receipts обрезаны TIMEOUT. При ошибке будет ложный MISMATCH, ложного MATCH не будет.

### Проверено

- **Дельты.** Overlay: +1/−4 в `validity_main.rs`. Control: 7 файлов, workflow и tool bundle не тронуты. `frozen()` и digest совпадают, авторство в порядке.
- **B1, синтетика на `verdict.decide` по реальным записям n19 ON.**
  - Точное место со статусом SUCCESS → MATCH.
  - Без argv → UNKNOWN.
  - FAILURE, UNDETERMINED, ERROR, другой тип, длина, координата, ID, функция, файл, дубликат, лишнее свойство или FAILURE → MISMATCH.
  - n18 с FAILURE → `MATCH_KNOWN_LIMITATION`, n18 со SUCCESS → MISMATCH.
- **Достижимость.** Место `:423:28` стоит после `if no_merge { return; }`.
- **Другие корни.** У n03 и n02 `mutable cast` нет. Через `small_sort_network` идут только n10 и n18.
- **Старые замечания.** R5-3, R5-6 и R5-2 закрыты.
- **Replay.** A — 18/18, B — без падений.
- **Suite и rustfmt.** Suite 139/139 OK. rustfmt не даёт новых отличий.

NOT_RUN: Kani, CBMC, cargo, rustc; `static_import`, `check_trigger`, `run.py pins`; YAML и `bash -n`. ID свойства у n10 на реальном прогоне не проверен: если он не `.1`, получится MISMATCH, а не ложный MATCH.

## R7 · FIX7

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров нет. Пины: control `008d4e16a7cda26e26502d253f497d9299b96fbb` / tree `3181cc4a239a6fc83e80c89e0f3490f79ebe5990`, review-trigger `5327ba35e7`, overlay `30545a3ce3`, request `949ed18f…d986`, bundle `6e37fa5c…b71d`. Все SHA-256, bundle (HEAD `30545a3ce3`, prerequisites `f94155ef29`, `dab03cf510`), цепочка overlay, авторы и сообщения коммитов сверены. Suite 139/139 на свежем клоне trigger. Координаты B пересчитаны независимо, ошибок 0. В request и verdict функциональных ожиданий для двух изменённых слотов нет.

1. **Риск: запас `vv_sort8_char_n08` ON** (cold 142,6/180 с, VT 110,4/120 с в 45886041869). TIMEOUT этого слота разбирать как ресурсный, не как результат по валидности.
2. Nit: оценки времени n10 не имеют прямого аналога (оговорено в handoff).
3. Nit: позитивный MATCH не требует `read_binding`. При разборе прогона отдельно проверить `read_binding=OBSERVED` у `vv_stable_char_n09` ON.
4. Nit: комментарий overlay `validity_main.rs:115-116` («final UNSAT alone») неточен для ON.
5. На будущее: вернуть чтение всего выхода в validity-only корнях (сдвигает строки, не для FIX7).
6. Риск R6 по ID допуска n10 снят: pinned FAILURE n18 ON в 45886041869 имеет ровно ожидаемый ID на `smallsort.rs:423:28`.
