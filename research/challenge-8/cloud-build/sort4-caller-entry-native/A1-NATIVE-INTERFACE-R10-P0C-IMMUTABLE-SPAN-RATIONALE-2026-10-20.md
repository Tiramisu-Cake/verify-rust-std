# R10 P0c immutable caller-span rationale

The S2 Evidence Brief reported that the Build reached `positive-receipt-issued`
and then failed with `A1-FOCUS: source-bound caller MIR Body.span required
before focus`. The focus backend requires a source-bound MIR body location
before constructing the verifier focus argument. That guard is necessary: the
focus line must come from the decoded caller MIR and identify `verified/lib.rs`,
with ordered positive line bounds.

The call-binding observer returns its result through `_freeze`, which
recursively wraps dictionaries in `MappingProxyType`. Therefore the valid
`binding.mir_body_span`, and its `lo`/`hi` records, implement the Mapping
interface but are not `dict` instances. The focus backend's concrete
`isinstance(span, dict)` check rejects this immutable observer result before
using the already source-bound line. This cause is established from the two
source interfaces; it is not inferred from a successful verifier run.

The bounded correction accepts `Mapping` at each record layer and retains the
existing path and ordered-line requirements. It also copies the accepted span
into plain JSON-compatible containers before adding it to the raw observation:
the backend serializes that result with `json.dumps`, while the original
observer span is immutable and not JSON-serializable. Missing, null, scalar,
malformed, wrong-file, or invalid-bound values continue to fail with the same
focus guard. It does not derive or relax source identity, alter the
call-binding criterion, or grant proof/admission credit. An isolated synthetic
regression exercises the frozen observer through the actual span-selection
and emitted-observation serialization seam, plus malformed variants, without
running fixture preparation, a compiler, the full runner, or Cloud work.
