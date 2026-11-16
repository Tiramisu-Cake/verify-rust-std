# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `c03363b3b0a83fa9e78c4841720cb48ee7638c6a`
- Candidate tree: `8c51bd047ed6d3287572277eba23b28f458e7e87`
- Diff SHA256: `19b10fcc0877ecce0476242a35f7beea9725773f794754172926ac5b3dc013cf`

## Defect

S1-02 standalone list codegens every std harness and was killed by an incorrectly shared 600s/root timeout, without list receipt.

## Applicability

TASK-CH8-S1-LIST-W13.md; g0 input45498717e2; preparation only, no push/CI/publication/ledger; no compiler/verifier execution. Previous control for minimal delta comparison:8c8ac10d675fff41d5ec1b2684c6f673cd6bfaf2 (sibling, not ancestor).

## Invariants
- Candidate is sole child of stock tool0aac; source S-prime f22f84f316/treee0dc unchanged. Host/workflow binding and all23 literal rows/oracles/root limits remain unchanged.
- Option a: list timeout1500 independent of600s/root; list consumes existing shared4500s phase. Existing120min job=30min setup+75min phase+15min fallback/upload, including observed~6min list compilation. No budget enlarged except list-specific timeout. Planned list is updated300 to1500, so planned list+rows=4260s; actual phase guard remains authoritative.
- Inventory validation and row proof parsing retain previous semantics and PFC target binding. List receipts persisted for nonzero/timeout/signal/launch/preflight/parse failures; capture stdout/stderr bounded head+tail; fallback marks uncompleted receipt UNKNOWN.
- execute default row behavior retains prior caps; capture_tail is opt-in only for list.

## Required controls
- 20 synthetic unit tests including real Python subprocesses (no Kani) for success/nonzero/child signal/external signal/timeout/RSS/output caps/exec errors, invalid list JSON/bindings, fallback interrupted/completed receipts and unchanged prior error paths; exact row/workflow/function comparisons, payload hashes, actionlint, clean source and control checks.

## Declared dependencies
- `.github/workflows/ch8-s1.yml` → `dependencies/0000.bin` (mode 100644, SHA256 8c396c715dc65add25a7a28e6812824d45ae1eb263456a85e567864516f41a6f)
- `.github/actions/setup/action.yml` → `dependencies/0001.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)
- `kani-driver/src/args/list_args.rs` → `dependencies/0002.bin` (mode 100644, SHA256 bcc5d36a41df479d6e5ad7380a5bcca9f7c7e57f6bc6e1f98ae9e61f5f40f64e)
- `kani-driver/src/list/collect_metadata.rs` → `dependencies/0003.bin` (mode 100644, SHA256 32948d1a96535a49ed82e1c3bb854f6ff9f8ce51fd02a8a8af85ad6b5a55cc90)
- `kani-driver/src/call_cargo.rs` → `dependencies/0004.bin` (mode 100644, SHA256 6801ea256ab3464b72487c8aacc17e5e79920903304aa82d5f02e23d129c6129)
- `kani-driver/src/args/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 ba665a7270786a30b4ffe3cf1bf0b5dc971023901c8ee110de8c6a79b3ae4d7e)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No compiler or verifier has been run locally; all23 proof rows NOT_RUN; no proof credit. A larger list timeout does not prove full std list will complete in1500s.
- No nested delegation. Review committed exact candidate and return compact findings/decision. Write report only to g0 kani-host-list/REVIEW.md; do not edit candidate.

Do not execute source or evidence from this packet. Do not claim new proof credit.
