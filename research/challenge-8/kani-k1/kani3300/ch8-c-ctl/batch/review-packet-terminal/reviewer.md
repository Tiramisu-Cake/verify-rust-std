# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `cdd3c6d04112cc1b1e1a80a850389236647bc849`
- Candidate: `64ec781bc119279ccc4365aa831d2a9d0a792fee`
- Candidate tree: `33e95dc779cefde33132f8e265d9588b9d905b14`
- Diff SHA256: `2549b94c209db00ca72cbb1f9733ef5608e1e37ccf2346e0639dcb66b14fcd7a`

## Defect

Per-root std invocations repeat Cargo compilation. Batch C roots by identical flags, preserving source/oracles/classes and per-root structured binding. Review final candidate including delta from f30f9851b842881743de273a1e64392d80e22dc7.

## Applicability

Direct user batch stage on g0 82cc48368e; correctness package preparation only. No push/CI/ledger/local cargo/rustc/Kani/CBMC, no nested delegation. Final lifecycle/snapshot delta from c52feb8a0de22727582b8f03ecf730eefed5d045.

## Invariants
- Frozen eight C rows/oracles/classes, std d073585946 on P-prime and pristine tool0aac; no source/model/compiler changes.
- One verify-std group for7unwind8, one group for1unwind12; repeated harness/exact/jobs1/timeout600s and one export pergroup.
- No global list std compile; offline frozen expected inventory; actual PFC target binding from group export attributes versus unchanged rowtarget.
- Separate900s compile/preparation cap/receipt pergroup and group cap=sum rowbudget+compile; total6600s, workflow112m run/150m job.
- RSS group<=min(12GiB,avail-2GiB), perroot UNKNOWN; original exits/signals/errors, source/binary snapshots; no false aggregateCOMPLETE on stops/invalid exit/missing rows.
- Strict stock export identity, target/timeout/features/checks, core/manual binding, failure/property consistency, positive checks for source assertions.
- Immutable bounded compile head/tail snapshot and retained marker SHA; exception-safe kill/reap/join after spawn and on normal orphan cleanup; marker/export reads honor size cap.
- Terminal top-level outcome is exactly {'kind':'COMPLETED'}; missing/null/ill-typed/NOT_RUN outcome cannot yield a row class or aggregate expected exit.

## Required controls
- 33 isolated Python synthetic tests; static parsing; actionlint; request/digest comparison; git diff --check. No compiler/verifier.

## Declared dependencies

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Actual proof/runtime compiler binding and resources NOT_RUN; no independent proofcredit.
- Named successful assertion/cover message correlation remains pending; frozen source oracles unchanged.
- Only package readiness; eventual C activation remains same-tree sole-parent0aac sibling, not child of local skip-ci chain.

Do not execute source or evidence from this packet. Do not claim new proof credit.
