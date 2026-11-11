# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `230fa9aa656dd90503390019a6c0d153ef93520b`
- Candidate: `4770341265db9e8e5b3f4863705f3ae1e5a91703`
- Candidate tree: `ffeb23509e0294c4c722e8db2c9c14c8ca71f529`
- Diff SHA256: `3ed46f58a3460918b8bd2e130aa172b126303776c35a00af0985fcd06c2467a0`

## Defect

Independently review B2 diagnostic probe scenarios against TASK-KANI3300-B2.md; establish static correctness, not measured MIR or Miri outcomes.

## Applicability

Only b2 probe crate and its expectations/historical case restoration. Kani is unchanged. No compilation/execution/build/dispatch/Cloud/network writes.

## Invariants
- Each source read derives from a raw pointer taken before transfer and observes the same live local/allocation/field; no unrelated UB.
- Use initialized padding-free bytes except the explicit uninit detector control; distinguish Copy, assignment Move, bodyful Call, intrinsic forget, and reinit.
- Forecasts are not observed pinned outcomes, proof acceptance, or justification for Kani model changes.

## Required controls
- All 10 removed historical cases represented accurately.
- Independent binaries include Copy, assignment non-Copy, by-value inline(never) call, address-taken parameter, mem/intrinsic forget, reinit, field/union/MaybeUninit.
- Assess likely Rust compile hazards by reading only; local Rust tool execution is forbidden.

## Declared dependencies
- `research/challenge-8/kani-k1/TASK-KANI3300-B2.md` → `dependencies/0000.bin` (mode 100644, SHA256 80c02c1af267ff47f3f46a5a0e3b9711cb565ea6de9649df6e6dd830054ac75d)
- `rust-toolchain.toml` → `dependencies/0001.bin` (mode 100644, SHA256 689c159497e53389671511fa85e200533c2a892488346620ccaae0a34ad45618)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No local cargo/rustc/Kani/CBMC/Miri, compiler wrappers, builds, dispatch, Actions, Cloud, raw logs/archives, credentials, or external writes. No nested delegation.
- Exact actual MIR/Miri outcomes are reserved for coordinator CI in another stage.

Do not execute source or evidence from this packet. Do not claim new proof credit.
