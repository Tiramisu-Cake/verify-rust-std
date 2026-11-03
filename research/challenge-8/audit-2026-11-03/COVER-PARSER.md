# Cover/result parser prototype

**Prototype only, not integrated into CI; no historical cover acceptance established.** No workflow, script or
K-1 tooling calls it. It was exercised only on hand-written synthetic records ([test_cover_parser.py](test_cover_parser.py));
it was not run on any real log of any Build or of Run 41404150041, and it never runs Kani.

## What it checks

[cover_parser.py](cover_parser.py) (Python standard library) reads one or more Kani `--output-format=terse` logs
(one per job or partition), an explicit JSON manifest and the verifier's exit status, and returns `PASS`, `FAIL`,
`INCOMPLETE` or `INPUT_ERROR` with per-harness reasons.

- **Binding.** Every result line is bound to the open harness of the same `(log, worker)`; a `Thread N:` prefix
  selects the worker. It never uses the most recent `Checking harness` line of another worker. A result line that
  cannot be bound, a harness restarted on a worker before its block ended, an unclosed block or a log without its
  `Complete - …` line makes the run not PASS.
- **Per harness.** Status (SUCCESS / FAILED / TIMEOUT / OUT_OF_MEMORY / PARTIAL / UNKNOWN / MALFORMED), check
  and cover counts, designated failed check for expected failures. TIMEOUT and OUT_OF_MEMORY are resource caps,
  reported as such, never as counterexamples, and never PASS an expected SUCCESS.
- **Set.** Every manifest harness needs exactly one record. Missing → `INCOMPLETE`; identical duplicates →
  `INCOMPLETE`; conflicting duplicates (e.g. two partitions) → `FAIL`; a row in the SmallSort namespace that is
  not in the manifest → `FAIL`. Rows of other namespaces (the rest of `std` in a partition job) are only counted
  per top-level module, kept apart from SmallSort.
- **Counts.** `Complete - s successfully verified …, f failures, t total` must equal the per-harness records of
  that log; malformed or inconsistent counts are not PASS. A `Verification failed for - …` list, when present,
  must agree with the records.
- **Covers.** Every required cover must be satisfied: the reported total must equal the manifest's
  `covers_total`, and satisfied must equal total. `covers_total: "UNKNOWN"` (also the default) stays UNKNOWN and
  gives `INCOMPLETE`; it is never read as 0. An explicit `0` is accepted only with
  `cover_policy.explicit_zero_allowed: true`. A root with `panic_cut: true` must list at least one cover of kind
  `route` (normal-return witness); a manifest whose only cover is a panic cover is rejected.
- **Suites.** `suite: "ordinary"` accepts only `expect: "SUCCESS"` rows and verifier exit 0; an expected-FAILED
  row in it is an `INPUT_ERROR`. `suite: "controls"` may contain expected failures (each with `expect_check`) and
  must state `expected_verifier_exit`; met expected failures are counted separately from success rows.
- **Identities.** Keys `source_commit`, `library_tree`, `kani_commit`, `toolchain`. A key declared in the
  manifest but not observed → `INCOMPLETE`; observed but different → `FAIL`.
- **Verifier exit.** A missing exit status is UNKNOWN (`INCOMPLETE`). A non-zero verifier exit is returned
  unchanged as the parser's own exit status, whatever the parser concluded.

## CLI

```sh
python3 -B cover_parser.py --manifest M.json --log job1.log [--log job2.log …] --verifier-exit N \
    [--identity source_commit=<sha>] [--identity library_tree=<sha>] > report.json
```

Exit status: the verifier exit if non-zero; else `0` PASS, `10` FAIL, `11` INCOMPLETE, `12` INPUT_ERROR.
Manifest (`format: "smallsort-cover-manifest/0"`):

```json
{"format": "smallsort-cover-manifest/0", "suite": "ordinary", "expected_count": 1,
 "identity": {"source_commit": "<40 hex>", "library_tree": "<40 hex>"},
 "cover_policy": {"explicit_zero_allowed": false},
 "harnesses": [{"name": "slice::sort::shared::smallsort::verify::<path>", "expect": "SUCCESS",
                "covers_total": "UNKNOWN", "panic_cut": false, "covers": []}]}
```

Tests: `python3 -B research/challenge-8/audit-2026-11-03/test_cover_parser.py` (44 synthetic cases: single
success; two interleaved workers; unreached cover; missing result or cover record; UNKNOWN status, TIMEOUT, OOM,
truncation; malformed counts and identity mismatch; duplicate and conflicting records; verifier exit 1 with full
covers; unknown versus explicit-zero cover totals; a negative row in the ordinary set; CLI).

## Limitations

- **Format.** The record shapes are those read by the K-1 lane parser
  ([kani_k1.py:89–107][k1-re], used here only as a source reference). They were not re-validated against a
  pinned real log in this stage; the order of a timeout marker relative to its status line is handled both ways
  but is otherwise unverified. Unknown or changed lines degrade to `INCOMPLETE`/`FAIL`, not to PASS, with one
  exception: under `explicit_zero_allowed`, a changed cover line is indistinguishable from a root without covers.
- **Cover identity.** Terse output gives only satisfied/total counts. A route witness is therefore established
  only when all covers of the root are satisfied and the total matches the manifest; which cover is unreached
  is not identified, and the binding of a manifest cover label to a `kani::cover!` site in source is not checked.
- **Manifest.** No manifest for the 202 ordinary v6 roots is published: their cover totals are UNKNOWN in this
  package (README Section 2) and are not derived from a grep or macro name. Such a manifest would keep
  `covers_total: "UNKNOWN"` and therefore give `INCOMPLETE`, not PASS.
- **Not done.** No integration into `kani.yml`, `run-kani.sh` or the K-1 lane; no run on real logs; no claim
  about any historical run. Integration needs a separate owner decision.

[k1-re]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/30f77e859903df14b442ff9294d4fbbd44827f20/research/challenge-8/kani-k1/tools/kani_k1.py#L89-L107
