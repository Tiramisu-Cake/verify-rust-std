# S2 r4-r1 — one-run GO request with scoped gate exception

Root agrees to ONE new r4-r1 attempt under coordinator/owner-delegated GO.
Review e7837b0f70e235399e53f8da1b48a4a84b33f693 remains **CHANGES_REQUIRED**:
R14-01 and R14-02 CLOSED; R14-03 remains OPEN, **DEFERRED / NONBLOCKING FOR THIS RUN**.
This is an explicit coordinator/root scope exception, not reviewer APPROVE.

Package474e0b4209554bdd69c4303410192d2d472af4a2. Exact source
bd62e54df1b4749154790aa3db3cc7978f547f75, tree dc2e7a7f258719a05c65bbb9b1e2c7f1e8271ac8,
parent97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a. Control
0e8c836857344866564e1423ad5d8d28bbc4106b, tree9f7c903f2039e6a52b19f37c5f32fbd9cc86566f.
Publish exact source; trigger must be a SAME-TREE SIBLING of control, sole parent
9e14e033f9ee31522b571c127609dcdff76d230b, not a child of0e8. Stock0aac16ef62da9e9d5645782d458593e5d78143ba,
checkout control/source/tool7/5/2. Request SHA256
9d165365933b6bc117311d7d52568f834bc2f083c2272800803a84883f286717; workflow
93521eefcbd83c50218d8484b2f8bbc044ff9acd2dd2b003749fe0e316c0ea6c.
Actual final trigger/ref/run/attempt are not created by root and must be recorded.

R14-03 is a real generic lexical-scanner completeness defect: nested-parenthesized
calls can be omitted. Reviewer confirms no injected missing_static call in the
unchanged source; root independently checked EVERY token adjacency `)(` in the
entire exact S2 batch module, including all eight new/changed functions/branches,
without using defective call_paths. There are no parenthesized callees at all;
known bad/qualified/simple forms exercise this separate check. Exact source/hash/
correspondence guards remain. CALL-SYNTAX-CHECK.json records SHA, method and limits.
The exception covers this immutable input and ONE run only; changes need fresh
review/decision. Gate completeness is not accepted; R14-03 stays in next-revision
backlog. Frozen review, source, control and all earlier packets remain unchanged.

One group,11 roots/20covers/6 exact negative oracles, all existing controls/caps:
backend600s, compile900s, rootsum6600s, group7500s, internal8100s, step7560s,
setup1800s, job180min, serial1, RSS12GiB+2GiB headroom. No automatic reruns.
Independent96 final-object tests and six static patch replays passed; root verified
package60files/59hashes and review18files/17hashes plus exact clean Git identities.
Native compile/causal repair NOT_RUN; actual R3 failing unit/body UNKNOWN.
Sort13/general32 DIAGNOSTIC_ASSUMED; sort8 PFC registration is not a theorem.
Two weak controls cover faithful source-bound copies/seams, not original caller
identities. Actual merge32 remains exactu8/32/sorted-halves/allocation domain.
No proof admission, fit600, causal-speedup or complete Rust name/type/MIR claim.
Preserve TIMEOUT censoring, incomplete/UNKNOWN metrics and diagnostic receipts.

Ledger reference a4e8bdd22f:29/29 +9/14=38/43; next item2 is10/14 if counted.
Only confirmed compile failure before first root qualifies0; successful runs are
not free. Preserve real CI costs; every retry separate review+GO. Coordinator alone
performs dispatch/accounting. Root did not compile, publish, push, run CI, reserve,
charge, modify ledger or open PR/issue. This GO packet changes no executed inputs.
