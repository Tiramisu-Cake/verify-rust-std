# KANI3300 E1 — semantic edges before final export (DRAFT / NOT ISSUED)

2026-11-13. Worker 14, одна будущая стадия. Это верификация корректности, не security-работа.
Сейчас только черновик; не создавать source branch, не менять код и не запускать CI по этому документу.
После отдельной выдачи: exact base `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`, isolated clone/branch,
Cloud $0; local cargo/rustc/Kani/CBMC/Miri/builds запрещены, push/CI — координатор. Dirty/wrong base → STOP без reset/stash.

## Цель и границы

Закрыть четыре вопроса R3, ответ 10 (`AUDIT-REPORT-KANI3300-PART1-R3-RU.md`), до M3 на final export.
Это bounded correctness/reproducer stage: минимальный локальный фикс или точный fail-closed guard с control;
новую модель/протокол/домен не вводить. Сначала составить source→actual MIR/операция→guard/setter→read/property map.
Кодовые выводы до CI помечать SOURCE-REPORTED/NOT_RUN; E0277 и ранний unrelated Unsupported не квалификация target edge.

## Четыре обязательных ряда

1. **Константный by-value аргумент обычного union.** Достичь именно `Operand::Constant` в argument transfer,
   проверить `relevant_instruction.rs::operand_ty` и материализацию. Valid storage, legal companion и настоящий hole
   после transfer; materialize с сохранением data mask/false либо узкий явный Unsupported до частичных операций.
   Не `unreachable!()`/ICE, не all-true mask и не выдавать MU constant за ordinary union. Сравнить variable-operand companion.
2. **`(*ptr).field = v`.** Valid raw-pointer field store с ненулевым offset/alias: записанное поле затем читается legal,
   соседнее незаписанное поле даёт intended uninit-read. Setter затрагивает ровно поле, не весь parent/padding.
   Не формировать invalid initialized `&T` до intended read. Legal falseFAIL — дефект, не expected negative.
3. **Immutable origins вне M1 admission.** Различить qualified whole allocation, nonzero-offset/subrange,
   relocation-bearing immutable и named static. Не требовать отказа всех named statics: их может покрывать прежний static path.
   Для каждого: legal и actual-hole, источник allocation/mask/offset, M1 admission или независимый existing path.
   Никакого необоснованного seed/bless, reseed mutable copy или Some(0)=None. Необслуженный legal path классифицировать
   как limitation/falseFAIL и вернуть решение по выпуску, не маскировать его golden "обычный UB".
4. **By-value DST со слотами MU.** Сначала установить expressible valid source на pinned toolchain и фактический
   Slice/Move call operand. `&mut [MU<T>]`/Box/fat pointer — не by-value unsized argument.
   Если путь достижим — explicit unsupported-size guard до size-dependent transfer, плюс legal sized/by-reference companions.
   Если source недопустим — документировать reachability и проверить compiler-side guard unit test, не считать compile error
   проверкой runtime-модели. Не расширять scope до `MU<[MU<T>;N]>`, heap/realloc или новой ABI.

Не размножать cases: переиспользовать существующие initialized/transfers/reset/typed-data/masks controls, а новые
поместить в `tests/expected/uninit/part1-edges/**`. Ожидания зафиксировать по смыслу до CI; после CI привязать exact
root, source operation, failure class и полное множество failures. Если ожидается Unsupported — точная причина/граница,
а не произвольный FAILED. Требовать matched legal companion, чтобы ранний guard не скрывал intended negative.

## Write scope и приёмка

Compiler allowlist: `kani-compiler/src/kani_middle/transform/check_uninit/`,
прежде всего `ptr_uninit/uninit_visitor.rs`, `relevant_instruction.rs`, `ty_layout.rs`;
при доказанной необходимости существующий codegen operand/immutable-allocation guard. Перечислить exact touched paths.
Не менять runtime, points-to/contract body selection, DFCC, driver, shared JSON schema/compiletest и existing JSON suites W15.
Если минимальный исправляющий diff выходит из этого договора — STOP с repro и локализованным предложением.

Ручная проверка типов каждого нового Rust operand/cast, projection offsets и integer widths обязательна;
не подменять её неподдерживаемым локальным compiler run. `git diff --check`, fixtures/expected map и bounded source review.
Сохранять CC1 cycle fail-closed, CC2 ordinary argument slots, CC3 upvar layout, M1 masks/S3 и strong oracles.
Нет source-panic fallback, skip checks, assumptions об initializedness и смены expected ради зелёного набора.

Research `kani3300/final-edges/`: INPUTS (SHA/tree), EDGE-MAP, CONTROL-MAP, PATCH-REVIEW, CI-REQUEST, RESULT.
CI-REQUEST: tiny singleton edge controls, unchanged legal PFC/ordinary + eight strong oracles, затем existing Quick;
heavy tests object-bits 12 как на принятой базе, без глобального ослабления profile. Любой regression/ICE/lost check → STOP.
Source neutral commit(s) в isolated clone, author/committer Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push.
Research package отдельно, без CI overlays в export. Финал после выдачи: `READY <source sha>`; CI qualification — координатор.
