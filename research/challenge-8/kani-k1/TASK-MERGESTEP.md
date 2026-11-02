# MERGESTEP — real merge_up/down summaries и малая машинная калибровка

Runtime: Claude Code, без субагентов. Worktree `/root/verify-rust-std-kani-mergestep`, ветка `experiment/kani-k1-mergestep-20261102` (alias не нужен); base NET18-LEAVES
`7d8b21728b1ccb632d67374918bd13d2c45de116`, library commit `4eb7e81259f843da6517a8de97c68e23b584eb76`,
tree `1fa41b3a5f101ee3981787f71588bfc22e2aae5b`. Slug ветки **только [a-z]+**, пример
`experiment/kani-k1-mergestep-20261102`. Не dispatch-ить ветку
с цифрами в slug и не менять k1g.sh regex. Если нужен alias — проверить exact SHA equality до GO.
Cap проекта$88.96, used при постановке≈$78.23; cap стадии$2.50, один плановый Build, максимум2 по compile-error
ветке. Отдельный stable owner/slot/ledger назначает координатор: U64-N9 уже использует свой активный owner.
request_id `mergestep-*`, exact-packet PRE-BUILD GO обязателен. Wait — `k1g.sh wait BUILD` в фоновом Bash task
Claude Code; не Codex watch/CODEX_THREAD_ID. Evidence Brief/Select-Merge к K-1 не относятся.
Clean room: код/ветки/diff конкурентов не открывать. Новые сессии запускает владелец, обходов лимитов нет.

## Вопрос и этап

Можно ли на pin9461e07af7 получить пригодные для композиции closed u8/U8Cmp summaries настоящих merge_up/down,
проверить raw→adapter→summary binding и actual merge N4 с их применением, не меняя runtime helpers/алгоритм?
Большой merge18 TIMEOUT не повторять. Этот stage не доказывает N18 и не запускает N18/N32 caller.

F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP=reified strict_less::<u8>; полный u8/default-<.
Source backing18 initialized, destination backing32 MaybeUninit, отдельные allocations. Калибровка использует
source prefix4 (half2+2), destination prefix4; физические backings остаются18/32. Source/произвольный probe
не сужать кроме законного sorted-half requires у самого merge PFC.

Прочитать RESULT-NET18-LEAVES, TASK-NET18-LEAVES; TASK-NETCOMP2/RESULT-NETCOMP2 как образец bridge/controls;
actual smallsort.rs merge_up/down/bidirectional_merge; specfix.rs merge_profile/geometry/models;
assembly::advancement_merge_up_u8_n2; TASK-SPECFIX (запреты/evidence/format/expect_check), pfc_order.py.
Имеющийся ordinary witness — plain proof, не готовая шаговая summary и не разрешение на перенос geometry/F.

## Файлы и неизменяемое

Новый opt-in child `network::netcomp::mergestep`, файл `verify/network/netcomp/mergestep.rs`;
в netcomp.rs только его регистрация после существующих targets. Старые N9/N13/NET18 targets/roots не менять.
Не трогать network.rs/U64-N9 worktree: u64 параллельно добавляет sibling network::u64nine.
Не обобщать общий framework, не менять visibility, runtime smallsort.rs/inline(always), profiles/flags/pin,
Kani/compiler/validator/tooling/workflows/runner. Ordinary200 unchanged; при ровно6 новых roots cfg-on398→404 статически.
Никакого нового generic order/frame обещания для arbitrary FnMut. Все ограничения — closed proof domain.

## Step contract: scalar decision плюс проверенное кодирование tuple

Новые concrete forwarders `up_step_u8` / `down_step_u8` принимают actual left/right/dst pointers и cmp:U8Cmp,
возвращают **bool take_left**, а не pointer tuple. Это выбранное encoding, не предположение, что Kani умеет
havoc tuple raw pointers. Bool replacement и actual helper interception тоже проверяются этой стадией.

Requires: canonical received cmp; оба source cells readable/initialized/aligned, в одной source allocation,
distinct; dst writable, в отдельной allocation от source. В checked fixtures source18 и destination32;
up dst-index0..31, down dst-index1..31. В down requires дополнительно writable predecessor
`dst.wrapping_sub(1)` той же destination allocation: raw down делает dst.sub(1), поэтому dst=allocation-start
в этот domain не входит. Не требовать initialized predecessor — фактический merge может его ещё не записать.
Modifies только original dst cell, не source/context/probe/другие destination cells.
Pure ensures: up take_left ⇔ old(left_value<=right_value); down take_left ⇔ old(right_value<left_value);
original dst после call содержит old выбранное ПОЛНОЕ значение. Pre-dst value не читать: оно может быть uninit.

Actual body каждого forwarder вызывает настоящий merge_up/down с local actual:U8Cmp=received cmp.
Decision можно вычислить из сохранённых pre-values, но обязательно проверить returned RAW tuple против decoder:
- up: L'=L.wrapping_add(take_left), R'=R.wrapping_add(!take_left), D'=D.wrapping_add(1);
- down: L'=L.wrapping_sub(take_left), R'=R.wrapping_sub(!take_left), D'=D.wrapping_sub(1).
Все bool→usize conversions явные. Использовать shared pure decoder и в leaf refinement assertions, и в adapters.
Leaf assertions сравнивают decoder **с фактическим результатом std helper**, не с копией его алгоритма.
Down ties take_right; up ties take_left. Source returned pointers могут стать one-past/one-before:
это допустимые opaque wrapping values, не читать через них и не требовать can_dereference для return.
Не заменять wrapping_sub на sub для source и не делать offset_from у pointer before-base.

## Независимые leaves — строки1/2

По одному proof_for_contract для up_step_u8/down_step_u8, **без любых stubs/stub_verified**.
Source `[u8;18]=any`, independent source indices i!=j<18, cmp explicit canonical U8Cmp. Destination:
отдельный MaybeUninit<[u8;32]>; up k:any0..31, down k:any1..31. Передать root+indices/root+k.
Чтобы охватить partially-written output будущего merge, arbitrary initialization mask32 и independent byte values32:
инициализировать только mask=true cells перед call, остальные оставить uninit. Не читать весь backing как [u8;32].
После call прочитать только written cell и ранее initialized mask-cells; frame остальных checked cells unchanged;
source18 неизменен целиком. Любые uninit tail/mask=false cells не читать/snapshot-ить как u8.
Probe:any u8 для explicit indicator output==probe vs selected pre-source==probe, без связи с source.
Target сам probe/global context не читает и не пишет. Preserved full value даёт основу учёта occurrence, не
«source physically consumed» и не whole-merge count conservation автоматически.
Covers вне targets: left/right selected, tie, probe hit/miss selected value, reachable source-edge и dst-edge;
точные достижимые labels/counts перечислить в PRE-BUILD, не собирать невозможные общие covers.
Unwind34 для initialization/frame loops≤32 и helper; unwinding assertions включены.

## Raw-call binding и actual composed merge4 — строка3

Same-signature generic adapters raw merge_up/down возвращают прежние typed pointer tuples. Closed trait impl
только u8/U8Cmp, без fallback. Adapter получает actual L/R/D/*is_less, проверяет canonical value и geometry,
вызывает свой verified scalar forwarder и возвращает decoder(actual args, take_left).
Не подменять cmp на canonical и не менять raw helpers или их inline(always). Поскольку helpers inline(always),
interception на этом pin — реальная гипотеза: missing binding/unsupported означает STOP, не removal атрибута/patch.

Readonly proof context регистрируется **до** outer merge target: source18 base, dst32 base, active_len4,
общий probe и два readonly negative-binding flags (up/down). Source indices/действительные d вычислять только после same-allocation/range
checks; для down returned reverse endpoints сначала wrapping_add(1), не offset_from(before-base).
**Никаких global hit counters/ghost writes в adapters:** outer PFC merge_profile имеет modifies только dst-prefix4;
посторонние context writes нарушат его assigns. Context/StrictU8 probe остаются readonly в actual target.
Два unconditional entered-covers в adapters и source map actual loop/calls подтверждают reachable hooks;
не добавлять пачки per-iteration conditional covers в общий helper с невозможными копиями.

Outer root: proof_for_contract existing merge_profile<StrictU8>, slice source18[..4], dest scratch32+0;
StrictU8::set_probe(any), source18:any, dest32 uninit. Sorted halves2 — только target requires, без ручных assumes.
Annotations: raw merge_up→up_adapter, raw merge_down→down_adapter; stub_verified(up_step_u8),
stub_verified(down_step_u8). **Не stub bidirectional_merge или сам merge_profile.** Его настоящий loop/odd/consumption
check исполняются; N4 even, две пары up/down. Не stub panic_on_ord_violation: canonical/sorted должны исключить его.

В adapters добавить assertions инвариантов, а не assumptions. После up:
count written dst-prefix == sum counts forward-consumed prefixes двух source halves;
после down: count written dst-suffix == sum counts reverse-consumed suffixes.
Состояние получать из actual returned tuple/текущего dst offset; source неизменен, читать лишь written destination.
Forward endpoints и reverse+1 endpoints определяют эти диапазоны; проверять bounds, не предполагать их.
Эти два ledger могут перекрываться по source до финального доказательства — не assume noncrossing/unique consumption.
Финальные std consumption checks должны дать partition original source. Для sortedness отдельно проверять
front-prefix order, back-suffix order и boundary front_last<=back_first после down; новые reads только initialized cells.
Внешние PFC ensures sortedness/full-probe count/frame сохранить полностью; source/probe frame проверить explicit.
Post-return covers: return, left-first/right-first/equal first, probe hit/miss source-prefix4; оба adapter entered reachable.

## Отрицательные controls — строки4/5/6

Все три — plain roots через тот же actual merge4/step substitutions, source18=[0;18], probe0, dst32 uninit,
valid sorted halves, canonical U8Cmp. Эта узкая постановка только для controls, не positives.
- Up binding negative: только fail_up=true, fail_down=false; **тот же up adapter** перед verified forwarder
  проверяет `kani::assert(!ctx.fail_up, "mergestep actual up adapter binding control")`, затем продолжает законный
  forwarder/decoder. Требовать reachability entry/up adapter и FAILED только этого literal.
- Down binding negative: fail_up=false, fail_down=true; аналогичный guard в **том же down adapter**:
  `mergestep actual down adapter binding control`. FAILED только его literal. Это отдельный root, чтобы успешный
  перехват одной inline(always) функции не маскировал отсутствие перехвата другой.
  В positive оба flags=false. Не портить comparator/advancement и не пропускать инициализацию output:
  это породило бы другой ord-violation/UB failure. Actual two-edge loop source map проверяется отдельно.
- Count negative: оба flags=false, actual composed merge4 сначала проходит invariants/frames/sorted/count;
  после возврата `dst[3]=1`. Prefix4 остаётся sorted, count0 4→3. Covers return-before-corruption и reached-check;
  expected FAILED только `mergestep calibration negative: full-value count preserved` у того же typed oracle.
Никаких unexpected panic/assigns/UB/unwind/unsupported/geometry failures как intended negatives.

## Build и gates

G1: шесть exact rows — up leaf, down leaf, composed merge4 PFC, up-binding negative, down-binding negative, count negative.
measurement/controls:true/jobs1/uninit off/600s per row/k1-standard4/16GiB/swap off, прежние pin/flags; unwind34,
все unwinding checks включены. Резерв `(6×10+30)×$0.0135=$1.215`.
Gate: identities/source/pin/tooling match;3 positives SUCCESS с intended checks и всеми required covers;
три negative FAILED только на named checks, все обязательные witness covers достигнуты; raw-to-summary trace обеих
step-функций и body refinement decoder подтверждены; outer destination-only frame не расширен для ghost state.
Порядок выполнения rows не гарантирует early-stop; consumer не получает credit без обоих независимых leaf proofs.

G2 — только compile error G1, без смены encoding/domains/mechanism/flags, после нового review/GO:
тот же6-row пакет, reserve$1.215; own fact_spent+reserve≤$2.50 и общий budget/slots соблюдены. Два резерва$2.430.
Resource/semantic/coverage failure не разрешает повтор; G3 нет. Учесть параллельный U64 owner в existing coordinator:
project≤2 queued/running/unresolved Builds,≤1 на stable owner. Никаких новых owners для обхода слота.

PRE-BUILD: diff; domain/init-mask/pointer-return records; exact guard/control labels/covers; raw-call map;
readonly-context/outer frame audit; annotations каждого root; targets before PFC/pfc_order плюс ordinary200/cfg404
статически; source/library/request/pin/tooling hashes; reserve/slot ledger. Rustfmt/whitespace;
library/research commits отдельно, [skip ci], push без force. Local cargo/rustc/Kani/proof и Actions dispatch запрещены.
Bounded K-1 summary/rows/peaks/targeted excerpts только; raw archives/full logs/Cloud Logging/credentials не читать.

## Итог и stop

RESULT-MERGESTEP.md ≤40 строк: identities/T/F/geometry/return encoding, rows/status/VT/CBMC RSS/checks/unreachable/
covers, gate и inherited-vs-new facts, own spent/reserved; compiler/driver/process-sum RSS отдельно.
TIMEOUT cap600, VT UNKNOWN если не напечатан; OOM отдельно. Historical merge18 TIMEOUT не переписывать.
PASS = real step/refinement proofs + actual composed N4 calibration в названных backings, не merge18 theorem.
Следующий MERGE18-COMP — только отдельная сессия/task/GO с same N18 source18→scratch32prefix18 и сохранёнными posts;
пока не запускать N18/N32 caller, u64/stable/function-item перенос. Не обещать speedup, если нет matching direct4 baseline.
Не заявлять arbitrary backing/T/FnMut, uninit detection/full alias-validity/unwind, stability или ordinary/Part1-v6 credit.
Маркеры REVIEW REQUEST <sha> / MERGESTEP ЗАВЕРШЁН; один stage — затем стоп.

## Уточнение координатора

Stable owner этой стадии — `"agent": "k1-network"` (U64-N9 идёт под `k1-merge`). Слот и ledger — по k1-network.
