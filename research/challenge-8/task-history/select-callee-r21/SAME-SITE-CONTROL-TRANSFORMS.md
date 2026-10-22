# R21 same-site final-select control transforms

`overnight-assume-actual/r21_final_select_controls.py` is an inactive,
source-only byte transform. It accepts only already branch-selected repaired
bytes with the exact selected branch block copied from
`r20_final_select_repair.py` (source SHA-256
`3646b05602b7dce35cd4b2ab8f74d8cfe280d65df2637ac4f6cc0a128dd7e2a3`; block
SHA-256 `1b8f099d28b1f52b094a600e16b9040b0ca4c5daeca63c4d25717acdddc18c6e`).
It retains the existing single ghost `if/else`, both
`close_MaybeUninit::<*Element>` statements, the final select, and all source
bytes outside the removed lines.

The two variants remove these paired ghost ownership closes:

- `omit-selected-own`: omit `selected_payload` in both branches; the true
  branch retains `false_payload`, and the false branch retains `true_payload`.
- `omit-unselected-own`: omit `false_payload` in the true branch and
  `true_payload` in the false branch; each branch retains its
  `selected_payload` close.

The transform refuses non-bytes input, unknown variants, missing or duplicate
final-select anchors, missing/moved/duplicate payload bindings, a missing or
duplicate selected-payload binding, an altered/duplicate/pre-repaired/wrong
branch block, extra wrapper closes outside the exact block, and executable or
ghost-line text in the block-to-final-select gap. Tests verify that the
project's byte-preserving ghost stripper yields identical runtime bytes for
each control.

These are diagnostic controls only. Every future proof attempt must still bind
each control to its own exact source, body, and unit certificate pins and run
the same final-select wrapper obligation. A control supports the intended
negative result only if that exact obligation is reached and fails. Certificate
refusal, parse failure, timeout, `NOT_RUN`, missing rows, or any earlier failure
is inconclusive and cannot count as control confirmation. No certificate,
profile, runner, recipe, proof credit, or bypass is produced here.

## Validation

Ran `python3 -m unittest -v test_r21_final_select_controls.py` from
`overnight-assume-actual`; all 6 tests passed. They pin the source/block bytes,
check both exact transforms and ghost-stripped runtime equality, check which
payload is omitted in each branch, and cover malformed/duplicate/pre-repaired
inputs, wrong branch text, payload binding position/count, extra closes,
executable gap text, final-call anchors, and unknown input types/variants.
No preparation, extraction, compiler, exporter, verifier, reconstruction, or
Cloud service was run.
