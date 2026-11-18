# READY for ONE same11 combined W11-01 + new-base delta review

Current15 task09840da5715c0462ee09256930d8487712beebf3,
TASK-KANI-4591-MAIN-REBASE-W15.md. High/FastOFF, zero subagents/model changes.
New immutable directory: kani3300/wave0/issue4591-fix-main-r2/.
The delivery g0 SHA is the commit containing this directory, supplied in the
final handoff without a circular self-pin. Old r1 is preserved, not submitted
as the final CI candidate. W11-01 remains pending independent closure.

| Binding | Exact value |
| --- | --- |
| Frozen r1 g0 | 1d7ef5455f2ea790cd98dde9f38565edb59357ea |
| Frozen r1 source / tree | e6aa083da3c93f3189039077795cc9a0d67d3a6d / 01140856c15e161ff6fc4c1ce460fd4208a298cd |
| Frozen r1 sole parent | faffcee3bca2770c03bd21c3bde89cc8f6f7a14e |
| Original review | 54ea8a918b761dc67213f7f24ae5163b7f463b42 |
| Approved new main / source sole parent | 969f4648980a8e66cd0ca32fd3e714a55ac32cef |
| New main tree | c9a832dc1647c51ac3036429e5f97e73eb717ba7 |
| New main sole parent | faffcee3bca2770c03bd21c3bde89cc8f6f7a14e |
| New worktree | /root/kani-issue4591-fix-main-r2-w15 |
| New branch | fix/ordinary-stub-contracts-4591-main-r2-w15 |
| New source commit | 3a770b5db51ba07acffce3483bde0901e6533f3a |
| New source tree | 7a3d5c05b5d663d515c198b2bfa7c4926ae133ac |
| fix.patch SHA256 | af782bc5473f4b45852ed253aefd929a0ca78746b5fa20452483bdc128cea6cd |
| regression-main.patch SHA256 | ef04091ab11f9af5067fc2d634bd901f013d75f8427bb026334566fb8fd536bd |
| full-main.patch SHA256 | bb4a00fa83852bc67730c3271c2f31fffc673fb2b79d53407fdd37cb37bfeeed |
| CI-REQUEST.json SHA256 | 50da6854da282d718e28ee93953cd5d27c0bf47b366f538248cd5f461b71fdbe |
| Future nonskip final head | NOT_CREATED: same-tree sibling, sole969f parent, exactly one nonskip commit in969f..final |

SOURCE-PINS.json seals every source/test blob and SHA256, new-main protected
files/trees and all16 workflow hashes. REGRESSION-ORACLE.json binds all38 harness
rows and current-main/source identities. MANIFEST.json seals every package file
except itself. The source is a real committed local [skip ci] object authored
Tiramisu-Cake <igkharin@gmail.com>, with exactly new main as sole parent.
It is a fresh isolated main-based candidate; no old history/worktree is rewritten.

The repaired r1 full patch applied cleanly without conflict, resolution or
additional compiler adaptation. Candidate patch content is unchanged after
removing only git index blob headers; upstream old-main..new-main content is
also exactly old-r1..new-source. RANGE-DIFF.txt differs only in commit message.
TRANSFER.json records commands/exits, all31 upstream path identities and both
normalized-delta comparisons. NEWBASE-ANALYSIS.md assesses relevant contracts.rs,
attributes.rs API/feature/type changes and new toolchain/dependencies explicitly.
All accepted upstream updates survive, including Cargo.lock/chrono removal and
library changes; all workflows/scripts/actions retain new-main bytes.

All eight fixture/oracle files remain byte-identical to repaired r1. Each
affected PFC harness directly calls its selected provider in its own body before
the copied f call. Negative provider is identity with ensures result == 0:
direct input0 passes, copied input1 fails that postcondition. Existing bad_contract,
remaining controls, safety assertions and i32 caller-overflow oracle are intact.
W11-01-CLOSURE.md maps the author repair; independent closure is NOT claimed.

VALIDATION.json records bounded static/mutation/mock checks, exact complete
split/full patch replay, new-main invariance and future publication gate cases,
including old-base/source/tree rejection. Restricted lexical checks are not
compiler FnDef/MIR/typechecking or native evidence. All current-main/fixed native,
compiler/cargo/rustc/rustfmt, expansion, Kani/CBMC, verifier/fullrunner, performance
and CI remain NOT_RUN. Old faff MRE/intake stays historical INCONCLUSIVE, with
no current-main credit. A fresh MAIN-CHECK.json observes approved969f exactly.

No CI/push/PR/issues/comments, ledger/reservation/budget action occurred; S3/tool0aac
and open PRs were not touched. Reference budget remains item1 30/31, item2 11/17,
total41/48. Next: same11 ONE combined W11-01 + new-base delta review of these exact
objects; exact APPROVE -> root exact GO -> usercoordinator alone launches one
full standard push-CI bundle (item1 31/31, total42/48). Owner alone publishes PR
or pushes open PR branches. All5 regression OS entries, remaining native jobs,
Format and Deny remain complete; PR-only release/std/bench scope remains deferred.
No custom CI/cron/enable/dispatch or future nonskip object is created here.
