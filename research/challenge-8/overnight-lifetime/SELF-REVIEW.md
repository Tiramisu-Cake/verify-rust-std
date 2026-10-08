# Initial static review of the 26.10 cut draft

Historical draft `verifast-strict-lft-cut-26.10.patch` SHA-256
`392823e7a3cabc819d4b89e75417017405acf58337f02f0775b1d1a27adfa464`
is superseded. The current candidate SHA and exact production-chain base are
recorded in the addendum below. This component is **not accepted**. The
historical draft was generated against f76012fb with S6, CFG,
A1 inhabited, A1 pointer transmute, tuple2, A1 linkage, H2a, callback
`61d7525cc8ff3e6e9c736ea00178c002f071b521c78845bf68d0e4890e2be07a`,
and H2b `c9afb4bfd696efc38f2bc71e10463a34170d9d769e851a07388c01278e99b2ff`
applied in that order. No 26.09 HRTB patch was applied. The old authored
26.09 patch's four kernel hunks and six translator hunks applied with offset;
three translator hunks were adapted to the current `TrBody` signature and
module instantiation. Added a one-marker-per-body check and explicit
fail-closed errors for a missing reconstructed block head/entry. The resulting
patch changes only `vf_mir_translator.ml` and `verifast.ml`.

Static `git apply --check --reverse` passed against the edited disposable
worktree, and `git -c core.whitespace=cr-at-eol diff --check` passed. The
`verifast.ml` upstream file uses CRLF, hence the explicit whitespace mode.
No verifier, compiler, runner, extractor, or executable test was run locally.
The new H2b hash normalizes patch context whitespace only: a second disposable
f76012fb worktree applied the current ten-patch chain in order with
`git apply --check` at every step, then byte-compared both final lifetime
component files to the first staging worktree; both comparisons passed.

The translator obtains the source marker from a parsed regular ghost
statement, demands one named lifetime and no arguments, pairs it with the
sole `TypeWithTypeidDecl` of a real exporter block, relocates the synthetic
end to that marker, and keeps the original brace as a no-op. Its reconstructed
CFG check rejects an incoming edge into the shortened prefix except its
designated entry and rejects a malformed exit from the end block. It does
not inspect the actual Rust body hash or first-call operand aliases; those
remain external per-function source/MIR certificates, especially for sort4.
The extension rejects any parsed marker unless the explicit
`SORT4_STRICT_LFT_CUT=1` environment opt-in is set; no-marker bodies stay on
the stock path. This gate does not by itself certify a particular source
body. The hosted capture records exact isolated source hashes, unique
function DefPath inventory and complete paired typed MIR for review. Actual
sort4 will need its own full-body/operand/CFG certificate before enabling
the marker there.

The kernel opt-in is identified by an internal first AST statement in the
shortened block. It checks that this block declares only the paired lifetime,
prevents shadowing an outer type/value, suppresses stock silent filtering
of scoped heap chunks, rebases only outer type-parameter bound metadata to
the entry snapshot, rejects live scoped chunk types and outer variable/bound
escapes, and applies the same continuation checks on normal, return, and
outgoing-goto exits. It rejects an AST exception continuation. There is no
change to memory, permission, prelude, SMT, refinement, or target contract.

Open review questions for hosted evidence:

1. Whether `positive_direct_unwind` retains a direct Continue call in 26.10
   MIR and the resulting `ReturnStmt(unwinding())` uses the checked return
   continuation. The case and classifier remain diagnostic until its full
   graph and trace are inspected.
2. Whether the current HRTB projection/type-bound table uses the same entry
   snapshot representation and semantic rebasing as the 26.09 profile. The
   port preserves the old code, but no compiler or proof run has tested it
   on 26.10.
3. The original patch's nested/outer-variable/metadata/CFG ingress controls
   were not all present in the historical 12-case template. The new matrix
   names them as mandatory fresh controls before ACCEPTED.
4. The current callback hook uses a synthetic outgoing goto; its first
   actual sort4 extension is separate and not implied by this patch. A
   hosted AST trace must prove it exits only the ghost scope and preserves
   every real cleanup edge.

If any positive fails in frontend setup or no complete graph is captured,
that is inconclusive. If the strict chunk/bounds check fires on the actual
borrow protocol, the resource protocol must be repaired; the check must not
be removed or bypassed.

## Current 12-patch rebase and snapshot correction

The current patch was rebased statically after all 12 production patches in
`overnight/run-s6.sh` order, including H2c, G1 call CFG, and 26.10 FnMut
HRTB. Its SHA-256 is
`d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8`.
The staged 12-patch input SHA-256 values are
`6abe2aa920dfe9cc193d1331d0ee5e90310f2ac7609b03d92f3000959d5115bf`
for `vf_mir_translator.ml` and
`adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0`
for `verifast.ml`. The edited outputs are
`64a32e92e2f500abf41dcc3af796d0ca0351211fa14a6451f34d36dd1a1bcf51`
and `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
The old patch had one rejected translator hunk where HRTB state now
sits between `body_tr_defs_ctx` and the callback hook; the `strict_lft_scope_ends`
binding was placed immediately after `body_tr_defs_ctx` without replacing
either state component. All other hunks applied with reviewed offsets.

The new trust review is [SNAPSHOT-REVIEW-BEFORE.md](SNAPSHOT-REVIEW-BEFORE.md).
Entry bound and outer-variable types are recursively frozen by resolving
`EqConstraint` and rebuilding every nested current AST type constructor.
Unresolved/cyclic inferred references fail at entry. At every strict exit,
current bounds, outer-variable types, and all heap type arguments undergo
the same check before any permitted outer-`F` metadata rebase. A resolved
inference missed by a call site can no longer pass through the rebase helper:
it fails closed. Unsupported new type constructors fail closed only in this
opt-in path. This is a trusted semantics change requiring hosted build and
normal, return, unwind, outgoing-goto, metadata and ordinary-profile tests.

The source marker must share its file path with both ends of the enclosing
exporter ghost declaration block. The reconstructed CFG check also rejects
a synthetic entry mistakenly classified inside its own prefix, as well as
a path from any exit of the reconstructed prefix back to its synthetic entry,
or an internal edge back to its head except the existing synthetic end edge;
such loops would otherwise reenter a shortened binding without a separately
reviewed scope correspondence. All generic cut uses still require an exact
source/MIR body certificate; the actual sort4 certificate is not present.

The updated fixture includes `positive_f_bound`, an isolated copy of the
hosted callback-positive ownership/borrow protocol with a cut inserted after
the sole FnMut call. The function still has DefPath `callback_positive`,
because the accepted callback hook admits exactly that local body; the case
label only distinguishes evidence. This is a **candidate** for the concrete outer-`F`
rebase, not a proof. The runner records complete decoded MIR hashes and runs
the HRTB matcher only for that body. Missing negative fixtures for inferred
alias, live nested bound, outer-variable escape and altered CFG/source path
remain mandatory before acceptance; they cannot be counted from a green
positive or from a parser failure.

Local static review only: the component changes only the translator and
`verifast.ml`; `git -c core.whitespace=cr-at-eol diff --check` passed on the
disposable staged 12-patch clone, and reverse `git apply --check` passed on
the edited clone. No local compiler, verifier, runner or executable test was
invoked.
