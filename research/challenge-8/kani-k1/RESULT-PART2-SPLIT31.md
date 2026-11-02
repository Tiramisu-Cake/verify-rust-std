# RESULT PART2-SPLIT31 — bytes17 N31 safety pair разделён на Stable/Unstable roots: CANDIDATE_PASS / BASELINE_PASS

Owner k1-network, Claude Code; ветка `experiment/kani-k1-partsplit-20261102`, база MACSPLIT `4f4034527d`.
Library commit `b2a13747dae7`, tree `05eb97eaef01dc4015e659d46256b2d910750d58` — один и тот же для G1 и G2.
Tooling `30f77e85` (check-tooling ok оба Build), Kani `9461e07a`, nightly-2026-10-12; GCB k1-standard4, jobs1, controls on,
uninit off, 10 мин/row. Reviewed: G1 GO `52c9be6c` (PREBUILD.md), G2 GO `041d904f` (G2-PREBUILD.md).
Diff: +4 строки `verify/network.rs`, два `#[cfg(kani_smallsort_controls)] dispatch_safety_cases!` (`[u8;17]`, STABLE true/false, `[31]`);
исходный pair root, макросы, `dispatch_safety_fixed`, runtime не изменены. Static: ordinary 202=202 (set-equal macsplit ref),
cfg-on 384→386 (+2 точных имени), opt-in 182→184, PFC 36, pfc_order bad 0; native inventory этой стадией не запускался.

Domain: pair = `stable: any bool` × `dispatch_safety_fixed::<[u8;17],31,stable>`; Stable root = stable=true, Unstable = false,
каждый с полным входом (31 init, 17 full-any bytes), F `volatile_reading_less::<[u8;17]>` fn item, scratch 48, stub
panic→assume_order_violation, unwind65. Union = домен pair. Route: оба случая — general (Stable `small_sort_general_with_scratch`,
Unstable `small_sort_general`; не network, size 17 > 8).

| Build / request | Row (network::) | Status | Checks | Covers | VT s | CBMC peak |
|---|---|---|---|---|---:|---:|
| G1 ce83c352 / partsplit-g1-… (57bf1824) | dispatch_safety_stable_bytes17_n31 | SUCCESS | 0/368 | 2/2 | 113.3 | 1.64 GiB |
| G1 ce83c352 | dispatch_safety_unstable_bytes17_n31 | SUCCESS | 0/368 | 2/2 | 167.4 | 2.38 GiB |
| G2 488092c0 / partsplit-g2-… (2b516f70) | dispatch_safety_stable_unstable_bytes17_n31 | SUCCESS | 0/370 | 3/3 | 237.9 | 4.00 GiB |

Per-Build process peaks (не складывать между Build): G1 compiler 1.57 / driver 0.71 GiB, max sampled RSS sum 2.90 GiB,
wall 5:55; G2 compiler 1.54 / driver 0.91 GiB, sum 4.45 GiB, wall 5:04. OOM нет в обоих.

**Candidate gate: PASS** — оба новых root SUCCESS, 0 failures, covers 2/2 каждый, source/domain/pins совпадают.
**Baseline gate: PASS** — G2 SUCCESS, 3/3 covers (Stable return, Unstable return, family end).
Сравнение (matching, тот же tree/tooling): max VT 167.4 vs 237.9 с (−30%); сумма VT 280.7 vs 237.9 с (+18%);
CBMC peak 2.38 vs 4.00 GiB (−40%). Max VT ≤300 с с запасом RAM — GCB screening target выполнен.
Сходно с N32 (MACSPLIT: max −52%, сумма меньше), но здесь сумма больше baseline.

Own: 2 Build из 4; spent $0.1755 + $0.1620 = **$0.3375** ≤ cap $2.50; reserved $0. G1R/G2R не нужны.
Ограничения: GCB jobs1 не прогноз macOS jobs3; новые roots — opt-in candidates, ordinary 202 остаётся текущей подачей.
MacOS/jobs3/600s с запасом 400–450 с — OPEN до решения owner v7 и полного organizer CI обеих ОС на exact tree.
Отдельного native inventory/повторного proof не было; формальный scope — normal-return safety с panic cut, без sorting claims.
