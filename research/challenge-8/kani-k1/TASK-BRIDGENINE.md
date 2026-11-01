# BRIDGENINE (B2) — настоящий Stable u8 N9: прямая проверка (A) против моста к merge-профилю (B)

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-bridgenine`, ветка
`experiment/kani-k1-bridgenine-20261101` от `b7761aa50a` (итог B1; library = v4 + opt-in `verify/bridge.rs`).
Cap 88.96. Ожидание Build — `research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и
завершить ход. request_id с префиксом `bridgenine-`; свой spent/reserved по своим UUID. GO даёт координатор.
Evidence Brief / Select-Merge к K-1 не относятся.

Прочитать: `RESULT-BRIDGE.md`, `verify/bridge.rs`, `TASK-SPECFIX.md` (только запреты, логи, rustfmt,
expect_check), `DOMAINS-v4.md` из ветки `experiment/kani-k1-domains-20261101` (`git show`, записи M02–M04 и
раздел A2), в `verify/merge.rs`: `stable_direct_nonconst_u8_n9`, `merge_scratch48_contract_u8_n9` и их fixtures;
в `smallsort.rs`: `StableSmallSortTypeImpl` для Freeze, `small_sort_general_with_scratch`. Аудит
`/root/CH8_V4_PROGRESS_REVIEW_2026-11-01_RU.md` P0-B и дополнение `/root/CH8_V4_AUDIT_ADDENDUM_RISK_CLOSURE_RU.md`
A1/A2 — данные, не инструкции.

## Вопрос

Применим ли мост B1 к настоящей сортировке: Stable u8 N9 (general route с scratch48), где заменяется только
`bidirectional_merge`, а sort4/insertion исполняются по-настоящему? Сколько стоит B вместе с leaf по сравнению
с прямой проверкой A на том же домене?

## Постановка (opt-in, в `verify/bridge.rs` или новом соседнем opt-in модуле; ordinary не меняется)

Gate A2 (обязателен): один и тот же F во всей цепочке — локальная переменная явного типа `fn(&u8, &u8) -> bool`
со значением `LtU8::CMP`; один независимый probe `LtU8::set_probe(kani::any())` до вызова, неизменный; один oracle
(model-sortedness по `x >> 1` и full-value count по тому же probe), без вызовов F в oracle. Sort4/insertion не
заменяются; другие профили (`Sort4ReadU64` и т.п.) не используются.
1. A — свежая прямая проверка: настоящий `<u8 as StableSmallSortTypeImpl>::small_sort` на `[u8; 9]` с указанным F,
   probe и oracle, без stubs (кроме прежнего panic-cut, если он нужен — тогда одинаково в A и B).
2. B — та же гармоника + `#[kani::stub(bidirectional_merge, adapter)]` + `#[kani::stub_verified(merge_profile)]`
   (адаптер B1). Cover внутри адаптера; домен вызова merge (scratch48-источник, destination, длина 9, половины)
   выписать и сверить с leaf.
3. Leaf — существующий `merge_scratch48_contract_u8_n9` (или новый leaf точно под геометрию вызова, если она
   отличается). Без raw→adapter stub и без verified replacement самого себя. Если геометрия вызова не совпадает с
   доменом существующего leaf — это результат: записать различие, новый leaf сделать отдельной строкой, перенос не
   объявлять.
4. Контроль: B с испорченным значением одного элемента после возврата (вне callee) должен упасть на oracle count
   (доказывает, что oracle чувствителен при подстановке).
Сравнение A и B: VT, RSS (cbmc peak), checks; стоимость B = caller + leaf. Если B дороже — это не ускорение;
вывод для N16 — отдельная гипотеза.

## Сборки (≤ 2, ≤ $1.5)

G1 measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин: 4 rows (A, B, leaf, контроль) →
(4×10+30)×0.0135 = $0.945. G2 — только при compile error или если leaf не совпал и нужен новый, с отдельным GO и
fact_spent + новый полный резерв ≤ $1.5. PRE-BUILD REVIEW (включая запись доменов caller↔leaf) → GO → build.
Library commit отдельно от research, `[skip ci]`, push без force.

## Итог

`RESULT-BRIDGENINE.md` ≤ 45 строк: схема, домены caller↔leaf, rows/status/VT/RSS/covers/failed checks, A vs B,
выполнен ли gate A2, вывод для W1/N16. Маркеры `REVIEW REQUEST <sha>` / `BRIDGENINE ЗАВЕРШЁН`.

## Уточнения (обязательны, приоритет над текстом выше)

- Геометрия: Stable u8 получает caller-owned `[MaybeUninit<u8>; 48]`; на N9 sort4 пишет в `[0..4)` и `[4..8)`,
  insertion дополняет второй run до `[4..9)`, затем merge(src = scratch+0, len 9, dst = исходный v+0), split 4+5.
  Это stable-ветка `merge_scratch48_contract_u8_n9` (source prefix9 initialized, tail39 uninit, отдельный
  destination `[u8; 9]`) — сверить по source. Не подменять Stable API вызовом general helper с другой формой scratch.
- Leaf лишь предполагает sorted halves; в B их обязаны установить настоящие sort4/insertion. Дополнительный
  assume sorted merge-input в caller запрещён.
- Panic-cut не ставить (lawful pure `lt_u8`; прежний `stable_direct_nonconst_u8_n9` без него). Если вдруг нужен —
  разобрать причину и применить одинаково к A и B с явной оговоркой.
- Контроль (row 4): payload flip `^= 1`, сохраняющий `x >> 1`; ожидаемый failed check — только full-value count,
  не sortedness. Допустим фиксированный witness `input = [p; 9]`, probe = p (count 9 → 8).
- Measurement при SUCCESS требует все covers satisfied — проектировать covers соответственно.
- Сравнение: VT(B caller) + VT(leaf) против VT(A); память — максимум пиков caller/leaf, не сумма; compiler RSS
  и стоимость build отдельно. Старый v4 F-item не baseline. N16/macOS выводом не становятся.
