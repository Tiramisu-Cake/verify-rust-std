# R13 dispatch binding and tool-route review

## Scope and decision

Reviewed the `a1-call-binding.py` source-order change, its synthetic test changes, and only the R13 `FOCUS_PROFILE_NAMES` route in `a1-tool.py`. **Conditional GO** for the call-order fix and profile-map entry. The profile’s `a1-tool.py` SHA is stale against the current edited file and must be refreshed during integration before the profile is published or dispatched.

The added R13 route maps `SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13` to the exact `A1-REFERENCE-OWN-R13-PROFILE-2026-10-21.json`. That profile carries the same authorization ID and the existing A1 protocol phase. A pure import/JSON check confirmed this mapping. The separate R13 reconstruction changes in `a1-tool.py` were outside this review’s assigned scope.

## Call ownership and ordering

The R13 representation design does not change the relevant caller source. The current checked-in `quicksort.rs` has one `T::small_sort_threshold()` call followed by one `T::small_sort(v, scratch, is_less)` call in `quicksort`. The R12 P-dispatch design requires the exact source-certified trio: those two calls owned by `quicksort`, plus the threshold call owned by the uniquely renamed observer. `_source_functions` verifies the generated-source digest and exact original quicksort signature; `_source_calls` derives each caller’s call set and source lines from that source; `_calls_for` requires an exact MIR call set, substitutions, lifetime count, line, and argument roots.

The change orders calls by the source-derived `expected_lines` mapping. Its insertion order comes from `_source_calls`’ explicit threshold-then-small-sort expression list, so it preserves the certified order instead of lexical callee order. The exact-call-set and call-count checks still reject extra, missing, or duplicate trait calls. The MIR call spans remain attached to the same callee row for P-dispatch; the downstream join still checks owner/callee bijection and compares each AST and MIR span to its own trace field and certified call line. The code does not assume AST and MIR span ranges equal each other.

## Validation

Passed the 23-test `test_a1_call_binding.py` suite, plus the five-test `test_a1_dispatch_trace_join.py` and five-test `test_a1_dispatch_admission.py` synthetic suites. No compiler, preparer, verifier, full runner, Cloud Build, or raw evidence was used. The registration/profile route check confirmed the exact R13 mapping and protocol identity.

## Integration action

Refresh `A1-REFERENCE-OWN-R13-PROFILE-2026-10-21.json` → `a1_helper_sha256["a1-tool.py"]` to the final integrated `a1-tool.py` SHA. This review does not establish actual Cloud trace applicability or proof credit; P-dispatch remains a structural, non-credit observation until run on its authorized source/tool profile.
