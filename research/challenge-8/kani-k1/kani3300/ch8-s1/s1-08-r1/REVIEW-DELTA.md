# S1-08 r1 — exact closure-coordinate repair

Review: **PENDING_DELTA_W14**, no GO. Task commit `4ccfdcc024`.

Source `99e8456d200fff1299ee5756279cddb23921dc65` is unchanged.
Old control `9ccd882ef2460fbc97400594e7e3dfc884a4a997` and old g0 package
`8ea1c1d370f4076eb6ed4aeaa0a96898499ce580` remain immutable.
Corrected control `7c41333f9bfcfd7eb4e0ede7bd316443090c9025` is a sibling over
`9208b373c0a08a265fa0d7493a6529e331065271`, not a child/amend of the frozen control.
Embedded request SHA256:
`77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e`.

| Oracle root | Old ID span | Correct ID span from99e |
| --- | --- | --- |
| activation_descending_rejected | 100:32–100:48 | 95:32–95:48 |
| activation_effectful_rejected | 106:21–106:37 | 101:21–101:37 |

Both spans cover exactly `|a: &u8, b: &u8|`, one-based columns, exclusive end.
The spans in source5be856 are also extracted and checked against the old IDs.
The two full new IDs, old→new IDs and source spans are in ORACLE-REPAIR.json.
The full helper/type/path prefix, `.assertion.1`, assertion source90, condition
`enabled::<T,F>()`, expected FAILURE/DETECTED and sole-failure semantics are
unchanged. The other six complete oracles and their rows are byte-equivalent
JSON values to the old request. No new failure/exporter/verifier results were used.

The prior checker verified relocated assertion lines/hashes but did not inspect
coordinates inside the generic helper instance's closure type. Pinned producer
passes through complete instance names and the driver demangles/re-emits the
complete function component. Consequently those coordinates must match source;
an exact ID matcher cannot accept the old100/106. Producer references and hashes
are in SEMANTICS.md / PRODUCER-SOURCE.json. New IDs remain source-derived
expectations; compiler/exporter/verifier are NOT_RUN.

New offline `oracle_source.py` checks all eight declared negative oracles using
pinned source bytes, assertion contexts/expressions, complete IDs and canonical
source/variant hashes. It derives the closure declaration span from the selected
source function, with no fallback guess for unsupported syntax. The regression
rejects old100/106, wrong columns/path/ordinal and coherent shifted source/hash/ID
replacements, including source95/101 shifted back to100/106. The source fixtures
are exact copies from99e; package verification additionally compares them with
actual pinned Git source and applies existing variant patches in temporary indexes.

`negative_oracle.py`, runner, export/decoder/collector, native metadata capture,
snapshots/location exceptions and admission semantics are unchanged. Runtime
matching still requires the entire exact ID, location, FAILURE and sole failure;
no wildcard/suffix matching or source classifier is introduced into the runner.
The new module is called only by static/synthetic package checks.

35 roots/14 groups,127 required bindings (111 labels +16 preserved semantic
bindings),113 covers, all cfg/domain/guards/checks/unwind/caps/group order and
max-parallel1 remain unchanged. ROLE-MAP is byte-identical to the old payload.
Workflow adds only test_s108r1.py to the existing preflight suite; depth5/2/2 and
all timing/resource caps remain unchanged. Existing historical export_sha256
navigation fields and historical ROLE-MAP records are retained as historical,
not new observed CI evidence.

All67 small Python tests pass; actual committed control preflight, pinned-source
oracle checks, immutable-old-package checks and three patch tree reconstructions
pass. See VALIDATION.json, STATIC-VALIDATION.json, DELTA-VALIDATION.json and
ARTIFACT-VALIDATION.json. W14 delta review is pending; no admission/dispatch or
proof credit is granted. No cargo/rustc/Kani/CBMC/rustfmt, CI/push/ledger or
publication was run. Additional concrete findings were not received before freeze.
