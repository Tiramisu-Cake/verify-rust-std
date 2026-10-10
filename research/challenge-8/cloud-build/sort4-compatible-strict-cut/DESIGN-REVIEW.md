# Independent design review: production-base strict lifetime cut

**Verdict: conditional GO for this narrowly scoped design, not implementation
or dispatch.** The card directly addresses the dependency blocker: a translator
splice and a source marker lowered to `Noop` do not prove that `'cmp` has left
all heap/type/bound state. The proposed verifier rule supplies that missing
escape check while preserving the helper's full normal and direct-unwind
contracts. It does not create ownership or assert comparator properties.

I compared
[`COMPATIBLE-STRICT-CUT-SEMANTIC-CARD.md`](COMPATIBLE-STRICT-CUT-SEMANTIC-CARD.md)
with
[`DEPENDENCY-BLOCKER.md`](../sort4-native-compose-c1/DEPENDENCY-BLOCKER.md)
and the historical
[`verifast-strict-lft-cut-26.10.patch`](../../overnight-lifetime/verifast-strict-lft-cut-26.10.patch).
This was a read-only design review; no implementation, patch application,
Cloud dispatch, compiler, verifier, or proof was run.

The proposed scope is appropriately narrow. It pins the production caller-entry
translator/kernel bases and distinguishes them from the historical patch's
different translator base. The historical component is used as design
evidence only; the card requires a new translator-plus-`src/verifast.ml` delta,
new resulting hashes, and a fresh capture. Its verifier checks cover resolved
outer type/bound snapshots, local-name shadowing, live heap type arguments,
outer local types, current and entry bounds, and fail-closed unresolved/cyclic
inference. It rejects live scoped chunks rather than filtering them, limits
rebasing to outer bound metadata, and leaves heap terms, coefficients,
permissions and owners unchanged. It also covers normal, return, outgoing-goto
and direct-unwind exits, with exception escape and unsupported CFG cases
refused. These decisions track the historical patch's security-relevant
structure without importing its unrelated translator changes or pointer-add
lowering.

The source-bound marker/cut contract is concrete enough to guide an exact
implementation: one parsed named marker inside the sole matching lifetime
declaration block, synthetic end at the marker, original exporter dummy
retained as a checked no-op, and an internal strict-scope marker at block
entry. The card calls for preserving real statement order/CFG edges and
refusing duplicate, malformed, outside, nested, entering, re-entering, or
unsupported exits. The separate source/MIR/pre-AST and path-level allocation,
initialization, address-taking, `StorageLive`/`StorageDead`, and free audit is
necessary because the callback tuple local may allocate even when uninitialized.
The fresh capture must re-identify the actual operands (cells 1 then 0),
marker coordinates and direct-Continue unwind; old AST/MIR pins cannot be
reused.

One small fail-closed case should be explicit in the gate before implementation:
when a marker-bearing input is processed with the strict-cut opt-in **off**, it
must refuse before target proof rather than lower the marker to `Noop` or emit
the internal scope marker. The matrix currently names ordinary no-cut/default-off
replay, which protects the no-marker baseline, but does not explicitly state
this marker-bearing/off negative. Add it as a separate expected refusal and
confirm the source marker never becomes a proof credit path. This is a test
specification gap, not a reason to widen the semantics.

The test/admission plan otherwise covers intended positive exits and targeted
heap/type/bound, inference, marker, token, debt/owner, CFG and allocation
negatives; it preserves source/F/destination posts, return, leak and dead-code
checks, and calls out inconclusive setup failures. The Cloud path is also
correctly treated as a separate trust gate: the current profile only accepts
translator overlays, while the historical lane pins the wrong patch/base.
The card explicitly prohibits bypassing either allowlist and requires an
isolated recipe with an explicit two-file allowlist, pinned base/result hashes
and frozen remainder. Keep primary C4 capture pinned and independent; no
strict-cut delta may touch its inputs or claim its result.

Before implementation or any Cloud work, close the marker-bearing/default-off
test specification above, review the exact two-file production-base diff and
its independent trust rationale, and separately settle the Cloud transport
profile with the owner. Then require a fresh capture under that exact tool,
the full targeted CUT matrix, and regression of the frozen production tests,
pointer-add lowering and existing C1/C2 unbound refusals. A passing helper
fixture or VF0 result alone does not accept this semantic change.
