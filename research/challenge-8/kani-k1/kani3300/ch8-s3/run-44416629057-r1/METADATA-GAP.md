# sort4same location gap — exact metadata gate accepted; runtime repair NOT_APPLIED

Exactly one offending record in the authenticated compact properties.json:

- ID/display_id: `slice::sort::shared::smallsort::verify::sorting_s3_leaf::s3_sort4_u8_same_alloc.unreachable.1`
- class `unreachable`, status `SUCCESS`, description `unreachable code`.
- normalized `file` and `line` fields are **present null**, not absent.
- location_display is `library/core/src/lib.rs:0:0 in function slice::sort::shared::smallsort::verify::sorting_s3_leaf::s3_sort4_u8_same_alloc`.

The file string and zero line/column survive the compact rich export. Positive source coordinates do not. The stock JSON successful-property representation has a success count and non-success buckets; it does not export this successful check's individual SourceLocation. Native per-check CBMC JSON is not in the compact package. The harness registration's valid source line70 is a different record and cannot repair this property. Its true source origin remains UNKNOWN.

Exact tool0aac SourceLocation Display formats stored file/line/column fields; this display contains lib.rs:0:0. CONTROLcb6303 rich_evidence.RegularEvidence._record requires `[1-9][0-9]*` for line and therefore maps both normalized fields to null while preserving display. validate:213–217 requires nonempty file plus positive decimal line OR an exact location_exception. The S1-07 exception map does not contain this harness/property tuple. runner._run_group:1178 raises ValueError; exception path persists properties.json INCOMPLETE and receipt FAILED; controller root_outcome preserves UNKNOWN, seals it and continues. No property was lost.

The frozen reader reproduces the exact rejection after checking every count/status bucket. An isolated parser reconstruction from authentic structured fields reproduces display and normalized nulls. This is a recognized display shape with a zero sentinel rejected by location qualification, not a compact projection accidentally omitting valid coordinates. No actual positive coordinate can be recovered from the retained fields. Compiler/lowering reason for the sentinel is UNKNOWN.

This is a successful system unreachable-code check, not a literal assertion role, cover, failed panic or unwind property. All five positive assertion roles and seven covers bind exactly and independently at their valid leaf source coordinates; all5 U sites have separate source-local arguments. Native SUCCESS351/356 checks,5U,7SAT covers remains separate from rich metadata failure and strict rejection.

NOT_APPLIED: original worker/reviewer can add a narrowly reviewed location-only exception for this exact harness/id/display_id/class=unreachable/status=SUCCESS/description/display tuple, preserving null coordinates, same-invocation totals/status validation, strict U and role gates; alternatively producer provides authentic positive origin. Never global missing-location allowance.

Feed authentic compact offending display record to existing RichParser; require normalized nulls and current rejection. Any reviewed exception must reject changed harness/id/class/status/description/display, locationless literal roles and extra missing-site records; valid role bindings remain unchanged.

Exact reversible location metadata gate accepted by coordinator+planner at f74025e493a627962842e8f7bc6a2766d33dd300, based on review a9fe0055aab3279e3f5bb71bde9667925da80e65 and base intake d29ab46dbbb45d7106fa30c3ac04bb419a2ac286. ADMISSION-REFERENCE.json retains the full exact property tuple, present null file/line, counts, protected identities and constraints. Actual source origin/lowering remain UNKNOWN. Overall qualification awaits SAME14 reporting delta and root/coordinator case assessment; no whole-S3/B1/B2/caller/generic proof credit. Producer UNKNOWN, strict0/9, REJECT_ALL and disabled U proposal stay unchanged; no runtime reader patch.

The repair proposal above remains historical NOT_APPLIED runtime work. No exception, policy, source, reader or artifact was changed.
