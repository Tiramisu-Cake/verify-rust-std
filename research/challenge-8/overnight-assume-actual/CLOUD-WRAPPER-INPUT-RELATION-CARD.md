# O26 wrapper input-relation diagnostic (source only, not accepted)

## Problem and rule

Cloud 218568df admitted component 23 R2, verified the seven prefix callees,
and reached the outer return. The old wrapper-ownership failure was absent;
the first failure was the unchanged normal postcondition
`result == (condition ? true_val : false_val)` at verified source line 143.
This is evidence of a missing pure equality in the proof, not evidence that
the actual runtime returns the wrong pointer. The generic nested Drop body
was not reached before the outer failure.

This opt-in source candidate starts from the exact R2 verified source. Before
the Rust `let mut` declarations shadow the two input pointer names, two
single-statement ghost `let` commands save those inputs. After the existing
storage opens and payload assertions, two ghost assertions check that the
payloads equal the saved inputs. After both R2 wrapper-owner closes, five
more ghost assertions check `inner` of each current wrapper and each shadowed
Rust wrapper against its saved input, then check `inner` of the conditional
wrapper against the conditional saved input. Each command is a separate
`/*@ ... @*/` comment and an ordinary proof obligation. No assumption,
ownership chunk, pointer cell, or source-level premise is introduced.

The target remains the actual pointer-specialized outer function with
unrestricted implicit-Sized `Element`. Its original selected-pointer normal
postcondition and `on_unwind_ens false` remain exact. Runtime statements,
algorithm, generic signature, contracts, callee specifications, parser,
translator, kernel, memory model, exporter, refiner, leak/dead/validity checks,
and the generic nested Drop obligation do not change.

## Capture and refusal

The preparer requires the exact R2 source pair and inserts exactly three
byte-reversible regions at unique, ordered boundaries. It records all nine
new ghost comments, their order, bytes and source spans; ghost stripping must
recover the byte-identical original runtime source. The function inventory
and runtime intrinsic/forget/assume-init call counts must remain the same.
`--wrapper-input-relation` is a separate capture mode; the canonical and R2
preparers remain unchanged.

The first Cloud run is capture only: paired NORMAL and readonly MIR, refinement,
all nine decoded bodies, ten independently hashed Marshal records, and the
fingerprint collector refusal. The old owner17 refusal is predicted and is
not executed by this capture; it requires a separate later control. No proof profile may admit this source until
its new source/unit/body-7 pins, ghost metadata and typed graph have been
observed and reviewed as a separate R3 profile. A failed assertion identifies
the first unavailable pure link; an old-certificate refusal, setup failure,
frontend error, or unrelated helper failure is not an intended equality
negative. Component-17, A1 and SAFE-forget controls, same-version callee
proofs, full normal/unwind resources, and the generic nested Drop proof remain
required. `verification_accepted` is false for this diagnostic.

The two input ghost bindings are inline before the original four-space Rust
shadow declaration, without inserted newlines. This preserves the actual nested
Drop source spans165–170. The other eight body hashes are predictions until
Cloud capture independently checks them; no inferred hash is an admission pin.
