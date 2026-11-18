# W14 — standalone F4 fix review

PREPARED_NOT_ISSUED. Только после выдачи/committed READY15; exact g0/fix SHA укажет
координатор. Это верификация корректности, не security-работа. Отвечай кратко.
Fresh/current model+/fast, без субагентов; STOP только реальный blocker.
Пути от `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Контракт TASK-CH8-F4-FIX-W15.md; frozen mainfaff, reproduction intake06ff67af4a,
observed run44177926794. Проверить exact minimal compiler/test diff: правильная
per-harness isolation/restore boundary, cached/transformed body lifecycle, contract/
stub/target discovery/codegen invariants и сохранённые intended uninit checks.
Blanket instrumentation disable/reset не скрывает defect. Ограниченные regression
singletons/shared/two cfg проверяют initialized paired SUCCESS и intended unsafe
FAILURE; main-failure соответствует сохранённому evidence. Fixed PASS до execution
остаётся NOT_RUN. Actual compilation order/causality не выдумывать из cfg названий.

Standard workflows/library/toolchain сохранены; confirmation CI-only deletions и
research runner не попадают в PR. Style upstream, PR draft и full-standard-CI plan
готовы для review, но publication/последний CI только новый GO владельца. Static/
synthetic checks и source reasoning сейчас; без local compiler/verifier/full runner.
Output новый `kani3300/wave0/f4-fix-review/`: REVIEW/VALIDATION/HANDOFF с exact pins,
APPROVE/CHANGES_REQUIRED. Findings original15, code не чинить.27/28 сейчас; ledger/
budget/CI/push/PR/reservation не менять. `[skip ci]`, author Tiramisu-Cake
<igkharin@gmail.com>, exact own paths/commit --only. Финал `READY <g0> <verdict>`.
