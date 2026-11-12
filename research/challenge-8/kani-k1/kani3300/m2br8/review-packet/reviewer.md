# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `8e01eb2aff5183c53403e1d1e73e573ce28d3095`
- Candidate: `2bd63183d88bec2efeeccb88b450b50939d120c3`
- Candidate tree: `f827cc9a6235eb5cc28ec03f2f719085fcbb1dcd`
- Diff SHA256: `27750c941d4fac0e4b4a4824b6e84960f88f2798ec6a8cb6bf30d9684db79679`

## Defect

Coordinator R7 B0/B1 P1/P2 resource cutoff; R8 changes only current A3 snapshot carrier, not protocol or core witness.

## Applicability

KANI3300 M2-B/R8 only; bounded source representation/metadata/lifetime/false/frame-cell review. No compilation/proof/cost claim.

## Invariants
- Preserve complete A3 protocol/ABI, demonic choice, mandatory return0, selected false and no-witness distinction, capture-before-Move, partial reset and M1 seeds.
- Replace numeric relative_offset by saved_base/saved_byte:*const u8. Selected has_witness formation only. Store exact non-vacuous round-trip/same-object/range assertions, Load metadata only under original source-follow branch with same-object/range assertions. Never assume/fallback/drop on codec loss.
- Audit pinned CBMC6.11 bit slices/zero-extension, offset width versus usize, wrapping_add path, valid representable extent lemma and stored globals through DEAD/pop_frame. Report real gaps; no proof claim for unbound actual backend.
- DFCC field list contains 13 buffer cell lvalues plus unchanged main; correct unsigned8 pointer IR type, no saved pointee/deref/blanket range or casts to rvalue. Exact markers/emitted objects preserved.
- Only two source sites; all old tests/callers/skip/instrumentation/finalizer unchanged. No new helper/assume/ABI/layout scope. Check source Rust signatures/types/macro alias/null inference/unsafe blocks.

## Required controls
- Independently inspect actual committed diff/dependency identities, required assertions and source relation. Read task and source dependencies, not an author PASS verdict.
- Inspect matching protocol prefix/suffix and false value path; confirm inactive/no-witness/zero no decoding/add, captured false does decode.
- No local cargo/rustc/Kani/CBMC/Miri/build/network CI. No writes to source; compact findings with paths/lines, required fixes, proof gaps. No nested delegation.

## Declared dependencies
- `cprover_bindings/src/goto_program/symbol.rs` → `dependencies/0000.bin` (mode 100644, SHA256 882b95e3fc299c871f7db2665ef11e1fee22d40e1c273b92bbeb06418331c5e4)
- `cprover_bindings/src/goto_program/symbol_table.rs` → `dependencies/0001.bin` (mode 100644, SHA256 26e5e72c0014aafc640897f65e0b380186da4ca3aa86bdd49717cf74260aac77)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs` → `dependencies/0002.bin` (mode 100644, SHA256 20042aa1631620ed3fd546bdd1d86ee449563d805565be19c9bc2a7ceb999787)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/static_var.rs` → `dependencies/0003.bin` (mode 100644, SHA256 e96373714350b1cced3a0c3d9732ab8d9fbbad04273121f41af9bd96351f93fc)
- `kani-compiler/src/kani_middle/attributes.rs` → `dependencies/0004.bin` (mode 100644, SHA256 0b7cfe3b74e1958770b94a763fc89bc5b8156a1d120a69e8bdac67ada630078e)
- `kani-compiler/src/kani_middle/kani_functions.rs` → `dependencies/0005.bin` (mode 100644, SHA256 c991f53c452f162f153880e178f728394e679d80b3175c226baec34f57b31773)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0006.bin` (mode 100644, SHA256 d116bef5bceb32cf65f344600ddeb71dca7c85eb1aaf7f0d29382b296f638ed2)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0007.bin` (mode 100644, SHA256 3e63dff930116bb80cbcbb8cac122a8941b27a0e6b1ddc18ff146a4cc45b170f)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0008.bin` (mode 100644, SHA256 d85c1adf759d9913e05c2a4effbb47cf66b3f35a11d2f198c12a9497d7d96dba)
- `library/kani_core/src/arbitrary.rs` → `dependencies/0009.bin` (mode 100644, SHA256 cdd7aa7e5c4cf7f1e977b965b9551cb2a5fdd2fe340e83051cf8df6a6ad53070)
- `library/kani_core/src/lib.rs` → `dependencies/0010.bin` (mode 100644, SHA256 bb77d147b03f64586bb38a31edafaddc0c99e3cc3fb65a5c5c541b4fc0198649)
- `library/kani_core/src/mem.rs` → `dependencies/0011.bin` (mode 100644, SHA256 598428730a32f2c4034091688b50dde5a44deb69e2e3c61e08a0d394a5e42844)
- `library/kani_core/src/mem_init.rs` → `dependencies/0012.bin` (mode 100644, SHA256 dd391c4b160c24d34ca2b314cd519b350553dadbc8e79e7868c9dc47bbdbfb56)
- `rust-toolchain.toml` → `dependencies/0013.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)
- `rustfmt.toml` → `dependencies/0014.bin` (mode 100644, SHA256 d1886a654a790b5f5779d12c770b32c5328e4e4eaa415fc3a024c6ba9df687b1)
- `kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs` → `dependencies/0015.bin` (mode 100644, SHA256 c01ced42f97efdbc8d6a34c75f229753af59f380549518af971ecea672cd72b2)
- `kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs` → `dependencies/0016.bin` (mode 100644, SHA256 b90b5b19d9fdaedae2657e8fc42f52912063f47fb734c157e2d72413054c3087)
- `kani-compiler/src/codegen_cprover_gotoc/context/goto_ctx.rs` → `dependencies/0017.bin` (mode 100644, SHA256 cf0433855bf460b679d6202effbece3dcdd4d2f920cff274b53e359cfeb21957)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs` → `dependencies/0018.bin` (mode 100644, SHA256 c367bc4da9cc250b839f2860508788973b87bf1c6246f012e5988c83668fa02d)
- `kani-compiler/src/args.rs` → `dependencies/0019.bin` (mode 100644, SHA256 cb1f451503f39856f5a2f7bf4eea1c9ee852bcb45c6012be08983ce6440495d3)
- `cprover_bindings/src/goto_program/expr.rs` → `dependencies/0020.bin` (mode 100644, SHA256 acf2baf0f67dc32868b55b4fa92757628b5c219951a631390b91b0ecc0701780)
- `cprover_bindings/src/goto_program/typ.rs` → `dependencies/0021.bin` (mode 100644, SHA256 ade325a1e884f3d6a648a64fe668c8f5e821c0ba42fcff419d4b2f9532b33871)
- `kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs` → `dependencies/0022.bin` (mode 100644, SHA256 ad73c82580f8f9ba3528ce9b6b371c6a4f717443e31a86b1fad6bad0a2c80d64)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs` → `dependencies/0023.bin` (mode 100644, SHA256 bc0f72b9efb456a1d39a4c2ce19aaa62c675303ef80fc9a5323074a69ca5d6d1)
- `cprover_bindings/src/irep/to_irep.rs` → `dependencies/0024.bin` (mode 100644, SHA256 bda4f823aafe43d547476d540cf264e62293dc8693df861c65864566413d7b0c)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Actual compilation, emitted/reached Move/return/metadata/ensures, target address/extent/object, backend/version/binary/flags and guard outcomes await coordinator CI. R8-C test-only composition may follow without source change.

Do not execute source or evidence from this packet. Do not claim new proof credit.
