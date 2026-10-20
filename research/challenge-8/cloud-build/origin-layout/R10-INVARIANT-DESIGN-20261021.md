# R10 moving-gap candidate design — pending observed inventory

Defect: fullbody normal backedge revisits the actual loop head without LoopSpec.
Source536–574 sets sift=tail-1, reads tail into tmp, creates original guard;
each pass copies sift→dst, advances dst=sift, may break, decrements sift,
and on comparator true continues. FIRST_SHIFT_PREP describes entry only.
No runtime/CFG/signature/domain change is permitted.

Candidate shape, not yet implemented/verified: existential index i in {0,1}
with sift=begin+i and guard.dst=sift+1, stable tail=begin+2 and original tmp
source/debt. Retain a current initialized prefix before sift, initialized source
cell at sift, permissive physical gap cell at dst (initially uninitialized;
may be physically initialized after a copy), and current initialized suffix
strictly after dst. Retain exact original tmp readonly coefficient/token,
current F/thread/type resources and source provenance/limits. No per-call
lifetime/loan in the invariant: late scope must close before Continue.
Keep any old entry own-list separate; it does not assert current value equality.
Do not assert a complete initialized array over the live gap.

Init: checked split of actual current prefix/read tail; fold zero suffix with
proven geometry. Backedge: returned late comparison cell becomes next sift;
old source is new physical gap; copied previous destination joins suffix.
Use checked lemma bodies for representational changes, never assumed bridges.
Break at sift==begin and false-comparator exits need their actual distinct
resource layouts and guard Drop returns, not a forced next-iteration state.

Evidence gate: first actual R10 diagnostic backedge inventory must confirm all
physical chunks/coefficients, CURRENT values, local/guard binding, tmp debt,
F/thread and lack of live per-call tokens before committing a concrete invariant.
Diagnostic-only Build1 source5f7139fa/tool07116a39 is in flight. All proof gates,
full normal/unwind/B2/qualification remain OPEN/acceptedfalse/credit0.

## Checked annotation binding, static reader finding

`inv` is a regular ghost InvariantStmt (rust_parser609), not compiler
LoopSpecBlock (`req/ens` is that separate path). Place a distinct `//@ inv ...;`
line first inside `loop {`, before original let_lft. Translator3264–3287 matches
compiler ghost command source line; cycle-head first InvariantStmt produces
WhileStmt/LoopInv at4677–4695. Late binding relocation6553–6607 moves its declaration
to explicit late scope begin and leaves original placeholder Noop; invariant
must remain the first translated head stmt. Distinct source lines required by
candidate uniqueness6654–6689. No source-only coordinates prove the runtime
MIR/head identity. `sift` assigned local is freshened by WhileStmt; gap_guard
address-taken local needs the actual mutated field chunk in invariant.
Kernel2161–2177 consumes invariant and frames residual heap; body only gets
produced invariant heap. Residual frame returns at exits, cannot be used inside
copy/callback/drop. Include resources actually needed by those body paths.
Static helper /root/r10_review, Luna HIGH; no additional proof credit.

Next candidate diagnostic rationale: kernel missing-invariant receipt names its
source location but not MIR ids. Add a read-only translator cycle-discovery
receipt under the same admitted first+late callback/R9 trace gates, using the
same decoded Body identity/phase/fingerprint and current reconstructed CFG
head/from ids plus source location. Label it reconstructed CFG, not execution;
source/stage hashes and compiler ghost-command matching remain separate gates.
This preserves find_blocks decisions and all original successors/parents.

## Build1 inventory and concrete candidate2

Build403f96a0/source5f7139fa/tool07116a39/profile016ad1bf; native kernel
inventory at verified271:37/37heap,41/41env. Reader exact bounded1792–1871,
file3cd3d799, archive0fe0bf89,index4e3f4061, parser-input binding NOT_ESTABLISHED.
Backedge: current sift=(tail-1)-1; guard.dst=tail-1; tail=begin+2. Full current
array(sift,1,cons(dummy54,nil)); full points_to(tail,value2) and
points_to(tail-1,value2); full empty arrays at begin+2 and begin+3.
Original token(r4_tmp_ref,tmp_addr,1/4), ref_initialized(actual originalref),
reference quarter points_to(value1), ref+1 emptyquarter; origin tmp quarter
merged from two eighths has current dummy51. Field chunks src/dst/len/padding
full; current F points_to(self10)+F.own/self10, thread/typeinterpF/u64 and
func_lft token full. Old own foreach is separate. Only dummy late shares/frac
borrows/dead-token remain; no non-dummy live late token/full borrow/end token.
No equality of tmp current/reference/current array vs entry values is assumed.

Candidate2 uses the existing concrete pair of positions, avoiding unnecessary
arbitrary-n arithmetic. Common heap: current first singleton, initialized
middle, empty tails, original tmp/reference quarters+token+initialized, guard
fields/padding, current F/thread/type/lifetime and own-list. Conditional:
sift=begin+1/dst=tail permits optional physical tail contents; sift=begin/
dst=begin+1 requires initialized tail. The live logical gap is distinguished
by guard.dst; no whole-array assertion over it. At second iteration open the
first singleton; generic per-iteration geometry is checked from actual current
source/destination resources. FIRST_SHIFT_PREP remains only in preheader.
Explicitly open/reclose existing empty arrays before invariant to normalize
nil values without creating ownership. No allocation premise extension.

Backedge after late return preserves common heap directly. At sift==begin break,
normalize middle to singleton before original implicit Drop. Its return supplies
first singleton; R9 checked post-Drop rejoin then joins current three cells.
False comparator/late cleanup keep R9's original layout/recovery. Formal entry,
preservation and all exits remain unverified until exact candidate Cloud run.
Controls: intact original matrix, R10 versioned wrongorigin token mutant and
source-exact duplicate-marker repair; no arbitrary-n/generic credit.

Next read-only receipt gate: instrument ordinary LoopInv entry consume,
production, and backedge consume/leak-check completion under existing R9 trace+
R8 option. Emit bounded-row existing heap snapshots through the same formatter,
without touching h/env, rules, branch scheduling or checks. `entry_consumed`
is specifically assertion consumption, not full body proof. `backedge_checked`
only follows successful invariant consumption, termination and leak checks;
normal/unwind theorem remains separate. Native cycle receipt/source-stage hashes
bind the loop location; a log marker alone never grants independent proof credit.

## Build2 parse frontier and candidate3 correction

Buildd4487296/sourceaada9d02/tool48ace768 compiled all seven milestones; target
attempt stopped in annotation parsing at verified290:36–37/log2: C ternary `?`
is not part of the pinned Rust annotation grammar. Exact source284–295 and
complete log1–4 read via v0.11. Entry/preservation/exits NOT_ESTABLISHED, recovery
controls prerequisite NOT_RUN; old proof claims not transferred.

Use supported if-expression (`rust_parser.ml322–330`, as pinned array predicates)
with the identical two branch assertions. Also batch related head ordering fix:
keep invariant first, then original let_lft placeholder (translated Noop), then
dynamic head preparation. Ordinary While rejects an immediate PureStmt as first
body statement (`verifast.ml2155`); existing translator6617 preserves original
late declaration location as a Noop while relocating actual type binding.
The Noop is an existing compiler/source placeholder, not a new runtime statement
or skipped check. No invariant resources/meaning/CFG/posts changed.
