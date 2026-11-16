# TASK — worker15: E (insertion произвольной длины) — статический design spike (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Контекст: план пункта 1 v2, §6 «E» ([PLAN-CH8-ITEM1-REMAINING-v2.md](PLAN-CH8-ITEM1-REMAINING-v2.md)),
ROADMAP §5 (E: 15 — invariant/control design; 13 — core integration). A1-R3 запущен координатором
(run 43779285270); его intake — отдельная стадия позже.

База: std P′ `c5ff36ff433692140605891f646043f991db05de` (P′ = #752 head + upstream main, nightly-10-23;
компилируется с Kani 0aac — подтверждено S1-02), tool upstream `0aac16ef62…` (+ отдельно SEL1 `14bc57fdb9`
для uninit ON). Только чтение и проектирование, без CI.

1. По исходникам Kani 0aac: что реально поддерживают loop contracts для pointer loop с hole/gap_guard
   (`loop_invariant`, `loop_modifies`, `loop_decreases`, quantifiers над raw pointer диапазоном,
   symbolic-length allocation без константного backing cap) и как havoc взаимодействует с uninit shadow
   (ON). Ссылки file:line на 0aac/SEL1.
2. Для `insert_tail` / `insertion_sort_shift_left` на P′: точные program points, invariants outer/inner
   loop (§6 пп. 3–4), frame, decreases, ZST-случай; где нужны правки в smallsort.rs (это делает 13 —
   дай compact patch proposal, сам файл не меняй).
3. Калибровочный план (§6 п. 1): минимальные harness/controls (base/step/frame/negative invariant,
   ON/OFF) и их oracles; оценка cost на root (600 s/6 GiB). STOP E — записать, если сработал.
4. g0 `kani3300/ch8-e/`: DESIGN.md, PATCH-PROPOSAL-13.md, CONTROLS.md, HANDOFF.md; коммит `[skip ci]`,
   author `Tiramisu-Cake <igkharin@gmail.com>` в команде. Последней строкой `READY <g0>` или `STOP <причина>`.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; без правок smallsort.rs.
