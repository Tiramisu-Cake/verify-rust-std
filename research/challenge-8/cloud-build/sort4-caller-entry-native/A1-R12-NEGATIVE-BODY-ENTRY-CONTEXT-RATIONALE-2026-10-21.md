# R12 focused negative body-entry context controls

For `N-default-contract` and `N-freeze-contract`, a candidate failure at the
intended `result<=32` post does not alone prove that execution entered the
selected implementation body. The same-build AST and compiler inventory bind
the implementation alias and source line; the first verifier error and its
following context notes must then contain exactly one `Verifying function
'<alias>'` frame at that body line. A prototype-implementation frame, a frame
before the first error, multiple errors, or missing/ambiguous context leaves
the candidate unattested. The classifier's `error_context` and the runner's
independent raw-log gate are separate checks.

The S2 source observation had an intended-negative candidate with the expected
error and `impl-body` classifier context, while the matrix rejected the row for
missing focused execution attestation. The runner's body-entry gate was
incomplete: after validating the unique first error it returned without
evaluating its intended post-error frame matcher, whose code was unreachable
after the environment-digest return. The source owner restores that matcher;
the synthetic suite here protects success for both implementation aliases
and rejection of header-only, missing, wrong, duplicate, prior, or ambiguous
context. A negative execution attestation records body reach and preserved
conformance while keeping `focus_body_verified=false` and `proof_credit=false`.

These tests exercise only local synthetic log strings and stubbed attestation
inputs. They establish parser behavior, not a new verifier run or proof result.
