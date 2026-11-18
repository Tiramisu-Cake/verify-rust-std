# PASS — static plan delta only

Replay from the g0 repository root:

```sh
python3 research/challenge-8/kani-k1/kani3300/wave0/f4-fix-plan-r1/validate_plan.py
python3 research/challenge-8/kani-k1/kani3300/wave0/f4-fix-plan-r1/validate_plan.py --check-manifest
```

The first command prints the deterministic VALIDATION.json report without writing
files. Requires the existing Python/PyYAML installation; no dependencies installed.
It reads YAML directly from frozen source Git objects, using BaseLoader to preserve
GitHub's `on` key, job IDs, conditions and matrix strings. It derives all seven
applicable PR workflows from the sixteen frozen YAMLs and rejects workflow_dispatch.

The release contract retains all four actual bundle builds and both complete
five-OS test matrices, including `include` artifact/target routing and all build
`needs`. Existing include rows overlay the five OS combinations; none adds another
instance. It checks the explicit 14-instance inventory and only the two native
publication skips: tag-push-gated kani_release and dependent package_docker.

41 negative cases reject the old six-workflow request, every removed workflow,
every removed build, each of ten matrix OS removals, each of fourteen instance
removals, a missing test job, display-name substitution, wrong artifact route,
missing release PR event and a required job misclassified as skipped. These are
plan fixtures in memory; frozen YAML and source tests are never mutated/executed.

Hash checks bind existing source/test bytes to the old manifest, all sixteen
workflow blobs, clean cab66681/tree858533 source identity and unchanged frozen
.github/scripts trees. They establish preservation without repeating the source
semantic audit. The exact old-to-new CI request diff is also recomputed.
The second command verifies all package hashes and immutable old748/cbfd/input
references, including unchanged working bytes for the old packages.

Operational gates in CI-REQUEST.md/json are future owner/coordinator obligations;
static plan PASS does not establish actual labels/events/checkouts or CI success.
Compiler build, new-test runtime, full CI and performance remain NOT_RUN; proof
credit NONE. Existing source-review/validation results remain at their immutable
references. F4-R14-1 remains open until reviewer14 approves the exact plan delta.
