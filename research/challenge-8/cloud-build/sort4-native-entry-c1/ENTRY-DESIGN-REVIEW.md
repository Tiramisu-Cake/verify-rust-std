# Separate native entry entailment — pre-execution review

Independent GPT-6 Sol read-only review in assigned worktree. This experiment
replaces failed selected-path filters with a separate lemma/function: no trusted
source/MIR/AST CFG projection is introduced and no reachable original caller
path is removed. Runtime std and generic signatures remain untouched.

The native real function uses the original parameter shape and exact read-only
len/as_mut_ptr/division/cast operations. All native lengths/scratch lengths/type
states remain admitted. Ghost len>=8 branches ask a resource entailment; complete
VF0 automatic native return/leak is required. The helper req/ens carries ONLY
source4 initialized array, foreach CURRENT owners, current F cell/F.own and thread
(currentThread). Scratch remains native MU frame. No size or type_interp assumption
for this subset. Positives retain all checks; range negative is bounded to avoid
len+1 overflow for ZST usize::MAX, duplicate and false-post controls fail intended.

This is useful source-resource entailment, not proof that every len>=8 input
reaches actual first sort4. Actual applicability additionally conditions on original
len<2 continuation, scratch guard success and sort8 condition false; opaque generic
inline const is not equated to a duplicate condition. No assertion in failed VC
receives completed credit. Native post states CURRENT ownership, not snapshots
across legal callback effects. No callback occurs in this first lemma.

Stock MaybeUninit open/close does not restore arbitrary original wrapper: only
inner(new(x))=x is available. Full writable optional dst cannot coexist with retained
full original MU storage; fractional/borrow tokens do not repair that. Strong bridge
remains a distinct diagnostic; source-only theorem leaves MU bytes/owners unchanged.
Stock produce_type_interp is a real-function production rule, not heap derivation;
if used later it is tracked explicitly as stock trusted capability, with full
resource accounting. ZST legal selected caller domain 8..15 remains open for c1
but admitted in source-only lemma. No competing runtime-layout implementation.
