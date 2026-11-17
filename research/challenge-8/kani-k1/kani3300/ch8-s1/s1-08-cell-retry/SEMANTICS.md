# Exact delta from reviewed7c

The review target is da8c766f957c576eafa44bccfba2c45490cef6d1 over parent9208.
REVIEW-DELTA.patch is relative to7c; CONTROL-CANDIDATE.patch is relative to9208.
Both reconstruct the exact candidate tree. No amend of7c and no source patch.
Machine-readable whitelist, every JSON pointer change, changed function inventory
and SHA256 of unchanged control files are in SEMANTIC-DIFF.json.

- `.github/workflows/ch8-s1.yml`: keep the previous cell job with exact same
  setup/checkouts/runner/fallback/upload commands and all caps. Remove light,
  activation and heavy jobs, remove cell's needs edge and its now-unnecessary
  always condition, update workflow name and targeted Python test selection.
  Push trigger/fork concurrency/cancel-in-progress=false/max-parallel1 unchanged.
- `CI-REQUEST.json`: only the two cell timeout fields600→1200; new explicit
  execution scope, selected workflow/artifact count, derived timing totals,
  reservation metadata/schema, payload hashes and path inventory. All35 rows,
  their order,14 reference groups, all source bindings, ROLE-MAP, unions, flags,
  oracles, source/tool pins, native/snapshot/location/admission policies remain
  exactly7c modulo the two timeout fields.
- New `cell_retry_profile.py`: freeze all reference rows/proof settings against
  canonical7c semantic digest (normalize exactly two1200s fields back to600 for
  comparison). Check exact selected scope, budgets, workflow/batch/artifact
  policy; reject any different group/pair/geometry. This strengthens the
  existing request checks and does not replace them.
- `runner.py::load_request`: validate1200 only for these two row IDs, retain600
  for all reference others; retain every old source/config/mode/inventory gate,
  then require frozen profile. Error reports the required exact timeout.
- `runner.py::select_groups`: validate profile; omitted --groups selects cell
  only; any explicit value other than exactly[cell-u34] is rejected.
- `runner.py::build_argv`: require the exact ordered pair and unwind34, then
  change only --harness-timeout600s→1200s. All other flags/features/solver/checks,
  --jobs=1, exact matching and CBMC object-bits12 remain unchanged.
- `runner.py::_selection_matches`:1200s for the exact cell pair, original600s
  for reference fixtures; reject partial/reordered/extra cell selections even
  if a600s export is supplied. All existing marker/config/selection gates kept.
- `runner.py::_run_group`: reject any group other than exact production/PFC cell
  pair; receipt root_timeout_seconds derives from the row1200s and is retained
  even on failed/incomplete paths. Existing compile+sum(row-timeouts) expression
  now yields3300. Child execution, phase/cleanup/memory checks, original
  exit/exception, protected snapshots, rich validation, raw export, native
  capture, binary identity and fail-closed classification are unchanged.
- `check_package.py::check_yaml`: exact single cell job and frozen profile;
  all existing YAML/payload/pins/ancestry/caps/scalar/checkout gates kept.
  `fallback` uses validated same cell-only selection, including omitted groups.
  Setup build wrapper and incomplete receipt behavior remain unchanged.
- New `test_cell_retry.py`: exact scheduling and duration mutations, cell pair
  service cases and reused existing preflight/error/timeout/partial/snapshot
  controls. Existing test files remain byte-identical to7c. Full-matrix service
  fixtures are replaced with exact cell-pair synthetic fixtures for this profile.
  See PREFLIGHT-COVERAGE.json; no skipped/PASS substitution.

All other existing control files are byte-identical to7c, including rich_evidence,
binding_metadata, collect, pack_evidence, negative_oracle, ROLE-MAP, location
requirements/exceptions, oracle sources and variant patches. The pinned source
and stock tool commits/trees are identical. No source conditions, assumptions,
types, geometry, covers, labels, checks, oracle, solver, flags or unwind changes.
parse_export itself is byte/AST unchanged; the sole imported selection timeout
expectation adjusts to1200 for the exact pair. TIMEOUT remains NOT_COMPLETED /
UNKNOWN. Missing RESULTS remains an error; no completion or SUCCESS is invented.
This is scheduling/resource preparation only, with no new trusted premise.
