# REALCONTRACTS G2 — pre-build packet

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
