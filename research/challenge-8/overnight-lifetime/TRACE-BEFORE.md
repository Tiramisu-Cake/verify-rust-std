# O24 trace-only diagnosis of strict entry inference

O23's CUT candidate rejects `callback_positive` at the `let_lft` entry with
`Strict lifetime binding has unresolved inference in entry outer type`. The
source and MIR/refinement stages pass. The formal `is_less` input has a named
region, while MIR nonparameter temporary locals `_27`–`_32` have erased
regions and are declared at the top of the translator's AST, before the
actual CFG. NORMAL MIR shows their `StorageDead` at source line 103, ahead
of the cut marker at line 106. The strict block currently freezes **all**
outer `tenv` entries at source line 84, including those temporary
declarations. We have not yet proved which entry is the first failure or
that all six are dead on every normal/unwind path in both MIR modes.

A separate **trace-only** overlay on the experimental CUT console will print
the name and formatted type of each outer entry immediately before its
existing strict freeze call. It does not catch or change the error, adjust
types or inference states, produce/consume a resource, alter the return
value, suppress checks, or change CUT's default behavior. The code is gated
by `SORT4_STRICT_LFT_TRACE=1` and runs only when strict CUT is active. The
existing Rust type formatter reads `InferredType` states without assigning
them. This is instrumentation, not a proof or an accepted semantic profile.

Run it only on the unchanged, exact-source O23 `positive_f_bound` fixture
with the same full NORMAL/readonly MIR, refinement, contracts, and full
verifier options. The original O23 first error must remain at the same
strict entry obligation; the trace must identify the last visited outer
entry and show its erased/inferred type. Compare the trace console's
production/CUT sources, specs, exporter/decoder/refiner and compiled binary
hashes to the uninstrumented CUT console. Only `src/verifast.ml` may differ
in the trace overlay. No actual helper/sort4 or S6 proof is run on this TEST
console. Preserve both logs, exact source/body hashes, and first-error
classifications. If the error changes stage or predicate, the trace is
inconclusive.

This trace alone does **not** authorize skipping unresolved inference.
The smallest possible future sound CUT change would need a certified set of
specific dead/uninitialized MIR locals: every normal and unwind path must
kill them before the cut, with no subsequent StorageLive/use, address escape,
heap chunk or outer live value retaining their inferred type. The kernel
must continue to inspect all live outer variables, bounds and heap chunks;
source/MIR controls must reject a changed liveness or alias path. A generic
`allow unresolved` at entry or exit is unsound because later unification can
resolve an outer inference reference to the ending `'cmp` type.

## Prepared diagnostic overlay

`verifast-strict-cut-entry-trace-TESTONLY.patch` SHA-256
`bc129b381af7bfe8cd5ca56eef099d90312ad7695dbbf852864d0e28148a4c3b`
adds three print-only lines immediately before the pre-existing entry
freeze. It is checked against O23 CUT `src/verifast.ml` SHA-256
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`
with `git apply --check`; it must not be applied to production or added to
the accepted CUT patch. The variable name and formatted type are printed
before each original freeze attempt, so the final `STRICT-CUT-ENTRY` line
identifies the first failing outer entry without catching the exception.

On a separately built TRACE console, invoke the existing source/graph
capture with the trace environment variable and one pinned case:

```
SORT4_STRICT_LFT_TRACE=1 python3 research/challenge-8/overnight-lifetime/capture.py \
  --case positive_f_bound --tool-home "$TRACE_TOOL_HOME" \
  --out "$FRESH_TRACE_EVIDENCE" --deadline-epoch "$DEADLINE_EPOCH"
```

The capture program will exit nonzero because `positive_f_bound` still has
the O23 strict-entry error; preserve its generated case result, all logs
and MIR. The intended diagnostic requires the same first error
`Strict lifetime binding has unresolved inference in entry outer type` at
the same source line and no changed exporter/refiner/spec/schema/profile.
It must identify a name/type; a changed proof stage is inconclusive.
