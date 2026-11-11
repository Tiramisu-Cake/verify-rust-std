# Independent review — KANI3300 T1b-D reader

**Verdict: PASS for the bounded validation-metadata accessor. No blocking findings.**

## Checked identities

- Candidate commit: `6646181d23377325d9893b9f08e173f32c766f8c` (matches requested candidate).
- Candidate tree: `58400f0a937ca2ec577a78ddba0cc9b9d6948ab5`.
- Spec SHA256: `8864b2020535918c273c6f3ff22af9952a7531816107f4a7c7bce173ef0facb7` (matches requested spec).
- Diff SHA256: `e088294ff7cf333406755744f99fc08a518746d5a39fa8ce39af9312e7789995`.
- Changed-source dependency snapshots match packet inventory: `diagnostic_trace.py` `9bbf42b888a5a2654a9a71b2ef80ef7b3ef000b9f63c011d7ee67765c8514756`; `test_diagnostic_trace.py` `3760325b7b40328371721a8c3d654ba9480b9579e9bb378470ab8ba68c176f98`.

## Findings

- `diagnostic_trace.py:183-187, 497-509`: validation metadata uses the envelope validator, while every non-`validation.*` path still uses `validate_trace_page_identity`, which rejects `state == INVALID`. The metadata path is an exact one-level allowlist (`state`, `complete`, `errors`, counters, byte counts, sidecars, coverage, invocations, identities); `validation.records`, nested identity selection, and unknown metadata paths are rejected. The existing expected-build check runs before either path.
- `diagnostic_trace.py:67-180, 511-543`: metadata still requires the existing build/head/request/source/stage/schema, Kani/applied-tree, tooling/argv/env/filter, counter, sidecar, and coverage envelope checks. The shared page renderer enforces `count <= 20`, byte cap `<= 12000`, and `next_start` paging for lists; oversized scalar metadata is rejected.
- `test_diagnostic_trace.py:462-503`: new coverage exercises INVALID metadata access, payload/unknown-path denial, page/byte bounds, and source/stage/applied-tree/env/counter mutations. Existing wrong-build test remains. I found no change to `native`, `native-field`, summary, or their identity paths in this diff.

## Validation and limits

- Ran `python3 -I tools/test_diagnostic_trace.py` from `research/challenge-8/kani-k1`: **11 tests passed**.
- Reviewed only the committed packet candidate and declared reader/test changes. No build, compiler, proof, raw archive, or log evidence was read; this review grants no proof credit.

## Follow-up producer/validator schema assessment

The metadata accessor verdict remains PASS. Separately, the existing sidecar validator has a producer/schema mismatch at `diagnostic_trace.py:436-440`: it equates `sum(omission_counts)` with `omitted_records`. The producer's `mark_omission` only increments category counts (`trace.rs:362-375`), and its callers count different units: excerpt bytes (`394-414`), selected lines, and skipped external witness events (`346-359`). `omitted_records` is incremented independently only for dropped serialized records (`188-220`). The validator should own the correction: retain mapping/integer/nonnegative and boundedness checks, but do not equate these unlike units; still reject `COMPLETE` when omission counts are present. Changing producer record counters to satisfy the sum would break event `seen/emitted/omitted` accounting.

When that footer check fails, the reader raises before aggregation (`diagnostic_trace.py:439` precedes `448-453`), so the rejected sidecar's event records are not retained in `diagnostic_trace.records`; records from other accepted sidecars may remain. I did not inspect any real summary or raw evidence.
