# Exact construction → canonical FBC V4: INCONCLUSIVE

Build `9bbabaf6-b2c4-45de-9ef3-4b9f733c4ef2`, proof/infra
`572cfe9ebd94abb2822ec5608253504338a6800c`, collectorSUCCESS/314s.
Evidence `gs://smallsort-ci-evidence-504462351565/cloud-build/9bbabaf6-b2c4-45de-9ef3-4b9f733c4ef2/`;
archive `337b41f94c5cc66d0407f064e2e47b85714ab45e656734f1dd8ec4b66af9f3e2`.
Full archive/text integrity verified; all8case stages/logs inspected.
[Exact source/tool/profile/case identities](AFTERNOON-IDENTITIES.json).

Affected existing V3b controls, stock/six: positive PASS_FRAGMENT_ONLY with full
post/return/leak; negative matched false78:20–25. Source279 / extracted73 exact.
New V4, stock/six, both positive and first-body-false: exporter/decode/refinement0,
AST/MIR admission true, source279 initializer73 and full-own close74 reached.
Canonical FBC-close75 fails at generated first field5:5–18:
`No matching heap chunks: CopyOnDrop_src<T>(drop_guard_addr, _)`.
No dead/unrelated errors; FBC-open/current roundtrip/full post/false80 not reached.
Allfour are INCONCLUSIVE, no negative or FBC packaging credit.

## Exact permission frontier (pinned static review)

Ghost AddressOfVar is correctly admitted; kernel stmt_mark_addr_taken traverses
Close/Open patterns (verify_expr1518–1535), so changing address syntax is not a
repair. Translator2024–2041 declares immutable MIR local as ConstTypeExpr.
Kernel verifast993/1044 allocates addressed const aggregate with coefficient1/2;
produce_c_object (verify_expr1683–1911) propagates that to fields/padding. Three
Initialization assignments preserve1/2 (verify_expr2652/2675/2755). Scope cleanup
verifast189 expects1/2. Generated canonical FBC has FULL field/padding chunks.
The missing match is a coefficient mismatch. No ghost operation can create the
missing permission. Actual std/source/algorithm/signature are unchanged.

Stripping ConstTypeExpr, changing exact let to let mut, silently accepting a
fractional FBC or adding full chunks would bypass this obligation. None done.
The needed next transition is source-linked move/implicit mutable borrow for
compiler Drop, with explicit immutable-byte/alias/permission conservation.
Canonical full FBC at the immutable local is NOT established by V3b own.

[Completed payload post/glue design](../../completed-payload/SEMANTIC-CARD.md)
remains design only. Full caller and actual Drop-bearing construction remain
OPEN; no actual seed/sort/insert owner acquisition or public/general theorem.
