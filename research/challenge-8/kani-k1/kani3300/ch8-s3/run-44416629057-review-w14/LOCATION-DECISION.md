# RECOMMEND_ADMIT_EXACT_LOCATION_ONLY_CASE — NOT_APPLIED

For run44416629057/attempt1 only, SOURCE_REPORTED S1 case assessment may admit the location metadata of the following exact successful system record. Producer UNKNOWN/rejection, strict0/9, null coordinates, property status and all historical evidence remain unchanged. Root/coordinator admission is still required.

| Field | Exact value |
|---|---|
| harness | `slice::sort::shared::smallsort::verify::sorting_s3_leaf::s3_sort4_u8_same_alloc` |
| id AND display_id | `slice::sort::shared::smallsort::verify::sorting_s3_leaf::s3_sort4_u8_same_alloc.unreachable.1` |
| class | `unreachable` |
| status | `SUCCESS` |
| description | `unreachable code` |
| file, line | both keys present with JSON null |
| location_display | `library/core/src/lib.rs:0:0 in function slice::sort::shared::smallsort::verify::sorting_s3_leaf::s3_sort4_u8_same_alloc` |

The stock SourceLocation formatter prints its optional file/line/column fields without requiring positive line numbers (`cbmc_output_parser.rs:261–310`). Its property renderer uses that display. Exact control's rich `_record` requires a positive line regex and therefore preserves the display while normalizing BOTH file and line to null. Feeding a reconstruction from this exact structured record into the actual frozen streaming parser reproduces this result. No original per-property CBMC sourceLocation object for this successful check is retained; normalization is established, compiler/lowering cause and true positive source origin remain UNKNOWN.

The full frozen qualification reader verifies all counts/IDs/status buckets and then rejects the missing coordinates. Its existing `S1-07_EXACT_STOCK_UNREACHABLE_LOCATION_ONLY_V1` map uses the same exact status/class/description/display/null shape for other authorized pairs. This pair is absent. That precedent explains a bounded location-only decision; it confers no automatic exception on this case.

Reason to recommend: only one non-role system SUCCESS check lacks coordinates; it remains recorded with its original ID/status. The same native invocation reconciles363 properties:356 checks=351SUCCESS+5U, zero failures and7 SAT covers. All five required positive assertion roles and seven required covers have exact positive source coordinates and bindings; all5 U have separately sound site-local arithmetic arguments. Protected source/tool/request/namespace and binary epoch observations agree, with no recovery/ignored error. SOURCE_REPORTED S1 permits bounded source evidence without independent MIR trace. The location gap does not invalidate the independently located roles or justify a missing safety failure.

Risk retained: a zero sentinel cannot identify the actual source origin, and the review cannot explain why lowering produced it. Admission gives no source-line provenance or independent correctness credit to that system check. A higher assurance level would require authentic positive producer-origin evidence. There is no invented coordinate or borrowed registration line70.

Required case constraints are cumulative:

- Exact tuple above, including both present-null keys, for this single run/attempt/head/source/tool/control/request/workflow/compact member identity and the original invocation/namespace recorded in LOCATION-DECISION.json. Same-invocation native export, rich inventory, binding metadata, compile receipt, native start and seals must remain mutually bound.
- Exactly one missing-location record. Preserve all counts and stock status partitions:363 properties,356 checks,351SUCCESS,5U,0FAILURE,7 covers all SAT. Reject extra missing records, duplicate/count mismatches or any unknown/error/undetermined checks.
- All5 required literal assertions remain SUCCESS; all7 exact source-local covers remain SAT, with no extras. Every actual role, cover, failed check, U and other source check remains positively located. This tuple cannot excuse any literal assertion, failed panic/unwind/safety check or status-UNREACHABLE site.
- Preserve all5 U records and separate per-site premises, source hashes, cfg/target/domain/init/frame applicability; never turn U into SUCCESS. Retain successful unsupported guards and the system check itself. Protected binary/source/compile/request/provider identities and original exits remain validated.
- No global missing-location rule, future ID/prefix/stdlib waiver or automatic future-run applicability. Root/coordinator must explicitly decide this exact case; no reader/acceptance/policy patch is implemented or authorized by the review.

The actual frozen reader still rejects. A distinct offline hypothetical case model accepts this authentic case and rejects24 mutations, including identity changes, missing roles/failed-check locations and extra gaps/count mismatches. Its results are bounded tests of the proposed constraints, not executed frozen-parser acceptance.

Accordingly the observed native sort4same result can be **assessed** separately under the owner's S1 criteria despite producer UNKNOWN. Any admitted case assessment must cite the immutable producer rejection, the unresolved source origin and this exact decision. It must not rewrite producer/history, activate proposal93f158, claim independent B1/B2, or become an assumed caller summary.
