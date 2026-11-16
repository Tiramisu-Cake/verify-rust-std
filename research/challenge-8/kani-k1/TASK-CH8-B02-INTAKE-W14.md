# TASK — worker14: intake B-02 census (одна стадия, после C-01 intake)

Это верификация корректности, не security-работа. Отвечай кратко.

B-02 run 43788110361 (trigger `f601ca74ca`, pkg `99dbb2157b`, std P′ `c5ff36ff43`, Kani 0aac), conclusion success,
artifact 14192030971 (zip в scratch, raw logs не читать).

Координатор (bounded): `summary.json` COMPLETE 235/235: **PASS 11, "copy Unsupported" 224**. Одна multi-harness invocation,
wall 886.9 s, group peak RSS 3.29 GB, exit 1 (224 failed). Пример root-001 `fixed_inputs::advancement_merge_up_u8_n2`:
единственный failure `ptr::copy_nonoverlapping::<u8>.unsupported_construct.1`, unreachable — список.

1. Таблица 235: класс, единственность failure (только copy unsupported или есть другие), 11 PASS — какие и почему
   они не доходят до copy; есть ли intended invalid-value roots.
2. Причина в Kani 0aac (`-Z valid-value-checks` + `copy_nonoverlapping`): file:line, есть ли upstream issue
   (gh, только чтение); минимальный MRE; что это значит для плана B (§8): no-requirements fast path / producer checks.
3. Что ещё можно извлечь без нового CI; предложение следующего шага B (cap: B 2 из 3 использованы).
4. g0 `kani3300/ch8-b/pprime-batch/run-43788110361/`: RESULT.md, TABLE.json, HANDOFF.md (+ черновик issue, если нужен,
   без публикации). Последней строкой `READY <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
