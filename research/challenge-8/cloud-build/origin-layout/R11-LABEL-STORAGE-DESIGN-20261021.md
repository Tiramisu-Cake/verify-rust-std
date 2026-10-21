# R11 first gate — observe label execution and native storage

Baseline R10 actual Build0d17cca8/toolbb557d43 compiles and parses the invariant,
but fails StorageDead276:44-45. Bounded MIR identifies unit117 Live, compiler
ghost command destination117, then Dead; native cycle97<-151. Existing evidence
shows invariant consumption/leakcheck/production but does not causally bind the
runtime env/local to those transitions. Unit/zero-size/name alone is no authority
to omit a storage event. Prior R10 layout-only Noop recognition is not a fix for
this independent label-invariant path.

Candidate1 adds opt-in read-only receipts at actual storage execution before/
after Live/Dead, exact AST+original MIR locations/local IDs and current env/live
binding; generic label invariant initial/backedge consume/leakcheck and separate
body production receive distinct execution receipts. Existing native decoded
Body/cycle discovery remains separate. Bound output to32 live receipt entries
with total/shown counts; format only existing pointer terms and heap counts.
Do not consume/produce heap/env, invoke assumptions, fabricate missing state or
change control flow. Every check and symexec_result is preserved. Ordinary locals
and missing/dead markers keep their existing failures. Scope is R11 child actual
case only with existing R8 opt-in plus new trace env; default-off/legacy unchanged.

Target: actual insert_tail concrete u64/array3 body. Distinguishing evidence:
StorageLive117 before boundary vs independent body env absent117; or a different
cleanup/path would refute that hypothesis. Then choose a source-preserving
placement/lowering fix with exact source/body/marker admission. No fix is
implemented based merely on the source hypothesis. Original algorithm/posts,
normal/unwind/abort checks, original tmp debt and approved narrow allocation
premise remain unchanged. Controls must exercise valid/invalid placement,
ordinary local, missing/dead/ambiguous binding before any semantic fix qualifies.

Existing compile gate -> actual target -> relevant retained controls in one
Build; timeout1200/envelope1260 fits fresh3600 and120minute main. Prior fullcold
577..644sec supports a full target attempt plus packaging margin. Compilation
and static/service review are not proof acceptance. Luna HIGH review required.

Review finding corrected before submission: statement translation precedes the
terminator-only State.current_block assignment, so diagnostic plan now receives
the decoded block ID/cleanup flag directly as immutable arguments from its caller.
No reliance on stale mutable translator state. The change affects receipts only;
Rocq/AST statement generation and old state updates are unchanged.
