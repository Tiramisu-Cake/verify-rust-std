# KANI3300 D1-A — результат

Стадия выдана координатором в активном поручении; DRAFT/HELD в шаблоне снят этим поручением.
Run 43314208878 attempt1; research D1-P cedd1a7b5fd99c27baf9d9c07180ecaea5b92b97.
Trigger 8a4664fe1d3587c8ce17790ac2d818cdb169cd25 локально проверен: push, один workflow, exact checkout refs.
CI R1 1d0f1d30bfcf8ce64d63716a31a0a9bd3e06c7a0; R6 86f9b171513de7a11eec7587bead1edc6877d950.
Identity/allowlist/fixture PASS; 129/129 manifest files на каждом pin совпали по SHA256/bytes.
Pre/post-DFCC и actual CBMC input разделены по hashes; in-place filename не использован как identity.
P1 legal единственный captured case на каждом pin; P2 source сохранён, run P2 отсутствует.
Setup/build/capture snapshots/DFCC/symex-only COMPLETE; Kani rc101 — diagnostic parser incompatibility.
Top-level capture=failure/upload=PENDING сохранены отдельно от complete per-phase captures.
Normal verification NOT_RUN; parser INCOMPLETE; новый failure verdict/proof credit отсутствует.

Исходный parser считал только префикс из-за 200000-character budget.
Офлайн census всего bounded printed stream: R1 all5280/ignored4213/retained1067, guards2039.
R6 all5865/ignored4588/retained1277, guards1961; ASSERT96/115, ASSUME33/41.
Byte-extract/update: R1 4/1, R6 9/1; все sliced. Retained WITH: R1 0, R6 13.
Top30 occurrences пересчитаны; logical Boolean roots отделены от UNKNOWN operand widths.
Selected Layout0/1 перечислены отдельно; Layout1 = один Boolean mask element, storage1B/8bit.
R1 state56B; R6 tracked state24B + ARGUMENT_BUFFER32B; это storage/type-derived widths.
Source→GOTO write→retained SSA цепочки и точные coordinates записаны в MODEL-MAP/ATTRIBUTION.
R1 saved-object write PC639 → phi PC664, field64bit; phi не назван исходной записью.
R6 store buffer PC631 → DFCC check PC628/ASSERT629; extent32B, pointer cell ≠ pointee.
R6 assume(false) load paths и private-frame obligations мешают semantic resource equivalence.
Оба symex streams предупреждают о nondeterministic arguments saturating_add/sub.

**Offender не найден.** Converter cost/cache/DAG/allocations/postponed work не измерены.
R6 остаётся историческим frameFAIL-контрастом, не корректным PFC performance baseline.
Следующий выбор: отдельно одобряемый C; сначала запросить наличие сохранённых typed/conversion fields.
Никакой оптимизации/representation/scope-cut здесь не реализовано, новых runs/заданий нет.
M3/full gate/PFC scope claim/resource fix — HELD/NOT_ESTABLISHED. Cloud $0. STOP D1-A.
