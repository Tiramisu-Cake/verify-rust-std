# READY — SAME14 gate-only delta review

NOT_AN_EXECUTABLE_CI_PACKAGE. Author fix for SAME14 gate-only delta review;
R14-03 independent closure remains pending. R14-01/R14-02 remain CLOSED in frozen review.

Proposed local control 0e97a487d8b7f8e8cbced5dbe2b6909c7150c695
Tree b980862474e3630c459ee147def4fa45f3ea42fd
Sole parent 0e8c836857344866564e1423ad5d8d28bbc4106b
Worktree /root/kani-ch8-s2-r14-03-gate-backlog-w13
Patch SHA256 1dfaf5a1fa2d748e81bea4093018eb65972d7cfc807e47c0d1f7ad39565f8cba
Entry G0/task commit 6db728b62b62d6d98d683f3d2cf6fb824dd6cc68
Frozen review e7837b0f70e235399e53f8da1b48a4a84b33f693
Frozen source bd62e54df1b4749154790aa3db3cc7978f547f75
Frozen control 0e8c836857344866564e1423ad5d8d28bbc4106b
Frozen request reference SHA256 9d165365933b6bc117311d7d52568f834bc2f083c2272800803a84883f286717
G0 output identity is the commit containing this directory, reported in READY.

The proposed control is a new child of frozen0e8 in an isolated worktree. Exactly
two paths differ: lexical_bindings.py and new targeted test_r1403_lexical.py.
Only call_paths changes in the checker; AST outside it is identical. Fixtures,
source/model/contracts, cfg, oracles, caps, tool, runner and workflows are unchanged.

call_paths now unwraps complete nested parentheses around its supported static
paths iteratively; token offsets still identify the actual path for lexical scope
checks. Direct/single/double/deeper paths resolve once, including qualified paths,
aliases, local functions and callable values. Tested extractor depths reach2048.
The guard rejects unsupported grouped/index/block/direct-call-result callee forms
with line diagnostics; it prevents tuple/deref/member/closure/computed-call shapes
from disappearing through the repaired parenthesis path. Parenthesized receiver
method calls remain explicitly inventoried as METHOD, without resolution credit.

The exact review mutation fn sort13_weak() { ((missing_static))(); is replayed
through both actual frozen and proposed lexical gates on temporary fixtures.
Only lexical_source_sha256 is removed; all other request fields are unchanged.
Its SHA256 matches frozen review. Frozen gate silently accepts77 calls; proposed
gate rejects unresolved missing_static. Direct/single/depth8 unbound forms reject.
The exact unmodified source is accepted and its entire baseline map equals the
frozen map:77 static calls,8 functions,11 contexts.

23/23 actual final-committed-object targeted tests pass. These include new
discriminators plus affected existing lexical, alias and selected cfg/PFC controls.
Full96 runner suite NOT_REPEATED. An initial targeted run had one diagnostic-expectation
mismatch in a synthetic scope test; an explicit semicolon now separates its block.
The checker bytes did not change. PRECURSOR-TESTS.txt/PRECURSOR-NOTES.json preserve
that failure without acceptance credit; the successful final run is separate.
TEST-PROVENANCE.json binds the actual transcript;
DISCRIMINATOR.json records full-gate rejection, and PATCH.patch replays to the exact tree.
PRESERVATION.json confirms frozen package474e, reviewe783 and GO6db bytes unchanged,
with clean exact frozen source/control worktrees checked before and after testing.

This is a finite token extractor/guard repair, not a general Rust expression parser
or complete name/type checker. Supported parentheses contain one already-supported
path. Other callable-expression coverage is limited to the explicitly guarded
forms; no broader syntax completeness is claimed. Methods, associated-type/trait
selection, executable expansion, typing, borrow checking and MIR remain outside
scope. Rust snippets are scanner input only. Native compile/verifier/full runner/CI
and causal repair NOT_RUN; actual R3 failing unit/body UNKNOWN; proof credit NONE.

The frozen bd62/0e8 one-run GO and its scoped R14-03 deferral are unchanged. That
exception applies only to its exact inputs and supplies no next-revision CI credit.
This child deliberately retains the old payload/request/workflow bytes and ancestry;
they are NOT rebound to this patch. Next integration must rebind payload/request and
ancestry, receive independent review and fresh GO. No automatic integration.
No compiler/CI/rerun/cancel/push/PR/issue/source publication/ledger/reservation/budget
operation or external message. Current settings retained; Fast OFF per owner unchanged;
no subagents. SAME14 gate-only delta review is the next local handoff.
