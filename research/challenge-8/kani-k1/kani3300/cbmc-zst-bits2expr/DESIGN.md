# Design and scope

Defect: bits2expr accepts zero-width struct components, but its array branch rejects
an array element of the same width. This prevents reconstructing a nonempty wrapper
with a zero-width array subtree from its initialized byte representation.

The only implementation change is `*el_size_opt > bitst{0}` to
`*el_size_opt >= bitst{0}` in the array branch. Presence remains checked, before
conversion to size_t. No zero-initializer branch, fake bits, assumptions, enclosing
zeroing or replacement of the wrapper type is introduced.

For known finite count N and element width0, the whole array width is0. Its input
bits are empty by the existing whole-type check. Each unchanged loop iteration takes
string(bits, i*0, 0), a valid empty slice at position0, and recursively reconstructs
the declared subtype. The base empty struct produces a typed zero-operand struct;
nested arrays terminate by descending finite type structure. Exactly N operands are
appended. N0 produces a correctly typed empty array without recursion. Failed
subtype reconstruction still returns optional failure; it is not replaced by a
fabricated value. Illegal cyclic by-value types are outside the existing domain.

A zero-width component advances the enclosing offset by0, so nonzero neighbours
consume exactly their previous bit ranges. No endian logic changes; scalar maps
still perform their existing conversions. Public API tests additionally round-trip
a tagged E array between differently valued head/word/tail fields and reconstruct
a suitable union arm under both endian flags.

Whole-type consistency, the constant-count precondition, checked count conversion,
unknown/negative widths, vector/complex guards, ABI/layout/frontend rules and the
outer zero-width byte_extract guard are unchanged. expr2bits already concatenates
empty strings correctly and has no new failing roundtrip justifying an edit.
This stage does not expand utility support for unknown/incomplete widths, symbolic
sizes, negative counts, arbitrary unsupported subtypes or array compression.

Risk: N can be large even though physical extent is0; reserve and recursive operand
construction still use O(N) IR (nested arrays proportional to their finite element
product). Tests use only small counts. No array_of/compression optimization is added.

The literal owner C repro is retained byte-for-byte in owner-literal.c and in the
CI-only fixtures. The source regression strengthens it by checking every payload
byte and layout. The int case uses aligned union backing, completely written bytes,
unsigned repeated-byte values and explicit target layout checks. Separate files
keep baseline crashes from suppressing other C cases. The negative companion has
one false assertion about a nonzero field; the CI runner rejects extra failures.

No runtime result is claimed for develop. Independent Luna High review covers the
source candidate. Only static checks and isolated Python runner service tests ran.
Paired baseline/fix C CI, compilation and formatting remain for the coordinator.
A Kani-like C padded union is a C model only; no Kani/Rust replay or Kani#5085/case B
closure is claimed, and the B3 workaround remains untouched.
