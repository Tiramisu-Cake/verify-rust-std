# P2 `*mut Element`: static inventory of const-only translator gates

Static `grep` over the applied translator (`vf_mir_translator.ml` SHA-256 `50a77b8d220178d0253df4def38c06b1e29e46d51389873e35db18198096fcf2`, reproduced in R22 by `git apply` of the pinned O26 20+2 chain, branch-selected and fractional patches on tool objects `f76012fb`). Line numbers refer to that applied file. Nothing here was compiled or run; no proof credit.

A `*mut Element` unit needs a separate closed opt-in at each gate below. Each one should be a parallel `*_mut` checker or take a closed mutability tag; widening any existing const check is not allowed. The default const route must stay byte-identical.

| Line | Gate | Const-only condition |
|---|---|---|
| 401 | `Sort4MaybeUninit.pointer_element` | `D.RawPtr {mutability = D.Not}` over `Param "Element"` |
| 418 | `Sort4MaybeUninit` constructor signature | `sort4_checked_maybeuninit_new<Element>(val: *const Element)` |
| 497, 502 | `Sort4AsMutPtr` signature/body | `&mut MaybeUninit<*const Element> -> *mut *const Element` |
| 544 | `Sort4PointerDrop.signature` | `slot: *mut *const Element` |
| 709, 711 | `Sort4SelectIntrinsic.ptr_signature` / `mu_signature` | `*mut *const Element`, `MaybeUninit<*const Element>` |
| 805, 810-ish | `Sort4A1Link.const_ptr` / `pointer_wrapper` / `local_shape` | `RawPtr {mutability=D.Not}` |
| 1544 | local union type check | "local union type must be MaybeUninit<*const Element>" |
| 3338 | `assert_inhabited` admission | "admitted only for *const Element" |
| 3696 | external `MaybeUninit::new` | "requires the sole *const Element argument" |
| 4515 | aggregate admission | "aggregate type is not *const Element" |
| 11152 | result-position text anchor | `"*mut *const Element"` |
| 12197, 12276, 12287, 12727 | actual `select_unpredictable` source-signature certificates | `true_val/false_val: *const Element -> *const Element` |
| 12980-12991 | checked select parameter/result text | `*mut *const Element` / `MaybeUninit<*const Element>` |
| 13243 | checked constructor input | "checked constructor input is not *const Element" |

The local-binding mutability matches (`MutabilityRd.Mut/Not` at 821, 9835, 9968, 10088, 10234, 10470, 11225, 11563, 11961) are about MIR local mutability, not pointer kind. They would carry over unchanged, but a fingerprint must confirm each one.

In addition, the actual-owner and nine-body admissions bind the verified-source SHA, the decoded unit and body hashes, the ordered ghost text and coordinates, the call inventory and the cleanup graph. All of these need fresh `*mut` pins from a Cloud fingerprint of a new source pair. The ghost text uses the VeriFast pointer type `*Element` for both kinds, so the ghost annotations may carry over byte-for-byte. Only the decoded typed MIR can establish that; it must not be assumed.

Next steps (each is its own reviewed candidate):
1. A source route that forks `prepare-actual-helper-capture.py::write_fixture` with only the three signature types changed, plus a ghost-strip identity check and a test that the const fixture stays unchanged.
2. A `*mut` fingerprint lane that runs no proof.
3. A mutable opt-in translator patch covering the gates above, with refusal controls for const/mut substitution and wrong depth.
4. A proof run plus the full matrix.

This order follows `../select-callee-r21/MUTABLE-CALLEE-NEXT.md`.

## Source-route progress (R22, static only)

Step 1 is committed but unreviewed and not on any route. It consists of `overnight-helper/prepare-actual-helper-capture-mut.py` and its test, 4 synthetic tests OK.

The writer loads the const preparer by its SHA `2c5ce72f…` and takes that preparer's exact fixture bytes. It replaces only the three signature types. It checks:
- ghost-strip identity;
- that the std body's only raw-pointer token is the generic `inner: *mut T` guard field;
- that the contract-text SHA equals `P2-INTERFACE.json` (`dc985de2…`).

Static check, run without any tool: `prepare-actual-owner-projection.py::candidate` was applied to the mutable pair and to the const pair. For the flag sets `{}`, `owner_post_completion`, `owner_post_completion+annotate_nested_drop`, `owner_safety_proof` and `owner_safety_proof+annotate_nested_drop+owner_literal`, the two outputs are byte-identical modulo the signature.

Still unchecked on the mutable route:
- the R20 repair and the R21 fractional/control transforms, because they act on the full nine-body unit produced by the capture chain;
- every translator gate listed above.
