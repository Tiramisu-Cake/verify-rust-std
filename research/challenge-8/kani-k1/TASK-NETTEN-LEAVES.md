# NETTEN-LEAVES — matching u8 N10 leaves для sort9 + insertion

Runtime: **Claude Code**, tmux4, **без субагентов**. Worktree `/root/verify-rust-std-kani-netten`,
ветка `experiment/kani-k1-netten-20261102`, база NETCOMP2 `58d464ce1ce3d3ad7e60325e3297fdf07d38db4c`;
library commit `f4d3775dc505ef26e30158cfa7e78f120cd3c30e`, tree `3b6d2a51dae08e52464f4b2b82f5168d8ba9977b`.
База выбрана верно: NET18/MERGESTEP/U64/v6 сюда не интегрировать. Stable owner **k1-merge**,
новый stage/UUIDs/request_id `netten-leaves-*`; U64-N13 terminal и не возобновляется.
Cap проекта$88.96 (used при постановке≈$79.04), cap этой стадии **$1.40**, один плановый Build,
максимум2 только после compile error. Exact-packet PRE-BUILD REVIEW/GO координатора обязательны.
Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` в фоновом Bash task Claude Code, без
Codex watch/CODEX_THREAD_ID/polling-субагентов/новых сессий. Evidence Brief/Select-Merge к K-1 не относятся.
Clean room: код/ветки/diff конкурентов не открывать.

## Вопрос и маршрут

Проходят ли matching leaves будущего actual Unstable u8 N10: swap_net9 в prefix9/backing10 и
insert_tail_profile<StrictU8> на всём backing10 begin0/tail9? Это leaf-only foundation, не full-route N10 theorem.
T=u8; F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP=reified strict_less::<u8>, обычный `<`.
Actual N10: Freeze+Copy/efficient-swap→network, sort9 в prefix9, insertion_sort_shift_left offset9 делает одну
insert_tail(begin0,tail9), затем no_merge return. Source initialized exact backing10, offset0, всё in place;
sort13/general/merge/scratch здесь не нужны. Все byte values/probe независимые полные any u8.

Read RESULT-NETCOMP2/TASK-NETCOMP2; netcomp.rs swap_net9/leaf9/U8Cmp/canonical; network.rs StrictU8/count/
sorted helpers и прежние insertion PFC; specfix.rs insert_tail_profile/tail_region/tail_len/model_count/model_sorted;
actual sort9/insertion/insert_tail; TASK-SPECFIX (запреты/evidence/format), pfc_order.py.

## Разделение файлов и неизменяемое

Новый opt-in child **network::netcomp::netten**, файл `verify/network/netcomp/netten.rs`;
в netcomp.rs только регистрация child после existing targets/roots. Parent private swap_net9/U8Cmp/StrictU8
и pure helpers доступны child без изменения visibility.
DIRECTFOUR пишет только дочерний directfour.rs и parent mergestep.rs в другом worktree; эти файлы не трогать.
Наш netcomp.rs edit не переносить в peer; source integration/RUN-REQUEST histories позже отдельно.
Старые targets/contracts/roots/contexts/pin/tooling/workflows/runtime smallsort.rs не менять и не обобщать.
Ordinary exact200;2 новых PFC roots → cfg-on395→397 статически (не native inventory/proof).

## Ровно2 independent PFC, без stubs

1. `netten_swap_prefix9_backing10`: proof_for_contract **прежнего swap_net9**, unwind25.
   Полный `[u8;10]=kani::any()`, snapshot всех10; independent probe:any u8; a,b distinct<any9.
   Actual argument base+0, cmp explicit U8Cmp=StrictU8::CMP. Target/его requires/ensures/modifies/body не менять;
   он реально вызывает swap_if_less::<u8,U8Cmp>, без manual/verified stubs.
   После return проверить pair/order, count active9 и whole-backing10 с тем же probe, все8 cells вне выбранной
   global pair unchanged, особенно v[9]==pre[9]. Не выделять отдельный [u8;9] вместо prefix backing10.
   Required covers8: старые7 leaf9 (swap/no-swap,0→8,8→0,interior,probe hit/miss ACTIVE9) плюс
   `probe==pre[9] && count(pre[..9],probe)==0` — untouched-tail-only probe hit. Это cover, не input assumption.
2. `netten_insert_strict_u8_begin0_tail9`: proof_for_contract existing insert_tail_profile, instance StrictU8,
   unwind25/unwinding assertions. `StrictU8::set_probe(kani::any())` до независимого any `[u8;10]`,
   сохранить probe и полный pre. Передать base+0, base+9, actual cmp:U8Cmp=StrictU8::CMP.
   Не делать новый target/wrapper, не добавлять stubs. Body реально вызывает insert_tail::<u8,U8Cmp>.
   Sorted prefix9/initialized writable region10/canonical cmp — только существующие requires PFC; они
   автоматически ограничивают допустимые leaf inputs. Без ручных assumes или сортировки constructor-ом.
   Проверяются исходные sortedness10/full-model count/region-only assigns. Дополнительно pure typed post-check:
   full10 sorted, count(pre,probe)==count(post,probe), StrictU8 probe unchanged. Pre-prefix9 и pre-tail сохраняются
   в local snapshot, не считываются после мутации как будто это old state.
   **Весь backing10 writable**: прежний tail-v[9] frame относится лишь к SWAP leaf, не к insertion.
   Здесь не добавлять sentinel/backing12 ради frame — это изменит нужный actual domain.
   Required covers8 после target: returned; pre[9]<pre[0] (new first); pre[8]<=pre[9] (last/no move);
   pre[0]<pre[9] && pre[9]<pre[8] (interior); pre[9]==pre[4] (tie with prefix); actual output differs from pre;
   independent probe hits whole pre10; independent probe misses whole pre10. Все достижимы при sorted-prefix9.

Для обоих roots all source/probe values unrestricted кроме **легитимного helper sorted-prefix premise** строки2.
Старый LtU8 uses x>>1/backing17 и не является этим StrictU8/default-< leaf. Старый exact9 swap PFC также не
доказывает backing10. В swap probe by value, в insertion Profile::probe static; общий будущий caller обязан
инициализировать их одним выбранным значением до вызовов и сохранить frame. Здесь end-to-end witness ещё не соединяется.
Covers outside targets/ensures, только достижимые; новые scalar predicates/посты ради скорости не ослаблять.

## Controls, G1, stop

Stage только добавляет2 geometry/tag fixtures к прежним targets. Старые negatives и таймаутные roots не запускать;
новых binding controls/adapters/caller N10 сейчас нет. Существующие controls не выдавать за проверку будущего
actual insert-tail hook. Caller позже отдельно обязан установить prefix-sorted9 настоящей сетью, без assume,
и проверить raw swap/insert_tail→summary связь с pre-failure-only witness covers.

G1 exact2 positive rows, expect SUCCESS; measurement/controls:true/jobs1/uninit off/600s/k1-standard4/16GiB/swap off,
unwind25/unwinding assertions, прежние pin9461e07af7/nightly-2026-10-12/tooling/flags.
Резерв `(2×10+30)×$0.0135=$0.675`. С DIRECTFOUR G1$0.540 —$1.215 плановых резервов, отдельные owners/stages.
Project≤2 queued/running/unresolved Builds,≤1 на stable owner; текущий global used/reserved и slots проверить перед GO.
Gate: identities match, оба real-body PFC SUCCESS/0 unexpected failed checks и8/8 covers каждый;
runtime/source/ordinary restrictions соблюдены. Это prerequisite будущего caller, не actual N10 proof.
TIMEOUT/OOM/FAILED/coverage/UNKNOWN → сохранить per-row facts, PARTIAL/FAIL и стоп; no input/probe narrowing,
no N11/N14/32 или caller автоматически, no timeout/machine change.
G2 только после compile error G1, тот же2-row вопрос/domains/targets/flags, новый review/GO,
reserve$0.675 и own fact_spent+reserve≤$1.40 плюс global slots/ledger. Два полных резерва$1.350≤$1.40.
Resource/semantic/coverage failure не разрешает repeat. G3 нет; после стадии стоп.

PRE-BUILD: diff, domain T/F/CMP/model/probe/N/backing/offset/init/frame; roots/annotation table без любых stubs;
source-map будущих N10 calls и отличие requires/executed domains; exact cover predicates/counts;
request/library/source/pin/tooling hashes; target ordering/pfc_order плюс ordinary200/cfg397 статически;
rustfmt/whitespace, own/global reserve/slots. Library/research commits отдельно, [skip ci], push без force.
No local cargo/rustc/Kani/proof, Actions dispatch/deployment. Evidence — bounded K-1 summaries/rows/peaks/
разрешённые targeted excerpts; raw archives/full logs/Cloud Logging/credentials/hidden configs не читать/скачивать.
Historical results/ledger и U64-N13 PARTIAL не переписывать.

## Итог

RESULT-NETTEN-LEAVES.md ≤30 строк: reviewed/build/library/request identities, exact T/F/CMP/model/probe/backing/
geometry каждого leaf, rows/status/VT/CBMC RSS/checks/unreachable/covers/gate, own spent/reserved;
compiler/driver/process-sum RSS отдельно. TIMEOUT cap600 и VT UNKNOWN если не напечатан, OOM отдельно.
PASS = новый matching swap-prefix9/backing10 и StrictU8 insertion10 begin0/tail9 leaf credit, не whole N10 theorem.
Не обобщать на other N/backings/offsets, generic T/FnMut/function-item F, ties stability,
uninit detection/full alias-validity/unwind или Part1-v6/ordinary. U64-N13 consumer остаётся OPEN.
Маркеры REVIEW REQUEST <sha> / NETTEN-LEAVES ЗАВЕРШЁН; один stage — после результата стоп.
