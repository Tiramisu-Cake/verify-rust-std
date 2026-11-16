# TASK — worker15: intake E-01 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

E-01 run 43783430196 (sibling `3219b3f220` of control `628ba7fd9b`), conclusion success (runner), artifacts:
upstream 14188654722, sel1 14190061402 (скачай через `gh api repos/Tiramisu-Cake/kani/actions/artifacts/<id>/zip`
в scratch-каталог вне репозиториев, анализируй из zip, raw job logs не читать).

Координатор (bounded, export verdicts):
- E-Q: `e_q_pointer_loop` и `e_q_false_pointer_loop` OFF — FAILURE 3129/8 и 3128/8 («Check invariant before entry/after
  step»), т. е. **положительный** quantified-pointer invariant тоже не проходит; `e_q_isolated_witness` OFF FAILURE 3085/7
  (`kani::exists!` + pointer outside object bounds); все E-Q ON — без export. `e_q_scalar_invariant` SUCCESS на обоих pin, ON и OFF.
- E-H OFF — SUCCESS на обоих pin. E-H ON upstream — unsupported `[MaybeUninit<u8>; N]` / raw pointers+unions.
  E-H ON SEL1 — FAILURE с `Check that self->value is assignable` / `self->tracked_object_id is assignable`
  (вероятно, записи shadow `MemoryInitializationState` внутри цикла вне loop assigns), `e_h_outside_false_alias`
  ON SEL1 — UB uninitialized read (ожидаемый negative?).
- E-S `e_s_unbounded_slice` — без export на обоих pin.

1. Классифицировать каждую строку против своих oracles из CONTROLS.md (intended/unexpected/setup), причины без export
   (из bounded stdout/stderr tail в artifact).
2. Ключевой вопрос: несовместимы ли loop contracts с `-Z uninit-checks` в Kani (shadow writes vs loop assigns) — точная
   цепочка file:line на SEL1/0aac, MRE (single-file), есть ли upstream issue (искать по model-checking/kani через gh,
   только чтение). Почему положительный E-Q pointer invariant не проходит OFF — ошибка encoding или ограничение.
3. Итог для E: что ещё можно, что STOP; предложение (issue-текст черновиком, без публикации) если это новый upstream дефект.
g0 `kani3300/ch8-e/e01/`: RESULT.md, MRE/, HANDOFF.md. Последней строкой `READY <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
