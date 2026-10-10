# C1+C2 bound-prefix Cloud integration checkpoint

Status: **NOT_RUN**. This is an experimental, source-linked bounded prefix,
not a callable `sort4_stable` summary or an accepted tool profile. The
independent pre-Cloud structural review found no exploratory-run blocker;
allocation-placement admissibility and causal negative-control attribution
remain **PENDING** after any VF0.

Use the existing `o26-sort4-c1-current-recovery` owner/ledger and its frozen
Cloud lane. After a fresh C1 bounded VF0 and the mandatory refused C2 unbound
discovery, import this directory's `driver.py` by path and call:

```python
c2_bound = c2_bound_driver.run_bound(
    a, fixture, tool, env, result, c2_result, snapshot)
result["c2_bound_prefix"] = c2_bound
```

Here `tool` is the **same isolated C1 tool directory** already patched and
built by `c2_discovery.run_discovery`; that function mutates it in place to
the exact unbound C2 baseline translator. The new driver checks baseline SHA
`8e467ca535bfcead8555a717897ec0355261ee8ccb011f98441e2dba80b5984f`,
applies only `verifast-c2-bound-prefix-TEST.patch`, and checks resulting SHA
`daf29b03fbb7aa10e6f580c70780a9fdc5a2eb6d3f4470e1c38673212ca3d9a3`.
The patch SHA is
`4851c87be76630a627ff04d351ba6146879568eb877a28235a95d4cbea913925`.
No common runner, recipe, control or coordinator change is included here;
the main owner decides integration and dispatch under the current budget.

The driver pins annotated source, ghost-stripped runtime source, full normal
and readonly MIR, and full pre-AST. It checks both complete MIR edge graphs
are linear, noncleanup and direct-Continue, and the 18 later normal-mode
locals and 12 later readonly-mode locals first become live after C2. It exercises
saved-input MIR/pre-AST admission mutants without executing a compiler. It
then checks default-off C1, mandatory unbound refusal, the new positive, seven
negative controls and a verifier source-hash mutant. First failing VC
predicate/location and post-AST allocation/free paths require manual review
before any control or allocation claim is upgraded.

Local validation so far: Python syntax parse, saved-A5DE MIR/parser audit,
saved-input mutant parser audit and `git apply --check` against the exact
unbound C2 baseline all passed. No local compiler, extractor or proof ran.
