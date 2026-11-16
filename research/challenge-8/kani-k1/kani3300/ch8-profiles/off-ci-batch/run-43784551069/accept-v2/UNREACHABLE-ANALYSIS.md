# Unreachable roles at the frozen source

Source `9fa2f7f97760584f38738909625c064006d8a936`, stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`.

All 1505 positive and 205 negative unreachable occurrences are enumerated by
row and exact ID in ACCEPT.json. No defensive exception is admitted in this batch.
UNREACHABLE-REVIEWS.json is scoped by row, then property ID; its empty row objects
mean no exact property-role binding was established, rather than no investigation.

The export schema keeps unreachable IDs only: `ChecksExport::from_properties`,
`kani-driver/src/frontend/schema_utils.rs:515-543`. It omits their source locations
and descriptions. The `success` bucket is a count. A CBMC `.assertion.N` ID is not
a source assertion number. In particular, it can describe compiler-generated
overflow checks inside a source helper, rather than that helper's logical result.
Reading the source function cannot establish which numbered check this is.

Source inspection found these relevant families:

| Function family | Source context | Why it does not settle exact property role |
|---|---|---|
| `model_sorted` / `model_count` | `verify/merge/profiles.rs:127`, `:146`; 31/32 guarded, unrolled model accesses | These helpers implement postcondition models, but some emitted checks may be defensive arithmetic checks in excluded unrolled steps. Neither a blanket required-assertion veto nor a blanket helper exemption is justified. |
| `regions_are_disjoint` | `verify/merge.rs:107` | Geometry/pointer checks need the exact emitted condition and scenario domain. |
| `sort4_stable`, `bidirectional_merge`, `small_sort_general_with_scratch`, `small_sort_network`, `small_sort` | Actual algorithm bodies called by the forwarders | Reachability of a specific branch/check cannot be inferred from the algorithm name. |
| `ptr_offset_from` | Kani intrinsic model | Several numbered conditions exist, and export has no per-ID condition/location. |
| `is_aligned_to`, `from_str`, `is_valid_allocation_size`, numeric helpers | `ptr/const_ptr.rs:1474`, `fmt/mod.rs:815`, `ub_checks.rs:147`, numeric implementation | Plausible defensive branches still require exact-ID/location/domain binding. Library membership is insufficient. |

The receipt therefore records role `UNKNOWN`, location `null`, function from the
export ID, and the missing-binding reason for every such occurrence. This is an
explicit information limitation of this artifact's JSON schema. No logs, raw
archives, compiler, verifier, new build, or changed exporter were used to fill it.

The classifier implements both alternatives for future exact reviews: unreachable
postcondition/frame/relation/required-section checks block admission; a reviewed
defensive branch requires an exact ID, location, target/wrapper relation and reason.
Synthetic tests exercise both, including a defensive branch inside the target.
