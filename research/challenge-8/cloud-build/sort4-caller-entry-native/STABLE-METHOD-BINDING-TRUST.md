# Narrow selected stable method binding — rationale before patch

Session SORT4-CALLER-DERIVED-BOUND-CLOUD-2026-10-11, owner select-sort4.
Base translator21ca026ae3279ef7da9a8a482b5355fab4c39250dec553854509b1f8923f52c4,
all other inherited effective files frozen/experimental/unaccepted.
Actual pinned quicksort4a41df6b, SmallSort85c75bc9 and FreezeMarkerfa9eec29.

## Concrete problem / permitted scope

Existing compute_trait_impl_fn_specialisations matches generic args and emits
WARNING that clauses are ignored. A Freeze-selected caller theorem cannot use
that as admissible specialization evidence. Owner explicitly authorizes exact
threshold/small_sort source-bound bindings, not a general specialization model.
We propose an opt-in narrowly matched rule for StableSmallSortTypeImpl's threshold
method in one pinned standalone source fixture. Ordinary translation stays
unchanged when disabled. A future fixture must admit exact source, compiler
MIR/body/impl/const identities; source mutation/wrong impl/false qualifier refuse.

## Rule and assumptions

At the exact trait call, require compiler type argument ParamT, method's exact
trait identity and call arity, actual body caller's compiler clause FreezeMarker<T>,
and one exact nonnegative safe local implementation with same ParamT and
FreezeMarker<T> clause. Infer the local selected body by exact source and compiler impl clauses;
**the exporter does not report a resolved selected impl DefId**. This inference
is an experimental, unaccepted trust assumption, not compiler selection evidence;
 retain normal FnCallOutcome, original operands/substitutions and native
contracts. No numeric32 substitution, no ownership permission or type model.
Threshold32 summary must be verified from actual constant-return body before
use. The selected small_sort still calls helper with the original same slices/F.
This is a theorem explicitly qualified by FreezeMarker, never an unrestricted
quicksort theorem or a runtime generic-signature change.

Trust: pinned Rust compiler/exporter correctly reports source clauses, DefIds,
operands; selection inference remains a separate open trust gate; source shapes exactly match current std.
The rule does not establish nonzero, scratch allocation or arbitrary recursive
quicksort safety. Marker qualification is necessary, not additional safety credit.
Existing ignored-clause routing must not run for these bound calls. Any relevant
unsupported source/ADT/specialization shape fails closed; general repair out ofscope.

## Required gates / outcome map

Fresh threshold-body VF0 and selected method VF0/full generated safety-template
posts; selected call32 positive and false31 intended assertion; wrong selected
impl or absence of actual FreezeMarker compiler clause admission refusal;
default-off result retained separately. Wrong bound/resource/callee posts must
reject with normal/unwind/free/leak/refinement/dead-code enabled. Native contracts
for helper/selected method may carry explicitly conditional length<=32 premise
only by exact permitted C1–C4 interface; guarded caller must prove it at call.
No premise assume or rewrite of abort/guard allowed. Model/tool/proof verdicts
separate. If identities/requirements cannot be admitted without new general
architecture, record exact blocker instead of broadening this rule.

## Fresh compiler evidence / narrowed implementation decision

379098e8 atcaa42f2abe2a1fef098bdef9803fe079e0dd5dde passes all paired exports
and refinement. Threshold body32 VF0; all trait probes refuse on duplicate
prototype atselected impl lib.rs23. Raw exporter traitImpls=[], both methods
have identical DefPath `<T as StableSmallSortTypeImpl>::small_sort_threshold`.
They have distinct compiler implBlockClauses (SizedT vs SizedT+FreezeMarkerT)
and exact source spans. The narrow rule therefore must identify both local
bodies by their source/clauses and give them distinct diagnostic AST names;
retain both bodies, full native safety templates and strengthened user posts.
No body or safety check is deleted. Generic trait call reroutes to selected
local AST name only in caller with exact FreezeMarkerT compiler clause. Cellu8
control gets default name only for the exact compiler concrete Cell<u8> type.
An unconstrained ParamT refuses; no general specialization architecture.
Whitelisted full verified fixture hashes plus pinned std source admissions
precede rewriting. Modified source refuses. Unknown clauses/types/extra body
inventory refuse. Model/parser/RSSpec/kernel/refiner/exporter unchanged.

## Review correction 2026-10-11

Raw FnDef is the trait identity and traitImpls is empty. There is no exported
compiler-selected impl target. Threshold probe PASS therefore cannot establish
actual caller applicability. Current patch is threshold-only; selected small_sort
and helper transfer are separate obligations. Exact Sized+Freeze clauses and
Cell<u8> decoder type are required; no additional clause/type admits.

## Current admission decision — 2026-10-11 19:22:51UTC

New phase SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11 supersedes the prior
source/clauses-only inference for any new caller proof. The first experiment
observes pinned compiler selection with both blanket and Freeze implementations
present in one diagnostic source. Real body.typing_env(tcx), original callee
DefId/args and original slice/comparator operands are compulsory. Compiler
DefIds are run-local; they must map through source spans/impl predicates to
exact source impl bodies, not a numeric ID carried across runs. Freeze caller
and concrete fallback are controls; original unconstrained generic caller is
recorded separately, including no resolved instance. No source/runtime MIR or
compiler selection changes are permitted by the observational exporter.

Native binding may open only after runner validates complete fresh evidence
against exact source/compiler/exporter/profile identities, complete caller
T/F/FnMut predicates, higher-ranked lifetimes and generic substitutions. The
selected-only proof fixture additionally requires checkable body/callsite/source
correspondence to the program containing both impls. Missing/stale/ambiguous/
mutated evidence or wrong impl/callsite fails admission; an environment flag
alone supplies no proof. Clause-ignoring generic dispatch must not handle these
bound edges. Final post-translation inventory/callgraph/cardinality and per-unit
reset are mandatory, with unchanged native resource preconditions and full
normal/unwind posts. The sole interface addition is pure ptr_len(v)<=32 in
selected small_sort and helper. Root caller receives no added bound premise.

A successful query is compiler/tool evidence only. Until qualified bound proof,
helper prefix/resources and full posts execute, all caller/prefix claims stay
open. General specialization, sizes/associated constants, ownership/aliasing/
MU inverse, callback, kernel/solver repairs remain outside this assignment.
