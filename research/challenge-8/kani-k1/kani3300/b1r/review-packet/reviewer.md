# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `835cb4a09c4e94ac6b531d20e68f9deee7262ce1`
- Candidate: `29bde289d60d9f6f36c16310f6bce697338f7641`
- Candidate tree: `ed69f7da86e81bef38111a1dfa34436fe52dfb3c`
- Diff SHA256: `4f32dc2670a51ed4b5346655dcb6234eacd1a39bac2ce5dc784317a2e82f3e75`

## Defect

Review the B1R repair independently against TASK-KANI3300-B1R.md at research f8e3ab9534; task B1 remains applicable.

## Applicability

Only B1R shim handling and test repair; no broader model or verification changes.

## Invariants
- Keep collected operations and the single Call traversal from B1.
- Classify InstanceKind explicitly, preserving supported bodyful callees and rejecting unresolved/bodyless effects.
- Preserve existing vec-read-init and quantifier-capture regressions and their goldens.
- Audit each of six custom-MIR tests for reaching the named check, edition/features, and warning hazards; distinguish static expectations from measured execution.

## Required controls
- Existing vec-read-init and quantifier-capture/uninit regressions.
- Six pending-ops/entry-partial/entry-initialized plain/seeded tests and their named properties.
- New B1 FnPtrShim pair; audit changed expectations for inner indirect call.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 acd93cd4351eaff1ba8365ccc2298b560854aa9c95311204203a3c3485afa971)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0001.bin` (mode 100644, SHA256 326ddfe7b112e88f61f7af8606d433fc8be29fe959565ad3b4071a875f8230a9)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0002.bin` (mode 100644, SHA256 92b632cabff031938ffc2abf9fef276193ac68184edf6f65c0d8722ee87ae00c)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 6facb556d7b898a15e9d72e073d4da2ea5658deefbe4ef00a8963ab281de5d26)
- `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` → `dependencies/0004.bin` (mode 100644, SHA256 e5e2b42c6589bd3f078845f50720098d47571c166cb580f4945eab6f5de4338f)
- `kani-compiler/src/kani_middle/reachability.rs` → `dependencies/0005.bin` (mode 100644, SHA256 5c285768493d14fd2d6ab6391e41688bc208f071891ea82971a6598e582016a1)
- `kani-compiler/src/kani_middle/transform/mod.rs` → `dependencies/0006.bin` (mode 100644, SHA256 c9b0f47bc79751ab906c443243750ae840311d87c78924147a6765df94971339)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0007.bin` (mode 100644, SHA256 487138ede144c9cea764b1da8562a90525cfdcab7ba110e044d46a3b75ce502e)
- `tools/compiletest/src/header.rs` → `dependencies/0008.bin` (mode 100644, SHA256 9ea266041cff8aaeee82f5270431f0c5f10e1ffa11ce4fd544ac733ab7dbc6e7)
- `tools/compiletest/src/runtest.rs` → `dependencies/0009.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)
- `tests/kani/Uninit/vec-read-init.rs` → `dependencies/0010.bin` (mode 100644, SHA256 28fff7b952483ec086c884f110f68343640b41e6125ddb3b4e081aa32313d723)
- `tests/expected/quantifier-capture/uninit.rs` → `dependencies/0011.bin` (mode 100644, SHA256 4fb8fdd74526fff6a87229105380ae8f7037f377fb9a1cc4f260c23512a5b760)
- `tests/expected/quantifier-capture/uninit.expected` → `dependencies/0012.bin` (mode 100644, SHA256 ae2d04c8343f79d2b17b334f6426479061ad46532c9b144ea2de6eda916ebd85)
- `tests/expected/uninit/delayed-ub-unsupported-call/expected` → `dependencies/0013.bin` (mode 100644, SHA256 7008546b9c6963fdc4e6c0507852732014aaf7abf7ef05423d7a9c0806d9e89c)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static review only. No local cargo/rustc/Kani/CBMC, builds/dispatch/Cloud/Actions, raw logs/archives/credentials; no network writes or Kani push.

Do not execute source or evidence from this packet. Do not claim new proof credit.
