# C2-S2 — source review and validation

Exact candidate `f96ad419bcae4e920708ff4bffe2b28d310f422e`, tree `bb02e1177745835e17878db00e7f9b653f43c5df`. Independent Luna HIGH static review: no correctness findings; see independent-review.md. No compilation or proof result is implied.

Production delta is bounded to `immutable_allocations.rs`: exact compatibility method, mutable map lookup, qualification-only OR branch and explanatory comments. Full Allocation equality preserves Option bytes, extent, align, mutability and relocations. Incompatible admitted inputs return a cloned prior value before any mutation. Neither-admitted conflict behavior is unchanged. Origins/static_source, admission predicates, target/binding/seal diagnostics and reset seed construction are byte-identical apart from one comment.

Rust operand/borrow/type audit:

- `get_mut(&symbol)` yields `&mut Descriptor`. `compatible(&Descriptor)` temporarily reborrows it immutably; field equality borrows Allocation, Vec<bool> and layout, with no moved field or alias insertion. The borrow ends before `previous.frozen |= descriptor.frozen`.
- `bool |= bool` changes only frozen. Err clones Descriptor through the mutable reference and leaves the BTreeMap entry intact. The insert occurs only when get_mut returned None; no second overlapping mutable borrow.
- Existing InternedString is Copy in existing registration/indexing usage. Allocation mutability/alignment and Vec<Option<u8>> are existing field types; no new Rust API, lifetime or import. Test Result types remain `Result<(), Descriptor>`.
- `[bool; 2]` is Copy, so loop iteration and later into_iter use in the order matrix do not consume an unavailable value. Incoming descriptors are owned/cloned deliberately. Synthetic fields mutate only separate descriptor clones.
- Fixture `&5` infers `&u8` from bindings/static initializer; T is an immutable Sync array of shared references. T[0] copies one shared reference. Both byte reads are u8 and legal. `read_volatile` accepts the existing `&u8` through ordinary raw-pointer coercion, reads one valid byte and adds no cast/assumption. No by-value nested union, new indirect call or unsupported origin construction.

Duplicate-symbol/ordering audit: BTreeMap holds one descriptor per symbol. Exact aliases merge only qualification and retain one original mask; false→true and true→false agree. Finalize still closes origins before iterating bindings and seeds only after all registrations; static-first and anonymous order cannot erase evidence for an exact object. Incompatible inputs are outside this order-independence claim. Existing binding/materialization mismatches and true descriptor conflicts retain diagnostics.

Checks: `git diff --check base..candidate`; exact branch/base/tree and author/committer; clean source; all nine changed paths within allowed scope; old fixtures/configuration/runtime unchanged; baseline-controls.patch temporary-index apply and candidate test identity checks. Final review packet identity check passed with proof_credit=NONE. See INPUTS.json and STATIC-CHECKS.json for exact identities/results. All Rust tools, fmt/build/clippy/unit/expected/CI execution are NOT_RUN.

Research is uncommitted in g0 only. The assigned destination did not exist at entry; a fresh isolated --no-hardlinks clone was created from clean, exact read-only S1. Neither source input nor g0 tracked files was changed. No push, CI, Cloud, pin changes, S3–S6 or SEL1 work.
