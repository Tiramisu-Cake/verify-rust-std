# Pre-dispatch review — native opaque batch

This is a static preflight record, **not** Cloud evidence or a proof verdict.
Scope: `SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10`, owner `select-sort4`, one
`o26-sort4-c1-current-recovery` lane, fresh 3600-second account. Policy revision
read: `c7ca8c467aecf10a4b53039372ee97714f854ee3` (branch adoption
`6726a08d30b37d6d0f4ae65c3d8c2861615d249a`). The old native-C4 ledger
and profile remain closed historical inputs.

## Entry and dependency closure

`control.py` selects the exact new phase/window/owner/ledger/lane and injects
`SORT4_NATIVE_OPAQUE_PHASE{,_ID}` into both Cloud execution and upload steps.
The pinned-object transport is `source-input.py` using the committed
`o26-sort4-c1-current-recovery.json` recipe. In Cloud, `run-proof.sh` checks
the exact recipe, then `run-o26-sort4-c1-current-recovery.sh` →
`run-o26-refresh.sh` → `run-sort4-c1-current-recovery.sh` →
`sort4-native-c4/driver.py`. The new marker routes to that same existing
driver, which must select `sort4-native-opaque/profile.json` and
`sort4-native-opaque/cases.rs` while retaining the frozen C4 snapshot and
slice-expression metadata under `sort4-native-c4`. The historical marker must
continue to select the historical profile and cases.

The driver imports Python standard-library modules and dynamically loads
`sort4-c1-current-recovery.py`, `sort4-native-entry-c1/c2_discovery.py`, the
C3/C4 drivers, `caller-entry/prepare.py`, and the pinned
`overnight-sort4/capture.py`. These are already in the recipe's infra/proof
path lists. Its frozen translator patch chain, C4 source/capture profiles,
`FROZEN-C4-SNAPSHOT.json`, and `SLICE-EXPRESSION-SOURCE.json` also remain
listed. The new profile/cases are separate proof inputs. The old
`sort4-native-c4/cases.rs`, `followup-cases.rs`, and `profile.json` are omitted
from this new recipe: the new marker selects `sort4-native-opaque` for those
reads. Historical Builds retain their exact earlier recipe/SHAs; the old files
stay in Git. The historical C4 phase is closed and uses its old published
infrastructure if reproduced.

No new verifier or kernel patch is included. The C4 effective tool pins and
prior fresh C4/admission IDs are fixed in `profile.json`. Prior admissions are
reused only as gate evidence; they do not prove a new case. The cases are
isolated diagnostics: pointer expression, early-return resources, checked
`usize + 16`, and opaque `MaybeUninit<T>` frame. They do not establish the
native→C4 or actual caller→sort4 edge. Full raw MIR/AST/refinement/verifier
artifacts and generated normal/unwind posts must be inspected after a fresh
Cloud run before any proof claim.

## Static checks and dispatch gate

Use only static parsing and shell syntax locally; do not invoke preparation,
extractor, compiler, verifier, or proof runner on the VPS. Before the first
Build, verify:

```text
git status --short --branch
git diff --check
bash -n research/challenge-8/cloud-build/run-sort4-c1-current-recovery.sh
python3 -m json.tool research/challenge-8/cloud-build/sort4-native-opaque/profile.json
python3 -m json.tool research/challenge-8/cloud-build/sort4-native-opaque/BUDGET.json
```

Also statically parse `control.py`, `caller-entry/prepare.py`, and the driver;
confirm sorted unique recipe paths, all referenced input files present,
`CASE_BEGIN`/`CASE_END` names exactly match `profile.followup_cases`, and
the new phase rejects the wrong owner, ledger, lane, marker and deadline.
After committing/pushing, confirm full published infra/proof SHAs and that
the committed recipe transports every input. Check the pinned-object payload
fits the 191-part transport ceiling. Inspect v2 reservations and active Cloud
Builds before a single submit; keep this account and one stable owner.

The main window ends **21:27:14 UTC**. The controller has an initial and a
second pre-reservation main-deadline check; timeout plus queue reserve must
fit the absolute **21:57:14 UTC** deadline. After main end, only an already
begun step, evidence, accounting and checkpoint may continue. No Actions
dispatch, local proof execution, selector or strict-cut extension is in scope.

Static local review: the driver selects the new directory only for the new
marker and fixes the two frozen metadata reads to the old directory; the initial six
case blocks are present in profile order, and all recipe paths exist. Python
AST parsing, JSON parsing, sorted unique recipe checks, Bash syntax, and
`git diff --check` pass. This review does not execute any proof input.
Published exact-SHA identity, pinned-object payload size (191-part ceiling),
capacity, and deadline remain dispatch-time gates after commit/push.

Follow-up preflight20:03UTC: prior1ba7 archive/inventory verified; opaque and
earlyreturn positives plus intended CURRENT-helper false post reviewed. Do not
rerun those unchanged cases. New exact case names: native-slice-cast-expression,
checked-add-overflow-reproducer, native-c1-unbound-capture. Bare multi-command
ghost annotations repaired as single block / individual source statements; no
assertions/posts/cut removed. Direct pinned rustc --emit=mir overflow-checks=on
panic=unwind added solely for checked-overflow diagnosis, no acceptance credit.
Same frozen general tool source/spec semantics; saved pure classifier replay
passes on retained d5 log (exact original hash). Static closure unchanged.

Thirdbatch preflight20:34UTC: new separate exact-native capture-only translator
delta86952a6a on1eab6eb5, kernel37ed unchanged; newbinaryusedonlylistedcapture
and default-off cases. Basefrozenbinary retained separately. Independent
addressreview confirmed sourceSHA/MIRcall210:21–92/markers194,212; oldC4gates
unchanged, fullcapturealwaysrefusesbeforeproof. Capturemayfailserializer ornew
shapegates; noacceptanceupgrade. Preparednativecomponent retainsrealresources,
alllinear debt/owners/thread/MU/type obligations; sharecleanup/strict/leak must
beprovedfresh. A preparedfalseArgs control is intended onlyafterpreparedtuple
assertion. ExistingpointerVF0/90 repeatedonceon newdelta opt-in0 as targeted
default-off regression; oldfullC4/native/MUmatrices not repeated. Allcurrent
source/MIR/header/posts/return/leak checks remain enabled.

20:47UTC controller definitively refused84616990 payload BEFORE reservation/API
Build creation: bounded source transport overflow; zeroCloudseconds/noBuildID.
Keep191partmaximum unchanged. Exact opaque follow-up with prioradmission skips
unused prepare_c4 call; old historical mode retains it. Recipe removes only
C2draft/sourcepin, C3selected/annotation, C4annotation and C3/C4fixturedrivers
used by that skipped preparation. All frozen tool manifests/patches/production
preflight/strictrelocation inputs remain present. C2ghost-strip module and normal
MIRcapture module retained. This is transport closure repair, no source gate
or proof assertion/post removed. Newpublished infraSHA requiredbeforeretry.
