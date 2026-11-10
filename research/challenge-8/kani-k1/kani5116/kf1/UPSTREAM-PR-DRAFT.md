Preserve specialization defaultness in function contract macros

Contract attributes on a blanket implementation's default fn currently fail during macro parsing.
Retain the original default token alongside ItemFn and emit it on the outer method through initial and stacked expansion.
Keep each implementation's contracts attached to its own method, with no contract inheritance.
Add individual/stacked clause, FnMut, verified-stub, override and eager-old regressions with negative controls.
Validation: 19 native selectors pass, including all nine new fixtures and ten existing regression fixtures; formatting and fresh-pin patch application pass.
Full upstream CI and core safety-attribute/default-method integration smoke tests remain pending.
