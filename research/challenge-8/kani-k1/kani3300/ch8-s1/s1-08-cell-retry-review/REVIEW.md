# W14 independent cell retry review — CHANGES_REQUIRED

**P2 W14-CELL-RETRY-01 — восстановить fallback controls.**
`ch8-s1-control/test_cell_retry.py:129` выбирает из PackageTests только control/build checks;
workflow `ch8-s1.yml:43` больше не запускает test_package.py целиком. Замена fallback
в `test_cell_retry.py:82` проверяет пустой output. Прежние
`test_fallback_terminal_after_setup_failure_and_mid_run_interruption` и
`test_fallback_preserves_receipt_materializes_tail_and_bounds` не исполняются и не адаптированы.
Это нарушает явное требование задания сохранить обязательные service/error controls.

Различающая мутация в памяти: заменить единственное `if not receipt.exists():`
в `check_package.fallback` на `if True:`. Все17 новых workflow tests остаются PASS,
но captured cell receipt теряет original_exit42/signal15 → null/null и становится NOT_RUN.
Прежний preservation test проходит на base7c и отклоняет ту же мутацию на строке337.
Проблема — утрата проверяемой гарантии; порча данных неизменённым candidate не установлена.

Оригинальному W13 owner через координатора: адаптировать и включить оба fallback controls
для exact cell pair. Проверять сохранение captured/completed receipts и original outcomes,
mid-run interruption, interrupted-terminal context и bounds; overwrite mutation должна
отклоняться ниже payload hash gates. Author code reviewer не менял.

Остальная bounded delta проверена: только шесть разрешённых файлов; source/tool,
ROLE-MAP, proof settings, decoder/native capture/snapshots/location/admission неизменны.
Exact pair выбран fail-closed, включая отсутствие --groups. Actual argv/parser/receipts1200,
child900+2×1200=3300, cleanup10, phase8100/job10800/setup1800/reserve900 согласованы.
Один job/max-parallel1, concurrency/cancel policy сохранены. Missing RESULTS/TIMEOUT
остаются UNKNOWN. Все17 штатных tests прошли. Manifest22/payload/mirrors/две patch tree
reconstructions совпали; actual shallow5/2/2 preflights PASS, depth2 negative128.
Механические checks автора повторены с report writes только в память; historical files
не переписывались. Полный повтор неизменённых U/PFC/source audits не проводился.

Exact reviewed pins:

| Объект | Pin |
|---|---|
| Package g0 | `9f4c37c894e7fecee0f59321ba66b65309a87606` |
| Control | `da8c766f957c576eafa44bccfba2c45490cef6d1` |
| Control tree | `a0e21f185de757c05397cf32547153325012469f` |
| Parent | `9208b373c0a08a265fa0d7493a6529e331065271` |
| Delta base | `7c41333f9bfcfd7eb4e0ede7bd316443090c9025` |
| Source | `99e8456d200fff1299ee5756279cddb23921dc65` |
| Stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` |

Embedded request SHA256: `7a2cdc282a76e36bfee611c3987471c6eb70b76ff314f2f7785906cb0badaf5c`.
Подробные pins/checks и mutation result — VALIDATION.json.

Review ≠ GO. CI/compiler/rustfmt/Kani/CBMC/full runner/push/subagents NOT_RUN;
proof/admission/B1/B2 credit NONE. Intake11 не ожидался; его files не затрагивались.
Retry решает координатор после terminal S1-08 и intake.1200s evidence не устанавливает
fit600s, обычный cost budget или причинность labels. Новый run/profile/origin должны
быть явны; same-run composition не разрешена этим review. Charge остаётся8/14;
9/14 только после нового GO и принятого run, сейчас NOT_RESERVED/NOT_RUN, auto-rerun нет.
