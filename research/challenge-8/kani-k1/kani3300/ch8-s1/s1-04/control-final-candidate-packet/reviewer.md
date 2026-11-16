# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`
- Candidate: `5fd538730869103cb7108cd823f58b1dac924960`
- Candidate tree: `81ded40ddd99579cbe06efd74e19b1bf5801803a`
- Diff SHA256: `6d1ecf3739233823b5e8577be6048ab53893f17cfcedd2fcb17d04dd93b5be53`

## Defect

S1-03 variant restoration/source snapshot diagnostics and negative description oracle fail; heavy symbolic roots timeout and grouping hides partial results.

## Applicability

S1-04 bounded Python runner, immutable request and group workflow; source is separately frozen/reviewed5be85699b8826e3286c0bf89efb9affefac0acb5.

## Invariants
- same checks root timeout600 compile900 jobs1 unwind source bounds and arbitrary values
- no proof credit; incomplete source/export/negative oracle and union fail closed
- no push/dispatch or ledger authorization; full14group coverage and exact identities

## Required controls
- Synthetic runner/package/service tests plus static source/YAML/identity closure; no Rust or Kani execution.

## Declared dependencies
- `ch8-s1-control/activation-default.patch` → `dependencies/0000.bin` (mode 100644, SHA256 cee9e21c4b5015d6daf53c286f781602d0890e4ed23239f968d228088335dcc3)
- `ch8-s1-control/activation-override.patch` → `dependencies/0001.bin` (mode 100644, SHA256 6dcb40cc4118035de700f0988a6766c96aad8f4def76513f0f10f275d091c356)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Actual proof NOT_RUN; false-ensures wrapper IDs unbound; named success/cover binding and exception-role review pending; no runtime-cost claim from split.

Do not execute source or evidence from this packet. Do not claim new proof credit.
