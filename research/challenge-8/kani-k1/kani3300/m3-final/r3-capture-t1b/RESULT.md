# M3-R3 composition capture / T1b — worker14

Candidate: `ada5c7bd44ee33a9c9e229cc5c35bcd32464d0fb`, directly on
`3a29b3323561c5765505ef617607cadfc91f0ce8`, clone
`/root/kani-fix-3300-m3r3`. No Rust input, manifest binding, validator,
DelayedUbPass implementation, CI configuration or shared cache was changed.

Explicit `--collect-unbound` capture now records every mixed root/order diff
and continues through all 11 invocations instead of stopping at the first
inventory difference. The report has exact added/removed rows, per-comparison
acceptance, and T1b evidence; its aggregate oracle is EXACT_MATCH,
MATCH_WITH_T1B or MISMATCH. A complete capture always returns 2 / UNBOUND_CAPTURE,
even with reviewed bindings or mismatches; no PASS credit. Process, schema,
incomplete output and root-binding guards still stop invalid observations.
Ordinary bound regression rejects oracle mismatches.

The oracle preserves exact verdict, failure kind, full failure multiset
(including ID, description, source location, class, trace availability and
status), Unsupported inventory, and useful checks/covers. Root and target
checks stay exact. Only extra/missing SUCCESS/UNREACHABLE `.safety_check.N`
rows in explicitly reviewed shared `std::ptr::read::<u8>` are exempted; exact
function location and ID must agree. Unknown functions fail closed. Existing
IDs cannot change metadata or status. Assertions, reachability checks, covers,
failures and Unsupported never receive the T1b exemption. Covers are retained
with exact regular-output metadata and validated against JSON status buckets.
README explicitly records known T1b and the separate upstream mechanism
(R3 answer 7/11); this change does not repair or qualify shared-cache isolation.

Validation: Python-only `test_compare.py` passes **41 tests**. Synthetic cases
include allowed shared supersets/subsets, forbidden extra/missing/changed
failures, root/target/unknown-function and useful-check drift, exact reached
covers, shared status/metadata drift, complete 11-invocation capture after
oracle mismatch, and ordinary bound regression versus explicit capture exits.
Existing process/timeout/hash/schema/error-path tests still pass.
`git diff --check` passes. No cargo, Kani, CBMC, push or CI dispatch performed.

`AUDIT-CAPTURE.py` revalidates only supplied local r2 artifacts from run
`43502450916`, checks source/receipt/export/output hashes and original exits,
and emits `CAPTURE-AUDIT.json`. It launches no verifier and changes no original
evidence or historical verdict. All **8 available invocations** validate:
seven isolated roots and `all_A_then_B`. Mixed comparison results:

| Root | Result | Extra shared SUCCESS checks |
| --- | --- | --- |
| immutable_legal | accepted T1b | 6 |
| immutable_hole_negative | accepted T1b | 9 |
| ordinary_ensures_legal | exact | 0 |
| pfc_legal | exact | 0 |
| pfc_negative | exact | 0 |
| cycle_root | **MISMATCH** | 0 |
| unrelated_legal_after_cycle | accepted T1b | 3 |

The reported original `immutable_legal` rejection is explained by shared
`std::ptr::read::<u8>.safety_check.5`–`.10`, all SUCCESS, with unchanged SUCCESS
verdict and zero failures.

Additional finding: `cycle_root.unsupported_construct.1` keeps the same ID,
FAILURE status, source location, verdict, class and trace availability, but
its description differs between isolation and `all_A_then_B`. The embedded
diagnostic prints allocation-dependent numeric Ty/AdtDef IDs, e.g. AdtDef
`496` → `521`, Ty `35` → `331`. Replacing only those numeric IDs in an offline
diagnostic experiment makes the descriptions equal; **the oracle does not
normalize or accept this difference**. The required exact failure-description
and Unsupported comparison therefore correctly reports MISMATCH. Full exact
rows are preserved in the audit. Any diagnostic stabilization or change to
failure identity policy is separate work for the coordinator.

`all_B_then_A`, `cycle_then_legal`, and `legal_then_cycle` are absent from r2
because the old runner stopped early. The next coordinator-authorized capture
on this candidate must collect all 11 actual invocations. Existing local files
cannot establish those missing results. Binding remains BINDING_PENDING,
producer order remains uncontrolled, and no independent proof credit is claimed.
