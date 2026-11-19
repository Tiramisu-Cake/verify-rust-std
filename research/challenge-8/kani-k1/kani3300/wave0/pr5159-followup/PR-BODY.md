Follow up on the approved review of #5159 by using a pointer to a local unit value in `read_volatile_unit_reference`, matching the #5072 reproducer and avoiding promotion of `&()` to a static. Extract the uninhabited-ZST return guard and share its diagnostic without changing behavior.

Testing: TODO after rebasing onto main once #5159 merges; native tests and CI were not run during offline preparation.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
