# Callback borrow protocol — stock 26.10 fixture

This fixture isolates the resource protocol needed around the comparator call
in the pinned `merge_up` source. It is a diagnostic adapter, not an actual
callee proof. `callback-borrow-cases.rs` uses the exact stock VeriFast 26.10
RustBelt primitives and the separate `callback.patch` frontend/parser change.
No runtime source is altered; no local exporter, verifier, compiler, or test was
run while preparing this design.

The target fixture admits unrestricted `T` and `F: FnMut(&T, &T) -> bool`,
requires two initialized, distinct source cells with one `own<T>` each and one
`own<F>`, and keeps the actual merge comparator order (`right`, then `left`).
On normal return, its post returns each source's current valid value and the
callback's current state. The values are not equated to their entry snapshots,
so the contract admits safe interior mutation through shared references. The
unwind post asks for the same current source and callback ownership after a
callback panic. It does not assume the callback cannot unwind.

The intended ordinary path is:

1. Convert each source cell's current `own<T>` plus memory points-to chunk into
   `<T>.full_borrow_content`, then create a lifetime borrow and shared access.
2. Use `precreate_ref`, `init_ref_share`, and `close_ref_own` to model the two
   source reference locations and the typed tuple passed to `FnMut::call_mut`.
3. After the call, close each fractional `ref_initialized` borrow before ending
   the short lexical lifetime binding.
4. Call `end_lifetime`, `borrow_end` for each source, and reopen each
   full-borrow content to recover the latest `own<T>`.

This order is necessary: the callback may mutate a `Cell`-like value and then
return either Boolean. A later actual merge copy must read from the recovered
source cell, not reuse `left0`/`right0`. `copy_nonoverlapping` should receive a
read fraction for only the selected source bytes and full write permission for
the destination; its byte post must not create another `<T>.own`.

The main unresolved obligation is the exceptional edge. The explicit
`close_frac_borrow` commands and the lexical block exit occur only on normal
control flow. The fixture keeps the full `on_unwind_ens` goal, so the hosted
run must reveal whether stock MIR/VF unwinding automatically closes these
temporary-reference fractions and returns the lifetime token before checking
the enclosing unwind post. A failure at that point is the intended proof
rejection, not grounds to weaken the post. A later source-linked bridge may
place ghost cleanup after the actual MIR cleanup successor, after the
references are dead, but before unwind propagation. The old `end_lft_binding`
kernel experiment cannot be used unchanged: it rejects exception escape from
a shortened binding.

## Trust boundary

The stock primitive specifications (`begin_lifetime`, `borrow`,
`share_full_borrow`, `precreate_ref`, `init_ref_share`, `close_ref_own`,
`end_lifetime`, and `borrow_end`) remain trusted RustBelt contracts; this
fixture uses their declared domains and does not add an ownership axiom.
`callback.patch` changes only the exact generated tuple-2 ownership
representation and preserves a narrowly matched compiler-origin HRTB
`FnOnce::Output = bool` bound for the actual `FnMut::call_mut` invocation. It
does not grant pointer permissions or a callback effect guarantee. First run
this callback-resource fixture on the pinned stock VeriFast tree with
`callback.patch`. A combined W1+M2a run must keep the wrapping and callback
patches as separately hashed inputs against the same pinned VF tree; neither
patch's evidence substitutes for the other's obligations. Keep normal return,
unwind, leak, dead-code, and refinement checks enabled.

The distinct-address precondition is intentional for this first resource
fixture: it prevents accidentally requiring two separated full ownership
chunks for one cell. The shared/coincident-candidate model remains a separate
obligation, and must use one exclusive owner with shareable read access rather
than transferring ownership based on equal numerical addresses.

## Acceptance matrix

| Case | Required result | What it establishes |
|---|---|---|
| Generic `T`, generic `F`, arbitrary normal `bool` | Full body, return and leak gates pass | The two-reference tuple, HRTB call and normal borrow recovery compose without `Copy`, `Freeze`, or purity |
| Callback mutates an interior-mutable value before normal return | Post recovers current valid source ownership; no equality to the entry value | Fresh source ownership is available for a subsequent copy |
| Callback unwinds after legal interior mutation | Full unwind post returns current source and callback ownership; destination/cursors absent in this adapter | Whether stock unwind cleanup discharges the loan or needs a source-anchored cleanup bridge |
| Omit left/right source ownership or one reference initialization fraction | Intended points-to/ref-initialization obligation rejects | Both source reads require their own valid permission |
| Omit callback ownership | Intended `FnMut::call_mut` precondition rejects | Callback state is not manufactured |
| Keep a lifetime-indexed borrow/ref-initialization chunk at scope exit | Intended leak/lifetime-close obligation rejects | The lifetime cut cannot discard an open fractional access |
| Use coincident source addresses with two full `own<T>` resources | Fixture setup is rejected / precondition is unsatisfiable | Equal addresses do not justify transferring or duplicating ownership |

This adapter does not prove actual `merge_up`, `merge_down`, copying,
destination initialization, pointer/index associations, ZST behavior, or
bidirectional composition. Its result only selects the next lifetime/resource
implementation step for the exact-source proof.
