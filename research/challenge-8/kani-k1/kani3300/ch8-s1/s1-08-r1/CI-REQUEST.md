# S1-08 r1 — corrected local request

READY_FOR_REVIEW / **PENDING_DELTA_W14**. Preparation only; no dispatch authority.

Source `99e8456d200fff1299ee5756279cddb23921dc65` is unchanged.
Control `7c41333f9bfcfd7eb4e0ede7bd316443090c9025`, tree
`7ba8030690596cb491d1ae4f44e32805aa25931e`, parent
`9208b373c0a08a265fa0d7493a6529e331065271`.
Stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba` is unchanged.
Embedded request SHA256 `77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e`.

The two require_active closure type spans are repaired100/106 →95/101, preserving
exact full identities outside those coordinate substrings. Other six oracles,
all35 roots/14 groups,127 roles/111 labels/16 preserved bindings/113 covers,
negative expressions/companions, cfg/domain/checks/unwind/budgets/caps and exact
negative matcher remain unchanged. ROLE-MAP retains its prior hash
`bad63e0616c0061bf40d7e8d5c72324c8089574624a20f07a1f98a2806e5043d`.

New source-oracle package checks derive spans and validate every declared oracle;
the workflow preflight includes test_s108r1.py. No admission classifier moved into
the runner. Control depth5, export/tool depth2 remain. Source/variant fixtures are
checked against the actual pinned Git files by verify_package.py.

CI-REQUEST.json adds the external control envelope; EMBEDDED-CI-REQUEST.json is the
exact committed request. Payload/ROLE-MAP/request hashes are acyclic. Full source
and sibling control patches are pinned in PATCHES.json; REVIEW-DELTA.patch maps the
old frozen control tree to the corrected tree. Each reconstructs the exact tree.
Old s1-08 package, old control9ccd and source99e are immutable.

The same W14 must review this committed delta. Compiler/runtime, actual
exporter/verifier and CI/push are NOT_RUN; admission remains offline/PENDING and
proof credit NONE. Detailed scope and evidence: REVIEW-DELTA.md / VALIDATION.json.
