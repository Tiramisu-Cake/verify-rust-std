Preserve specialization defaultness in function contract macros

Contracts on a blanket implementation's `default fn` currently fail during macro parsing.
Parse the method with its specialization qualifier and retain it alongside the existing function representation.
Emit the original `default` token on the outer method during both initial and stacked contract expansion.
Add tests for individual/stacked clauses, method generics, verified stubs, specialization overrides and old snapshots.
Include negative controls for false postconditions, invalid preconditions, frame violations and missing override contracts.
Validation: static patch/format checks pass; the selected native Kani regression run is pending coordinator GO.
