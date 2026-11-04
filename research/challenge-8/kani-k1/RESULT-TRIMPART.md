# RESULT TRIMPART — Part 1 v7 (Claude Code, статически, без сборок)
Base `233f96f66ab3785881cead133817ed5db4c76b09`, v6 `d6b8caf7fe0e…` (library `d4ec476a7a`); head (кандидат v7, library-коммит)
`bd7fb8196e15fc78e2b252de5b4820cee0ad0632`, library tree `32ce0c62f6c2…`. Runtime `smallsort.rs` c0bd09c354→233f96f66a не менялся;
регистрация `mod verify;` и check-cfg в `Cargo.toml` — строка в строку как в v6.

| файл (строки: всего / ordinary-код / opt-in-код / комм.) | v6 | v7 |
|---|---|---|
| verify.rs | 41 / 7 / 2 / 31 | 51 / 7 / 2 / 41 |
| assembly.rs | 196 / 167 / 0 / 14 | 181 / 140 / 9 / 17 |
| merge.rs; merge/specfix.rs | 1239 / 684 / 370 / 85; 589 / 254 / 209 / 75 | 804 / 674 / 0 / 58; 413 / 254 / 63 / 59 |
| merge/specdiag.rs; mutations.rs | 136 / 0 / 109 / 14; 174 / 0 / 137 / 6 | удалён; 27 / 0 / 20 / 2 |
| network.rs | 1488 / 1064 / 235 / 77 | 1091 / 924 / 0 / 70 |
| types.rs / smoke.rs | 232+51 / 187 / 50 / 15 | 172+34 / 171 / 0 / 10 |
| wrap.rs, comparators.rs, smallsort.rs, Cargo.toml | 299 / 177 / 46 / 46 | без изменений |
| **итого** (+пустые 384 → 282) | **4445 / 2540 / 1158 / 363** | **3072 / 2347 / 140 / 303** |
## Контроли (cfg-on = 202 + 8 = 210)
Имена совпали с v6 без замен. 1 `assembly::reject_mutant_swap_u8_n2` — `check_swap` на `mutant_swap_if_less` (обращён обмен);
2 `specfix_full_value_checker_rejects_payload_change_u8` — реальный sort4 + флип payload, ловит full-value count; 3 `wrap::rejects_payload_corruption`
— trait-вход + флип, ловит count wrap-чекера; 4 `wrap::rejects_always_true` — always-true в трёх wrapper, ловит `canonical_guard`;
5–8 `specfix_wrong_f_{swap,sort4,insert,merge}_rejected_*` — `stub_verified` профиля с always-true F, ловит requires `specfix_canonical_comparator`.
## Удалено (уходит в Part 2, добавлением кода)
174 opt-in корня (network 85, merge 64, specdiag 7, types 7, specfix 5, assembly 4, smoke 2; список
`trimpart/moved-to-part2.txt`), файл `specdiag.rs`, 4 мутанта из 5, осиротевшие helpers/imports: `scratch_view` (в v6 cfg-off
сирота под `allow(dead_code)`), `insert_tail_len`, `lt_b85`, `zst_less`, `merge_safety_body_u64`, `impl ArbitraryValue for ()`,
specfix raw/oracle helpers, import `VALUE_PROBE_BYTES…`, второй arm `trait_cases`. `should_panic` и новых `allow` нет. Split:
`paired_case` → `original_case` + прямой `reject_mutant_swap_u8_n2`; `insertion_offset_group_cases` → `_u64_case`/`_cell_case`.
## Проверки (`trimpart/check_trimpart.py`, отчёт `trimpart/check-report.json`, статус PASS)
1. Ordinary cfg-off = v6 = 202 (36 PFC), совпадает с MACSPLIT G1 inventory (202). 210 корней (202 + 8) и 280 транзитивных
   items совпадают с v6 по токенам после раскрытия `macro_rules` (39 корней из split-макросов — тоже); изменены только
   module docs и комментарии; `impl ArbitraryValue for ()` удалён: unit-типа нет ни в одном оставшемся корне network.
2. cfg-on − ordinary = ровно 8 имён выше; 5 мутаций проверки (тело, unwind, сирота, контроль, лишний корень) ловятся.
3. Ссылок на 204 удалённых имени, `specdiag`, неразрешённых `mutations::` нет; сирот/лишних imports/arms нет в cfg-off/on (v6: 1/3).
4. rustfmt `--check` (wrapper, edition 2024) rc=0 на 10 файлах; `git diff --check` rc=0; строк > 100 нет.
5. Diff против `233f96f66a`: только verify*, 5 строк `smallsort.rs`, 2 строки `Cargo.toml` (+ research); runtime-строк нет.
6. Строки: 4445 → 3072 (opt-in-код 1158 → 140). Ordinary-код 2540 → 2347 без изменения корней: в v6 смешанные макросы
   (negative arm `paired_case`, 23 cell-строки `insertion_offset_group_cases`), сирота `scratch_view` и arm `trait_cases` считались ordinary.
## Не проверено без компиляции
Разрешение имён/типов, раскрытие rustc и гигиена макросов, отсутствие warnings (в merge/network остался `#![allow(dead_code)]` v6),
`kani list`, исход 8 контролей и SUCCESS ordinary на pin `cd355b0b`/nightly-2026-10-22 — следующая стадия.
