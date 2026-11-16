# TASK — worker11: Profiles OFF control — путь repo в validate (короткая стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

PROF-OFF-01 run 43782419242 (sibling `56caab8637` of control `242ca63174`): упал за 1 s на шаге
«Validate control and synthetic wrapper»: `check_package.py:69` → `git -C /home/runner/work/kani/kani rev-parse HEAD`
exit 128. Причина: workflow `.github/workflows/ch8-prof-off.yml:39` — `python3 check_package.py control --repo ../..`
из `working-directory: control/ch8-prof-off-control` указывает на workspace root, а не на checkout `control`.
В рабочем S1 kani-host (`8c8ac10d67`) стоит `--repo ..`.

1. Исправить на `--repo ..`; пересчитать все привязанные хэши (CI-REQUEST/MANIFEST/review binding).
2. Добавить synthetic/static проверку, что `--repo` из working-directory шага резолвится в checkout `path: control`
   (чтобы такие ошибки ловились до dispatch) — по возможности общую для всех control (S1/B/C/E).
3. Review (diff только это). g0 `kani3300/ch8-profiles/off-ci-batch/fix1/`. Последней строкой
   `READY <control> <g0>` или `STOP <причина>`. Без push/CI/ledger; без локальных cargo/rustc/Kani/CBMC.
