# W13 — S2 r4 avoid ordinary replacement of contracted functions

ISSUED coordinator/owner16:31. Fresh /new13, current model/tier, Fast OFF;
no subagents. Correctness verification. STOP only real blocker, not volume/context.
No local compiler/cargo/rustc/Kani/CBMC/expansion/verifier/full runner or CI.

Frozen inputs:
- Source diagnostic04c61ba50ae4d62caaf87ed84b90e84e958c184f at
  kani3300/ch8-s2/r3-closure-diagnostic/ (11 files/10 hashes root checked).
  Trace establishes conditional FnStubPass replacement-body/original-instance
  contract metadata mismatch; actual failing R3 unit/body remains UNKNOWN.
- Exact stock tool0aac16ef62da9e9d5645782d458593e5d78143ba unchanged.
- R3 packageba7286f5f77277aed531eaaab601e94396dec909,
  source478dbf10d3fccd1119f4de7ac596c96d6dbe8ade/treeb5b25f4e59308df7b15340cae343f50ae9fd8a81,
  control dc1ad0f9ce364f9a7efb2c3cc32db6ed51b6db4b/tree1c199ee22001213c164ac0bb9c9b56c2e5f827df.
  Review379d32fcf6 and GO bcaf60f3e5 describe old candidate only.
- R3run44310254730: coordinator reports21.9s compile failure/0roots, same
  missing __kani_recursion_check_swap_if_less as r2. R1 cause still UNKNOWN.
  No V-W/V-R execution: owner superseded standalone bisect with this r4 package.

Implementation contract, one immutable candidate in isolated worktrees:
1. Remove ALL FOUR active ordinary contracted-target bindings across THREE roots:
   sort13_weak: swap_if_less -> weak_swap;
   general32_assumed and general32_weak: sort8_stable -> diagnostic_sort8;
   general32_weak: bidirectional_merge -> weak_merge.
   Audit all other active ordinary stubs in the11 effective root/cfg contexts,
   including imported/provider context where relevant, for the same pattern.
2. Negative controls use an S2-local faithful network copy or uncontracted callee
   seam/wrapper; no ordinary stub replacing a contracted function. Preserve fault
   meaning, positive comparator/domain/frame/init obligations, and six exact
   intended failure tags. Do not replace a faulty leaf test with unconditional
   assert(false) or remove the relation being tested. Explain copy-to-original
   operation correspondence and any changed control coverage explicitly.
3. For both general32 roots choose the least intrusive valid source-supported
   route: stub_verified with active same-cfg PFC registration, or separate
   uncontracted model callee. Preserve the exact full-value sortedness,
   multiplicity, initialized-byte and frame relation/domain; no lower-bit/order-only
   shortcut. If verified registration is used, it is registration ONLY: no proved
   leaf/PFC qualification inferred. Keep sort13/general32 DIAGNOSTIC_ASSUMED.
   Preserve positive production behavior/S1/nonS2 and all five swap preconditions,
   modifies/ensures. Do not evade the issue by disabling original contracts.
4. Add static preflight gate: every EFFECTIVE kani::stub target must have NO
   active contract attrs in that root cfg. Resolve full target identity, aliases,
   active cfg_attr and safety wrappers; requires/modifies/ensures/internal markers
   count. Reuse existing cfg/PFC machinery; ambiguous/unsupported input fails
   closed with an exact diagnostic. Keep verified-target same-cfg PFC gate.
   Both gates actually execute BEFORE build for ALL11 effective contexts.
   Distinguishing offline tests: frozenr3 rejected at all four bindings; newr4
   accepted; active/inactive contract cfg, wrapper spelling, alias/full target,
   foreign same basename and missing/wrong-cfg PFC mutations. No broad framework.
5. Keep one group, same11 selected roots/20 covers/6 negative oracles, three
   primary probes, protected binaries/decoder/error controls, backend600s,
   compile900s, rootsum6600s, group7500s, internal8100s, step7560s,
   setup1800s, job180min, serial1/RSS12GiB+2headroom. Stock tool and reviewed
   runner B-01/B-02 logic unchanged except necessary gate/identity integration.
   Enumerate exact changed bytes; native compile/causal repair NOT_RUN.

Use new source/control worktrees, preserve all old candidates/reviews. Final
source must retain checkout-depth5 ancestry (sibling parent97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a,
not extra child of478); final control sole parent9e14e033f9ee31522b571c127609dcdff76d230b,
not child ofdc1. Keep control/source/tool checkout7/5/2. Rebind full stock-relative
ci_changed_paths/payload/request/workflow hashes and all source/variant inventories.
Replay exact source/control/stock-parent patches; test actual final identities,
or distinguish precursor tests and final binding-only changes explicitly.

Write only g0 kani3300/ch8-s2/batch-r4/: exact SOURCE/CONTROL/PINS/CI-REQUEST,
patches, ORDINARY-STUB-CONTRACT-MAP/CFG-PFC-MAP, source diagnostic references,
targeted tests/preflight evidence, validator/manifests, REVIEW14-REQUEST/HANDOFF.
Read r3 package layout to reuse; no broad audit or native execution. Include a
small owner-only issue-candidate note: conditional stock mechanism, minimal
reproducer needed, actual runtime confirmation NOT_RUN; do not open issue/PR.
Ownpaths-only commit --only, [skip ci], Tiramisu-Cake <igkharin@gmail.com>.
No CI/rerun/cancel/push/PR/ledger/reservation/budget; ledger a4e8bdd22f:
29/29 +9/14=38/43, historical r0..r3 charged0. Only confirmed pre-root compile
failure qualifies0; successful execution not free by assumption. Next: review14,
then exact GO-request, coordinator alone dispatches after separate GO.
READY <full g0/source/control/tree/parent/request hashes> <test and scope limits>.
