# NETCOMP2 reuse of G1 leaf9 and binding control

Historical Build: b3e257d1-eaf9-4323-a8f1-f4648798cbd9.
Source: 0944189023c0c53620ed74a45bb2d2efef4c53cd.
Library commit/tree: 47ed440a23641545fba1eedd279a0ebabe6edf02 /
f9fa2945d6fd31f042b66926aad098f906f4abca.
Request SHA256: e7afc8c7cb631569289b751c103892302c736191f28153e95216f24c41dc312a.
Bounded recorded evidence: ../netcomp/g1.rows.txt, g1.checks-lines.txt, g1.tooling.txt,
g1.assessment.json and ../RESULT-NETCOMP.md. The historical G1 gate remains PARTIAL.

| Reused row | Historical fact | Dependency closure retained |
|---|---|---|
| netcomp_leaf_u8_n9 | SUCCESS, covers7/7, VT49.674446s, CBMC314920KiB | PFC root/annotations, swap_net9 clauses/body, region9/count9/canonical, StrictU8 and pure models, real raw swap and memory predicates |
| netcomp_wrong_cmp_u8_n9 | FAILED only canonical guard, covers2/2, VT0.5270568s | root/annotations, always_true_u8, register9/context9/Context9, adapter9/closed SwapBridge9, swap_net9 and dependencies, actual trait/network route |

static_check.py compares the entire N9 prefix to historical source after applying ONLY the
specified single cover move. That exact comparison preserves every N9 target/root/annotation,
contract clause, assertion, comparator/value/probe/backing/frame declaration and helper body
except check_context9's removed cover and the B9-root's added cover.
Neither reused row calls check_context9 or the composed positive root: leaf9 calls swap_net9
with no stubs; wrong-cmp9 registers then calls the actual trait entry directly. Its guard rejects
the received comparator and returns before the summary. Their reachable N9 source stays intact.
The same script verifies that every other library file is unchanged from historical G1,
including network.rs helpers/StrictU8/strict_less, specfix models and canonical guard,
smallsort runtime dispatch/networks/raw swap, memory predicates and all lower library code.
Dependency SHA256s are in static-check.json; protected lane hashes are in tooling-static.txt.
No tooling, compiler/model, pin, runner, solver/checker flags or trusted rule changes.

Both runs: T=u8, F=U8Cmp=fn(&u8,&u8)->bool; canonical StrictU8::CMP, full initialized
exact backing9/offset0, independent by-value u8 probe, pair-only modifies, unwind25,
measurement/controls:true/jobs1/uninit off/600s, k1-standard4, identical pinned tooling.
Pin: Kani9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12.
New N13 names/context/bridge are separate, with no edits to shared models or N9 assertions.

Reuse is explicitly authorized by TASK-NETCOMP2 Уточнения. These are historical rows,
not rows of the new Build. count-negative9 DOES depend on run9/check_context9 and therefore
is re-run; its expected cover inventory is3/3, not historically observed4/4.
New A9/B9 timings are compared directly. VT(B9_new)+VT(leaf9_old) is a mixed-run estimate;
CBMC peak=max(B9_new,leaf9_old), never a sum. No same-build leaf cost claim.
Source equivalence does not establish native compilation, cover reachability or new proof results.
