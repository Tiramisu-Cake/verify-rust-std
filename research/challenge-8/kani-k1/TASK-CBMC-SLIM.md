# CBMC-SLIM — one regression and Make/CMake unit coverage (ISSUED 2026-11-13 → worker15)

2026-11-13. Выдано координатором worker15; одна preparation/implementation session.
Это верификация корректности, не security-работа.
Локальные компиляторы/CBMC/Kani/builds запрещены; Cloud $0; push/CI — координатор после GO.
Upstream PR/issue и комментарии запрещены. Режим CI (свой узкий workflow или внутренний PR в форке) решает координатор с владельцем; готовь CI-only пакет под узкий workflow по CI-REQUEST.

## 1. Вход и точная база

Прочитать целиком `kani3300/cbmc-zst-bits2expr/AUDIT-REPORT-CBMC-ZST-BITS2EXPR-RU.md`
@t0 `42876420080053712844507498255a05b39d120e`, особенно §3 и З1–З6.
Research: `/root/verify-rust-std-kani3300-t0`, `experiment/kani-k1-kani3300t0-20261111`.
Source: `/root/cbmc-fix-zst-bits2expr`; сейчас clean CI branch `ci/zst-bits2expr-20261113-r1` @33235a4ef1.
Его историю/старый cd41a5c74b не переписывать. Старые результаты и issue draft — история, не действующий план issue.

Fetch в этой подготовке подтвердил develop **37a17adc07f29e1127f100debf1d8eea00532a24**.
Повторить fetch upstream develop и зафиксировать BASE. При сдвиге tip проверить relevant diff и перепривязать
CI/тексты к новому exact BASE. Уже исправленное условие или иной конфликт по смыслу → STOP, не делать дубликат.
Новая ветка `fix/array-zero-width-elements-slim` от BASE в этом clone, без reset/stash/amend старых веток.
Dirty/collision → STOP. `origin` указывает на **diffblue/cbmc**: source push туда не разрешён.
CI fork — `Tiramisu-Cake/cbmc`; local CI refs/remote допустимы, worker push — нет.
Прочитать AGENTS.md/CODING_STANDARD.md и PR template на BASE; local build ban выше примеров guide.

## 2. Clean source commit: З1–З4

Не cherry-pick старый 28-file commit. Единственная production строка в array branch bits2expr:
`src/util/simplify_utils.cpp`: `> bitst{0}` → `>= bitst{0}`.
Сохранить has_value, whole-type width checks, recursion, vector/complex guards и остальные типы.

Новый каталог **`regression/cbmc/byte_extract_empty_struct_array/`**, без ZST в имени:
- `main.c` — именно эскиз §3: GNU empty struct; `unsigned char a[4]`, `empty z[2]`, `unsigned char b[4]`;
  `memset(buf,0x5a,8)`, typed read и проверки всех четырёх байтов с каждой стороны. Не заменять memset инициализатором
  и не добавлять второй layout без нового paired evidence.
- `test.desc` — §3: `CORE gcc-only`, `main.c`, пустая строка options; anchored EXIT0/SIGNAL0/SUCCESS,
  forbidden ignored-warning/invariant и пояснительная секция после второго `--`.
  Не добавлять `--gcc`, `--64`, `--little-endian`, negative, memcpy-control или новые profile exclusions.

Три TEST_CASE из старого `unit/util/zst_bits2expr.cpp` перенести в **существующий** `unit/util/simplify_expr.cpp`
сразу после `expr2bits and bits2expr respect bit order`. Assertions/type/count/endian/roundtrip и названия сохранить,
теги `[core][util]` как в §3. Проверить includes, не дублировать их. Новый unit-файл не добавлять:
Make уже перечисляет simplify_expr.cpp, CMake находит его через glob; Makefile/CMakeLists ради этого не менять.

В свежем source delta нет прежних13 каталогов, negative/memcpy, отдельного zst_bits2expr.cpp,
новых `// Author:` строк или CI helpers/workflows. Старый block header существующего unit-файла сохраняется.
Allowlist: production cpp, существующий unit cpp, main.c/test.desc нового каталога — **четыре пути**.
Не расширять scope на lowering/SMT2. Обязательна static type/API audit переноса и bitst comparison;
formatter/source inspection не объявлять компиляцией.

Один новый source commit, один parent BASE, непустое тело: причина, почему empty slices сохраняют count/type,
одна фраза о consolidated regression и unit cases. Author/committer через
`git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`; source message без [skip ci].
Без force/push, переписывания cd41 или merge-коммита в source package.

## 3. Узкий CI-only пакет — подготовить, не запускать

Контракт: `kani3300/cbmc-zst-bits2expr/CI-REQUEST-CBMC-SLIM-draft.md`; после подготовки заполнить exact identities.
Новый local CI branch от clean source, один CI-only commit: удалить inherited `.github/workflows/*`,
добавить один push-filtered bounded workflow и минимальные scripts. Этот delta не входит в PR source.
Fork PR не открывать ради штатной матрицы. Координатор запускает собственный workflow в `Tiramisu-Cake/cbmc`.

BASE+**те же final test bytes** против fix, один каталог, пять профилей —10 regression invocations.
Unit: genuine Make и genuine CMake исправленного source, три перенесённых + старый bits2expr case —4+4 calls.
Baseline util/полный util/regression/platform matrix не назначаются. Раздельные outputs, без CMake .o в Make
и без старых binaries107a. Default console Catch reporter, не `--reporter xml`.
Final diff: clang-format18.1.8, project cpplint, diff checks. r2 PASS на новый пакет не переносить.
Все новые outcomes — NOT_RUN до coordinator CI. Версия/actual argv/main.c/verbatim invariant block для PR
должны происходить **из одной final baseline invocation**, не из смеси6.11/r2/develop.
Failed profile, skip/no selection, missing solver/build error → STOP; не добавлять exclusions/отключения проверок.

## 4. PR и отдельный Kani handoff — З5

`PR-CBMC-ZST-BITS2EXPR-DRAFT.md` рядом — текущий PR draft. Отдельный issue не готовить/не публиковать.
Кратко: defect/reproducer + matched version/command/invariant block, причина и one-line fix,
kani#5085 без Fixes/Closes, Testing ровно две фразы, checklist template дословно, disclosure:
`*Disclosure: this change and description were prepared with the help of AI assistants.*`
До нового CI измеряемые поля и Testing pending. После полного успеха допустимы две фразы:
“The new regression fails on develop with the invariant above and passes with this change.
It passes in the five standard regression profiles, and the four focused unit cases pass in Make and CMake builds.”
Это будущий шаблон, не уже установленный результат. Старые13/13/205/212 и fork-process narrative не переносить.
N/a пояснения к checklist отдельно от дословных пунктов. Source/version соответствуют final BASE.

Kani B3: перед **отдельным Kani PR** исправить comment в codegen/typ.rs около1319–1324 @6e9e782024,
где причиной назван lowering. Предлагаемый смысл: “CBMC's bits2expr constant reconstruction rejects zero-width array
elements in this nonzero-width padded struct.” Сохранить rustc-layout/recursive-arm пояснение.
Это handoff: Kani код здесь не менять, обход не снимать, #5085 закрытой не объявлять.

## 5. Результаты и STOP

В `kani3300/cbmc-zst-bits2expr/slim/`: INPUTS.json, SOURCE-MANIFEST.json, TEST-MANIFEST.json,
TYPE-AUDIT.md, CI-MANIFEST.json, CI-REQUEST.md, PR-READINESS.md, REVIEW.md, RESULT-CBMC-SLIM-PREP.md≤35строк.
Отдельно source SHA/tree/BASE/test-only baseline overlay, source/CI allowlists, Make/CMake registration и binary paths.
Допустимы static/Python/shell/synthetic service checks без компилятора/CBMC: missing solver, cap/signal,
0 descriptors, wrong pin/hash/profile, baseline unrelated failure и formatter empty diff.
Research [skip ci] от Tiramisu-Cake через -c, stage только свой пакет и явно обновлённый PR draft; без push/выдачи.
Непроверенные build/format/verdict — NOT_RUN; prepared package не означает upstream-ready.
Финал `READY <clean-source-sha>` и CI-only SHA в handoff.
