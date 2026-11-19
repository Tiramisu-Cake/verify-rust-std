Title: Report recursive calls in delayed UB analysis instead of overflowing the stack

With `-Z ghost-state -Z uninit-checks`, delayed UB analysis can follow a recursive call chain until the compiler overflows its stack. The analysis now reports “Kani does not support memory initialization checks across recursive calls.” at the recursive call site.

The analysis tracks resolved function instances on the active call chain and removes each instance when its analysis returns. Sequential calls to the same helper are analyzed separately. The tests cover recursion reached from a delayed UB target, repeated calls that leave an uninitialized read, and a repeated-call control that initializes the full value before checking it.

Testing: [Full standard CI (pending)](PENDING_FULL_STANDARD_CI_URL).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
