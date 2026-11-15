# Контроли и oracle

CONTROL-MAP.json — exact planned selectors11 roots:2 probe,1 checker companion,
8 expected-failure controls. Rust/compiler/property inventory NOT_RUN. Все9 control
roots регистрируются только с kani_smallsort_controls; не запускать весь controls
module как ordinary suite. Прежние S1/model/helper controls остаются обязательны.

Сначала получить compiler inventory на combined source; подтвердить exact target,
contract attachment/mode и concrete T/F. Для каждого negative запустить отдельный
root, требовать указанный failure и отсутствие посторонней infra/compile/UB ошибки.
Requires/frame property IDs назначаются только после реального inventory; заранее
выдумывать ID запрещено. Wrong-precondition control не должен падать на spec-read UB.
Все positive asserts/required covers проверяются отдельно от exit0: unrealizable
cover означает vacuity/ошибку summary и admission запрещён. Негативы не кредитуются
по одной подстроке FAILURE и не теряются в job с общим ненулевым exit.

Frame negative deliberately вызывает actual swap с effectful comparator другого
типа; generic inactive semantic branch не оправдывает внешний write. Это проверка
старой element-only frame boundary, не теорема сортировки для произвольного F.
Weak-summary negative использует отдельную identity replacement, допустимую для
safety/frame-only post: она показывает, почему old contract не доказывает sorting.
Ни один положительный probe не использует этот replacement или assume(false).
