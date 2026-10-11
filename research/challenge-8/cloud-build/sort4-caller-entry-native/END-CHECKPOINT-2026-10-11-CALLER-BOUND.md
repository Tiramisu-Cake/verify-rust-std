# Caller bound session — raw review and checkpoint

Initial checkpoint `64922e1e5978b7204a6664e33a9f202aa6eea920`.
Policy revision `c7ca8c467aecf10a4b53039372ee97714f854ee3`; fetched fork main.
Owner select-sort4, existing assigned worktree/branch and lane unchanged.
Start16:25:01UTC; owner extended main to18:55:01UTC afterlongpause,
finish-only19:25:01UTC. Fresh budget3600; actual1449 seconds, unused2151
retired without carry. Four terminal/accounted/download-verified Builds.
Own advisory ready request withdrawn; no own active Build/reservation.
No Actions, merge, upstream publication, external messages or local compiler/proof.

## Separate verdicts

| Obligation | Verdict / exact limit |
| --- | --- |
| Public guard ghost lookup | FIXED by fully qualified std::mem::size_of::<T>() |
| Public guard positive nonzero | OPEN: T::IS_ZST lowers to opaque unevaluated_constant<bool>; no link to sizeof(T) |
| Public false-zero continuation | Intended assertion rejection, does not establish nonzero; both zero/nonzero are unprovable |
| Reachable ZST-arm assert false | Intended assertion rejection at lib.rs10 |
| Actual selected threshold body / const32 | VF0 plus native generated safety-template/normal/unwind checks |
| Two-impl selected/default probes | Selected32/default16 VF0 on experimental source/clauses binding; compiler-resolved target not yet exported |
| False31 / missing Freeze / changed threshold source | Intended semantic assertion / distinct admission refusals |
| Wrong selected impl control (+Copy) | INCONCLUSIVE: compiler export cannot specialize Copy/Clone; no intended admission credit |
| Actual caller transfers bound to selected method/helper | NOT_PROVED / NOT_RUN |
| Helper len+16 overflow | OPEN at lib.rs20; no caller premise supplied |
| Helper abort / pointer order / first-call resources | NOT_REACHED in actual helper proof |
| Pointer-only canonical T/MU + native consumer | VF0, full posts/refinement/cleanup; intended pointer/authority/MU-initialized negatives retained |
| Caller→C4 / full sort4 C5 copies / secondcall / sort8 | NOT_RUN / OPEN; historical guarded C1–C4 credit separate |

Model verdict: frozen inherited experimental/unaccepted. Tool verdict:
threshold-only candidate compiled at5dde9c2f; isolated body/name routing works,
but selection by exact source/clauses remains an unaccepted trust inference.
Proof verdict: local threshold body/probe and pointer candidates only; no actual
caller/helper/C4 upgrade. Positive public guard is not PASS.

## Evidence and causal results

0b7b3e53: qualification fixes lookup, first positive >0 lacks size fact;
negative-zero/ZST false intended; pointer consumer fullVF0; helper overflow.
379098e8: constant32 body VF0; trait probes stop duplicate prototype because
both compiler DefPaths are `<T as StableSmallSortTypeImpl>::small_sort_threshold`.
5a60dd5f: tool build fails OCaml record-kind ambiguity; no final-profile public
or threshold proof executed. Exact source annotation fixed in next candidate.
8fa3210b: source/clauses-bound names preserve both safety templates and both
impl bodies. Selected/default positives and false31 execute intended stages;
public positive fails semantic sizeof!=0 linkage before layout lemma/resource
assertions. Wrong-impl Copy control is frontend refusal, never proof negative.
Archive integrity independently checked: first748, third494, fourth981 listed
files. Standard download verifies each receipt/inventory/text index. Raw archives
are external evidence, not committed generated output. Full IDs/pins/accounting
are in SESSION-RESULT-MANIFEST.json and the ledger.

## Prepared but not executed

selected-branch-cases.rs retains real base guard and same-argument selected
method/helper transfer; explicit cuts exclude later quicksort/sort8/copy work.
selected-branch-binding.patch is a default-off text candidate only, with native
pre-only len<=32 interface and narrow existing abort semantic alias. No Cloud
compiler/source pair, selected target, resource proof, overflow or abort credit.
It requires runner-attested compiler binding; no runner sets that flag. It is
not registered in the runnable driver/recipe. An evidence-only exporter query
text candidate and exact pins/rationale are also prepared, uncompiled/notrun;
its observed source/selected target admission and runner integration are pending. Compilation and further trust
review remain required, including complete decoded clauses/generic lifetimes,
call-graph gates (final counter cardinality check is absent) and same-source
compiler target evidence. Current T,F clauses/lifetime substitutions have not
yet been observed/admitted; no broad clause matching is authorized.

Pinned exporter serializes raw trait FnDef, not selected impl; traitImpls=[]
because its HIR inventory admits concrete struct self types, excluding blanketT.
Stock pinned rustc Instance::try_resolve is a possible narrow evidence query in
real Freeze-qualified caller TypingEnv. Literal unconstrained quicksort TypingEnv
cannot be silently strengthened. No invented env, general specialization model,
size axiom, ownership bridge or MU inverse is authorized. Source API reading is
not observed compiler selection.

Next permitted action requires a new session/window/account: finish exact
compiler evidence for qualified selected route, admit observed target, integrate
reviewed native interface and run true/false-bound/resource/pointer/unwind gates.
Then prove helper len+16, abort and ordered pointer prefix. Preserve native posts
and direct-unwind/free/leak/dead-code/refinement. Nonzero has separate provenance;
len<=32 alone cannot permit nonzero C4. Public associated-const linkage is an
explicit blocker outside current size-model scope. Maintainer reviews candidate;
select-sort4 retains ownership of caller mission. No automatic next session.

Local validation: imported driver inspected (standard-library imports, guarded main);
small isolated replay of all17 saved8fa classifier cases identical, nocompiler/proof
tool called. Static Python AST/JSON parsing and source patch hashes checked.
