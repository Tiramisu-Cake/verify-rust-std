# S3 checked-helper pair normalization review

**Review result: GO for the localized source-pair schema fix.** The raw focus observation uses exactly `{"verified": sha, "original": sha}`, while the checked-helper producer records the same files under `verified/lib.rs` and `original/lib.rs`. The previous chained equality compared those incompatible key sets and rejected a same-Build helper receipt before caller/P1 classification.

The fix now requires the raw mapping to have exactly the two expected keys and 64-hex values, normalizes those labels to the canonical source paths, and requires both the helper receipt and normalized observation to equal the hashes recomputed from the fixture. This keeps missing, extra, redirected, malformed, stale, and wrong-pair inputs fail-closed. The focused test uses the producer’s path-keyed receipt shape and covers absent/null, missing/extra, wrong-key, malformed-hash, and stale-hash cases.

I found no soundness or error-path issue in this change. It repairs validation of the same exact source pair; it does not confer proof credit or establish P1 native AST correspondence. The shared validator is used by P0c and P1, so a Cloud run must independently show both gates consume the helper receipt successfully before either downstream result is claimed. The separate false31 reporting edit was not part of this review.
