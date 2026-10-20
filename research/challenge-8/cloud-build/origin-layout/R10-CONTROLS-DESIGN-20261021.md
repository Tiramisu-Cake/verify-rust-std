# R10 recovery-control corrections

## Duplicate marker source binding

Build6's `duplicate_marker` source and stage gates passed, and the expected
frontend message was observed, but the checker attached it to the cloned outer
PureStmt at `verified/lib.rs(318,5-333,10)`. The control runner instead chose
the first `/*@ {` in the mutated file, so its expected line 227 referred to the
original block. The mutant is the exact original marker block cloned after the
original; bind the rejection to the inserted block's complete byte-derived
source span, including start/end lines and columns. Keep the exact diagnostic,
VeriFast stage, source identity, and stage receipts mandatory.

## Versioned wrong-origin meaning

Build6's historical `wrongorigin` mutant changes the half-share assertion to
`assert [1/2](*begin |-> ...)`. That target is not source-distinguishing: the
actual `array(begin, 1, ...)` may satisfy/open the same points-to resource, and
the verifier reached the independent missing-loop-invariant refusal at line
271 before the intended predicate. Preserve the archived Build6 verdict as
INCONCLUSIVE; do not infer any result for it from a later run.

For the versioned replacement meaning (`wrongorigin_mutant_version`), mutate
the sole cleanup marker command from
`end_ref_readonly::<u64>(r9_guard_ref)` to
`end_ref_readonly::<u64>(begin)`. The pinned `aliasing.rsspec` contract requires
`ref_readonly_end_token(p, x, f)`, `[f](*p |-> v)`, and `ref_initialized(p)` for
the exact argument `p`; `init_ref_readonly` creates that token keyed by its
reference argument. The marker first obtains the token for `r9_guard_ref`, then
opens the associated array resources. Calling the end lemma on `begin` therefore
asks for a token keyed by `begin`, not for a generic token or numeric-address
match. This is a source-local mutant on the observed cleanup recovery edge,
before the later loop-head/backedge refusal.

Classify it as an intended resource refusal only when strict source/stage and
selected cleanup-return binding gates pass, the exact mutated end command is
executed and is the last executed statement before the sole verifier error, and
the diagnostic names the missing `ref_readonly_end_token` at that command.
Any earlier loop-invariant refusal, another predicate/error, missing binding,
ambiguous error, or setup/timeout remains INCONCLUSIVE/NOT_RUN. No checker path,
invariant admission, runtime CFG, or proof predicate is bypassed.

R9 remains the historical five-case campaign, including its original
nondiscriminating `wrongorigin` v1 mutant. R10 uses the separately named
`r10-guard-return-controls-v2` campaign with the same five case names; its
`wrongorigin` slot uses the v2 end-token-origin mutant above. This makes the
active R10 gate discriminating without rewriting or retroactively classifying
any archived R9 verdict. R10 inherits the existing source/stage/native
selected-cleanup binding gates, so the new command is qualified against the
same observed returning cleanup Drop and exact preparation/source identity.
The bounded Build6 record explicitly leaves parser-input binding unestablished;
this control preserves that limitation and does not promote source coordinates
or a synthetic service pass into proof credit.
