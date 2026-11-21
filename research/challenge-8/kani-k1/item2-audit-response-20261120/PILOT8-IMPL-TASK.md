# Кампания 8 q-пилота: N17 plain с local cap 10 GiB (воркер, 2026-11-21)

Основание: кампания 7 (`run-44856804576/SUMMARY.md`) — N17 plain дошёл до решателя и упёрся в 6 GiB. Изменяется только control; std `1b82e2a9a70f0712986fab263c5e336e6edef3ca` без изменений.

Новая ветка от `experiment/ch8-q-pilot-control-v7` (`bc7fb06c39`), коммит с parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Roster: `N17-PLAIN-STUB-SWAP-INSERT`, затем `N17-PLAIN-QPOST-CORRUPT` (те же селекторы, 12 бит, без доп. CBMC-аргументов, child 600 с). **Local RSS cap 10 GiB** (`10485760` KiB); outer 12 GiB, reserve 2 GiB и правило `effective=min(local, min(12 GiB, A−2 GiB))` без изменений; nominal и effective в raw index. Тесты под roster/cap; validate, check-source, test_run.py.

Без cargo, rustc, Kani, CBMC, CI и пушей. Коммит `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Handoff `PILOT8-IMPL-HANDOFF.md` здесь, коммит в g0 `[skip ci]`.
