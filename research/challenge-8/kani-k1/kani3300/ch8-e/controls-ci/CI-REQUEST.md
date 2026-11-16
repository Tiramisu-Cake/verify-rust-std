# E-01: изолированные controls, только подготовка

Задание: `TASK-CH8-E-CONTROLS-W15.md`, вход g0
`7d8ddd22f40a64053de7de13fb23a3f3303bc07a`.
Одна стадия: локальный CI-only пакет, synthetic tests и independent review.
Push, dispatch, публикации, ledger и локальные Rust/Kani/CBMC не выполняются.

Будущий координаторский запуск: **один dispatch**, bucket **E**, item **1**,
только attempt **1**, push branch `uninit-ci/ch8-e-ctl-*` в `Tiramisu-Cake/kani`.
Matrix: upstream `0aac16ef62da9e9d5645782d458593e5d78143ba` и
SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7`, ON/OFF companions
на каждом pin. Все остальные default checks сохранены. Два matrix jobs
исполняются последовательно, fail-fast=false. Это не две dispatch reservations.

Каждый root — отдельный single-file fixture, без `verify-std`, std checkout,
изменений smallsort или новой shadow/havoc модели. E-Q: pointer quantified
invariant, false mutant, изолированный witness, scalar alternative. E-S:
uncapped symbolic primitive storage и чтение valid index. E-H: live-byte
preservation, unwritten hole, outside false bit, actual write/copy companions.
Точные источники, ожидаемые outcomes и oracles — в `ch8-e-control/rows.json`
и `ORACLES.md` CI пакета; frozen identities и payload hashes — в соседнем JSON.

Flags: `-Z unstable-options -Z loop-contracts -Z quantifiers`, ON добавляет `-Z uninit-checks`;
`-Z export-json --export-json <absolute-file>`, `--harness-timeout 600s`,
`--jobs 1`, `--exact`, `--cbmc-args --object-bits 12`. Нет target-loop unwind.
Per-invocation envelope 660s включает single-file compilation; harness cap
600s задаёт Kani. Process-group RSS cap 6GiB; отдельные head ≤1MiB и tail
≤4KiB каждого stdout/stderr, export ≤8MiB. Общее окно run ≤75min на pin;
job ≤120min включает setup/build и reserve. При недостаточном остатке
полного envelope следующие roots становятся NOT_RUN; retry не разрешён.

Это бюджетные caps, а не измеренные затраты. Compile/driver/CBMC stage costs
и точный per-process RSS могут остаться UNKNOWN; group elapsed/peak не выдаются
за solver VT. Symbolic storage ещё не связано с actual core theorem.

Сохраняются исходные exit/exception/signal, argv/cwd/pins/source hashes,
partial export и bounded output. Setup/resource/timeout/schema/mismatch ошибки
не удовлетворяют negative oracle. Cover IDs без описаний требуют отдельной
runtime correlation; source expectations не являются независимым proof credit.
Все runtime outcomes **NOT_RUN**, proof credit **NONE**.

Control commit содержит `[skip ci]`. Он предназначен для review. Активация —
только после отдельного решения координатора: same-tree sibling без `[skip ci]`
с единственным parent upstream0aac на новой подходящей branch, затем один push;
не child поверх preparation commit. В этой стадии activation не создаётся.
