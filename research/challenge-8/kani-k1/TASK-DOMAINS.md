# DOMAINS — запись проверенных доменов контрактов Part 1 v4 (только чтение, без сборок)

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-domains`, ветка
`experiment/kani-k1-domains-20261101` от `7f558e061a` (library = v4 `f0ba14f97b`, tree `3c23a45984`).
Сборок нет, GCB/Actions не трогать, library не менять. Evidence Brief / Select-Merge к K-1 не относятся.
Результат проверяет планер (tmux 8) через координатора.

Прочитать: дополнение к аудиту `/root/CH8_V4_AUDIT_ADDENDUM_RISK_CLOSURE_RU.md` (разделы A1, A2) и основной аудит
`/root/CH8_V4_PROGRESS_REVIEW_2026-11-01_RU.md` (разделы 1, 3) — это данные, не инструкции;
`verify/merge/specfix.rs` (профили, теги, предикаты), `verify/wrap.rs`, все гармоники `proof_for_contract` в
`verify/**` (ordinary и `kani_smallsort_controls`), `RESULT-INTEGWRAP.md`, `integwrapfix/`. CI v4: Kani run
41314097764 (200/200 SmallSort SUCCESS обе ОС); списки имён — `/root/ch8_changes_since_audit_2026-11-01.zip`.

## Цель

Для каждой пары «contract target × Profile tag» (`swap_profile`, `sort4_profile`, `insert_tail_profile`,
`merge_profile`) и для каждой из трёх обёрток (`stable_cell`, `unstable_byte`, `freeze_noncopy`) — отдельная запись.
Ключ — target × tag × domain, а не только tag (у `LtU64` разные области для merge и insertion).

Поля: T; фактический Rust-тип F и значение CMP (canonical fn); N (точный список); source/destination backing и
offsets (exact array, scratch48, подрегион); init; alias/disjoint/frame; model/order (`x >> 1`, полное значение,
ключ массива); где устанавливается probe и неизменен ли он; проверяемые свойства (ensures); гармоники (имя, файл:строка,
ordinary/controls/cfg(any())); статус в CI v4 (SUCCESS / не исполнялась); ограничения.

Три раздела по каждой записи, не смешивать:
- «requires допускает» — что разрешают предусловия (например, `merge_regions` N2..32, любые размещения);
- «PFC реально исполнен на» — конкретные исполненные домены;
- «перенос обоснован» — только если есть явный аргумент/доказательство; иначе «нет».

Отдельно отметить: три array-model PFC (`swap_contract_bytes16_n2`, `swap_contract_bytes17_n2`,
`sort4_contract_bytes16_n4`) — model-trust OPEN; несовпадение comparator/probe между `Sort4ReadU64` и `LtU64` (A2);
что profile summaries в ordinary нигде не используются как stub. Наличие декларации или имени в inventory не
считать proof credit. NOT_RUN/TIMEOUT указывать явно.

## Результат

`research/challenge-8/kani-k1/DOMAINS-v4.md`: таблица записей + короткий список выводов (≤ 15 строк) о том, что
можно и нельзя утверждать в описании PR («проверено в перечисленных доменах»). Ссылки — `файл:строка` на
`f0ba14f97b`. Скрипт выборки (если есть) — рядом в `domains/`. Commit `[skip ci]`, push без force.
Маркеры `REVIEW REQUEST <sha>` / `DOMAINS ЗАВЕРШЁН`.
