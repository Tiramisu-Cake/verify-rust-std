# KANI3300 B1R — статическая передача
- Input: TASK-KANI3300-B1R.md в research f8e3ab9534; только B1R, Cloud $0.
- Kani base: 835cb4a09c4e94ac6b531d20e68f9deee7262ce1; production 500eae8; tests/HEAD 29bde289d60d9f6f36c16310f6bce697338f7641.
- Коммиты поверх B1, автор/committer Tiramisu-Cake; Kani push не выполнялся.

| InstanceKind / исход | Путь после ремонта |
| --- | --- |
| Shim с has_body() | Общая с Item ветка: обычный MIR callee, StoreArgument для прямых union args; без blanket Unsupported. |
| Shim без тела | Явный Unsupported до вызова: calls to bodyless Shim instances. |
| Virtual | Явный Unsupported trait object method calls; vtable target статически неизвестен. |
| LlvmIntrinsic | Явный Unsupported; reachability::collect_instance прямо указывает отсутствие Rust body. |
| Intrinsic | Существующие явные memory effects/skip whitelist; остальные Unsupported. Fallback-policy не изменена. |
| Item | Существующая ветка foreign allocator effects / union StoreArgument сохранена. Foreign/realloc model не расширялась. |
| FnPtr / FnDef resolve Err | Единственный локальный Unsupported; ранее собранные ops/entry loads публикуются общим epilogue; один super_terminator. |

- Основание bodyful Shim: kani_middle/reachability.rs::collect_instance собирает Shim и Item; visit_fn использует transformer.body_ref.
- transform/mod.rs::BodyTransformation::body_ref применяет UninitPass к MIR callee без фильтра Item; find_all ставит union LoadArgument в entry.
- Поэтому caller/callee union-протокол теперь совпадает для bodyful Shim и Item; это не расширение memory model из будущей A3.
- FnPtrShim допускается снаружи, но его внутренний fn-pointer Call должен получить обычный Unsupported; B1-added shim-{plain,seeded}.expected обновлены под этот путь.
- Запрет менять regression goldens применён к существующим upstream-регрессиям из задания: vec-read-init, весь quantifier-capture и delayed-ub-unsupported-call побайтно равны bf9c58e662.
- Все шесть custom-MIR fixtures передают --edition 2021 -D warnings; custom_mir/core_intrinsics включены, internal_features локально разрешён; optimized MIR и inline(never) сохранены.
- compiletest/header.rs::load_from разбирает compile-flags; runtest.rs::run_kani передаёт их в RUSTFLAGS, поэтому core/mir import получает edition 2021.
- pending-ops plain/seeded: первый bb — Call f(*pointer); visit_place собирает raw-pointer Check до Err/Unsupported; ожидается named indirect.safety_check FAILURE.
- entry-partial plain/seeded: entry LoadArgument затем CheckRef value.word в Call до Unsupported; Word{byte:42} оставляет часть u32 uninit; ожидается FAILURE.
- entry-initialized plain/seeded: тот же LoadArgument/CheckRef, Word{word:42} полностью initialized; ожидается SUCCESS safety check и отдельный Unsupported.
- Before ops сохраняют порядок в relevant_instruction::push_operation и UninitInstrumenter::build_check_for_instruction; safety checks не assume, последующий Unsupported не скрывает их в исходной инструментализации.
- Шесть custom-MIR goldens требуют named property, diagnostic и ровно один failed harness; seeded-варианты сохраняют безопасный copy_nonoverlapping seed.
- static-checks.json: шесть source-structural checks PASS; это не compiler/MIR execution evidence и не доказательство фактического достижения свойств.
- rustfmt wrapper --config-path rustfmt.toml и --check: PASS; git diff --check для B1..HEAD и upstream..HEAD: PASS.
- Source audit -D warnings: новых imports/locals/feature attrs нет; полноценная компиляция, macro expansion и actual named-property outcomes НЕ проверены.
- Локальные cargo/rustc/Kani/CBMC, builds/dispatch/Actions/Cloud, raw evidence/credentials не запускались/не читались.
- Следующий исполнительный gate — fork CI координатора на exact Kani HEAD: все шесть fixtures должны скомпилироваться и показать указанные named checks; существующие регрессии — прежние outcomes; FnPtrShim — внутренний Unsupported.
- Независимое Luna HIGH review: PASS, findings нет; REVIEW.md. Committed delta packet f4bb3648f8f5df1be44a43b7ee23375e74e331f0f10f6196c99c4b56d06eb412 проверен review check.
