# R9 S2 caller-binding diagnostic rationale

## Observed defect and evidence limits

S1 Build `2f7b5d56-f9b6-44d1-a1fd-89f7b79870a4` reported
`CallBindingError: normal and readonly caller MIR semantic call bindings differ`
during `prepare-admission-controls`. The supplied P0a normal and readonly MIR
files are normal ID `2f4438d29b2ade2d32d0ef0005d26469ae940d30c8e0f77aa0c47b12c17c0d7c`
(SHA-256 `658620daa186f9bc49e6340479edd29bd67f64e7df68ed87c5dbdca7de494480`)
and readonly ID `6d637f2d547e8933050fcc273fe50d7e22750ab843ee70f0bebfc9260f4eaefe`
(SHA-256 `eafa543b1d1da383d5d590d62cda2bdb9a089eb683a70401fd7c919ac2cb1302`).
Their bounded caller excerpts retain the same T/F generic rows,
the same four source clauses, and the same threshold call at
`verified/lib.rs:129`; compiler lifetime labels differ while their input and
FnMut binder positions remain distinct and ordered. The comparator currently
alpha-normalizes those labels. An isolated synthetic pairing with that
renaming passes, so the observed label change alone does not explain the S1
equality error. The failed `observe()` input pair and the actual differing
normalized field remain unknown.

## Narrow change and preserved criterion

Keep exact normal/readonly semantic equality as the admission condition. On a
mismatch, report only case/caller, SHA-256 of each exact decoded MIR string,
the bounded set of normalized field names that differ, and up to four first
differing paths with short scalar values or bounded type/length/hash summaries.
Do not emit either decoded MIR string or a normalized object. This diagnostic
explains the next failure without accepting a mismatch, changing source/body
binding, relaxing generic, argument, region, resource, clause, or callsite
checks, or assigning proof credit.

## Validation boundary

Synthetic tests cover exact field/path reporting, alpha-renamed regions still
passing the unchanged equality gate, malformed helper inputs, and bounded
handling of long and non-ASCII keys/paths. An integration test confirms a
semantic clause-order mismatch still raises `CallBindingError` and reports a
field-prefixed path. Diagnostics hash exact decoded inputs, bound traversal and
summaries, and cap the complete ASCII-escaped error message at 3000 bytes; they
are constructed only on mismatch. The 22-test synthetic suite, `py_compile`,
and `git diff --check` pass. These checks validate only the diagnostic
implementation. The cause is still unknown until a Cloud retry reports the
failed pair's normalized field/path differences. The separately justified S2
native-signature fix may proceed independently; this diagnostic supports
examination of the actual next S2 caller pair. No local compiler, exporter,
decoder, extraction, runner, or verifier is run.
