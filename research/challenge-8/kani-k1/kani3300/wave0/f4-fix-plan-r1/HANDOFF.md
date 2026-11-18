# READY_FOR_DELTA_REVIEW14 — F4-R14-1 plan-only correction

Issued task `task4817b5ddf0c1526432b9c7fa3b16a9ba81a85bb7` is complete.
Old package `7485bbb27a72dd463d4a9628c8627689d30e7e56` and review
`cbfd888f274a0666f09af79d98ef4b8b8061f497` remain immutable and unedited.
The latter's CHANGES_REQUIRED verdict is historical; reviewer14 alone closes
F4-R14-1 after reviewing this exact committed delta. No new review was run/sent.

Source remains `cab66681c912a3e5ee01a106faaeee5237ca0232`, tree
`8585336ed35a14fe0fc157a7ca4e0d52075c0e49`, direct parent/frozen main
`faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`, base tree
`09b828b47c93e90e140e8c41f9048109a2f4a786`. No Kani commit was created.
Compiler fix, regression bytes, all sixteen workflows and scripts are unchanged.
The source semantic audit is not repeated. Existing source validation and review
remain authoritative for their stated static/synthetic scope.

## Exact old → new metadata delta and hashes

Only CI-request/metadata/docs/validation are added in `f4-fix-plan-r1/`.
This is an overlay over the immutable old package, not a replacement source bundle.
`METADATA.diff` is the exact unified diff of old748 CI-REQUEST.md/json to this
package's versions; validate_plan.py recomputes it directly from old Git objects.

| Metadata | Old748 SHA256 | New SHA256 |
| --- | --- | --- |
| `CI-REQUEST.json` | `da722e7fe2ffee8f8c6822c276d5fc37da54e7c7ec19895ec14644e99e06fb7b` | `7a1117c9806f2af86ff7304233885748d209ed367089bdd41778efe7d0cb0739` |
| `CI-REQUEST.md` | `b57829eb6a60c2b76063398f30799c8fcb362c9d65e0305e7f2591a93c63b648` | `65f036dd8318d548990d9509d8b2b61e493f63a30a16a80d969ac8035c7d1c02` |
| `CHECKPOINT.json` | `7676bbbbeec7f4fd0b11e5570bb1256b2bc81a610388e4d383bdc9f85386ea8f` | `9d23b7a678358a83124234b20acd4e1731da242390ae7851b154baebefe8e561` |
| `VALIDATION.json` | `2789c946725212589c149197d3e3379909b9ad6a1ad8b1e87db43eca73ca0913` | `5afdb897d7ea261dc82552811ca7deb90d7bd67b3cbdc79dbd7f4eec2b12d087` |
| `VALIDATION.md` | `ffe48721db493a0375f3b401249c93941a80d8fb92f519020bca7e8ef03a98a4` | `9e76b42af5c65a41f7ceecb4e2097f6808b23a95b5ede05661005f34162d899c` |

CI-REQUEST.json: the original six workflows remain in order; release.yml is
appended. New structured release coverage records the exact four build job IDs,
platforms and runners, test_bundle and test-use-local-toolchain full five-OS
matrices (including artifact/target include rows and needs), fourteen explicit
instances, and only kani_release/package_docker publication skips. Native events
for all seven workflows are recorded. The review gate now explicitly requires
approval of this plan delta. Source/base identities, labels, regression OS matrix,
27/28 reference, no authorization/consumption and untouched ledger fields remain.
Future run identity fields are explicitly NOT_CREATED_OR_RECORDED.

CI-REQUEST.md: corrects the old release exclusion, enumerates the 4+5+5 PR
instances and carries the review's operational gates. The authorized owner must
bind reviewed source/trigger/final PR branch HEAD/tree/base, record actual PR
merge-ref checkout SHA/tree separately, review any merge-tree delta, handle skip
text in final PR HEAD and the entire pushed range, establish both benchmark
labels and eligible native event, preserve concurrency outcomes and every native
matrix conclusion. None of the seven has workflow_dispatch; feature push alone
cannot supply full PR coverage. Owner selects choreography and accounting.

CHECKPOINT and HANDOFF describe only the new plan-delta readiness. VALIDATION
now records the narrow static plan gate; old source/oracle validation remains
unchanged at old748. validate_plan.py is an added package validation tool and
never edits/runs source scripts or tests. MANIFEST binds old inputs and all new
package hashes; no historical manifest, validation, evidence or ledger is edited.

METADATA.diff SHA256: `2a856b2ddb273177636454146ac48c0557f57f0c3ce88d91b36b1751cf5e2898`.
New validation gate SHA256: `4bd054c2fc2dfb7caedf353a214bf8806c536f15dbb715a3aa3f51d13c0fa8eb`.

MANIFEST.json lists exact hashes/commit:path references for all fourteen old
package files, all review files and the issued task; source/test blob/hash inventory
and sixteen workflow identities are retained from the immutable old manifest.
The complete source patch remains old748:`research/challenge-8/kani-k1/kani3300/wave0/f4-fix/fix.patch`,
SHA256 `01cb57c32c39d03335e47e74182634f638e3566e93338ca51b29e029c81f5318`.
Regression-main patch SHA256 remains
`392e0b2ae93282c39ba5324d2bde33cb9dc1f054c3f7c05f8a57aa18a7686b37`.
All source/test bytes are referenced at cab66681 with their original hashes;
there is no copied or modified compiler/test source in this delta package.

## Validation and next step

PASS: seven applicable PR workflows/native events and fourteen release PR
instances match frozen YAML. All 41 removal/identity/routing/skip negative cases
are rejected. Existing source/test hashes, sixteen workflow hashes and frozen
.github/scripts trees match; immutable old748/cbfd working bytes and all new
package hashes are verified. See VALIDATION.md/json for replay and limits.
Actual compiler build, new-test runtime, performance and full CI remain NOT_RUN;
proof credit NONE. Static PASS does not establish future labels/events/checkouts.

Next: coordinator gives this exact committed g0 package to the same reviewer14
for **plan-only delta-review**, with no repeated full source audit. Reviewer closes
F4-R14-1. After approval, coordinator prepares the separately authorized full
standard CI GO request on final exact PR HEAD with all operational gates. The
owner's publication command and CI/accounting GO remain outstanding.

Item1 stays reference 27/28; final 28/28 is unspent, with no reservation. S2r1 GO
awaits its owner and is outside scope. No CI/rerun/cancel/push/PR/publication/label/
event/ledger/reservation/local compiler/verifier/full runner actions, model/fast
changes or subagents occurred. This task reaches its requested committed READY;
there is no implementation blocker and no additional task scope is inferred.

The new g0 identity is the enclosing commit. Resolve it with:
`git log -1 --format=%H -- research/challenge-8/kani-k1/kani3300/wave0/f4-fix-plan-r1/HANDOFF.md`.
