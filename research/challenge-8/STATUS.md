# Merge-R13 CLOSED — synthetic publication verified; size receipt unavailable

[Новое текущее задание](CURRENT-TASK.md): worktree `/root/verify-rust-std-merge-origin`, branch `merge/incoming-origin-20261009`, owner `merge`. T0 2026-10-21T12:10:26Z, main14:10:26Z, absolute14:40:26Z; свежие120мин+30мин/3600 Cloud-секунд, без лимита числа последовательных Builds; timeout90..1200/envelope+60. Phase `MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21`, новый ledger `CURRENT-RECOVERY-R13-UPLOAD-BUDGET-20261021.json`. Закрытые счета/3491retired не возобновлять, carry0.

Owner/admin report для synthetic Build `68d2fe9c-bb4b-494e-844d-1a779d8d9f41`: финальный marker есть (11:17:34.761UTC), uploadedtrue/prerequisite exit0; archive537691281bytes > processor limit536870912bytes на820369bytes. Отчёта v8 нет. Код при превышении выдаёт archive too large/NOT_PUBLISHED_INVALID_EVIDENCE/422; получение события и фактическая первичная production-ошибка не подтверждены. Historical R12 records сохранены.

Исправление задания: synthetic payload268435456bytes (256MiB), согласованные producer/card/validator/pins; до первой upload проверка actual compressed archive<=536870912. Для synthetic дополнительно archive>effective composite threshold. Сохраняются exportFalse, effective-policy guard, IAM/SDK/account/create-only flags и marker-last; лимит обработчика не повышать. Сначала отдельный Cloud probe и доступный Brief/integrity, затем разрешён unchanged R11 proof retry. Backend-диагностика отказов — отдельная задача.

Checkpoint R12 `72981ed1ce289397371e2f10f3bbdd6d5be456e3`, tested source `1e33bd24e37d11cf4de4c2163be3925a6be0fbea`. R12 закрыта109charged/108execution/3491retired/remaining0/carryfalse; own0/0/0/0, proof retry не запускался. [Архив задания и отчёта](task-history/merge-noncomposite-upload-recovery-2026-10-21-r12.md), [probe result](cloud-build/origin-layout/R12-PROBE1-RESULT-20261021.json), [release](cloud-build/origin-layout/R12-RELEASE-20261021.json).

Normal proof остаётся source0c1d0d78/tool660b576b/profileeb61e493,158 frozen normal-proof files. **Full target gates0/acceptedfalse/independentcredit0; B2/generic/qualificationOPEN.** Последний доступный proof-фронтир — R11 Build5 checkedLive/Dead117 → iterationprep301 points_to_limits/dummy30none; initialized-value invariant без доступного formal result. Новая авторизация сама proof status не меняет.

R13 actual synthetic Build331fba31-4548-40e7-bb6d-1d225f590602 SUCCESS,
source c9b5151735c352d212752c5fe644adcd3543b68d; charge94/execution94.
Brief VERIFIED_ARCHIVE_AND_INVENTORY; archive SHA8ecf904c01ef647009619d7d445e13cb258c18a656dc65bc873756c610183efb,
indexad0e439b6d42371ade0c1db672f0f675e0eb6e209ca643e04b5b079d9a5a428e.
Payload268435456bytes; effective False/150M; exact source/config bound.
Gate pending exact compressed archive size/guard sidecar receipt: Reader v0.11
supports catalogue archive members only; owner requested supported route or
admin metadata. No raw bypass, proof retry pending required gate. Account CLOSED12:39:00Z, used94/retired3506/remaining0/carryfalse; own active/unresolved/requests/reservations0. See R13 probe/session.

R13 CLOSED2026-10-21T12:39:00.159587Z:94charged/94execution/3506retired/remaining0; own0/0/0/0. Next: exact receipt or supported route and fresh explicit retry authorization; closed account not reopened.
