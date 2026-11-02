# U64-TEN-LEAVES — два matching real-body leaf для будущего u64 N10

Runtime: **Claude Code**, без субагентов.
Worktree `/root/verify-rust-std-kani-usixtyfourten`, ветка `experiment/kani-k1-usixtyfourten-20261102`; slug **usixtyfourten**. Stable owner **k1-network**, новая стадия,
UUIDs/request_id `usixtyfourten-*`. База завершённого U64-N9 —
`9ab925b1578b9102e3009c0ec940c5c9cc0280cb`, library commit
`fddf308321046a8cd8f5526622a5e2353d79830e`, tree `d22566ab5a685df2608ddb756714e51ad288f08d`.
Не брать базой U64-N13 и не возобновлять его PARTIAL стадию. Project cap $88.96, used≈$79.74;
свой cap **$1.40**, один плановый Build, максимум2 только по compile-error ветке ниже.
PRE-BUILD REVIEW + exact-packet GO координатора обязательны. Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD`
в фоновом Bash task Claude Code; без Codex watch/CODEX_THREAD_ID, polling-субагентов/новых сессий.
Evidence Brief/Select-Merge к K-1 не относятся; clean room: competing code/branches/diffs не открывать.

## Вопрос и маршрут

Проходят ли для **полного u64** два leaf на геометрии actual Unstable N10: swap prefix9/backing10
и insertion begin0/tail9/backing10? Здесь нет caller, нового summary/context или новых stubs.
T=u64, F=U64Cmp=fn(&u64,&u64)->bool, value StrictU64::CMP=reified strict_less::<u64>, обычный `<`.
Exact initialized backing10, offset0, independent full-width any u64 probe. Actual будущий маршрут:
Freeze+Copy/efficient swap → sort9 prefix9, insertion offset9 с одним insert_tail(0,9), no merge.

Прочитать RESULT-U64-N9, u64nine.rs/swap_u64_net9/count9_u64; NETTEN-LEAVES как geometry pattern;
network.rs StrictU64/strict_less/model helpers; merge/specfix.rs insert_tail_profile/tail_region/tail_len/
model_sorted/model_count и реальные raw swap/insert_tail. TASK-SPECFIX/pfc_order.py — checks/формат/ordering.
Старый exact9 u64 swap leaf не доказывает backing10. Старые LtU64 insertion PFC используют x>>1 и другие
backing/offset; они не заменяют StrictU64 begin0/tail9/backing10.

## Файлы и независимость

Новый opt-in child **network::u64nine::tenleaves**, файл
`library/core/src/slice/sort/shared/smallsort/verify/network/u64nine/tenleaves.rs`;
в u64nine.rs только регистрация child после existing items. Parent private swap_u64_net9/U64Cmp/count9_u64
и ancestor StrictU64 доступны child без widening visibility. Если нужны pure sorted/count10 helpers,
разместить их в новом child; payload/probe — u64, результат count — usize, без сужения payload.

Старые targets/contracts/bodies/roots/contexts, runtime std, tooling/runner/workflows/pin/flags не менять.
Не интегрировать v6/U64-N13/Part 2 и не факторизовать общий u8/u64 framework. Параллельная PARTTWO-TREE
читает только pinned historical commits в другом worktree; она не потребляет этот незавершённый кандидат.
Никаких изменений чужого worktree, live requests или ledgers.

## Ровно два independent PFC, без stubs

1. `u64ten_swap_prefix9_backing10`: proof_for_contract **existing swap_u64_net9**, unwind25.
   Any `[u64;10]`, полный pre snapshot, independent any probe:u64, arbitrary distinct a,b<9;
   actual base+0 и explicit canonical U64Cmp. Target/его requires/ensures/modifies/body не менять:
   он реально вызывает swap_if_less::<u64,U64Cmp>. Проверить full-value pair transfer/order,
   count active9 и whole10 с тем же probe, frame всех8 элементов вне pair, включая v[9]==pre[9].
   Не подменять backing10 отдельным `[u64;9]`.
   Required covers9 после target: swap; no-swap; a==0&&b==8; a==8&&b==0; interior pair;
   probe hits pre active9; probe misses pre active9; probe==pre[9] и misses pre active9;
   probe>=(1u64<<40) и hits whole pre10. Все — covers, не input assumptions.
2. `u64ten_insert_strict_u64_begin0_tail9`: proof_for_contract **existing insert_tail_profile**, StrictU64
   instance, unwind25/unwinding assertions. `StrictU64::set_probe(kani::any())` до независимого any `[u64;10]`;
   сохранить probe/pre, передать base+0/base+9 и actual cmp:U64Cmp=StrictU64::CMP.
   Не создавать новый wrapper target и не добавлять stubs. Real body вызывает insert_tail::<u64,U64Cmp>.
   Sorted prefix9/initialized writable region10/canonical cmp — только existing PFC requires;
   без manual assumes/any_where/constructor sorting. Проверить исходные sortedness/full model-count/
   region-only assigns, дополнительно typed pure sorted10/count(pre,probe)==count(post,probe)/probe frame.
   Весь backing10 writable; tail-v[9] frame от swap здесь не действует. Без sentinel/backing12.
   Required covers9 после target: returned; pre[9]<pre[0]; pre[8]<=pre[9];
   pre[0]<pre[9]&&pre[9]<pre[8]; pre[9]==pre[4]; output differs from pre;
   probe hits whole pre10; probe misses whole pre10; probe>=(1u64<<40) и hits whole pre10.
   Условия относятся к pre-state, не к перечитанной после мутации памяти.

Входы и probe не ограничивать до u8/u32, малых значений, distinct values или конкретного high-bit witness.
High-bit cover показывает достижимость, не заменяет full any u64 домен. Легитимная sorted-prefix premise
insertion — предусловие helper, не доказательство этой premise реальной сетью; это задача будущего caller.
Swap получает probe by value, insertion — через StrictU64 static; будущий caller обязан связать их одним
значением до entry. Эта стадия проверяет leaf отдельно и не утверждает end-to-end связь.
Covers вне targets/ensures. Никаких caller/adapters/binding controls здесь; старые negatives не запускать.

## G1, gate и stop

Один exact packet из двух новых positive rows: measurement/controls:true/jobs1/uninit off/600s per row,
k1-standard4 4CPU/16GiB/swap off, unwind25/unwinding assertions. Frozen tooling `30f77e8599`,
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12, прежние organizer flags/checks.
Резерв `(2×10+30)×$0.0135=$0.675`. С PARTTWO-TREE G1 общий плановый резерв $1.350, отдельные owners/stages.
Project≤2 queued/running/unresolved Builds, ≤1 на stable owner; перед GO актуальные ledger/slots.

Gate: exact identities/domain; оба real-body PFC SUCCESS, 0 unintended failed checks, 9/9 covers каждый;
no stubs/target changes, ordinary/runtime restrictions сохранены. Оба PFC fixtures новые; не присваивать им
скорость/RSS старых u8 leaf и не считать успех одного за успех второго.
TIMEOUT/OOM/FAILED/coverage/UNKNOWN → per-row facts, overall PARTIAL/FAIL и стоп. Не сужать width/probe/input,
не ослаблять posts/frame/covers, не менять RAM/timeout и не переходить к caller/N14/N18 автоматически.
G2 только после compile error G1, тот же вопрос/domains/targets/две rows/flags, новый review/GO;
reserve$0.675 и own fact_spent+reserve≤$1.40, глобальные slots/ledger соблюдены. Два резерва$1.350≤$1.40.
Resource/semantic/coverage failure не разрешает repeat; G3 нет.

PRE-BUILD: semantic diff/dependencies; T/F/CMP/probe/backing/offset/init/frame каждого leaf;
PFC target/annotation table без stubs; точные cover predicates/counts; target ordering/pfc_order отдельно
от source/cfg inventory. Ожидается ordinary200 базы без изменений; cfg-on399→401 статически при ровно
двух новых roots, проверить exact name-set delta, не выдавать static counts за native inventory/proof.
Request/source/library/tree/pin/tooling hashes, static rustfmt/whitespace и бюджеты/slots.
Library/research commits отдельно, `[skip ci]`, push без force. No local cargo/rustc/Kani/proof,
Actions dispatch/deploy. Evidence — bounded K-1 summaries/rows/peaks/разрешённые targeted excerpts;
raw archives/full logs/Cloud Logging/credentials/hidden configs не читать/скачивать.
Historical results/ledger и U64-N13 PARTIAL не переписывать.

## Итог

`RESULT-U64-TEN-LEAVES.md` ≤30 строк: reviewed/build/request/library/tree identities, typed domains/geometry,
rows/status/VT/checks/unreachable/covers/gate, CBMC RSS и отдельно compiler/driver/process-sum RSS,
own spent/reserved. VT не напечатан → UNKNOWN; TIMEOUT cap600 не завершённый VT, OOM отдельно.
PASS — только matching u64 swap-prefix9/backing10 и StrictU64 insertion10 leaves. Whole actual N10,
raw binding/shared probe/prefix establishment, function-item F, arbitrary T/FnMut/N/backings/offsets,
stability/uninit detection/full alias-validity/Rust unwind и ordinary v6 credit здесь не установлены.
Caller после PASS — новая стадия; учитывать NETTEN-CALLER driver14GiB и заранее рассмотреть highmem,
не запускать его автоматически. Маркеры `REVIEW REQUEST <sha>` / `U64-TEN-LEAVES ЗАВЕРШЁН`; затем стоп.
