# Source regression oracles and coverage

REGRESSION-ORACLE.json binds all38 declared harnesses to the repair source/tree,
their exact attributes and source-predicted outcome. All repair native results
are NOT_RUN. Baseline observations retain their original assurance: positive
replacement_contract_target fails natively per coordinator, the other18 in
that file verified per coordinator, expected-suite cases NOT_RUN, and separate
no-assert file execution UNKNOWN. No native property quotas are inferred.

| File | Source expectation on repair | Baseline boundary |
| --- | --- | --- |
| ordinary_stub.rs | All19 harnesses verify; replacement_contract_target checks the caller once and asserts nested provider contracts | Native positive provider-PFC arrangement fails single-call guard; all other harnesses same file reported verified |
| ordinary_stub_no_assert.rs | Ordinary copied body uses Original; PFC/verified modes remain active, bad provider PFC is expected panic | Source unchanged, per-file native status UNKNOWN |
| ordinary_stub_fail.rs | Two providers verify; eleven named failures, including provider ensures0 under caller PFC | Expected suite NOT_RUN; old provider-PFC pattern predicts guard failure before intended post |
| ordinary_stub_issue_4591.rs | Verbatim caller addition overflows for allowed replacement i32::MAX | Expected suite NOT_RUN; caller counterexample retained |
| ordinary_stub_overlap.rs | Existing explicit original PFC+verified+ordinary overlap reports missing f closure | Expected suite NOT_RUN; unchanged compile-error control |

Main969f lacks the ordinary body-source handoff, so these added ordinary-stub
regressions are expected from source to encounter missing target closures.
No new execution on main969f is claimed. The published6f compiler repair is
preserved byte for byte. Its native result validates neither the two affected
fixture expectations nor any unrun expected suite.

The positive caller and provider both require x<16 and ensure result==x+3.
The negative caller ensures result==x; the provider returns x but ensures0.
Input1 discriminates provider Assert from provider Original or weakened identity
postcondition while admitting the caller post. Source-call traces contain one
selected caller Check and one nested ordinary provider Assert. Baseline traces
instead contain two provider Checks sharing a once guard. The direct0-only
and copied1-only alternatives fail different goals: removing copied1 loses
ordinary composition; removing direct0 loses selected-provider exact reachability.

All .expected files are byte-identical to6f. The ordinary_stub_fail golden
retains descriptions for overflow, x<8, false result==x+2, result==0 and x<4,
every named failed harness and its declared 2success/11failure/13total summary.
These are harness inventory counts, not verifier property counts. A generic
compiler failure or single-call error cannot supply the required ensures0
description. Native execution must still confirm actual output behavior.

Same-function f PFC and verified controls remain alongside ordinary f→g;
requires-only and ensures-only have corresponding controls; recursive controls
retain recursion instrumentation. replacement_provider and
replacement_verified_contract preserve provider PFC/verified coverage separately
from caller composition. Replacement arithmetic/pre/post failures and unstubbed
contract failures remain intact. Unsupported same-original-target overlap stays
an explicitly separate diagnostic control, not a substitute for semantic tests.

Coverage limit: the former sequential direct-provider-plus-copied-provider PFC
case is replaced. The repair covers ordinary provider Assert inside caller PFC,
plus separate provider PFC and provider verified selection. It does not prove
a new supported policy for every mixed PFC-provider alias shape. PFC-AUDIT.json
records all13 source harnesses and their selected target, exact direct call,
recursion/overlap mode and native boundary.
