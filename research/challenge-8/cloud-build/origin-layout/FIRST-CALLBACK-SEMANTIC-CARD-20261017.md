# First actual comparator: semantic card, before implementation

Status: DESIGN / NOT_RUN / NOT_PROVED. Owner merge; separate phase
MERGE-FIRST-CALLBACK-CLOUD-2026-10-17. Start 2026-10-17T00:32:42Z;
main deadline 02:32:42Z; finishing-only deadline 03:02:42Z. Fresh ceiling
960 Cloud seconds, at most one Build, timeout <=900 plus 60 queue reserve;
no carryover or automatic retry. Existing v3 coordinator only.

Policy read: WORK-POLICY at 6e1a8e59c56669abe5e6ec2013478e45ed2cc267,
addressed adoption 1e65f562994220a909ccf97903c36cb054576b76; local Evidence
Brief policy revision 2026-10-17 takes precedence. Preserve local instruction
changes and all three previous sessions. Baseline project checkpoint proof/infra
9e15014b5c62f94eb797e044d1f4ca9bd8cb74f1, Build
30bce9a0-29e8-4535-9060-ee6d9df2dccc, tool
a158398e336edce9817f62a55733a3470a986d7b, experimental v8 profile
0e67b038f940a9892dcb840747fbcc340532a31649979601af545acc41a0c68b.
Current project parent 7c02d329 includes later infrastructure history, not a new
proof result. New profile must be independently reviewed and exactly pinned
before any Build. Neither old nor new profile is accepted for integration.

## Exact source CFG and domain

Unchanged SmallSort blob 40939f922bcb6fdc7ee0d30427fa861827043827,
SHA256 85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1;
insert_tail body SHA256 9bc00f3913373e5879769b9970d66b1a56ada05a10205d51cafdf6533ecc2f29.
Mechanically specialize only T=u64; retain generic F: FnMut(&u64,&u64)->bool,
all legal comparator effects and panic. Actual wrapper initializes [10,20,5].
No runtime std or generic signatures are changed in the repository.

The CFG is: entry -> tail.sub(1) -> first &*tail and &*sift -> first actual
FnMut::call_mut at source541. Normal false -> original early Return.
Normal true -> original tail.read -> ManuallyDrop -> guard construction ->
loop copy -> update gap -> sift==begin? -> decrement -> late FnMut source566.
First panic -> original Continue (no live guard) -> caller unwind exit.
Late panic -> original Cleanup -> actual guard Drop -> Resume. Normal loop exit
-> separate normal guard Drop -> Return. Those paths must stay distinct.
Numeric bb IDs are deliberately not inferred from historical logs: fresh
compiler MIR spans, call identities and successors must bind this graph, and
an absent binding is INCONCLUSIVE. Full-body diagnostic retains every runtime
statement and identical final normal/unwind posts.

## Resource provenance and obligations

Entry owns array(begin,3,xs), length=3, foreach(xs,own<u64>(t)), tail=begin+2,
thread_token(t), type_interp<u64/F>, and current *is_less + F.own. Wrapper cells
come from its actual local array; comparator from its canonical input borrow.
No supplied receiver/FBC/origin/end-token/gap permission or assumed bridge.
The first cell remains framed. Existing proof splits singleton sift/tail cells
and their corresponding sole owners, closes full-borrow contents, borrows/shares
under fresh cmp_k, derives precreate and genuine ref_initialized resources,
opens two tracked fractions with their lifetime tokens, and packages the tuple.
No extra owners are introduced. The compiler-derived FnMut and Output clauses,
binder identities/order, type substitutions and lifetimes justify the callback;
a registration flag or reached statement does not establish this contract.

On BOTH normal outcomes and panic, consume exactly the returned temporary
reference fractions/tokens, close their fractional borrows, leave the local
lifetime binding, end cmp_k, borrow_end both original full borrows, open their
contents and rejoin singleton arrays/foreach owners with the framed first cell.
Restore CURRENT *is_less/F.own, thread/type/lifetime resources and caller frame.
Final posts existentially describe CURRENT arrays and F, not entry comparator
state. False must reach original Return; true must reach tail.read/guard with
all three initialized cells. Panic must run recovery before original Continue.
No loan or lifetime may escape its binder; no leak/assume and no purity/no-panic.

## Proposed narrow trusted delta and admission

Exporter/schema already preserve trait/projection boundRegions. Translator
currently discards Trait binder lists and recognizes only Param referents;
u64 cannot match either bound collection or call substitution. Preserve Trait
binders and admit exactly u64 in addition to the pre-existing generic case.
Require matching compiler trait/projection binder identities/order, exact bool
Output, two shared refs, same F/referent, unique clause and matching call MIR /
ghost substitutions with explicit same instantiated lifetime. Equality stays
call-local; no global HRTB instantiation and no new prelude/kernel rule.

First-call ghost recovery must be separately opt-in and bound to source insert_tail,
its unique first actual FnMut span, original normal successor and Continue.
Reject Cleanup, a second marker, wrong type/call, ignored unwind and late callback.
Use explicit close/scope-end/recover annotations and existing strict lexical
lifetime machinery. Attach the panic recovery to the first call alone, at a
local continuation outside its ended lifetime binding, preserving the actual
Continue return. Never use the old function-wide shared synthetic unwind
epilogue, or redirect late Cleanup to first recovery. If a local continuation
cannot preserve lexical environments without changing the kernel, stop with that
blocker; do not weaken scope checks. All commands remain ordinary checked ghost
proof commands and consume existing resources.

Official refiner: narrowly compare first source-bound Call unwind actions,
requiring original Continue == verified Continue. Mutation to Cleanup/Terminate/
Unreachable must reject at that check. Late cleanup remains explicitly
unqualified. Refiner exit0 without an affirmative first-edge check is insufficient.
No change to kernel, memory/alias/layout model or prelude.

## Controls and decision gate

Source-linked prefix check (explicit cut after first callback recovery, before
tail.read) must cover false, true and panic with full CURRENT resources. It is
partial and cannot substitute for full-body insert_tail. Full-body unchanged-post
diagnostic separately reports the next actually reached frontier.

Proof negatives: lose one ref_initialized fraction or corresponding token;
lose CURRENT F; lose one cell owner. Count only the intended resource predicate
at recovery/post, after verified HRTB admission. Earlier error is INCONCLUSIVE.
HRTB controls: wrong Output, missing projection, wrong F/referent, mismatched
instantiated lifetimes, wrong binder count/order/identity, binder/ref mismatch,
ambiguous projection and cross-body leakage. Refiner mutant: change first Call
Continue to another action, require the new official first-edge rejection.
New mechanism on late Cleanup must refuse at admission. Keep B1 positive/six
proof negatives/ten admission/four receiver-end-retirement controls, helper4,
normal/unwind, default-off and existing HRTB regressions. None are claimed run.

Independent patch review and exact source/tool/compiler/spec/profile/patch pins
are mandatory before Build. If candidate or controls are incomplete, no speculative
Build: checkpoint prepared work and precise blocker, with zero new proof credit.
After terminal Build only smallsort-brief UUID; no raw archive/log access, including
local copies. Missing/insufficient Brief limits claims; separate admin audit only
with explicit authorization. B2 remains open through full shift/gap/latepanic/
realcleanup/Drop/caller posts; generic T, ZST and profile I integration excluded.

## Implementation decisions recorded during preparation

The isolated prefix is named insert_tail_first_callback_prefix. It retains the
actual source segment through the first comparator/false return, cuts immediately
before the comment introducing tail.read, and closes the unsafe/function braces;
its true path returns at that explicit cut. The source-owned [10,20,5] wrapper
calls this renamed prefix only in that isolated case. This is a partial resource
theorem, not the full insert_tail body. Full-body diagnostic remains separate.

Three adjacent one-line annotations after the first if head configure the new
first_callback_close / first_callback_scope_end / first_callback_recover protocol.
The six checked fraction/token-close commands execute on both callback outcomes
inside the strict lifetime binding. A local normal-edge block leaves that binding,
runs the sixteen existing lifetime/borrow/owner/array recovery commands, then jumps
to the original normal successor. The first panic exits the same binding to a
local continuation immediately after it, runs those recovery commands and returns
the original unwinding outcome. No whole-function unwind epilogue or late callback
rewrite is installed. These are only admission facts until proofs succeed.

Exporter encode_region already maps ReVar/ReErased to the sentinel '<erased>.
Translator encodes that as InferredTypeExpr. The method's one late-bound argument
is synthesized as 'erased from late_bound_generic_param_count. New HRTB admission
checks those source forms rather than treating arbitrary source lifetimes as
wildcards; explicit source ref regions must match their ghost instantiation.
The compiler's universal clause, with retained ordered trait/projection binders,
is instantiated to the explicit ghost lifetime. Erased source regions themselves
are not identity evidence, and cannot replace actual reference-own/call proof.

Resource-loss fixtures are intentional negatives only: malformed fraction and
a stronger token assertion at the close step; a source ghost leak of CURRENT F
on false-return AFTER the markers; and opening the restored foreach, discarding
one cell owner and attempting to close it again. The last two are ordinary
negative-source instrumentation, not commands accepted by the new marker gate.
Positive source rejects leak/assume and retains every full normal/unwind post.
A negative that fails admission or before its intended recovery/post is
INCONCLUSIVE. This clarifies the no-leak invariant for all positive proofs.
