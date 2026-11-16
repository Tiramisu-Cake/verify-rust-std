# TASK — worker14: один CI-пакет для MRE двух черновиков issue (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Владелец решил публиковать issues после вычитки. Два черновика опираются на MRE, которые ещё ни разу не запускались:
1. valid-value × copy_nonoverlapping — kani3300/ch8-b/pprime-batch/run-43788110361/ISSUE-DRAFT.md
   (copy_integer + контроли raw_bool_overwrite / raw_bool_read);
2. slice havoc под uninit-checks — kani3300/ch8-profiles/on-ci/gaps/ISSUE-DRAFT-B.md и MRE-B-slice-havoc.rs
   (check_body, check_slice_havoc + сравнения из раздела «Checks needed before submission»:
   инициализированный out, thin targets, отрицательный контроль настоящего uninit read).

Сделать: kani-host control по образцу E-02 (kani3300/ch8-e/e02/: parent = чистый upstream 0aac16ef62, только
.github/workflows + один control-каталог, stock workflows удалены), без std: каждый MRE — отдельный .rs, отдельный
вызов kani с точным argv, флаги ровно как в черновиках. Для каждого harness — заранее объявленный ожидаемый исход и
oracle (VERIFICATION, exact failed property ID/description). Bounded receipts + export. Synthetic tests, review.
Одна job, ≤30 мин. Без SEL1 (только чистый upstream: issue — про upstream).

g0 kani3300/issue-mre/: CI-REQUEST, REVIEW, HANDOFF. Коммиты [skip ci], author Tiramisu-Cake <igkharin@gmail.com>.
Последней строкой READY <control> <g0> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC. Тексты issues не менять — их правит координатор.
