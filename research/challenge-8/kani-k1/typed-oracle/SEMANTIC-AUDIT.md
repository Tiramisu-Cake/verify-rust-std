# TYPED semantic/source audit — PRE-BUILD, proof NOT_RUN

Source commit `241d94a41182ed6850244e0b51ddc8031daf7435`;
pilot library tree `702a552ae226f885fe03ef5e8af0a386848587ac`.
Base `e0ff82577dc58950621dadc9c141d88a5821987f`, library
`c522edd42ae67c385e1ee42a1c4d1bffb611c90b`; cap exception
`6b12002d79b6ccb4ded6c4790b1c592c65d6c591` remains untouched.
Below, M = `library/core/src/slice/sort/shared/smallsort/verify/merge.rs`,
T = `library/core/src/slice/sort/shared/smallsort/verify/merge/typed_oracle.rs`,
R = `library/core/src/slice/sort/shared/smallsort.rs`; coordinates are pilot source.

## Ownership and ordinary projection

The only existing library change is M:7–8, the cfg-controls child declaration.
Removing that declaration and its blank line reproduces the base M byte-for-byte.
All other existing library files, runtime bodies/contracts, visibility, oracle/static definitions,
comparators, old harnesses, network/correct/verify modules are unchanged.
All eight new harnesses and helpers are unreachable when controls cfg is absent.
Lane/tool/pin/flags files equal the full cap commit; cap remains 88.96 only here.
`static-audit.py` records text/hash checks; these are not compiler/AST/MIR binding or proof evidence.

## Bridge argument and memory

T:10–29 uses the original raw-static write pattern, without constructing a static reference.
For u64 the first eight bytes are `p.to_ne_bytes()`; for u8 byte zero is p.
Production callers zero all other bytes. Bridge T:73–87 supplies arbitrary bytes before overwriting
only the observed prefix, so successful bridge verification must also establish tail independence.
M:39–74 reads exactly sizeof(T): one unaligned u64 read for u64; one byte for u8.
The local x is initialized and readable for that whole size. Probe is 128 initialized bytes,
so neither read can exceed its allocation. Types have no padding and every bit pattern is valid.
Native-endian conversion reproduces the native bytes without assuming little endian.
Every old 128-byte probe prefix is some unique u64 (`from_ne_bytes`) or u8; its suffix is unobserved.
Therefore projecting arbitrary p covers every observable old probe for each selected concrete type.
Pointwise equality of `matches_value_probe(&x)` and `x == p` yields equal finite sums over every
initialized input/output element. Arbitrary p is unconstrained: this is exact full-value counting,
not a hash, key count, alphabet restriction, or probabilistic claim.

All reached generic probe uses within each real sort/contract instance have its single T:
u64 for G8/S8/A13/control64 and u8 for G9/control8. Runtime helpers preserve T under monomorphization
(R:205–290,680–754,837–856). No recursive cross-type call or probe initializer is introduced.
p and the projected static are fixed across each real call and both postcondition counts.
Only bridge changes type/probe between two completed, separate predicate checks; no call spans that.
The bridge assertions, completion cover, and memory obligations remain NOT_RUN until G1 evidence.

## Theorem/fixture mapping

| Pair | Baseline source | New source | Preserved / permitted change |
| --- | --- | --- | --- |
| G8 projection | M:1001–1010,1050 | T:92–101 | any [u64;8], snapshot, lt_u64 item, real small_sort_general, old checker/cover; initializer only |
| G8 native | same | T:105–114 | same body/F/layout; projection and native final count |
| S8 native | M:1012–1023,1053 | T:118–128 | original StableSmallSortTypeImpl call, const-repeat scratch48, lt_u64; projection/native count |
| A13 projection | M:257–268,1262 | T:132–147 | actual bidirectional_merge PFC, any [u64;13], separate MaybeUninit dst, same lt_u64 F, original requires/modifies/ensures |
| optional G9 u8 | M:1613–1622,1644 | T:166–175 | real small_sort_general, existing internal nonconst aggregate scratch48, lt_u8, any [u8;9]; projection/native count |

All wrappers keep unwind34 and one completion cover with the corresponding baseline message.
Native B uses T:31–69: all indices 0..N (guarded unrolled32), full `== p`, and the same adjacent
sortedness assertion/loop as M:836–849. It does not invoke the old generic count in its final checker.
Normal direct calls use existing `--no-assert-contracts`; actual A PFC still checks its own original
callee ensures, including generic `probe_count_unrolled`. No typed wrapper assertion substitutes it.
No stubs, new requires/ensures, assumptions, axioms, trusted rules, runtime selector, or clone callee.

## Payload controls and acceptance

Controls T:151–162 /179–190 call real general N2 with original function-item comparator, then flip
`v[0] ^= 1`, cover before deliberate assertion, and call exactly the B native typed checker.
This preserves key x>>1. For p equal to the pre-flip output value the count decreases by one;
no assume selects p. Only the native count assertion is allowed to fail; sortedness must pass.
Semantic assertion site T:60–63, concrete macro invocations T:68/69; actual Kani macro-expanded
file:line/check class and all assertion/cover totals are UNKNOWN until bounded build evidence.
Requests expect FAILED with source message `typed full-value counts are preserved`.
If Kani emits its known placeholder instead, retain gate=false on matcher mismatch and bind the
failure manually to the actual frozen file:line/class; do not rename an unrelated failure to success.
Acceptance requires exactly one intended count failure, reached pre-assert cover, no other failures,
and successful positive/bridge checks. Missing/timeout/OOM remain distinct. Until then: PARTIAL.

## Limits

Only source/rustfmt/Python checks have run. No local Rust/Kani/CBMC, inventory or build was invoked.
This package makes no B1 proof claim yet; later bounded evidence cannot imply B2, Linux jobs3/Mac,
N16, new typed A callee backend, X6/migration, or ordinary/P2 admission.
The separate A u8 consumer audit is source-only and cannot replace an A theorem with direct B proof.
