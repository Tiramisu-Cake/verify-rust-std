# Stock Rust pointer/index component — authorized 2026-10-07

Entry documentation HEAD `7d27ce106d27208bcd1156fe5675f70f8f9bf1aa`.
G2/A/B accepted and unchanged. Same merge budget: 330/1800 used, 1470 remain.
This is a partial projection of exact pointer operations, not verification of
the complete `bidirectional_merge`, its callers, references or copies.

## Applicability audit before any executable check

Vendored SmallSort matches byte-for-byte Rust commit
`b6f0945e4681bc4d2faa7c22c5f61dc36abf7dd2`, SHA256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
Other caller files are reference evidence from that exact upstream revision;
they are not present in this repository's reduced core subtree. Their hashes
and paths are in SOURCE-MAP. This is a source audit, not caller verification.

Stable `sort/sort_by/sort_by_key` -> alloc `stable_sort` -> core
`stable::sort` -> `driftsort_main` -> drift `create_run` -> stable quicksort
-> `StableSmallSortTypeImpl::small_sort` -> general scratch. The Freeze
specialization selects general scratch; the other specialization uses insertion.
General scratch invokes `sort8_stable` twice when len>=16 and size<=16, then
merges the full scratch input. Sort8 itself merges exactly eight elements.
Unstable `sort_unstable/_by/_by_key` -> `unstable::sort` -> ipnsort/quicksort
-> `UnstableSmallSortTypeImpl` -> Freeze dispatch -> general scratch or network
(otherwise insertion). Network merges only on its 18..32-element path.

Both entry `sort` bodies return for `T::IS_ZST` before their length/dispatch
paths. Thus these public routes do not execute merge for ZST. Their len<=20
fast paths use insertion; larger sorts reach SmallSort on smaller subproblems.
Cached-key sorting instead builds `(K,index)` tuples and sorts those with
`sort_unstable`, then swaps the original values. The integer index makes this
sorted type nonzero even when original T or key is ZST; it supplies no path to
`bidirectional_merge<T=ZST>`.

The Challenge explicitly quantifies generic SmallSort entry contracts over all
valid slices. Direct trait/helper invocation has no enclosing entry ZST return.
Stable Freeze and unstable Freeze/non-Copy ZST select general scratch; unstable
Freeze+Copy ZST selects network (size thresholds are zero). Direct general
len>=2 has a merge route, including fixed-8 sorts.
Non-Freeze uses insertion. These direct cases and their ZST ownership/panic
behavior remain OPEN. No `size_of<T>()>0` is added to the Challenge contract.
General's independent `len+16` scratch check also needs a usize bound for a
standalone enormous ZST slice; public threshold dispatch supplies len<=32.

Direct ZST network requires an additional distinction: len2..17 returns through
no_merge, while len18..32 never reaches merge on normal-returning paths. Its
loop breaks only when region.as_ptr()!=v_base (line354). The right region is
constructed from v_base.add(len/2), whose ZST address equals v_base, so this
comparison never breaks the loop. It repeatedly processes the right partition.
Network's own len>32 abort establishes the upper bound independently of caller
dispatch. This semantic nontermination finding is an uncovered generic behavior,
not a verified ZST implementation or a stock layout-model result.

## Component premises versus actual caller facts

Let s=size_of<T>()>0; M=usize::MAX+1; n=2m+e, m>=1, e in{0,1}.
Require n representable as usize, n*s<=isize::MAX as mathematical integers.
Let source allocation have live provenance P, base address A, metadata none,
and an aligned valid element range [A,A+n*s). Destination has its own live
provenance Q, aligned base B and writable range [B,B+n*s). Each base/end lies
within the corresponding allocation's provenance limits; addresses A+n*s and
B+n*s are <=usize::MAX and do not wrap. Alignment is an actual memory premise,
not a result of index arithmetic. For ordinary add/sub require the whole crossed
byte range in the one allocation, and count*s<=isize::MAX. A one-past pointer
is admissible for arithmetic/comparison, never a readable element.

The operation fixtures use explicit positive s, byte bound and provenance-limit
facts; they preserve pointer provenance/metadata through stock pointer arithmetic.
They do not own an allocation or typed cell. `pointer_within_limits` is the
stock model's geometry predicate, not a Rust read/write permission or a proof
of liveness. Numeric equalities alone establish neither memory permission nor
that an arbitrary pointer was derived from the chosen allocation.

Source audit establishes n>=2 on each merge path, exact n=8 for sort8, and
18<=n<=32 for network. Trait dispatch bounds general subproblems by32; normally
passing scratch guard supplies len+16 elements. Safe slice arguments motivate
source validity and nonzero-size slice byte bounds. Scratch allocation and source
comments motivate separation/initialization/restoration. None of those resource
claims has been composed or proved for the actual caller in this phase.
Nonzero T follows only along the audited public entry routes. It remains an
explicit component premise for standalone generic use.

## G2 connection and wrapping semantics

At paired state(k,a,d): L=a; R=m+k-a; LR=m-1-k+d; RR=n-1-d;
D=k; DR=n-1-k, 0<=a,d<=k<=m. Represent an in-range source cursor i by
the pointer derived from src with provenance P and address A+i*s, similarly
destination j by Q and B+j*s. G2 bounds give readable candidates before each
comparison/copy, add targets <=n and destination reverse decrement >=0.
Exact forward bits are left.add(is_l as usize), right.add(!is_l as usize);
reverse right.wrapping_sub(is_l as usize), left.wrapping_sub(!is_l as usize).
No pointer update precedes the copy. The Rust ghost g2_steps fixture checks
bodies of the local step/terminal formulas anew; it does not import C lemmas
as axioms or implement the unbounded trace/composition theorem in Rust.

Wrapping is distinct: W_P(i) carries P and byte address (A+i*s) mod M.
Intermediate LR=-1 after the final reverse-left selection is W_P(-1), which
may be outside the allocation or numerically wrap. No A>=s requirement is
introduced: wrapping permits either outcome. It is not readable. The next exact
wrapping_add(1) produces the source-derived W_P(0); more generally ends are
P(d), P(n-d), both in[0,n]. Provenance is retained while leaving/re-entering;
equality of modular addresses with a foreign allocation does not transfer P.
The pinned Rust pointer docs describe this behavior, but the stock Rust proof
bridge must verify the exact wrapping calls before composition can use it.

For in-range nonwrapping endpoints, positive s makes i -> A+i*s strictly
increasing and injective. Thus left<left_end iff a<d, and exact final pointer
guard equals scalar `(L!=d || R!=n-d)` after the optional odd advance. The
order/guard fixtures assume those pointer/index associations and check the exact
operators and Rust ghost multiplication lemmas; they do not derive terminal
associations from wrapping or from raw integer addresses.

For s=0, i*s=0 for every logical i: addresses are noninjective, pointer `<`
cannot realize a<d, and pointer equality cannot imply equal indices. This is
a semantic Rust audit result. No concrete stock-VF ZST layout fixture is used:
its known incompatible positive struct-size model would not establish Rust
ZST behavior. Original G2 permits either odd branch; A needs scalar guard,
B additionally needs scalar odd choice. Those premises cannot be discharged
from ZST pointer guards by this nonzero component.

## Stock support audit and experiment gates

Stock source `809de4596839b739dd999f9e462242c835e3af46` translator
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml:2395-2439`
maps exact const/mut add/sub; BinOp Lt/Ne/Eq have ordinary operator mappings.
No pointer wrapping method mapping or stock specification was found. Minimal
independent symbolic fixtures will distinguish unsupported methods from proofs.
No intrinsic substitution, new spec, tool patch, historical experimental
profile or unchecked imported lemma is authorized.

Every isolated case retains ghost-strip source identity, pinned SmallSort full
admission, readonly compiler export/decode, full verifier exit/body/return/leak/
dead-code gates and independent refinement. Refinement relates each fixture to
its ghost-free projection only, never to the whole merge. Normally executing
pointer-only fixtures target their stated result/provenance posts and no unwind.
True-post wrapping probes test support only, not correspondence.

Controls: wrong_cursor uses exact add(1) but asserts step2; intended failure
is the TARGET assertion, not its add precondition. address_index asserts i==j
from unrelated equal addresses without source/index association; intended
TARGET assertion failure. wrapped_read tries reading intermediate -1; intended
missing points_to at that read, but an earlier wrapping unsupported failure
must remain INCONCLUSIVE. Exact predicate/location metadata and fail-closed
mutants are required before a negative is accepted; metadata calibration needs
a new run. Timeout, setup, unrecognized diagnostics and unrelated failures
remain INCONCLUSIVE.

P1: existing registered selection `proof=merge_geometry, sort4_component=range`
routes only on challenge-8/merge to pointer-run.sh; default index retains G2.
One ubuntu24 hosted job,6-minute cap, per-stage timeouts, remaining1470s.
Supported positives may complete independently. A wrapping semantic blocker
stops wrapping composition with a minimal reproducer and no unchanged retries.
Annotation/checked-lemma repairs on supported operations remain within scope.
FnMut, copies, ownership, comparator model and unwind are unchanged and OPEN.

## P2 established support boundary / P3 scope

P2/run37686101335 establishes `No such function` for exact stock pointer
wrapping_sub at projected15:17–54 and wrapping_add14:20–44, with export/decode/
refinement0/source unchanged. Wrapping bridge stops; all four wrapping/re-entry/
read cases excluded from later runs. Intermediate-1 read remains INCONCLUSIVE
(earlier ghost variable shadow in its own P2 projection), not intended rejection.
Draft ghost rename/prototype correction in those excluded cases is NOT RUN.
Supported11-case P3 repairs only own classifier footer/body braces and research
unsafe prototype qualifiers, then checks order/guard and both exact negative
oracles. Actual std runtime/signatures/contracts and all proof gates unchanged.
