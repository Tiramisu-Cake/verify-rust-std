# CBMC-SLIM — focused paired CI request (DRAFT / NOT ISSUED / NOT_RUN)

2026-11-13. Это верификация корректности, не security-работа. Запрос координатору, не разрешение запуска.
Один собственный workflow в `Tiramisu-Cake/cbmc`; **PR внутри форка запрещён**, upstream issue/PR/comments тоже.
Cloud $0. Worker готовит local CI-only commit; push/dispatch/caps — координатор после отдельного GO.

## Identity и три build configurations

BASE подтверждён fetch: `37a17adc07f29e1127f100debf1d8eea00532a24`; при будущем сдвиге freeze actual reviewed BASE.
FIX `fb9c8d53d4f5e109324d8b17fd8794ed4776b43e`; TREE `038a4b47e21ce8d5ebfcb29124d830fd38688235`; test delta sha256 `c788e7bddbaf0aee957087d41ae8d657652d2bbb88acf371c47faf9759e84c90`; baseline overlay TREE `73d8992542645f35d70763ac0be0b03acb0dd26d`. CI-HEAD указан в CI-MANIFEST.json; identities не являются разрешением запуска.
Directory: `regression/cbmc/byte_extract_empty_struct_array/`, один main.c и один positive test.desc.
BASELINE = BASE + exact final regression/unit test delta FIX, не old107a/старые13 tests.
Baseline/fix test hashes идентичны; production difference — только array-width comparison.
CI overlay отдельно от этого сравнения/PR source; source SHA/tree и overlay SHA записать раздельно.

Три clean configurations, минимальные project recipes из COMPILING и Make/CMake на BASE:
1. Baseline CMake: cbmc + `smt2_solver`, без unit run.
2. Fix CMake: cbmc + `smt2_solver` + `unit`.
3. Fix Make: настоящий Make build unit/dependencies, без CMake .o/libs/binary.
Раздельные worktrees/outputs; shared dependency downloads допустимы, stale build outputs — нет.
Ubuntu24.04/GCC13/Release, обычный SAT backend прежнего recipe; actual compiler/config/target/versions фиксируются.
Не принуждать descriptor к64/little-endian; normal CPP/platform defaults записать. Другие платформы не заявлять.

Preflight: установленный Z3 (version/path/hash/check-sat), project `smt2_solver` из текущей сборки/PATH,
Perl test.pl, build deps, clang-format **18.1.8**. `--cprover-smt2` запускает helper **smt2_solver**,
не executable cprover-smt2. Missing tool → SETUP_FAILURE, зависимые verification cases NOT_RUN.
Если профиль упрощается без solver invocation, записать: profile исполнен, actual solver path не доказан.

## Пять профилей × baseline/fix —10 cases

Через штатный `regression/test.pl`, cwd regression/cbmc, выбрать **только final directory**.
Common Make runner arguments: `-e -p -c <CBMC command>` + profile options + explicit directory.
CBMC_BIN — executable соответствующего CMake варианта; actual argv/cwd сохранить.
`-X gcc-only` применяется только к MSVC; на Ubuntu он исключил бы наш test, поэтому не добавлять.

| Profile | CBMC command | test.pl profile options |
|---|---|---|
| SAT + validation | `CBMC_BIN --validate-goto-model --validate-ssa-equation` | `-X smt-backend` |
| paths-lifo | `CBMC_BIN --paths lifo` | `-X thorough-paths -X smt-backend -X paths-lifo-expected-failure -s paths-lifo` |
| cprover-smt2 | `CBMC_BIN --cprover-smt2` | `-X broken-smt-backend -X thorough-smt-backend -X broken-cprover-smt-backend -X thorough-cprover-smt-backend -s cprover-smt2` |
| z3 | `CBMC_BIN --z3` | `-X broken-smt-backend -X thorough-smt-backend -X broken-z3-smt-backend -X thorough-z3-smt-backend -s z3` |
| incremental SMT2 | `CBMC_BIN --incremental-smt2-solver 'z3 --smt2 -in'` | `-X no-new-smt -s new-smt-backend` |

Это профили Makefile и соответствующих CMake registrations; у CMake **нет отдельного z3 profile**.
Solver string последней строки остаётся одним backend argument; проверить quoting/-c handling статически.
Не запускать `make -C regression/cbmc test*`/`ctest -R cbmc-...-CORE` как focused command — они выбирают весь suite.
Не добавлять -X tags и не менять descriptor ради обхода failure.

Для каждого case: ровно1 selected descriptor,0 skips/ignores, actual command с нужными flags.
Baseline expected — **bits2expr array invariant**, `Invariant check failed`, bits2expr, el_size_opt/positive-width condition,
не generic nonzero/test.pl fail/SMT2 Unsupported. Положительный test.pl oracle на базе не проходит закономерно:
только специальный baseline classifier с underlying output/exit/signal даёт ожидаемый differential result, не blanket `|| true`.
Fix: test.pl PASS, CBMC SUCCESS, EXIT0/SIGNAL0, нет ignored warning/invariant/timeout. Все10 results раздельно.

## Unit: два реальных build styles, четыре случая в каждом

unit/util/simplify_expr.cpp есть в explicit unit/Makefile и CMake glob; отдельного zst_bits2expr.cpp в candidate нет.
Проверить inclusion/list of executable tests в обеих сборках. Make path: `<fix-make-tree>/unit/unit_tests`;
CMake: `<fix-cmake-build>/bin/unit` (CMAKE_RUNTIME_OUTPUT_DIRECTORY). Не копировать один binary под два имени.

Точные Catch names, каждый запускать отдельно, default **console reporter**, без XML/JUnit:
1. `expr2bits and bits2expr respect bit order`;
2. `bits2expr reconstructs empty structs and arrays`;
3. `bits2expr reconstructs nested zero-width arrays`;
4. `bits2expr preserves tagged zero-width elements and nonzero siblings`.
List/names preflight требует matching set4; listing exit трактовать по Catch contract, не как обычный test exit.
Далее8 invocations: каждая matched1, assertions>0, exit0 и полный итог PASS. Ноль совпадений — FAILURE, даже при exit0.
Оба endian проверяются внутри3 TEST_CASE; это не два hardware platforms.
Полный212 util/весь unit/ctest/baseline util не запускать побочно. Старые2 subprocess errors не включать в PR narrative;
их XML-reporter diagnosis не разрешает проглатывать новые failures.

## Format, ограничения и receipts

Final diff: clang-format18.1.8 и project cpplint; empty format diff + exit0 — clean. Unrelated reformat unit-файла не включать.
На build steps **нет RLIMIT_FSIZE**. Existing bounded-drain capture, не head/grep-only; process-group cleanup,
original exit/signal, raw KiB, truncated/UNKNOWN, artifacts always. Не печатать secrets/environment credentials.

До GO caps утверждает координатор. Предложение: один build/solver одновременно, build jobs2, ≤45min/configuration,
runtime case≤120s/6GiB, unit case≤90s, setup≤15min, workflow≤210min. Это upper-bound request, не прогноз/разрешение расхода.
Cap/build error → STOP/зависимые NOT_RUN; adaptive retries/новые platforms/profiles не разрешены.

Case receipts: BASE/FIX/tree/test hashes, build-style/binary hash, actual versions/argv/cwd, descriptor/profile/selection,
underlying CBMC и runner exit/signal, bounded output outcome, wall/RSS KiB, cap/completeness.
Unit: binary provenance, matched-case/assertion counts. Constant manifest fields не доказывают built-source binding.
Для PR взять **из одного final baseline case** main.c, `cbmc --version`, actual argv и verbatim Invariant block;
File/Condition/Reason/команду не смешивать с historical6.11/r2 или другими profiles.

Acceptance: fix5/5 profiles, baseline5/5 именно array invariant, Make4/4 и CMake4/4 unit, final format/lint clean.
Иначе пакет не upstream-ready; auto issue/PR нет. Старый cd41/r2 PASS не переносится на новые inputs/BASE.
После CI result обновляет slim/RESULT и PR Testing двумя factual предложениями только на actual outcomes.
Публикация diffblue/cbmc PR и возможный комментарий kani#5085 — отдельные действия владельца.
Сейчас **DRAFT / NOT ISSUED / NOT_RUN**.

## Prepared implementation handoff

Local branch: `ci/array-zero-width-elements-slim-20261113`; source branch: `fix/array-zero-width-elements-slim`. One workflow `.github/workflows/cbmc-slim.yml`, only push on `ci/array-zero-width-elements-slim-*` in `Tiramisu-Cake/cbmc`. No dispatch or PR trigger. Use the exact CI-only SHA from CI-MANIFEST.json; no source push to origin/diffblue. Coordinator GO and cap approval remain required.

Runner creates three fresh trees; baseline applies the full final test-only patch with `--index --unidiff-zero`, then checks expected tree and hashes. Make passes Release flags through the environment so project config.inc warnings remain appended; WITH_MEMORY_ANALYZER=0 matches CMake OFF. Make's existing unit dependency recipe recursively builds source dependencies; no CMake outputs are reused.

All new build/test/formatter outcomes are NOT_RUN. Local Python AST/YAML parsing, static identities/allowlist/registration/transferred-body checks, cpplint and isolated Python service tests pass. RSS is recorded as sampled process-tree peak and cumulative child high-water usage, labeled separately; neither is an exact per-case kernel accounting claim. Runtime memory has RLIMIT_AS per process plus sampled process-tree enforcement. No build RLIMIT_FSIZE.

Probe receipts preserve underlying CBMC argv/cwd/exit/signal and bounded output independently of test.pl's shell status. All invocations stop at first unexpected outcome and retain unstarted states as NOT_RUN. Capture exceeding cap, timeout, signal, incomplete drain or missing binary/output are failures; no adaptive retries/exclusions. The final result snapshot and artifacts upload run on failure. If setup never starts the runner, not-run.json supplies all18 NOT_RUN cases. Workflow cancellation may leave IN_PROGRESS in the last snapshot; this is not acceptance.

Acceptance remains coordinator-only: all10 differential regression results, all8 focused unit invocations, final formatter18.1.8/lint/diff clean. Source receipts and exact test hashes do not independently prove built-source binding. No B1/B2/Rust/Kani or general solver-path credit is granted.

Final CI-only SHA: `b7f9d36ff2edf1b795b2273635872a57fd244ca1`; TREE `4465ca1ffee74550c35cf0bf9ad982b1f654bf0f`; sole parent clean source `fb9c8d53d4f5e109324d8b17fd8794ed4776b43e`.
