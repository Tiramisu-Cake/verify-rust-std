# W11 handoff to reviewer14

READY for exact committed delta review. Task `task90b7e5bd7f7dcecc00e7009196a466a7422f179d`.

- Control: `b678fb6cdd5edf69a4e952167422f36a45a3d6cb`, tree `beb2346615ffbb7027b2f1ea8ea33a149952aa0b`, required parent `9e14e033f9ee31522b571c127609dcdff76d230b`.
- Baseline: `2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8`, tree `b04ce6fd7a2c937bf72fcda7a262eef65a9f45bb` (untouched).
- Std: `9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6`, tree `64d96010b0b4b896322e26d700c253f834ba9fd6`.
- Stock tool: `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.
- Worktree: `/root/kani-ch8-s2-diagnostics-w11` (detached; no CI branch).
- Narrow review: CONTROL-REPAIR.patch, from baseline 2ec to the candidate.
- Parent replay: CONTROL-DELTA.patch; full stock replay: CONTROL-CANDIDATE.patch.
- Exact payload/request/workflow hashes: IDENTITIES.json and CHANGED-FILES.json.

New `rustc-stdout-receipt.json` / `rustc-stderr-receipt.json` retain textual error
blocks independently of previews. Group/execution/compile/row receipts expose
`rustc_diagnostics` summaries with references to those shared receipts (never
per-root attribution). Compact evidence embeds the structured receipts and a
separate `diagnostic_retention` summary. Text strips ANSI; offsets always index
original per-stream bytes, half-open. Receipts persist at each chunk, including
pending header/context; provisional snapshots remain incomplete through EOF
until execution finalization. Fallback reads these durable receipts, never
reconstructs omitted diagnostics from previews.

Retention and pending-line bounds derive from the unchanged stdout/stderr caps;
record-count bounds derive from the same caps to bound metadata. Cap loss and
abnormal EOF have explicit reason, observed dropped blocks/bytes, unscanned
bytes, and unknown unobserved counts. `complete` covers observed textual error
retention only. Producer completeness always remains UNKNOWN; reported error
count gaps and explicit suppression make the combined summary incomplete.
Natural nonzero compiler exits with fully read pipes can retain complete emitted
diagnostics. Successful empty streams differ from spawn/timeout/cap/partial data.

Packing prioritizes small receipts, then diagnostic receipts. Compact caps retain
full diagnostics when possible, otherwise emit explicit payload-omission
counts/reasons/projection/original hashes and mark artifact retention incomplete.
Input limits/missing/invalid receipts remain explicit. No raw log export. The
synthetic-evidence directory is a bounded Python-child example, not CI evidence.

Validation: 29/29 final targeted tests PASS; static checks/patch replay in
PACKAGE-CHECK.json. Expanded earlier selection 69/69 PASS is stage-qualified.
Source/tool/argv/cfg/11 roots/20 covers/6 negative oracles/proof outcomes and all
hard caps unchanged. Workflow adds only the offline diagnostics unit tests to
its existing preflight; derived payload/request hashes updated.

Reviewer14 must review this exact committed delta; review **PENDING**. Production
runtime/CI retention **NOT_RUN**. Run44284869572 cause **UNKNOWN**. No new proof
credit. Item1 28/28, item2 provisional10/14, total38/42 are owner-reported and
unchanged; charge/retry is owner-only. No CI/rerun/cancel/push/PR/ledger/
reservation/budget/labels/publication. W13 static source diagnosis is untouched.
