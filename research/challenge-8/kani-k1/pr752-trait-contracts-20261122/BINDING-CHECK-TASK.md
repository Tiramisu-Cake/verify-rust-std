# Planner task: close the default-fn binding role for #752 trait contracts

Run `45018616243` passed the CI acceptance in [REVIEW.md](REVIEW.md): 16/16 jobs, 245 SmallSort roots per platform including the 10 new `trait_contracts` roots, 0 failures, longest shard 79 min. Details: [RUN-45018616243-SUMMARY.md](RUN-45018616243-SUMMARY.md).

Open role: the organizer log is terse (per-harness aggregate counts only). It does not show that the three `default fn` Checks verify their own `ensures` lowering (native postcondition property, DFCC/frame, unwind, covers), nor callee selection and conditional summary for the Replace roots.

Task (planning and review only, no code edits by you):

1. Decide the cheapest route that closes this role with native, per-property evidence for the same candidate `152f11556a` (tree `08c6c08235`) on pin `9834c96ce9`: the three default-fn roots, plus the opt-in controls K1–K4/W1 under `kani_smallsort_controls` with their expected native outcomes. Options: GCB via k1g.sh (q-pilot style control, 8 GiB lane, budget is the item-2 GCB ceiling) or one fork Actions run; justify the choice by cost and evidence quality. Do not change the candidate tree.
2. Write `BINDING-CHECK-PLAN.md` in this directory: exact roots and flags, expected native outcome per root (which property must be SUCCESS, which control must FAIL and on which property), resource bounds, and the offline acceptance checklist.
3. If a worker implementation is needed (runner/control package), write a worker task file; the coordinator dispatches it.

Out of scope: the push to the PR branch and any public text (owner decision).
