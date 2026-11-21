# Кампания 7 q-пилота: композиция без Check sort13 (воркер, 2026-11-21)

Основание: кампании 3–6 — Check `sort13_optimal` (DFCC) даёт ~1 млн дизъюнктов на swap и не проходит ни на реальных swap, ни на 45 Replace; `--refine-arrays` не помогает. При этом plain-корень P-4 с `stub_verified` проходит (кампания 2).

Идея координатора: **не делать PFC для sort13 вообще.** Провайдеры уже есть: P-1 (PFC `swap_if_less`, SUCCESS) и P-3 (PFC `insert_tail`, SUCCESS). Потребитель N17 — plain `#[kani::proof]` на **реальном** `small_sort_network(&mut v[1..18])`, где реальный `sort13_optimal` исполняется своим телом, а его 45 вызовов `swap_if_less` и 4 вызова `insert_tail` заменены `stub_verified`. Runtime-код std не меняется; sort13 не нужен как провайдер; его безопасность памяти проверяется в этом же plain-корне обычными проверками Kani; frame — внешней проверкой V34.

## std

Worktree `/root/verify-rust-std-ch8-q-pilot-v1`, новый коммит поверх `c8b703918a40c03d5b889d3018d8d818a70c233f`, только `sorting_q_pilot.rs` (и при необходимости `sorting_q_controls.rs`):

1. `q13_plain_stub_swap` — plain proof, `#[kani::stub_verified(swap_if_less)]`, реальный `sort13_optimal(&mut v[1..18], &mut f)` на V34/base1, q any; пост `P2_ORDER_QPOST` (по маске префикса), q-frame, байтовый хвост и V34 frame, те же covers что у P-2 (уникальные метки).
2. `n17_plain_stub_swap_insert` — plain proof, `#[kani::stub_verified(swap_if_less)]` и `#[kani::stub_verified(insert_tail)]`, реальный `small_sort_network(&mut v[1..18], &mut f)` (внутри — реальные `sort13_optimal` и `insertion_sort_shift_left`); пост и covers как у P-4 (уникальные метки).
3. `n17_plain_qpost_corrupt` — контроль как P-5c для корня 2 (порча `[0;17]`, q=1, назначенная FAILURE с уникальной меткой).

unwind36, V34, полный байт, q:any. rustfmt check-only как раньше.

## control

Новая ветка от `experiment/ch8-q-pilot-control-v6`, коммит с parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Roster в порядке 1, 2, 3; object bits 12; без дополнительных CBMC-аргументов; child 600 с для каждого; cap 6/12/2 GiB. В request — новые std sha/tree и хеши. validate, check-source, test_run.py.

Без cargo, rustc, Kani, CBMC, CI и пушей. Коммиты `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Handoff `PILOT7-IMPL-HANDOFF.md` здесь, коммит в g0 `[skip ci]`.
