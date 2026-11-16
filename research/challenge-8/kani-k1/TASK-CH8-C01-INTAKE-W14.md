# TASK — worker14: intake C-01 и пакет C-02 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

C-01 run 43788110742 (sibling `d224c83361`, control `64ec781bc1`, std `d073585946`). Artifact id —
`gh api repos/Tiramisu-Cake/kani/actions/runs/43788110742/artifacts`; анализ из zip в scratch, raw logs не читать.

Координатор (export verdicts): group-01 COMPLETE (compile 28 s): `c_merge_source_write_restore` FAILURE 280/2 —
`Check that *dst is assignable` (N1 frame violation пойман) **и** `unwinding assertion loop 0`;
`c_merge_source_read_only` FAILURE 280/1 — только `unwinding assertion loop 0` (legal companion не прошёл из-за unwind);
`c_callback_live_shared_in_outer_frame` SUCCESS (N2 — documented alias gap, как в дизайне);
`c_callback_read_only_in_outer_frame`, `c_external_mut_state`, `c_external_cell_state`, `c_local_storage_reuse` SUCCESS;
group-02 `c_insert_tail_local_lifetime` SUCCESS. Covers в group-01 satisfied 18/30. Job failure.

1. Классифицировать все 8 строк против oracles (CONTROLS-DESIGN/ORACLES), разобрать 12 неудовлетворённых covers,
   проверить binding (если runner дал UNKNOWN из-за binding — тот же вопрос, что у Profiles: worker11 разбирает
   `SOURCE_STAGE_TARGET_MISMATCH`, его вывод в g0 `kani3300/ch8-profiles/off-ci-batch/run-43784551069/` если уже есть).
2. Исправить unwind для merge-пары (минимально достаточный, обоснованный по длине цикла; не ослаблять проверки),
   новый std commit на P′ и batch control → пакет C-02 (последний C credit): только merge-пара + её oracle,
   или все 8, если дешевле и чище — обоснуй.
3. Обновить LIMITATIONS-DRAFT формулировку по фактам (N1 пойман на merge frame; N2 — gap), без публикации.
4. g0 `kani3300/ch8-c-ctl/run-43788110742/` RESULT.md + C-02 CI-REQUEST/REVIEW/HANDOFF.
   Последней строкой `READY <std> <control> <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
