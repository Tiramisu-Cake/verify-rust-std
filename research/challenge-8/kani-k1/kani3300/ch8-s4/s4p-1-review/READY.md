# W14 immutable READY — localized findings

READY_WITH_LOCALIZED_FINDINGS / REQUEST_CHANGES; exact author 590dd6360f5b4c92eab9fff30aa0d2e7d8d942ce.

Two P2 blockers: R14-01 skips all sorting-enabled cfg projections (16/32; zero complete ACTIVE contexts). R14-02 local/upload readers accept missing/null/old/wrong-type terminal schema, including full8 RECORDED observations.

See REVIEW.md and FINDINGS.json. Exact pins, 54/53 author manifest, 40 source/117 control hashes, six independent patch-tree replays, shallow5/7/2 and lexer-cache checks pass. Sixteen distinct targeted tests pass; initial stdin-harness import error preserved and corrected without candidate edits. Original final Validate302 PASS/554.090s/1.949 margin checked, not rerun. No native/CI/fullrunner/raw/GCS/push/accounting/subagents/model change; proof credit NONE.

Root -> originalfresh13 CURRENT26d -> new immutable repaired candidate/packet -> SAME14 delta/new review output. This sealed output must not be rewritten. Commit SHA is reported externally to avoid a selfhash loop.
