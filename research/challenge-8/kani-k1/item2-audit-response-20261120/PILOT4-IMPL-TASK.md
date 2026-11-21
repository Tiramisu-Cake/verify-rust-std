# Кампания 4 q-пилота: P-2 на реальных телах swap (воркер, 2026-11-21)

Основание: кампания 3 (`run-44844623193/SUMMARY.md`) — P-2 с 45 Replace `swap_if_less` упёрся в 9 GiB до первой CNF. По `PILOT-RUN2-ANALYSIS.md` следующий вариант — тот же PFC `sort13_optimal` без `stub_verified(swap_if_less)`, cap 6 GiB. Решение координатора: принять.

## std

Worktree `/root/verify-rust-std-ch8-q-pilot-v1`, ветка `experiment/ch8-q-pilot-v1`, новый коммит поверх `0e9b28b293f4360b005d33583d2cf9ac06d1790b`.

- В `sorting_q_pilot.rs` добавить **новый** корень `p2b_sort13_u8_b01_len17_q_any_actual_swaps`: тот же fixture, домен, assertions, covers и метки, что у P-2 (общий helper допустим, если P-2 остаётся побайтно эквивалентным по семантике), атрибуты `#[kani::proof_for_contract(sort13_optimal)]` и `#[kani::unwind(36)]`, **без** `stub_verified`. P-2 не удалять и не менять.
- Остальные файлы не трогать. rustfmt check-only как раньше.

## control

Worktree `/root/kani-ch8-q-pilot-control-v1`, новая ветка от `experiment/ch8-q-pilot-control-v3` (`b716a7f821`), новый коммит с parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Roster — один корень `P-2b` с селектором `slice::sort::shared::smallsort::verify::sorting_q_pilot::p2b_sort13_u8_b01_len17_q_any_actual_swaps`, normal cfg, прежний argv, unwind36, child 600 с, **local RSS cap 6 GiB**. В request — новые std sha/tree и SHA-256 изменённого std-файла; тесты обновить под roster; validate, check-source, test_run.py локально.

Без cargo, rustc, Kani, CBMC, CI и пушей. Коммиты `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Handoff `PILOT4-IMPL-HANDOFF.md` здесь, коммит в g0 `[skip ci]`.
