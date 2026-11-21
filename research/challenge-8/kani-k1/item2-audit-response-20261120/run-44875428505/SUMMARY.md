# q-пилот, кампания 12 (merge-пакет B) — сводка координатора (run 44875428505)

std 4707a7354a, control 7ad0c3d567 (trigger 8f33dfb1b1), tool 0aac16ef, cap 10 GiB.

- MB-MERGE-N18, MB-MERGE-N19, MB-PRE-NUMERIC-N18: **ошибка компиляции** (24 с): `E0599` — `Option<MergeSnapshot>::clone` в `old(...)` ensures `bidirectional_merge`; у `MergeSnapshot` не было `Clone`. Ни одного верификационного результата.
- MB-H10-CORRUPT-LITERAL (контроль): **FAILURE ровно `MB_H10_LITERAL_CORRUPT_NUMERIC_ORDER`**, 1/1061, covers 2/2, child 166 с, 8,22 GiB, 3,64 млн дизъюнктов — облегчённый контроль H10 теперь работает.

Исправление координатора: `#[derive(Clone, Copy)]` на `MergeSnapshot` (поля q:u8, len:usize, target:u32), std `8ae4029765`; request перепривязан к новому std (sha/tree/хеш файла), roster прежний. Повтор — кампания 12b.
