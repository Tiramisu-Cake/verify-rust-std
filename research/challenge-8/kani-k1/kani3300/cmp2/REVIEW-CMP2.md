# KANI3300 CMP2 − CMP1 static review

- Baseline: `6ef9fd72066443f7f113440ba32f77f310520a93`
- Candidate: `b1f0105c0390fb55081e3d186fa286d23867b585`
- Candidate tree: `45511935c1ce911ea6c85eee5f6850095cbf966e`
- Review packet inventory SHA256: `d2aee8734223d455bc987fa00338f3522e69adefd6353f9dee9ba39a04e8f44e`
- Spec SHA256: `beee1d51eaacd847d8a771f6cd07341c91ff4f4340877be3a189f743ea452fb8`
- Diff SHA256: `50dd4a6ef02274d642f0d326a4f9c0b41b39d131134cbf5b389e2ef3ec050b03`

## Verdict

**Static review: GO for coordinator PRE-BUILD consideration; native acceptance remains NOT_RUN and proof credit is NONE.** I found no static soundness defect in the production delta. This review covers only the committed packet and declared dependency snapshots; the failing-instance MIR/points-to binding was not available.

## Findings

- **No blocking finding.** In `instrumentation_visitor.rs:54–80`, the entry seed is limited to by-value argument locals that resolve to an existing analysis target, excludes unions and all recursively storage-bearing types, and requires a sized `PointeeInfo` layout. `SetStorage` uses that typed data-byte mask: ordinary R bytes become initialized while padding remains false; storage-containing aggregates are not blanket-blessed. The operand is the argument local itself, so a pointer/reference parameter seeds its value representation, not its pointee. The caller’s operand/place read remains visited and checked before the callee entry seed can affect the callee’s fresh parameter storage. This ordering is consistent with the three argument negatives, including poisoned caller bytes, callee poisoning after entry, and an uninitialized pointee.
- **No blocking finding.** `instrumentation_visitor.rs:45–53, 132–148` starts an empty block at its terminator and retains newly added entry operations while switching to that terminator. `MutableBody::insert_stmt` appends a before-terminator operation to the block, preserving those operations and pre-terminator ordering. The baseline terminator transition reset its operation vectors, so this change specifically preserves the new entry seed on an empty first block.
- **No blocking finding.** The padding fixture now performs a direct byte dereference at `main.rs:78,92`; the unchanged golden requires `u8` failures for both padding reads. That keeps the intended byte-level diagnostic instead of depending on `ptr::read`’s pointer-argument checking. The fixture has five harnesses total: these two direct padding reads and three other expected failures. No CMP1 test path is removed in the packet.

## Coverage note

The new fixtures cover aggregate move, `ManuallyDrop`, unsize plus field projection, cloned ordinary arguments, thin pointer arguments, and all three argument negatives. They do **not explicitly demonstrate the empty-entry-block case** exercised by the production cursor fix. Add a focused case if the coordinator needs direct regression coverage for that branch; static inspection found the insertion logic valid. The pointer positive/negative cover direct pointer parameters, not a pointer nested in an ordinary by-value aggregate, so nested-field alias behavior is assessed from the field-insensitive points-to implementation rather than a dedicated fixture.

## Validation limits

No cargo/rustc/Kani/CBMC or Cloud build was run. The report establishes a static review only; it does not establish the candidate’s runtime behavior, native selector execution, or proof acceptance.
