# TASK — worker15: изолированные E-Q/E-S/E-H controls — CI-only пакет (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: твой E design (g0 `9b73c4e316`, `kani3300/ch8-e/`): STOP E для quantified-pointer invariant при ON;
shadow после loop havoc — UNKNOWN. Координатор разрешает подготовить **один** дешёвый CI dispatch
(bucket E, item 1) с изолированными single-file Kani tests — **без сборки std**, поэтому без
проблемы пересборки std на harness ([CH8-RUNNER-BATCH-NOTE.md](CH8-RUNNER-BATCH-NOTE.md)).

1. Fixtures из [CONTROLS.md](kani3300/ch8-e/CONTROLS.md): E-Q (quantified pointer invariant ON/OFF —
   подтвердить/опровергнуть frontend rejection), E-S (symbolic-length storage без constant CAP),
   E-H (uninit shadow после loop havoc: initialized-before-loop остаётся readable / hole после havoc
   ловится / false-bit сохраняется). Для каждого — ожидаемый исход и oracle; несколько вариантов
   кодирования invariant, если дешёвы. Не std, не smallsort.rs.
2. Два tool pin в одной matrix-run: upstream `0aac16ef62…` и SEL1 `14bc57fdb9` (ON) — один dispatch.
   Kani `-Z loop-contracts -Z quantifiers` (+`-Z uninit-checks` где нужно), `--harness-timeout 600s`,
   export JSON, bounded head+tail stdout/stderr, upload без target/. Чеклист: push trigger
   `uninit-ci/ch8-e-ctl-*`, `runner.*` только в step env, fetch-depth ≥2, sibling layout, path
   normalization от cwd, static YAML/actionlint, attempt 1; stock workflows удалены в control.
3. Synthetic tests, review. g0 `kani3300/ch8-e/controls-ci/`: CI-REQUEST, REVIEW, HANDOFF.
   Последней строкой `READY <ci-pkg> <g0>` или `STOP <причина>`.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC. Новую shadow/havoc модель не делать.
