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
