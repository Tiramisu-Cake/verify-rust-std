# U64-N13 — exact-N13 typed leaf и actual network composition

Runtime: **Claude Code**, tmux4, исполнитель сам, **без субагентов**. Worktree
`/root/verify-rust-std-kani-usixtyfourthirteen`, ветка `experiment/kani-k1-usixtyfourthirteen-20261102`
(slug [a-z]+, alias не нужен). База U64-N9 `9ab925b1578b9102e3009c0ec940c5c9cc0280cb`, library commit
`fddf308321046a8cd8f5526622a5e2353d79830e`, tree `d22566ab5a685df2608ddb756714e51ad288f08d`.
Stable owner **k1-merge**: U64-N9 terminal; новую стадию учитывать отдельно по своим UUID/request_id `u64thirteen-*`.
Cap проекта$88.96, used при постановке≈$78.42; cap этой стадии$2.00. Один плановый GCB Build,
максимум2 только по compile-error ветке ниже. PRE-BUILD REVIEW + exact-packet GO координатора обязательны.
Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` в фоновом Bash task Claude Code, без
Codex watch/CODEX_THREAD_ID, polling-субагентов и новых сессий. Evidence Brief/Select-Merge к K-1 не относятся.
Clean room: код/ветки/diff конкурентов не открывать.

## Вопрос и scope

Доказать машинной композицией sortedness/full-value permutation настоящего Unstable u64 N13 в600s/row,
через matching real swap leaf и actual raw-call→adapter→verified summary, по образцу U64-N9/NETCOMP2.

T=u64; **F=U64Cmp=fn(&u64,&u64)->bool**, value существующего StrictU64::CMP=reified strict_less::<u64>.
Все64 бита input/probe unconstrained, default `<`, initialized exact backing13, active offset0.
u64 Copy+Freeze/size8/efficient swap → network, не general. N13: sort13_optimal, **45** raw exchanges,
insertion_sort_shift_left offset13 без вставок, no merge. Ни sort9/25 hits, ни N18 halves здесь не применять.
N9 PFC и u8 N13 не являются matching leaf этого T/N. Function-item F/ arbitrary FnMut не заявляются.

Read: RESULT-U64-N9/TASK-U64-N9, u64nine.rs целиком; RESULT-NETCOMP2 и N13-код netcomp.rs как пример;
StrictU64/strict_less/count helpers в network.rs; actual dispatch/sort13/swap/insertion в smallsort.rs;
TASK-SPECFIX (запреты/format/expect_check/evidence), pfc_order.py. Старые source/results не переписывать.

## Разделение файлов и параллельность

Новый opt-in child **network::u64nine::uthirteen**, файл `verify/network/u64nine/uthirteen.rs`.
В u64nine.rs только регистрация child после existing targets/roots. Из parent можно импортировать прежние
private U64Cmp/canonical/StrictU64 и pure helpers без изменения visibility.
Свои target13/count13/context13/bridge13/adapter13/roots; **не менять и не обобщать** существующие N9 функции,
contract attributes, ContextU64Nine, counters, tests или controls. U64Cmp/canonical pure code можно читать/использовать;
нельзя вызывать count9/run9/adapter9 как замену N13 proof.

MERGESTEP owner k1-network параллельно редактирует netcomp-поддерево/merge; его worktree/файлы не трогать.
Не интегрировать NET18/MERGESTEP/MACSPLIT/v6/DOMSIX; runtime smallsort.rs/tooling/flags/pin/workflows неизменны.
Ordinary exact200 этой ветки без изменений;4 новых roots дают cfg-on399→403 статически, не новый native proof inventory.
Объединение веток/RUN-REQUEST/research records позже отдельно; shared live state для двух worktrees не создавать.

## Target и independent leaf — строка1

Конкретный `swap_u64_net13(v:*mut u64,a:usize,b:usize,cmp:U64Cmp,probe:u64)` до его PFC.
Requires: canonical **received** cmp, nonnull/aligned readable initialized/writable full span13,
a,b<13 и distinct, same-allocation/swap geometry. Modifies только actual v[a]/v[b].
Ensures pure StrictU64 pair transfer по pre-values, ordered post-pair и
`old(count13_u64(v,probe)) == count13_u64(v,probe)`. Old — scalar count/full pair values, не pointer snapshot.
Без callbacks в specs, global context/probe reads и ghost writes внутри target.
Body реально вызывает raw swap_if_less с local actual:U64Cmp=received cmp; no stubs.

`u64thirteen_leaf_u64_n13`: proof_for_contract нового target, unwind25, без manual/verified stubs.
Полный any [u64;13], независимый any u64 probe, произвольные distinct a/b<13, canonical U64Cmp.
После call explicit pair transfer/order, full-u64 count и frame всех11 остальных элементов.
7 достижимых covers: swap/no-swap, first→last(0,12), last→first(12,0), interior pair, probe hit/miss.
Не копировать literal9/8/7 из предыдущего fixture; не заменять backing13 exact9 или prefix в более крупной allocation.

## Composed root и actual binding — строка2

ContextU64Thirteen: base:*mut u64, probe:u64, initial_count:usize, hits:usize. Dedicated static, свой register/read;
все init присваивания до library call; не использовать/менять CONTEXT_U64_NINE.
Raw adapter сохраняет actual raw swap parameters/return/two generic T,F; closed impl только u64/U64Cmp,
без blanket/fallback. Guard actual base==registered root, a/b distinct/in13, canonical received *is_less;
literal `u64thirteen canonical comparator required`, при rejected guard вернуть без summary call.
Передать actual pointers/indices/comparator value/probe в swap_u64_net13, canonical value не подставлять.
В adapter вне target увеличивать hits и assert count13(actual base,ctx.probe)==initial_count.
Target pair-only write-set не включает counter/context. После entry assert hits45, base/probe/initial-count frame,
canonical cmp unchanged. Общие check/run helpers содержат assertions, не positive covers.

`u64thirteen_composed_u64_n13`: plain proof, `stub(raw swap_if_less, adapter_u64thirteen)` плюс
`stub_verified(swap_u64_net13)`, unwind25. Реальный `<u64 as UnstableSmallSortTypeImpl>::small_sort`.
Полный any [u64;13], snapshot до call, independent any u64 probe, explicit canonical U64Cmp.
Final sortedness и typed full-u64 count; остальные std bodies не заменять, никаких assumptions об output.
7 required covers: adapter entered, complete45 hits **в positive root после return**, sort moves,
probe hits input, probe misses input, duplicates, probe>255 и probe hits input.
Все достижимы в этом fixture; не переносить covers в shared context checker/contract clauses.
Сверить реальные45 call edges с source и приложить annotations/call map в PRE-BUILD.

## Два negative — строки3/4

Все roots той же typed summary/actual-entry области; expected check literals уникальны новому модулю.

- `u64thirteen_wrong_cmp_u64_n13`: same adapter/stub_verified, valid any [u64;13]/probe, register собственного
  context; received `cmp:U64Cmp=always_true_u64`. Cover actual entry и adapter. Не проверять sorted/count/hits45
  результата в этом root: только guard должен FAILED (`u64thirteen canonical comparator required`), возможны
  повторения одного guard при45 calls. Прямой вызов contract target вместо actual network не считается binding.
- `u64thirteen_count_negative_u64_n13`: canonical composed path на `[P;13]`, `P=1u64<<40`, probe=P.
  Сначала все invariants/hits45/frames обязаны пройти. После return `v[12]=1u64<<41`: ordinary порядок сохраняется,
  count(P)13→12, low32 bits одинаковы. Это проверка полного u64 oracle, не byte/truncated-word count.
  Assert sortedness после corruption и достигнутый count-check; expected FAILED только
  `u64thirteen N13 negative: full-value count preserved` того же typed oracle. Covers adapter + return-before-
  corruption + count-check reached =3. Narrow witness только negative; positive input/probe не ограничивать.

Запрещены cast/truncation к u8/u32, выбор probe из input, предварительная сортировка/ограничение диапазона values,
удаление asserts/frame/covers ради времени. Wrong-cmp —2/2 witness covers; count-negative —3/3.
UB/unwinding/geometry/hits/frame/unsupported/setup/ERROR/TIMEOUT/OOM не intended negative.

## G1 / бюджет / stop

Один joint packet4 exact names: leaf13, composed B13, wrong-cmp13, count-negative13.
measurement/controls:true/jobs1/uninit off/unwind25 с unwinding assertions/600s per row,
k1-standard4/16GiB/swap off, прежние pin9461e07af7/nightly-2026-10-12 и tooling/organizer flags.
Резерв `(4×10+30)×$0.0135=$0.945`; planned MERGESTEP G1$1.215 вместе дают$2.160 резервов,
но own stage costs/UUIDs/ledgers не смешивать. Project≤2 queued/running/unresolved Builds,≤1 на stable owner;
проверить актуальные global used/reserved и оба slot states через существующий coordinator перед GO.

Gate: source/request/pin/tooling identities match; real leaf13 и B13 SUCCESS с0 unintended failures и7/7 covers
каждый; оба controls FAILED только named literals с полными witness covers; all runtime/source/ordinary bounds соблюдены.
Consumer не получает composition credit без matching independent leaf, даже если его строка SUCCESS.
Цена u8 B13≈269s и u64 B9≈148s не даёт линейного прогноза u64 N13. Следить отдельно за CBMC, driver/compiler,
process-sum RSS; прежний u8 driver достигал≈8GiB. Не менять machine/timeout/flags при нехватке ресурса.

Любой positive TIMEOUT/OOM/FAILED/coverage/UNKNOWN → сохранить per-row facts, stage PARTIAL/FAIL и **стоп**.
Если B13 TIMEOUT600, negative counts/leaf PASS не превращают это в positive theorem. Не сужать input/probe,
не понижать width, не разбивать probe-domain без новой постановки, не переходить автоматически к N18/32.
G2 только после compile error G1: тот же вопрос/mechanism/domains/4rows/flags, новый PRE-BUILD review/GO,
полный reserve$0.945, own fact_spent+reserve≤$2.00 и актуальный global ledger/slots. Два резерва$1.890≤$2.00.
После resource/semantic/coverage failure повтор не разрешён. G3 нет. N9 rows не повторять без изменений.

PRE-BUILD: diff, T/F/CMP/probe/N/backing/offset/init/frame record, actual raw→adapter→summary→leaf table;
45-edge source map, context/ghost-write audit, полный список annotations, exact expect_check/required covers;
request/library/source/pin/tooling hashes, ordinary200/cfg403 статически, target ordering/pfc_order отдельно,
rustfmt/whitespace, own/global reserves/slots. Library/research commits отдельно, [skip ci], push без force.
Компиляция/proof только в authorized GCB; local cargo/rustc/Kani/Actions dispatch/deployment не выполнять.
Evidence — bounded K-1 summaries/rows/peaks и разрешённые targeted excerpts; raw archives/full logs/Cloud Logging,
credentials/hidden configs не читать/скачивать, historical evidence/ledger не менять.

## Итог

`RESULT-U64-N13.md` ≤35 строк: reviewed/build/library/request identities; actual typed domain и binding;
rows/status/VT/CBMC RSS/failed-total/unreachable/covers, gate, own spent/reserved; source/runtime/ordinary identity.
Compiler/driver/process-sum peaks отдельно; TIMEOUT cap600, VT=UNKNOWN если не напечатан; OOM отдельно.
B13+leaf13 VT — цена этого доказательства; matching direct A64-N13 отсутствует, поэтому speedup не установлен.
Сравнения с u64 N9/u8 N13 — разные domains/runs, не доказанный коэффициент масштабирования.
PASS = real-route machine composition exact u64/U64Cmp/default-< N13/backing13 offset0 с independent full-u64 probe,
matching leaf pair/frame/count invariant и intended controls; opt-in research.
Не доказаны function-item F, arbitrary T/FnMut/other backings/offsets/N18/N32, stability ties,
uninit detection/full alias-validity/unwind или trait PFC. N9 и ordinary200 этой ветки/Part1-v6 202 не расширять молча.
Маркеры `REVIEW REQUEST <sha>` / `U64-N13 ЗАВЕРШЁН`; одна стадия — после результата стоп.
