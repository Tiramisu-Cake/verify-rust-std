# KANI3300 MARKER-MODES — private-state diagnostic and unclaimed modes (DRAFT / NOT ISSUED)

2026-11-13. Предлагаемый worker15, одна ограниченная implementation/preparation session. **Не выдан.**
Это верификация корректности, не security-работа. Сейчас только черновик, без создания clone/ветки, изменений кода и запусков.
После отдельной выдачи local cargo/rustc/Kani/CBMC/Miri/builds запрещены; Cloud $0; CI запускает координатор после GO.
Никаких raw-log downloads, source push/публикаций и nested subagents. Это не реализация отложенного G-SC.

## 1. База и владение

Exact Kani base `ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677` (CLOSURE-ZST + correction flags + heavy fixtures b12).
Read-only source `/root/kani-fix-3300-closure-zst`; после выдачи isolated clone `/root/kani-fix-3300-marker-modes`,
ветка `fix/kani-3300-marker-modes` от exact base; dirty/wrong base → STOP без reset/stash.
Research g0 `experiment/kani-k1-kani3300g0-20261111`; task-prep HEAD `f95a821af94acb36b0875843e9499fa2bcff4b2d`.
Quick r6 43419217261 на принятой цепочке весь PASS по сообщению координатора; не регрессировать этот результат,
не менять production base на R7/R8 и не объявлять повторно закрытым ещё не выполненный полный gate.

Разрешённые write scopes после выдачи: `kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs`,
необходимые узкие internal plumbing/tests для required-state fact, `docs/src/reference/experimental/contracts.md`,
новые `tests/expected/uninit/contract-mode-boundaries/**` и/или `tests/json-handler/uninit-contract-mode-boundaries/**`.
Worker14 LAWFUL-ORACLES владеет lawful-modifies, существующими P1/P2/frame/clause inventories и
`tests/json-handler/uninit-contract-oracles/**`: здесь их не редактировать, его checker ещё не является зависимостью.
Не менять shared compiletest/JSON schema. Ветви готовятся параллельно; review/композиция/общий CI — координатором.

## 2. Conditional missing-marker diagnostic

Прочитать audit R3§9–13 и codegen/contract.rs::handle_check_contract/codegen_modifies_contract/attach_modifies_contract.
Сейчас lookup: find kani/core statics → fn_marker KaniMemoryInitializationState → Instance.mangled_name
→ symbol_table.lookup → whole-static Lambda; `.unwrap_or_default()` молча превращает оба вида отсутствия в empty assigns.
Нужно заменить **неявную потерю требуемого private state** явной диагностикой, сохранив прежний successful path.

Не путать три условия:
1. uninit-checks выключены;
2. uninit включён, но в проверяемом DFCC extent не нужны private shadow-state writes;
3. uninit включён и такие writes нужны, но уникальный marker или соответствующий emitted symbol отсутствует.
Только3 — missing-state diagnostic; отсутствие marker/symbol в1/2 не должно ломать обычный PFC.
Флаг доступен через `self.queries.args().ub_check.contains(&ExtraChecks::Uninit)`; один флаг **не** доказывает3.

Сначала описать REQUIRED-STATE.md: откуда берётся локальный fact required/not-required для конкретного contract/extent,
какие actual transformed helpers/writes он покрывает, и почему не теряются Set/Copy/AssignUnion/Begin/Store/Load,
immutable seed и indirect helper paths. Есть reachable MonoItems в handle_check_contract; их наличие не равно writes внутри extent.
Reset при входе harness и clause bookkeeping вне frame не считать самостоятельно свидетельством required private assigns;
чужой root в том же unit также не основание. UNKNOWN нельзя по умолчанию превращать в false.
Indirect helpers связывать с effect/call chain от конкретного transformed modifies-wrapper, не со списком всех reachable items:
тот же helper может вызываться только из requires/ensures или другого кода вне проверяемого extent.
Предпочесть существующие transformed/codegen данные или маленький per-contract fact; не строить новый общий analysis framework.
Если корректного bounded predicate нет, STOP с конкретным препятствием до расширения instrumentation/межмодульного дизайна;
не подменять цель `uninit && !symbol` и не вводить blanket требование для всех контрактов.

При required=true различить missing marker, marker найден/no emitted symbol, неоднозначный marker/symbol.
Выдать устойчивый compiler/model diagnostic с contract/context и стадией lookup через штатный diagnostic API,
не panic/ICE и не поздний случайный `assignable` failure. Не маскировать broken-model error как успешную verification.
При найденном state сохранять **тот же whole-static assigns target** и все user modifies targets;
не добавлять пользовательские pointees, global wildcard exemption, scalar-field targets или новый private static.
Не удалять найденный старый target только из-за uninit-off: успешный lookup path сохраняется без побочной переработки.

Контроли lookup/условий:
- uninit-off PFC без marker/state usage → нет новой ошибки, нормальный контракт;
- required=false с absent marker/symbol → нет новой ошибки; этот lookup branch проверяется synthetic resolver/unit fixture;
- required=true + отсутствующий marker → ровно новая targeted diagnostic;
- required=true + marker definition есть, GOTO symbol отсутствует → отдельная targeted diagnostic;
- required=true + duplicate/ambiguous marker/symbol → отказ, не произвольный `.find()`;
- required=true + корректное state binding → один прежний private target, пользовательский assigns unchanged.
Fault injection — узкие compiler/unit fixtures/чистая testable helper, без публичного CLI/production отключения marker,
второго испорченного runtime или нового test-only trusted skip. Нельзя выдавать наличие shadow write внутри extent
за no-state case; один reset вне extent, напротив, сам по себе не доказывает required private assigns.
Чистый resolver unit проверяет ветви, но не доказывает source→emitted lookup: добавить хотя бы нормальный integration control.
В реальном uninit-on/no-shadow integration reset обычно делает state reachable/emitted: не требовать естественного отсутствия
объекта. Проверить отсутствие новой ошибки и shadow writes **внутри wrapper extent**, а не отсутствие state глобально.

## 3. Replace/Recursive: строка и regression controls, без новой семантики

Решение владельца: **Replace (`stub_verified`) и RecursiveCheck с shadow transfers не заявляются как поддержанные Part1 режимы**.
Добавить короткую явную строку в публичную limitation-секцию contracts.md; согласовать терминологию с contract_mode.
Это не означает запрет всей рекурсии, всех stubs или ordinary/SimpleCheck/Assert и не доказывает unsoundness каждого такого input.
Не писать «Unsupported», если implementation не выдаёт такой определённый исход.

Нужны отдельные малые regression fixtures для реальных Replace и RecursiveCheck под uninit-checks:
ориентироваться на существующие tests с `stub_verified`/`kani::recursion`, а не угадывать macro API.
Contract-mode выбор в `transform/contracts.rs::contract_mode`: actual verified_stubs/recursion metadata + transformed mode/body binding.
Inputs — valid MU.new/uninit, ordinary/simple-check legal companion, реальный by-value shadow transfer через helper/return;
не создавать invalid typed value до целевой операции. Одинаковые source contracts должны различать intended mode, а не потерю root.
Для Replace обязательны helper/return и requires/ensures path: проверить, где возникают проверка payload/демонический return.
Для RecursiveCheck обязательны actual recursive edge/reentry replacement, не просто атрибут на невыполненном пути;
явный небольшой unwind/bound по существующему образцу и обе ветви base/recursive.

Сначала фиксируются source-level семантические ожидания и mode/transfer map; после coordinator CI — полный per-root inventory,
lawful prefix и конкретная граница (например, current false uninit/protocol failure). Не угадывать точный failure из source.
Если ожидание не установлено статикой, состояние BINDING_PENDING/NOT_RUN, а не произвольный golden «FAILED».
Использовать имеющийся JSON export для полного completed outcome/наборов failures; не зависеть от незавершённого worker14 checker.
Безопасный частный SUCCESS записать как результат этого input, **не** повышать до general mode qualification;
не заставлять его падать лишь ради документационной строки. Неразрешённая root/mode/path привязка остаётся gap.
Негатив с лишним Unsupported/ранним unrelated frame failure не доказывает нужную границу.

Не менять any_modifies/Arbitrary(MU), assert→assume, hooks pairing, mode selection, checks или S3.
Отдельный blanket guard/cut для Replace/Recursive здесь **не** разрешён; если нужен, вернуть отдельное предложение координатору.
Тест фиксирует реально воспроизведённую boundary, а строка сохраняет честный scope; не маркировать xfail как квалифицированную proof.

## 4. Проверки, CI-request и результаты

После будущей выдачи локально только source/type audit, синтаксические/synthetic проверки без cargo/rustc/Kani.
Обязательны unit scenarios для lookup truth table, неизвестного required-state и ambiguous/false-positive cases;
явная type audit Rust operand types, API/import/error-flow; formatter сам по себе не typecheck.
CI-REQUEST: targeted compiler units + integration uninit-off/no-state/normal-state + два mode roots и companions,
точный predeclared список/число roots/caps утверждает координатор. Heavy tests используют принятую b12 policy,
`-Z unstable-options` перед consuming `--cbmc-args --object-bits 12`; normal solver/slicing/checks без изменений.
Не запускать CI и не переносить старые grants. Build error → downstream NOT_RUN; staged units ≠ verifier acceptance.

С worker14 общий финальный gate после review: lawfully allowed user/private writes всё ещё проходят,
P2/postcondition-hole сохраняют mapped checks, frame-negative падает на пользовательской *outside записи;
missing-marker diagnostic не подменяет ни один из этих semantic результатов. Затем один согласованный Quick + новые selected suites,
M3/platform/SmallSort — отдельно. Не брать вторую ветку за уже зелёную и не угадывать новое количество тестов.

В research `kani3300/marker-modes/`: INPUTS.json, REQUIRED-STATE.md, LOOKUP-CONTROLS.md,
MODE-SCOPE.md, TEST-MANIFEST.json, CI-REQUEST.md, REVIEW.md, RESULT-MARKER-MODES-PREP.md≤35строк.
Указать exact changed files, отсутствие blanket guard/exemption/semantics rewrite, все NOT_RUN/binding gaps.
Source commit от ee2695e5a2, author/committer через `-c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, без push/CI overlay.
Research `[skip ci]`, stage только свой directory, без push. После будущей выдачи финал `READY <source-sha>`;
если predicate/тест требует большего дизайна — точный STOP/handoff, без самовольного расширения. Сейчас **DRAFT / NOT ISSUED**.
