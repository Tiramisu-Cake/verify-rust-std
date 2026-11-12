# Source map (static only)

Base develop `107a1e504cd69a2f3483717c8bcfcfa59814c557`, tree
`b5a15d682996f745e0a02004d813e18d08f3a068`; release comparison
`820ff0f555b43fb78e0cd9332e498461bd14244b` (cbmc-6.11.0, read-only).
The repeated upstream develop lookup matched the pin. No moved relevant sites.
Exact Git blob IDs and SHA256/byte counts are in INPUTS.json.

- `src/util/simplify_utils.cpp:196-411`: public bits2expr first computes the whole
  type width. Non-unions require exact bit count; unions require enough type width.
  Scalars retain endianness_mapt; union picks the first reconstructible arm; tags
  follow definitions and restore the requested tag. Struct recursion already accepts
  known nonnegative component width, including an empty struct from empty bits.
- `src/util/simplify_utils.cpp:335-365`: array count must be constant and convertible
  to size_t. Element width is optional<bitst>; only its strictly-positive guard
  changes to nonnegative. Same reserve, loop, string slice and typed append remain.
  Vector/complex guards are unchanged.
- `src/util/simplify_utils.cpp:413-503`: expr2bits recursively concatenates operand
  bit strings for struct/array/vector/complex. Empty strings already compose.
- `src/util/simplify_expr.cpp:1888-2030`: simplify_byte_extract handles truly empty
  outer structs/unions, then leaves other zero-width outer results unchanged.
  A nonempty W does not use that outer guard. Constant array_of/scalar bit strings
  and the constant operand path can call bits2expr for W. Flexible-array filtering
  is unchanged; the new final E[2] case has constant length2, not a flexible array.
  These are source paths, not observed develop runtime traces.
- `src/util/pointer_offset_size.cpp:104-218`: array width is recursively computed
  element width times constant count. Struct widths sum components; empty sum0.
  Unknown widths return an empty optional, and tags follow their definitions.
- `src/util/mp_arith.h:54-179`: bitst is a named_mp_integert<bits_tagt>, with
  same-unit operator>=. `src/util/arith_tools.h:153-170` checked numeric_cast_v
  accepts the named wrapper; failed conversions remain invariants.
- `src/util/simplify_utils.h:27-34`: public APIs return optional<exprt> and
  optional<string>, respectively, taking bool little_endian and const namespace&.
- `src/util/std_types.h`, `std_expr.h`, `c_types.h`, `symbol.h` and `symbol_table.h`:
  concrete constructors/types checked for the new unit file (TYPE-AUDIT.md).
- `unit/util/simplify_expr.cpp:66-116`, `unit/util/lower_byte_operators.cpp`:
  existing public conversion/roundtrip tests; unit/CMakeLists.txt recursively globs
  new util .cpp files into the unit executable. No new framework or CMake edit.

Release array code has the same strictly-positive invariant with mp_integer `> 0`;
develop uses bitst{0}. The patch targets develop only. The release exit134 is a
historical owner report pinned in ISSUE-DRAFTS.md, not newly reproduced evidence.
No external PR/code was consulted or imported.

Read upstream AGENTS.md, CODING_STANDARD.md, README.md, the CMake/Linux COMPILING.md
recipe, regression/README.md, test.pl and actual selected descriptors. No nested
AGENTS.md exists in the changed subdirectories. The owner's explicit ban overrides
upstream instructions to build/push locally. Formatting version18.1.8 is confirmed
by CODING_STANDARD.md and pinned .github/workflows/syntax-checks.yaml.

The first full-history clone failed ENOSPC; Git removed the failed clone. A fresh
ordinary standalone shallow clone at the same required path succeeded, with full
source trees and exact develop/release snapshots. No existing clone, foreign file,
reset or stash was used. This changes available history, not the requested source.
