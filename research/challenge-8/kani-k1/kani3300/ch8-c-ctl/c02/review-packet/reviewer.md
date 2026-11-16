# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `64ec781bc119279ccc4365aa831d2a9d0a792fee`
- Candidate: `af49c7ef04d462f5f89b4b3d362b484b1d3f20d0`
- Candidate tree: `e10c359aba4830016105bb7e8a8b95544e4c3664`
- Diff SHA256: `6543624a9d45c4811866283894e07709f85321240ef3ae0f2776d6b7f283bb03`

## Defect

C01 bare PFC target syntax rejected by qualified-path equality; merge fixture memcmp unwind8 insufficient for 16-byte equality.

## Applicability

C02 preparation only, g0 d535d987b4. No push, CI, publication, ledger, local Rust/Kani/CBMC or nested delegation.

## Invariants
- Only merge pair selected for C02, both unwind17; source candidate 597e54c5cb503955f9483edc6acc9d4752d57713 on P-prime.
- Algorithms, checks and strict inventory/coverage/failure-location matcher unchanged. All nonmatching failures remain UNKNOWN.
- Bare exported target equals exact pinned source attribute spelling; fully qualified request target/import, source file/line/unwind checked separately. No independent MIR symbol resolution claimed.
- Existing caps and envelopes preserved; one group2100s (900 compile +2x600 rows), same112m step/150m job ceiling.
- C01 raw verdicts are observations. C02 proof NOT_RUN; no proof credit; ptr/mod.rs2282 frame location not silently admitted.

## Required controls
- 36 Python synthetic tests including source import/attribute/file/line/unwind mismatch, exact path token boundaries and existing service error/timeout/partial/missing/null/wrong type/NOT_RUN.

## Declared dependencies
- `ch8-c-control/runner.py` → `dependencies/0000.bin` (mode 100644, SHA256 55d216f35051bffb34116d3c39298ba50a1dbd5449acc2af9c549b5296a79591)
- `ch8-c-control/check_package.py` → `dependencies/0001.bin` (mode 100644, SHA256 b68ad40d1915ee0b51776d839c0f7548506835b1a733839b6300ead9283c6a84)
- `ch8-c-control/test_runner.py` → `dependencies/0002.bin` (mode 100644, SHA256 e6120f8ff2c16765eac2ef5dacae6d34c55417e1587fb2131bf73d9d672e1651)
- `ch8-c-control/test_package.py` → `dependencies/0003.bin` (mode 100644, SHA256 d03fc6121392f687e00a60d29f4b1eddf5933fdc23ed5e5884fdf68e3b55568c)
- `ch8-c-control/CI-REQUEST.json` → `dependencies/0004.bin` (mode 100644, SHA256 defc5fc6d75a62623fda86b1a37f430a08ed0b4eb90ac30f7b94da65ca7b532c)
- `.github/workflows/ch8-c.yml` → `dependencies/0005.bin` (mode 100644, SHA256 8f3eb8994d9746014136541dd968c3c7420d83f6cb3b72bf3cd76ff474cd1662)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- C02 may remain UNKNOWN under unchanged strict gates; no promise of proof credit.
- Source labels to generated cover IDs and callback writes to ptr/mod.rs frame location remain independent binding limitations.
- Review source dependency directly via git diff d073585946..597e54c5cb in /root/verify-rust-std-ch8-c-ctl-w14-pprime (only two unwind attributes).

Do not execute source or evidence from this packet. Do not claim new proof credit.
