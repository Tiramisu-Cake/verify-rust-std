# SAFETYNET — четыре существующих network safety groups u64 N18..29

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов. Worktree **/root/verify-rust-std-kani-safetynet**,
ветка **experiment/kani-k1-safetynet-20261103** от **2104e7a596fabb058a99c8bcdf0e3f487d9a7753**.
Slug **safetynet**, stable owner **k1-network**, новые stage/ledger/UUID/request_id `safetynet-*`.
Library tree **d4ec476a7a001363e58f19948c188a9c2078e370** = Part1 v6; K-1 tooling из базы FAST/MACSPLIT.
Не возобновлять FAST/POSTS8 ledger и не merge их новый library/research code или integrated tree.
Project cap **$88.96**, свой **$1.00**; **один Build, retry/G2 нет**. Повышение до$95/$105 здесь не требуется.
Main120min+closeout30min, T0 при фактическом старте. Полный70min envelope должен помещаться в main с finishing reserve.
Проверить HEAD/branch/dirty state, identities, current global/night spent/reserved/slots до подготовки GO.

## Цель и exact rows

Измерить прежние opt-in roots, закрывающие normal-return safety выбранного u64 Unstable network domain
для N18..29. Source/harnesses/домены не менять. Это не correctness, не все T/F и не вся general/Stable matrix.
Request names — полные с prefix `slice::sort::shared::smallsort::verify::`:

| Root в network:: | Длины | Required covers, source forecast |
|---|---|---:|
|network_safety_unstable_u64_n18_to21|18,19,20,21|6/6|
|network_safety_unstable_u64_n22_to25|22,23,24,25|6/6|
|network_safety_unstable_u64_n26_to27|26,27|4/4|
|network_safety_unstable_u64_n28_to29|28,29|4/4|

Read pinned `verify/network.rs`: unstable_dispatch_network_cases, unstable_dispatch_network_fixed,
volatile_reading_less_u64, cut_order_violation_panic/assume_order_violation; actual trait/network/merge route.
Пути verify относительно `library/core/src/slice/sort/shared/smallsort/`.
Cover totals = нормальный возврат каждой перечисленной длины +family end +cover внутри panic stub.
До GO сверить полный reachable source cover inventory. Если forecast не совпал, показать concrete discrepancy
координатору; не удалять cover и не подменять ожидаемый total ради PASS. Нельзя засчитать один panic witness
за normal return всех lengths. Штатный K-1 gate проверяет полную satisfied/total coverage.

## Frozen domain и source restrictions

Exact initialized any `[u64;N]` в каждом dispatch arm, base offset0, все64 bits. F — прежний function-item
volatile_reading_less_u64: оба аргумента читаются volatile, возвращается arbitrary bool; никакого ordered profile.
Actual `<u64 as UnstableSmallSortTypeImpl>::small_sort` →Freeze/Copy network, реальные sort9/sort13/insertion/
merge callees; не заменять entry прямым вызовом helper. Внутренний network scratch32 прежний.
Исходный `#[kani::stub(panic_on_ord_violation,cut_order_violation_panic)]` сохранён: panic cover затем assume(false).
**Unwind35**, unwinding assertions и прочие исходные checks сохраняются. No verified stubs/contracts/summaries.
Это normal-return scope: не Rust unwind-cleanup, не full UB-class assurance. Uninit checks профиль не расширяет.

Library/runtime/harness bodies/annotations/covers, workflows/tooling/runner/pins не менять.
Не сужать payload/comparator/lengths, не добавлять assumed sorted prefix, новые cuts или invariants.
Разрешены только свои task/request/PREBUILD/research receipts/RESULT. Ordinary202/PFC36,
static cfg-on384/opt-in182 неизменны; extra inventory/proof roots в этой стадии не создавать.
Clean room: competing PR/диффы/код/ссылки не открывать и не включать в задания/пакеты.

## Единственный G1, ledger и GO

Ровно4-row **measurement**, expect SUCCESS для каждой строки; runner gcb-e2-standard-4 →k1-standard4,
4CPU/16GiB/swap off, controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10/600s per row.
Kani **9461e07af7ec929f050aa4192f29363c9be07779**, nightly-2026-10-12;
frozen tooling **30f77e859903df14b442ff9294d4fbbd44827f20**, check-tooling против него.
Никакого highmem/kind resource/solver flags/new instrumentation/ручной list preparation.
Резерв **(4×10+30)×$0.0135=$0.945≤cap$1.00**. Own fact_spent+reserve≤cap;
global cap$88.96, night envelope, project≤2 queued/running/unresolved и≤1 на stable owner соблюдены.
Проверить, что предыдущий k1-network Build terminal/accounted; foreign reservations/ledgers не трогать.
Unknown submit сначала разрешить через coordinator, не дублировать. GO относится только к этому exact packet.

PRE-BUILD: source/library/tree/request/tool hashes, exact names/cfg/stub/unwind/cover table,
domain/actual route/scratch record, library unchanged, static ordinary set preservation;
existing request validation/preflight, бюджет/slots/deadline. Metadata commits `[skip ci]`, publish без force.
Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` в фоновом Bash task Claude Code;
без Codex watch/CODEX_THREAD_ID/polling-субагентов/новых сессий.

## Gate, stop и RESULT

Gate каждого root: matching identities/profile; SUCCESS,0 unintended failures, все исходные covers достигнуты.
Overall PASS только4/4 accepted. Cloud SUCCESS не заменяет per-row gate. TIMEOUT/OOM/FAILED/coverage/
UNKNOWN/compile error → bounded facts, PARTIAL/FAIL и стоп. **Никаких retries, compiler/code fixes, второго Build,
нового split, timeout/RAM/profile change или автоматического запуска general batches.**
GCB≤300s — рабочий shortlist; ≤600s proof fit не доказывает macOS/jobs3 с запасом400–450s.
CBMC row RSS отдельно, compiler/driver/process-sum по Build; missing UNKNOWN, timeoutcap600 не завершённый VT.

**RESULT-SAFETYNET.md**,≤35 строк: reviewed/build/request/library/tree/pin/tooling identities,
4-row table status/VT/checks/unreachable/covers/CBMC RSS, packet peaks/gate, own spent/reserved,
source limits и candidate-for-Mac flags. Исторические Mac timings не выдавать за новый matched run.
Результат opt-in, ordinary/v7 не менять; внешние PR/issue/CI только по решению владельца.

В RESULT добавить **план следующих general-пакетов, не запускать их**: existing
`merge::route_safety_all_routes_nN` для23 N={9..15,17..32}, на том же v6 library/tooling pin:
A[9,10,11,12], B[13,14,15,17], C[18,19,20,21], D[22,23,24,25], E[26,27,28,29], F[30,31,32].
Пять4-row reserves по$0.945 +один3-row$0.810 = **$5.535**, отдельные будущие stages/caps/GO.
Указать три исходных routes: direct general u64, non-Copy Unstable general, Stable u64; source covers/frames
проверять отдельно, не называть это всеми типами/всеми trait impl. После первых пакетов пересмотреть дальнейший план.

Evidence только bounded K-1 summaries/rows/peaks/targeted excerpts; Evidence Brief/Select-Merge к K-1 не относятся.
Raw archives/full logs/Cloud Logging/credentials/hidden configs запрещены. Нет local cargo/rustc/Kani/proofs,
Actions/deploy/submission. Historical results/ledgers сохраняются. Маркеры `REVIEW REQUEST <sha>` /
**SAFETYNET ЗАВЕРШЁН**, одна стадия, затем стоп.
