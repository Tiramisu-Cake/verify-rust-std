# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `657c2b24516b967f67ce71994299d0ef328aede9`
- Candidate: `0780eb57cedf07cf96ebba25b7a14701d647bf3e`
- Candidate tree: `a4c85b12642d114d7d1c69b724265119e674e5f0`
- Diff SHA256: `fa8d8d0610fd6253906a3d2d19a5e389ebedbbfcb4f6a7be877f351be493af63`

## Defect

KANI3300 G1: supported direct union raw pointees; typed and untyped transfer separation with conservative padding; G2 remains rejected.

## Applicability

One static Runtime Codex stage. No builds/local proof tools/publication to Kani. Review G1 diff plus complete P1 production dependencies.

## Invariants
- Single-byte nondeterministic shadow witness must detect any initializedness violation; data/padding masks preserved; copies must invalidate overwritten destination and preserve source witness.
- Flat bool/usize buffer is inside marked MEM_INIT_STATE. Non-deterministic argument selection, deterministic return index zero, nested calls and consuming active state must preserve witnesses.
- copy_by_id must not inspect dead return pointers or fabricate object/provenance ownership. Snapshot IDs while source live.
- DFCC may exempt verifier-private MEM_INIT_STATE only; actual writes outside modifies must remain checked. No assumptions or user-check weakening.
- Full rustc storage extent versus typed preserve-mask: false source stays false; untyped copies preserve padding; typed copies/load/constant clear uncovered padding and tail.
- Whole-create resets full union, projected stores touch exact field/subfield extent, ZST field does not bless payload; address formation never initializes union.
- Matching argument/return/destination protocol, captured addresses before overwrite, no return dead pointer dereference.
- No layout shortcut bypasses nested union/G2, fn-pointer, niche/different-padding enum; all-ZST handled.
- Thin/fat union pointer field aliases reach delayed typed reads; pointer bytes do not imply initialized pointee.
- Unmodeled volatile/typed_swap/select_unpredictable/bodyless/foreign and MU-specific transmute fail closed.

## Required controls
- Review all new G1 sources/goldens and exact manifest; bind each negative harness to its own reading/property/type/outcome. Native outcomes NOT_RUN.
- Existing renamed P1 controls and frame golden must remain identical to base657c.
- No assumptions/check removal/golden weakening, no successful G2 workaround via [U;N].
- No cargo/rustc/Kani/CBMC/build/Cloud; static review only.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0001.bin` (mode 100644, SHA256 98cc8f96504b5cee192eb777e1b53075965f0ff348efbc98e9b008da3f07cd3e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0002.bin` (mode 100644, SHA256 503b2c0f60762313b6f61b4308f154a90c459b3a4370aeb4ba2aa4e4a7aef6ba)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 cdbb06031a9794993e2efcfc9a119532ff76475ffe063e776b7bfb71486d97a1)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0004.bin` (mode 100644, SHA256 a6421b3d9ec9976aaae80346a89e9eeb53a7a787dea9c431cb05a19fc63b2726)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0005.bin` (mode 100644, SHA256 5441ca6dfe44a3f50e309a84739888208fdbace3ea2e4a40bb247ad5bdc2f0d8)
- `library/kani_core/src/mem_init.rs` → `dependencies/0006.bin` (mode 100644, SHA256 5eb267c31b1119a8b8664ad5d1a456d172fd2d710785cec65220293781ecfe0d)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs` → `dependencies/0007.bin` (mode 100644, SHA256 df0b9b50b8d035aa9b447ec0af648b7466cdc74a30ed34c85a08dc9cffec5789)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0008.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/kani_functions.rs` → `dependencies/0009.bin` (mode 100644, SHA256 4fc4ef480440d05432e1f5b2245be83bd7c70b3cd547c57442c901457feb3ab4)
- `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` → `dependencies/0010.bin` (mode 100644, SHA256 9f78de44ceffa0436de11ff3a4bf789c5d9909fe8425c7de543f84cd6c37fd91)
- `kani-compiler/src/kani_middle/points_to/points_to_graph.rs` → `dependencies/0011.bin` (mode 100644, SHA256 775b43c73d1350994de789dd30847e6c0339ee6ddc4ec91d9261cb2346c027d2)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs` → `dependencies/0012.bin` (mode 100644, SHA256 354079ebb24304c7f8dc6516ba2e50dad70f0e30466f9660d17ecece01bc7277)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0013.bin` (mode 100644, SHA256 0f32763a6981ae6269d4b938302ac106ff6ebaa19df9fa413765a982f1390277)
- `kani-compiler/src/kani_middle/transform/kani_intrinsics.rs` → `dependencies/0014.bin` (mode 100644, SHA256 62242895cd5608f1631b68ed1a4bfffc0b9dfc593809778a029de8ec4c5fb840)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No native or compiler results; full regression/core replay later require separate GO.
- G2 by-value union containers/wrappers remain Unsupported, including unaligned U transfers via Unaligned<U>.
- OR-of-arm data mask is explicit rustc-layout inference; no backend observation used as preservation guarantee.
- Existing P1 PFC limitation remains open; no independent B1/B2 credit.

Do not execute source or evidence from this packet. Do not claim new proof credit.
