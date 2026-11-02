# NETTEN-CALLER — actual Unstable u8 N10 через swap и insertion summaries

Runtime: **Claude Code**, исполнитель сам, **без субагентов**. Worktree
`/root/verify-rust-std-kani-nettencall`, ветка `experiment/kani-k1-nettencall-20261102`, база
`9835bd00dc4bf386e68e5f7885964a17d0dda240` (NETTEN-LEAVES); library commit
`23ba8cfddbce1cf0313ab402fd6376d157a0f845`, tree `74e42aaa191879280e8e7827c1e32a4ac65d5f18`.
Stable owner **k1-merge**: NETTEN-LEAVES terminal. Новый stage/UUIDs/request_id `nettencall-*`.
Cap проекта$88.96 (used при постановке≈$79.30, DIRECTFOUR G2 reserve$0.540 отдельно);
cap стадии **$2.00**, один плановый Build, максимум2 только по compile-error ветке ниже.
PRE-BUILD REVIEW + exact-packet GO координатора обязательны. `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD`
в фоновом Bash task Claude Code; не Codex watch/CODEX_THREAD_ID, polling-субагенты или новые сессии.
Evidence Brief/Select-Merge к K-1 не относятся. Clean room: код/ветки/diff конкурентов не открывать.

## Вопрос, маршрут и принятые листья

Получить full sortedness/count actual `<u8 as UnstableSmallSortTypeImpl>::small_sort` N10 через independently
checked leaves на фактической геометрии, с проверенной raw-call→summary связью обоих helpers.
T=u8; F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP=reified strict_less::<u8>; ordinary `<`, full u8 model.
Exact initialized backing10, offset0, independent any u8 probe; не function-item F и не arbitrary FnMut.

Actual route: Freeze+Copy/efficient swap → small_sort_network, sort9 на prefix9 (25 raw swap_if_less),
insertion_sort_shift_left offset9 выполняет **один raw insert_tail(begin0,tail9)**, затем no_merge return.
Не менять/заменять сеть или insertion_sort_shift_left; sort13/merge/general здесь отсутствуют.

NETTEN-LEAVES build `f6fdbf06-58fa-4c1d-9692-c8236cc38892`, reviewed source
`1914e42274cb2a7e574a0d6497c4a9922983a9cf`: matching swap_net9 prefix9/backing10 (8/8,77.10969s)
и insert_tail_profile<StrictU8> begin0/tail9/full backing10 (8/8,59.589855s), оба no-stub PFC SUCCESS.
Их body/contracts/fixtures/annotations и все зависимости сохранить; они остаются evidence старого Build,
не новыми строками NETTEN-CALLER. PRE-BUILD reuse record связывает targets/T/F/CMP/model/probe/backing/init/frame.

Read RESULT-NETTEN-LEAVES/TASK-NETTEN-LEAVES, netten.rs и swap_net9/netcomp.rs; specfix.rs insert_tail_profile,
tail_region/tail_len/model_sorted/model_count; real sort9/network/insertion/insert_tail; TASK-NETCOMP2 как bridge
pattern; TASK-SPECFIX (запреты/format/evidence/expect_check) и pfc_order.py. Урок MERGESTEP: failing kani::assert
отсекает путь; никаких требований covers после failing guard.

## Файлы, source integrity, размещение

Новый opt-in child **network::netcomp::netten::caller**, файл `verify/network/netcomp/netten/caller.rs`.
В netten.rs только его регистрация после existing items. Private parent sorted10/pure helpers и private ancestor
swap_net9/U8Cmp/canonical доступны descendants без widening visibility.
DIRECTFOUR параллельно меняет mergestep/directfour и другой parent; его файлы/worktree/request не трогать.
Не интегрировать NET18/MERGESTEP/U64/v6/DOMSIX, не обобщать общий framework и не редактировать старые leaf targets.
Runtime smallsort.rs/flags/pin/tooling/workflows/runner неизменны; ordinary exact200.
Ровно4 новых plain roots → cfg-on397→401 статически; это не native proof inventory или ordinary credit.

## Один probe и phase-aware context

Своя static ContextTen: root:*mut u8, probe:u8, initial_prefix_count9:usize, initial_count10:usize,
initial_tail:u8, swap_hits:usize, insert_hits:usize, fail_swap:bool, fail_insert:bool.
Setter вне любых contracted targets: сохранить root/backing10 и scalar snapshots, counters0 и flags;
**одним выбранным probe** заполнить ContextTen.probe и StrictU8::set_probe(probe) до actual entry.
Positive probe и весь input — independent any, без requires/assume связывающих probe с input.
Не копировать Context9 и не делать initial_prefix_count9 равным whole-count10. По определению
initial_count10 = initial_prefix_count9 + (initial_tail==probe) as usize; это вычисление/check, не assume.

## Actual raw hooks и invariant

Два same-signature adapters с исходными generic T/F и return(), closed trait impls только u8/U8Cmp,
без blanket/fallback. Фактические аргументы и `*is_less` передавать unchanged в summaries, canonical не подставлять.

1. Raw swap_if_less → свой swap_adapter10 → **прежний swap_net9**.
   Guard actual base==ctx.root, actual distinct a,b<9, canonical received cmp, valid initialized backing10.
   Проверить readonly StrictU8::probe()==ctx.probe; swaps происходят только до insertion (insert_hits==0).
   Перед summary отдельный marker assert !fail_swap с literal
   `nettencall actual swap adapter binding control`. Positive flag=false; markers не заменяют geometry/canonical checks.
   После verified target вне его pair-only write-set увеличить swap_hits; assert prefix9 count равен initial_prefix_count9
   и actual tail9==initial_tail. Читать через проверенный actual base, не произвольную cached pointer/provenance bridge.
   Не пересчитывать full10/prefix-sorted после каждого swap: phase bridge проверяется один раз ниже.
2. Raw insert_tail → свой insert_adapter10 → **existing insert_tail_profile<StrictU8>**.
   Guard begin==ctx.root, tail==begin.wrapping_add(9), received cmp canonical, swap_hits==25/insert_hits==0,
   same allocated initialized writable region10; StrictU8::probe()==ctx.probe.
   Перед summary assert pure model_sorted<StrictU8>(begin,9): **реальная сеть должна это доказать**, не assume.
   Проверить prefix count/tail frame и count10==initial_count10; model_count<StrictU8> использует тот же probe.
   Затем marker assert !fail_insert с literal `nettencall actual insert adapter binding control`.
   Вызвать profile на actual begin/tail/received cmp. Его verified replacement обязан проверить memory/order/canonical
   premises и сохранить full model-count; --no-assert-contracts не превращает обычные calls в доказанные summaries.
   После возврата увеличить insert_hits вне contracted target; assert sorted10 и count10==initial_count10,
   probe/context frame. **Tail и count prefix9 теперь вправе меняться**: после insertion не assert actual v[9]==initial_tail
   или actual prefix9 count==initial_prefix_count9. Неизменны snapshot-поля context, а не прежняя раскладка данных.

Context/StrictU8 probe не должны изменяться target summaries; ghost counters пишет только adapter instrumentation
вне contract targets. Consumer — plain proof, не outer PFC с чужими ghost writes в modifies.
После actual entry: swap_hits25/insert_hits1, root/probe/initial-count/prefix-count/initial-tail/flag fields frame,
canonical outer cmp unchanged; final sorted10 и full typed count против pre-state snapshot.
Перечень25 swap edges + единственный actual insert_tail call/source positions приложить к review.
Никаких user assumes о sorted prefix/output/count, panic cuts, network copies или новых profiles на raw generic std.

## Четыре exact roots

У всех composed roots annotations: `stub(raw swap_if_less, swap_adapter10)`, `stub_verified(swap_net9)`,
`stub(raw insert_tail, insert_adapter10)`, `stub_verified(insert_tail_profile)`; unwind25 с unwinding assertions.
Не stub insertion_sort_shift_left, trait entry или final checker. Independent leaves имеют другие roots без stubs,
сохранённые как old evidence. В root/annotation table показать оба typed instances и отсутствие recursion/self-proof.

**Общее правило covers:** в adapters/check/register/run helpers **нет kani::cover вообще**. Иначе failing swap guard
оставит более поздний insert-enter cover unreachable (ошибка MERGESTEP). Actual binding фиксируется intended
failed marker внутри соответствующего adapter; positive дополнительно проверяет оба точных hit-counts.

1. `nettencall_positive_u8_n10`: any [u8;10], pre snapshot, independent any probe, canonical U8Cmp, flags false.
   Настоящий Unstable entry, оба phase invariants, final posts. Required covers8 — только в positive root после return:
   returned; input имеет descending adjacent pair; probe hits pre10; probe misses pre10;
   pre10 содержит duplicate value; probe==pre[9] и probe misses original prefix9;
   swap_hits==25 && insert_hits==1; pre[9] меньше всех original pre[0..9] (tail-min input returned).
   Cover predicates про исходный input/probe, без новых premises. Это consumer-model reachability;
   real leaves отдельно подтверждают реализацию summaries/допустимые domains.
2. `nettencall_swap_binding_negative_u8_n10`: canonical input=[0;10], probe0, fail_swap=true/fail_insert=false;
   register, **один** cover `nettencall swap control: actual entry reached` ДО actual entry.
   Вызвать настоящий entry; нет post-return covers/обязательств, нет shared positive-cover helper.
   Expected FAILED только swap marker; failure доходит до реального raw swap adapter. Required covers1/1.
3. `nettencall_insert_binding_negative_u8_n10`: input=[0;10], probe0, flags false/true; один root-entry cover до call.
   Canonical swap phase проходит; failure на insert marker после корректных geometry/prefix/count premises.
   Expected FAILED только insert marker. Required covers1/1; не ожидать merge/entry return после failing assert.
4. `nettencall_count_negative_u8_n10`: canonical composed path [0;10]/probe0, оба flags=false;
   все phases/hits/frames/final posts сначала проходят. Cover returned-before-corruption, затем v[9]=1;
   assert sorted10 и cover count-check reached ПЕРЕД последним assertion.
   Count0 10→9; expected FAILED только `nettencall negative: full-value count preserved` у того же typed checker.
   Required covers2/2. Узкие нулевые witnesses только controls, не positive input/probe.

Если unexpected canonical/geometry/probe/prefix-sorted/hit/frame/UB/unwinding/unsupported failure — это FAIL stage,
не intended negative. Expected failed assertions могут иметь unreachable последующие checks; это не post-guard
witness. Не требовать all later checks reached и не переоформлять исторические control counts.

## G1, budget, stop

Один совместный packet4 exact names: positive, swap-binding, insert-binding, count-negative.
measurement/controls:true/jobs1/uninit off/600s per row/k1-standard4/16GiB/swap off/unwind25,
тот же pin9461e07af7/nightly-2026-10-12/tooling/organizer flags. Резерв `(4×10+30)×$0.0135=$0.945`.
С DIRECTFOUR G2 reserve$0.540 —$1.485 active/planned резервов при двух разных owners; проверить текущие цифры/slots
через coordinator, не фиксировать stale used как разрешение на dispatch. Project≤2 queued/running/unresolved,
≤1 на stable owner. NETTEN-LEAVES old spent не включать в собственные UUIDs новой стадии.

Gate: all identities/domain/reuse matches; positive SUCCESS с0 unintended failed checks и8/8 covers;
три controls FAILED только designated literals с1/1,1/1,2/2 covers; оба historical matching leaves и source integrity
сохранены. Caller без matching leaf credit не принимается; источники old/new builds разделены.
TIMEOUT/OOM/FAILED/coverage/UNKNOWN → сохранить per-row facts, PARTIAL/FAIL и стоп, без input/probe narrowing,
удаления prefix/count/frame checks, увеличения машины/timeout и автоматического N11/N14/N18/32.
G2 только compile error G1, тот же mechanism/domains/4rows/flags, новый review/GO и полный reserve$0.945;
own fact_spent+reserve≤$2.00 и global ledger/slots. Два резерва$1.890≤$2.00; G3 нет.
Resource/semantic/coverage repeat не разрешён; legacy NETTEN-LEAVES/U64/MERGESTEP стадии не возобновляются.

PRE-BUILD: diff, annotation matrix, actual call-map, typed F/CMP/backing/offset/init/write-set/probe record;
reuse-dependencies record двух old leaves, prefix→whole-count algebra и single-probe setup/frame;
context phase/counter audit, control literals и per-root cover-source/reachability inventory;
source/library/request/pin/tooling hashes; target ordering/pfc_order плюс ordinary200/cfg401 статически;
rustfmt/whitespace, budgets/slots. Library/research commits отдельно, [skip ci], push без force.
No local cargo/rustc/Kani/proof/Actions/deployment. Evidence только bounded K-1 summaries/rows/peaks/targeted excerpts;
raw archives/full logs/Cloud Logging/credentials/hidden configs не читать/скачивать. Историю/ledger не переписывать.

## Итог

RESULT-NETTEN-CALLER.md ≤40 строк: reviewed/build/library/request identities, actual typed domain/raw binding/
shared probe/prefix premise, rows/status/VT/CBMC RSS/checks/unreachable/covers/gate; own spent/reserved.
Compiler/driver/process-sum RSS отдельно, TIMEOUT cap600/VT UNKNOWN если не напечатан; OOM отдельно.
VT(B10_new)+77.10969+59.589855 — если приводится, только **mixed-run estimate** с двумя old leaves,
не same-build measurement. Без direct matching A10 нет speedup. Успех других widths/N не временной прогноз.
PASS = actual u8/U8Cmp/default-< N10 composition на exact backing10/offset0 с unrestricted input/independent probe,
обоими matching leaves и проверенными premises/frames/binding; opt-in research.
Не обобщать на function-item F, arbitrary T/FnMut/N11/N14/N18/32/backings, stability, uninit detection/full
alias-validity/unwind или trait-PFC. Ordinary200/green Part1-v6 202 не расширяются; U64-N13 remains PARTIAL.
Маркеры REVIEW REQUEST <sha> / NETTEN-CALLER ЗАВЕРШЁН; одна стадия — после результата стоп.
