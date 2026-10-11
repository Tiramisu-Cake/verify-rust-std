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
We propose an opt-in narrowly matched rule for StableSmallSortTypeImpl's two
methods in one pinned standalone source fixture. Ordinary translation stays
unchanged when disabled. A future fixture must admit exact source, compiler
MIR/body/impl/const identities; source mutation/wrong impl/false qualifier refuse.

## Rule and assumptions

At the exact trait call, require compiler type argument ParamT, method's exact
trait identity and call arity, actual body caller's compiler clause FreezeMarker<T>,
and one exact nonnegative safe local implementation with same ParamT and
FreezeMarker<T> clause. Bind to that implementation's compiler-exported method
DefId; retain normal FnCallOutcome, original operands/substitutions and native
contracts. No numeric32 substitution, no ownership permission or type model.
Threshold32 summary must be verified from actual constant-return body before
use. The selected small_sort still calls helper with the original same slices/F.
This is a theorem explicitly qualified by FreezeMarker, never an unrestricted
quicksort theorem or a runtime generic-signature change.

Trust: pinned Rust compiler/exporter correctly reports source clauses, DefIds,
operands and specialization selection; source shapes exactly match current std.
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
