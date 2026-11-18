# W11 localized repair — same14 delta handoff

Ready for exact committed repair review of **B-01/P1** and **B-02/P2** from
review `5db34a924329e05602bf1f8643ad0f4082653b3c`. Author repair evidence does not close these findings.

- Control `472be8c3794d7a4530760ab7d5eae4ce950aa01c`; tree `4835c615d20e6606ddcdc64bbb8314973cec141b`.
- Required parent `9e14e033f9ee31522b571c127609dcdff76d230b` (new detached immutable sibling).
- Frozen old control `b678fb6cdd5edf69a4e952167422f36a45a3d6cb` / tree `beb2346615ffbb7027b2f1ea8ea33a149952aa0b`.
- Frozen old package `ac956bdf4db98a95e2da988ccd2c527582d3d32f`; original worktree unchanged.
- Source `9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6` / tree `64d96010b0b4b896322e26d700c253f834ba9fd6`.
- Stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.
- Request SHA256 `8efb33417013116119602d9cf8e62a01de7b25ed2d2bbde6b9abd5d6457dd212`.
- Workflow SHA256 `973944169dd4d7f2fc169582b1327cc8e31fa96710a2a597ed0a126ef37e4a2e` (byte identical to b678).
- Worktree `/root/kani-ch8-s2-diagnostics-r2-r1-w11`; no CI branch or publication.

Review CONTROL-REPAIR.patch from b678 to this candidate: only parser, packing,
localized regression tests and three necessary payload hash bindings change.
CONTROL-DELTA.patch replays from parent9e14; CONTROL-CANDIDATE.patch from stock0aac.
All three reproduce the exact tree. CHANGED-FILES.json and REPAIR-MAP.json bind
old/new bytes and both finding-specific tests. MANIFEST.sha256 covers this package.

**B-01:** packing enumerates expected selected group/execution receipt inventory
as well as actual stream receipts. Both-main-stream deletion cannot vanish
behind complete setup. Missing receipts and NOT_RUN/IN_PROGRESS/INTERRUPTED
remain explicit in diagnostic state/reasons; existing receipts/exits/outcomes
are untouched. Row/compile references do not create separate pipe captures.

**B-02:** numbered N-minus/N-plus lines remain in their error block, including
following source/note/help context. Exact165-byte, both-stream, ANSI/split and
packed-text controls pass with original byte offsets and no cap increase.

Final evidence: **32/32 localized PASS + isolated preview1/1 PASS**; preflight
and three exact patch replays PASS. An earlier33-test attempt failed the existing
preview snapshot timing assertion; its full transcript is retained. That runner
code/test are unchanged. This observation is explicitly returned to coordinator
and same14; no out-of-scope timing change was made. See VALIDATION.md/json for
all stages and the discriminating old-candidate negative results.

Same reviewer14 must independently review this exact committed delta. W13 may
consume these exact repaired runner pins after approval; its source, combined
batch-r2 files and scope-A approval are untouched. This is not a combined-candidate
approval. Source/tool/caps/argv/cfg/selection/11roots/20covers/6negative oracles,
native exits/shutdown and proof outcomes remain unchanged. No production retention
claim; historical r1 error not recovered. Production NOT_RUN, historical cause
UNKNOWN, proof credit NONE.

No compiler/cargo/rustc/Kani/CBMC/full runner/CI/rerun/cancel/push/PR/ledger/
reservation/budget/labels/publication/subagents. Item1 28/28, item2 provisional
10/14, total38/42 unchanged; charging/retry is owner-only. Current model/Fast unchanged.
