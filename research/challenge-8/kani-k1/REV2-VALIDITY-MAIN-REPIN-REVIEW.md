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
