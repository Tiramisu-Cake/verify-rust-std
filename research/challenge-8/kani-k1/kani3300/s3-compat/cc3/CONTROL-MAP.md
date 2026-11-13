# CC3 controls — execution NOT_RUN

| Input / roots | Required result and discrimination |
| --- | --- |
| closure-upvars/ordinary.rs: bool_captures_true_false | Both valid bool values; reached typed closure copy/layout and callback/outer assertions SUCCESS |
| ordinary_captured_contract / simple_check_captured_contract | Actual ensures captures &initialized; both input branches and useful true payload read reached; no bool/ref/layout failures |
| closure-upvars/layout.rs: mixed_scalar_ref_padding | bool ref + MU ref + scalar + whole repr(C) padded field + ZST; closure nested in Offset<F> at nonzero offset; all useful reads/outer assertion reached SUCCESS |
| reordered_nested_captures | Different logical use order, u64/u8/ref fields, complete inner closure captured by value; own rustc offsets/order and recursive current_offset; useful outer SUCCESS |
| closure-upvars/holes.rs: two_refs_initialized / two_refs_preserve_hole | Same valid &bool and &MU slots; positive reads17, negative reaches MU u8 read and fails local Check plus delayed CheckRef only; no slot/invalid-value/Unsupported failures |
| capture_padding_stays_false | Legal padded value captured by value; typed closure copy followed by reached byte1 read inside actual copied upvar; padding stays false; Check plus CheckRef only |
| Existing closure-zst capture-scalar / padded / reference-legal / raw-legal / mu-reference-new / union-reference | Typed ptr::read<F> must actually request nonzero closure layout; supported positives SUCCESS |
| Existing capture-reference-hole / raw-hole / mu-reference-uninit | Actual body read reached and required two u8 uninit obligations remain; Unsupported is not a payload-negative PASS |
| Existing capture-mu-value-new / mu-value-uninit / union-value | Reached recursive layout of by-value union yields explicit UnionAsField; no blessing; an earlier unrelated Unsupported is NONDISCRIMINATING |
| Existing unit/align64 legal/hole and scalar-pfc legal/hole | Preserve zero-size case and exact required legal/read-negative behavior |
| Original mode-boundaries replace_ordinary / replace_simple_check | Original Rust bytes unchanged; both branches/covers and useful checks reached SUCCESS, with no residual bool/&bool/layout failures |
| Original recursive_check / recursive_ordinary / recursive_simple_check | Separate complete collections; CC1 detected-cycle Unsupported allowed only for unclaimed recursive mode; ordinary cycle remains release BLOCKED |
| Original replace_transfer | Prior five failures stay historical fact; do not require removal of two havoc-result u8 checks or claim mode qualification |

Selected MIR/model must establish actual closure type/upvars/field offsets/masks,
reached typed layout request, aggregate setter and consumer CheckRef. Source
assertions or declarations alone do not establish these. Unsupported or absent
request before a boundary makes that boundary NONDISCRIMINATING. Capture-based
controls do not silently become capture-free companions; existing CC1/CC2
capture-free fixtures remain intact and required for final composition.

Mixed three-file runs compare each root with its singleton result. Actual
starting_items grouping and both actual root orders must be captured through
existing coordinator support; declaration order alone is not order evidence.
