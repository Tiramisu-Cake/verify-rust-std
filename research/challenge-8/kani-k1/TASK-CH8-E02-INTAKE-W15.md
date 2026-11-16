# TASK — worker15: intake E-02 и финальный черновик upstream issue (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

E-02 run 43792979809 (sibling `4a8f7e7b10`, control `79baf66106`), artifacts upstream 14193351491, sel1 14193800295
(zip в scratch, raw logs не читать).

Координатор (export verdicts), одинаково на **upstream 0aac** и SEL1:
- `e_h_primitive_write` ON — FAILURE ровно `Check that self->value is assignable`; OFF — SUCCESS;
  `e_h_primitive_no_write` ON/OFF — SUCCESS; `e_h_primitive_no_loop` ON/OFF — SUCCESS.
  → несовместимость loop contracts с `-Z uninit-checks` воспроизводится на **чистом upstream**, не только на нашем стеке.
- `e_h_issue_mre` ON: upstream — `Interaction between raw pointers and unions` (до assigns не доходит), SEL1 — 2× assigns.
- E-S: `e_s_unbounded_slice` OFF — FAILURE `Offset result address must equal original pointer address plus offset`;
  `e_s_false_value` OFF — та же + intended assertion; ON — unsupported intrinsic (uninit).

1. Классификация строк против oracles; убедиться, что primitive_write — минимальный и чистый upstream repro.
2. Финальный ISSUE-DRAFT для model-checking/kani (английский, краткий, в стиле наших прошлых issue #5175): MRE =
   primitive_write (точный код), ожидаемое vs фактическое, версия 0aac16ef62, что OFF и no-write проходят, file:line
   причины (loop assigns без shadow allowance; у function contracts allowance есть). Без ссылок на наши research-документы,
   без внутренних имён; disclosure-строка «*Disclosure: this issue was prepared with the help of AI assistants.*».
   Проверить через gh (только чтение), нет ли уже такого issue. НЕ публиковать.
3. E-S: что именно ломает offset check в symbolic-length storage (кодирование фикстуры или ограничение Kani); следующий шаг.
4. g0 `kani3300/ch8-e/e02/run-43792979809/`: RESULT.md, ISSUE-DRAFT.md, HANDOFF.md. Последней строкой `READY <g0>`
   или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
