# R9 S3 — normalize compiler-local lifetime names inside role tuples

S1's admission preparation reports a normal/readonly semantic mismatch. The
runner's `prepare_admission_control_inputs` calls `observe("P1", ...)` on the
baseline decoded files, selecting the original quicksort with both threshold
and small_sort calls. The earlier bounded inspection of the observer alone did
not identify this callsite. S2 remains active on immutable published inputs;
its diagnostic must establish the actual failing fields before S3 submission.

The current pure reproducer passes the existing synthetic full-quicksort MIR
pair with only compiler-local input/HRTB region names alpha-renamed consistently.
It fails at `/calls/0/argument_region_roles/0/2`, `/1/2`, `/2/2`: these validated
role rows are tuples, while the semantic normalizer recurses only through lists
and dictionaries. The observer-only alpha test passes because it has no
small_sort argument-role rows. This establishes a representation defect in the
full P1 route; it does not by itself establish S1 causality or actual proof.

The minimal candidate recurses through tuples while retaining their tuple kind,
using the same already validated positional input/HRTB alias map as list/dict
values. Keep the exact resulting semantic-equality gate, source/callsite/body
binding, T/F/generic bounds, three argument roots/order/reborrow checks, distinct
input regions and HRTB scopes, clauses and normal/unwind resources unchanged.
Unknown/unmapped strings remain literal and mismatches remain failures. No new
alias/memory model or proof premise is introduced.

Controls: full P1 alpha-renaming pair must be accepted; genuine argument,
callee, lifetime-count, collapsed-region, body-span and clause mismatches stay
rejected by the existing parser/service suite. Diagnostic hashes/paths and size
caps remain unchanged. Local checks use only hand-written synthetic MIR/parser
fixtures; actual compiler/exporter/decoder/refinement/verifier and binding
regressions remain Cloud-only. Independent Luna HIGH review and exact R9
profile/helper pins precede any authorized S3 submission.

S2 actual evidence confirmed exactly these three tuple-slot differences: normal__78,__79,__81 vs readonly__73,__74,__76; caller=quicksort/caseP1, decoded source SHA3bf1b47d7e28be437c7f5288c31ad930a1219018fa1cbd035706a94e9a2e6a01 and d57caad6a69e35778ba32cedf37850b31f76da64d385c3a80d08da6181f1d05e. Exact Reader audit/error first+rest request IDs and provenance are preserved in S2-EVIDENCE/Reader records. Tuple fix received independent Luna HIGH GO; all22 synthetic tests retain both observer and fullP1 alpha cases. Actual binding acceptance on the new helper remains Cloud-only.
