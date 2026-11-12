# CBMC ZST-BITS2EXPR — narrow utility fix + tests, worker 15

**Source + отдельный CI-only пакет, 2026-11-13.** Runtime Codex, одна стадия на сессию, **Cloud $0**.
Это верификация корректности, не security-работа. Это отдельный B3 backend-трек, не возобновление G-SC/PFC resource.
**Без локальных compiler/CBMC builds/verifier runs, worker CI/Cloud dispatch, push и issue/PR публикаций.**
Владелец создал **https://github.com/Tiramisu-Cake/cbmc**, default develop, Actions включены; нового решения о создании форка не нужно.
Worker готовит source/tests и отдельно CI-only workflow. Все push/запуски в этом форке выполняет координатор; публикаций нет.

## Вход и база

Прочитать `kani3300/cbmc-zst-bits2expr/PLANNER-PLAN.md`, `kani3300/b3p/ISSUE-DRAFTS.md` @d377f342f49b2e39498745198df73f4d1999a593,
CBMC root AGENTS.md, CODING_STANDARD.md, README/COMPILING, regression/README.md и инструкции в изменяемых подкаталогах.
AGENTS — гайд для AI, запрета нет; требование local build из общего workflow переопределено явным запретом владельца.
Исходники читать из upstream diffblue/cbmc (develop и cbmc-6.11.0); owner fork — место будущего CI.
Чужие PR/их код в задание/реализацию не переносить.

Exact develop base **107a1e504cd69a2f3483717c8bcfcfa59814c557**, tree b5a15d682996f745e0a02004d813e18d08f3a068.
Release comparison cbmc-6.11.0 **820ff0f555b43fb78e0cd9332e498461bd14244b** — read-only, не база предлагаемого PR.
Создать обычный local upstream clone `/root/cbmc-fix-zst-bits2expr`, branch `fix/zst-bits2expr` от exact develop.
Клонирование исходников не создаёт GitHub fork. Existing/dirty clone/branch → STOP без reset/stash/чужих файлов.
Проверить upstream develop ещё раз; если сдвинулся — сохранить заданный pin и сообщить diff relevant sites,
не переходить на новую базу молча. Эта версия source-review всё ещё имеет array el_size>0 invariant, runtime на ней NOT_RUN.

## 1. Обязательное source обоснование и узкая реализация

Проверить `src/util/simplify_utils.cpp::bits2expr/expr2bits` и caller из `src/util/simplify_expr.cpp::simplify_byte_extract`.
Array: constant count → pointer_offset_bits(element) → CHECK_RETURN(present && width>0) → recursive slices i*size,size.
Struct уже допускает component width0; empty struct восстанавливается из empty bits; tags/union выбирают/сохраняют типы.
Минимальное направление: **только array branch**, known width>=0 вместо >0 (develop использует bitst{0}).
При width0 existing loop должен породить N typed elements через bits2expr(empty,element); count0 — пустой array_exprt.
Сначала обосновать этот путь, не вводить лишний zero-initializer branch, если достаточно существующей recursion.

Сохранить top-level type-width/bits consistency, optional failure unsupported subtype, constant-count precondition,
unknown/negative width guards и непреждевременный cast в size_t. Не менять ABI/layout/frontend/endianness rules.
Не заменять enclosing W нулём/empty struct, не добавлять fake bits/assume, не выбрасывать nonzero members/assertions.
expr2bits уже конкатенирует empty strings: менять только при конкретном новом failing roundtrip того же scope.
Zero-width outer-result byte_extract guard сохранить. Не ослаблять все >0 в vector/complex/lowering по аналогии.
Смежный fix допустим лишь если необходим для этого же valid repro и минимально обоснован; независимая проблема → STOP/proposal.

TYPE-AUDIT: optional/bitst comparisons, size_t conversion, operand reserve/count/type/tag, substr bounds при size0,
recursion termination и endian mapping. Большой N при zero extent может увеличить IR без увеличения bits — описать риск,
не расширять эту стадию в array compression/array_of optimization или обработку произвольных symbolic sizes.

## 2. Tests в том же source-коммите

Ориентиры существующих regression/cbmc/: Empty_struct1/2/3, empty_compound_type2/3/4, byte_extract1,
Struct_Bytewise1, union-unequal-element-size1. Просмотреть их actual descriptors/semantics, не считать совпадение имени coverage.
Новые focused CORE cases в `regression/cbmc/zst-bits2expr-*` (или соседнее согласованное имя), main.c + test.desc.
Используем GNU C **empty struct**, не C++ (там empty class обычно ненулевого размера). Маркер gcc-only по стилю существующих tests;
это tag для исключения MSVC, не самостоятельный dialect flag. Actual GCC frontend/target/mode записать в CI-REQUEST.

Минимальный независимый набор:
- typed dereference после memset0x5a для `struct E {}; struct W { E z[2]; char pad[8]; };`, проверка всех pad bytes;
- union typed copy с такой W первым подходящим arm и nonzero backing, полезные byte assertions;
- interior zero-width field в ненулевом arm/struct (`E z[2]; int x`/Tail-shaped), сохранение x и других neighbours;
- memcpy positive control той же geometry; не подменять им typed path, вызывающий defect;
- zero-array позиции first/middle/last, nested E[2][3], nonzero-element array длины0 внутри array, N0/N1/N2;
- negative companion: заведомо неверный **nonzero-field assertion** должен дать intended verification FAILURE, не crash/UNKNOWN.

Можно объединить формы в компактные files, но crashing base не должен скрыть результаты остальных обязательных случаев;
CI/request должен уметь вызвать их раздельно. Размеры/offset assertions относятся к выбранной GNU target модели.
Для struct с int обеспечить alignment backing (например aligned union storage), legal extent и полностью записанные bytes;
не смешивать нужный invariant с misalignment/OOB/uninitialized или непереносимыми предположениями о padding/endian.
Сохранить literal minimal repro владельца отдельно в research и сопоставить его со strengthened upstream test.
Assertions сохраняют nonzero patterns: fix, который только перестал падать, но обнулил payload, не проходит.

Добавить focused unit tests через public bits2expr/expr2bits API, если существующий unit/util harness подходит:
empty struct/array/nested conversion, exact element count/type и roundtrip empty bits; positive nonzero siblings и оба endian flags.
Unknown/negative/incomplete-width поведение не объявлять новым supported domain. Указать, что exact cases проверяют, а что нет.
Не создавать новый test framework и не добавлять known-crash PASS oracle для незакрытого соседнего failure.

## 3. Статика, packaging и review

Local builds/cargo/rustc/Kani/CBMC/C/C++ compilation и запуск regression/unit запрещены. Git/source/hash/Python static inspection
и clang-format разрешены; clang-format CI использует18.1.8, ориентир — actual pinned workflow/CODING_STANDARD, без global reformat.
Если нужного formatter нет — явно NOT_RUN, formatting обеспечивает координатор в CI; не выдавать визуальный осмотр за formatter PASS.
Один bounded Luna High review recursion/zero-width/byte preservation/test-oracles и типов, без nested delegation.
Исправить concrete findings, `git diff --check`; SOURCE_READY ≠ COMPILED/PASS.
Итог source — **один локальный commit от develop**: fix+regression/unit tests, одна feature; без workflow или несвязанных formatting changes.
Subject + обязательный **commit body**: symptom, zero-width mismatch, why recursion is valid, tests и честный CI NOT_RUN.
Author/committer Tiramisu-Cake <igkharin@gmail.com>; source commit без [skip ci]. Не push/force и не создавать ещё один remote fork.

## 4. Отдельный CI-only commit — исполнит координатор в созданном форке

Разрешены workflow/scripts и CI-REQUEST **как отдельная локальная CI-only ветка/commit** поверх clean fix+tests.
CI-only commit без [skip ci]: push-trigger должен исполняться, когда координатор решит запустить пакет.
Рабочая ветка для координатора: `ci/zst-bits2expr-<id>`. Из CI-only HEAD удалить **все** штатные файлы
`.github/workflows/`, оставить ровно один наш `.github/workflows/cbmc-zst-bits2expr.yml`.
Проверить inventory/count=1; удаление inherited workflows находится только в CI-only commit, не в clean source patch.
Fork default develop не менять. Координатор пушит **сразу CI-only HEAD**, не промежуточный source HEAD с тяжёлой upstream матрицей.
Для нового workflow выбрать push-trigger, ограниченный CI branch prefix: новый workflow_dispatch-only файл вне default
может не быть зарегистрирован GitHub. Публикацию ветки/запуск делает координатор, worker ничего не dispatch/push.

Один workflow, runner **ubuntu-24.04**, stock CMake configure + build **cbmc**; unit target только если добавлены unit tests.
JBMC/полная upstream matrix/benchmarks не нужны. Зафиксировать dependencies/compiler/CMake options и bounded build parallelism.
Точные команды взять из pinned COMPILING/CMake/workflow source; не использовать готовый release binary вместо нового source build.
Paired first gate: develop **с теми же test bytes** против exact fix+tests; provenance overlays, target/compiler/config/flags/hash бинарника.
Можно matrix baseline/fix с fail-fast=false и max-parallel=1; отказ baseline не должен отменить fixed configuration.
Execution checkout model refs отделить от workflow overlay; baseline получает только test-only delta, без fix/других source changes.
Общие fixtures/scripts побайтно одинаковы; case-to-source/tree/test/workflow/binary map обязателен.
Обе сборки только в Actions owner fork. CMake stock recipe из COMPILING.md, целевые cbmc/unit binaries;
resolved absolute path к binary, не двусмысленное ../../../src из примера AGENTS.
Targeted runner из `regression/cbmc`:
`../test.pl -C -p -c <absolute-cbmc-binary> <new-case-dir> ...`
Добавить стандартные --validate-goto-model/--validate-ssa-equation как в pinned Makefile, сохранить actual argv.
Если используются EXIT/SIGNAL regexes в desc, согласовать `-e`; проверить test.pl options на pin, не изобретать формат.
Positive требует VERIFICATION SUCCESSFUL/exit0 без invariant; negative — intended assertion FAILED/exit10 без extra failure.
Base crash фиксировать rc/signal/invariant отдельно, не выдавать его за expected suite PASS. Если develop repro уже не падает,
зафиксировать path/simplification и STOP: старый6.11 результат не переносится на develop автоматически.
После focused pass — соседние empty_struct/empty_compound/byte_extract/struct-bytewise/union cases и util unit tests;
добавить небольшой **явный список array cases** из pinned regression/cbmc. Соседи byte-ops/arrays/struct выбираются по имени,
не default `ctest -L CORE`/полный `make test`. При использовании ctest сначала проверить selection через ctest -N;
нулевой selected count — ошибка, не PASS. CTest и test.pl не должны незаметно дважды гонять всю suite.
Отдельными case прогнать literal C repro владельца и Kani-подобный C padded-union/embedded-ZST example с nonzero payload.
Это **CBMC C inputs**, не actual Kani/Rust replay и не закрытие Kani#5085/case B.
Широкий штатный regression перед PR отдельно согласует координатор. Новые solver matrices/benchmarks не нужны.
Per-case bounded logs + complete failed properties/exit/signal/rawKiB/time/identities, artifacts after failure;
нет grep|head acceptance, swallowed exit, blind retries или зеленого proof credit при kill.
Выделить configure/build/test timeouts и memory/parallelism limits в CI-REQUEST; artifacts upload через always().
Build failure → тесты NOT_RUN; baseline invariant/exit134 и intended negative exit10 не смешивать с timeout/OOM.
Ни один workflow/run в этой worker-сессии не исполняется: готовность только SOURCE_AND_CI_PACKAGE_READY/NOT_COMPILED.

## Результат и STOP

В t0 **kani3300/cbmc-zst-bits2expr/**: SOURCE-MAP.md, INPUTS.json (develop/release/code hashes), DESIGN.md,
TYPE-AUDIT.md, TEST-MANIFEST.json, REVIEW.md, CI-REQUEST.md, RESULT-CBMC-ZST-BITS2EXPR.md (≤30 строк), source/test patch.
Дополнительно CI-MANIFEST.json: clean source SHA/parent/tree, CI-only SHA/parent/tree, workflow/scripts hashes и allowlist diff,
полный список removed inherited workflows + ровно один remaining workflow, baseline test-delta hash и selected case list.
CI-only diff/patch хранить отдельно от source/test patch; author/committer тот же, никакого push/dispatch.
Планировочный PLANNER-PLAN.md сохранить; worker добавляет свои результаты, не переписывает исторические outcomes.
Issue/PR тексты можно подготовить **файлами**, не публиковать. Сначала подтвердить develop baseline/fix CI; затем владелец решает issue→PR.
PR target develop, одна feature, новая точная строка: *Disclosure: this change and description were prepared with the help of AI assistants.*
Не обещать исправление Kani#5085/case B до отдельно измеренного Kani replay на обновлённом CBMC; B3 workaround не откатывать.
Research commit [skip ci], тот же author/committer, stage только свой research каталог; **локально, без push до отдельного разрешения**.
Не читать raw CI/GCS archives/full logs/credentials; доказательства только из согласованных bounded reports.
После reviewed source/test и CI-only commits/CI-request STOP. Последняя строка: `READY <sha локального CBMC fix+tests commit>`;
CI-only SHA передать отдельным полем handoff координатору.
