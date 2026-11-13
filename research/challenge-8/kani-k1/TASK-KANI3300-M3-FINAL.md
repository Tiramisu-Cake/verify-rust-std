# KANI3300 M3-FINAL — composition and mixed-root qualification (ISSUED 2026-11-13 → worker14)

2026-11-13. Worker 14, отдельная следующая сессия после E1/X1. Это верификация корректности, не security-работа.
Выдано координатором. Local cargo/rustc/Kani/CBMC/Miri/builds запрещены; Cloud $0; CI/push — координатор.

## Start receipt

Вход не произвольный HEAD: координатор задаёт C0 SHA/tree = принятые E1 + X1 поверх
`94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`, semantic-edge dispositions и targeted/Quick results.
94 Quick43465107918 — исходное свидетельство, не результат C0. Старый M3 HELD документ — история, не новая база.
Без C0 manifest/решения по открытым edges — STOP до source changes. Isolated clone/branch, без reset/stash.

## Composition: до восьми новых selectors

Переиспользовать existing masks/transfers/typed-data/call-pairing/Move/PFC controls и source-bound mixed C1-T2-A.
Взять snapshot `7f9eec41e892dad0ca64673dab3de88d17d010af` из `/root/kani-fix-3300-c1t`:
только16 файлов `tests/expected/uninit/mixed-promoted-allocations/**`, bindings в research `c1t2/TEST-MANIFEST.json`
и `c1t2a/INPUTS.json`. Сам commit7f меняет только четыре Rust inputs относительно C1-T2; одного его cherry-pick
недостаточно для импорта16 файлов. Сверить hashes исходного manifest с четырьмя repair updates, перенести отсутствующие
tests без старой production chain. Если уже присутствуют/изменились — exact equivalence/delta. Старые outcomes не proof C0.

Новые маленькие roots в `tests/expected/uninit/part1-composition/**` должны сочетать, а не дублировать отдельно:
1. nondet immutable-promoted/stack origin + alias/helper + nonzero src/dst offset; оба operands, legal/hole companions;
2. raw full-extent copy vs typed data/stride на flat `[MU<T>;N]`/slice, сохранение source-following false;
3. initialized → overwrite/reset → bad read и reinit → legal read; без reseed mutable destination;
4. Move/call return/live-source handoff и reinit в принятом supported domain, reuse actual normal-edge controls.
У каждого row: allocation/mask/carrier→object/offset→reset/seed/setter/transfer→retained intended read/property.
Одна nondet shadow witness — не bitmap; false counterexample обязателен на source-following ветви,
но exact false на каждой optimistic ветви не требовать. Some(0) не None, typed padding не raw extent.
Не использовать `MU<[MU<T>;N]>`, invalid initialized refs на hole, new heap/realloc/foreign/ZST domain.

## Mixed roots — настоящие два порядка

Маленький набор: immutable legal/hole, ordinary Assert/ensures legal и PFC legal/negative,
плюс mode-boundary fixtures с repeated nonrecursive callee и genuine cycle. Existing inputs сохранить.
Каждый root отдельно; затем совместный unit A/B и B/A, fresh process/model, normal single-run worker concurrency.
Сравнить complete per-root required/failure inventories и binding actual selected body/mode, masks/registry locality;
cycle Unsupported не должен перекинуться на unrelated legal root. Не выводить contamination из одного различия counts.

Source declaration/CLI selector order сам по себе не доказывает codegen order. Нужен bounded receipt actual producer order
от координатора/существующей диагностики с exact identities. Если оба порядка не удалось создать/наблюдать —
`ORDER_UNCONTROLLED`, конкретный CI request, без matched-AB/BA credit. Не чинить broad shared-cache architecture здесь.
Существующие лишние SUCCESS checks допускаются лишь после operation/source attribution; пропавший required check/лишний FAIL — STOP.

Новый `tests/json-handler/uninit-part1-composition/**` может собрать эти comparisons и exact per-root оракулы;
не импортировать private tooling W15 и не менять его два suites. Использовать неизменённый shared validator.
Поддержать lost-check/extra-failure/wrong-root/incomplete cases; no substring-only FAILED и no automatic golden learning.

## Приёмка и freeze

Разрешены новые tests и минимальный доказанный bounded composition fix в E1 allowlist;
новая model/runtime/cache/DFCC policy → STOP с отдельным proposed stage. Никакого source-panic fallback.
`git diff --check`, explicit Rust type/offset review; local Python checker tests без compiler/verifier допустимы.
CI-request: composition/mixed qualification + неизменённые eight strong oracles/mode roots + existing Quick,
объектный профиль тяжёлых cases 12. CI NOT_RUN до координатора; ожидаемые Unsupported не legal proof.

`kani3300/m3-final/`: INPUTS, COMPOSITION-MAP, ROOT-ORDER-MAP, TEST-MANIFEST, REVIEW, CI-REQUEST, RESULT.
Записать deferred rows/UNKNOWN и accepted edge limitations. Source commit(s) neutral, автор/коммиттер Tiramisu-Cake
<igkharin@gmail.com> через `git -c`, без push. Координатор интегрирует reviewed package в C1 и квалифицирует именно C1;
все export cleanups уже должны быть внутри. W15 затем binds full gate/replay к тому же export SHA/tree.
Финал: `READY <source sha>`. Нельзя объявлять Part 1 release-ready до отдельных final gates.

## C0 receipt (координатор)
C0 = Kani `53d883add` (/root/kani-fix-3300-e2, ветка fix/kani-3300-e2): 94c00a885 → E1 dc24745c6 → X1 (cherry-pick 478aad601)
→ E2 19588e0af (immutable named statics в M1, фикстуры transmute) → координатор 68dd1f3cd/53d883add (clippy-импорт,
rustfmt, immutable-subrange-legal = задокументированное консервативное ограничение: подрезы с ненулевым offset не сеются).
Quick run 43481108546 ВСЁ PASS: kani 22/0, expected 185/0, ui 14/0, script 1/0, json-handler 2/0.
Semantic edges: константный union-аргумент — fix; (*ptr).field=v — fix; unsized by-value transfer — явный Unsupported;
immutable: named statics — seed; subrange offset — known limitation (fail-closed false FAIL); relocation-legal — PASS.
Isolated clone для M3: `/root/kani-fix-3300-m3` (git clone из /root/kani-fix-3300-e2), ветка fix/kani-3300-m3 от 53d883add.
