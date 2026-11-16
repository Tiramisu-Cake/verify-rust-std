# TASK — worker14: B census на P′ (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

B-01 (run 43774504122) координатор отменил: std 872d + Kani 0aac не компилирует `core`
(нет upstream #745) — см. [TASK-CH8-PPRIME-REBASE.md](TASK-CH8-PPRIME-REBASE.md).
P′ `c5ff36ff433692140605891f646043f991db05de` компилируется с 0aac (S1-02: core/std Finished за 5m22s).
Но S1-02 упал на глобальном `kani list` по verify-std: на 0aac он делает codegen каждого std harness и
не укладывается в 600 s (TASK-CH8-S1-LIST-W13 — 13 сейчас чинит это для S1-runner).
Твой C-controls пакет (`cdd3c6d041`) использует тот же list — координатор держит его до фикса 13.

1. Пересадить B census на P′: тот же manifest 235 roots (имена/модули сверить на P′; если что-то
   изменилось из-за upstream merge — явная таблица), новый control (kani-host как прежде).
2. Проверить, делает ли B runner глобальный `kani list`/иную полную инвентаризацию; если да —
   спроектировать так, чтобы фаза не упиралась в per-root cap и всегда писала receipt
   (exit/timeout/elapsed/RSS, bounded head+tail). Если 13 уже закоммитил решение
   (`kani3300/ch8-s1/kani-host-list/`), переиспользуй его.
3. Synthetic tests, review. g0 `kani3300/ch8-b/pprime/`: CI-REQUEST, REVIEW, HANDOFF.
   Последней строкой `READY <ci-pkg> <g0>` или `STOP <причина>`.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
