# REALCONTRACTS G2 — historical pre-build packet and outcome

Coordinator GO after review of G1 report `a376005646353f5a9c15cd9af717bf83b0658b17` authorizes
self-dispatch of this described G2 after publication. Owner remains `k1-merge`. Dispatch must
wait for VALIDVALTWO build `13642a63-de9e-4e28-b4e3-f55fd370538d` to finish via k1g watch.
The alternative k1-network/CODEFIX lane is not used. No other agent's code, branch or diff is read.

Branch `experiment/kani-k1-realcontracts-20261104`; G2 library commit
`92d131ab3308199c1a739a3dcad178cc6806b732`; unchanged tooling base
`59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; Kani pin unchanged.
Stage `realcontracts-g2`; request `realcontracts-g2-20261104`; ledger `realcontracts-ledger.json`.
Diagnostic standard4 pool, controls true, jobs 1, ten minutes per harness, six rows, all expect SUCCESS.

| Row in verify::realcontracts | Domain / comparison |
| --- | --- |
| insertion_safety_u64_len2 | u64 backing2; arbitrary offset 1..=2, nondeterministic comparator |
| insertion_safety_u64_len3 | u64 backing3; arbitrary offset 1..=3, same comparator |
| unstable_network_safety_u8_n9_real | actual Unstable entry, full u8 backing9, real swap bodies |
| unstable_network_safety_u8_n9_stubbed | identical entry/body/F/backing, stub_verified(swap_if_less) |
| unstable_network_safety_u8_n13_real | actual Unstable entry, full u8 backing13, real swap bodies |
| unstable_network_safety_u8_n13_stubbed | identical entry/body/F/backing, stub_verified(swap_if_less) |

Insertion PFCs have one T/F instantiation each and unwind 8; offsets are symbolic, with no
sorted-prefix assumption. Covers request both comparator answers, offset 1, offset == len,
offset < len and normal return. These exact lengths isolate G1's symbolic len1..6 TIMEOUT;
a pass here does not establish the full len1..6 PFC or the universal generic contract.

u8 selects Copy/Freeze + efficient swap, then small_sort_network. N9 uses sort9_optimal (25
swap calls, indices 0..8); N13 uses sort13_optimal (45 calls, indices 0..12). Both then call
insertion at offset == len (zero iterations) and return via no_merge. A source check confirms
all constant positions are in bounds of the corresponding initialized writable allocation.
No panic stub is needed. Both members of each pair use one identical helper body, unwind 16,
full-domain kani::any inputs and arbitrary_less::<u8>, the same function item as G1's u8 PFC.
Only the verified-stub attribute differs; no assertions about order or permutation are added.
The consumer checks safety and normal-return reachability under the real call-site requires.
G1's swap PFC used backing4: compositional runs with a verified summary on backing9/backing13
are bounded consumer evidence, not an independent universal proof of that summary's body
on larger allocations. Report this scope distinction with the timings.

Only opt-in realcontracts.rs changes in library. Runtime bodies, signatures, existing contracts,
G1 roots, ordinary roots, scripts, workflows and tooling remain unchanged. Validation: existing
request validator; whitespace check; source equality for runtime/G1 roots; in-bounds position
check for both networks. No local cargo/rustc/Kani/CBMC. Compilation/proof remain untested.

Reserve (6 * 10 + 30) min * $0.0135/min = $1.215; existing spent $0.3645; sum $1.5795 <= $3.
Project preparation snapshot: 222 builds, used $94.4025, reserved $1.8225, with this packet
at most $97.4400 < $118.96; dispatch must refresh its ledger. G2 is the second primary build.
Publish library and research commits with [skip ci], push without force, emit PRE-BUILD REVIEW.
Then watch the gate build and end the turn. Its completion notification permits G2 self-dispatch
under this GO (no new permission request); dispatch exactly the published G2 request, immediately
k1g watch the new build and end the turn. Read only bounded K-1 evidence after completion,
update RESULT (<=35 lines) and ledger, publish, then REVIEW REQUEST / REALCONTRACTS ЗАВЕРШЁН.


## Observed G2 outcome

VALIDVALTWO watch delivered terminal FAILURE for `13642a63-de9e-4e28-b4e3-f55fd370538d`;
completion was the scheduling condition, so G2 self-dispatch proceeded under the existing GO.
No VALIDVALTWO summary, branch or code was read. G2 dispatched source
`c848fd4d0ddf5cfbb6ec3b0cccee12cfca88be1b` as build `ee952605-3d34-4831-b34d-5e84d22c2aea`,
then k1g watch delivered SUCCESS. Bounded summary/row page bind request hash
`d2c82a16e774b870643d8d06529f7a9f89b5e924843a7a8b4c3253390c2bd443` and the exact source.
Check-tooling passed pool/source identity and all six tooling hashes against the full base.
Summary COMPLETE, gate true, expectations true, Kani exit 0; all six rows SUCCESS.

| G2 root suffix | Time s | Failed/total | Covers | Unreachable checks |
| --- | --- | --- | --- | --- |
| insertion_safety_u64_len2 | 81.02985 | 0/160 | 6/6 | 4 |
| insertion_safety_u64_len3 | 105.375145 | 0/160 | 6/6 | 4 |
| unstable_network_safety_u8_n9_real | 6.299193 | 0/298 | 3/3 | 18 |
| unstable_network_safety_u8_n9_stubbed | 8.070763 | 0/375 | 1/3 | 18 |
| unstable_network_safety_u8_n13_real | 11.438447 | 0/298 | 3/3 | 18 |
| unstable_network_safety_u8_n13_stubbed | 16.726189 | 0/375 | 1/3 | 18 |

Exact-length insertion PFCs at 2 and 3 are feasible on this pin with arbitrary offsets/answers;
this does not close the symbolic backing6/len1..6 timeout or locate the next infeasible length.
The insertion CBMC peaks are 4.62 GiB (len2) and 4.71 GiB (len3), whole-run maximum RSS
4941096 KiB, wall 5:18.93; OOM scan none_seen. Unreachable checks are reported separately
from covers and are not extra independent proof credit. All insertion covers are satisfied.

The same-body paired consumers show no speedup: stub/real = 1.281238 for N9 (+28.12%) and
1.462278 for N13 (+46.23%). These are single diagnostic runs, jobs 1 on the standard4 pool,
not a repeated performance experiment. The stubbed network has more checked properties
(375 vs 298), but that correlation alone does not establish the cause of its slower time.
Real consumers execute the nondeterministic comparator and report 3/3 covers. Stubbed
consumers report 1/3: source inspection shows all swap callbacks replaced and insertion at
offset == len, so the return cover remains while the two comparator-answer covers are not
executed. This cover interpretation is inferred from the paired harness/route source;
the bounded summary reports counts, not individual cover names. Bounded log-grep independently
reports 1 of 3 covers with 2 unreachable for both stubbed consumers. Normal-return safety is
checked in the stated domains; ordering/permutation are not asserted. Larger-backing
consumers assume the real helper summary whose body PFC was bounded at backing4; they do
not independently establish a universal swap-body proof for backing9/backing13.

Evidence for the next step: requires/modifies on the real safe insertion helper compile and
prove at exact lengths 2 and 3; real swap summaries can be applied at actual N9/N13 call sites,
but measured stub composition is slower here. insert_tail/bidirectional_merge contracts and
an ensures model need separate work; no such contract/model was added in this task.

Costs from combined bounded k1g budget: three builds $0.5400, reserve $0. G2 cost $0.1755
is the combined amount less prior $0.3645; own cap $3 is respected. The two authorized
primary builds and sole G1 compile repair are finished. Only reports/ledger change after
this build; tested library, request, workflows and tooling stay unchanged. RESULT is 35 lines.
No further build or implementation is undertaken. Publish the final report with [skip ci],
REVIEW REQUEST, and REALCONTRACTS ЗАВЕРШЁН.
