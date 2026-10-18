# A1 unused_mut fix — 2026-10-18 (CLOSED; R-only build exit2)

Owner select-sort4; initial checkpoint/HEAD and remote d2444867. No newer commit
was present. Eight pre-existing local Evidence Brief policy/instruction files
remain outside the implementation commits and byte-preserved.

T0 **2026-10-18T08:37:29Z**; main deadline **10:37:29Z**; finish/checkpoint absolute
cutoff **11:07:29Z**. New ledger BUDGET-A1-UNUSED-MUT-FIX-2026-10-18.json:
960 Cloud seconds, maximum one Build, timeout900 plus existing60 queue reserve.
Old account330/960, retired630, and all earlier closed accounts stay unchanged;
no carry/retry. v3 coordination/slots/owner rules unchanged.

Updated ordinary Brief for57ea65a3-475e-4370-810c-19ad36803174 (processor0.4.0)
corroborates R-only reference build exit2 and two unused_mut diagnostics at
exporter src/lib.rs843:17 and906:60. The pinned source has deny(warnings).
All26 rows are source-reported NOT_RUN. This resolves the old reporting gap for
selecting the minimum fix; historical UNKNOWN reports remain immutable history.
See diagnostic-57ea65a3-2026-10-18/REPORT.md and its original reader reports.

The new R file preserves the old R patch, with exactly the two approved mut
removals. Exact full source reconstruction applies43 unchanged pre-R patches,
checks old/new R and C maps, and confirms the proposal overlay equivalence.
No compiler/exporter/extraction/refinement/verifier runs on VPS. Exporter result
c29d0d4692eab84257fe61036d6e41dbc11ee3ad999005df4ffb157bb8b463ad;
full new R-patch SHA91fe9ad49c34d834e435605d95fb183e92e03c72f3d353e588dd7092fbeb6466.
Schema/translator/C patch/kernel/model/prelude/refinement and all other semantic
inputs retain their pins. No allow(unused_mut) or warning-policy change.

Authorization phase SORT4-A1-UNUSED-MUT-FIX-CLOUD-2026-10-18 governs this ledger.
C's immutable translator checks the existing experiment protocol phase
SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17. The coordinator explicitly maps
new authorization to preserved protocol through separate env fields; entry and
runner enforce the exact pair and new profile hash/proof/infra pins. This keeps
the C/translator bytes unchanged; no old account is reopened. The new root result
records both identifiers. Stage receipts remain bound to this Build, new profile
and exact proof/infra/tool/source identities.

R-only exporter+console must build exit0 before its independent reference receipt;
C is applied/built only afterwards. The unchanged runner retains all26 rows,
full P1 native pre/returning/unwind equality and mappings, positive two-body
conformance→receipt→caller sequence, negatives, seven regressions, and false31's
own-pair two-body→own-receipt→caller/boundary lifecycle. No positive receipt is
substituted for false31. Synthetic controls have no compiler/refinement provenance
or formal credit. Unreached rows stay NOT_RUN; early/wrong-stage failures remain
INCONCLUSIVE. Reuse is identical-pair export/decode/refinement inside this Build
only, each proof target separate, no cross-mutation evidence or general cache.

Source-only tests:10 dispatcher admission/profile checks (old/new phases,
wrong account fields, no retry/timeout/profile binding) and4 same-Build reuse
identity checks PASS. P1/classifier/receipt algorithms are unchanged. Independent
Luna High source review found no blocker; no nested delegation. Full committed
closure/config preflight and publication exact pins remain mandatory before
submission. A synthetic PASS or source review is not formal verification.

Stage budget keeps the existing900s outer envelope/815s nominal work deadline;
no required row is removed. Earlier failed execute268s is not evidence that the
whole matrix fits; time exhaustion leaves incomplete gates explicit. After
terminal status use smallsort-brief only, no raw/archive/log fallback.

Full A1/A2 remain open, even if threshold/interface matrix later succeeds. Actual
small_sort→helper, A2/ZST/resource redesign, C5/copies and sort8 are excluded.

Committed-source preflight PASS for `e58a75bbdcf6704175ceebcd72a227607a92d2ae`:504218 bytes/672292
base64 bytes,169/191 substitutions;33 infra +107 proof paths restored from160
shared Git objects with exact hashes/closure. New auth + preserved protocol env
and new profile hash verified; config argument and submitted-config transport
bounds PASS. Published release binding: A1-UNUSED-MUT-RELEASE-2026-10-18.json.
The copied patch artifact retains inherited context whitespace; its delta from
old R has no introduced whitespace issues and exact two-token source difference.

## Closure

Sole Build7c26b389-1ad9-45c8-9adf-089125476fdb: FAILURE,433s charged,
527s retired. R-only combined build exit2 corroborated;26NOT_RUN source-reported.
Brief has no actual compiler/make diagnostic. Final C and case lifecycles not
reached by source flow. See A1-UNUSED-MUT-CHECKPOINT-2026-10-18.md and bounded
ADMIN-AUDIT-REQUEST-7c26b389-2026-10-18.md. No retry or raw fallback.

Local work window extended by owner by1h after the Build: main11:37:29Z,
finish/checkpoint12:07:29Z. Closed CI ledger retains its original window and
accounting; no new Build/raw-audit authorization. Owned /tmp source/preflight
scripts and redundant report copies cleaned via explicit whitelist; coordinator
state and unknown/foreign artifacts retained. See cleanup manifest.
