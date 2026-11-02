# DOMSIX — перепривязка публичного реестра доменов контрактов к Part 1 v6

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-domsix`, ветка
`experiment/kani-k1-domsix-20261102` от DOMFIVE `45f6e7f7cc`. **Без GCB Builds и без CI**: только Python stdlib и
чтение Git. Evidence Brief / Select-Merge к K-1 не относятся. Код конкурирующих PR не открывать.

## Контекст

Part 1 v6 = `submission/ch8-smallsort-part1-v6` @ `d6b8caf7fe` (library tree — см. «Уточнения»;
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

## Уточнения (обязательны, приоритет над текстом выше)

- Исправить library tree: `git rev-parse d6b8caf7fe:library` даёт **d4ec476a7a001363e58f19948c188a9c2078e370**, а не b578183b92895f7792fbbda7b5dda54f453bd9ec. Полный commit — d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097; parent c0bd09c354a50bf9fe4dcc7cc5f9c34503658479. MACSPLIT G1 head71d18696613bdd6b00648a0d7b44d1cd3c6da940 имеет тот же d4ec476a7a tree; эту связь inventory→v6 проверить и записать.
- DOMSIX от45f6e7f7cc сохраняет library v5/cbe69760c8. Старый checker требует `HEAD:library == TREE`, поэтому с запретом менять library он не пройдёт после простой замены TREE. Проверять источники через `git show d6b8caf7fe:path`, identity целевого PIN:library и соответствие inventory-head:library; явно отделить source pin от HEAD документационного worktree. Не выдавать HEAD за v6 и не переносить library ради прохождения checker.
- Обновить все set-equality проверки: v4-live содержит старое tail13_to16, а native v5 G2 — оба старых ordinary имени. Использовать явное отображение двух старых имён в четыре новых. Для cfg-on v6 построить static set как `(native_v5_cfg_on − old2) ∪ new4`, проверить source/cfg provenance и native ordinary202; не ограничиваться числом384 и не называть этот набор native G2 v6. Проверку отсутствия retired72 и прочие независимые проверки сохранить.
- TSV теперь содержит38 конкретных PFC entries:36 ordinary +2 controls; insert_tail5, остальные family counts прежние. Обновить header `cfg v5`, docstrings/output/README и v4→v6 mapping. Разбиение invocation не добавляет lexical PFC attribute site или новый semantic domain:22 domain records сохраняются; число lexical sites сверить с source, не увеличивать механически вместе с PFC count.
