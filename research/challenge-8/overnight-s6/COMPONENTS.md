# S6 transfer artifact and next hosted gate

`verifast-s6-26.10-candidate.patch` is a **cumulative experimental candidate**
against VeriFast source `f76012fb518703b1d98e243ac4f487f16877cfcb`.
SHA-256: `38f8797a7a64d0f8b0992b73cd2741e1d3a4a5e1eef1ba83ddd670abfe4a07c1`.
It modifies only `bin/rust/std/lib.rsspec` and
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`. `git apply --check`
passes on that source pin; no build or verifier was run locally. It is **not an
accepted profile** and must not be used as an actual-helper summary yet.

The four semantic components are explicit in the translator modules and hooks:

| Component | Definition / trust and applicability | Local checked target |
| --- | --- | --- |
| Constructor | `Sort4MaybeUninit`, aggregate and external-new redirects; `MaybeUninit_pointer_own` is a defined predicate | Exact local `sort4_checked_maybeuninit_new` body and complete typed MIR certificate |
| Storage pointer | `Sort4AsMutPtr`, exact external method redirect | Exact local `sort4_checked_as_mut_ptr` body and complete typed MIR certificate |
| Intrinsic values | `Sort4SelectIntrinsic`, two type-exact compiler value rules and defined wrapper ownership transfer | Pointer and wrapper fixture bodies; `select_MaybeUninit_pointer_own` lemma |
| Pointer drop | `Sort4PointerDrop`, exact raw-pointer-payload compiler glue rule only; `ptr::drop_in_place` and new `drop_glue` source certified separately | Exact method fixture and `pointer_drop_glue_identity` lemma |

The new source pins are content-reviewed: `MaybeUninit::new` body and union
fields, `as_mut_ptr` body, intrinsic attributes/fallback, method adapter, free
drop adapter and lang-item placeholder were examined at std `cd371e03`.
The patch repins full files and checks local fixture body/contract spans and MIR
identity. This broad full-file pin deliberately fails closed if adjacent std
content changes, even where the operation body stays stable.

The old S6 strict MIR graphs are retained as a **diagnostic starting point**.
The 26.10 nightly may change local/block counts or cleanup edges, so no exact MIR
applicability conclusion is inferred from `git apply --check`. A fresh hosted
export must capture each complete NORMAL and readonly MIR before amending those
gates. Source/MIR mutation controls must still reject after any amendment.
The current patch also retains old exact actual-helper/projection certificates;
they require separate 26.10 MIR and ghost-coordinate review before actual use.

First hosted diagnostic: build the pinned 26.10 source with this patch in the
existing workflow and invoke `diagnose-s6.py` (defaults to all five isolated
fixtures). It makes constructor, as_mut_ptr, both intrinsic types and pointer
drop fixtures independently. Each fixture records full NORMAL and readonly MIR,
stage logs and first certificate/proof error even when a previous family fails.
It never calls a component accepted. Keep its whole evidence tree as artifact.
Amend one component's exact graph from the observed MIR, then run its complete
positive/negative/admission matrix, preserving the others as fail-closed. After
each component gate passes, repeat previously accepted components on the
resulting cumulative profile. Run the old five unfinished pointer-drop
admissions before calling that component accepted.

Hosted CLI after applying this patch and rebuilding only the console:

~~~bash
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
python3 research/challenge-8/overnight-s6/diagnose-s6.py \
  --tool-home "$source_home" \
  --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" \
  --evidence "$evidence/s6-diagnostic"
~~~

This collector returns zero after writing a complete diagnostic summary even
when individual fixtures fail; the summary always marks `accepted_component`
false. Its hosted-only guard rejects server execution. Do not use the old
checkers' acceptance summaries as proof until fresh complete matrices run.

The old runner `run-select-pointer.sh` pins VeriFast 26.09 and the February
nightly; it must **not** dispatch this candidate unchanged. Use the stock 26.10
archive/source/rustc/schema identities in `run-stock-2610.sh` and its effective
spec audit; rebuild only the patched console, keep stock exporter/refiner, and
record exact tool/spec hashes. The copied component/classifier scripts here have
repinned exact 26.10 source files and load each other from this directory. Their
strict old MIR expectations are retained. They need updated 26.10 MIR mutation
spans after the first capture. This gate is a hosted executable action only.
