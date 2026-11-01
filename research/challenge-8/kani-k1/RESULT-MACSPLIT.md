# RESULT MACSPLIT — кандидат v6: разбиение двух медленных на macOS гармоник (подготовлено, CI не запускался)

Повод: CI v5 (Kani run 41343234520, attempt 1) — macOS autoharness 1945/1946, `dispatch_safety_stable_unstable_bytes17_n32`
CBMC timeout 600 с (v4 mac 189 с, v5 ubuntu 140 с; код v4=v5). Остальные workflows v5 зелёные.
Library commit `7650948bc6` поверх v5 (`e382287728`, tree cbe69760c8): только `verify/network.rs`, +5/−7.
- `dispatch_safety_stable_unstable_bytes17_n32` → `dispatch_safety_stable_bytes17_n32` + `dispatch_safety_unstable_bytes17_n32`
  (существующий макрос `dispatch_safety_cases!`, тот же `dispatch_safety_fixed`, stub, unwind65; домен = объединение).
- `insert_tail_contract_u64_start1_tail13_to16` → `..._tail13_to14` + `..._tail15_to16` (тот же макрос/PFC target).
Ordinary 200 → 202; PFC 35 → 36 (insert_tail 4 → 5). pfc_order: 16 sites, bad 0. rustfmt --check PASS.

| Build | Что | Итог | Стоимость |
|---|---|---|---|
| G1 cbce904f | inventory controls off | native exact 202 = macsplit/ordinary-expected.txt | $0.567 |
| G2 78bdbbf9 | measurement 4 новых, jobs1 | все SUCCESS, covers полные | $0.270 |
| B 3f1f39be (ветка macbase) | measurement 2 старых на v5, jobs1 | все SUCCESS, covers полные | $0.2565 |

| Гармоника (GCB e2-standard-4, jobs1) | VT, с | CBMC peak | checks / covers |
|---|---:|---:|---|
| old bytes17_n32 (пара Stable+Unstable) | 284.0 | 4.20 GiB | 0/370, 3/3 |
| new stable_bytes17_n32 | 110.8 | 1.70 GiB | 0/368, 2/2 |
| new unstable_bytes17_n32 | 137.1 | 2.50 GiB | 0/368, 2/2 |
| old insert_tail tail13_to16 | 367.0 | 2.84 GiB | 0/619, 6/6 |
| new tail13_to14 | 262.9 | 2.84 GiB | 0/619, 4/4 |
| new tail15_to16 | 218.3 | 2.85 GiB | 0/619, 4/4 |

Вывод: bytes17 — максимум VT −52%, пик памяти −40%, сумма меньше (248 < 284). insert_tail — максимум −28%, память
та же, сумма больше (481 > 367). Гипотеза о конкуренции за RAM на macOS (7 GB, jobs3) правдоподобна для bytes17,
не проверена. GCB jobs1 не предсказывает macOS jobs3; финальный gate — полный CI организаторов на дереве v6 (по
решению владельца). Ветка без submission-коммита; ordinary домены не сужены.
