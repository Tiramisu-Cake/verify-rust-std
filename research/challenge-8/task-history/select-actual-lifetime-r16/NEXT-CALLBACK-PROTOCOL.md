# R16 next callback protocol (source/spec audit)

This is a read-only design note from the active Select project and pinned
VeriFast commit `f76012fb518703b1d98e243ac4f487f16877cfcb`. No compiler, Cloud
build, or tool worktree was used. Runtime target remains the exact
`sort4_stable` body: five `FnMut` calls, eight `select_unpredictable` calls,
four `copy_nonoverlapping` calls.

## What the existing proof resources establish

`a1-actual-body-c1.py` builds one c1 scope and a `comparison_debt<T>` that
contains two fractional `ref_initialized_` close tokens plus borrow-end tokens
for `right`, `right+1`, `right+2`, `right+3`. Its direct-unwind marker closes
that debt, calls `recover_pair(left,right)`, and its normal continuation closes
the same debt, ends `'cmp`, then recovers. `recover_pair<T>(left,right)` requires
`left == right + 1` and returns `right[..4]` with current `own<T>` for all
four values. This is specifically the c1 layout (`left=v_base+1`,
`right=v_base`). It discharges supplied resources; it does not establish that
the actual call's MIR arguments are those references.

`a1-actual-recover-four.rs` has the more suitable generic four-cell interface:

```text
pred callback_four_debt<T>(
  t: thread_id_t, k: lifetime_t, base: *T,
  left_ref: *T, right_ref: *T,
  left_fraction: real, right_fraction: real)

lem recover_four_sources<T>(base: *T)
  req thread_token(?t) &*& type_interp<T>() &*&
      callback_four_debt<T>(t, ?k, base, ?left_ref, ?right_ref,
                            ?left_fraction, ?right_fraction) &*&
      [1/2]lifetime_token(k);
  ens thread_token(t) &*& type_interp<T>() &*&
      base[..4] |-> ?current &*& foreach(current, own<T>(t));
```

The predicate carries both fraction-close tokens and all four
`borrow_end_token(k, <T>.full_borrow_content(t, base+i))`, `i=0..3`.
The lemma closes the two fractions, ends `k`, opens all four source cells,
and joins them. As with `recover_pair`, this is not a callback binding bridge.

Pinned `bin/rust/std/lib.rsspec` gives the required generic mutable callback
contract at `std::ops::FnMut::call_mut<'a>` (lines 44–50):

```text
req thread_token(?t) &*& *self |-> ?self0 &*& <Self>.own(t, self0) &*&
    <Args>.own(t, args);
ens thread_token(t) &*& *self |-> ?self1 &*& <Self>.own(t, self1) &*&
    <Output>.own(t, result);
on_unwind_ens thread_token(t) &*& *self |-> ?self1 &*& <Self>.own(t, self1);
```

For this source, `Self=F`, `Args=(&'cmp_i T,&'cmp_i T)`, and output is `bool`.
Thus each invocation can preserve a *current*, possibly mutated `F`; no
equality to entry `F`, purity, `Copy`, or `Freeze` premise follows. The current
`*is_less |-> less_i` and `<F>.own(t, less_i)` must flow into the real mutable
receiver and out as the call's `less_{i+1}` on both normal and unwind paths.

Pinned `rust_belt/general.rsspec` signatures used by the c1 setup are:

```text
close_full_borrow_content<T>(t, l)
  req *l |-> ?v &*& <T>.own(t, v)
  ens <T>.full_borrow_content(t, l)();
borrow(k, P)                    // lifetime_logic.rsspec
  req P(); ens full_borrow(k, P) &*& borrow_end_token(k, P);
share_full_borrow<T>(k,t,l)
  req type_interp<T>() &*& full_borrow(k,<T>.full_borrow_content(t,l)) &*&
      [?q]lifetime_token(k)
  ens type_interp<T>() &*& [_](<T>.share(k,t,l)) &*& [q]lifetime_token(k);
init_ref_share<T>(k,t,p)
  req type_interp<T>() &*& ref_init_perm(p,?x) &*&
      [_](<T>.share(k,t,x)) &*& [?q]lifetime_token(k)
  ens type_interp<T>() &*& [q]lifetime_token(k) &*&
      [_](<T>.share(k,t,p)) &*& [_]frac_borrow(k,ref_initialized_(p));
close_ref_own<'a,T>(l)
  req thread_token(?t) &*& [_](<T>.share('a,t,l))
  ens thread_token(t) &*& <&'a T>.own(t,l);
```

`open_frac_borrow` / `close_frac_borrow` and `borrow_end` return precisely
the access and restoration tokens consumed by the existing debt/recovery
helpers. The helper can be reused only after the actual source cells and
argument references have been tied to these resources.

## Per-call annotations and binding obligations

Use a fresh lifetime and fresh reference/fraction names at each call. Keep the
call expression, source order, CFG, selectors, and copies unchanged. Before
each call: establish all four current source cells as owned points-to facts;
close and borrow their full-borrow contents to retain four end tokens; share
only the two cells selected for this callback; `precreate_ref` the two actual
argument references in source operand order; `init_ref_share`, close each
`&'cmp_i T` own, close the `(&'cmp_i T,&'cmp_i T)` tuple own, and open the two
fractional initialized-reference facts. On normal and direct unwind, close
`callback_four_debt<T>` for that same `base=v_base`, end only that call's
lifetime, call `recover_four_sources<T>(v_base)`, and retain the current four
source owners before subsequent selects/callbacks/copies.

| Call | Exact source operands | Per-call source-binding obligation |
|---|---|---|
| c1 | `v_base+1`, `v_base` | Existing prefix has pair setup and extra borrows for cells 2/3; replace/prove its c1-only recovery against the generic four-cell debt if the shared path uses `recover_four_sources`. |
| c2 | `v_base+3`, `v_base+2` | Fresh scope after c1 recovery; bind refs to the second call's ordered MIR tuple fields. A prior source draft explicitly keeps operand order `(3,2)`. |
| c3 | `c`, `a` | Fresh scope after c2; prove the selector-derived pointer values are current source-cell addresses and bind them to the third call's tuple. Existing prefix draft uses `split_selected_four(v_base,t,c1,c2)`; it is not an actual MIR binding certificate. |
| c4 | `d`, `b` | Same, with ordered `(d,b)` tuple at fourth call. Existing draft's receiver/call order is `d,b`. |
| c5 | `unknown_right`, `unknown_left` | Same, but first prove the nested selector results are valid source-cell pointers and bind their ordered values to the fifth call. Source comments classify these as remaining input elements; that does not itself prove which concrete cell each is. |

For each `i`, the missing source/MIR certificate must establish all of the
following from exact function/body/call identities and def-use, not pointer
value coincidence: (1) the callback is the corresponding source call in
order; (2) its receiver is the real `&mut F` `is_less` place, so pinned
`FnMut::call_mut`'s current-`F` contract applies; (3) tuple fields 0 and 1
are the actual call borrows represented by `left_i_ref` and `right_i_ref` in
the same order; and (4) their referents are the annotated current source slots
or selector-derived source pointers. The certificate must reject a missing,
duplicate, displaced, reordered, or wrong-call annotation/unwind marker. The
current first-call marker mechanism is singular; c2–c5 need a distinct,
call-indexed consumer and proof that the direct-unwind marker is consumed by
that exact call.

The source review cannot certify the generated MIR borrow/tuple/receiver local
identities or prove callback result and panic-edge association; those facts
must come from the fresh complete source-bound MIR/AST consumer. In particular,
do not infer c3–c5 pointer identity from printed names, coordinates, booleans,
or equal addresses. If that consumer cannot bind a call's tuple borrow to the
two `precreate_ref` resources and source cells, the recovery lemma remains
unapplied and the full-body result is inconclusive. Preserve the existing
strict entry/exit, escape, initialization, leak, return, unwind, and no-false
post gates.

## Concrete next step

First extend the existing actual-body source constructor/consumer to admit a
unique indexed marker per actual callback and validate the complete ordered
receiver/tuple/borrow/source chain for c1 before generalizing. Keep helper
verification independent: prove `recover_four_sources<T>` once with its
current signature, and do not weaken it to accept free references or
unconnected debts. Then add c2's fresh lexical scope and marker and require a
same-build positive plus negative controls for wrong operand order, wrong
call index, missing debt token, and displaced marker. Only after those gates
pass should c3–c5 be added with selector provenance proven at each step. This
keeps the runtime body exact and lets each result report the verified callback
prefix without claiming full-body proof early.

## Clarification from the reconstructed R16 translator

The preceding binding gap is narrower than a missing call/unwind check. In
`/tmp/vf_mir_translator-r16-s2edited.ml`, `State.callback_unwind_marker`
(around lines 3270–3295) accepts only the exact nested ghost block containing
`__vf_callback_unwind_pair()`, a `comparison_debt` close with the expected
variable names, and `recover_pair(left,right)`. Marker discovery compares raw
and parsed counts. The actual-body opt-in then requires `sort4_stable`,
`verified/lib.rs`, the supplied exact file SHA-256, one marker, and the
R16 authorization/provider/strict-lifetime environment. This is a source-file
identity and shape gate.

At the following MIR call, the pending marker path checks
`std::ops::FnMut::call_mut`, two arguments (receiver plus tuple), a two-field
tuple type with shared references of one equal type and lifetime, and that
the method lifetime equals the argument lifetime. It also checks
`UnwindAction::Continue`, a normal target, enabled unwind translation, and
that the marker is immediately before the call. In actual-body mode, the call
must be at the configured c1 source line and be the first/only marked call.
The c1 argument-evaluation guard separately requires one typed `*const T::add`
with literal offset `1`, at that same line, and a normal successor. The
original add, callback call, and their existing successors are retained; the
unwind edge routes through a recovery label emitted in the epilog.

What these checks do **not** establish is the value/place identity of the
receiver or either tuple field: the marker's `left_ref`/`right_ref` are not
compared with the MIR call's receiver/argument operands, nor are those call
operands tied to source cells or selector results. The `FnMut` AST check is
structural: it does not match generic `F` to the actual function binder or
inspect the call's argument places. The c1 source line plus preceding
`add(1)` is useful selection evidence, but it is still not a receiver/tuple
def-use proof. Therefore the previous note's proposed same-build certificate
should be read as an additional gate, not a claim that the existing translator
has no callback or unwind validation.

Next gap after S3: preserve these existing checks, then add a fail-closed
callback binding certificate for c1 that compares the translated MIR `FnMut`
receiver and ordered tuple-borrow operands to the actual ghost `is_less`,
`left_ref`, and `right_ref` resources using local identity/def-use (not printed
pointer values). Also bind the first argument's source expression to
`v_base+1` and the second to `v_base`. Only after a positive and wrong-receiver,
wrong-operand-order, wrong-ref, and displaced-marker controls pass should the
consumer generalize to indexed c2–c5 markers and selector-derived referents.

### Kernel binding qualification

The preceding certificate gap concerns an independently inspectable
source/MIR receipt; it is **not** evidence that the verifier lacks a semantic
resource bridge. Pinned `bin/rust/aliasing.rsspec` at the same tool commit
provides:

```text
lem precreate_ref<T>(x: *T) -> *T;
  req true;
  ens ref_precreated_token(x, result) &*& ref_init_perm(result, x);

fn create_ref<T>(x: *T) -> *T;
  req ref_precreated_token(x, ?p) &*& [?f]ref_initialized(p);
  ens [f]ref_initialized(p) &*& result == p &*&
      ref_origin(result) == ref_origin(x);
  on_unwind_ens false;

fn reborrow_ref<T>(x: *T) -> *T;
  req [?f]ref_initialized(x);
  ens [f]ref_initialized(x) &*& result == x;
  on_unwind_ens false;
```

`reborrow_ref_<T>(x)` is the ghost shared-reference case: it preserves
`[f]ref_initialized(x)` and adds `ref_precreated_token(x,x)`.

In particular, a successful actual-body proof that consumes the
`ref_precreated_token`/`ref_init_perm` for a ghost-created argument ref can
establish equality with the kernel-created ref; this is not a new axiom or
unchecked bridge. Keep the two claims separate: the kernel's verified resource
flow may prove semantic equality inside the proof, while a fresh independent
source/MIR receipt is still needed to show which actual callback/ordered
operand sites consumed those resources. Do not require an AST local-name match
as a prerequisite for sound verification if the checked kernel proof already
establishes the equality; use the receipt/control gate for inspectable
call-site attribution and reject any path where the actual proof does not
consume the intended precreated-ref resources.
