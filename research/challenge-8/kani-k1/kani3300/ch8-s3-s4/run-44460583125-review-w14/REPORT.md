# W14 terminal intake review — APPROVE with limits

Exact intake `97eaff96cd28267e36af69fe98077dd08737eea6`, task
`7c2c6af9f538d43e5cce51d548bdd73633358241`. Approval covers the accuracy,
completeness and restrained interpretation of the sealed terminal intake only.
No localized correction finding or remaining intake blocker was identified.
The independently checked outcome is **2 native SUCCESS, 3 exact intended
FAILURE, 2 whole-child600 WALL timeouts, strict producer0, no admission**.

The 30-file intake has 29 manifest-covered byte/hash matches at the pinned
commit. The compact payload SHA256 is
`32fdc7741046b1dfd4d944ddf4881bffef993e87d949a91deddaf46f97b3d865`;
all105 structured members match their individual byte counts/hashes. Exact
request/workflow, source/tool/control/trigger identities, 100 control payload
hashes and39 source hashes were checked. Transport authentication is the sealed
W11 acquisition receipt and connected artifact metadata; this review reused
that receipt and did not independently reacquire the transport. Transport digest,
compressed payload hash and decompressed hash remain distinct.

| Root | Actual mode/target | Native result | Properties | U | SUCCESS guards |
| --- | --- | --- | ---: | ---: | ---: |
| checker_order_corrupt | Original/null | FAILURE, exact S2_NEG_CHECKER_ORDER | 24 | 8 | 0 |
| checker_count_corrupt | Original/null | FAILURE, exact S2_NEG_CHECKER_COUNT | 26 | 1 | 0 |
| sort13_weak | Original/null | FAILURE, exact S2_NEG_SORT13_WEAK | 25 | 8 | 0 |
| i_p01_b01_fullu8 | PFC/insert_tail | SUCCESS | 353 | 7 | 4 |
| sort9_v34_b01_len09_real | Original/null | SUCCESS | 174 | 4 | 3 |
| fallback_cell_b01_n00_16 | Original/null | UNKNOWN incomplete | UNKNOWN | UNKNOWN | UNKNOWN |
| network_u8_b01_n00_08 | Original/null | UNKNOWN incomplete | UNKNOWN | UNKNOWN | UNKNOWN |

Each root has one observed start, a unique invocation namespace and a durable
completion seal in the required order. Portable selected_roots is genuine int7.
Completion includes failed and censored observations. Fresh materialized/upload
replay agrees. Source/tool/request/cfg/argv/export/native registration and
E0/pre/worker BEFORE/worker AFTER/controller-post binary snapshots agree for
all7, including both partial rows. Source_before/source_after/current
source_under_test and compile provenance agree. This establishes the exported
identity observations only: compiler instance/compilation ID, effective clauses,
AST/MIR/property causal edges and physical inode identity remain UNKNOWN.

The three negatives have one located intended failure each. Order is the fixed
[1,2]→[2,1] fixture; count is fixed32 ones with index31 changed to2. sort13_weak
is the fixed descending[12..0] caller-copy with ordinary uncontracted
s2_swap_seam→weak_swap. It establishes neither arbitrary13 coverage nor the
actual positive13 body. Every recorded native ID/status/location remains
available in the pinned NATIVE-PROPERTIES.json; ROWS.json preserves the exact
role records and class/status counts reviewed here.

Insertion uses all34 arbitrary u8 values, base1, relative tail1, span2 and the
concrete KeyLess<u8> provider: one I-D1 geometry out of16, one old-grid geometry
out of256. Its actual native PFC registration names insert_tail, and the DFCC
single-top-level/no-recursion checks and located checked ensures are SUCCESS.
sort9 is Original with null target and all34 arbitrary u8/base1/len9. Inspection
of the pinned body confirms25 real swap_if_less calls and no verified stub.
Both retain four SUCCESS source roles: active model, sorted/full-value count,
every outside-value frame, and arbitrary outside canary. Each has all five exact
SAT covers. The owned snapshot and equal-length per-input-value multiplicity
checks support the source full-value multiset argument; length equality leaves
no capacity for a novel output value after all input multiplicities match.
This remains SOURCE_REPORTED normal-return evidence. It does not close a
generic provider, ownership, panic, dispatch, initialization-mask or MIR theorem.

U-REVIEW.json enumerates all28 exact root/invocation/property tuples. The17 U in
the negatives are source-local active_post bounds/overflow sites. Entry rejects
invalid snapshots, length mismatch or L>32. Order increments only with i<L;
outer/inner count indexes stay below L, counters are at most the preceding
iteration count, and increments remain <=32. Early false returns explain
unobserved later sites without converting U to SUCCESS. The11 positive U are:
two unsigned abs_diff branches per root (subtrahend <= minuend); align-1 after
the power-of-two guard (normal continuation implies align>=1); literal shift1
below usize width64; insertion Span::ordered i-1/i+1 under 1<=i<n<=32; and
allocation-size division protected by the size==0 branch. These are valid
source-local definedness arguments, conditional on the source-reported site
association. They do not establish independent property origin, readability,
ownership or admission. Strict REJECT_ALL/proposal DISABLED remains unchanged.

GUARDS.json preserves all7 exact SUCCESS unsupported records: insertion has
is_inbounds pointer-to-unallocated-memory, same_allocation, caller_location and
panic runtime; sort9 has same_allocation, caller_location and panic runtime.
SUCCESS does not remove their presence or create an independent theorem about
unsupported paths. No guard, U or extra failure was filtered. All five completed
inventories total602 properties, with71 class=unreachable/status=SUCCESS records
separate from28 status=UNREACHABLE records. All602 have nonempty file and positive
string line locations. No new missing-metadata case or location waiver is
needed or recommended. Earlier f740/ff193 exact exceptions do not transfer.
Shared emitter/source/MIR origin and both incomplete location inventories stay
UNKNOWN. Twenty-five missing/null/wrong-type/zero-location mutations, including
SUCCESS system records, reject through the frozen rich reader.

The source plan contains19 assertion sites and46 covers, not predicted native
property counts. Unwind34 on controls and36 on positives matches native
registration/argv, with unwinding assertions enabled. All five exported native
unwind properties, on insertion, are SUCCESS. No native unwind properties are
invented for other inventories. Source bounds cover the34-element frame and
construction loops with exit headroom and the <=32/16/8 nested scans per loop.
The Cell fallback N0..16 and u8 network N0..8 families have no completed native
inventory: the source-wide assertion total is not a result; all respective
four role sites,22/14 covers, including17/9 exact length covers, remain UNKNOWN.
Neither row qualifies a length family or full N16/N32 path.

| Cost scope | Cell fallback | Network u8 |
| --- | ---: | ---: |
| Compile/initial-export upper bound s | 37.293 | 36.091 |
| Whole child elapsed s | 600.515 | 601.687 |
| Observed PGID VmRSS peak KiB | 3007384 | 3883252 |
| Observed outer census peak KiB | 3031420 | 3907572 |
| Effective inner memory cap KiB | 6291456 | 6291456 |
| Admission available KiB | 14908636 | 15305768 |

Both reach initial stock export and a native start, then termination_reason
timeout, timed_out=true, originalexit=-15/signal15. The outer child600 timer
includes compilation, which completed under180. This is not a recorded RSS,
compile180, slot720, worker710 or campaign6900 cutoff. Memory is
min(6GiB,12GiB,available-2GiB); all caps remain unchanged. Shutdown is verified,
worker exit0, exclusive-subreaper PID/starttime containment verifies and adopted
children are reaped. Fallback cleanup precedes the network launch; network
cleanup precedes terminal packaging. No supervisor cutoff/global stop or
surviving owned processes is recorded. Original RunnerError/incomplete states
are preserved. Each retains64 lifecycle events with122/101 omitted respectively;
this is not complete diagnostic history. Exact kill time and escalation history
beyond the retained observations remain UNKNOWN.

RSS is nominal50ms, non-atomic owned-PGID sampling. It is not a true kernel,
cgroup or process-tree peak; component maxima are not simultaneous. Exact
RSS at signal, symex/backend subphase, VCC counts, exclusive backend duration,
and censored native verification times remain UNKNOWN. Insertion51.863257375s
and sort9223.202229754s are exported native verification_time_s, versus whole
children94.058/260.338s. Campaign1672.393379874s, setup581.386216640s and tool
build283.670s are distinct scopes. No matching speedup or uncensored fit follows.

Bounded validation passed: the disposable W11 replay reproduced all29
manifest-covered files byte for byte with1000 checks/45 adverse controls; the
separate audit.py passed648 checks and25 metadata adverse controls. No acquire,
full267Validate, compiler, verifier, native runner, CI, raw/full archive/log,
GCS, ledger, source/control/evidence or policy mutation was performed. The only
new persistent files are this review directory.

Disposition is APPROVE with the limits above; findings=[] and no correction
request to original11. Strict producer and sealed expected_match remain false
on all7; two SOURCE_REPORTED positives are candidates only. Qualified new
leaves, provider contexts, closed proof obligations and independent B1/B2 credit
remain zero. All10 deferred categories remain open. Root may verify this exact
committed review and intake before separately issuing an S4 PLAN task; this
review authorizes no source implementation, dispatch, CI or admission.
