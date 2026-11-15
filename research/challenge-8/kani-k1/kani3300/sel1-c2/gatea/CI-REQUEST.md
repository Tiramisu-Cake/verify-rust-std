# A — подготовлено, NOT_RUN / PENDING_FREEZE

Источник реализации: accepted c2-gatea run 43665002636, overlay `39bcdd7ad51dc169f75a9974e43717205553bad0`.
Observer/lifecycle и synthetic tests сохранены; изменены только embedded source identity/state.
Workflow использует sibling `control` / `export`; Bash 3.2 owner guard сохранён.
Три платформы: ubuntu-24.04, ubuntu-24.04-arm, macos-15; fail-fast false, max-parallel3, одна попытка.
Полный неизменный `bash scripts/kani-regression.sh`: 33 стадии, без фильтров/новых ignores/check disables/RSS-watchdog.
Job360min, regression≤20400s, receipt reserve600s; compiletest2400s/test.
stdout/events256MiB, metadata16MiB, artifacts384MiB/platform, retention14d.
Process-group timeout, original exit/signal, artifacts always и aggregate missing/failed rows сохранены.
Собственный setup/dependency/toolchain freeze, без upgrades/патченного CBMC.

Приёмка: три полных exact-source receipts, 33/33 ordered стадий, exit0, clean source до/после,
полные bounded события, runtime identities и отсутствие необъяснённых failures/ignore/suite loss.
C2 totals — reference, новые totals объяснить SEL1 добавлениями. UNKNOWN требует review coordinator.
Финальный binding/CI parent — после freeze. `CI-REQUEST.json` машинно фиксирует caps;
`full-export/scripts/kani3300-gate/binding.json` намеренно PENDING и не проходит observer preflight.
