# StrictCUT Cloud controls before actual sort4 scope work

This is a bounded diagnostic for the frozen strictCUT kernel patch
`d557082b…` with the separate callback relocation patches `e7189430…`
and `fa862fe8…`. The verified Cloud build `bf77d8a1` showed full VF0 for
the isolated two-cell `callback_positive` after the mapped declaration
relocation, while its unrelocated baseline still stopped at
`verified/lib.rs(84,9-38)` on entry outer-type inference. The same source
pair and complete normal/readonly MIR passed export, decode and refinement;
the proof log includes the actual callback and both return/leak checks.
That is a fixture result, not acceptance of the kernel, relocation, any
general FnMut rule, or actual sort4.

The dedicated `o26-strict-cut-controls` exact-recipe-v1 Cloud lane first
recreates the unchanged O26 canonical source/MIR/refinement and proof
baseline, then runs `run-cut-relocate.sh` once in the same Build. Only a
full-VF0 relocated F-bound callback permits the separate control helper to
start. The lane requests no AST probe, actual-sort4 capture, owner/A1,
coordination, wrapper, or old trace diagnostic. A complete matrix is
classified `STRICT_CUT_CONTROLS_DISCOVERY_COMPLETE` at the outer audit while
all acceptance fields remain false.

The falsifiable control hypothesis is that the **same isolated tool source
and binary** used for that relocated positive still verifies the four
previously reviewed ordinary positive cases and rejects each of the twelve
reviewed negative cases at its named strictCUT obligation. Run exactly the
existing `overnight-lifetime/capture.py` against its exact `cases.rs` bytes:
`positive_basic`, `ordinary_unmarked`, `positive_early_return`,
`positive_direct_unwind`, and all twelve `negative_*` cases. Do not rerun
the old `positive_f_bound` matrix case; it is known to fail the original
outer-type inference, and the same-build relocated `callback_positive`
evidence is the distinct positive F-bound diagnostic. Run a separate fresh
`positive_basic --without-opt-in` source directory to test the off gate.
The tool must keep the CUT kernel, exporter, parser, schema, specifications
and stock dependency binaries byte-for-byte equal to the already audited
relocation tool. Only `capture.py`'s provider guard may be overlaid in the
disposable proof checkout, using its frozen bytes and real Cloud identity;
no `GITHUB_ACTIONS` impersonation is permitted.

Every case must retain the exact selected verified source, ghost-stripped
original, complete normal and readonly MIR binaries/text and SHA-256,
refinement result, full verifier log, all stage exits, first error and
target/callee headers. The direct-unwind case has a same-unit
`cut_maybe_unwind` callee; its proof header must precede the target, and the
target MIR must show direct `Continue`. The positive normal posts restore
their full lifetime token; the direct-unwind case restores that token on
both normal and unwind outcomes. The F-bound callback has its own stronger
normal/unwind post covering thread, types, two T cells/owners and F
cell/owner. Source/MIR or setup failures are inconclusive. A negative
counts only as a **candidate boundary** if export/decode/refinement pass,
the single first error matches the case's reviewed predicate, and the
relevant target (or admission gate) is reached. It is never an accepted
soundness negative merely because it exits nonzero.

The existing matrix has no same-profile exact full-MIR SHA or exact full
first-error line pins for its individual cases. This Cloud run records those
observations for subsequent review; it cannot invent them in advance.
The matrix also lacks explicit false-normal-post and false-unwind-post
negatives under this profile. Add those only after source/MIR/CFG and
expected proof obligation are reviewed in a separate card. Incoming CFG
edge, source-position, renewed StorageLive, outer-variable/bound/heap type
retention, nested bounds, alias/address escape, all-path liveness and
hidden heap-term controls are likewise OPEN. A stock block filter is
forbidden. The absence of those controls prevents accepted strictCUT or
actual-sort4 scope claims, even if every existing matrix case is green.
