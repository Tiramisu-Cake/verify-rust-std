# Exact oracle recalibration after the usize stdspec insertion

This note records source-coordinate maintenance for existing negative controls;
it does not change their obligations or classifier rules. The prior hosted
matrix, run37750163906 at proof SHA
`0c6699b7700b7f2b4d474f23da8fe8ad153fd553`, inserted five lines before the
relevant pinned VeriFast stdspec obligations. The fixture files retained the
older absolute lines, so several exact errors were observed but remained
`INCONCLUSIVE`. The following metadata changes bind the same observed error
stage, full message, predicate operand, target invocation and source profile at
the exact new location. They do not change historical artifact classifications;
only a fresh hosted run can apply these oracles.

| Fixture | Previous expected location | Observed location | Exact intended obligation | Hosted evidence |
| --- | --- | --- | --- | --- |
| `copy_one_overlapping_ranges` | `std/lib.rsspec:622`, columns 562–564 | `std/lib.rsspec:627`, columns 562–564 | `primitive_precondition`; same `Cannot prove condition` overlap disjunction over `ptr` and `sizeof(T_typeid)` | Export/decode/refinement 0, VeriFast 1; helper and target body visited, target executed 4 statements; one helper return/leak pair; first error is at the called stock primitive precondition |
| `copy_one_misaligned_source` | `std/lib.rsspec:622`, columns 143–145 | `std/lib.rsspec:627`, columns 143–145 | `primitive_precondition`; same `%(get_pointer_address(src), alignof(T_typeid)) = 0` obligation | Same stage pattern; helper and target visited, target executed 4 statements; one helper return/leak pair; source alignment is the observed operand |
| `copy_one_misaligned_destination` | `std/lib.rsspec:622`, columns 193–195 | `std/lib.rsspec:627`, columns 193–195 | `primitive_precondition`; same `%(get_pointer_address(dst), alignof(T_typeid)) = 0` obligation | Same stage pattern; helper and target visited, target executed 4 statements; one helper return/leak pair; destination alignment is the observed operand |
| `copy_zst_count_one_mapping_boundary_calibration` | no predeclared rejection oracle | `std/lib.rsspec:627`, columns 143–145 | `primitive_precondition`; exact observed source-alignment message names `CopyControlZst_type_info` | Export/decode/refinement 0, VeriFast 1; target visited and executed 4 statements after generated ZST support bodies; helper has one return/leak pair; observed first error is at the call's primitive precondition |
| `unsupported_count_two` | `std/lib.rsspec:303`, columns 25–27 | `std/lib.rsspec:308`, columns 25–27 | `primitive_precondition`; same `Cannot prove 2 = 0 || 2 = 1` count requirement | Export/decode/refinement 0, VeriFast 1; own body visited and executed through the call (2 records); exact failure is under its `TARGET_NEGATIVE` invocation |
| `unsupported_signed_offset` | `std/lib.rsspec:313`, columns 35–37 | `std/lib.rsspec:318`, columns 35–37 | `primitive_precondition`; same `Cannot prove 2 <= 1` signed-offset bound | Same stage pattern; own body visited and executed through the call (2 records); exact failure is under its `TARGET_NEGATIVE` invocation |

The run377501 copy rows all reported `INCONCLUSIVE`: exporter, decoder and
refinement succeeded; VeriFast exited 1; the exact errors were present in the
full logs, but the three old lines did not match and the ZST row had no oracle.
The wrapping result rows were likewise `INCONCLUSIVE` because the expected lines
were five lines early. The fixture changes update only those five old coordinates
while the ZST mapping probe remains uncalibrated. Columns and
messages are retained as observed; target source lines, contracts, operation
arguments, source profiles and classifier behavior are unchanged. The full
overlap formula remains required, so a generic `copy_nonoverlapping` failure at
some other operand or location cannot satisfy it.

The next planned profile keeps the usize stdspec insertion at the same five-line
offset: current expected locations remain 627, 308 and 318. The final one-line
usize patch is `ecdd1fd6fcc8d811f02fa308ddc533386e0031193d527ea6950a099f8ccccaa1`
with post-stdlib SHA
`d92e5044bbb2692e7b006fc649df361fe80bf878b69b5a2bb80635a27330f227`. The
multiline `b499…` candidate was not dispatched. These identifiers and the expected
five-line shift are static planning evidence, not evidence that this recalibration
passed. The next hosted artifact
must show each target is reached and classified at its exact expected verifier
error with exporter/decode/refinement `0`, VeriFast `1`, unchanged source checks,
and the intended body execution. Fail closed if any stage, target, source hash,
predicate text, columns or message differs. In particular, no nonzero exit without
the exact observed proof obligation counts as a negative control.

No classifier implementation, semantic specification, verifier, refiner, or
runner was changed here. No local executable checks were run; these metadata
changes require fresh hosted validation.

Root review: removed generated `target_line` fields from input metadata; the
runner itself derives those fields from TARGET, and its input schema rejects
them. Also retained the ZST mapping case as INCONCLUSIVE: source alignment is
an earlier unresolved model condition, so its error does not establish the
intended ZST/positive-size boundary. The table preserves the observed diagnostic
for research; no negative oracle or ZST acceptance is assigned to that row.
