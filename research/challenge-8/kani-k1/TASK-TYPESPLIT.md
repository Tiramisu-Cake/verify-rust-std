# TYPESPLIT — фаза B4: разбиение пар N31/32 матрицы типов по маршруту и длине

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-typesplit**, ветка **experiment/kani-k1-typesplit-20261103** от
  **0d33d29f0e** (TYPEMATRIX: v6 + tooling e8e238db9d + opt-in `network::typematrix`).
- Slug **typesplit**, stable owner **k1-network**. Новые stage/ledger/UUID/request_id `typesplit-*`.
- Project cap **$93.96**, свой cap **$2.05**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Tooling base для check-tooling: e8e238db9d.
- Окно: main 150 + closeout 30 мин.

## Контекст

TYPEMATRIX
([RESULT](https://github.com/Tiramisu-Cake/verify-rust-std/blob/0d33d29f0e/research/challenge-8/kani-k1/RESULT-TYPEMATRIX.md)):
10/10 SUCCESS. При этом три pair-root `*_n31_32` для `(u8, u32)`, u128 и `[u8; 9]` заняли 452–538 с и 6.5–6.8 GiB.
Это выше ориентира v7 ≤ 300 с. Делим каждый на 4 корня: маршрут × длина.

## Source scope

Только `verify/network/typematrix.rs`: дописать 12 roots существующим локальным `dispatch_safety_cases!`
(single-route, тот же stub, unwind 65, scratch 48, `volatile_reading_less`). Существующие 10 roots, макросы,
`ArbitraryValue` и const-проверки не менять.

| Тип | Roots |
|---|---|
| `(u8, u32)` | `dispatch_safety_stable_u8u32_n31`, `_stable_u8u32_n32`, `_unstable_u8u32_n31`, `_unstable_u8u32_n32` |
| `u128` | `dispatch_safety_stable_u128_n31`, `_n32`, `dispatch_safety_unstable_u128_n31`, `_n32` |
| `[u8; 9]` | `dispatch_safety_stable_bytes9_n31`, `_n32`, `dispatch_safety_unstable_bytes9_n31`, `_n32` |

Вместе 12 roots покрывают те же клетки «тип × маршрут × длина», что три pair-root. В PRE-BUILD показать это
соответствие и разницу covers: у pair-root covers по маршрутам, у single-route — по длине и family end.

Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta (+12);
- rustfmt;
- без warnings.

## Пакет

12 строк, measurement, expect SUCCESS:
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (12×10+30)×$0.0135 = **$2.025**.

Project ≤ 2 unfinished, ≤ 1 на k1-network. Параллельно может идти WRAPEIGHT (k1-merge). Перед dispatch проверить:
global spent + все reserves ≤ $93.96. Если не помещается — стоп и ко мне, состав не сокращать самому.

PRE-BUILD: соответствие клеток, hashes, budget. Коммиты library/research отдельно, `[skip ci]`, push без force.
`PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в фоне.

## Gate и RESULT

**Gate root.** SUCCESS, 0 failures, все covers. TIMEOUT/FAILED — bounded facts, без retry и дальнейшего split.
Настоящий counterexample — немедленно мне.

**RESULT-TYPESPLIT.md**, ≤ 30 строк:
- таблица 12 строк: status, VT, checks, unreachable, covers, CBMC RSS;
- какие клетки N31/32 получили корень ≤ 300 с;
- итоговый список v7-кандидатов матрицы типов: 7 из TYPEMATRIX и прошедшие отсюда.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **TYPESPLIT ЗАВЕРШЁН**, одна стадия, затем стоп.
