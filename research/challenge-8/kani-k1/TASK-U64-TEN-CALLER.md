# U64-TEN-CALLER — actual Unstable u64 N10 через matching swap и insertion summaries

**Решение координатора: standard4, отдельные positive и controls Builds, frozen tooling.**
Runtime: **Claude Code**, исполнитель сам, **без субагентов**. Worktree
`/root/verify-rust-std-kani-usixtyfourtencall`, ветка `experiment/kani-k1-usixtyfourtencall-20261102`,
база `f057b7e4ebebd2050861976ee8bb0ee0172703c2` (U64-TEN-LEAVES);
library commit `e4c696648a5a4ff4f92dbe1ec7ed145afea25ee8`, tree `3c600416e508b037ebdfe817f6dc93d0314c9b21`.
Stable owner **k1-network**; новая стадия/UUIDs/request_id `usixtyfourtencall-*`, slug **usixtyfourtencall**.
Project cap $88.96; свой cap **$2.80**. Два плановых Build: G1 positive, G2 controls;
по одному compile-error повтору каждого, максимум4 Build с разными UUID/request_id.
Использовать **k1-standard4, 4CPU/16GiB, $0.0135/min, swap off**, без highmem/tooling patch.
PRE-BUILD REVIEW + exact-packet GO координатора обязательны для каждого Build.
Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` в фоновом Bash task Claude Code;
без Codex watch/CODEX_THREAD_ID, polling-субагентов/новых сессий. Evidence Brief/Select-Merge к K-1 не относятся.

## Ресурсное решение и frozen profile

Оба пакета — штатные **measurement** requests с runner **gcb-e2-standard-4** → pool **k1-standard4**.
Tooling baseline **`30f77e859903df14b442ff9294d4fbbd44827f20`** неизменён; `check-tooling` против него обязателен.
Kani `9461e07af7ec929f050aa4192f29363c9be07779` / nightly-2026-10-12, checks и flags прежние.
Tooling/runner/coordinator/IAM/dispatch не менять, kind не подменять на resource, highmem не включать.

G1 и G2 — разные Builds, поэтому G1 positive стартует в свежем процессе driver без результатов трёх controls;
G2 тоже стартует заново. Это проверяемая гипотеза о снижении накопления памяти, не гарантия RAM-fit.
В u8 NETTEN-CALLER driver перед positive уже удерживал около6.59GiB, а общий пик был14.10GiB.
Его пик при отдельном positive не измерялся; пиковая память одиночного u64 positive также неизвестна.
OOM/TIMEOUT G1 не разрешает positive retry/highmem/сужение; controls G2 всё равно выполнить по правилам ниже.

## Цель, маршрут и independent leaves

Перенести механизм NETTEN-CALLER @ `61cfba69c3dac0b87324d2845c1164e08222d0a6` на **u64/U64Cmp/StrictU64**,
не переносить его u8 targets/context как новые доказательства u64.
T=u64; F=U64Cmp=fn(&u64,&u64)->bool; value StrictU64::CMP=reified strict_less::<u64>; обычный `<`,
полные64-битные input/probe. Exact initialized backing10, offset0, independent any u64 probe.
Actual `<u64 as UnstableSmallSortTypeImpl>::small_sort`: Freeze+Copy/efficient swap → sort9 prefix9
(25 raw swap_if_less), insertion_sort_shift_left offset9 → **один raw insert_tail(begin0,tail9)**,
no_merge return. Sort13/general/merge/scratch здесь отсутствуют; actual алгоритмы не заменять.

Принятые matching leaves: Build `dd2f7e52-52a5-46fd-a8a2-d5658713ad90`, reviewed source
`9009451c82740af506708b7a2217099b57970807`, RESULT-U64-TEN-LEAVES @f057b7e4eb:

| Existing target / fixture | VT s | Checks / covers |
|---|---:|---|
| swap_u64_net9; prefix9/backing10, pair-only writes, tail frame | 100.61334 | 0/413 failed, 9/9 |
| insert_tail_profile<StrictU64>; begin0/tail9/backing10, sorted-prefix requires | 79.74734 | 0/640 failed, 9/9 |

Оба real-body no-stub PFC; full any u64 и independent probe, high-bit hit covers. Их bodies/contracts/fixtures/
annotations/dependencies сохранить. Это reused evidence старого Build, не rows нового caller Build.
PRE-BUILD reuse record связывает source/target/T/F/CMP/model/probe/backing/init/frame и отсутствие semantic drift.
Оба новых пакета сохраняют прежние tooling/Kani/profile semantics и typed leaf domains; различается набор rows.

Read tenleaves.rs/u64nine.rs (swap_u64_net9, U64Cmp/canonical/count9_u64), network.rs StrictU64,
merge/specfix.rs insert_tail_profile/tail_region/tail_len/model_count/model_sorted, actual dispatch/sort9/
insertion/raw helpers. NETTEN-CALLER source и TASK — образец фаз/controls; TASK-SPECFIX/pfc_order.py — checks/ordering.

## Размещение и непересечение с PARTTWO-TREE

Новый opt-in child **network::u64nine::tenleaves::caller**:
`library/core/src/slice/sort/shared/smallsort/verify/network/u64nine/tenleaves/caller.rs`.
В tenleaves.rs только регистрация child после existing items. Private ancestor targets/U64Cmp/canonical/count9_u64
и parent sorted10_u64 доступны descendants без widening visibility. Dedicated ContextU64Ten, не CONTEXT_U64_NINE.
Не менять прежние contexts/leafs/targets, не обобщать общий framework и не интегрировать другие proof-линии/v6.
PARTTWO-TREE идёт отдельно у k1-merge в tmux1 от MACSPLIT `4f4034527d` с library tree v6;
его файлы/ветку/requests/ledger не трогать, этот незавершённый caller туда не переносить.
Runtime smallsort.rs, generic signatures/CFG, workflows/tooling/runner/check flags неизменны.
Ordinary exact200; ровно4 новых plain roots → cfg-on401→405 статически, проверить exact name-set delta.
Это не native inventory/proof credit и не расширение ordinary v6/202.

## Один probe, две фазы и actual hooks

ContextU64Ten: root:*mut u64, probe:u64, initial_prefix_count9:usize, initial_count10:usize,
initial_tail:u64, swap_hits/insert_hits:usize, fail_swap/fail_insert:bool.
Register вне targets до actual entry: snapshots input, root и counts, counters0, flags;
**одним выбранным probe** заполнить ContextU64Ten и StrictU64::set_probe(probe).
Вычислить/проверить `initial_count10 = initial_prefix_count9 + (initial_tail==probe) as usize`.
Полный any input/probe независимы; никаких assumptions о hit/диапазоне/high bits/порядке.

Два same-signature raw adapters с исходными T/F и return(), closed impls только u64/U64Cmp, без blanket/fallback.
Фактические pointers/indices/received `*is_less` передавать unchanged, canonical внутри не подставлять.

1. raw swap_if_less → swap_adapter_u64ten → **existing swap_u64_net9**.
   Assert actual base==root, a/b distinct<9, canonical received cmp, full allocated/aligned/initialized/readable/
   writable backing10, StrictU64::probe()==ctx.probe, insert_hits==0.
   Затем marker assert !fail_swap: `u64tencall actual swap adapter binding control`.
   После verified summary вне pair-only target writes увеличить swap_hits; проверить prefix9 count invariant
   и actual tail9==initial_tail. Читать через checked actual base; не cached-pointer ownership bridge.
   Full sorted/count bridge не пересчитывать после каждого swap.
2. raw insert_tail → insert_adapter_u64ten → **existing insert_tail_profile<StrictU64>**.
   Assert actual begin==root, tail==begin.wrapping_add(9), canonical received cmp, swap_hits25/insert_hits0,
   same-allocation initialized writable backing10 и profile probe frame.
   **Assert**, не assume, model_sorted<StrictU64>(begin,9): реальная сеть должна установить prefix premise.
   Проверить prefix9 count, actual tail frame и whole model_count10==initial_count10 с тем же probe.
   Затем marker assert !fail_insert: `u64tencall actual insert adapter binding control`.
   Summary получает actual begin/tail/cmp; его memory/order/canonical requires должны проверяться.
   После return увеличить insert_hits вне target write-set; assert whole sorted10/count10 и probe frame.
   После insertion prefix9 count и actual tail9 вправе измениться: их старые frame-условия сюда не переносить.

Context snapshots/probe/flags не изменяются summaries; ghost counters пишет только adapter instrumentation.
Consumer — plain proof, не outer PFC с чужими ghost writes. После actual entry проверить hits25/1,
root/probe/all initial counts/initial_tail/flags frame, canonical outer cmp unchanged, sorted10 и full-u64 count
против pre-state. Использовать один typed full-u64 count predicate/checker для positive и count-negative.
Payload/probe не сужать до u8/u32 и не маскировать; snapshots сохраняются до мутации.
К review приложить actual25 swap edges +1 insert call/source positions. Никаких assumed sorted/count invariants,
panic cuts, копии network implementation или нового trusted summary.

## Ровно четыре roots и reachability controls

У всех4 roots: `stub(raw swap_if_less, swap_adapter_u64ten)`, `stub_verified(swap_u64_net9)`,
`stub(raw insert_tail, insert_adapter_u64ten)`, `stub_verified(insert_tail_profile)`, unwind25/unwinding assertions.
Annotation table показывает оба typed instances и independent no-stub leaves отдельно.
Не stub trait entry/insertion_sort_shift_left/final checker; no recursion/self-proof.

**Все kani::cover только в roots. В register/run/check/adapters/targets covers нет.**
Binding-negative имеет cover до actual entry и failing guard; после guard не требовать return/later-phase covers.

1. `u64tencall_positive_u64_n10`: any [u64;10], pre snapshot, independent any u64 probe,
   canonical U64Cmp, flags false. Actual entry/все phase checks/final posts.
   Required covers9 после return: returned; pre has descending adjacent pair; probe hits whole pre10;
   probe misses whole pre10; pre has duplicates; probe==pre[9] и misses pre prefix9;
   swap_hits25&&insert_hits1; pre[9] меньше всех pre[0..9]; probe>=(1u64<<40) и hits whole pre10.
   Cover predicates не являются assumptions. Это consumer-model reachability, не замена independent leaf evidence.
2. `u64tencall_swap_binding_negative_u64_n10`: [0u64;10], probe0, flags true/false;
   register, один root cover `u64tencall swap control: actual entry reached` до actual entry.
   Expected FAILED **только** swap binding literal выше; required covers1/1. Никаких post-return обязательств.
3. `u64tencall_insert_binding_negative_u64_n10`: [0u64;10], probe0, flags false/true;
   один root cover `u64tencall insert control: actual entry reached` до actual entry.
   25 swaps/geometry/probe/prefix/count premises должны пройти до insert marker.
   Expected FAILED **только** insert binding literal; required covers1/1, без post-guard covers.
4. `u64tencall_count_negative_u64_n10`: P=1u64<<40, Q=1u64<<41; input=[P;10], probe=P, flags false.
   Сначала весь canonical composed path, оба hits/frames/final posts проходят; root cover returned-before-corruption.
   Затем v[9]=Q: sorted10 сохраняется, count(P)10→9, младшие32 бита не меняются.
   Проверить sorted10, root cover достижения count-check **до** последнего assertion; тот же full-u64 count
   predicate обязан дать единственный failure `u64tencall negative: full-value count preserved`.
   Required covers2/2. Узкий witness допустим здесь, не у positive.

Unexpected canonical/geometry/probe/prefix/hits/frame/UB/unwinding/unsupported failures не являются intended negatives.
Ожидаемый failed assertion может отсечь последующие checks; не требовать all later checks reached.
Gate сравнивает точные literals/locations, не просто ненулевой Kani exit.

## G1/G2, compile-error повторы и budget

Общий профиль обоих пакетов: **measurement**, controls:true, kani_jobs:1, uninit_checks:false,
harness_timeout_minutes:10 /600s per row, runner **gcb-e2-standard-4** → **k1-standard4**,
4CPU/16GiB/swap off; прежние Kani/nightly/tooling/checks/unwind25. Все4 roots подготовить/review до G1;
планировать G1/G2 на одном frozen library tree, менять между пакетами только research/request metadata.

| Пакет | Exact rows | Резерв | Допустимый compile-error повтор |
|---|---|---:|---|
| G1 | только `u64tencall_positive_u64_n10` | `(10+30)×$0.0135=$0.540` | G1R, тот же1-row вопрос, $0.540 |
| G2 | swap-binding, insert-binding, count-negative из раздела выше | `(3×10+30)×$0.0135=$0.810` | G2R, те же3 rows, $0.810 |

G2 — **плановый control Build, не retry G1**. Порядок G1 → при compile error исправление/G1R → G2 →
при compile error исправление/G2R. G2 запускать после terminal/accounted G1 либо G1R независимо от proof-исхода:
SUCCESS, OOM, TIMEOUT, unexpected failure или incomplete coverage. При OOM/TIMEOUT positive остаётся OPEN,
для positive больше Builds нет, но стадия продолжается controls. Никаких предположений о порядке roots внутри G2.
Если G1 compile error, сначала исправить его статически и использовать единственный G1R с новым review/GO.
Если compile blocker сохраняется после G1R, не отправлять заведомо некомпилирующийся G2: HANDOFF,
G2 NOT_RUN/blocker, общий PASS запрещён. UNKNOWN submit/незавершённый учёт сначала разрешить через coordinator;
не занимать второй слот того же owner.

G1R/G2R допустимы только после соответствующего **compile error**, с исправленным кандидатом, новым review/GO
и сохранёнными mechanism/domain/rows/runner/flags. По одному такому повтору на пакет; не повторять неизменённый
compile-failing input. Resource/semantic/coverage failure не разрешает дополнительные попытки этого пакета.
G1R OOM/TIMEOUT → controls G2; G2R OOM/TIMEOUT → итог PARTIAL, новых Builds нет.
Не запускать positive снова ради результата controls или изменения его source после полученного proof.

При compile repair G1 зафиксировать новый общий кандидат для G1R и G2. Если repair G2 меняет library,
отдельно доказать source-dependency equivalence уже проверенного G1: root/его reachable helpers/adapters/
contexts/targets/contracts/runtime и flags должны быть неизменны. Изменение их семантики оставляет
positive нового кандидата UNVERIFIED и общий результат PARTIAL/FAIL; автоматического повторного G1 нет.
Сохранить обе source/library identities и reuse record, не выдавать результаты разных semantics за общий PASS.
Matching historical leaves также требуют неизменности своих targets/dependencies.

Два плановых резерва **$1.350**, все четыре с compile repairs **$2.700 ≤ cap $2.80**.
Каждый следующий submit: own fact_spent + полный reserve пакета ≤$2.80, актуальные global ledger/slots/deadline
позволяют. Будущие G2/repair envelopes учитывать в плане, а не тратить весь cap на G1.
С PARTTWO-TREE плановым reserve$0.675 суммарный план $2.025, но его actual reserved может уже отличаться.
После NETTEN used≈$79.74 и leaf own$0.1485 расход вырос минимум на leaf сумму; перед каждым GO читать current ledger,
не фиксировать оценку как разрешение на dispatch и не включать старые UUIDs в own spent.
Project≤2 queued/running/unresolved Builds, ≤1 на stable owner. Окно не продлевать автоматически:
полный envelope каждого Build должен помещаться в действующие deadlines с closeout reserve.
Если полномочий/остатка окна/бюджета не хватает, соответствующий пакет NOT_RUN с точной причиной, без PASS.

Gate общей стадии: identities/domain/reuse matches; G1 или G1R positive SUCCESS/0 unintended failures/9 из9 covers;
G2 или G2R все3 controls FAILED только designated literals с covers1/1,1/1,2/2;
два matching historical leaves applicable и source/runtime restrictions сохранены. Показывать gates пакетов отдельно:
positive SUCCESS не заменяет controls, intended control failures не устанавливают whole-route theorem.
OOM/TIMEOUT/NOT_RUN/UNKNOWN positive → общий PARTIAL при отсутствии отдельного обнаруженного дефекта,
даже если все controls сработали. Unexpected assertion/UB/binding failure → FAIL, не intended-negative PASS.
Cloud SUCCESS/exit1 сами по себе не заменяют gate. Никаких highmem/tooling/timeout/RAM изменений,
сужения input/probe, нового разбиения пакетов или автоматического N11/N14/32.

PRE-BUILD: semantic diff/dependencies, frozen standard4 measurement request/pool-price binding;
source/library/tree/request/Kani/nightly/tooling hashes; old-leaf reuse map и G1↔G2 source identity record, root/annotation table,
actual call-map; typed geometry/init/write-set/probe record, phase/context/counter/frame audit;
control literals и per-root cover inventory/reachability; source ordinary200/cfg405 set delta,
pfc_order/target ordering, static rustfmt/whitespace, own/global budgets/slots/deadline.
Library/research commits отдельно `[skip ci]`, publish reviewed candidate без force.
No local cargo/rustc/Kani/proof, Actions dispatch/deploy. Tooling не менять; highmem — вне этой стадии.

## Итог

`RESULT-U64-TEN-CALLER.md` ≤40 строк: reviewed/build/request/library/tree/tooling identities,
actual typed route/raw binding/shared probe/prefix premise, rows/status/VT/CBMC RSS/checks/unreachable/covers/gate,
compiler/driver/process-sum RSS **по каждому Build отдельно**, own spent/reserved и machine/pool.
Отдельно перечислить G1/G1R/G2/G2R, terminal причины и неприменённые repairs; полный общий бюджет по своим UUIDs.
TIMEOUT cap600 не завершённый VT; VT не напечатан → UNKNOWN, OOM отдельно. При отсутствующих данных — NOT_RUN/UNKNOWN,
без PASS предположений. Не складывать peaks разных Builds; теперь positive driver peak измеряется в отдельном процессе.
Если приводится VT(B64_10)+100.61334+79.74734 — **mixed-run estimate**, не same-build measurement;
без matching direct A64_10 нет speedup, u8 timings не прогноз u64. Успех — opt-in bounded actual u64/U64Cmp/
default-< N10 theorem на backing10/offset0 с independent full-u64 probe и двумя matching leaves.
Не расширять на function-item F, generic T/FnMut/N/backings/offsets, stability, uninit detection/full
alias-validity/Rust unwind/trait-PFC или ordinary v6/202. U64-N13 остаётся PARTIAL.
Evidence только bounded K-1 summaries/rows/peaks/разрешённые targeted excerpts; raw archives/full logs/
Cloud Logging/credentials/hidden configs не читать/скачивать. Исторические results/ledgers не переписывать;
код конкурентов не открывать. Маркеры `REVIEW REQUEST <sha>` / `U64-TEN-CALLER ЗАВЕРШЁН`; одна стадия, затем стоп.
