# Production-base compatible strict lifetime cut: design gate

This card records a conditional semantic design for the bounded native/C1
helper in [`DEPENDENCY-BLOCKER.md`](../sort4-native-compose-c1/DEPENDENCY-BLOCKER.md).
It authorizes no implementation, patch application, proof or Cloud dispatch.
The active C4 capture is independent and remains on its pinned inputs. Any
future implementation needs an independent addressed review of this exact
production-base direction before changing trusted verifier semantics.

## Exact base and difference from historical component

The production caller-entry base before its capture overlay is VeriFast
translator SHA-256 `4d3a190fcec695415b41162ddf8d71aec6e2826d2b69e7692df306a568add98c`
and `src/verifast.ml` SHA-256
`adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0`.
The existing capture overlay moves the translator to `4dc5f332d4c813fee966ef0724aa1f8ce0e6578ff1e15a0cb61bfb9719c6d14e`
without changing the kernel. Its complete original helper AST is
`64c01593d890907756c2e707e09adb9da80c6a1d0967a6720d2200defacf8b06`,
captured before any semantic rewrite and therefore not a pin for a new tool.

The historical [`verifast-strict-lft-cut-26.10.patch`](../../overnight-lifetime/verifast-strict-lft-cut-26.10.patch)
has SHA-256 `d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8`.
It starts from translator `6abe2aa920dfe9cc193d1331d0ee5e90310f2ac7609b03d92f3000959d5115bf`
plus the same kernel `adbf2c3...`, and produced translator `64a32e92e2f500abf41dcc3af796d0ca0351211fa14a6451f34d36dd1a1bcf51`
and kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
Those translator bases differ. The old patch and whole isolated C1/C2/C3
files are design evidence, not an applicable production-base delta. A new
patch must contain only reviewed changes to `vf_mir_translator.ml` and
`src/verifast.ml` relative to `4d3a...`/`adbf...`; record both resulting
hashes and its own SHA before a Cloud experiment. Do not copy unrelated
experimental code or silently import a different pointer-add lowering.

## Falsifiable obligation and proposed narrow semantics

The native helper's original `let_lft 'cmp = cmp_k` exporter block spans the
first callback and source-written `end_lft_binding::<'cmp>()` marker. Stock
lexical block exit does not check that a live heap chunk, outer variable type
or outer bound still mentions `'cmp`; treating the marker as `Noop` deletes
the obligation. The hypothesis is that a uniquely source-bound strict cut
lets the first callback's normal and direct-Continue unwind paths close their
debts, leave `'cmp` exactly once, recover fresh CURRENT pair/four-cell owners,
then satisfy the unchanged full original posts and leak checks. This feature
does not itself supply debt closure, owners, comparator purity or a callable
whole-sort4 summary.

The translator may recognize one exact parsed `end_lft_binding::<'cmp>()`
inside the sole matching exporter declaration block. It relocates that
block's synthetic end to the marker, retains the original brace dummy as a
checked no-op corresponding to its real exporter call, and emits an internal
`#strict_lft_binding_scope` first statement in the shortened child block.
It must pin function/source and full normal/readonly MIR/CFG for each actual
application, preserve real statement order and all normal/cleanup edges,
reject malformed/multiple/wrong/outside/nested markers, jumps into the prefix,
post-cut re-entry, an unmatched exit or unsupported exception continuation.
The source marker is not a token producer. Moving compiler temporaries into
the child scope is a separate exact source/MIR/pre-AST delta with a path-level
allocation, initialization, address-taking, StorageLive/Dead and free audit;
the native helper's eight temps cannot be moved by analogy with older fixtures.

At strict entry, the verifier snapshots outer type and bound metadata,
resolving/failing inferred aliases before they can conceal a scoped type.
At each normal, return, direct-unwind return and outgoing-goto exit, it frees
the same locals, restores the reserved lifetime fraction exactly once and
checks every surviving heap chunk type argument, outer-variable type and
current/entry outer bound for a scoped lifetime. It rejects a live scoped
chunk or escaped type/bound, rather than silently filtering a chunk. Only
outer type-parameter **bound metadata** may be rebased to the immutable entry
snapshot after escape checks; heap terms, coefficients, owners and permissions
remain unchanged. Unresolved/cyclic inference and unsupported type forms
fail closed in this opt-in path. The ordinary no-marker path retains its
production semantics. No parser, spec, memory, prelude, SMT, exporter,
refinement, leak, validity or dead-code rule changes are proposed.

## Admission and regression gate

First capture fresh exact source, full normal and readonly MIR/CFG, unchanged
source/runtime correspondence and complete pre-rewrite AST under the new
two-file tool. The old Build4 AST hash is invalid for this profile. Verify
the helper's actual first `FnMut::call_mut` operands (source cells 1 then 0),
direct-Continue unwind, marker/block coordinates and all declaration
allocation/free effects. A source or tool mismatch must refuse before proof.

The isolated CUT matrix must include positive normal, early return, direct
unwind and outgoing-goto exits, plus ordinary no-cut/default-off replay.
Negatives must hit the intended obligation: live `'cmp`-typed heap chunk,
outer-variable and outer-bound escape, inferred alias, unresolved/cyclic
bounds, duplicate/consumed token, missing debt or owner, wrong marker, wrong
goto/CFG ingress or re-entry, and changed allocation/free effects. Parser,
setup and unrelated helper failures remain inconclusive. Preserve full
normal/direct-unwind source/F/destination posts, return/leak and dead-code
checks; paired MIR/refinement and source pins must pass. Regress the existing
C1/C2 mandatory unbound refusals, stock pointer-add lowering and frozen
production tests. A green fixture or VF0 does not accept the new trust rule.

## Cloud lane constraint and next decision

The current `o26-sort4-caller-entry` path applies `profile.json` overlays
through [`run-o26-refresh.sh`](../run-o26-refresh.sh), lines 367–411. That
allowlist accepts at most two **translator-only** patches and explicitly
freezes `src/verifast.ml`; it cannot carry this two-file component. The
historical `o26-strict-cut-controls`/`run-cut-relocate.sh` lane does create an
isolated tool and apply the exact old `d557...` kernel patch, but it pins that
patch and older callback fixtures, not a new production-base delta or native
helper proof. Reusing it unchanged would be a profile mismatch. The nearest
infrastructure pattern is an isolated Cloud tool copy with an explicit
two-file patch allowlist, base/result hashes, frozen remainder and controls;
it needs a separately reviewed recipe/profile and cannot be smuggled into
the translator-only overlay. The current owner assignment explicitly authorizes this separate narrow
profile and minimal recipe changes. Main chooses an isolated two-file driver
under the new `o26-compatible-strict-cut-test` lane; it inherits the exact
reviewed caller-entry production base, never the old overlay allowlist.
Independent exact delta and runner review must precede its Cloud experiment. If the new strict check exposes a
real live borrow or bound at the helper cut, repair the source resource
protocol; do not bypass the check.

Addressed independent design review: add a mandatory marker-bearing source
control with the strict opt-in OFF. It must refuse before target proof; ordinary
no-marker default-off VF0 alone does not establish this. The new profile must
record the first refusal stage/location and distinguish admission refusal from
a semantic negative. Main accepts this addition to the narrow design.

Main implementation contract 2026-10-10: design review read and marker-OFF
gap addressed before isolated two-file adaptation. Separate driver freezes
production input, applies the explicit exact two-file delta only to an isolated
copy, rebuilds console in Cloud, captures fresh fixtures, records required
NOT_RUN gates and assigns no native/downstream credit. Primary C4 remains
pinned. Cloud dispatch remains gated on exact patch/runner review and account.
