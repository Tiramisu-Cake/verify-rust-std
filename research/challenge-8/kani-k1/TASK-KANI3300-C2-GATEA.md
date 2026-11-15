# C2 Gate A — подготовка CI-only overlay для трёх платформ

2026-11-15. Worker15, одна сессия подготовки. Это верификация корректности, не security-работа.

Подготовить локальный overlay и запрос координатору. **Push, dispatch и любые CI-запуски — только координатор.**
Локальные cargo/rustc/Kani/CBMC/Miri, сборки, Cloud Build и публикации запрещены; Cloud $0.
Разрешены чтение, Git, Python/shell synthetic tests и статическая проверка обвязки без запуска toolchain/verifier.
Не менять замороженные source/tests/docs, freeze refs и исторические receipts. Gate A сейчас NOT_RUN.

## 1. Неизменный вход и рабочая область

- Репозиторий инструмента: `Tiramisu-Cake/kani`.
- Exact export SHA: **`ad499e41dd2db9ccd432f89721638a1f3a0bbd44`**.
- Exact export tree: **`9829702c1aa0ecb73c860fc0ad5451757917d6cb`**.
- Fork refs `fix/kani-3300-c2-s6` и `freeze/kani-3300-c2` должны указывать на этот SHA;
  при подготовке подтвердить доступные локальные identities, удалённые refs перепроверит координатор перед dispatch.
- Read-only источник: `/root/kani-fix-3300-c2-s6`. Его HEAD/tree/status проверить; не checkout/reset/clean/stash и не писать туда.
- Новый изолированный clone `/root/kani-fix-3300-c2-gatea`, ветка `ci/kani3300-c2-gatea-w15` от exact export.
  Если путь занят/dirty или исходная привязка отличается — STOP, без перезаписи.
- Research output: `research/challenge-8/kani-k1/kani3300/c2-gatea/` в g0; чужие пакеты не менять.

Сначала прочитать root/project AGENTS и зафиксировать INPUTS. Обязательные материалы g0:
`PLAN-KANI3300-C2.md`, `kani3300/c2-s6/ci-43656920767/ACCEPTANCE.md` (g0 `b624253cb6`),
`kani3300/final-gate/{FULL-GATE-REQUEST.md,CI-REQUEST.md,CI-ONLY-OVERLAY-MAP.md,ci-only-overlay.patch}`,
`kani3300/final-gate/gatea-c1b/receipt.json`.
Приёмка S6: targeted Quick 43656920767, matched hook qualification 43653700248→43653703827.
Это входные свидетельства; они не заменяют полный Gate A.

Образец C1b использовать как протокол наблюдения, **не как binding или ожидаемые числа C2**.
Его receipt содержит 33 стадии, но другой SHA/tree. Не переносить старые JSON suites, manifests, T1b allowlist,
property inventories, счётчики или ограничения checkout-путей: C2 уже использует переносимые expected-тесты.

## 2. CI-only overlay, отдельный exact export

Подготовить один локальный CI-only коммит, прямой parent — exact export. Автор через
`git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`; сообщение с `[skip ci]`. **Не push.**
В overlay удалить все штатные `.github/workflows/*`, оставить только новый manual workflow
`.github/workflows/kani3300-c2-gatea.yml`. Сохранить `.github/actions/setup` и остальные штатные файлы неизменными.
Допустимые добавления: observer/binding/synthetic tests в отдельном `scripts/kani3300-gate/`.
Полный diff overlay против frozen source ограничить этими путями; compiler/runtime/tests/docs/deps не меняются.

Workflow работает только через `workflow_dispatch`, с fork guard `github.repository == 'Tiramisu-Cake/kani'`,
`permissions: contents: read`, без PR/push/schedule/workflow_run, retries и `continue-on-error` для gate.
Control checkout получает exact CI-overlay SHA; **второй независимый checkout** `export/` — literal frozen source SHA.
Observer, binding, логи и artifacts находятся вне export. Выполняется source из export, а не overlay.
До setup проверить source HEAD/tree, clean status (включая untracked), tracked file/subtree hashes и submodule pins.
После setup и regression повторить identities/status; сохранять diff при изменениях, не скрывать их cleanup/reset.
Setup/build outputs, штатно игнорируемые Git, не считать изменением tracked source; неожиданные изменения требуют review.

Использовать **собственный frozen** `.github/actions/setup` с `os: ${{ matrix.os }}`, `kani_dir: export`:
штатные OS-specific dependencies, toolchain и submodules. Не импортировать Quick workflow/dependency upgrades.
Пины проверить по frozen файлам: nightly-2026-10-23, CBMC 6.11.0, Kissat 4.0.1; остальные solver versions — по штатному setup.
Никакого патченного CBMC, общего target/cache между платформами или подмены solver/model.

## 3. Матрица, одна попытка и caps

Ровно три matrix rows: **`ubuntu-24.04`, `ubuntu-24.04-arm`, `macos-15`**.
`strategy.fail-fast: false`, `max-parallel: 3`; одна попытка каждой строки, один dispatch, без rerun/retry loops.
Один общий concurrency group для C2 Gate A, `cancel-in-progress: false`: не отменять другие платформы при отказе одной.
Зафиксировать фактические runner label, OS/image/version, arch/host triple, доступную RAM/disk и run/run_attempt/job identities.
Unavailable runner/setup failure — NOT_RUN/INCOMPLETE с причиной, не замена на Intel/другую Ubuntu/macOS.

Caps по образцу: job **360 min/платформа**, regression subprocess **не более 20400 s (340 min)**,
штатный compiletest timeout **2400 s/test**. Максимальный суммарный job envelope — 1080 runner-min;
это предел, не оценка длительности или гарантия завершения. В FULL-GATE-REQUEST явно описать резерв setup/receipt/upload.
Observer должен завершать subprocess до job deadline с запасом для receipt/upload (целевой запас 10 min);
его фактический timeout — min(20400 s, оставшееся job-время минус резерв), без повышения cap.
Если setup съел резерв, оформить incomplete, не запускать заведомо незавершаемый gate и не урезать suites.

Ограничить общий regression stdout/stderr/event stream **256 MiB/платформа** и parser этим же пределом;
receipt/metadata суммарно ≤16 MiB, artifact package ≤384 MiB/платформа, retention 14 days.
Бounded чтение/запись и summary counts (до 20 строк/стадию, строка ≤4096 bytes); превышение → explicit
`TRUNCATED`/`INCOMPLETE`, неизвестные поля UNKNOWN, никакого успеха по обрезанному потоку.
Не ставить глобальный RLIMIT_FSIZE на setup/build и не выгружать target/sysroot/исходные архивы.
Timeout/output cap/cancellation должны завершать всю process group (TERM→bounded grace→KILL), сохраняя original exit/signal.
OOM/runner loss отдельно от test failure; не добавлять низкий RSS-watchdog, меняющий штатную регрессионную нагрузку.

## 4. Полный неизменный regression и observer

Исполнить **один раз `bash scripts/kani-regression.sh`** из exact export без редактирования скрипта,
фильтров, выборочного продолжения, tee-пайплайна, новых ignores и suppressions.
`KANI_REGRESSION_KEEP_GOING=""`, timeout 2400; не задавать RUST_TEST_THREADS и не ослаблять проверки.
Отклонить неожиданные внешние RUSTFLAGS/KANI_FLAGS/CBMC_FLAGS/EXTRA_X_PY_BUILD_ARGS/BASH_ENV overrides;
штатные scoped RUSTFLAGS внутри самого скрипта разрешены. Не сохранять полный environment/секреты в artifacts.
Никаких глобальных object-bits12, --no-slice-formula/arrays-uf или отключения checks;
принятые per-fixture 12-bit flags остаются в неизменных tests.

Observer адаптировать из `scripts/kani3300-gate/{receipt.py,test_receipt.py,binding.json}` старого patch.
BASH_ENV/DEBUG/EXIT допустимы только для top-level original regression: не инструментировать дочерние shells/tests,
не менять `$?`, errexit/pipefail/argv и исходный exit скрипта. Неполный exit trace не восстанавливать как успех.
Проверить Bash/Python/POSIX переносимость на macOS и ARM: без обязательных GNU timeout/date/stat/sha256sum/time,
Linux `/proc` или предположения о Bash 4+; явный Bash и Python hashing/process-group control.
Перед настоящим regression добавить дешёвый observer self-test на synthetic shell (success/failure/EXIT/order),
не запускающий cargo/Kani: ошибка наблюдателя останавливает строку до regression с явным статусом.

Сверить STAGES с **actual frozen script**, зафиксировать его hash и source lines. Сейчас обязательны 33 стадии:

1. CBMC version; Kissat version; fmt; cargo build-dev (4).
2. Unit: cprover_bindings, kani-compiler, kani-driver, kani_metadata, compiletest, kani-cov,
   kani с concrete_playback, kani_macros с kani_sysroot + syn/extra-traits --lib (8; итого 12).
3. Compiletest dry configuration; build kani-cov (2; итого 14).
4. Все 15 suite/mode пар **в штатном порядке**: kani/kani, expected/expected, ui/expected,
   std-checks/cargo-kani, firecracker/kani, prusti/kani, smack/kani, cargo-kani/cargo-kani,
   cargo-ui/cargo-kani, script-based-pre/exec, coverage/coverage-based, cargo-coverage/cargo-coverage,
   kani-docs/cargo-kani, kani-fixme/kani-fixme, json-handler/exec (итого 29).
5. Firecracker codegen; cargo smoke trivial_success; cargo clean того manifest; финальный
   RUSTFLAGS="-D warnings" cargo build с cprover и штатным target-dir (4; итого 33).

Receipt на каждую платформу: ordered stage presence/command/mode/exit/counts, passed/failed/ignored/filtered,
script exit, termination kind/signal, timestamps/duration, actual timeout/caps, event hash/completeness,
source/overlay/run identities и clean before/after. Setup/preflight/observer имеют отдельные statuses вне этих 33 стадий.
Не переносить C1b count values: counts собираются заново, platform-specific ignores/нулевые suites требуют объяснения.
Test oracle PASS с intended verifier FAILURE/Unsupported отличается от неожиданного compiletest failure;
внезапный новый ignore/filter/skip, отсутствующие counts, повтор/потеря стадии или ненулевой exit запрещают COMPLETE.

Сохранить actual binary paths/versions и SHA-256 для Kani compiler/driver/runtime/models, CBMC/goto-instrument,
Kissat/используемых solvers, rustc/toolchain и dependency/submodule identities; отражать отсутствие как UNKNOWN.
Между architectures бинарные hashes различаются штатно: сравнивать source/pins/coverage, не требовать одинаковых binaries.
Записать effective top-level argv и allowlisted environment policy; полный verifier argv не изобретать, если он не наблюдался.

Artifact preservation/upload — `if: always()`, уникальные имена с OS/arch/run attempt, без конфликтов matrix rows.
Fallback receipt при setup failure хранит binding/platform и причину; не заменять им уже существующий частичный receipt.
Hard runner loss может лишить EXIT/upload: GAP, не автоматически test failure или success.
После трёх строк отдельный lightweight summary `if: always()` объединяет доступные receipts/матрицу и отмечает missing rows;
failure/CANCELLED/MISSING не маскировать зелёным aggregate step. Это не четвёртый regression job.

## 5. Подготовка, deliverables и STOP

Python synthetic tests: complete 33-stage stream, исходный nonzero exit, missing/repeated/out-of-order stage,
missing/failed/count overflow, timeout/signal/output truncation, setup-only failure, неправильный SHA/tree,
missing matrix row и одна failed row при двух complete. Проверить end-to-end synthetic shell observer без compiler.
Статически проверить workflow, Bash syntax, binding hashes, direct parent и overlay path allowlist;
не запускать штатные regression/setup scripts локально. macOS/ARM execution validation остаётся будущим CI.

Выдать в `kani3300/c2-gatea/`:

- `INPUTS.md`, `EXPORT-MANIFEST.json`: exact source/tree, refs, script/setup/toolchain/dependency/subtree hashes.
- `FULL-GATE-REQUEST.md`: три платформы, 33 стадии, caps/reserve, один dispatch, coordinator-only push/dispatch,
  no retries, критерии приёмки и явный NOT_RUN.
- `ci-only-overlay.patch`, `CI-OVERLAY.json`: локальный clone/branch/commit/parent/tree, changed paths и hashes,
  точная инструкция координатору push/dispatch **этого overlay SHA**, без force/движения freeze.
- Observer + synthetic test source доступны в patch; `VALIDATION.md` с реальными локальными результатами и ограничениями.
- `receipt-template.json`/schema и `REVIEW.md`: per-platform fields и aggregate acceptance; template не имеет PASS-данных.

STOP при source drift, необходимости менять frozen source/deps/oracles или фильтровать suites,
непереносимости observer без изменения смысла, отсутствии обязательной привязки/наблюдения или выходе за caps.
Возвращать точный blocker, не ремонтировать candidate под тем же freeze и не начинать дополнительные попытки.

Worker-ready означает только подготовленный overlay/CI request: **Gate A NOT_RUN**.
Будущая приёмка координатором требует трёх полных receipts с exact source identity, 33 завершёнными стадиями,
нулевыми неожиданными failures и без неизвестных/truncated участков; aggregate exit0 сам по себе недостаточен.
`COMPLETE_EXIT_ZERO_REQUIRES_REVIEW` — технический статус, не автоматическое proof credit/разрешение публикации.
Без SmallSort/SEL1 replay, perf/LLBC/других штатных workflows: этот запрос только про полный kani-regression Gate A.
Не читать/скачивать raw CI archives/logs для подготовки; использовать названные curated материалы. Cloud evidence — через Brief.
Research не commit/push без отдельного поручения. В конце сессии: `READY <local CI-only overlay sha>` и путь к FULL-GATE-REQUEST.
