# Independent static tool review — 2026-10-12

Reviewed `/root/verifast-i-actual-glue` commit `059687f1` against the I base
`b6cb276a`, the pinned compiler-source excerpts and the package DESIGN. This
is a static admissibility review, not a verifier, exporter or refiner run.

**Decision: GO for the authorized C0–C2 Cloud Build gate.** A follow-up commit
`059687f1` closes the sole identified C0 admission gap: all four native mode
settings and their two bound controls now reject when the I profile is present.
The runner has one real C0 mixed control for each native mode. The full tool
tree `f299edd9b8c4e1283cb377b50681697de90d8a60` and additive patch SHA-256
`dc9950d5d5500dfbfae70b1c0ccd86b3e752b05294559e6b74acc4a8ecbc34de`
match the final manifest. The Cloud build, official refiner, full logs and
location-specific positive/negative controls remain required evidence.

* The exact profile is opt-in and rejects native, listed C3/C4, selector and
  generated-glue settings. With it absent, MIR StorageLive/Dead retain I's empty
  translation, layout attributes are not emitted, and Drop's stock normal and
  unwind posts are unchanged. No C3 routing, Instance observation or generated
  glue schema was imported.
* The exporter obtains a full source-byte SHA-256, local nominal identity,
  three compiler-typed fields and PostAnalysis layout from the pinned compiler.
  The translator checks complete metadata, exact source allowlist, compiler,
  target, width, field shape, size, alignment and nonoverlapping recorded
  offsets before issuing the internal attribute. The kernel checks the
  attribute and translated field types before asserting layout facts;
  duplicates reject. The 18 allowlisted digests match the committed positive
  and control source pairs; the changed-source pair is excluded. Compiler pin
  is also an external runner requirement because the exported commit field is
  a profile constant, not compiler self-attestation.
* MIR storage markers carry both the compiler local id and translated name.
  Body inventory, declaration binding and active env checks precede use. A
  fresh supported u64 local gets its real uninitialized resource first, then
  calls I's existing `points_to__limits` as a checked ghost lemma. Positive
  size and object bounds are queried before any numeric separation assumption.
  Incoming u64 chunks must be the exact body-entry heap object still present,
  have a positive non-dummy coefficient and checked object bounds. Active
  local separation is limited to simultaneously live u64 incarnations;
  StorageDead retires the marker and does not exclude later address reuse.
  The guard's 24-byte storage obtains qualified layout and liveness only; the
  tool does not assume a numeric guard-span exclusion.
* The I strict lifetime entry/exit checks remain in place. At strict exit the
  origin snapshot maps only via an old heap object's physical identity to the
  new frozen chunk, preserving symbol, coefficient, size and terms. A consumed
  or reconstructed resource cannot acquire the old origin by matching its
  address or contents. The mapping and storage context are restored per path.
* The normal Drop post gains a source- and type-qualified effect predicate
  only for the concrete checked CopyOnDrop method. The declaration and
  definition must occur in the guard source file with the expected arity and
  types. The generated unwind post keeps the stock field ownership and
  padding shape without the effect. The source Drop body and safety proof
  still have to verify; the effect is not an assumed callee summary.

The review caught an intermediate OCaml binding-order error in
`translate_adt_def`: `layout_attrs`, `is_local` and `kind_cpn` were used before
definition. The worker corrected it before `8d3ed7d1`; the committed version
binds all three before the layout check. The committed diff passes
`git -c core.whitespace=cr-at-eol diff --check b6cb276a..059687f1` (the tool
sources use CRLF). Compilation, proof results and actual first-diagnostic
classification remain Cloud-only and unobserved here.

## First Cloud failure and localized API correction

Cloud run `d02ccd21` at project SHA `1c1be000` stopped at exporter compilation
(`exit 101`), before any proof obligation. The saved `exporter-build.log`
reports three pinned rustc API mismatches: `SourceFileHash` and its algorithm
were imported outside the nested module, `Generics.params` is absent, and
`IndexSlice<FieldIdx>` rejects integer/usize indexing. Tool follow-up
`c23278c3` changes only these sites: fully qualified `rustc_span` names,
`own_params.is_empty()` plus `parent_count == 0`, and `fields.iter().nth(i)`
after the checked three-field length. It introduces no new trust fact or
profile path. The new tree is `3a2c16640c10958a5d185dc8d928c47950406907`.
Static review: **GO for one fresh Cloud run**; exporter compilation and all
proof gates remain unobserved for this corrected source.
