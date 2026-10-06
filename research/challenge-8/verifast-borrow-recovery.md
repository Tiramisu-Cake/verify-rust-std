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

The debt wrapper is an ordinary, imprecise predicate: its close-token conjunct
is itself imprecise in the pinned runtime. A precise declaration fails before
body verification, as run37437183634 showed. The explicit nonghost-only helper
does not need a precise wrapper. The correction removes that invalid metadata
claim and leaves every conjunct, ownership resource and target post unchanged;
it neither introduces automatic application nor disables precision checking.

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

## First hosted result

[37437183634](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437183634)
checked source `f9a7159c3e3320726cbb0b286ea9d233b1e4c0c8`, selection
verifast_borrow_recovery90min. Full logs/artifacts inspected. All five readonly
exporter/decode/refinement checks return0, and source hashes remain unchanged
after each tool. All five VF runs return1 at the same predicate declaration:
`Preciseness check failure: callee is not precise.` No helper/caller body or
explicit call is reached; negative classifiers correctly reject this failure
as unrelated to their intended resource/postcondition errors. Thus no recovery
proof or intended-negative result is claimed. VF .10s (.11s generic), refinement
.05s (.06s generic); runner17.65s,RSS640,548KiB. Cold release setup dominates,
no source compilation, covers or loop bounds. Exact release console SHA-256
`dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc`,
prelude `d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5`.
Next new exact-SHA run after correcting the wrapper declaration.

## Ordinary-wrapper result

[37437514808](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437514808)
checked source `2a16b2421e81590e91025bf8b662e96be0660369` with the same
release/tool pin and selection. Full logs/artifacts inspected: all five readonly
exporter/decode/refinement checks pass and source hashes remain unchanged after
each tool. Both i32 and unrestricted generic T callers verify with full current
cells and T.own; each caller/helper header is exactly1, actual helper body18
trace records, explicit call1. All three negatives reject at their intended
helper precondition or caller post with the same body/call counts and refinement0:
missing half lifetime token, missing comparison debt and the false recovered-value
condition. No unrelated frontend failure is accepted. VF .08s per case,
refinement .04s (.05s generic/missing debt), runner16.35s,RSS637,208KiB; cold
release setup dominates, no source build/covers/loop bounds. Console/prelude
hashes match the first run above. This proves only the baseline normal two-cell
generic lifecycle. Next extend it to actual ManuallyDrop temporary creation,
`&*tmp`, complete storage recovery and return to an initialized destination;
direct callback panic remains open.
