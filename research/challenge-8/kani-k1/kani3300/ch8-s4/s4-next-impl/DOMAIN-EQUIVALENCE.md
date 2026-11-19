# S4P3 finite domain correspondence

This is a static source argument for the approved finite fixture, not Rust
compilation, AST/MIR equivalence, native verification, cover SAT evidence or
proof credit. The immutable reference is std
8faf8e62af8f82b5c46af020086f8df591b6757e and its unchanged
`sorting_s4_network_r2.rs`, SHA256
25fcbfa26052727a47c9628e0c41f33c80a57f06971fa61efcc36f4af77d838c.
The new module instantiates the reference N2 singleton harness template at the
four approved new lengths; N2 proof/admission is not transferred to them.

For fixed N in {8,9,13,17}, let B={0,...,255}^34 and
C(N)={i in {0,...,33} | i<1 or i>=1+N}. The plan's initialized V34/base1
fixture quantifies B × {N} × C(N). Each implementation has independent
`let mut v: [u8;34] = kani::any()`, an owned copy of all34 bytes, constant N,
and a separately arbitrary usize canary restricted only to C(N). Thus it
quantifies exactly that product. Every active byte and every outside byte
remains arbitrary. Index0 and index33 are outside at all four lengths. There
is no value, ordering, distinctness, alphabet, or canary-side assumption.

The plan's slices [1..1+N] equal the implementation's literal [1..9], [1..10],
[1..14], [1..18], respectively. Each root makes one original
`small_sort_network` call on exactly that range, between the same typed owned
snapshot and post call, using a fresh stateless `KeyLess<u8>`. No shared symbolic
length/helper, copied circuit, replacement callee, assumed/verified stub or
summary edge is introduced. All old harnesses and the actual callee tree,
models, kernel bodies and contracts remain byte-identical to the parent.

All three existing concrete u8 model guards are required. `sorting_model`
retains its valid equal-length owned snapshot, adjacent sortedness, and full
input-value multiplicity checks. Since the counts of every distinct input
value sum to N and output length is N, equal counts also exclude a new output
value; duplicate queries do not weaken this argument. No sampling, hash count
or binary projection replaces that oracle. The frame iterates all34 indices,
allowing changes only in [1,1+N), and the additional canary compares the complete
byte at an arbitrary outside index. Four separately named SUCCESS roles per
root bind these obligations to exact source lines and SHA256.

Six named covers per root remain independent existential witnesses. The old
`n>=2` guard in the three pair covers is true for each selected N; the retained
`n==N` guard on descending is also true. These agree with the approved plan
predicates on the entire domain. The role contract supplies separate static
full-u8 assignments: descending N,...,1 witnesses an unsorted, nonconstant
sortable input and the maximum-descending predicate; all-zero input witnesses
duplicates. The candidate sorted outputs only check oracle/predicate
consistency of these examples; they are not executions or native SAT evidence.
Covers never constrain the input via assume.

Pinned `small_sort_network` uses `no_merge = len < 18`. N8 uses insertion tails
1..7; N9 calls actual sort9 and zero-body shift at offset9; N13 calls actual
sort13 and zero-body shift at offset13; N17 calls actual sort13 and insertion
tails13..16 (span through17). All return before final merge/copy-back. In
particular N17 supplies no merge proof. Descending input exists for all four
lengths in u8 and forces maximal source insertion movement at N8/N17; this is
not a native branch-origin assertion.

`s4p3_domain.expected` accepts only the exact SHA-pinned network-r2 header and
N2 template instantiated at the four lengths with fresh names/labels. Full
text comparison rejects any additional oracle/frame/canary/guard/callee/domain
change. New regression tests perturb each root's call, snapshot and post
lengths, constants, byte domain, frame/canary range, unwind, actual callee,
active guard and roles/covers. The request inventory and source snapshot are
separately immutable and all role sites are checked. These gates provide
checkable source correspondence, not compiler equivalence or proof acceptance.

The four fixed negatives and their bindings/expectations are identical to the
control parent. They remain first. Positives and Cell retain unwind36; the
other three negatives retain34. The frame still needs34 source bodies, and
the largest oracle inner loop has N bodies (N squared total work). Source
bounds do not establish lowered loop/intrinsic/contract sufficiency. Native
resolved argv, all unwind properties and new role/cover/U/model/builtin/source
origins must be bound separately for each future invocation. No earlier
producer ID, accepted unreachable site or missing-location exception transfers.
ZERO_U, REJECT_ALL and strict0 rejection remain unchanged.
