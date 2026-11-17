# TASK — w11: немедленный intake 13 SUCCESS groups S1-08 + timings

Это верификация корректности, не security-работа. Отвечай кратко. Свежая Codex-сессия,
текущая pane-модель/effort; без субагентов. Одна компактная intake стадия, не acceptance или retry.
Координатор подтвердил terminal run44095954742/attempt1:13 групп SUCCESS, только cell-u34 FAILED.
Эта выдача **активирует** prepared `TASK-CH8-S1-08-INTAKE-W13.md` для **w11** с уточнениями ниже;
его run/pins/provenance/timing requirements действуют, его writer-role w13 заменяется этой выдачей.
Input g0 `9f4c37c894e7fecee0f59321ba66b65309a87606`; exact pins в `s1-08-postrun/INPUTS.json`.

1. Подтвердить terminal metadata/exact head21592884db/attempt1/request77ae… и получить **только13 SUCCESS
   compact artifacts**, все кроме cell-u34, с digest/embedded SHA/bytes/identity/partial checks по parent task.
   Не ждать review/retry: они независимы от этого intake. Полные/raw logs не читать и не скачивать.
2. Cell не скачивать заново: использовать read-only `s1-08/run-44095954742/cell-diagnostic/` commit929f21bb1f
   с exact same-run hashes/provenance и уже сохранёнными structured projections. Если чего-то не хватает,
   отметить конкретный UNKNOWN, не блокировать готовность13 успешных групп. `stable_default_cell` — TIMEOUT,
   `unstable_default_cell` — source SUCCESS, но вся failed/incomplete cell-группа остаётся не admitted.
3. Итоговый collected/RESULT включает35 declared rows:13 complete groups/33 rows и2 cell observations/UNKNOWN
   с исходными статусами и provenance, без восстановления missing RESULTS. Не делать ложный14/14 COMPLETE.
   Выдать точный вход для последующей offline acceptance, не менять её policy и не присваивать qualification.
4. TIMING-COMPARISON.json/md **по всем common logical harnesses/variants** с S1-07: raw verification_time_s,
   outcomes/limits/joins/deltas/ratios, completed cohorts отдельно от TIMEOUT censoring, missing не0;
   per-harness поле не заменять group/job wall. Учитывать reviewed label source delta5be→99e, прочий domain/config
   проверять. Cell times брать из проверенных diagnostic projections. Нового retry1200s здесь ещё нет;
   его не ждать и не смешивать. Labels causality не утверждать. При нулевой baseline duration ratio UNKNOWN.

Write scope: только новый полный intake в `kani3300/ch8-s1/s1-08/run-44095954742/`,
**исключая** immutable cell-diagnostic/ и будущий accept/. Не менять retry packet/source/control/ledger.
Parent task outputs RESULT.md, collected.json, INPUTS/manifest/replay/VALIDATION/HANDOFF плюс timings обязательны.
Reuse существующих intake helpers; новые tests только изменённого adapter/timing/partial-group интерфейса,
не начинать большой новый classifier/full audit. Evidence directories не дублировать без нужды;
diagnostic references закрепить hashes, необходимые cell projections можно адресовать как read-only refs.

Не STOP по размеру/контексту/«не успеваю»; реальный missing input оформить UNKNOWN/partial, без подделки evidence.
Без CI/rerun/cancel/push/публикаций/ledger/cargo/rustc/Kani/CBMC/rustfmt. W14 параллельно ревьюит retry,
его результатов не ждать и его пути не stage. Commit только своих paths, без git add -A/reset/rebase чужого;
`[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0>` с completeness/timing либо реальный STOP.
