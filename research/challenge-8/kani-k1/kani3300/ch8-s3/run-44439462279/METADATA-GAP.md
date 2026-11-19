# Exact location metadata gaps — immutable producer UNKNOWN

Each of the three completed merge exports has exactly one invalid location record: both keys are present-null, no missing keys, no non-null wrong-type fields; the preserved raw display is lib.rs:0:0 in its exact harness function. Every literal role/cover, every source-locally assessed U, and every successful unsupported guard has positive coordinates. All three original group receipts retain FAILED and canonical UNKNOWN with ValueError: rich metadata incomplete: file/line missing.

## m8_s32_d00_allinit

Harness `slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit`; invocation `189628db8bdc48279407d1b3ee938808`; namespace `/home/runner/work/kani/kani/export/target/ch8-s1-cargo/189628db8bdc48279407d1b3ee938808`. Member `groups/s3-m8_s32_d00_allinit/properties.json` SHA256 `33f1cc56448a77072e4f354b02eee82fafd4399aa2a437c77273bf557b070c2b`; export SHA256 `d28bd84d208c6b4fa51152b8c77f195373867d0cfb314806da6c581f59120e37`.

```json
{
  "class": "unreachable",
  "description": "unreachable code",
  "display_id": "slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.unreachable.1",
  "file": null,
  "id": "slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit.unreachable.1",
  "line": null,
  "location_display": "library/core/src/lib.rs:0:0 in function slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_allinit",
  "status": "SUCCESS"
}
```

Native386 properties/380 checks/372 SUCCESS/8 statusUNREACHABLE/6 covers SATISFIED. Five positive literal assertions SUCCESS, six located covers, eight individually contextualized U, four located SUCCESS unsupported guards; no extra failed/error/unknown/undetermined check.

## m8_s32_d00_partial_diag

Harness `slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag`; invocation `684bfd6aab514f55bb6a9cb250b2b8b0`; namespace `/home/runner/work/kani/kani/export/target/ch8-s1-cargo/684bfd6aab514f55bb6a9cb250b2b8b0`. Member `groups/s3-m8_s32_d00_partial_diag/properties.json` SHA256 `8b33b24811f9dbbb296dd07d9d7608470ab72d5f393ea033e9061c2f4a11a0a6`; export SHA256 `05a3178cd72098abd4dca640caa78d1c3bef37331101ee7b4c2b33bc9743d460`.

```json
{
  "class": "unreachable",
  "description": "unreachable code",
  "display_id": "slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.unreachable.1",
  "file": null,
  "id": "slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag.unreachable.1",
  "line": null,
  "location_display": "library/core/src/lib.rs:0:0 in function slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s32_d00_partial_diag",
  "status": "SUCCESS"
}
```

Native386 properties/380 checks/372 SUCCESS/8 statusUNREACHABLE/6 covers SATISFIED. Five positive literal assertions SUCCESS, six located covers, eight individually contextualized U, four located SUCCESS unsupported guards; no extra failed/error/unknown/undetermined check.

## m8_s40_d16_partial_diag

Harness `slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag`; invocation `74b9eae5ed164a8ea4732993b42e4de1`; namespace `/home/runner/work/kani/kani/export/target/ch8-s1-cargo/74b9eae5ed164a8ea4732993b42e4de1`. Member `groups/s3-m8_s40_d16_partial_diag/properties.json` SHA256 `daad811a79761e718332a2a4f290bfc9df675ddcc159ce471d8d197ea70091c1`; export SHA256 `dc5e07fbf24f76871a4a87a96a1dab053dc48b32c93314bea0ca0ac369e28fc8`.

```json
{
  "class": "unreachable",
  "description": "unreachable code",
  "display_id": "slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.unreachable.1",
  "file": null,
  "id": "slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag.unreachable.1",
  "line": null,
  "location_display": "library/core/src/lib.rs:0:0 in function slice::sort::shared::smallsort::verify::sorting_s3_2_leaf::m8_s40_d16_partial_diag",
  "status": "SUCCESS"
}
```

Native386 properties/380 checks/372 SUCCESS/8 statusUNREACHABLE/6 covers SATISFIED. Five positive literal assertions SUCCESS, six located covers, eight individually contextualized U, four located SUCCESS unsupported guards; no extra failed/error/unknown/undetermined check.

## Exact historical comparison

Old decision `f74025e493a627962842e8f7bc6a2766d33dd300` and review `a9fe0055aab3279e3f5bb71bde9667925da80e65` name `slice::sort::shared::smallsort::verify::sorting_s3_leaf::s3_sort4_u8_same_alloc`, run44416629057/1 only. Its full authentic exact property/protected identities/member digests/counts are retained in METADATA-GAP.json; the independent review and coordinator document agree on the property. Old counts363properties/356checks/351SUCCESS/5U/7SATcovers differ from each new386/380/372/8/6. New source/control/request/root/IDs/invocations/namespaces/members are different. Same tool0aac and byte-identical rich parser; no original-run exception is transferred.

The source trace supports possible emission and exact normalization routes. At stock statement.rs468-469,512-516 a MIR Unreachable terminator can emit PropertyClass::Unreachable / unreachable code using its span; assert.rs214-221 passes the location to assert-assume(false). span.rs40-65,92-109 derives filename/line/column/current function. None of these sources binds the actual new records to a particular MIR terminator or explains their0:0 origin. cbmc_output_parser.rs261-310 prints optional file/line/column/function; cbmc_property_renderer.rs274-347 prints the regular record; schema_utils.rs485-550,750-790 preserves status partitions but individually omits successful system-check location/ID from stock JSON. Rich evidence supplies the exact display IDs with same-invocation stock partition checks. All source files are pinned to tool0aac by hash.

The byte-identical frozen RegularEvidence._record positive-line regex rejects0, retains raw display and normalizes both file/line to null. An isolated authentic-field parser reconstruction establishes that behavior for each new record. The full frozen validator reconciles counts/status IDs/guard records before rejecting its final location gate. No coordinate is reconstructed from registration or a neighboring source site.

**Actual shared system-check emitter identity, causal lowering route and positive source/MIR origin: UNKNOWN.** Same class/text/suffix/display shape proves neither a shared emitter nor cause. classunreachable/statusSUCCESS is a successful system record, distinct from statusUNREACHABLE source assertions. Recommend exact enumeration only, or leave PENDING; no prefix/lib.rs:0:0 wildcard. See LOCATION-PROPOSAL.
