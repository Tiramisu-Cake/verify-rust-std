# Independent W14 validation

Result: PASS within static and bounded synthetic scope. See VALIDATION.json,
CHECK-RUNS.json and PROVENANCE.json for stage distinctions.

| Check | Result |
| --- | --- |
| Source714 packet | 40 committed files, 39 manifest entries MATCH |
| Repaired runner a8e packet | 28 committed files, 27 manifest entries MATCH |
| Component patches | Nine exact Git diff/replay matches; old composed2d00 replay is not approval |
| B-01 | Eight independent expected-group/removal/interruption cases PASS |
| B-02 | Twelve both-stream/chunk/ANSI/exact packed-coordinate cases PASS |
| Original long-middle | Actual baseline2ec vs repaired472 PASS; same bounded previews, exact new error block retained |
| Runner controls | 33/33 PASS once, including unchanged preview; RUNNER-33-RECIPE.py and RUNNER-33-TESTS.txt |
| Source CFG/model controls | 19/19 PASS once, exact draft source-policy/test/fixture bytes inherited to final |
| Final5a9e packet | 45 committed files, 44 manifest entries MATCH |
| Final7 patches | Exact Git diffs and replayed source/control trees MATCH |
| Final integration | CLOSED; source714 and repaired472 byte identities plus reviewed binding changes |
| Final preflight | PASS; actual shallow control/source/tool depths7/5/2; all request/source/payload hashes |
| Author final79 | Exact final provenance bound; not independently rerun |

Commands executed: `python verify_components.py`, `python reproduce_repairs.py`,
the immutable repaired runner `validate_package.py`, RUNNER-33-RECIPE.py from the
repaired control directory, and `python -m unittest -v test_cfg_pfc` in a disposable
materialization of the exact source draft control. Then `python
verify_integration.py` and immutable final `batch-r2-r1/validate_package.py` ran
static checks only. Python children in service tests are synthetic fixtures.

The initial reviewer fixture-path failure is retained in
COMPONENT-BINDINGS-INITIAL-ERROR.txt. After correcting the harness dependency and
function-name token lookup, only that static binding check reran. The final
COMPONENT-BINDINGS.json records the successful corrected check. Synthetic suites
and independent repair reproductions ran once each.

Historical W11 expanded33 preview failure remains preserved; our one-run33 PASS
does not establish that the asynchronous preview ordering is fixed. No source,
test gate, runtime or ledger was changed to obtain a pass.

Native compile/model/production retention NOT_RUN; historical cause UNKNOWN;
proof credit NONE. No raw production evidence was read or downloaded.
