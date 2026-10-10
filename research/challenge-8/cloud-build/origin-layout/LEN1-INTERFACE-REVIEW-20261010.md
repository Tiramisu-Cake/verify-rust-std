# Independent addressed review of the next len1 interface

Readonly review observed during the 2026-10-10 12:58:04 UTC merge session,
after the two-failure compile reassessment. No verifier/proof was executed.
Compilation and the minimal layout/StorageLive bridge remain prerequisite;
this note adds no functionality or proof credit.

The nearest existing target is `onecell-drop-interface.py::run` case
`canonical_positive`. It constructs a nonempty concrete CopyOnDrop own with
len==1, source quarter permission/CURRENT value, destination gap and payload
separation; generated full FBC/own is opened in the safety proof, singleton
arrays are derived, the source-linked Drop body is called through checked
`call()`, and its normal effect is closed with full posts/return/leak. At best
this establishes a bounded canonical interface fragment. It does not exercise
an actual insertion caller, compiler Drop terminator/glue, or panic cleanup.
`direct_positive` alone would be a strong-pre body proof. The guard constructor
full-FBC false-entry control stops before mutable reopening/call/effect and is
not caller credit. Historical half-FBC readonly framing does not settle that
mutable transfer.

Before accepting canonical credit, address the following admission debts:

- `_mir_gate` currently checks fields and copy but not the exact compiler
  concrete-layout qualification. Add source-bound DefPath/hash, target64 and
  layout metadata equality to the corresponding AST Struct attribute, using
  the exact specialized source defSpan. A standalone Drop has no caller tmp
  or guard StorageLive, so do not reuse their existence as a premise here.
- `_effect_ast_gate` checks generated normal effect calls and absence from
  unwind, but not the effect definition. Check one precise defined predicate
  instance with exactly four inputs and structural len1, source quarter and
  initialized destination sharing one existential CURRENT, u64 own and one
  type interpretation; source text alone is not an AST definition binding.
- `qualification_rejection` must look for the exact malformed-effect
  diagnostic in translator/verifier stage `verifast.log` with exporter,
  decoder and refinement success and verifier exit1. It currently looks in
  exporter/decoder stages. Preserve exact intended causal failure.
- `canonical_no_effect` must require the intended residual-resource/leak
  refusal, rather than accepting any error after copy/return/leak markers.
- `run()` returns `accepted:false` and cases but no `all_matched`. A driver
  must require the exact twelve case names and expected classifications.

Any classifier-only repair must first pass saved/synthetic replay; a changed
proof/source requires a fresh exact-SHA Cloud run. No own=false compatibility,
arbitrary accepting predicate, assumed Drop summary, or unwind contract on a
nonpanicking body may supply missing canonical/caller/glue credit. DefPathHash
is opaque compiler provenance, not a hash independently computed from source.
