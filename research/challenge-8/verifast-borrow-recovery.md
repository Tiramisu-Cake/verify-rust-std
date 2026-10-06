# Explicit normal-path borrow recovery control

This release-baseline pilot checks whether a normal Rust caller can recover two
full `T` ownership chunks after creating and ending real shared references. It
uses VeriFast 26.09 with no translator or kernel patch. The fixture has an
`i32` case and a genuinely generic `T` case; the generic signature has no
`Copy` or `Freeze` bound and its postcondition returns current `T.own` storage
for both cells.

Both cases create a lifetime with `begin_lifetime`, create full-borrow content,
then use a normal Rust block with `let_lft` for the actual shared-reference
lifetime. They prepare references with `precreate_ref` and `init_ref_share`,
open the fractional initialization accesses before evaluating `&*left` and
`&*right`, and package the exact outstanding resources in `comparison_debt`.
After the block, each caller makes one explicit call to the ordinary
`nonghost_callers_only` ghost helper `recover_pair`. Its body closes both
fractional accesses, merges the returned portions with the half lifetime token,
ends the lifetime, performs both `borrow_end` operations, and opens both full
borrow contents to restore the current values and `T.own` chunks.

Three negatives target helper or function contracts: a missing half lifetime
token at the helper precondition, a missing `comparison_debt` at that same
call, and a false recovered-value postcondition after the helper. They must
reach VeriFast proof checking and fail with the corresponding resource or
postcondition diagnostic; refinement must still succeed. The runner records
fresh verified/original sources, exact ghost stripping, readonly MIR export and
decode, source hashes before and after every tool, exact caller/helper/call
trace counts, per-case exit codes and timing.

This is a normal-path mechanism control. It does not include `FnMut` callback
recovery: the exact generic direct-`Continue` full unwind obligation remains
open and separate. It makes no unrestricted comparator, `Cell`, insertion, or
domain-shrink claim. No local compiler, verifier, extractor, or runner execution
has been performed; hosted evidence is pending.

The [source audit and exceptional-routing design](BORROW-RECOVERY-DESIGN.md)
records why the earlier auto-lemma proposal was rejected before execution and
the unresolved obligations for a separate direct-unwind experiment.

The runner pins VeriFast 26.09 and `nightly-2026-02-05` through
`setup-verifast-home`. It fetches the pinned MIR schema from source commit
`809de4596839b739dd999f9e462242c835e3af46` and checks schema SHA-256
`7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9` before
decoding MIR.
