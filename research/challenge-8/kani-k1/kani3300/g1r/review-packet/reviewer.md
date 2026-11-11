# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `45d0300e054345b4f6bdf89528195ee7c5dba8a5`
- Candidate: `3d085249c9c6c49a9c2e5747e2167d629748fb70`
- Candidate tree: `54599d0e20241d4544185dceb96e57b63972f699`
- Diff SHA256: `cbb3ef3980d73cc5a2b1318b0dccb06faf8e779edf3703289f98c0a7971ed9d1`

## Defect

G1R: MachineSize used as usize for Repeat Move and intrinsic Forget masks; audit all G1 production API changes for compilation compatibility.

## Applicability

Independent static review of exact repair delta plus complete production diff 657c2b245..candidate and COMPILE-SWEEP.md. No compiler/build/Cloud execution. Exact rustc_public sources available at /tmp/kani3300-g1r-api (API-SOURCES.json).

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
- MIR Move differs from Copy: copy/retain destination then clear source-only bytes; selected argument Move clears on matching callee entry; constructor/field Move source checks precede source clearing and destination mask installation; Repeat clears source once after all slot copies.
- Direct intrinsic Forget Move clears tracked storage. G2 by-value formals/return locals/call arguments reject before no-op/zero-sized shortcuts; MU flat arrays retain validated storage path.

## Required controls
- Tests/selectors/goldens must remain byte-identical to 45d0300e05; no semantic change.
- Check every new/changed API use in five production files against f046 source and nightly-2026-10-23 source, including types, borrows, exhaustiveness, imports and generic model args.
- No cargo/rustc/Kani/CBMC/build/Cloud, no nested delegation, no edits outside g1r/REVIEW.md.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0001.bin` (mode 100644, SHA256 474483db6d76712472f97f7a852130a0ef864294ccccf8edc7e79b5d5e1e96fa)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0002.bin` (mode 100644, SHA256 503b2c0f60762313b6f61b4308f154a90c459b3a4370aeb4ba2aa4e4a7aef6ba)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 716461812b3ff9c405bbc0bdf4c4760dd19dc9635ca5384d1ab2d67c0044fea1)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0004.bin` (mode 100644, SHA256 a6421b3d9ec9976aaae80346a89e9eeb53a7a787dea9c431cb05a19fc63b2726)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0005.bin` (mode 100644, SHA256 31eab7bff7382d187879547501690eeab5cfada36a1b72e1f182d9008968357b)
- `library/kani_core/src/mem_init.rs` → `dependencies/0006.bin` (mode 100644, SHA256 7bfb55904a10d92186c96913f3e279304187c3014255074934e6799600b6abab)
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
- Inherited P1: non-Copy MU<T> transmute Move-source raw-alias invalidation in both directions is outside this direct-U change; conversion whitelist remains unchanged. No general P1 soundness claim.
- New 23 selectors (154 harnesses) plus 17 renamed/existing regressions require two future 20-selector requests; neither is executed.

Do not execute source or evidence from this packet. Do not claim new proof credit.
