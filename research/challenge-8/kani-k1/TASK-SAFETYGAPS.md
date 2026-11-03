# SAFETYGAPS — фаза B2: dispatch bytes85/ZST и mutating Cell insertion N6..20 (существующие opt-in roots)

**Выдано координатором 2026-11-03; каждый dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-safetygaps**, ветка **experiment/kani-k1-safetygaps-20261103** от
  **e8e238db9d87323fa4da011a1a8b37fb76ec91c0** (v6 library tree d4ec476a7a + K-1 tooling + cap 93.96).
- Slug **safetygaps**, stable owner **k1-network**. Dispatch G1 только после terminal/accounting DIRECTBOUNDS (тот же owner). Новые stage/ledger/UUID/request_id `safetygaps-*`. Ledger ROUTESEF и DIRECTBOUNDS не
  возобновлять, чужие ledgers (WRAPMORE/PERMSOLVER, k1-merge) не трогать.
- Project cap **$93.96** (поднят владельцем до $95, commit e8e238db9d), свой cap **$1.65**. **Два плановых Build (G1, G2), retry нет.** Исключение — один
  compile-error repair на всю стадию с новым review/GO, если own spent + reserve ≤ cap.
- Окно: main 150 мин + closeout 30 мин, T0 при фактическом старте.

## Цель и exact rows

Измерить существующие opt-in roots v6, которые добавляют домены, не покрытые ordinary 202 (выбор согласован с планером):
- **dispatch**: тип bytes85 на N31 и ZST на перечисленных длинах — новые типовые ветви;
- **mutating Cell**: `Cell<TaggedKey>`, произвольные ключи/теги, comparator читает и меняет ключи, сохраняет теги и
  возвращает any bool. Ordinary покрывает N1..5 и все offsets N20; широкие roots ниже закрывают все offsets N6..19.

Source, harnesses и домены не менять. Plain-u64 insertion-корни **не берём**: ordinary уже покрывает N1..20 и все
offsets. Подмножества Cell (`n13_to15`, `n15`, `*_offset1`, `*_offsets*`) **не берём**.

| Пакет | Roots (`slice::sort::shared::smallsort::verify::network::`) | Ожидание |
|---|---|---|
| G1 | dispatch_safety_stable_unstable_bytes85_n31, dispatch_safety_stable_zst_n0_1_2_7_8_15_16_17_31_32, dispatch_safety_unstable_zst_n8_9_12_13_17 | SUCCESS каждая |
| G2 | mutating_insertion_safety_cell_n6_to10, mutating_insertion_safety_cell_n11_to15, mutating_insertion_safety_cell_n16_to20 | SUCCESS каждая |

Unwind — исходный (dispatch 65, Cell 35; сверить по source). Covers — полный reachable inventory каждого root, включая
normal-return каждой длины и cover мутации. Prognosis-расхождение — ко мне, covers не удалять.

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
- tooling base **e8e238db9d87323fa4da011a1a8b37fb76ec91c0** (= frozen 30f77e85 + только CAP_USD в k1g.sh), check-tooling против него.

Резерв каждого пакета **(3×10+30)×$0.0135 = $0.810**; вместе $1.620 ≤ cap $1.65.

**Порядок.**
1. G1: PRE-BUILD G1 → GO → dispatch → `k1g.sh wait BUILD` в фоне (run_in_background), завершить ход.
2. После terminal/accounting G1 — PRE-BUILD G2 (новый request_id, тот же source) → GO → dispatch.

G2 запускается **независимо от исхода G1**, кроме общего compile-blocker: тогда сначала один разрешённый repair.
TIMEOUT/OOM строки G1 не меняют состав G2.

**Лимиты проекта.** Project ≤ 2 unfinished Builds, ≤ 1 на k1-network. Параллельно идёт INTEGPAIRS (k1-merge).
Global spent + reserves ≤ $93.96.

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
- автоматически запускать новые пакеты или split-задания.

Настоящий counterexample/UB — немедленно сообщить координатору с bounded excerpt (property, location).

Оценка: ≤ 300 с GCB — рабочий shortlist для v7; ≤ 600 с — proof fit, macOS не доказывает. CBMC row RSS отдельно,
compiler/driver/process-sum по Build.

**RESULT-SAFETYGAPS.md**, ≤ 40 строк:
- identities обоих Build;
- таблица из 6 строк: status, VT, checks, unreachable, covers, CBMC RSS;
- packet peaks, own spent/reserved, gates;
- для каждого root — какой домен (тип × N × offset × маршрут) он добавляет к ordinary;
- кандидаты в v7 (≤ 300 с);
- для Cell-строк с TIMEOUT — план разбиения (n11_to12, n13, n14, offset-группы N15..19) без запуска.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.

Маркеры `REVIEW REQUEST <sha>` / **SAFETYGAPS ЗАВЕРШЁН**, одна стадия, затем стоп.
