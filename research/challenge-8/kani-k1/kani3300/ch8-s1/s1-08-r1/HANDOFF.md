# S1-08 r1 — READY_FOR_REVIEW / PENDING_DELTA_W14

Concrete review finding confirmed and repaired. Two prospective negative oracle
IDs now use source-derived closure argument spans95:32–95:48 and101:21–101:37,
replacing stale100:32–100:48 and106:21–106:37. Full helper/type/file identity and
assertion ordinal remain exact; assertion location90 and intended expressions,
FAILURE/DETECTED and sole-failure semantics are unchanged. Other six full oracles
and their complete rows are unchanged. ORACLE-REPAIR.json contains both full IDs.

Source stays `99e8456d200fff1299ee5756279cddb23921dc65`.
Corrected control is `7c41333f9bfcfd7eb4e0ede7bd316443090c9025`, direct child of
reviewed9208, sibling of frozen9ccd. Embedded request SHA256:
`77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e`.
Old g0 package8ea1c1d370 /s1-08/, old control9ccd and source99e are immutable;
confirmed by tree/manifest/worktree checks. Exact identities/patches/envelopes are
in IDENTITIES.json, PATCHES.json and CI-REQUEST.json.

New regression derives locations from the current source declaration and checks
all eight exact declared oracles against canonical source/context/expression
pins and unchanged overlays. Old100/106, wrong columns/file/ordinal, coherent
source+hash+ID shifts and status/extra-failure mutations are rejected. Package
checks read actual pinned Git source; workflow synthetic checks use byte-exact
source copies and tiny isolated Git overlays. No observed failure was used to
choose an ID. No wildcard or suffix matching and no runtime admission changes.

67 small static/synthetic/Git-fixture tests pass. Committed control preflight,
actual-source checks, old-candidate immutability, exact mirrored payloads and
all three patch tree reconstructions pass. See VALIDATION.json and the detailed
STATIC-/DELTA-/ARTIFACT-VALIDATION.json. Logical source equivalence from5be to99e
is rechecked; no new source modification was needed. Negative matcher, runner,
collector/export/decoder/native capture/snapshots/location exceptions are unchanged.

35 roots/14 ordered groups,127 required roles/111 labels/16 preserved semantic
bindings/113 covers, max-parallel1, flags/checks/cfg/domain/unwind/caps and
preflight/shallow guarantees remain. ROLE-MAP is byte-identical to the old one;
historical closure-coordinate IDs inside historical semantic evidence are not
prospective negative oracle IDs. Control depth5 and export/tool depth2 are kept.

Next: coordinator transfers this frozen committed delta to the same W14 reviewer.
Review is PENDING_DELTA_W14; no GO, completed independent review or admission is
claimed. No additional concrete findings were received before freeze. Compiler,
runtime, cargo/rustc/Kani/CBMC/rustfmt, actual exporter/decoder/verifier, CI/push,
publication/ledger/budget reservation: NOT_RUN. Independent proof/B1/B2 credit NONE.

Recheck from this directory, without compiler or CI:
`PYTHONDONTWRITEBYTECODE=1 python3 verify_package.py`
`PYTHONDONTWRITEBYTECODE=1 python3 validate_delta.py`
`PYTHONDONTWRITEBYTECODE=1 python3 verify_artifacts.py`

Synthetic suite in /root/kani-ch8-s1-08-fix-w13/ch8-s1-control:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q test_runner.py test_package.py test_s104.py test_s105.py test_s107.py test_s108.py test_s108r1.py`.
