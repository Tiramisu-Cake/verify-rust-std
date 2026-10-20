# S2 positive-receipt input binding rationale

## Applicability

The delivered S1 lifecycle reached P0a/P0b VF0, then receipt admission failed because P0b was checked against P0a's certified `source_id` and `unit_id`. The constructor certificate assigns distinct unit identities to default16 (P0a) and freeze32 (P0b), even though both cases use the same verified/original source pair bytes. `A1Admission.record_implementation` correctly rejects an implementation receipt whose unit identity does not match its expected input. This is a receipt-construction binding defect, not a reason to weaken admission.

## Change boundary and preserved checks

For the ordinary positive receipt, bind `default16` to the certified P0a source/unit and `freeze32` to the certified P0b source/unit. For the own-false31 receipt, bind both implementations to the certified N-false31 source/unit, matching its existing receipt-only alias family. Before recording either implementation, require each collected raw observation's source and unit IDs to equal its selected certified case. Keep the same compiler inventory, exact body/conformance checks, source-pair hashes, native posts, receipt case, expected matrix cases, and `A1Admission` criterion. Missing, null, malformed, swapped, or cross-case IDs remain errors.

The change does not synthesize proof credit, change source/compiler inputs, copy N-false31 evidence into a positive proof, or alter the gate/classifier. Isolated tests will exercise the actual admission service with distinct P0a/P0b units and reject wrong bindings while confirming that the own-false31 path keeps its own IDs. No preparation, extraction, compilation, verifier, full runner, or Cloud action is part of this local check.
