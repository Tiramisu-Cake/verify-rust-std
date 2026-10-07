# OVERNIGHT-SELECT-SORT4-26.10: S6 transfer review (before implementation)

Status: **design and static source review only**. No 26.10 S6 component is
ACCEPTED until a fresh exact-SHA hosted matrix checks source, full typed MIR,
proof negatives, refinement, and full verifier/dead-code/leak gates. Historical
S6v4 acceptance stays attached to its 26.09 proof SHA and patch.

## Obligation and proposed semantics

The unchanged actual `select_unpredictable` helper in
`library/core/src/hint.rs` constructs two `MaybeUninit<*const Element>` values,
takes mutable storage pointers, selects pointer and wrapper values, and drops an
unselected raw-pointer cell. The S6 transfer supplies four narrowly certified
components, in dependency order:

1. `MaybeUninit::new<*const Element>` is a checked, source-equivalent constructor
   body. The defined `MaybeUninit_pointer_own` predicate owns only the raw
   pointer **value** and no `Element` cell. The ManuallyDrop wrapper remains a
   trusted compiler representation correspondence.
2. `MaybeUninit<*const Element>::as_mut_ptr` is a checked, source-equivalent
   two-cast body. It preserves the same storage cell/borrow and complete pointer
   identity; it creates no initialized cell or pointee rights.
3. The `std::intrinsics::select_unpredictable` rule applies only to
   `*mut *const Element` and `MaybeUninit<*const Element>`. It returns the
   selected **complete value** and discards the other input as specified by the
   compiler intrinsic. The wrapper ownership transfer uses a checked lemma.
4. `*mut *const Element::drop_in_place` is a checked, source-equivalent method
   adapter. Its free callee is now `ptr::drop_in_place`, whose runtime source
   creates `&mut *to_drop` then calls compiler-replaced `drop_glue`. Only the
   resulting exact raw-pointer-payload compiler glue may use a checked identity
   lemma: initialized `*slot |-> value` and thread token are returned unchanged,
   with no unwind or Element rights. The Rust-to-glue identity is **trusted**;
   the lemma itself proves resource preservation only.

No rule is generalized to arbitrary `T`, Drop, MaybeUninit initialization,
provenance-free numeric addresses, or a generic helper postcondition. The runtime
algorithm and std signatures remain unchanged. All normal and reachable unwind
paths remain in MIR; no verification gate is disabled.

## Source review at cd371e03 / tool f76012fb

The new repository std preserves the constructor body
`MaybeUninit { value: ManuallyDrop::new(val) }`, union fields `uninit: ()` and
`value: ManuallyDrop<T>`, and the `as_mut_ptr` two casts. `ManuallyDrop<T>` now
contains `value: T` directly. The intrinsic still has `rustc_intrinsic`,
`rustc_nounwind`, and `miri::intrinsic_fallback_is_spec`; its fallback remains
`if b { forget(false_val); true_val } else { forget(true_val); false_val }`.
`ptr::mut_ptr::drop_in_place(self)` remains the free-call adapter, but the free
function is no longer the compiler lang item: it calls `drop_glue(&mut *to_drop)`.
The `drop_glue` lang item has a compiler-replaced empty source body. An old
certificate that identifies free `drop_in_place` as the glue must fail closed.

Old cumulative patch `verifast-select-pointer-drop.patch` fails `git apply
--check` against 26.10 at translator old line 2873. Even a context-adjusted
application is insufficient: its old repository MD5 pins and exact typed MIR
graphs belong to the previous compiler. The updated direct MIR must be captured
on GitHub-hosted execution and compared with explicit expected shapes before
enabling any redirect. The new intrinsic source full-file hash differs, while the
reviewed declaration/fallback match by text; this is the reason to repin and
retain a body/attribute certificate.

## Trust boundary and regression gate

Trusted: exact std/exporter/compiler correspondence to the source; pointer-value
and transparent wrapper representation; the two exact typed intrinsic value
specializations; compiler drop glue for a stored raw pointer. Checked: resource
lemmas, constructor/as_mut_ptr/method adapter bodies, MIR/source admission,
normal/unwind posts. The refiner and memory model remain enabled and unchanged.

Hosted gate, one profile at a time: stock 26.10 u32/raw/ordinary-unwind/shared
cleanup positives and intended false-post/dead-code negatives; constructor
16+9 MIR+14 baseline, as_mut_ptr 9+17 admission, intrinsic 16+40 admission,
pointer drop 2 positive+11 proof negatives+22 source/MIR/pin admissions.
Each negative must fail at its declared certificate or proof obligation; setup,
frontend, unrelated body, and timeout are INCONCLUSIVE. Check NORMAL and readonly
export/decode, complete typed MIR/CFG including cleanup, full verifier body/return/
leak/dead-code, refinement, source hashes, exact overlay SHA, and runner artifacts.
The old pointer-drop tail (`mir_cfg_unwind`, `mir_extra_operation`, `mir_contract`,
`method_source_pin`, `glue_source_pin`) must be completed rather than inherited as
PASS. No S6 component is usable by actual linkage before its same-profile gate.

## Diagnostic implementation boundary

The copied `diagnose-s6.py` runs one canonical positive for each family on a
GitHub-hosted runner and preserves separate full NORMAL/readonly MIR. Every
family has its own fixture, so a failed constructor strict-MIR gate does not
prevent as_mut_ptr, both typed intrinsic forms, or pointer drop from reaching
their own certificate. The copied scripts repin the reviewed std files;
`ManuallyDrop`'s direct `value: T`, the intrinsic fallback/attributes, and the
new free-drop-to-`drop_glue` source path are checked explicitly. The old exact
MIR graphs are intentionally unchanged until fresh hosted data supplies a
content-reviewed replacement. Collector output is `DIAGNOSTIC_ONLY` regardless
of apparent proof success and cannot be promoted to component acceptance.

## O2 setup failure and localized compiler API repair

Hosted O2 run `37699058032`, proof SHA `b8cc3cfa` spent 89 job seconds and
stopped while compiling the patched translator. No S6 fixture ran. The first
error was `Unbound value D.decode_predicate` at translator line 8536.
VeriFast 26.10 changed the decoded MIR obligation container from `Predicate`
to `Clause`; stock translator uses `BodyRd.clauses_get_list`,
`BodyRd.impl_block_clauses_get_list`, `AdtDefRd.clauses_get_list` and
`D.decode_clause`. The 26.10 schema retains a `Clause.Trait` record with
`defId`, generic `args`, and `boundRegions`. The repaired candidate replaces
only the obsolete accessors/decoder at all S6 checks. It keeps each exact
`Sized<Element>` or `Sized<T>` trait match, sole clause count, empty bound
regions, and no impl-block clauses. This is a schema/API adaptation, not a
weaker applicability gate or a new trusted value rule.

Static review found all eight `D.decode_predicate` call sites, six body and
two ADT lookups plus six impl-block lookups; no obsolete names remain in the
candidate. The patch still passes `git apply --check` against stock source
`f76012fb`. A fresh hosted build is required; O2 supplies no proof result.
