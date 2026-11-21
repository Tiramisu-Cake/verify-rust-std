# Допуск координатора по кампании 9 (2026-11-21)

Основание: независимая офлайн-qualification `QUALIFICATION-RUN9.md` (воркер 14) по `QUALIFICATION-CHECKLIST.md`, run 44862241314 attempt 1, std `d968b9a8c341485e4df63ad852ac0806f37bb71b`, control trigger `d872e81f2f`, tool `0aac16ef62`.

**Допущены как bounded-результаты** (домен: `u8/KeyLess<u8>`, initialized V34, base 1 (P-1: base 0–20), полный байт, q:any, OFF-профиль без uninit/validity, 12 object bits, unwind 36, нормальный возврат; local cap 10 GiB):

- провайдеры: P-1 `Check(swap_if_less)`, P-3 `Check(insert_tail)`;
- network no-merge маршруты, plain-композиция на реальной `small_sort_network` с `stub_verified` P-1/P-3: **N2, N8, N9, N12, N13, N16, N17** — порядок и полное мультимножество (order-stat при всех q), q-frame, внешний byte frame;
- контроли N2/N13/N17-corrupt, P-5a, P-5b — квалифицированы как контроли; P-5b подтверждает правило отказа fixed-q провайдеру.

**Не допущены:** N01 (timeout 300 с).

Ограничения допуска: не контракт `sort13_optimal` (его `modifies` обоснован по исходнику, не Check); не generic T/F; не UB-классы uninit/validity/permission; не длины 3–7, 10, 11, 14, 15, 18–32; ресурсный профиль выше прежних 6 GiB. Исторические admissions S1–S4P3 не переписываются. Независимый B1/B2 credit не выдаётся этой записью.

Поправка к ledger: метки времени `~HH:MMZ` в строках q-пилота 2026-11-21 записаны по московскому времени, а не UTC (qualification нашла расхождение для кампании 9: фактическое окно child 03:45–04:22 UTC). Привязка строк — по SHA, tree, ref и run ID.
