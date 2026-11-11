# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `e3c529a0d5a501987a36c1481bb7e8a48c80dc73`
- Candidate: `55d704a56dbd5864ffb75e3d861a544c281f8ebd`
- Candidate tree: `f8c059aed34acbc2305651e361236854e51521a7`
- Diff SHA256: `f1e86aa80986620e486dd81a7de918fc9c69250eae4ac2376b93a951873e302e`

## Defect

KANI3300 A3 new fixture controls: paired calls, custom MIR in-place Move/Copy, unsupported foreign/shim shapes.

## Applicability

Test-only follow-up to semantic candidate e3c529a0d5a501987a36c1481bb7e8a48c80dc73; same A3 contract. Review fixtures plus existing semantic dependencies. Union pointer probes are being adjusted to avoid unrelated delayed-UB checks; follow-up edit will be supplied.

## Invariants
- Same predicate must gate caller StoreArgument and callee LoadArgument. Reject bodyless/shim/non-Item shadow transfers early with Unsupported; no initialized fallback if no current protocol. Check instance/signature identity, count, ordered indices, selected-payload size, completion, obligatory return0, no state leaked across nested/repeated same-size calls.
- For shadow storage union/MaybeUninit Call Move, snapshot witness while live before deinit, then full-extent deinit source, including padding. Callee must preserve pre-move false bytes, not reread reset shadow. Copy/assignment/field assignment/forget/temp-original storage must retain intended semantics. Ordinary union returns should pair too.
- Audit insertion order and interaction with delayed-UB pass, pointer checks and marked verifier-private state / DFCC. Check guard reachability and existing checks preserved; identify scope limitations rather than broadening to B1.
- Audit Rust API/types/borrowing/exhaustive matches, macro feature compatibility, unused imports/code, clippy/-D warnings statically using pinned /tmp/kani3300-g1r-api. No compilation or local tools beyond Python and permitted rustfmt. Check compiler-context Ty::to_index as protocol identity under actual transform lifecycle.

## Required controls
- No nested delegation. No builds/Cloud/dispatch/cargo/rustc/Kani/CBMC/Miri/Actions/PR/issues/comments/Kani push/raw logs/archives/credentials. Do not browse network.
- No implementation edits. Write only /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/a3/REVIEW.md. Report exact candidate/tree/diff/spec identities, actionable findings and static verdict/limits.
- No compilation/runtime/proof credit. Main will submit test-only controls after fixture worker finishes.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 46214010ffc67f498e6c175d700aac8b4f042c6747eca9eb1e782bba981c56f1)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0001.bin` (mode 100644, SHA256 b4b1edf5242be38a8079fdd5657356181dbc76eb5ba63889f72b56f72ccea52a)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0002.bin` (mode 100644, SHA256 ee7856515df8c49b4e1c9bd442aab631e511a1ffc81b822700ef610d2940a461)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 d391ef37e2ba51a4b867881cb7f80f638a41daaf214de9452fda005ed724f6be)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 d85c1adf759d9913e05c2a4effbb47cf66b3f35a11d2f198c12a9497d7d96dba)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0006.bin` (mode 100644, SHA256 70989e979e259cdfa5bfa0811cb53776f98a8ec1147c660ceec4e3f6d93b9186)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs` → `dependencies/0007.bin` (mode 100644, SHA256 354079ebb24304c7f8dc6516ba2e50dad70f0e30466f9660d17ecece01bc7277)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0008.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/transform/mod.rs` → `dependencies/0009.bin` (mode 100644, SHA256 c9b0f47bc79751ab906c443243750ae840311d87c78924147a6765df94971339)
- `kani-compiler/src/kani_middle/kani_functions.rs` → `dependencies/0010.bin` (mode 100644, SHA256 c991f53c452f162f153880e178f728394e679d80b3175c226baec34f57b31773)
- `library/kani_core/src/mem_init.rs` → `dependencies/0011.bin` (mode 100644, SHA256 6ecd75e2497e3b43b059c5acb83ea593c8a917b6391971ce70e38d3132a16d46)
- `rust-toolchain.toml` → `dependencies/0012.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)
- `tools/compiletest/src/runtest.rs` → `dependencies/0013.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)
- `kani-driver/src/call_single_file.rs` → `dependencies/0014.bin` (mode 100644, SHA256 3fc27b10a1db7705b514e7689e9c6e6b2f20516066664ad799b32f4adc23c996)
- `tests/expected/uninit/maybe-uninit-argument-buffer/main.rs` → `dependencies/0015.bin` (mode 100644, SHA256 09e5dd454f0cfcfeed1d9df436507c7d705270e85ee11592347113d58f9f1f55)
- `tests/expected/uninit/maybe-uninit-typed-transfer-data/main.rs` → `dependencies/0016.bin` (mode 100644, SHA256 4819312ce884c348b8964b085873dea53627c27aa30f53458229858283cf7f41)
- `tests/expected/uninit/maybe-uninit-typed-argument-padding/main.rs` → `dependencies/0017.bin` (mode 100644, SHA256 b72b3f4808b58061054d143ee568c044aea48671910e4f5ca33be41dc36ed069)
- `tests/expected/uninit/maybe-uninit-call-move/main.rs` → `dependencies/0018.bin` (mode 100644, SHA256 f449f574cde7beae230af9e43255eb1b07bf983fea135ef100c1126bcee445d2)
- `tests/expected/uninit/maybe-uninit-call-move/expected` → `dependencies/0019.bin` (mode 100644, SHA256 1d7926aeacf734436516c27ab83845a7caf5a5cc5bd3addceceb72e8dedcc132)
- `tests/expected/uninit/maybe-uninit-call-pairing/main.rs` → `dependencies/0020.bin` (mode 100644, SHA256 e4adfcd3369a6787421c1792ea659ab6d4e195ad063927003bbcd85c446fd9d3)
- `tests/expected/uninit/maybe-uninit-call-pairing/expected` → `dependencies/0021.bin` (mode 100644, SHA256 336212bb2b499b05eb202c95a67b9b8183c3e85099f316b201d055585eb7146f)
- `tests/expected/uninit/maybe-uninit-call-pairing-unsupported/main.rs` → `dependencies/0022.bin` (mode 100644, SHA256 0b7441a2d1ef041c32364334a0535a566f324e4ca59d0dddb65137060feadb5d)
- `tests/expected/uninit/maybe-uninit-call-pairing-unsupported/expected` → `dependencies/0023.bin` (mode 100644, SHA256 01cbc989516b4a6d21a432a1a1c4bce3b7df00ae50c9e9ca158d52450a4693d9)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static only. Coordinator fork CI owns compilation and measured verification. A3 shadow-storage domain uses preexisting transfers_shadow type recognition.

Do not execute source or evidence from this packet. Do not claim new proof credit.
