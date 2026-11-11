# Kani #3300 Part 1 — static invariant review

## Identity and scope

- Baseline: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`.
- Candidate: `c39cc1121cdb287d9d77c38b87cff6c84c2c8046` (tree `582c123d68fb1f585ffb3e40b0d5c96c1d7d4ca3`).
- Complete baseline-to-candidate diff SHA256: `b30758e575bb0bfabab186d615e8b28871543efb0703028aa721a8622ef28c40`.
- Spec SHA256: `6274eba94f8208d3e466c30e4e115d364aaafecc9d395913cfd518727be3b02b`; inventory/packet SHA256: `3797b5f5a590bdc7cf23c1f43fa2f79fab4b88feea917a4f483d79d9efdaf49b`.
- `/usr/local/bin/smallsort-session review check` returned `PACKET_VALID_NOT_REVIEWED`, candidate and spec hashes as expected, 15 files, proof credit `NONE`. All ten dependency snapshots matched metadata SHA256s. This validates packet identity only.
- The persistent review packet at `research/challenge-8/kani-k1/kani3300/p1/review-packet` independently returned the same packet digest and validation state.
- Production scope is the seven changed files under `kani-compiler/.../check_uninit` and `library/kani_core/src/mem_init.rs`. The three declared contract/body/function dependencies are unchanged from the baseline. The frame exemption is the existing marked `MEM_INIT_STATE` static in `contract.rs:142-170`; the candidate puts the argument-buffer fields inside that same verifier-private object.

Declared dependency snapshots (all SHA256s verified against packet metadata):

| File | SHA256 |
| --- | --- |
| `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` | `dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60` |
| `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` | `47b1063398159a376fd4edcecee4d28ac24f54b2e86a930d836b354023cd8ed0` |
| `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` | `503b2c0f60762313b6f61b4308f154a90c459b3a4370aeb4ba2aa4e4a7aef6ba` |
| `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` | `6a4d519b9261a2a3e479b6b143a8f6702273ddcaeee734fa513187fc4df92723` |
| `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` | `db408ef3264acfad8245ac52d7f3aa2e658578edce611552ef29d19b8729f28e` |
| `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` | `ce16fba0d46cae786b1a85672a67e2460ff1df4c5c91d76d2c4883eed0153253` |
| `library/kani_core/src/mem_init.rs` | `d565a600e34ef6199f4c6e0a799a5eb9a224ec0ed9a563ef47da2cbbe908cc06` |
| `kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs` | `df0b9b50b8d035aa9b447ec0af648b7466cdc74a30ed34c85a08dc9cffec5789` |
| `kani-compiler/src/kani_middle/transform/body.rs` | `930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5` |
| `kani-compiler/src/kani_middle/kani_functions.rs` | `4fc4ef480440d05432e1f5b2245be83bd7c70b3cd547c57442c901457feb3ab4` |

## Findings

No actionable soundness defect found in the reviewed Part 1 scope.

The reviewed paths preserve the requested invariants:

- `uninit_visitor.rs:150-289, 412-440, 782-865` updates MaybeUninit storage for supported constants, union construction, flat array/repeat assignment and typed transmute. Typed transmute installs the source data-byte mask (including false padding); conversion back to a typed value checks the required data bytes. Ordinary source reads remain visited. Unsupported forms inject an unsupported check.
- `ty_layout.rs:109-144` recognizes only a direct MaybeUninit slot or a flat array/slice of slots. `mod.rs:218-242, 435-483` uses all-storage layouts for bytewise state movement and substitutes explicit masks for typed sets, preventing generic delayed-UB sets from erasing slot state.
- `mem_init.rs:126-153, 400-454` snapshots source object ID and offset while the pointer is live; caller-side load uses those IDs and a live destination pointer, so it does not dereference a dead return-stack pointer. Copy remapping retains the tracked source witness on the reset branch and invalidates a tracked overwritten destination on the other branch. The flat argument state is consumed on a match; non-return argument selection is nondeterministic, return index zero is forced, and MIR argument locals use the matching one-based index (`uninit_visitor.rs:55-75, 480-520, 644-705`). Bodyless shadow transfers are rejected instead of leaving stale buffer state (`uninit_visitor.rs:490-505`).
- DFCC's exemption is scoped to the marked `MEM_INIT_STATE` global, which now also contains only the private transfer fields. The added frame-negative source still writes the user-owned `outside` reference at `tests/expected/uninit/maybe-uninit-buffer-u3-frame-negative/main.rs:22`; its golden points to that line and reports `Check that *var_7 is assignable`. I found no assumption or user-check weakening in the candidate diff.

## Test-source and golden review

Inspected the source and expected output for all 15 entries in `TEST-MANIFEST.json`, including the positive/negative pairs for padded typed transfers, argument/return transfer, overwritten copies, overlapping copies, repeated local values, reset/aliasing and reset after a ZST. The negative cases target the uninitialized read or overwritten bytes; positive cases retain initialized reads and padding exclusions. The PFC golden uses `Failed Checks`, and the frame golden remains tied to the actual user write at line 22. No pre-existing tests were modified or weakened by this diff.

The manifest records finite native PASS observations for prior source revisions. Those observations are not execution evidence for the packaged candidate: the manifest says the current packaged form is `NOT_RUN`. In particular, no conclusion is drawn from the PFC OOM or the excluded/unsupported cases.

## Limitations and verdict

Static source and packet review only; no build, test, Kani, CBMC or Cloud run was performed. This review does not establish formal verification credit, general support for excluded nested/compound cases, or current-candidate execution. The known PFC OOM is not evidence of soundness or unsoundness.

**Verdict: no blocking invariant violation identified for upstream Part 1, within the stated supported domain.**
