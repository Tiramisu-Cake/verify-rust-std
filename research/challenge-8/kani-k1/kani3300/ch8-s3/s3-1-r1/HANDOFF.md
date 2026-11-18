# READY — S3-1-r1 CONTROL-only repair, SAME14 delta next

G0 package is the commit containing this manifest; full SHA is in completion.
Control `fc29b93b1e333b73e55e2872701c80d9927f3b02`, tree `c0368fa64ab474e4f64861aedd75a8f2639b1c29`,
sole parent `9e14e033f9ee31522b571c127609dcdff76d230b`.
Frozen source `513341f41ce53833a279571401c924bdddddb6c8`, tree `a818efb2157d57af0c9c604f6d0ca85873b8712c`,
parent `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a`.
Stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, unchanged.
Request SHA256 `17f7cfba45ca5e572b7e32bea25d31add90885dc2378b725783737e1a6577604`.
Workflow SHA256 `8d5fd03476d3d7666692cc7267d3fe598a0007c54ec6576de3538cef434ac709` (same18min recipe bytes as1dfc).

R14-02: recorded worker protected errors/mismatches now globally stop regardless
of group state. A later matching controller post cannot erase drift/read errors.
The verified interrupted-worker case with genuinely absent inner AFTER remains
permitted; malformed/present unknown evidence does not become absence. Original
worker errors/exits, completed prefix and later NOT_RUN survive; local/portable
replay explicitly retains GLOBAL_STOPPED status and original stop evidence.

R14-01: actual S3 compile/source-under-test writers use requested source/tool
SHA/tree throughout. Current pre-overlay base_std_sha is513341; historical patch
ancestry99e845 has its own field. Both local sealing and upload-only replay check
all identities and reject missing/null/wrong-type/stale/mismatched values. Legacy
defaults/policy/fixtures remain intact. REPAIR.md details the seven-path delta.

Frozen reviewer regressions:3PASS means both old bugs reproduced on exact1dfc,
not acceptance. Fixed targeted22PASS/41.840s; focused10PASS/30.811s. Actual final
Validate on exactfc29: **182 PASS** (136 legacy +46 S3/repair), execution count1,
**490.471224626s**, margin **2.201964041x** at unchanged1080s >=1.5.
Source preflight STATIC_PASS/22.981898110s; three CONTROL patches
replay to exact final tree, ancestry7/5/2 retained. Precommit and final provenance
are separate; no old run is assigned to new hashes. No cap change was needed.

Source513341, tool0aac, originale8a8 package/review610d and six source/domain maps
are immutable. Nine roots/full-byte domain/actual bodies/PFC/cfg/71 literal sites/
44 covers/bounds remain unchanged. Reject-ALL-U and disabled proposal unchanged.
All campaign/resource/setup1800/job180/18minValidate caps remain unchanged.
Native compile/proof/fit, full native runner and CI **NOT_RUN**; proofcredit0.
No source edits, compiler/cargo/rustfmt/Kani/CBMC, CI/push/PR/issues/raw evidence/
ledger/reservation/budget/subagent/model action. Current11/17,total41/48 unchanged.

Optional next-leaf plan was sealed early as56edd773a58d40be0f1da6799364448f59303529
per explicit priority14 steering; it is an incomplete PLANONLY checkpoint.
No further plan expansion delayed this repair.

**READY → SAME14 delta → separately authorized root GO only.**
Use REVIEW14-DELTA-REQUEST.md and CLOSURE.json. User coordinator alone may launch
future12/17 after root consent; no dispatch authorization is requested here.
