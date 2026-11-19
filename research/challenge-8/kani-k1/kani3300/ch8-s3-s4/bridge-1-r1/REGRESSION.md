# Count regression and validation

Four new tests explicitly join s34_validate.NEW; all original selected 263 tests
remain. Exact list and expanded IDs are in TEST-LIST.json. Targeted count tests ran
first; only the corrected standalone portable test was run for B1-02. Full final
Validate runs once on exact committed repaired control, following control preflight
and a single source preflight. See VALIDATION.json for final measured counts/time.

Authentic file/hash/argv/streaming writers and serial controller launch/seal7, emit
int7, and accept it through public local and compact-only upload replay. Eight
adverse variants (8/missing/null/bool/string/float/0/6) reject on both routes. The
same controls cover STOPPED and SELECTED_PARTIAL with two or zero sealed rows;
selected count stays7. Frozen structured prefix bytes and later NOT_RUN/UNKNOWN
remain intact. Truncated/reordered request inventory rejects before terminal writes
or observations. Existing error/identity/protected/role/guard gates remain covered.

Separate fresh Python -B processes bind the committed old review reproducer to b9
and repaired tests to d675ef70; no worktree/module-cache mixing. Historical b9
263 PASS and standalone7!=9 FAIL remain immutable with exact committed references.
The baseline reproducer still records its authentic writer8 and all adverse accepts.

Native exports/process execution/resource telemetry are synthetic in service tests;
fixture dummy Kani/CBMC files are not executed. Python service PASS is no native
Rust compile, SAT/proof, runtime/peak/fit or B1/B2/init/provider credit.
