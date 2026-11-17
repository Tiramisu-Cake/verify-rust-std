# W11 — S2: offline merge-invariant pilot

Все относительные пути — от `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Это верификация корректности, не security-работа. Отвечай кратко. GO на эту стадию
дан сейчас. Fresh/current pane model, без субагентов. STOP только по реальному blocker
с evidence, не по объёму/контексту. Pins: `kani3300/s2-f4-coordination/INPUTS.json`.

Только offline design/pilot по actual bidirectional_merge на source99e, CAP32,
u8/default order. PLAN-CH8-ITEM2-SORTING-v2.md §6 — исходный контракт, не новый дизайн
всего sorting model. W13 готовит cost batch независимо: не ждать его и не менять
его source/control, smallsort.rs или frozen S1. Ни compiler worktree, ни CI не нужны.

Дать точное соответствие actual loop sites/variables и invariant clauses: четыре
фронта/consumed counters, disjoint src/dst, init/writable frame, ordered prefix/suffix,
remaining input и full-value counts. Проверить init→paired-write preservation→odd
leftover→exit/post; все indexed comparisons guarded, k0/empty/exhausted fronts и
wrapping_sub sentinel корректны. Ord-panic исключается из lawful inputs, не stub.

Отдельно закрыть описанную §6 C5/query-count ловушку: len4/src[1,9,2,10], output9/2,
probe0 не должен служить ложным order proof. Выбрать конкретную sound bounded форму:
полный multiset invariant либо guarded endpoints+самостоятельный order argument.
Один произвольный query probe требует ghost-independence и сохранения того же probe
через summaries. Явно разделить доказательные obligations и диагностические переборы.
Не считать native/Python enumeration индуктивным Kani proof или S3 qualification.

Минимальный executable Python pilot для формул и meaningful negative mutations:
unguarded endpoints, потерянная/дублированная величина, weak count/order, wrong frame,
odd leftover. Показать какие проверки различают каждый дефект и какие proof obligations
ещё требуют Kani. Никаких local cargo/rustc/Kani/CBMC/rustfmt/full runner/solver sweeps.

Write только `kani3300/ch8-s2/merge-pilot/`: INVARIANT.md, source-site/obligation map,
pilot/tests и compact validation receipt, HANDOFF с точным API/geometry для будущего
интегратора13. Core attrs давать только как предложение, не применять. Если найден
конкретный semantic blocker — локализовать, остальной полезный pilot закончить.
Не раздувать scope до arbitrary-length insertion, generic T/F или combined extra-UB.

Offline stage costs0 CI. Budget/reference только из INPUTS; никаких push/CI/rerun/
cancel/reservation/ledger/публикаций. Stage exact own paths, не add -A/reset/rebase;
`[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <full g0 SHA>`
с выбранной invariant формой/оставшимися obligations либо реальный STOP.
