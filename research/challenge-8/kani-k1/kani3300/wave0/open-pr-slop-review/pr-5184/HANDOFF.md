# PR5184 offline review — APPROVE

**APPROVE, no blocking findings. Retain all three harnesses and both test compilations.** The active-call set guard correctly distinguishes an in-progress resolved Instance from a completed callee on source inspection. The recursion diagnostic and the different-allocation unsafe/same-allocation reinitialized repeated-call controls are distinct and compact. No source functional change, test removal/merge or new framework is recommended.

- Task/input anchor g0: `98784e2ade6135d3177b0ad14c9ab88777ab6aa2`.
- Published head: `f99713506f7ba91f971f3b7359ebbe41ca373adf`.
- Tree: `d3127bc67a6317d939480aece405f6ea95993e24`.
- Base snapshot/merge base: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Read-only detached source: `/root/kani-pr5184-slop-readonly-20261119`.
- PR body SHA256: `78bf0bf18d653a3b6dcb1166707b998d9616f95f58ed57a2def038f76034b2d4`.
- Exact full-index patch SHA256: `7b24ed34ff91b4b33616fc3b91649df71359e5eec0f81a4086c9f71ea139a43c`.

REPORT.md traces insertion/removal, full monomorphized Instance identity, fresh argument graphs for finished callees and the explicit error/abort before recursive descent. It explains why depth0 still exercises a recursive analysis edge and why the later tuple target must remain. COVERAGE-EDITS.md accounts for all five files, all test/compiler helpers, three harnesses, flags/discovery and expected oracles. Keep the compiler byte-exact. Optional source edit is one comment explaining the depth-zero analysis choice; concise PR-only wording is provided in PROPOSED-PR.md with the exact license/disclosure and one pending CI link. No issue link was invented and no live/external text was touched.

All five source blob hashes/bytes, connected file identities, source patch and anchored snapshots match. Source is unchanged, detached and clean. Expected groups retain a supported user-facing recursion diagnostic and call-site text, plus a named adjacent uninit FAILURE triple, initialized marker/SUCCESSFUL and exact 1/1/2 summary. This is source/static checking, not actual native output, MIR or a graph-model proof. The Copilot snapshot is not independent validation.

Compiler/points-to solver/Kani/CBMC/verifier/compiletest/native formatting/CI: NOT_RUN. Base stack overflow, fixed diagnostic, property reachability, main-fail/fixed-PASS and historical runner/perf explanations remain unverified source claims here. Explicit coverage limits include mutual/diamond/generic/indirect and expanding-specialization variants; no broad recursion support or termination proof is asserted.

MANIFEST.json seals every other file here by SHA256 and byte length, excluding itself; the containing local [skip ci] g0 commit seals the manifest. Full delivery SHA is reported separately to avoid circular self-pinning. Other workers' files were preserved. No source edits, native tools, CI, push, live PR/external draft access/write, S4 work, ledger/accounting, subagents or settings changes occurred. Root must verify this packet before any later scoped text edits/implementation/exact review/CI/owner publication. No automatic next PR was started.
