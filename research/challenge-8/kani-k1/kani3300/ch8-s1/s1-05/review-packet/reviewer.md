# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`
- Candidate: `8860d38558651f7cf2e292d57b06b378c6ad3b94`
- Candidate tree: `28a1cfaff9484d4fa2ae0f2368f2c52a0c6d76ad`
- Diff SHA256: `1af4ebbe13783ca5a70d45bf7aecd1f2672c465f741764195b1674b9850f2f55`

## Defect

S1-04 terse output lost full check/cover descriptions and locations; stale runner oracle/veto made all jobs fail.

## Applicability

S1-05 preparation only; stock 0aac tool and unchanged std 5be85699, same35 rows,14groups; no dispatch.

## Invariants
- No source/tool changes, no relaxed proof checks, exact rows/groups/pins/timeout/unwind/memory retained
- Single-parent control40b5, changed paths, attempt1, typed YAML, depth3 retained
- Runner records evidence only; ACCEPTANCE-POLICY-BATCH/w11 offline classification; no acceptance/proof credit
- Each rich property must have exact ID/class/description/file/line/status and same-invocation stock reconciliation

## Required controls
- Synthetic success/error/timeout/partial/missing/null/wrong-type/NOT_RUN/source-target mismatch tests
- Real S1-04 rich object fragment with multiline description; reject missing location/description for every record
- Preserve native YAML and actual shallow-clone regressions; frozen F1-F8 oracle and companion declarations

## Declared dependencies
- `ch8-s1-control/activation-default.patch` → `dependencies/0000.bin` (mode 100644, SHA256 cee9e21c4b5015d6daf53c286f781602d0890e4ed23239f968d228088335dcc3)
- `ch8-s1-control/activation-override.patch` → `dependencies/0001.bin` (mode 100644, SHA256 6dcb40cc4118035de700f0988a6766c96aad8f4def76513f0f10f275d091c356)
- `ch8-s1-control/fixtures/s104-rich-fragment.json` → `dependencies/0002.bin` (mode 100644, SHA256 08958a31eb173ce59173a588ffd9e785ed9cef0086a733b7fc998af843c054cc)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No actual Kani execution in this stage; future regular output may expose missing locations and must fail closed
- B1/B2/general theorem NOT_ESTABLISHED; exact future artifact byte length unknown; bounded8MiB compressed32MiB uncompressed/group
- Raw regular display is unescaped; malformed or ambiguous records rejected, unknown status restored only from same-row stock ID; unsupported/mandatory unreachable role review offline

Do not execute source or evidence from this packet. Do not claim new proof credit.
