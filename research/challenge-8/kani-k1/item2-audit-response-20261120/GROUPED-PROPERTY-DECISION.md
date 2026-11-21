# Решение координатора: сгруппированные native свойства и повторные вызовы

Повод — [ADMISSION-N13-N19.md](ADMISSION-N13-N19.md): строки допуска N18/N19 (и функциональная часть N13–N17) не оформлены, потому что для свойств с общим ID (два исполнения sort9 Pre, несколько хвостовых вставок, `ptr::copy_nonoverlapping` precondition instances, DFCC/safety групп в Check) требовалось перечисление SSA instances и guards по каждому исполнению.

## Семантика цели CBMC на tool pin

CBMC 6.11.0 собирает все SSA assert-шаги с одним `property_id` в одну цель и проверяет её как **конъюнкцию всех экземпляров**: `goalt::as_expr()` возвращает `conjunction(cond_handle по всем instances)`, решатель ищет выполнение `not(conjunction)`. [goto_symex_property_decider.cpp:34–41, 47–71](/root/cbmc-pr9487-slop-readonly-20261119/src/goto-checker/goto_symex_property_decider.cpp:34)

Следовательно, `SUCCESS` для ID означает: ни один экземпляр этого assert ни в одном пути и ни в одном исполнении не может быть нарушен. Отдельного перечня instances для вывода о безопасности не требуется.

## Когда экземпляр конкретного исполнения гарантированно входит в цель

Symex порождает assert-шаг для каждого достижимого исполнения инструкции. Экземпляр исполнения может отсутствовать только если (а) путь отсечён развёрткой — исключено, так как unwinding assertions соответствующих циклов имеют `SUCCESS` при unwind36 (`--no-unwinding-assertions` не используется); (б) путь недостижим — тогда свойство вакуумно для этого исполнения, и это выявляется covers; (в) условие упрощено до `true` при symex — тогда это исполнение доказано на уровне упрощения.

## Правило допуска

Для свойства с общим ID, привязанного к декларации роли (clause, helper, precondition), исполнение конкретного вызова считается закрытым, если одновременно:
1. ID имеет native `SUCCESS` в exact root;
2. все unwinding assertions root `SUCCESS` (нет усечения путей);
3. достижимость исполнения подтверждена `SATISFIED` cover после этого вызова на том же пути (useful-return cover после всех вызовов сети, return/odd covers в Check) либо прямой последовательностью straight-line вызовов фиксированной геометрии, доказанной source-разбором;
4. вызов исполняется в режиме, который даёт этот assert (Replace → caller requires как assert; Check → ensures/DFCC/safety тела).

Отсутствие перечня SSA instances и guards в regular/export **не блокирует** допуск при выполнении 1–4. Требование mapping property→SSA instance снимается как избыточное.

Это решение не меняет `proof_credit=NONE` для исторических receipts и не затрагивает ресурсное решение по Check sort13.
