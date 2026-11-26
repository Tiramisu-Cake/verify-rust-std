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
