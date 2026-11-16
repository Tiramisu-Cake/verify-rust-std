# TASK — worker13: intake S1-03 и предложение S1-04 (одна стадия; S1 budget исчерпан — S1-04 только после владельца)

Это верификация корректности, не security-работа. Отвечай кратко.

S1-03 run 43784240498 (sibling `8233b98c15`, control `40b5d9cf48`, S′ `f22f84f316`), artifact — через
`gh api repos/Tiramisu-Cake/kani/actions/runs/43784240498/artifacts` (zip в scratch; raw logs не читать).
Политика приёмки: [ACCEPTANCE-POLICY-BATCH.md](ACCEPTANCE-POLICY-BATCH.md).

Координатор (export verdicts):
- production-u34 (15): SUCCESS — predicate_efficient_swap_type_matrix, stable_default_activation (6.4 s),
  stable_freeze_activation (35 s), **stable_default_cell 326.8 s**, **unstable_default_cell 326.6 s**, inactive_pairs_read_free,
  snapshot_guards_companion; **TIMEOUT 600 s**: freeze_copy_u8, freeze_default_noncopy, stable_freeze_u8, unstable_freeze_u8;
  FAILURE с description `This is a placeholder message; Kani doesn't support message formatted at runtime`:
  activation_descending_rejected, activation_effectful_rejected, activation_unsupported_type_rejected, invalid_snapshot_rejected.
- production-u4 (3): corruption_companion SUCCESS; order/count_corruption_rejected FAILURE (тот же placeholder).
- production-u5 (3): model_{cell,noncopy,u8}_n0_3 SUCCESS (~1.9 s).
- activation-default-u34 / activation-override-u34: export нет (фаза закончилась после 4 таймаутов) → NOT_RUN.

1. Классификация 23 строк по политике (binding, oracle, covers, unreachable/unsupported по роли).
2. Negatives: named failure по **property ID/location** вместо runtime-formatted description (это не ослабление,
   если привязка к той же assert-точке); проверить, что сбой — именно ожидаемая assert.
3. **Главное — стоимость:** почему freeze/u8 тела >600 s, а Cell ~327 s при N0..3. По export/receipts/источнику:
   размер формулы, unwind 34 vs нужный, KeyLess/snapshot модель, ensures/PFC вес; что именно доминирует. Варианты
   снижения без ослабления (корректный меньший unwind, разделение по N, переупорядочивание групп, отдельная группа для
   тяжёлых строк чтобы не съедать фазу). R8 bar: ≤600 s/root.
4. Подготовить пакет S1-04 (не запускать): исправленные oracles, порядок групп (лёгкие и activation раньше тяжёлых),
   изменения стоимости с обоснованием. Отдельно — что нужно от владельца (S1 cap исчерпан).
5. g0 `kani3300/ch8-s1/run-43784240498/`: RESULT.md, COST.md, S1-04 CI-REQUEST/REVIEW, HANDOFF.
   Последней строкой `READY <control|-> <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
