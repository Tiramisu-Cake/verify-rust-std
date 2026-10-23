# R22 diagnostic target helper design (inactive)

## Defect and applicability

The R21 fractional proof classifier deliberately leaves the four
`checked_forget_owned` controls unclassified and has only a line-derived target
for the three same-site controls. R22's control-target proposal identifies
candidate failure obligations, but its line/column/message observations are
not accepted R23 pins. Symbolic verifier names in those messages may vary.

This helper only validates an externally supplied fresh target map against the
exact source bytes, tool `lib.rsspec` bytes, and a verifier log. It does not run
or classify proof stages, establish semantic proof credit, change the existing
classifier/entry/audit, or publish a target map. Stage/source-before/source-after
binding stays with the existing classifier.

## Invariants

- Exactly the seven named negative controls are represented, each with its own
  variant label and exact `source_sha256` and `tool_spec_sha256`.
- The four callee targets derive their line from the unique exact generic
  `checked_forget_owned` signature, variant-specific contract, and body. The
  owner-loss target derives from the exact body end.
- `no-retained-half` derives its line from the unique full-cell assert after the
  retained-half merge marker.
- The two `omit-*` targets require the exact tool spec bytes, fixed rows 462/463,
  exact source precondition lines and row identities. The tool-spec diagnostic
  path is either the explicit relative `bin/rust/std/lib.rsspec` or the exact
  `tool_home/bin/rust/std/lib.rsspec` path supplied by the caller; no basename
  or suffix normalization is used.
- A target map is only an observed diagnostic record, never proof acceptance.
  Every target must include a complete one-line error message and exact
  file/line/column range. The log must contain exactly one error/fatal
  diagnostic and match the selected row in every field.
- Missing/null/wrong-type/unobserved maps, extra rows, duplicate/missing source
  anchors, stale source/tool hashes, wrong row/anchor/location, and extra
  diagnostics fail closed.

## Controls

The seven controls are `callee-false-normal`, `callee-owner-duplicate`,
`callee-owner-loss`, `callee-thread-duplicate`, `no-retained-half`,
`omit-selected-own`, and `omit-unselected-own`. Synthetic tests exercise each
row with invented messages and source/tool bytes; they do not encode R22
observations or claim Cloud evidence.
