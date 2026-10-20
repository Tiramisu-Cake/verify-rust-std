# R11 same-Build checked-helper prerequisite

The current R11 source certificate can declare the exact ghost block for
`a1_cleanup_option_ref`, and the active R11 profile pins that block's SHA-256.
When both declarations are present, caller-focused collection must prove the
lemma body in the same Build before it asks VeriFast to focus a caller that
uses the lemma. A focused caller check skips the helper body, so its use cannot
consume an unproved summary. The helper proof runs afresh for each caller; no
cross-case, cross-Build, profile, or support-cache reuse carries proof state.

The gate validates the certificate's inclusive source block against the
generated `verified/lib.rs` bytes and the profile pin, requires one exact
`lem a1_cleanup_option_ref` declaration within that block, then runs the
pinned VeriFast tool with focus on the certified lemma body. The pinned ghost
parser records the helper `Func` header location at its identifier token and
the body tuple's closing-brace location separately. The gate checks the exact
identifier coordinates against source bytes, checks the close-brace line,
and derives the focused interval from those two locations. It must select
exactly one same-name lemma interval matching the certified body. A nonzero
helper result, missing or malformed receipt, missing AST,
wrong AST kind/name/span, ambiguous declaration, exhausted deadline, or source
pair/tool identity change blocks caller verification and preserves the
original prerequisite failure as an explicit partial/not-run result.

The helper invocation uses the pinned contract's dedicated `checked-helper`
stage. It keeps the contract macro and phase enabled so normal compiler
prototype handling remains active, while removing the caller publication stage
and forced-redirect control only from a private environment copy. That copy
adds the certified helper name, full-source SHA-256, ghost-block SHA-256, and
inclusive source/body line bounds. The actual caller environment remains
unchanged for its later invocation. The raw prerequisite records both full
environment hashes and the A1 control projection, and core revalidation checks
that the helper projection is exactly the checked-helper form of the caller
projection. This stage does not publish the caller summary or grant proof
credit.

The raw same-Build record binds Build ID, profile/helper pins, verified and
original source pair hashes, focus line, verifier stage and AST artifact.
That is a prerequisite record only: it does not supply independent proof
credit, establish a Rust callsite/MIR binding, or classify the caller theorem.
Existing profiles and source certificates with neither helper pin nor helper
metadata retain their prior behavior; if only one side declares the helper,
collection fails closed.
