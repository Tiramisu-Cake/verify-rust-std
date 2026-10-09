# NEXT merge Drop/caller checkpoint — SESSION CLOSED / PROFILE NOT_ACCEPTED

Owner `merge`, `/root/verify-rust-std`, branch `overnight/merge-26.10`.
Policy revision read: `1fcd91eff1507fe0bd0620a23b578edb454f1c3e`.
PR #5 merge `cba39579ae561e692d8c5faa61fb40e1b92e63d0` safely integrated by fast-forward; original checkpoint `5eeead52` remains in ancestry. No reset, force-push, whole-main/foreign-branch transfer, runtime-source changes or Actions dispatch.

Actual start **13:27:15 UTC /16:27:15 MSK**, main deadline **14:27:15 UTC /17:27:15 MSK**, absolute finishing deadline **14:57:15 UTC /17:57:15 MSK**, 2026-10-09. Applied owner window **60 minutes + at most 30 minutes finishing only**, overriding the two-hour policy default. New budget 3600 conservative Cloud seconds, no carryover. At minute 46 the decision was to finish the existing step only; no further experiment was started. Checkpoint completed in the main window; extension not used.

Chosen caller: actual `insert_tail`, exact read/initializer at SmallSort 550–551. Mutable `gap_guard` storage is confirmed by actual and fragment MIR; immutable general guard's V4 field/padding halves are a distinct blocker, not an insertion prerequisite. Mutable guard physical fields/padding, immutable tmp complementary fractions/shared source, and the sole CURRENT logical held owner remain separate. Source SHA-256 `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`, blob `40939f922bcb6fdc7ee0d30427fa861827043827`.

Selected transition: conditional quiescent len=1 read/new/shared-source/mutable-guard construction→canonical FBC→literal-one copy/recovery diagnostic. Positive-size unrestricted T; no Freeze/Copy bound, no callback inside this fragment. **No new actual obligation closed.** The fragment removes the Drop impl and immediately copies held→tail; actual insertion first shifts sift→gap and updates dst. It is not a reachable actual Drop edge and cannot establish glue, full normal/unwind insertion, ZST, moving-gap or comparator recovery.

Premises: the diagnostic supplies writable initialized tail, one CURRENT owner, thread/type and tail geometry. Exact `tail.read → ManuallyDrop → &*tmp` is represented at runtime but its proof body was not reached. No entry premise has newly been established by actual caller. First caller debt: first comparator→current tail/sift owners, F/frame and shared-borrow recovery before read. A later arbitrary comparator also prevents reuse of readonly held-state as the full generic insertion invariant; genuine shared borrow/current-value/storage cleanup is needed. This source/spec no-go is separate from inconclusive proof runs.

Fresh runs, separately from replay:

- Build `000add59-443d-4cc6-bc67-cc412e3fc9bd`, exact proof/infra `6d138cd960b04078bbc3432782abe466cbb17c32`: charged 359s. Nine new cases INCONCLUSIVE before proof at AST serializer TODO.
- Build `5fddf20d-a40f-4559-ac7c-c7c304d0ca22`, exact proof/infra `d793eaa25f5cb4de92cda44ba9fc94ea1162d296`: charged 318s. Observational serializer repair worked. All five one-cell cases fail own syntax at 13:5–6 before target body; four MD controls fail unsupported address at 11:38–39 or 11:15–18. No intended-negative, constructor/FBC/copy/recovery or actual Drop credit.
- Both runs retain stock/six V3b full-post constructor positives PASS_FRAGMENT_ONLY, exact false controls and ordinary-call normal/unwind smoke PASS. Both complete archives/external text/identity receipts verified. Collector SUCCESS is not verification acceptance.
- Saved first-run MIR parser replay: five MIR admissions true after nonassignment handling repair; original VF2 cases remain INCONCLUSIVE. No skipped proof upgraded.
- NOT_RUN: unchanged V4, coordinator18, OR17, RESOURCE11, native and the broad historical matrix. Prior V3b supplied-entry CURRENT-pool theorem and geometry bounds retain their exact limits; alignment/intervals, actual Drop, canonical payload post, glue and forget remain open.

[Full case locations, artifacts, tool identities and applicability review](overnight/guard-ownership/insertion-onecell/RESULT.md). Profile `experimental-merge-six-tracked-md-onecell-v1` stays **NOT_ACCEPTED**, including failed MD gates. No missing-half creation, immutable check removal, generic uniqueness, snapshot substitution, disabled leak/unwind/refinement or unverified callee summary.

Cloud: **677/3600 conservative seconds**, 2923 unspent and closed. First setup/build 168s plus MD rebuild 4.64s; second MD rebuild 28.50s and nine-case staged group 5.37s. Remaining setup/control/publication time is not falsely classified as verification. [Ledger](../cloud-build/next-merge-drop-caller/BUDGET.json): both builds terminal/accounted/download verified, active=null. Coordinator own reservation absent, ready request withdrawn; no own active/unresolved Build. Foreign work/state untouched.

First remaining experiment prerequisite: supported own syntax and actual immutable ManuallyDrop local-address admission, with a passing isolated tracked-reference positive and intended authority controls. Recommended next single task: repair that source-linked admission using existing mechanisms and rerun those narrow gates, then mutable construction→FBC only if they pass. Do not promote the quiescent readonly adapter across comparator or treat general immutable guard repair as prerequisite. A semantic address-routing change, if needed, must receive a new scoped rationale/conservation/gate review; no general memory-model rewrite is authorized by this checkpoint.

Session closed; no new work or budget carryover until another owner instruction. This checkpoint commit is documentation/accounting, not a proof run.
