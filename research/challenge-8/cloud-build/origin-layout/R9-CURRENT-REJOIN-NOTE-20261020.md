# R9 checked CURRENT rejoin frontier

This note records a source-level rejoin contract for the selected guard Drop
normal-return edge, including a normal return reached while already in cleanup.
It does not claim that a proof run established the resource sequence. The
checked half-share recovery is owned by the separate worker.

## Address and value contract

The Rust body in `library/core/src/slice/sort/shared/smallsort.rs:536–574`
keeps the original `tail` parameter at `begin + 2`. The mutable gap destination
starts at `tail`, then changes to `sift` after each copy. At the relevant
selected-Drop return it can be `begin` or `begin + 1`; it must never be equated
with the original `tail` merely because it was initialized from it.

The Drop effect supplies the *current* value at its checked destination, plus
the destination singleton and `<u64>.own(t, current)`. Given a branch-local,
checked pointer match for `gap_guard.dst`, the reconstruction has these two
shapes:

```text
dst == begin:     [drop_current, middle_current, right_current]
dst == begin+1:   [left_current, drop_current, right_current]
```

Each sibling value must be bound by opening its actual physical singleton;
`dummy54` and `value2` in the native receipt are names for current values, not
constants and not evidence of equality with entry `xs`. The receipts' zero
arrays at `begin+2`/`begin+3` are useful bounds/shape facts, but do not supply
the missing values or owners.

## Checked reconstruction available in the pinned model

`bin/rust/prelude_core.rsspec:259–291` defines `array` recursively from
physical `*p |-> value` chunks and provides checked `array_join`. Its join
lemma combines adjacent ranges only when their coefficients agree. For either
destination arm, the checked work is therefore:

1. Bind the already returned destination singleton/current value. Build1 shows
   the effect representation already expanded, so do not open an absent folded
   `CopyOnDrop_drop_effect`. If another exact edge retains a folded effect, its
   checked open is a separate representation step. Prove
   the actual equality `dst == begin` or `dst == begin + 1` from the current
   MIR locals/guard fields. Keep the original `tail == begin + 2` fact separate.
2. For each of the other two addresses, bind the value from its extant full
   `points_to`/singleton resource. Close a one-element `array` over that same
   physical resource. For the destination, use the singleton in the opened
   Drop effect. Do not create a value or owner from an address fact.
3. Join the ranges in address order with the existing
   `array_join::<u64>(begin + 1)` and `array_join::<u64>(begin)`. This yields
   `begin[..3] |-> cons(v0, cons(v1, cons(v2, nil)))` for the three values
   just bound, with no equation to the entry sequence.
4. Close one `own::<u64>(t)(vi)` and singleton `foreach(cons(vi,nil), own)`
   for each of the same three bound values, but only where the corresponding
   owner resource is present. Combine singleton foreach chunks using the
   checked `foreach_append` twice, in the same order as the array. The pinned
   `bin/rust/list.rsspec:178–190` declares `foreach_append`; it does not
   declare `foreach_join`.

The existing checked two-cell pattern is in `first-callback.py:48–57`: bind
actual current values, close their owners/foreach/arrays, join physical ranges,
then append the owner lists. It is a pattern for resource-preserving rejoin,
not a premise that the current three-cell owners already exist. The physical
array and logical owner list are separate resources: an opened
`points_to`/array singleton alone does not establish `own` or
`foreach(..., own)`. The outer function's unchanged normal and
`on_unwind_ens` posts require both the three-cell current array and its
three-value owner list, alongside the original thread/type/F resources.

## Current limit and implementation gate

The provided Drop-return snapshot identifies the effect-side destination
singleton, one sibling singleton named `tail0-2` with current binder `dummy54`,
one sibling `points_to` named `tail0` with current binder `value2`, and zero
arrays. That is enough to propose a physical three-cell `array_join` only
after native binding establishes which sibling addresses are `begin` and
`begin+1` on each edge and the exact share/array form of all three cells. It
does not, as stated, establish `<u64>.own` for both siblings or show that their
`foreach` resources survived callback cleanup. The Drop effect establishes
only the owner for its destination value. A `points_to` value cannot be
replaced by an entry snapshot or an invented `own` token.

Accordingly, the next checked change can be narrowly limited to a selected
Drop normal-return target hook that (a) binds the exact source/MIR Drop and
normal target, (b) proves the destination/sibling address ordering for each
admitted arm, (c) consumes each real sibling physical and owner resource once,
and (d) runs the above ordered array/foreach joins before preserving the
original cleanup target/`Resume` and outer posts. If the bound heap state lacks
either sibling owner/foreach resource, the current model/source interface is
insufficient for the full post; source-bound recovery must first identify the
checked existing owner-return path. Do not solve that gap with entry-value
equality, pointer-address assumptions, `assume`/`leak`, a new ownership rule,
or weakened cleanup/unwind posts.

## Concrete-u64 owner refinement while Build3 runs

Static source check: `translate_u_int_ty` in translator defines `own tid vs =
Ok (True loc)` for concrete u64; `rust_belt/general.rsspec:149` defines
`own<T>(t)(v) = (<T>.own)(t,v)`. Consequently this exact concrete candidate may
close `own::<u64>(t)(current_value)` through ordinary verification, as the existing
CURRENT_OWNER_REJOIN already does. A checked recursive source lemma can build
`foreach(current_values, own::<u64>(t))` from that concrete interpretation. This
is not a generic ownership rule or physical-cell inference, and grants no actual
proof credit before Cloud checks it. The actual current values must still come
from the existing physical array/cells, never from entry snapshot `xs`.

Candidate sequence after tmp recovery, if the exact next heap supports it:
assert physicaltail current; close its fullsingleton using existingemptytail;
join begin+1 thenbegin from matching existingfullsingletons; bind resulting3-cell
CURRENT list; call the separately checked concrete-u64 foreach lemma. Existing
F/thread/type obligations remain and later failures must be examined separately.
Do not apply this as a source change until the actual frontier is observed.

Checked-source lemma sketch (unexecuted, ordinary proof body required):

```rust
lem r9_current_u64_owners(t: thread_id_t, vs: list<u64>)
    req true;
    ens foreach(vs, own::<u64>(t));
{
    match vs {
        nil => { close foreach(nil, own::<u64>(t)); }
        cons(v, rest) => {
            r9_current_u64_owners(t, rest);
            close own::<u64>(t)(v);
            close foreach(vs, own::<u64>(t));
        }
    }
}
```

No lemma declaration without its checked body may be substituted. Any source
fixture using it needs exact profile/source closure and compatible controls.
