# network-bootstrap-2026-10-22-n1 — closeout

T0 2026-10-22T15:07:38Z; main 17:07:38Z; absolute 17:37:38Z. Cloud budget 0:
no Build, request, reservation, phase registration or ledger; GitHub Actions
not used; no local rustc/Cargo/VeriFast/Kani; no OCaml build. Proof credit 0.

## Delivered (all pushed to `challenge-8/networks`)

| Step | Result | Review |
| --- | --- | --- |
| 1 Adoption | policy `9c96a5dd` adopted (`a8a24c34`), branch-local docs archived, ACK | docs |
| 1 Baseline | `cd371e03` merged (`722320d3`, `[skip ci]`); SOURCE-MAP re-pinned to blob `40939f92` after static re-check | static |
| 2 R4 | ghost-only `swap_if_less` generator on Select's pair layer, contract `a_pos != b_pos`, full control matrix incl. reachability | GO_WITH_NITS (reviews 1–4) |
| 2 W7 | ghost-only sort9/sort13 over the in-crate R4 helper, split/join lemmas, controls | GO_WITH_NITS (5–6) |
| 2 P1 | Select A1 source base reproduced by `git apply` (61 steps, translator `b5ea96a1`); admission patch → `c14d8f8a` | GO (7–8) |
| 3 Cloud readiness | v4 coordinator candidate (4 owners, cap 3) + transition + Network client (empty phase table) + runner core | GO_WITH_NITS (1–2, 9–10) |
| notes | W8 obligation map, N13 adapter hypothesis/controls, draft Network profile | docs |

## closure_reason (early end of main, 2026-10-22T16:25Z)

Goal steps 1–3 are done. Each remaining independent mission task was checked:

* R4/W7 proof runs, P1 build: need a Cloud lane and budget — this task grants 0.
* P1 adoption into Select's chain; P2 (checked `select_unpredictable` callee incl.
  `*mut T`): Select's layer/mission (S7). A Network copy is forbidden; requests
  are in `network/r4/SELECT-REQUESTS.md`.
* P3 (equal positions): needs Select's overlay marker grammar decision (request filed).
* W8 caller proof: depends on Merge's published insertion/merge proofs and on W7
  (obligations mapped in `network/W8-OBLIGATIONS.md`).
* N13 exact adapter: a performance question that can only be settled by
  measurement on a lane (`network/N13-ADAPTER-NOTE.md`).
* Network recipe wiring: needs Select's common runner files plus the tool build
  environment, installed with the lane; that is the owner's v4 decision
  (`network/cloud-readiness/PLAN.md`).
* smallsort-session network support: the shared tool's owner, tied to the v4 decision.
