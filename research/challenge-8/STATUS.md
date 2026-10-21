# Merge-R16 — ACTIVE

[Текущее задание](CURRENT-TASK.md): worktree `/root/verify-rust-std-merge-origin`, branch `merge/incoming-origin-20261009`, owner `merge`; tool `/root/verifast-merge-actual-glue`, branch `merge/actual-glue-instance-20261011`.

Новое разрешение:120мин + до30мин завершения, **3600 Cloud-секунд**, без отдельного лимита Builds. T0 2026-10-21T16:08:24Z; main18:08:24Z; absolute18:38:24Z; новый ledger открыт, used0/carry0. Phase `MERGE-CALLER-CURRENT-PROOF-R16-2026-10-21`, lane `merge`, ledger `CURRENT-RECOVERY-R16-BUDGET-20261021.json`; timeout<=1200/reserve>=420/execute<=780/envelope+60. R15 не возобновляется.

Baseline checkpoint `da54db9dd223ed2ab3926586f6089fcd63bbcf28`; actual source `97a9766513d5567bd291d8e49b71240ce246c472`, Build `f89ce5ff-644e-46ef-90da-044c96931270`; tool `660b576b6b1608db913c51e0785b443a8733396f`, profile `experimental-merge-label-storage-r11-v1` SHA256 `eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375`.

R15 CLOSED:4 Builds,2690spent/2557execution/910retired/remaining0/carryfalse; own0/0/0/0 по closeout. Checked singleton/CURRENT reassembly прошли прежние отказы на наблюдённых путях; array controls source4positivePASS/5negativeEXPECTED. Новый blocker caller `b2_three_from_local`441 `Placeholders are not allowed here` на `values.as_mut_ptr()`. Full targetINCONCLUSIVE, acceptedfalse/gates0/independentcredit0; полное insert_tail/CURRENT false-true-panic/B2/generic/qualification OPEN. [Архив task/report](task-history/merge-singleton-array-autonomous-2026-10-21-r15.md), [release](cloud-build/origin-layout/R15-RELEASE-20261021.json).

R16: source-preserving caller unsize/lifetime fix с сохранением metadata/borrow/provenance; actual regression нового R9 classifier из da54 (reviewed/18syntheticPASS, Cloud-unverified), затем body/CURRENT normal-unwind и полный совместимый набор. Original prefix/caller gates обязательны; broad placeholder acceptance не разрешена. R8 trusted premise сохраняется только в прежних границах. Publication исправна; новые upload probes без дефекта не нужны. Автономность/review/Evidence v0.11/Cloud-only сохраняются.
