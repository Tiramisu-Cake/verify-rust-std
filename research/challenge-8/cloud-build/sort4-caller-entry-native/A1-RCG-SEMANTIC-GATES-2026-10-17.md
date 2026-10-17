# A1 R/C/G — pre-implementation rationale and gates

Recorded 2026-10-17 before candidate implementation. Direct owner authorization
accepts common checked trait-contract route for this bounded experiment, not A1
completion. Owner select-sort4, branch research/night-select-sort4-cloud-2026-10-09,
initial HEAD 39c73ebb391ec9432644338f84f3cfd453d990a0. Policy read: WORK-POLICY
2026-10-10 plus uncommitted owner Evidence Brief revision 2026-10-17, preserved.

Session T0 00:28:49Z, main deadline 02:28:49Z, finish-only 02:58:49Z.
Separate [ledger](BUDGET-A1-TRAIT-CONTRACT-2026-10-17.json): 960 Cloud seconds,
one Build, timeout <=900s plus existing 60s queue reserve, no retry/carry.
Existing v3 coordinator and stable owner retained. Do not submit until independent
review, complete matrix implementation and exact proof/infra/tool/profile pins.
If not ready, checkpoint without spending a Build.

## Hypothesis and semantic rationale

For unrestricted T the common post 16 <= threshold <= 32 follows from both
actual implementations. Selection of one concrete Instance is unnecessary.
The trait summary must become available only after both actual threshold bodies
and their conformance obligations succeed at the same source/tool version.
The generic source call and original guard then establish len<=32 and
len+16<=48 (with native usize overflow checks). No supplied length bound,
Freeze/Copy/nonzero/purity/no-panic restriction or implementation redirect.

R transports compiler generic and region identities, method F and complete
clauses through schema, exporter, decoder and translator. A region identity is
scoped by owning item/binder depth/index/kind, never by printable name. Declaration,
input types, clauses and substitutions use one consistent map. Native duplicate
parameter checks stay enabled. Preserve three distinct input borrows, comparator
HRTB/FnMut tuple and Output=bool, normal/unwind and native safe obligations.
Unknown/malformed identity, scope or clause must fail closed.

C adds the safe threshold post in conjunction with the generated native contract,
including both outcomes. Each distinct impl item has a distinct compiler identity;
default and Freeze may not collide through printed Self=T. Existing unchanged
kernel conformance machinery may be used only with verified substitutions and
pre/post variance. No assume_correct, focus-skipped body or admitted stub can
publish a summary. If translator adaptation cannot discharge these conditions
with the frozen kernel, stop with NO-GO; do not change kernel semantics.

G preserves the original trait-item callee, generic arguments, regions and clauses.
For this certified item reject legacy clause-ignoring specialization and mixed
selected/common flags. Source certificate binds exact trait/impl/caller bytes,
full closed implementation inventory and identities; it is not proof evidence.

Full small_sort interface is inspected only. No unproved small_sort summary is
consumed. Diagnostic observer cuts before small_sort and non-base continuation
must remain explicitly distinguished from actual full caller/helper proofs.
Kernel, memory/alias/layout model, prelude, refiner, runtime std and signatures
are frozen. A2, ZST/resource redesign, C5/copies and sort8 are excluded.

## Mandatory gates and outcome decisions

The entire [first matrix](A1-FIXTURES-UNRUN-2026-10-12.md) is required:
OFF; P0a/P0b actual threshold body/conformance; P0c generic bound/overflow;
P-dispatch actual translated trait call; P1 full interface/export/decode/refinement;
N-binder-collapse, N-alpha-valid, N-free-region, N-region-swap, N-no-F, N-clauses;
N-default-contract and N-freeze-contract at intended result<=32 post;
N-false31 at caller assertion; N-source, N-binding, N-clause-redirect, N-duplicate;
and fresh R1–R7 (canonical T/MU, pointer positive, threshold positive,
wrong pointer, missing raw rights, MU cast without initialized T).

Early frontend/source/refinement failure of a body/assertion negative is
INCONCLUSIVE, never intended negative credit. A mutated impl control has its own
explicit mutation certificate so it reaches conformance instead of source refusal.
Unverified/bad impl summary availability requires an explicit blocking gate.
Any missing case, missing outcome or redirect prevents acceptance. A failed
positive identifies the next local scope fix; no second Build is authorized.
Successful full first matrix establishes only threshold/interface hypothesis.
A1 requires subsequent actual small_sort-to-helper transfer; A1/A2 remain open.

Review must inspect R/C/G and matrix/summary ordering, certify exact pins, and
resolve in-scope findings before submit. Terminal reporting exclusively through
smallsort-brief BUILD_UUID; raw evidence including local archives/logs is forbidden.
No Brief => reporting limitation, no proof upgrade or raw fallback.

## Focus attribution refinement (source review, before gate correction)

The frozen translator gives `Ast.Func.loc` the compiler `Body.span`; native
contract assertions use `fnSigSpan` separately. The unchanged kernel checks
header compatibility at `check_focus l l` and the body at `check_focus l close`.
Consequently a lexical declaration/fnSig line cannot establish either gate
unless it equals the actual MIR span start. The C guard must authorize only
`Body.span.lo` for threshold proof; caller focus/receipt must use the actual
observer Body.span start from the same full compiler inventory. The backend
must compare the complete function interval and select exactly one body and
its numeric prototype before any body/conformance attestation. This changes
only the opt-in admission guard, not focus/body filtering or kernel semantics.
The caller stage must reject a small_sort call inside the diagnostic observer;
P1's separate original caller remains interface-only. No unproved small_sort
summary may be consumed by the threshold observer.
