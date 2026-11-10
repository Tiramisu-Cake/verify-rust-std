Preserve specialization defaultness in function contract macros

Contracts on a blanket implementation's default fn currently fail during macro parsing.
Retain the original default token alongside ItemFn and emit it on the outer method through stacked expansion.
Add individual/stacked clause, FnMut, verified-stub, override and eager-old regression tests with negative controls.
Build 1: repro and all ten existing regression selectors pass; 18/19 selectors pass overall.
The remaining negative stub fixture needs a proof_for_contract harness; its six-line repair awaits the native rerun.
Full upstream CI is pending; no publication in this stage.
