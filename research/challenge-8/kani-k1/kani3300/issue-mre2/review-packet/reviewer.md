# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `47616f4105697ae3b6bc9a2203b53ccdf69168df`
- Candidate tree: `4700ee944e19804dd4d7374a6635754044f9c1a3`
- Diff SHA256: `2fb1b52d6f888da1e01f9525da2e22455f61a66d7ef95e39e35ffb34e2b10758`

## Defect

MRE v1 did not activate unstable stubbing and used union-backed storage unsupported by clean upstream uninit instrumentation. Prepare alloc-based slice havoc MRE v2 only.

## Applicability

TASK-CH8-ISSUE-MRE2-W14.md, one preparation stage. No push/CI/publication/ledger or local compiler/verifier. Clean upstream 0aac; same kani-host workflow/runner template as /root/kani-ch8-issue-mre-w14. Review exact committed candidate, including source, oracles and runner changes; no runtime evidence is available.

## Invariants
- Sole parent clean upstream0aac; changes only .github/workflows and ch8-issue-mre2-control. Stock workflows removed. Tiramisu-Cake <igkharin@gmail.com>, [skip ci]. Trigger uninit-ci/ch8-issue-mre2-* only; attempt1; no dispatch authority.
- Four no-union alloc-based files, seven invocations: original/initialized/thin each body and stub harness, true uninitialized byte read on same alloc. Two-byte allocation, raw writes, dealloc; initialized variant differs only in pre-call writes, thin variant only modifies. No valid-value invocations; no issue edits.
- Exactly -Z function-contracts -Z uninit-checks -Z stubbing plus export transport. All other Kani checks/options default. No local cargo/rustc/Kani/CBMC.
- Predeclared five SUCCESS, two UNINIT_FAILURE; slice oracle exact uninitialized *mut [u8] safety_check in write_any_slice. Negative control exact *const u8 safety_check. Preserve IDs/class/descriptions/locations and exit/exception/argv/snapshots. Unexpected failures and incomplete/stage/source identity mismatches never reproduction credit.
- No proof credit: concrete diagnostic harnesses are not a general unsafe function contract theorem. Alloc failure returns normally. write_any_slice property ID matching is conservative; unknown mangling stays UNKNOWN.
- Unchanged external build720s/row30s/phase330s/job30min caps and fallback/upload; no completion guarantee. RFC0015 validation, inventory and default checks remain enabled.

## Required controls
- Synthetic success/error/timeout/partial/missing/null/wrong-type/NOT_RUN and source/selection/metadata mismatch; new stubbing flags/branch family/allocation-only sources/write_any_slice function and safety class checks. Offline Python synthetic tests only.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)
- `scripts/validate_json_export.py` → `dependencies/0001.bin` (mode 100755, SHA256 af2a207bafbe4fd66254d40a0c022bfa4b51a76a426aedfc9f27ed14388e8b7d)
- `tests/json-handler/schema-validation/kani_json_schema.json` → `dependencies/0002.bin` (mode 100644, SHA256 e687c3af91544431c84071e1b5105682ae4f93c0dc191d03e8a545e375807670)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0003.bin` (mode 100644, SHA256 487138ede144c9cea764b1da8562a90525cfdcab7ba110e044d46a3b75ce502e)
- `library/kani_core/src/lib.rs` → `dependencies/0004.bin` (mode 100644, SHA256 fd4936db12f998df2419b9e6240f9171643f8287654840596ea2db40cfd76bc0)
- `library/kani_macros/src/sysroot/contracts/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 7ec87e829711d05928c3026249e6c79bd20e5c7e9499fe401b53a3647cd76979)
- `tests/kani/Uninit/alloc-to-slice.rs` → `dependencies/0006.bin` (mode 100644, SHA256 0cbf020b4271e7ebf330048b1ccf3612bd7161d88b88ac938b718abaa60cce3b)
- `tests/kani/FunctionContracts/modify_slice_elem.rs` → `dependencies/0007.bin` (mode 100644, SHA256 4dfe1b3636e066d00fda603184e0e1514d74cdfa8281f3266e44a75214001ad8)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- All runtime results ALL_NOT_RUN, expected outcomes are predictions. Unknown generated ID spelling fails closed. No B1/B2 credit.

Do not execute source or evidence from this packet. Do not claim new proof credit.
