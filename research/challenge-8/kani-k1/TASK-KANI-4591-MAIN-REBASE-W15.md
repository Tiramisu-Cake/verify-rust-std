# Original15 — transfer repaired #4591 support fix to new upstream main

ISSUED current15 after owner/coordinator23:52 and root agreement. Preserve
current high/FastOFF, no subagents/model changes. STOP only a real blocker.

Frozen READY r1: g0 1d7ef5455f2ea790cd98dde9f38565edb59357ea,
`kani3300/wave0/issue4591-fix-r1/`; source e6aa083da3c93f3189039077795cc9a0d67d3a6d,
tree01140856c15e161ff6fc4c1ce460fd4208a298cd, parentmainfaffcee3bca2770c03bd21c3bde89cc8f6f7a14e.
W11-01 repair remains author-reported, NOT independently CLOSED; review
54ea8a918b761dc67213f7f24ae5163b7f463b42 and original packet remain immutable.
Do not send old r1 to review as a final CI candidate.

Connected upstream main NOW VERIFIED:
969f4648980a8e66cd0ca32fd3e714a55ac32cef,
tree c9a832dc1647c51ac3036429e5f97e73eb717ba7,
soleparent faffcee3bca2770c03bd21c3bde89cc8f6f7a14e.
Commit: Upgrade Rust toolchain to nightly-2026-11-18 (#5188).
This is upstream-main source, an allowed clean-room input. Do not inspect
unrelated unmerged PR implementations. Existing open PRs BEHIND/no conflicts
are left unchanged; this task never pushes them or changes S3 stock0aac.

Create a NEW isolated main-based candidate: one local [skip ci] commit whose
sole parent is EXACT969f, containing repaired e6aa compiler+test delta applied
to this new base. Preserve old worktrees/commits/packages, no in-place history
rewrite. Fetch exact upstream objects if needed, read-only; no publication.
Record patch replay/conflicts/resolutions and semantic invariance. New main
changes contracts.rs and attributes.rs as well as toolchain/API/dependencies;
review those relevant changes explicitly. Do not accidentally revert new-main
API/trait/type changes, Cargo.lock/toolchain or other upstream updates. If
adaptation is necessary, keep it minimal, document exact API/semantic reason
and return design ambiguity to root. Do not invent compilation success.

Preserve ordinary-replacement-source routing, all original/verified/PFC modes,
replacement safety, and W11-01 discrimination (direct selected provider FnDef
reachable in each harness; direct provider input passes, copied call input
fails intended postcondition). Keep i32-overflow issue reproducer oracle and
other controls. New native main/fixed tests remain NOT_RUN, old MRE on faff
cannot establish current-main native behavior. No guessed property counts.

Own new immutable output `kani3300/wave0/issue4591-fix-main-r2/`, with exact
old/new base/source/tree/parents, source semantic delta/range-diff (or equivalent),
patch hashes/replays, W11-01 mapping, tests/oracle/validation/manifest, request,
PRdraft and fresh relevant-main-drift check. Derive all native workflow/job
matrices from new969f; .github/workflows/actions/scripts MUST match new main.
Library/dependency/toolchain files likewise new-main bytes, no F4/customCI.
Full standard PUSH-CI on future nonskip SAME-TREE SIBLING/sole969f parent,
one commit in969f..final (local skipped candidate excluded), actual final-head
gate/newbase bindings. Native Kani all5OS+alljobs, Format/Deny complete, PR-only
release/std/bench deferred by owner scope; no cron/dispatch/enable or subset.

Meaningful bounded static/mock tests incl exact repaired fixture reachability
and direct/copy negative discrimination, complete split/full patch replays and
new-main invariance. Record actual object/provenance, not typechecking/MIR.
No compiler/cargo/rustc/rustfmt/Kani/CBMC/expansion/verifier/fullrunner/CI/push/
PR/issues/comments/rawlogs/archives/GCS/ledger/reservation/budget.
Ownpaths commit --only [skip ci], Tiramisu-Cake <igkharin@gmail.com>.
READY fullg0/source/main/tree/parent/patch/test/CI pins -> same11 ONE combined
W11-01+newbase delta review -> root GO only -> usercoordinator fullCI31/31.
Night root+usercoordinator decide work/GO; PR publication remains owner-only.
