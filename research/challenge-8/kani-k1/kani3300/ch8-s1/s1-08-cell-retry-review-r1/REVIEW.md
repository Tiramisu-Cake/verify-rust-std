# W14 r1 delta-review — APPROVE

**W14-CELL-RETRY-01 CLOSED на exact r1 pins.** Новых findings нет.
Исторический ec48 verdict CHANGES_REQUIRED и old9f/da8 не переписаны.

Дельта da8→e27 — только `CI-REQUEST.json`, `test_cell_retry.py`, `test_package.py`.
В request меняются ровно два test payload hashes. Runtime/fallback/profile/workflow,
timeout/derived caps/source/tool побайтно прежние; broad U/PFC/compiler audit не повторялся.

Оба прежних fallback controls адаптированы к exact cell pair и включены через
`ProfileTests.test_reuse_existing_service_preflight_controls`. Проверяются captured и
completed row/group/compile receipts, сохранение original exit/signal/exception,
interruption только in-progress material, setup failure, interrupted terminal context,
malformed terminal и bounds с exact size/hash dropped data. Small10000-byte cap —
изолированный synthetic fixture после canonical request/selection; production256MiB прежний.

**Реально повторено:** обязательный workflow Python preflight18 tests — PASS7.227s,
без skips. Инструментирование unittest подтвердило успешный вызов обоих controls
в service preflight; оба также реально вызываются в mutation test и ожидаемо падают.
Reviewer отдельно, без author mutation helper, воспроизвёл sole
`if not receipt.exists():`→`if True:` в памяти ниже payload hash gates. Оба controls
ловят потерю exit42 с `None != 42`, errors/skips0. Независимый captured-row fixture:
real fallback сохраняет exact bytes/exit42/signal15; mutant теряет exit/signal до null.

Проверены exact committed27 package files/manifest26, payload/mirrors/request hash,
три patch reconstructions к exact tree2c4475bf, source/tool pins/hashes. Actual file://
shallow5/2/2 и control/source preflights PASS; negative depth2 даёт128. Report writes
механического helper перенаправлены в память; исторические пакеты не менялись.

**Перенесено из ec48 по byte invariance24 control files и unchanged request:**
fail-closed exact cell pair даже без --groups, actual argv/parser/receipts1200,
child3300+cleanup10, phase8100/job10800/setup1800/reserve900, RSS12GiB/headroom2GiB;
job/max-parallel1 и fork concurrency/cancel policy. Proof flags/oracles/ROLE-MAP,
decoder/native capture/snapshots/location/admission прежние. Missing RESULTS/TIMEOUT
остаются UNKNOWN. Эти гарантии не выдаются как новый proof/runtime credit.

| Объект | Old | New |
|---|---|---|
| Package g0 | `9f4c37c894e7fecee0f59321ba66b65309a87606` | `6b51a4df0273843f661e9f81d9645a99a491d378` |
| Control | `da8c766f957c576eafa44bccfba2c45490cef6d1` | `e27ec119eeac798d43d6bc056a449fa7576a5e94` |
| Control tree | `a0e21f185de757c05397cf32547153325012469f` | `2c4475bf17bb0354e9b204e19c652549c263f90f` |
| Request SHA256 | `7a2cdc282a76e36bfee611c3987471c6eb70b76ff314f2f7785906cb0badaf5c` | `3e61b78c0f527ea5966ca33ff5d05ad354c1846ae995ce320f361ae795f6f2d8` |

Оба parent `9208b373c0a08a265fa0d7493a6529e331065271`, review base
`7c41333f9bfcfd7eb4e0ede7bd316443090c9025`. Source
`99e8456d200fff1299ee5756279cddb23921dc65`, stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba` неизменны. Полные hashes/checks — VALIDATION.json.

Review ≠ GO; retry решает координатор после APPROVE и intake. Intake6d300f3ab9
не ревьюировался, acceptance не выдан. Compiler/verifier/full runner/CI/rerun/cancel/
push/subagents NOT_RUN; ledger/reservation/budget не менялись. Current8/14;
prospective9/14 не reserved/authorized. Proof/admission/independent B1/B2 credit NONE.
1200s не доказывает fit600s/обычный cost budget; labels causality UNKNOWN;
future cross-run composition отдельно.
