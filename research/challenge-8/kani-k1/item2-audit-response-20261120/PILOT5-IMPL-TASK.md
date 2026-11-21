# Кампания 5 q-пилота: измерительный пакет P-2 (воркер, 2026-11-21)

Основание: `PILOT-RUN4-ANALYSIS.md` (§«Одна измерительная кампания») — решение координатора: реализовать ровно эти пять корней.

## std

Worktree `/root/verify-rust-std-ch8-q-pilot-v1`, новый коммит поверх `c59b0d2a21c84bcf9786cd2b4c4c152be23588ae`. Только verification-модули (`smallsort/verify/…`), runtime `smallsort.rs` не трогать (кроме, если неизбежно, verification-only атрибутов — тогда обосновать).

1. `P-2b-OB11` — существующий `p2b_sort13_u8_b01_len17_q_any_actual_swaps` без изменений (отличие только в argv).
2. `D13-BODY-V34` — plain `#[kani::proof]`, прямой вызов actual `sort13_optimal(&mut v[1..18], &mut f)` с actual swaps; до вызова явная проверка len/active и `prefix_capture`, после — `prefix_post`, `P2_ORDER_QPOST`, q-frame, V34 frame, те же covers.
3. `D13-CHECK-V19` — тот же PFC, что P-2b, но backing `[u8; 19]`, тот же `v[1..18]`, по одному canary с каждой стороны, тот же q-пост и хвост.
4. `D13-CHECK-P17` и 5. `D13-CHECK-P31` — verification-only функции с первыми 17 и 31 реальными вызовами `swap_if_less` в том же порядке и с теми же литеральными парами, что в `sort13_optimal` (сверить статически с call sites), с контрактом той же формы: modifies первых 13 байт, q-frame, сохранение `count_ones` пороговой маски и байтового хвоста; PFC на V34/base1/len17, тот же внешний frame и covers.

Метки ролей уникальные по корням. rustfmt check-only как раньше.

## control

Новая ветка от `experiment/ch8-q-pilot-control-v4`, коммит с parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Roster из пяти корней в порядке 1–5; per-root `object_bits` (11 для первого, 12 для остальных) и per-root timeout (600 с для первого, 180 с для остальных), согласованные в Kani argv (`--harness-timeout`, `--cbmc-args --object-bits N`), внешнем child cutoff и расчёте latest start; local cap 6 GiB, outer 12, reserve 2. Записывать per-root object bits и timeout в raw index. Тесты на roster/лимиты/ошибочные значения; validate, check-source, test_run.py локально.

Без cargo, rustc, Kani, CBMC, CI и пушей. Коммиты `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Handoff `PILOT5-IMPL-HANDOFF.md` здесь, коммит в g0 `[skip ci]`.
