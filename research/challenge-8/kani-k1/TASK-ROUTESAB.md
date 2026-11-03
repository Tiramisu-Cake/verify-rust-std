# ROUTESAB — существующие general all-routes safety roots N9..15, 17 (пакеты A и B)

**Выдано координатором 2026-11-03; каждый dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-routesab**, ветка **experiment/kani-k1-routesab-20261103** от
  **969c94f8591d2aff08f671e53911e325b5cf529d** (terminal SAFETYNET; library tree d4ec476a7a = Part1 v6, K-1 tooling).
- Slug **routesab**, stable owner **k1-network**. Новые stage/ledger/UUID/request_id `routesab-*`. Ledger SAFETYNET не
  возобновлять, чужие ledgers (PERMPROBE, k1-merge) не трогать.
- Project cap **$88.96**, свой cap **$1.95**. **Два плановых Build (G1, G2), retry нет.** Исключение — один
  compile-error repair на всю стадию с новым review/GO, если own spent + reserve ≤ cap.
- Окно: main 150 мин + closeout 30 мин, T0 при фактическом старте.

## Цель и exact rows

Измерить прежние opt-in roots `merge::route_safety_all_routes_nN`, закрывающие normal-return safety трёх маршрутов
general/stable u64 для N 9..15 и 17. N2..8 и N16 уже ordinary. Source, harnesses и домены не менять.

| Пакет | Roots (`slice::sort::shared::smallsort::verify::merge::`) | Ожидание |
|---|---|---|
| G1 (A) | route_safety_all_routes_n9, _n10, _n11, _n12 | SUCCESS каждая |
| G2 (B) | route_safety_all_routes_n13, _n14, _n15, _n17 | SUCCESS каждая |

Историческая справка (другие деревья, не baseline): N9 34 с, N10 41 с, N12 43 с, N14 65 с; N11, N13, N15, N17 без
записанного результата.

Body — `all_upper_routes_safety_body::<N>` (`verify/merge.rs` около строки 370). Произвольный `route: u8` выбирает:
- 0 — direct unstable general u64;
- 1 — non-Copy Unstable general;
- остальное — Stable Freeze u64 со scratch `SMALL_SORT_GENERAL_SCRATCH_LEN`.

Компаратор — существующий `arbitrary_u64_order`. Атрибуты из `define_route_safety_harness!`:
`#[kani::stub(panic_on_ord_violation, abort_on_order_violation)]`, unwind 34. Перед GO прочитать их в pinned
source и выписать в PREBUILD.

**Covers.** До GO сверить полный reachable cover inventory каждого root: covers трёх route bodies и cover в stub. Если
прогноз не совпадает, показать расхождение координатору. Cover не удалять и ожидаемый total ради PASS не подменять.
Panic-stub cover не считать нормальным возвратом маршрута.

## Неизменное

- Library/runtime/harness bodies/annotations/covers, workflows/tooling/runner/pins не менять.
- Payload, comparator, routes и lengths не сужать. Assumed order, новые cuts и invariants не добавлять.
- Разрешены только свои task/request/PREBUILD/RESULT.
- Ordinary 202 / PFC 36 и static cfg-on 384 / opt-in 182 неизменны.
- Clean room: competing PR, их diff, код и ссылки не открывать.

## Пакеты, ledger и GO

Профиль measurement:
- gcb-e2-standard-4 → k1-standard4, 4 CPU / 16 GiB, swap off;
- controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10;
- Kani **9461e07af7ec929f050aa4192f29363c9be07779**, nightly-2026-10-12;
- frozen tooling **30f77e859903df14b442ff9294d4fbbd44827f20**, check-tooling против него.

Резерв каждого пакета **(4×10+30)×$0.0135 = $0.945**; оба вместе $1.89 ≤ cap $1.95.

**Порядок.**
1. G1: PRE-BUILD G1 → GO → dispatch → `k1g.sh wait BUILD` в фоне (run_in_background), завершить ход.
2. После terminal/accounting G1 — PRE-BUILD G2 (новый request_id, тот же source) → GO → dispatch.

G2 запускается **независимо от исхода G1**, кроме общего compile-blocker: тогда сначала один разрешённый repair.
TIMEOUT/OOM строки G1 не меняют состав G2.

**Лимиты проекта.** Project ≤ 2 unfinished Builds, ≤ 1 на k1-network. Параллельно идёт PERMPROBE (k1-merge).
Global spent + reserves ≤ $88.96.

**PRE-BUILD каждого пакета:**
- source/library/tree/request/tool hashes;
- exact names, cfg, stub, unwind, cover table;
- route map и scratch;
- library unchanged, ordinary set preserved;
- budget/slots/deadline.

Metadata commits `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <sha>`, затем стоп до GO.

## Gate, stop и RESULT

**Gate каждого root.** Identities/profile совпали; SUCCESS; 0 unintended failures; все required covers, включая
нормальный возврат **каждого из трёх маршрутов**.

TIMEOUT/OOM/FAILED/coverage/UNKNOWN — это bounded facts для своей строки, без retry. Запрещено:
- менять timeout, RAM или profile;
- делать split;
- автоматически запускать следующие пакеты C–F.

Настоящий counterexample/UB — немедленно сообщить координатору с bounded excerpt (property, location).

Оценка: ≤ 300 с GCB — рабочий shortlist для v7; ≤ 600 с — proof fit, macOS не доказывает. CBMC row RSS отдельно,
compiler/driver/process-sum по Build.

**RESULT-ROUTESAB.md**, ≤ 40 строк:
- identities обоих Build;
- таблица из 8 строк: status, VT, checks, unreachable, covers, CBMC RSS;
- packet peaks;
- own spent/reserved, gates;
- candidate-for-v7 flags;
- сравнение с исторической справкой (не как matched baseline);
- рекомендация по пакетам C–F: какие N, вероятно, нужно сразу дробить по маршрутам — по VT N13..17.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.

Маркеры `REVIEW REQUEST <sha>` / **ROUTESAB ЗАВЕРШЁН**, одна стадия, затем стоп.
