# CBMC ZST-BITS2EXPR-R1 — STOP

Source: `cd41a5c74b0c42edf4f08834b3e2808dd3344cab`; parent exact develop `107a1e504cd69a2f3483717c8bcfcfa59814c557`.
Source branch: `fix/zst-bits2expr-r1`; source tree `92c03401d6c2a6da069670260244bc021bbdba99`.
CI-only: `33235a4ef1dc4891842473f92e500a40ee78d8fa`; parent is the new source.
CI branch: `ci/zst-bits2expr-20261113-r1`. Both new branches are local.

Координатор сообщил: прежний CI `64a077ab6767c7a91fc9141bfac08423d5424bf7`, run43329473713,
обе задачи упали до сборки на patch SHA assertion; Format Check18.1.8 дал
предоставленный diff. Это source-reported результаты; CI reports здесь не читались.

R1 закрепляет `--full-index` и параметры отображения diff; cfg пересчитан.
Сохранены patch SHA, exact parent/source tree, overlay tree, changed-path и byte gates.
Test-only patch SHA256: `a75767929c55785f98cc6864144bb033b2dfd0b6b05913475f16e5620f3a3deb`.
Baseline overlay tree: `5ef52ba174f95b3ae51d19805b592a468db3c432`.
Единственное отличие overlay от source tree: `src/util/simplify_utils.cpp`.
При core.abbrev4/7/10/40 старый `--binary` diff имеет разные bytes/hash;
`--full-index` стабилен. Точный механизм прежнего несовпадения не установлен.

Source delta к прежнему source побайтно равен `/root/cbmc-zst-ci1-format.diff`;
его SHA256 `71d92ea67354977b98da6869528c6cf17fa7461e4dd3ce0700478b4270683cf2`.
Тело source-коммита теперь объясняет причину, recursion и покрытие тестов, без CI-процесса.

7 synthetic checks PASS; Luna High review без существенных замечаний; diff checks PASS.
Проверены abbreviation/display settings, обе synthetic variants, отказы на неверные
patch SHA, source/overlay tree и changed paths, прежние error/timeout/partial/status controls.
Formatter локально отсутствует: actual formatter NOT_RUN; подтверждена точность diff.
Actual prepare/build/CBMC/unit/regression/CI в R1 NOT_RUN; proof credit отсутствует.
Workflow и execution matrix сохранены, remaining workflow count1.

Исторические manifest/checkpoint/patches сохранены; актуальные R1 pins, hashes и
отдельные patches — в `R1-MANIFEST.json` и `r1-*.patch`. Review: `R1-REVIEW.md`.
Координатор использует новую CI ветку; force/перезапись старой ветки не нужны.
Worker push/dispatch/issue/PR/builds отсутствуют; Cloud $0; reset/stash не применялись.

READY 33235a4ef1dc4891842473f92e500a40ee78d8fa
