# Кампания 15 q-пилота: провайдер sort9 на 11 object bits (воркер, 2026-11-21)

Основание: кампания 14b (`run-44883003487/SUMMARY.md`) — потребители N18/N19 со сводкой sort9 SUCCESS, но `Check(sort9_optimal)` с 25 Replace swap упёрся в 10 GiB до CNF. У Check sort13 переход на 11 object bits снял проблему памяти (кампания 5). Решение координатора.

## std

Worktree `/root/verify-rust-std-ch8-q-pilot-v1`, новый коммит поверх `ad2c458a679bcf55691e5a208adc8d27ca3e31c3`, только verification-модули. Добавить три корня-близнеца существующих `md_sort9_left_b01_len09`, `md_sort9_right_b10_len09`, `md_sort9_right_b10_len10` **без** `stub_verified(swap_if_less)` (реальные swap; суффикс `_actual_swaps`), с теми же fixture, assertions, covers и уникальными метками. Контракт `sort9_optimal` не менять.

**Правило формы контрактов (две ошибки компиляции подряд в кампаниях 12 и 14):** любые `ensures` с `old(...)` на `&mut`-аргументе — одним `ensures` (условия через `&&`), как у `sort13_optimal`; всё, что попадает в `old(...)`, должно быть `Clone`. Сверить новые атрибуты с уже компилировавшимися образцами и указать образец в handoff.

## control

Новая ветка от `experiment/ch8-q-pilot-control-v14b` (`c01bf94117`), коммит с parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Roster по порядку, cap 10 GiB, child 600 с, **object bits 11 для всех**:

1–3. `MD-SORT9-L1-OB11`, `MD-SORT9-R9-OB11`, `MD-SORT9-R10-OB11` — существующие корни с Replace swap.
4–6. `MD-SORT9-L1-ACT-OB11`, `MD-SORT9-R9-ACT-OB11`, `MD-SORT9-R10-ACT-OB11` — новые корни на реальных swap.
7–9. `MD-NETWORK-N18-OB11`, `MD-NETWORK-N19-OB11`, `MD-N19-QPOST-CORRUPT-OB11` — существующие потребители и контроль.

validate, check-source, test_run.py локально. Без cargo, rustc, Kani, CBMC, CI и пушей. Коммиты `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Handoff `PILOT15-IMPL-HANDOFF.md` здесь, коммит в g0 `[skip ci]`.
