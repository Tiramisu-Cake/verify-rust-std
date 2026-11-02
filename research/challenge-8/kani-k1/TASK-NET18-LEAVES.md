# NET18-LEAVES — независимые листья для геометрии Unstable u8 N18

Исполнитель: свежая clean-room сессия. Worktree `/root/verify-rust-std-kani-net18leaves`, ветка `experiment/kani-k1-net18leaves-20261102`; база NETCOMP2
`58d464ce1ce3d3ad7e60325e3297fdf07d38db4c`, library commit `f4d3775dc505ef26e30158cfa7e78f120cd3c30e`,
library tree `3b6d2a51dae08e52464f4b2b82f5168d8ba9977b`. Не интегрировать MACSPLIT/v6/DOMSIX и другие пилоты.
Cap проекта$88.96, остаток при постановке≈$11; cap стадии$1.70, один плановый Build, максимум2 только по compile-error
ветке ниже. Stable owner/slot/ledger — существующий K-1 coordinator; свой spent/reserved по своим UUID.
request_id `net18-leaves-*`. PRE-BUILD REVIEW и exact-packet GO координатора обязательны.
Ожидание — `research/challenge-8/kani-k1/tools/k1g.sh watch UUID` с CODEX_THREAD_ID, затем завершить ход.
Evidence Brief / Select-Merge к K-1 не относятся. Конкурирующие решения/ветки/diff не открывать.

## Вопрос и критерий

Укладываются ли три недостающие real-body PFC в600s/row на pin: swap-summary active9 в backing18 на offsets0/9,
и canonical StrictU8 merge18 source input→destination prefix18 в отдельном scratch32?
Это foundation для будущего actual Unstable u8 N18, а не доказательство caller N18 в этой стадии.

Маршрут: u8 Copy+Freeze/efficient-swap → small_sort_network; N18 splits9+9, sort9×2, insertion offset9
без вставок, затем bidirectional_merge(v, stack32_ptr), copy back. sort13/sort4/sort8 здесь не вызываются.
T=u8, F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP=reified strict_less::<u8>; ordinary `<`, full-byte counts.
Это тот же explicit fn-pointer domain NETCOMP2, не его предшествующий function-item F.

Прочитать: RESULT-NETCOMP2/TASK-NETCOMP2 и сохраняющиеся запреты TASK-NETCOMP; actual dispatch/network/merge;
netcomp.rs swap_net9/leaf9; specfix.rs merge_profile, merge_regions, merge_halves_sorted, Profile/model_count;
TASK-SPECFIX (запреты/логи/format/expect_check), pfc_order.py. Обход raw-call binding пока не реализовывать.

## Размещение и неизменяемое

Добавить opt-in дочерний модуль `network::netcomp::neteighteen` после существующих targets/roots; он наследует
kani_smallsort_controls и может видеть private swap_net9/U8Cmp предка без расширения visibility.
Разрешены новый файл с fixtures/helpers и только регистрация child module в netcomp.rs. Старые targets, contracts,
PFCs, controls, Context9/13/bridges, runtime smallsort.rs, tooling/workflows/flags/pin неизменны.
Ordinary exact200; cfg-on395→398 при ровно3 новых harnesses — статическая проверка, не proof inventory.
Не создавать новые profile tags/comparators, не менять model/count/write-set для ускорения.

## Ровно три новые PFC

1. `net18_swap_left_backing18`: proof_for_contract прежнего swap_net9. Полный `[u8;18]=kani::any()`,
   snapshot всех18 значений; independent probe:any u8; local a,b<any9, distinct. Передать base+0,
   фактический U8Cmp и by-value probe. Active9 — глобальные0..8, не exact allocation9.
2. `net18_swap_right_backing18`: отдельный PFC того же target; такие же unrestricted данные, но base+9;
   active9 — глобальные9..17. Никакого symbolic выбора offsets или union/match двух placements.
   В обоих cases сохраняются старые requires/ensures/modifies; target исполняет настоящий swap_if_less без stubs.
   После возврата проверить pair transfer/order по выбранным local indices, active9 и whole-backing18 count
   того же probe, и каждое backing-значение вне глобальных выбранных a/b неизменно. Это подтверждает frame
   через границу двух halves. Не создавать второй `[u8;9]` как подмену нужного backing18.
   Covers по образцу leaf9: swap/no-swap, first→last, last→first, interior pair, probe hit/miss ACTIVE9 — 7 каждый.
   Helpers/covers outside contracted target; unwind25 с unwinding assertions.
3. `net18_merge_strict_scratch32`: proof_for_contract существующего merge_profile, instance StrictU8.
   `StrictU8::set_probe(kani::any())` до независимого arbitrary initialized source `[u8;18]`;
   destination — отдельный `MaybeUninit<[u8;32]>::uninit()`, base offset0, writes только prefix18.
   Передать source18 slice, dest u8 pointer, полученный canonical `cmp:U8Cmp=StrictU8::CMP`.
   Обе source halves9 model-sorted — именно requires цели PFC; они автоматически ограничивают допустимый
   leaf input. Не добавлять ручных assumes, сортировку source конструктором, probe correlations или stubs.
   Body generic forwarder реально вызывает bidirectional_merge::<u8,U8Cmp>. После возврата explicit checker:
   source все18 значений и global probe неизменны; dest initialized prefix18 sorted по ordinary `<`;
   full-value count src/dst по тому же StrictU8 probe совпадает. Existing destination-only modifies не менять.
   **Dest tail18..32 остаётся uninitialized: не читать, не snapshot-ить как u8, не инициализировать ради assert.**
   Проверяется real write frame, не автоматическое обнаружение uninit reads (instrumentation off).
   Unwind34 как у существующих merge PFC, unwinding assertions включены. До GO обосновать достаточность для
   merge18 и explicit source/frame/count loops; не менять bound пробными Builds.
   Только достижимые uncontracted covers: return; left-first/right-first (`src[0]<src[9]` / обратное);
   equal first values; independent probe hit/miss в source18 — 6 covers. Не добавлять cover на uninit tail.

Для swap by-value probe и merge Profile::probe паспорт различается; в каждом leaf он unrestricted/неизменен.
Будущий caller должен явно выбрать одно значение и присвоить его обоим механизмам до вызовов; этот task ещё
не соединяет отдельные leaf proofs в end-to-end theorem.

## Controls и границы этого этапа

Здесь targets/контрактные predicates/проверки не меняются, добавляются только новые geometry fixtures для
самостоятельных PFC. Старые negative controls не повторять и не выдавать их за controls новых actual adapters.
Не писать caller/adapter18, raw helper stubs/stub_verified consumers или сеть-копию. Actual raw→summary binding,
обе half-count invariants и final merge premises потребуются в следующем отдельном NET18-CALLER с собственными
binding/count negatives. Leaf18 с sorted-half requires не доказывает, что sort9 caller устанавливает их.
Запрет на ручные assumes не отменяет законные requires PFC; эти requires не являются обещанием всех placements.

## Build / stop

G1 measurement, controls:true, jobs1, uninit off, timeout10min, k1-standard4/16GiB/swap off, прежние pool/pin/flags.
Request — exact full names ровно3 новых positives, expect SUCCESS для каждой; все required covers SATISFIED,
0 unexpected failed checks/unsupported/unwinding. Резерв `(3×10+30)×$0.0135=$0.810`.
Любой TIMEOUT/OOM/FAILED/UNKNOWN даёт PARTIAL/FAIL stage, но отдельные доказанные rows сохраняются; остановиться.
Не сужать input/probe, не исключать правую half и не переносить результат на N32.
G2 допускается только после compile error G1: тот же механизм/3rows/domains/flags, новый review/GO,
полный reserve$0.810, own fact_spent+reserve≤$1.70 и вписывается в project ledger. Резерв двух попыток≤$1.620.
После resource/semantic/coverage failure автоматического G2 нет. G3 нет; переход к caller не входит в эту сессию.

До GO: полный diff и domain record (T/F/CMP/probe, actual argument bases/backings/offsets/init/frame);
source map будущих call geometries; target ordering/PFC order плюс отдельная ordinary200/source-cfg398 сверка;
request hash, library/source/pin/tooling identities, slot/reserve; rustfmt/whitespace. Library/research commits отдельно,
`[skip ci]`, push без force. Никаких локальных cargo/rustc/Kani/proof запусков, workflow dispatch или deployment.
Evidence читать через bounded K-1 reports/rows/peaks и разрешённые targeted check excerpts; raw archives/full logs,
Cloud Logging и credentials/config не читать/скачивать. Исторические proof/ledger записи не переписывать.

## Итог

`RESULT-NET18-LEAVES.md` ≤35 строк: reviewed/build/library/request identities, F/value/geometry каждого leaf,
rows/status/VT/CBMC RSS/failed-total/unreachable/covers, overall gate, own spent/reserved; compiler/driver peaks отдельно.
TIMEOUT cap600, VT=UNKNOWN если не напечатан; OOM отдельно. Native inventory/static counts не являются proofs.
При3 SUCCESS с covers установлен только matching leaf credit для названных двух swap placements и merge geometry;
actual N18 composition НЕ установлена. Не заявлять arbitrary backing/offset/T/FnMut/function-item F/N32,
stability ties, initialization detection/full alias-validity/unwind scope или ordinary/Part1-v6 proof credit.
Маркеры `REVIEW REQUEST <sha>` / `NET18-LEAVES ЗАВЕРШЁН`; один stage — после результата стоп.
