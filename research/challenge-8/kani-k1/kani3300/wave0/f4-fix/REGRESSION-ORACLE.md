# Main FAIL → fixed PASS acceptance

The standalone PR adds one script-based regression directory with the exact observed Cargo
fixture, two feature-selected call paths, and independent raw-padding control. It uses the
standard compiletest exec config, executable `test.sh`, `check.py`, and expected success line.
It imports no confirmation profile, workflow, service collector or historical runner.

The seven native invocations are: independent unsafe control, then delayed singleton,
initialized singleton, and paired selection for each of the two cfg variants. Each uses an
isolated target directory. The feature names select call paths and establish no actual compiler
processing order. Neither direction's compiler-order coverage is claimed.

The parser requires complete JSON export, exact harness selection, standard enabled checks,
terminal per-harness verdicts, a complete regular-output property inventory, sequential indices,
unique native IDs, matching success/failure/unreachable partitions, matching exported failures,
and native aggregate exit consistent with per-harness verdicts. Reachable or unresolved
unsupported constructs fail the regression. An aggregate paired exit of 1 is expected because
the delayed harness fails; it cannot establish whether the initialized harness passes.

Acceptance requires all of:

- Initialized singleton and paired harness SUCCESS, including its `result == 7` assertion.
- Delayed singleton and paired FAILURE from the uninitialized safety check at the shared
  `src/lib.rs:12` read, with every failure bound to that source site/class/description.
- Independent unsafe FAILURE at `control.rs:16` from its intended uninitialized safety check.
- Equal semantic multisets for each singleton and its paired result: function/class ID with
  only the final ordinal removed, status, description, source location, and multiplicity.

Historical 13/20/37 property counts remain observations; none is a fixed regression quota.
Missing exports, timeout, spawn failure, signals, error exits, partial results and malformed
schema/data fail the test. Static/mocked error-path checks live in this package's `validate.py`.

## Established versus pending

`validate.py` executes the new pure oracle against all seven retained compact results from
run44177926794 and rejects main's observed paired initialized failure. The exact fixture files
are byte-identical to the reviewed/executed reproduction. This establishes **main oracle FAIL
on observed compact data**; the newly packaged test itself has not run on a main compiler.

The parser compatibility check reconstructs COMPLETE/export envelope fields discarded by the
reviewed compact producer; it reuses retained configuration, selection and full properties.
That adapter does not independently re-establish native raw export integrity.

A synthetic fixture copies each singleton result to its paired slot. The oracle accepts it and
rejects dropped/duplicated/changed checks, unsafe failure suppression and wrong failure sites.
This is **synthetic expected-fixed oracle PASS**, with **actual fixed compiler/runtime NOT_RUN**.
Fixed PASS is the acceptance criterion for future authorized CI, never a current result.

`regression-main.patch` contains only the new tests against frozen main for an authorized
future red-check reproduction. `fix.patch` reproduces the exact complete candidate tree.
Neither patch has been run through a local compiler. A future CI failure of setup/compilation/
parser must be reported by its actual stage; it cannot satisfy the expected main defect failure.
