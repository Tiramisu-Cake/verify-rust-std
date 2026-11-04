# RESULT LOOPINV — loop contract внешнего цикла `insertion_sort_shift_left` (E2, диагностический пилот)

Build `c151dc31-7bb8-4cfb-8b63-c685c65192a5` (FAILURE), head `b64d6f6a86`, library `3e07b5d1ef`, tooling `b1242ef7fa`
(check-tooling exit 0), Kani `9461e07a`, CBMC 6.11.0, request sha `0f084bc6…9492`, gcb-e2-standard-4, controls on, jobs 1.
Компиляция core с атрибутом прошла (`Finished`, `[-]> .*smallsort`/`^error` — no match). Receipts: `loopinv/build.*`.

| # | Root | Ожидание | Статус | Окно row, s | CBMC peak RSS (≥, s от старта row) | Checks/covers |
|---|---|---|---|---|---|---|
| 1 | `loopinv_insertion_u64_n2_offset1` | SUCCESS | TIMEOUT | 1283–≈1884 (конец run) | 14.99 GiB (263) | — |
| 2 | `loopinv_copy_true` | SUCCESS | TIMEOUT | 675–1283 | 14.81 GiB (186) | — |
| 3 | `loopinv_copy_false_control` | FAILED (invariant step) | TIMEOUT | 66–675 | 14.91 GiB (176) | — |
## Gates
Lane gate: False (COMPLETE, expectation_met False, Kani exit 1). Ручной вердикт: **механизм не засчитан, 0/3**.
Исход — отдельный непринятый TOOL-RESOURCE: CBMC каждой row за 3–4.5 мин доходит до ~15 GiB (машина 15.63 GiB, swap
off), дальше samples почти не снимались (356 за 1884 s вместо ~942; пики — нижняя граница), до таймаута 600 s ни одного
property-результата (terse: `CBMC failed`/`CBMC timed out`). dmesg OOM none_seen; `time -v` max RSS 15751956 KiB;
kani-compiler 1.57 GiB, goto-instrument (DFCC) 0.60 GiB — инструментирование завершалось, CBMC стартовал.
## Вывод
Атрибут на реальном цикле на пине компилируется, но loop-contract путь (`--dfcc --apply-loop-contracts`) для harness
core std-сборки **непроходим по памяти** — включая тривиальные копии цикла на `[u64; 2]` без `insert_tail` (roots 2–3).
Гипотеза (bounded-evidence причину не устанавливает): узкое место — стоимость DFCC-модели целого harness в core, а не
`insert_tail` или инвариант. Ни инвариант, ни контроль 3 этот Build не проверил. Unbounded safety не заявляется.
## Что дальше потребовалось бы для unbounded safety
- Сначала сделать DFCC-путь проходимым: изолированный малый harness / диагностика, на чём растёт CBMC (вне этой стадии).
- Внутренний цикл `insert_tail` (`loop` со `sift`): свой loop contract (`begin ≤ sift < tail`, gap = sift/sift+1,
  modifies `begin..=tail`) или доказанный generic contract `insert_tail` (сейчас только closed profiles, merge::specfix).
- Внешний цикл: тот же инвариант + replace/summary `insert_tail` вместо тела; затем остальные циклы маршрутов
  (sort4/sort8/network-ветви, bidirectional_merge, `small_sort_general` и копирование scratch) — каждому свой контракт.
## Деньги
Own spent **$0.513** (cap $0.90; retry нет, compile-repair неприменим). Проект: used $92.7960, reserved $1.3500 (чужие), cap $98.96.
