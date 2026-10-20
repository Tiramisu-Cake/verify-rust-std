# R9 candidate 4 independent review — GO for bounded source rejoin

Reviewed the current tool and project diffs against the candidate-3 baseline
`899c9d7e4ef8370e53926ee6813baa97bb71d701`. The translator change only
expands the already R9-gated source-command whitelist for concrete `u64`
array-close, `array_join`, and the exact `r9_current_u64_owners` call. Each
operation remains a normal source AST command passed to kernel verification;
the native translator adds no resource, equality, or trusted premise.

The verified fixture adds the recursive `r9_current_u64_owners` lemma with a
body, `req true`, and the stated `foreach` postcondition. Its recursive case
builds ownership only through the existing concrete-u64 `own` interpretation
and checked `foreach` closure. The returning-edge marker reads the current
tail cell from its physical points-to chunk, closes the adjacent zero-length
and singleton array ranges, joins at `begin + 1` and `begin`, asserts the
three-cell current array, and calls that checked lemma. It does not use entry
`xs`, an address-only inference, `assume`, `leak`, or a newly declared
unproved lemma. The marker stays on the previously qualified selected-Drop
returning edge; own-unwind handling, CFG targets, lifetime handling, and
normal/unwind posts are unchanged. This is a source-level and static review;
the kernel must establish that these exact resources and fractions support
each command.

The stage-receipt fix now requires an exact three-key source map: the original
and verified case hashes plus `small_sort_source` equal to the preparation
record's pinned source SHA-256. Both before and after maps must match exactly,
and `source_unchanged` remains required. Existing exit, status, exact Drop
event, target-location, diagnostic, and source-integrity gates remain in force.
The new wrong-third-pin synthetic case is rejected.

Validation run: `git diff --check` passed for the candidate tool diff and the
project changes; `r9-guard-return-controls-service-test.py` passed all 9 tests;
`r9-marker-service-test.py` passed its source-marker, environment, and
returning-edge checks. No compiler, local preparation, proof, or Cloud Build
was run for this review. **GO for this bounded candidate only.** This grants
no proof credit or profile acceptance; source closure and Cloud qualification
remain required.

Final source closure: tool706e7c89fdf69dbe11e05ef275300b20d30a27cb,
profile055374de5bc913e4725951f0d8c9458f1c6498ab5f89d4a039d8cab591741a67;
static19patch/17pins/18retainedbase andbundleverify PASS. Source model/prelude/
R8allocationpatch remainbaseline; actualproof/controls pendingCloud.
