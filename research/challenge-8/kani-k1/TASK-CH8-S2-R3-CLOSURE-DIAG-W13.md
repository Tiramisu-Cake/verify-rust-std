# W13 — trace missing contract closure from exact stock Kani sources

ISSUED by coordinator, owner16:14. Fresh /new13, current model/tier, Fast OFF;
no subagents. Correctness verification. STOP only for a real blocker, not
volume/context. Finish available source analysis; unsupported conclusions UNKNOWN.
No compiler/cargo/rustc/Kani/CBMC, executable expansion, verifier or full runner.

Inputs, immutable:
- Tool 0aac16ef62da9e9d5645782d458593e5d78143ba (read exact Git objects using
  /root/kani-ch8-s2-r3-final-w13; do not inspect its changed control as stock).
- S2 source 478dbf10d3fccd1119f4de7ac596c96d6dbe8ade in
  /root/verify-rust-std-ch8-s2-r3-w13. S1 accepted source
  99e8456d200fff1299ee5756279cddb23921dc65; compare exact contracts and cfg.
- g0 batch-r3 ba7286f5f77277aed531eaaab601e94396dec909, review379d32fcf6,
  request f6a0d1c354237c1f0ffde252cef84ec2e30b739ae1e5ef41a54ec7cfa3fb761e.
- Control dc1ad0f9ce364f9a7efb2c3cc32db6ed51b6db4b; actual trigger
  6d7f3c4b5b3f5db3c20d7b30b6363ead9096ba26, parent9e14, tree1c199e.
- Coordinator16:14: run44310254730/1 compile FAILED21.9s,0roots, same sole
  error as r2: Failed to find contract closure __kani_recursion_check_swap_if_less.
  R3 path normalization did not remove failure; retire that candidate as a remedy.
  R1 original diagnostic remains unavailable/UNKNOWN. No historical-cause inference.
- Only this reported diagnostic and source files needed; no raw/full logs/archives,
  GCS/Cloud bypass or automatic old intake. Prior packets/evidence stay immutable.

One bounded source investigation, with exact commit/path/line citations:
1. Trace kani_macros sysroot/contracts generation through attribute state,
   closure naming/insertion/nesting and recursion-check synthesis. Trace stock
   contracts.rs find_closure (reported line728), mark_unused, all callers/modes,
   and the MIR body/var_debug_info actually searched. Identify concrete conditions
   for a generated closure to be absent or searched in the wrong body/scope.
   Separate source-provable paths from unobserved Rust MIR optimization behavior.
2. Compare S1 vs S2 swap_if_less: ensures with old(), modifies, all five actual
   preconditions, generic T/F, unsafe fn, return/body nesting and cfg. Include
   otherwise comparable contracted functions only where they distinguish a path.
   Explain the required var_debug_info name at each source step; no token-path
   speculation or claim of observed macro expansion/MIR without executing it.
3. Map ALL11 effective S2 roots/cfg and ordinary/verified stubs to swap_if_less:
   direct/transitive call or provider registration, contract mode, selected body,
   mark_unused entry and expected lookup. Trace compiled providers outside selected
   roots if they affect traversal. Explicitly mark any reachability/instance facts
   that require MIR and therefore remain UNKNOWN. Keep diagnostic models distinct.
4. Assess two workarounds as proposals ONLY: ensures without old() with snapshots
   in harness; separately contracted wrapper fn. For each show what state relation,
   domain/frame/init/multiplicity/PFC consumer guarantee is retained or lost, whether
   the original function still reaches mark_unused, and required controls. Harness
   assertions cannot silently replace a reusable contract. Do not weaken safety,
   S1/nonS2 behavior or promote DIAGNOSTIC_ASSUMED summaries to proof.
5. If exact sources do not establish the cause, say UNKNOWN and design the smallest
   discriminating diagnostic bisect: one factor per variant, minimal root/provider
   cfg, baseline S1 vs exact failing S2, old-free ensures vs old(), modifies and
   generic/unsafe factors ONLY when source reasoning motivates them. Give predicted
   observations separating hypotheses, required bounded diagnostics (including
   closure/debug names if proposed instrumentation is necessary), variant identities,
   stop conditions, controls, caps and how success/failure affects root start.
   Proposed patches/commands are reviewable DATA in packet, NOT_APPLIED/NOT_RUN.
   Do not design a broad solver sweep or promise every variant is free: only
   confirmed compile failure before first root qualifies0; other outcomes require
   accounting decision. Each execution needs independent review + separate GO.

Write only g0 research/challenge-8/kani-k1/kani3300/ch8-s2/r3-closure-diagnostic/:
REPORT.md/json, SOURCE-TRACE.md, ROOT-MODE-MAP.json, WORKAROUNDS.md,
DIAGNOSTIC-PLAN.md/json when needed, INPUTS/PROVENANCE/MANIFEST, HANDOFF.
Compact exact excerpts/references and source-only consistency checks suffice;
no new framework or broad repeated test suite. Include exact full hashes and a
clear ESTABLISHED / SOURCE_SUPPORTED / UNKNOWN distinction. No native credit.
No source/tool/runner/request edits or worktree mutation; no CI/rerun/cancel/push/
PR/ledger/reservation/budget. Ledger a4e8bdd22fc18919640fbff56e52eec69dc3f34a:
item1 29/29, item2 9/14, total38/43; r0/r1/r2/r3 charged0, real cost preserved.
Ownpaths-only commit --only, [skip ci], Tiramisu-Cake <igkharin@gmail.com>.
READY <full g0 SHA> <established cause or precise UNKNOWN and next discriminator>.
