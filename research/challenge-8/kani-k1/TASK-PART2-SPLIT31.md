# PART2-SPLIT31 — разделить исходный bytes17 N31 safety domain по двум routes

Runtime: **Claude Code**, без субагентов; одна стадия на сессию.
Worktree `/root/verify-rust-std-kani-partsplit`, ветка `experiment/kani-k1-partsplit-20261102`, tmux 4. Owner **k1-merge**, только после terminal/accounting
PARTTWO-TREE; старую стадию не возобновлять. Новые UUIDs/request_id `partsplit-*`.
База **MACSPLIT `4f4034527d3e3a26e4cd94e12ba6922e2b5e80e4`**: library tree
`d4ec476a7a001363e58f19948c188a9c2078e370` = Part1 v6 `d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097`,
но с необходимым K-1 tooling. Голый submission v6 базой не брать; текущий integrated PARTTWO-TREE сюда не merge.
Cap проекта$88.96; свой cap **$2.50**. Два плановых Build, максимум4 только по compile-error веткам ниже.
Wall window: main180min +closeout30min, T0 при фактическом старте; каждый полный Build envelope и closeout reserve
должны помещаться в действующие deadlines. Cap/окно не дают автоматического права на все4 попытки.
PRE-BUILD REVIEW + exact-packet GO координатора перед каждым Build. Подготовка TASK не регистрирует phase.

## Цель и matching исходная задача

Ускорить конкретный исходный opt-in root **network::dispatch_safety_stable_unstable_bytes17_n31**,
разделив его Stable/Unstable cases. Сохраняется весь объединённый domain, а не добавляется другая theorem/F.
Исторически organizer partitions run40748125754/source6cfc76cb: Ubuntu123.7s/macOS800.3s;
это не current v6 autoharness baseline и не GCB timing. Текущий matching baseline измеряется отдельно в G2.
Precedent RESULT-MACSPLIT: для N32 GCB pair284s/4.20GiB →Stable110.8s/1.70GiB и Unstable137.1s/2.50GiB.
Числа N32 не прогноз N31; per-root max и суммарный VT сравнивать отдельно.

Read `verify/network.rs` macros dispatch_pair_safety_cases/dispatch_safety_cases, dispatch_safety_fixed,
ArbitraryValue<[u8;17]>, volatile_reading_less, assume_order_violation; actual Stable/Unstable entry routes;
RESULT-MACSPLIT, macsplit native ordinary202/reference, TASK-SPECFIX restrictions/pfc_order.
Все пути verify ниже относительно `library/core/src/slice/sort/shared/smallsort/`.

## Ровно два новых opt-in roots, минимальный source diff

В **verify/network.rs** рядом с прежним N31 pair добавить через **existing dispatch_safety_cases!**:

1. `#[cfg(kani_smallsort_controls)]` invocation
   `dispatch_safety_stable_bytes17_n31`, type `[u8;17]`, STABLE=true, lengths `[31]`.
2. Такой же opt-in invocation `dispatch_safety_unstable_bytes17_n31`, type `[u8;17]`, STABLE=false, `[31]`.

Не менять/копировать macro definitions и dispatch_safety_fixed. Исходный pair root оставить без изменений как
research baseline; новые roots пока не ordinary. Domain equality: произвольный stable:bool старого pair =
объединение двух fixed cases, каждый с полным прежним input/comparator domain. Схему записать в PREBUILD.
Никаких дополнительных assumptions или сортировки/ограничения input ради PASS.

Сохранить: exact initialized31 элементов `[u8;17]`, все17 bytes каждого элемента full-any; allocation/offset0;
stable scratch exact48 MaybeUninit; прежний inferred **function-item F volatile_reading_less::<[u8;17]>**,
volatile reads обоих аргументов и arbitrary return bool. Не coercion в fn-pointer и не ordered profile.
Actual dispatch не заменять вызовом выбранного алгоритма. Для bytes17 проверить source route map,
не считать этот unstable case network только из-за названия модуля.
Те же panic-on-order-violation stub → assume_order_violation, unwind65/unwinding assertions и safety checks.
Это прежний normal-return safety scope с panic cut; sorting/permutation/unwind/drop-count claim не добавляется.
Не добавлять verified stubs, contracts, backing holder либо comparator restrictions.

Required covers: каждый новый root2/2 — normal return N31 +family end; old pair3/3 — Stable return,
Unstable return, family end. Оба старых route cases представлены новыми roots; один SUCCESS недостаточен.
Обычные N32 split roots и все202 ordinary source bodies/domains/annotations неизменны.
Static cfg-on384→386, opt-in182→184, PFC36 без изменений; проверить exact name-set delta +2,
не выдавать static forecast за новый native inventory. Ordinary202 сохранить set-equal native MACSPLIT reference.
Другие worktrees/requests/ledgers, runtime std/tooling/runner/workflows/pin/check flags не трогать.

## Requests и порядок Builds

Frozen tooling **30f77e859903df14b442ff9294d4fbbd44827f20**, Kani
**9461e07af7ec929f050aa4192f29363c9be07779**, nightly-2026-10-12.
Все пакеты: measurement, runner gcb-e2-standard-4 →k1-standard4,4CPU/16GiB/swap off,
controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10 /600s per row.
Никакого highmem/resource kind/tooling patch. Compile/proof только разрешённый GCB, не локально.

| Пакет | Exact rows | Резерв | Compile-error repair |
|---|---|---:|---|
| G1 | два новых fixed-route roots | `(2×10+30)×$0.0135=$0.675` | G1R, те же2 rows, $0.675 |
| G2 | только прежний pair N31 | `(10+30)×$0.0135=$0.540` | G2R, та же1 row, $0.540 |

G2 — matching resource baseline в свежем Build; результат baseline не должен отнять память у candidate G1.
Запускать после terminal/accounting G1/G1R, независимо от его proof-исхода, при актуальных полномочиях/бюджете/окне.
Compile error сначала исправить статически, единственный repair этого пакета с новым review/GO.
При повторном compile blocker не посылать заведомо некомпилирующийся следующий пакет: HANDOFF/NOT_RUN.
TIMEOUT/OOM/semantic/coverage failure не разрешает retry того же пакета, RAM/timeout/input changes или новый split.
Максимум G1,G1R,G2,G2R; неизменённый failing compile input не повторять.

Общий плановый reserve **$1.215**; все4 резерва **$2.430≤cap$2.50**.
Перед каждым GO: own fact_spent+полный reserve следующего пакета≤cap, global cap/remaining/reservations/deadlines
позволяют; source/project slots проверить через существующий coordinator. Project≤2 queued/running/unresolved,
≤1 на stable owner. Unknown submission сначала разрешить; не дублировать. Чужие расходы/UUIDs не присваивать.
Бюджеты будущих стадий и текущих U64-TEN-CALLER/PARTTWO-TREE сохраняются отдельно.

G1/G2 публиковать на **одном frozen library tree**, tooling/profile identities те же; request/research metadata
могут иметь разные full source SHA. Если compile repair меняет library, заново проверить applicability уже
полученных результатов: original helper/macros/runtime и доказанный candidate dependency closure неизменны.
При изменении их semantics старый результат не proof нового кандидата; общий вывод PARTIAL/UNVERIFIED,
без автоматического повторного proof вне compile-error веток.

PRE-BUILD: diff/domain-union explanation, actual dispatch map, F/type/backing/scratch/panic scope;
roots/annotations/covers table, preservation ordinary202/other opt-ins, exact static-name delta;
source/library/tree/request/Kani/nightly/tooling hashes, check-tooling, pfc_order/target ordering,
static rustfmt/whitespace, own/global budgets/slots/window. Library/research commits отдельно `[skip ci]`,
reviewed packet publish без force. Ожидание `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD`
в фоновом Bash task Claude Code; без Codex watch/CODEX_THREAD_ID/polling-субагентов/новых сессий.

## Gate и результат

**Candidate proof gate:** оба G1/G1R roots SUCCESS,0 unexpected failures, covers2/2 каждый,
source/domain union/pins match, runtime/ordinary/checks restrictions сохранены. Baseline gate отдельно:
G2/G2R SUCCESS/3 из3 covers либо точный TIMEOUT/OOM/UNKNOWN. Baseline resource failure не превращать
в counterexample и не переписывать его автоматический gate; candidate evidence остаётся отдельным.
Если один новый root не прошёл — весь исходный pair-domain новым набором не закрыт.

Performance: сравнить max VT двух частей с baseline VT, их сумму отдельно, CBMC RSS и compiler/driver/process-sum
по каждому Build. Новый GCB screening target — max VT примерно≤300s с заметным запасом RAM; это ориентир отбора,
не доказательство macOS readiness. Без завершённого matching baseline нет измеренного speedup.
Не складывать peaks разных Builds; TIMEOUTcap600 не VT, отсутствующие поля UNKNOWN.

`RESULT-PART2-SPLIT31.md` ≤35 строк: reviewed/build/request/library/tool identities, exact domains/union,
per-row statuses/checks/covers/VT/RSS, candidate gate и baseline gate отдельно, own spent/reserved,
сравнение max/sum и ограничения. Если baseline не прошёл, написать CANDIDATE_PASS/BASELINE_TIMEOUT или иной
точный составной статус, не общий automated PASS. Ordinary202 остаётся текущей подачей;
новые roots — opt-in candidates. **MacOS/jobs3/600s с запасом400–450s ещё OPEN** до отдельно разрешённого
owner v7 решения и полного organizer CI обеих ОС на exact tree; не запускать его в этой стадии.

K-1 evidence только bounded summaries/rows/peaks/разрешённые targeted excerpts; raw archives/full logs/
Cloud Logging/credentials/hidden configs и competing code не читать. Исторические results/ledgers не переписывать.
Никаких Actions dispatch/deploy/PR submission, новых dependencies или service changes.
Маркеры `REVIEW REQUEST <sha>` / `PART2-SPLIT31 ЗАВЕРШЁН`; одна стадия, затем стоп.

## Уточнение координатора (приоритет)

Owner этой стадии — **k1-network** (U64-TEN-CALLER terminal, слот свободен), а не k1-merge: PARTTWO-TREE (k1-merge) ещё идёт.
Ждать terminal PARTTWO-TREE не нужно; project ≤2 unfinished Builds, ≤1 на owner — проверить перед каждым dispatch.
