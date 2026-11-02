# DOMSIX — перепривязка публичного реестра доменов контрактов к Part 1 v6

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-domsix`, ветка
`experiment/kani-k1-domsix-20261102` от DOMFIVE `45f6e7f7cc`. **Без GCB Builds и без CI**: только Python stdlib и
чтение Git. Evidence Brief / Select-Merge к K-1 не относятся. Код конкурирующих PR не открывать.

## Контекст

Part 1 v6 = `submission/ch8-smallsort-part1-v6` @ `d6b8caf7fe` (library tree `b578183b92895f7792fbbda7b5dda54f453bd9ec`;
одиночный коммит на upstream `c0bd09c354`). Отличие от v5 `5a3009b065` — только `verify/network.rs`
(см. `git diff 5a3009b065 d6b8caf7fe`):
- ordinary `dispatch_safety_stable_unstable_bytes17_n32` → `dispatch_safety_stable_bytes17_n32` +
  `dispatch_safety_unstable_bytes17_n32` (не PFC; домен — объединение);
- PFC `insert_tail_contract_u64_start1_tail13_to16` → `..._tail13_to14` + `..._tail15_to16` (тот же макрос/target).
Итого ordinary 200 → 202, ordinary PFC 35 → 36 (insert_tail 4 → 5), opt-in без изменений (cfg-on 382 → 384 статически).
Нативный inventory v6 без cfg: MACSPLIT G1 `cbce904f`, exact 202 — файлы
`research/challenge-8/kani-k1/macsplit/{g1.inventory-pages.txt,ordinary-expected.txt}` на ветке
`origin/experiment/kani-k1-macsplit-20261102` (взять в этот worktree через `git checkout <ref> -- <paths>`).
Cfg-on inventory v6 не собирался: 384 выводится статически (v5 G2 382 + 2 − 0 opt-in изменений); так и написать.
Организаторский CI v6 — все workflows зелёные с первой попытки:
Kani run https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41404150041 (ubuntu и macOS autoharness:
все 202 SmallSort harnesses SUCCESSFUL). Это заменяет плейсхолдер `<V5-KANI-RUN>`.

## Сделать

1. `SMALLSORT-CONTRACT-DOMAINS.md`, `domains/pfc-inventory.tsv`, `domains/README.md`, `domains/check_domains.py`
   перевести с v5 на v6: коммит в permalink'ах `5a3009b065` → `d6b8caf7fe`, tree, все номера строк
   `network.rs` (и в URL, и в видимых `network.rs:NNN`) пересчитать по фактическому файлу v6 (другие файлы не
   менялись — проверить); insert_tail 4 → 5 строк/записей, totals 35 → 36, 200 → 202, 382 → 384 (static).
   Домен insert_tail LtU64 begin1: tail 2..16 теперь в четырёх harnesses — исправить текст.
2. check_domains.py должен проходить на v6: inventory-членство ordinary по MACSPLIT G1 (202); controls — по
   статической выводимости (нет G2 v6) с явной пометкой в выводе; убрать/обновить v5-специфичные утверждения.
   Сохранить все прочие проверки (ссылки, совпадение `file:line`, имена в строках, ≤250 строк, без внутренних терминов).
3. Язык публичного отчёта — английский, нейтральный, без внутренних кодов/имён этапов, без приватных материалов.
   README (приложение) может остаться на русском, как в DOMFIVE.
4. Commit `[skip ci]`, push без force. Library не трогать.

## Итог

Короткий `RESULT-DOMSIX.md` (≤ 20 строк): что изменено, вывод check_domains.py, открытые вопросы.
Маркеры `REVIEW REQUEST <sha>` / `DOMSIX ЗАВЕРШЁН`. Один этап — затем стоп.
