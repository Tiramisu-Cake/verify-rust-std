# WIDEDOMAINS G3 — final primary build proposal

G3_PRE_BUILD_REVIEW_PENDING. No G3 dispatched; new exact-packet GO required, including the changed
timeout/reservation: **4 minutes/root, $0.945 maximum**. This is primary build 3 of 3; no retries.
Worktree `/root/verify-rust-std-kani-widedomains`, branch `experiment/kani-k1-widedomains-20261105`.
Stable owner `k1-merge`, stage `widedomains-g3`. Task base `34f69f034b`, library base `4fa6151b6a`.
G1 source `90fadd7ccf8b5bb32d04401d274a6f492b612897`; G2 source `4fbe77cf46cd416fb6140a54bf6c9ffb78479d3c`.
G3 library commit `a1b66147f130b05eba221e8620105a6540341fb5` (only the opt-in module).
All G1/G2 functions and attributes, including F items and successful consumers, remain token-identical.
Runtime/contracts and tooling remain unchanged; tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`, nightly `2026-10-22`.

## G2 result and credit withheld

Build `100bfc31-d211-4e7a-be52-fc6e72ab7d69`: COMPLETE, Cloud FAILURE, gate=false, Kani exit 1.
Four SUCCESS: matching-F swap backing32 (39.150494 s), u64 N32 swap/insertion-stubbed network
(146.68248 s), merge8 scratch48 src32/dst0 (80.85085 s), real sort8 merge consumer (7.120541 s).
Their covers are 23/23. All four initialized-tail PFCs and both insertion PFCs timed out at 180 s.
The whole tail -> insertion -> network chain has **no composition credit**, and the G2 network
is not an unconditional ordinary candidate. The matching merge8/sort8 pair is credited separately
for its exact T/F/allocation/initialization/frame geometry, not the full general route.
Bounded diagnostics have six timeout lines, no error/unused/widedomains match, no reported OOM.
Tooling/source/request/pool checks pass; max RSS 4113984 KiB, compile+verify wall 24:45.44.
G1+G2 cost $0.9180; G2 $0.4320 is derived from combined ledger minus G1 $0.4860. No repairs/retries.
Exact bounded outputs and approved G2 request/covers/static report are preserved under `g2/`.

## G3 frame encoding and unchanged domains

Six new roots replace a whole-array saved copy plus 32 explicit equalities with one independently
arbitrary index p outside the modified region, saving only its original u64 value. The helper and
comparator do not receive p. All target requires/modifies checks, values, T/F and input domains remain.
For every valid tail input, at most 20 of backing32's elements are in its inclusive modified region;
for every insertion input, len<=20. Thus an outside p always exists: the assume on p eliminates no
helper input. Universally checking equality for every such p is equivalent to the previous explicit
post-frame equalities for every outside index. Universal input/comparator choices and p commute;
no value is sampled from a fixed subset and no helper call is cut by the frame probe. This is an
encoding change, not a proof of timing causality or a claim that the existing TIMEOUT roots passed.
Left/right frame covers and length/offset endpoints check reachability. This argument concerns the
explicit value-equality frame; the original target modifies clauses are neither removed nor weakened.

All G3 roots fix T=u64, F=this module's unchanged `tail_less_u64`. Its callback cover hook is replaced
with the same no-op only where all callbacks are cut by verified stubs. The F item/type, volatile
reads and fresh arbitrary decisions are unchanged. Real-body PFCs retain true/false callback covers.
G1's comparator is a different function item and its proofs are not reused for this chain.

## Request and row acceptance

Request `widedomains-g3-20261105-01`, SHA256
`64bc9e9a17803cf8f7f6fb962df0f2b2000ff52df740618dc9c05cfc76a8642d`.
Diagnostic, controls=true, inventory=false, jobs=1, gcb-e2-standard-4. Ten SUCCESS expectations,
**77/77 covers**, zero unreachable covers. Four minutes is the smallest integer-minute watchdog
that includes the complete 200-second candidate window; elapsed >200 is reported separately.
Each tail partition must both pass and take <=200 s to satisfy step 2. A tail SUCCESS at 200..240 s
does not meet that stage criterion. Other SUCCESS roots above 200 s are facts, not ordinary candidates.
The Kani gate alone does not check covers, timing eligibility, domain matching or transitive credit.

All names below have prefix `slice::sort::shared::smallsort::verify::widedomains::`.

| Root | Purpose / domain | Covers |
| --- | --- | ---: |
| insert_tail_probe_u64_backing32_tail1_to4 | unchanged initialized domain, outside probe | 9 |
| insert_tail_probe_u64_backing32_tail5_to9 | same, tails5..9 | 9 |
| insert_tail_probe_u64_backing32_tail10_to14 | same, tails10..14 | 9 |
| insert_tail_probe_u64_backing32_tail15_to19 | same, tails15..19; start16 permits only15 | 10 |
| insertion_probe_u64_backing32_len1_to16 | insertion PFC, verified tail calls, starts0/16 | 10 |
| insertion_probe_u64_backing32_len17_to20 | insertion PFC, verified tail calls, start0 | 8 |
| merge_probe_u64_len16_network_backing32 | intermediate N16, source32 -> disjoint uninit destination32 | 7 |
| merge_probe_u64_len32_network_backing32 | actual network N32 merge geometry | 6 |
| unstable_network_safety_u64_n32_all_helpers_stubbed | real unstable route, swap/insertion/merge verified stubs | 2 |
| merge_probe_u64_len32_general_scratch48 | actual final general N32 merge geometry; standalone PFC | 7 |

## Call-domain inclusion and dependencies

| Consumer / calls | Union of matching PFC domains | Inclusion / credit rule |
| --- | --- | --- |
| New insertion len1..16, s=0/16, any offset1..len; actual tail calls t=offset..len-1 | Four new tail PFCs: initialized [u64;32], s=0/16, t=1..19, s+t<32, same F | Each t<=15 fits both starts. Explicit probe ranges over every index outside [s,s+t]; target modifies unchanged. No credit unless all matching tail partitions pass <=200 s |
| New insertion len17..20, s=0, any offset1..len | Same four tail PFCs | Each t<=19 fits start0. offset=len is the valid zero-call case. Insertion probe ranges over all indices outside [s,s+len). Both insertion PFCs must pass for the complete length1..20 chain |
| G2 successful u64 N32 network: swaps s=0/16,a,b<=12; insertion len16,offset13,s=0/16 | G2 successful matching-F swap PFC + new insertion PFC + all four tail partitions | Identical F/u64/initialized allocation32; caller slices match. Consumer and these callee functions are unchanged. Credit across builds only after the entire chain is established; currently withheld |
| New all-stub real N32 network: same swaps/insertion plus merge32 | Same complete tail/insertion chain + G2 matching swap PFC + new network merge32 PFC | Merge source is backing32[0..32], destination is separate uninitialized MaybeUninit<[u64;32]>, exactly the real network stack scratch. Requires all prerequisites and consumer SUCCESS/covers |
| G2 accepted sort8 consumer: real sort4, merge8 scratch48 src32..40 -> dst0..8 | G2 successful matching merge8 PFC | Same F/u64, initialized src8 and otherwise uninitialized scratch48. Unchanged accepted pair; no source40/dst16 or complete general-route transfer |

The merge16 root is an intermediate proof in the same source32/destination32 geometry. Network
N16 returns before merge, so it is not presented as a real N16 network call-site consumer.
The source probe covers all 32 initialized source elements, including the suffix outside len16.
N32 uses the entire source slice; the separate destination allocation starts uninitialized.
No destination bytes are read as initialized output in the standalone PFC fixtures.

The general32 PFC has a different allocation domain: fully initialized MaybeUninit<[u64;48]>
source, slice [0..32], disjoint fully initialized original [u64;32] destination. At the actual final
general N32 call all scratch slots are initialized: [0..32] by the two sorted halves, [32..48] by
the sort8 temporaries. The source probe checks all 48 values, including that suffix. This root is
a standalone PFC; no whole-general consumer is claimed, and it is not used to justify network32.
The all-stub network executes the real raw scratch copy after merge; no initialization/sortedness
postcondition is added to the safety contract and no value-validity/uninit theorem is claimed.
Real merge PFCs cut only the explicit order-violation boundary under abort semantics; stubs cut
their target bodies. No generic/stateful callback, ZST, permission or unwinding theorem is added.

## Budget, source checks and stop rule

Reservation: 10*4 + 30 = **70 minutes, $0.9450**. Own spent $0.9180 + reserve = **$1.8630 <= $4.00**.
Project cap $118.96; current bounded snapshot is in RUN-LEDGER.json. Recheck budget, owner and SHA
after GO. The unchanged main deadline is 2026-11-05 12:44:34.233475 UTC, closeout 13:14:34.233475.
Require at least this 70-minute reservation window before the main deadline for dispatch.
No new main window, retry or fourth primary build. A compile-error repair needs remaining caps.

Static acceptance: ordinary=219, cfg-on=283 (253 original + 10 per build proposal); old verify files,
all G1/G2 function bodies/attributes and F items unchanged; runtime/contracts byte-identical;
tooling equals base; no static orphan; exact ten G3 names/hash/covers; rustfmt and diff check pass.
Name lists are source-only; no full compiler inventory or local prover is requested.
Separate library/research [skip ci] commits, push without force, stop with PRE-BUILD REVIEW.
After exact GO: single k1g dispatch, cache `/tmp/widedomains-k1g-g3`, record UUID, k1g watch, end turn.
After wakeup use bounded summary/rows/peaks/log-grep and check-tooling; validate row identities,
all covers, per-tail <=200 s, full dependency chain and same source functions before any credit.
Then final RESULT <=45 lines, honest residual domains, commit/push and REVIEW REQUEST/closeout.
Even if all rows pass, no claim covers scratch48 tail domains, other start/initialization/allocation
patterns or all intermediate/odd merge lengths. Report those gaps; do not expand to another build.
