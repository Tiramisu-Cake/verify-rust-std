# TASK-DRAFT KANI3300 CMP1 — compound storage для IntoIter

**DRAFT, не GO/phase/dispatch. Runtime и новое окно назначает координатор.** CMP0 — статический дизайн, Cloud $0, все fixtures/expectations ниже NOT_RUN. Резерв CMP1 не утверждён; предложения планера $0.60 native/$0.80 core не являются бюджетом или резервом.

Перед стартом зафиксировать результат U3B, полный accepted Kani SHA, baseline/patch SHA256/applied tree, std/toolchain/tooling/profile/config pins, assigned worktree/branch, owner/lane/ledger, T0/deadlines и новый cap. Исследованный `81dd85bfce67226e283fdd9a156932e32ece080b` (tree `c5b24f0b0da999d1deb9758215790382fe5e3be4`) — reference, не автоматическая accepted base. Research source CMP0 — `92d9677bb3823126d91bfdad6f53948c028cc338`. Если U3B не разрешает PFC acceptance, не выдавать её за принятую: сначала отдельное решение координатора о base/границе.

Реализовать ограниченный product descriptor и transfers по DESIGN-COMPOUND: ordinary masks отдельно от MU storage, target offsets/stride, aggregate/Copy/Move/projection/argument/return, address/drop/delayed-set safeguards. Сохранить v2 flat ghost-state, copy_by_id и один argument buffer. Production owner один; SEL1 может готовить docs отдельно, но совместные изменения uninit_visitor.rs/storage-result интегрируются последовательно от exact tree и с review объединённого diff.

Не менять std/алгоритмы/CFG/domain/signatures, SKIPPED_ITEMS, contract flags/frame checks, fn-pointer/vtable/select, произвольные union/enum, nested union/MU, trusted premises или runner. Ordinary Option<usize> на next остаётся в прежней модели; новый enum со storage явно Unsupported. Whole DST transfer не нужен: reference unsize и field/slice projection обязаны сохранить состояние. Не подменять стандартный IntoIter ручным iterator или примитивной имитацией.

До Build: production patch+fixtures+goldens, статический source/pin/scope check, независимый Luna HIGH review semantic diff/dependencies, публикация immutable SHA/patch/tree, existing Cloud preflight/check-tooling. Никаких локальных cargo/rustc/Kani/CBMC. Native acceptance предшествует отдельному GO на core replay. Изменение модели/semantic diff возвращается тому же reviewer как delta; повтор прежнего Unsupported без нового исправления не dispatch.

Ниже точный **draft** manifest существующего `kani-tests` request schema, 20 file selectors, harnesses=[]; это фрагмент для нового RUN-REQUEST, без budget/dispatch authority. `expect=pass` означает golden match; только require_success=true требует всех harness SUCCESS. Все новые fixture directories/goldens ещё предстоит создать; существующие брать из принятой base с сохранением checks. Старый full-IntoIter golden ожидает Unsupported и должен быть заменён SUCCESS golden с прежними assertions и drop; просто сохранить native PASS прежнего golden недостаточно.

```json
{
  "schema": "kani-k1-run-request-v1",
  "request_id": "DRAFT-kani3300-cmp1-native-NOT-AUTHORIZED",
  "kind": "kani-tests",
  "harnesses": [],
  "kani_tests": [
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-wrap-u3-intoiter/main.rs","expect":"pass","require_success":true},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-fields-positive/main.rs","expect":"pass","require_success":true},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-empty-negative/main.rs","expect":"pass","require_success":false,"diagnostic":"Undefined Behavior: Reading from an uninitialized pointer of type `usize`"},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-overwrite-negative/main.rs","expect":"pass","require_success":false,"diagnostic":"Undefined Behavior: Reading from an uninitialized pointer of type `usize`"},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-call-positive/main.rs","expect":"pass","require_success":true},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-call-negative/main.rs","expect":"pass","require_success":false,"diagnostic":"Undefined Behavior: Reading from an uninitialized pointer of type `usize`"},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-projection-negative/main.rs","expect":"pass","require_success":false,"diagnostic":"Undefined Behavior: Reading from an uninitialized pointer of type `usize`"},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-padding-negative/main.rs","expect":"pass","require_success":false,"diagnostic":"Undefined Behavior: Reading from an uninitialized pointer of type `u8`"},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-zero-zst-positive/main.rs","expect":"pass","require_success":true},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-drop-positive/main.rs","expect":"pass","require_success":true},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-layout-unsupported/main.rs","expect":"pass","require_success":false,"diagnostic":"Kani does not support this compound storage layout."},
    {"suite":"expected","mode":"expected","file":"uninit/compound-cmp1-no-mir-unsupported/main.rs","expect":"pass","require_success":false,"diagnostic":"Kani does not support shadow-carrying arguments to calls without a MIR body."},
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-wrap-u3-positive/main.rs","expect":"pass","require_success":true},
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-wrap-u3-padding/main.rs","expect":"pass","require_success":false,"diagnostic":"Undefined Behavior: Reading from an uninitialized pointer of type `u8`"},
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-wrap-u3-source-read/main.rs","expect":"pass","require_success":false,"diagnostic":"Undefined Behavior: Reading from an uninitialized pointer of type `u64`"},
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-review-positive/main.rs","expect":"pass","require_success":true},
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-review-overwrite-copy/main.rs","expect":"pass","require_success":false,"diagnostic":"Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 2]`"},
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-buffer-u3-positive/main.rs","expect":"pass","require_success":true},
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-buffer-u3-frame-negative/main.rs","expect":"pass","require_success":false,"diagnostic":"is assignable"},
    {"suite":"expected","mode":"expected","file":"uninit/maybe-uninit-buffer-u3-no-mir-unsupported/main.rs","expect":"pass","require_success":false,"diagnostic":"Kani does not support shadow-carrying arguments to calls without a MIR body."}
  ]
}
```

Конкретные тестовые гипотезы (текст, не выполненная реализация): базовый `#[derive(Copy,Clone)] struct C { marker:usize, slots:[MaybeUninit<usize>;2] }`; дополнительно nested struct, ManuallyDrop<C> и generic вариант C<T> с ordinary marker:T для Pad. Не предполагать offsets repr(Rust), иметь repr(C) вариант с storage до/после ordinary fields. Каждый сценарий ниже — отдельный harness внутри соответствующего selector, не ослаблять negative ради общего golden.

| Selector suffix | Обязательный сценарий и ожидаемое наблюдение |
|---|---|
| wrap-u3-intoiter | Полный `IntoIterator::into_iter([7usize,9])`, next == Some(7), Some(9), None; normal return/drop; require-success; никаких Unsupported/assigns. |
| fields-positive | marker=11, slots=[new(7),uninit()]; Copy whole C/ManuallyDrop/nested wrapper, обе живые копии читают marker и slot0==7; slot1 не читается. Отдельно оба заполнены, reordered repr(Rust) и repr(C) field/index projections. |
| empty-negative | marker=11 рядом с пустым slot1: typed read slot1 после aggregate и Copy должен дать uninit usize, reached-read cover; slot0/marker до него успешно прочитаны. Отдельные harness читают source и destination Copy. |
| overwrite-negative | Destination сначала заполнен, затем whole-product Copy/Move из C с пустым slot1; чтение slot1 обязано отказать. Отдельные harness для initialized source с пустым slot0 и partial slots различают смещённые masks. |
| call-positive | `#[inline(never)] fn id(C)->C` и вложенный id, `fn pair(a:C,b:C)->C` выбирает каждый аргумент в разных harness. Смешанные full/empty slots сохраняются без чтения пустого; заполненный выбранный slot читается. Повторный вызов после полного возврата проверяет stale-buffer cleanup. |
| call-negative | Те же Move через argument/return/nested call, empty slot читается только в caller после return; отдельные harness выбирают first/second аргумент с разными empty-slot positions. Повторить после предыдущего initialized возврата; ровно ожидаемый uninit, не stale blessing. |
| projection-negative | После C construction обновить marker, взять &mut C/raw address, обернуть в ManuallyDrop и снова проецировать; reset только slots[1], slot0 остаётся читаем. Отдельный Drop impl читает пустой slot: обычный Drop SetRef не должен благословить payload (ровно uninit). |
| padding-negative | repr(C) ordinary `Pad{u8,u32}` рядом с MU storage; typed construct/write, Copy и call/return C<Pad> сохраняют false padding Pad. Через u8 pointer прочитать известный из target layout padding byte → uninit u8; data fields перед ним проходят. Не создавать padding read из uninit ordinary value. |
| zero-zst-positive | Полные стандартные `[].into_iter()` с явным `[usize;0]` и `IntoIterator::into_iter([(),()])`; None/Some и len; нулевые transfers не меняют соседний непустой field; без деления на size=0. |
| drop-positive | Стандартный IntoIter с обычным Drop-token, счётчик через безопасную reference/Cell: взять один элемент и drop iterator — каждый token дропается ровно раз; полностью исчерпанный iterator не дропает yielded повторно. ManuallyDrop<C> без explicit drop ничего не вызывает; empty storage не читается. |
| layout-unsupported | Отдельные harness: struct с arbitrary union, enum со storage, MU<MU<usize>>/nested union; каждый сохраняет явный compound-layout Unsupported, никаких SUCCESS или substituted initialized masks. Точный новый текст — проектируемая диагностика, не уже наблюдённый v2 output. |
| no-mir-unsupported | Bodyless/extern call получает C с partial storage: явный shadow-carrying Unsupported до Store; никакого unpaired buffer или ложного SUCCESS. Не вызывать реальный external код. |
| existing 8 regressions | wrap positive, padding/source-read negatives, review positive/overwrite-copy, plain+PFC buffer positive, user frame negative, bodyless flat-storage guard; сохранить исходные harness/assertions/controls. Frame golden из принятого U3B, фактический user-write source binding обязателен, одного `is assignable` недостаточно. |

Для всех negative сохранять полный bounded перечень Failed Checks, source location, достигнутое чтение и отсутствие неожиданных failures/Unsupported/ghost assigns. Для layout/bodyless guards ожидается только конкретный Unsupported; timeout/OOM/setup/error не expected negative. Для positives все intended covers/assertions и normal return, ноль failures. Отчёт через Evidence Brief; native golden-match, archive integrity и exit0 не formal proof credit. Source-based design не устанавливает AST/MIR binding: в Cloud отдельно подтвердить actual product/transfer пути и target offsets.

Не выбранные partial-copy/reset/overlap/MU→T и остальные U1/U1T/PFC regressions перечислить NOT_RUN в этом пакете; существующие fixtures/checks не удалять. При новых alias/overlap изменениях расширить controls в отдельном пакете, не потеряв обязательные отрицательные. Неподдержанный overlapping aggregate оставить Unsupported, вместо несогласованного capture/transfer. PFC buffer negative OOM из U3 не считать soundness counterexample или PASS; состояние после U3B фиксировать отдельно.

После всех 20 native PASS с корректными SUCCESS/expected failures и принятого semantic review запросить **новое GO** на отдельный core пакет: исходные exact harness U1 `uninit_probe::pincheck_calibration_uninit_read_u8`, U2 `uninit_probe::pincheck_calibration_init_read_u8`, U6 `uninit_probe::permutation_merge_u8_n4`, U8 `uninit_probe::small_sort_general_with_scratch_u8_n4`, U9 `uninit_probe::small_sort_general_scratch_unwritten_slot_u8_n4` (до dispatch раскрыть полные paths из actual source). Сохранить calibration source/required assertions/covers, literal uninit/function-contract flags, panic/domain premises и нормальные source/tool identities.

U1 — прежний единственный uninit u8 отказ, U2/U6 — SUCCESS с normal return и прежними checks/covers. **U8** — normal return, прежние проверки/cover достигнуты, SUCCESS, без Unsupported/ghost assigns/uninit/validity failures. **U9** — подтверждённое успешное чтение scratch[3] и его covers, затем единственный uninit u8 отказ на scratch[4], все intended covers достигаются; отсутствие ошибки scratch[3] само по себе недостаточно. Новая причина остановки сохраняет U8/U9 OPEN; число checks может меняться из-за instrumentation, сами свойства/проверки не ослаблять.

U7 select, fn-pointer U4, u64/N8 и общий theorem/B2 вне этого scope. Резерв считать заново по final native/core selectors, полным timeout+queue envelope, текущим ledger/caps и окну; не переносить неиспользованный резерв ночных U3/U3B. После результатов — exact immutable patch/tree, review, Evidence Brief claims с assurance и честный handoff; никакой автоматической публикации upstream.
