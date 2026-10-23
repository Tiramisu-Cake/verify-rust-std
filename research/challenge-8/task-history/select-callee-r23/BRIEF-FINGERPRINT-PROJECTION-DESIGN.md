# R23 targeted fingerprint projection — design boundary

## Defect and applicability

The generic recursive walker used for the fingerprint-to-rows handoff follows
every Brief JSON child. The pinned R21 classifier consumes only a defined
subset of the S2d fingerprint, so walking unconsumed metadata (including MIR
detail and stage argv/diagnostics) costs extra Brief requests without adding
inputs to its pin calculation. This applies only to locally reconstructing the
fractional fingerprint record for the existing R21 `fingerprint_to_pins`
consumer. It does not change a Build, the classifier, or what any fingerprint
means.

## Invariant

Every value supplied to `fingerprint_to_pins` is copied exactly from an exact,
complete Brief observation tied to one unchanged build/file/index/archive
identity. Preserve request IDs and available coverage metadata. Use only
server-returned `next_offset` for container pagination; never infer missing
values or completeness. All consumed schema strings are bounded names, hashes,
statuses, or filenames. If a consumed scalar includes `next_value_start` or is
marked incomplete, fail closed. Narrow/manual Brief reads are required to handle
such a value; this projection does not assemble long strings. The result must
remain acceptable to the unchanged pinned consumer, which remains responsible
for strict proof-pin checks. Projection does not reconstruct or claim
completeness for omitted record fields.

## Distinguishing controls

Synthetic adapter tests must establish that the projection preserves every
field read by `fingerprint_to_pins`, is accepted by that unchanged function,
and fails when any required field is omitted/inexact/wrong-typed, a page or
response kind metadata disagrees with a required bool/number/string value, a
page or snapshot identity changes, a transport/Brief error occurs, or container
continuation metadata drifts between pages, a parent child-count disagrees with
the selected nested container, or array indexes are non-canonical. Include a
noisy unconsumed subtree and assert it is not visited; include partial and
incomplete consumed strings and assert refusal without requesting a string
continuation. The receipt must enumerate omitted fields/subtrees and retain
each Brief request identity; no live Brief reads are part of these tests.

## Scope

Inactive local service tooling only. No changes to validator, proof helper,
Cloud inputs, Build runner, recipe, source, or proof semantics. The projection
is suitable only as an input record to the existing strict `fingerprint_to_pins`
function; its existence and synthetic tests establish no evidence, source/MIR
binding, Build result, or proof credit.
