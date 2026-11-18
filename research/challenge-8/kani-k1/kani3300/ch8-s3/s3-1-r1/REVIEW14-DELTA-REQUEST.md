# SAME14 delta request — R14-02 and R14-01

Review only the localized CONTROL/evidence change from frozen1dfc to
fc29b93b1e333b73e55e2872701c80d9927f3b02 (tree
c0368fa64ab474e4f64861aedd75a8f2639b1c29; sole parent9e14e033f9ee31522b571c127609dcdff76d230b).
Source513341f41ce53833a279571401c924bdddddb6c8 and tool0aac16ef62da9e9d5645782d458593e5d78143ba stay frozen.
PINS.json provides full request/workflow/source/control/tree/parent identities.
CONTROL-DELTA.patch binds the seven changed paths; PARENT/CANDIDATE patches and
ANCESTRY.json retain audited7/5/2 base objects. Original packagee8a8 and review610d
are unmodified. Prior source-semantic review is not claimed to approve this delta.

R14-02: check all available worker protected evidence independent of group state;
reject affirmative drift/unreadability/malformed records while retaining valid
interrupted missing-inner-AFTER recovery after verified shutdown/controller post.
Check original errors/exits, global stop, later NOT_RUN and portable replay's
explicit global-stop evidence. R14-01: check actual request-derived source/tool
writers and the same strict identity readers at local finalization and replay,
including missing/null/wrong-type/stale/mismatched values and unambiguous current
source versus historical patch ancestry. Preserve legacy defaults and fixtures.

Review REPAIR.md, s3_evidence.py, runner.py, s3_campaign.py and the distinguishing
regressions. Frozen reviewer tests3PASS mean defect reproduced. Targeted tests
and actual once-only final Validate have separate provenance in PRECURSORS.json,
FROZEN-DEFECT.json and FINAL-VALIDATE.json; use VALIDATION.json for final scope.
No compiler/native/CI/proof credit or budget action. No U waiver/policy change,
new tool, source/domain change, retry, cap reduction or optional S3 expansion.

Requested output: same14 delta disposition/findings for these exact identities.
READY -> SAME14 delta -> separately authorized root GO only. No dispatch/push/
PR/issues/ledger action is authorized here. Current accounting11/17,total41/48.
