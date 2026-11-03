# CELLSPLIT — фаза B2: mutating Cell insertion N11..19 существующими split-roots

**Выдано координатором 2026-11-03; каждый dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-cellsplit**, ветка **experiment/kani-k1-cellsplit-20261103** от
  **e8e238db9d87323fa4da011a1a8b37fb76ec91c0** (v6 library tree + K-1 tooling + cap 93.96).
- Slug **cellsplit**, stable owner **k1-network**. Новые stage/ledger/UUID/request_id `cellsplit-*`. Чужие ledgers не
  трогать.
- Project cap **$93.96**, свой cap **$3.60**. **До трёх плановых Build (G1, G2, G3), retry нет.** Исключение — один
  compile-error repair на стадию с новым review/GO, если own spent + reserve ≤ cap.
- Окно: main 300 мин + closeout 30 мин, T0 при фактическом старте. G2/G3 dispatch только если до конца main
  осталось ≥ строк×10+20 мин; иначе пакет не запускается и записывается как не запущенный по окну.

## Контекст

SAFETYGAPS
([RESULT](https://github.com/Tiramisu-Cake/verify-rust-std/blob/e6a0b17e1d1ca40f8a9c6c2337da3b82f176e603/research/challenge-8/kani-k1/RESULT-SAFETYGAPS.md)):
- `mutating_insertion_safety_cell_n6_to10` SUCCESS 142.6 с;
- `n11_to15` — CBMC status 6 через ~367 с, без verdict (RUNNER/CBMC_ABNORMAL_EXIT, OPEN);
- `n16_to20` — TIMEOUT.

Ordinary покрывает N1..5 и все offsets N20. В v6 уже есть более мелкие opt-in roots, покрывающие N11..19 по всем
offsets. Их и меряем. Source не меняем.

## Exact rows (`slice::sort::shared::smallsort::verify::network::`)

| Пакет | Roots | Строк |
|---|---|---:|
| G1 | mutating_insertion_safety_cell_n11_to12, _n13, _n14, _n15_offsets1_to4, _n15_offsets5_to8, _n15_offsets9_to12, _n15_offsets13_to15 | 7 |
| G2 | _n16_offsets{1_to4,5_to8,9_to12,13_to16}, _n17_offsets{1_to4,5_to8,9_to12,13_to15,16_to17} | 9 |
| G3 | _n18_offsets{1_to4,5_to8,9_to12,13_to16,17_to18}, _n19_offsets{1_to4,5_to8,9_to12,13_to16,17_to19} | 10 |

Ожидание каждой строки — SUCCESS. В PRE-BUILD G1 по source подтвердить:
- offset-группы каждой длины N15..19 вместе дают ровно 1..=N, без пропусков;
- семантика split-roots совпадает с широким root: тот же тип `Cell<TaggedKey>` и backing, произвольные ключи/теги,
  `mutating_key_order`, вызов helper `insertion_sort_shift_left`, unwind 35; sorted-prefix assumptions нет. Длины,
  offsets и состав covers у разбиений различаются — это ожидаемо, перечислить.

Если расхождение найдено — стоп, ко мне. `*_offset1` (одиночные) и `n13_to15`/`n15` целиком **не берём**: они
перекрываются группами выше.

## Профиль и бюджет

Профиль measurement:
- gcb-e2-standard-4 → k1-standard4, 4 CPU / 16 GiB, swap off;
- controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10;
- Kani **9461e07af7ec929f050aa4192f29363c9be07779**, nightly-2026-10-12;
- tooling base **e8e238db9d**, check-tooling против него.

Резервы:
- G1 (7×10+30)×$0.0135 = **$1.350**;
- G2 (9×10+30)×$0.0135 = **$1.620**;
- G3 (10×10+30)×$0.0135 = **$1.755**.

Сумма максимальных резервов ($4.725) больше своего cap: план рассчитан на освобождение резерва после фактического учёта
G1/G2. Перед каждым dispatch: own spent + reserve ≤ $3.60, и global spent + все reserves ≤ $93.96. G3 условный: если
не помещается по бюджету или окну — не запускать, записать в RESULT как не запущенный.

Project ≤ 2 unfinished Builds, ≤ 1 на k1-network. Параллельно может идти UNSTABLEZST (k1-merge).

## Порядок

1. PRE-BUILD G1 (hashes, exact names, cfg/stub/unwind, covers, partition offsets, budget) → GO → dispatch →
   `k1g.sh wait BUILD` в фоне, завершить ход.
2. После terminal/accounting G1 — PRE-BUILD G2 (новый request_id, тот же source) → GO → dispatch. G3 так же после G2.

G2/G3 идут независимо от исхода G1. Исключение — CBMC status 6 на **≥ 4 из 7** строк G1: тогда стоп перед G2 и отчёт
мне. Abnormal exit — не counterexample.

Metadata commits `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <sha>`, затем стоп до GO.

## Gate, stop и RESULT

**Gate каждого root.** Identities/profile совпали; SUCCESS; 0 failures; все существующие declared covers root, включая
cover мутации. Отдельного cover на каждую пару (N, offset) не требуем: охват offsets даёт входной домен root.

TIMEOUT/OOM/FAILED/status 6/UNKNOWN — bounded facts своей строки, без retry. Нельзя:
- менять timeout/RAM/profile;
- делить дальше;
- запускать вне трёх пакетов.

Для status 6 — bounded `k1g.sh log-grep`, как в аддендуме SAFETYGAPS. Настоящий counterexample — немедленно мне с
bounded excerpt.

**RESULT-CELLSPLIT.md**, ≤ 40 строк:
- identities Build;
- таблица до 26 строк: status, VT, checks, unreachable, covers, CBMC RSS;
- packet peaks, own spent/reserved, gates;
- итог покрытия: какие (N, offset) из N11..19 доказаны, какие OPEN;
- кандидаты в v7 (≤ 300 с).

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **CELLSPLIT ЗАВЕРШЁН**, одна стадия, затем стоп.
