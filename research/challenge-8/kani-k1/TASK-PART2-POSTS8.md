# PART2-POSTS8 — разделить sortedness и full-value count исходного u64 N8

**Dispatch только после exact-packet GO координатора.**
Runtime: **Claude Code**, tmux4, одна стадия на сессию, **без субагентов**. Worktree `/root/verify-rust-std-kani-partposts`, ветка `experiment/kani-k1-partposts-20261102`;
slug **partposts**, stable owner **k1-network**, новые stage/ledger/UUIDs/request_id `partposts-*`.
PART2-FAST terminal; его ledger не возобновлять. База **`2104e7a596fabb058a99c8bcdf0e3f487d9a7753`**
(`experiment/kani-k1-partfast-20261102`, unchanged MACSPLIT/v6 library), tree
**d4ec476a7a001363e58f19948c188a9c2078e370**. В ней есть K-1 tooling и свежие FAST records.
Не merge integrated PARTTWO-TREE/audit/SPLIT31/U64 composition sources.
**Cap стадии$2.50**, два плановых Build, максимум3: один общий compile-error повтор на всю стадию.
Wall window main180min+closeout30min, T0 при старте; full envelope каждого submit должен помещаться
в main с finishing reserve. Разрешённый cap не гарантирует, что дополнительная попытка поместится в окно.
Project текущий cap$88.96, used по входному RESULT$82.293. Владелец разрешил повышение до$95 при необходимости;
самому ledger cap не менять. Для этого плана повышение не требуется при указанных цифрах. Перед GO сверить current
global/night spent/reserved/slots и действующий ночной лимит; повышение global cap не означает отмены ночного лимита.

## Вопрос и исходный domain

Получить два более дешёвых direct proofs вместо совместной постпроверки в
**network::network_correctness_u64_n8**, сохранив её **полный объединённый claim**.
Исходный combined root/его helper/macros оставить без изменений и измерить на том же новом library tree.
Исторический organizer partition timing636.2s на macOS — мотив пилота, не текущий matching baseline.

T=u64, exact initialized `[u64;8]=kani::any()`, offset0, полный pre-state copy;
independent full-width probe:u64=any. **F — существующий function-item `network::strict_less::<u64>`**,
inferred `let mut cmp = super::strict_less::<u64>;`, обычный `<`. Не создавать новый comparator function item,
не annotating/coercing F в `fn(&u64,&u64)->bool`, не переходить на StrictU64 profile/model.

Actual `<u64 as UnstableSmallSortTypeImpl>::small_sort`: Freeze+Copy/efficient swap →small_sort_network;
при len8 presorted_len1, actual insertion_sort_shift_left offset1 вызывает raw insert_tail tails1..7,
затем no_merge return. **Sort9/sort13/merge здесь не выполняются.** Не вызывать insertion helper напрямую
вместо actual trait entry; не копировать/изменять алгоритм.

Read pinned `verify/network.rs`: network_correctness_fixed/cases, strict_less, is_sorted_by,
count_matching_values, prefix_unchanged, old combined N8; actual dispatch/insertion/raw insert_tail;
PART2-FAST RESULT и существующие tooling/preflight/expected-check conventions.
Source paths verify ниже относительно `library/core/src/slice/sort/shared/smallsort/`.

## Source scope и два positive roots

Изолированный opt-in child **network::posts**, файл **verify/network/posts.rs**;
в network.rs только `#[cfg(kani_smallsort_controls)] mod posts;` после existing items.
Parent-private helpers доступны child как `super::...` без widening visibility.
Не вызывать parent macro из child с неверными относительными путями; новые roots — plain proof fixtures.
Ровно4 новых roots:2 positive +2 negative. Ordinary202/PFC36 и все old roots/bodies/annotations неизменны;
static cfg-on384→388, opt-in182→186, проверить exact name-set delta. Native inventory здесь не запускать.

Оба positives `#[kani::proof]`, unwind25/unwinding assertions; **никаких stubs, PFC, verified summaries,
assume/any_where для payload/probe, уменьшения width/range, отсечения panic или новых contracts**.
Setup повторяет исходный checker: full any backing8, pre copy до entry, independent any u64 probe,
тот же parent function-item cmp, actual entry. В sorted root probe может быть неиспользуемым; это не premise.
В count root не сортировать prefix constructor-ом и не ограничивать comparator/input исходным порядком.

1. **`network::posts::partposts_sorted_u64_n8`** — после actual entry assert исходный
   `super::is_sorted_by(&v,&mut cmp)`. Count post здесь не вычислять/проверять.
2. **`network::posts::partposts_count_u64_n8`** — после actual entry assert исходный typed
   `super::count_matching_values(&pre,&probe)==super::count_matching_values(&v,&probe)`.
   Sortedness post здесь не вычислять/проверять. Payload/probe остаются u64, count — usize, без masks/casts.

По3 required covers каждому, эквивалентных исходным: actual output differs from pre через prefix_unchanged;
fixed length8 normal return; family/check reached end. Все после actual return и нужного post-check.
Не удалять sort-moves cover и не добавлять ради этой оптимизации тяжёлые новые quantified/trace covers.
Корректное fixed-N оформление может отличаться от старого macro selector; отметить это в source diff,
не приписывать всю разницу VT изолированной стоимости одного assertion.

В PREBUILD явно записать логику замены: для тех же input/F/executions sortedness и count доказаны отдельно;
count root универсален по independent probe, поэтому оба accepted proofs вместе дают исходные свойства.
Один PASS не закрывает combined domain. Omitting post-check не меняет сортировку: parent sortedness checker
на фиксированном pure strict_less не пишет input/state; никаких новых global probes/ghost contexts нет.

## Два отрицательных контроля — full-u64 witnesses

Использовать **те же parent typed predicates**, что в positives, и тот же function-item/actual entry.
Узкие witness inputs разрешены только controls. Ни cover в helpers/targets/adapters, ни cover после failing assert.
Прежний mutant_small_sort_network относится к N10 и не является N8 control; его не переиспользовать/менять.

3. **`network::posts::partposts_order_negative_u64_n8`**:
   P=1u64<<40, Q=1u64<<41; input `[P,P,P,P,P,P,P,Q]`, probe=P.
   Выполнить real entry; прежде порчи проверить sortedness/count against pre, root cover returned-before-corruption.
   Ручными обычными присваиваниями обменять v[0] и v[7], сохранив multiset; assert тот же full-u64 count unchanged.
   Root cover order-check reached **до** последнего assertion.
   Expected FAILED только literal **`partposts negative: sortedness`** у исходного is_sorted_by predicate.
   Required covers2/2. Старшие bits отличают P/Q, младшие32 одинаковы; count должен пройти, порядок — отвергнуться.
4. **`network::posts::partposts_count_negative_u64_n8`**:
   input `[P;8]`, probe=P, тот же P/Q. Выполнить actual entry, проверить исходные posts;
   root cover returned-before-corruption. Затем v[7]=Q: sortedness сохраняется, count(P)8→7.
   Assert исходный sorted predicate, root cover count-check reached **до** последнего assertion.
   Expected FAILED только literal **`partposts negative: full-value count preserved`** у того же typed count equality.
   Required covers2/2. Не ограничивать positive probe/input этими свидетелями и не менять их post-check helpers.

Unexpected initial-post/count/order/UB/unwinding/unsupported/coverage failure не засчитывать intended-negative.
В annotations table у всех4 новых roots только proof+unwind25, stubs отсутствуют. Исходный baseline тоже direct/no-stub.

## Два пакета, один возможный compile repair

Frozen measurement profile: gcb-e2-standard-4 →k1-standard4,4CPU/16GiB/swap off,
controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10/600s per row, прежние checks.
Kani **9461e07af7ec929f050aa4192f29363c9be07779**, nightly-2026-10-12,
tooling **30f77e859903df14b442ff9294d4fbbd44827f20**, check-tooling против него.
Request full names с prefix `slice::sort::shared::smallsort::verify::`.

| Пакет | Exact rows / expectations | Reserve |
|---|---|---:|
|G1|только old `network::network_correctness_u64_n8`, expect SUCCESS|`(10+30)×$0.0135=$0.540`|
|G2|два новых positives SUCCESS +order/count negatives FAILED только своими literals|`(4×10+30)×$0.0135=$0.945`|

План$1.485; **один** compile-error repeat любого из пакетов, reserve максимум$0.945,
общий верх полных резервов$2.430≤cap$2.50. Это не по одному repeat каждого: максимум3 Build всей стадии.
Для repeat новый UUID/request_id/review/GO, исправленный compile input, тот же question/domain/rows/profile;
own fact_spent+следующий reserve+ещё неотправленные плановые reserves≤cap, current global/night/slots/deadline допускают.
Не повторять неизменённую compile-failing конфигурацию. Tooling/runner не менять.

G2 после terminal/accounting G1 или его разрешённого compile repeat, **независимо от proof-исхода baseline**.
Baseline TIMEOUT/OOM не отменяет split experiment; при заведомом общем compile blocker сначала repair,
после исчерпания одного repair — NOT_RUN/HANDOFF, без заведомо некомпилирующегося следующего пакета.
Resource/semantic/coverage failure не разрешает повтор того же пакета, дополнительный split/summary/highmem,
увеличение timeout/RAM или сужение input/probe. G2 TIMEOUT/OOM — per-row facts и стоп, не автоматически ещё один Build.

Оба пакета на одном frozen library tree; полные source SHAs могут различаться request/research metadata.
После compile repair record source-dependency equivalence: old combined root/его helpers/runtime неизменны;
новые positive/negative semantics не ослаблены. Если изменены уже проверенные зависимости, прежний result
не proof нового кандидата; PASS до reconciliation не объявлять и новые semantic reruns не добавлять.
Project≤2 queued/running/unresolved, ≤1 на k1-network. Не трогать docs/audit worktree tmux1 или чужие ledgers.
До первого GO проверить, что оба плановых reserves и полные envelopes доступны; не тратить всё окно на baseline.

PRE-BUILD: semantic diff/dependencies, исходный combined root byte/source preservation; T/F/geometry/probe/
property equivalence, actual route map, annotations/covers/literal table, negative witnesses/reachability;
ordinary202/static388 set delta/PFC36, target ordering/pfc_order, static rustfmt/whitespace;
source/library/tree/request/pin/tooling hashes, budgets/slots/deadline. Library/research commits отдельно `[skip ci]`,
reviewed candidate publish без force. Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD`
в фоновом Bash task Claude Code; без Codex watch/CODEX_THREAD_ID/polling-субагентов/новых сессий.

## Gate, performance и отчёт

**Split proof gate**: оба positives SUCCESS/0 unintended failures/3 из3 covers; controls только designated
failures с2/2 каждый; source/domain/profile equivalence соблюдена. Old baseline gate отдельно.
Если baseline дал настоящий counterexample/UB, а split прошёл — это discrepancy, до объяснения не рекомендовать
замену для v7. Resource failure baseline оставляет только timing UNKNOWN, а split gate оценивается по своим rows.

Сравнить **max VT(sorted,count)** и их **сумму** с завершённым baseline VT; control VT/compile/Cloud wall отдельно.
При baseline TIMEOUTcap600 не вычислять speedup из600 как будто это VT. При отсутствии выигрыша сообщить это:
такой исход не отменяет bounded proof, но не делает split полезной CI-оптимизацией.
Обязательный proof fit≤600s; screening target max примерно≤250–300s GCB с запасом RAM, не формальная macOS калибровка.
CBMC row RSS отдельно; compiler/driver/process-sum по Build. Не приписывать общий G2 driver peak каждому root.

`RESULT-PART2-POSTS8.md` ≤40 строк: reviewed/build/request/library/tree/pin/tooling identities,
5-row table (baseline+4 новых), exact F/backing/probe/properties, checks/covers/status/VT/CBMC RSS,
packet peaks/spent/reserved/gates, max/sum comparison и scope equivalence; missing поля UNKNOWN, OOM отдельно.
PASS новых proofs — opt-in decomposition исходного domain, не generic F/N theorem или ordinary promotion.
Не добавлять credit для other backings/offsets, stability, uninit detection/full alias-validity или Rust unwind;
loop unwinding assertions при25 не являются proof unwind-cleanup/ownership.
MacOS/jobs3/600s с целевым запасом400–450s OPEN до отдельно разрешённого v7 exact-tree CI обеих ОС после аудита.
Передать published RESULT координатору для audit addendum, не менять чужой audit report самостоятельно.

Evidence bounded K-1 summaries/rows/peaks/targeted excerpts; Evidence Brief/Select-Merge к K-1 не относятся.
Raw archives/full logs/Cloud Logging/credentials/hidden configs/competing code не читать/скачивать.
Нет local cargo/rustc/Kani/proofs, Actions/deploy/PR submission; исторические evidence/ledgers сохраняются.
Маркеры `REVIEW REQUEST <sha>` / `PART2-POSTS8 ЗАВЕРШЁН`; одна стадия, затем стоп.
