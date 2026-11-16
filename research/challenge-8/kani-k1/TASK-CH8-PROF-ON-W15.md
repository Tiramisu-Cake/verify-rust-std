# TASK — worker15: Profiles ON (uninit) — CI-only пакет (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Profiles OFF принят 62/62 (g0 `9c7ffcb385`, `kani3300/ch8-profiles/off-ci-batch/run-43784551069/accept-v4/`; политика
[ACCEPTANCE-POLICY-BATCH.md](ACCEPTANCE-POLICY-BATCH.md)). По плану (ROADMAP §5, план пункта 1 §7) ON-квалификация — твоя.
Бюджет: Profiles ON — 1 dispatch сейчас (item 1 остаток 4).

1. Source: тот же profiles std `9fa2f7f977` (P′). Tool: SEL1 `14bc57fdb9` (Tiramisu-Cake/kani; C2+SEL1, nightly-10-23 —
   совместим с P′). Флаги: организаторские + `-Z uninit-checks`; valid-value OFF; всё прочее как OFF.
   Если какая-то строка требует флагов/cfg, недоступных в ON, — явный STOP этой строки, не тихое удаление.
2. Runner: переиспользовать принятый OFF control (`112fcc9ada` + классификатор accept-v4) — batch-группы, per-row
   binding, stdout regular output (для ролей unreachable), receipts; tool checkout/сборка SEL1 из форка по SHA.
   Static path preflight (как fix1). Ожидаемые известные ON-риски перечислить заранее: PolymorphicIter unsupported
   (A1-R3) в general scratch, network N32 RSS — какие из 62 строк их достигают (по source); oracle для них не менять.
3. Synthetic tests, review. g0 `kani3300/ch8-profiles/on-ci/`: CI-REQUEST, REVIEW, RISKS.md, HANDOFF.
   Последней строкой `READY <control> <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
