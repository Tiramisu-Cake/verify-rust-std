# G1: future execution sequence

2026-10-11. **NOT_RUN / NO CURRENT EXECUTION AUTHORIZATION.** Cloud budget 0, no registration. Inputs/acceptance: [G1-CLOUD-PREPARATION](G1-CLOUD-PREPARATION.md). Future execution contract, not executable recipe; no G2.

## Before a Cloud session

1. Owner reviews exact-core route/frontend-only scope and deferral of foundational Rocq replay. Separately authorize implementation of own harness, image setup and minimal dispatcher-compatible registration. This task implemented none.
2. Freeze published proof/harness SHA, infra SHA/client bytes, recipe closure, unpatched RR profile, OCI digest and all source/compiler/component pins. Publish exact commands, fixture bodies, ghost-strip certificate and expected failure locations; statically confirm registration/callee paths/dumps/Cargo closure. No unknown SHA/mutable tag at dispatch.
3. Audit existing image receipts read-only; reuse only exact closure match. Otherwise separately authorize one cold frontend-image attempt: timeout/reservation 1740/1800 s, same stable owner, own setup phase/ledger, reviewed build recipe and image repository permission. Freeze OS/archive/crate hashes/result digest. Failure/timeout closes setup, no retry/admission from partial image. No Rocq compilation.
4. Owner grants admission window, stable owner refinedrust-feasibility, exact phase/lane, own absolute ledger/state, allowed recipe/profile and 1260 s ceiling. Review proposed machine/disk/config. Client registration must accept identity and preserve v2 two-slot limit. Incompatibility/refusal STOP; never bypass. Preparation continuation grants none of these permissions.

## One warm admission Build

Submit only with reviewed existing control.py semantics from [Cloud runbook](../cloud-build/README.md): explicit project/configuration smallsort-ci, account smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com, global Build API. Own owner/phase/ledger/state, exact infra/proof SHAs, pinned-objects, --no-source. No runnable command with unassigned SHAs. Poll returned Build ID/token; uncertain submission retains slot until exact reconciliation, no duplicate submit.

| Order | Action/evidence | Stage allocation / decision |
| --- | --- | --- |
| 1 | Restore/validate pinned recipe, source/ghost-strip, image/toolchain versions, config/environment/target/resources | 90 s; mismatch STOP before compiler |
| 2 | Independent P0 and N1 frontend fixtures; saved-certificate N2 rejection | 90 s; unexpected control failure INCONCLUSIVE, stop target |
| 3 | Native Cargo check exact core on RR nightly with frozen target/features/panic mode; complete invocation/errors | 240 s; incompatibility/direct-core build failure STOP; no source/compiler substitution |
| 4 | RR translation ghost-annotated exact core/callee closure; record selected/missing DefIds, glue/output | 540 s; selected unsupported operation or missing target binding STOP; unrelated registration/spec failure INCONCLUSIVE |
| 5 | Inspect source→MIR→Radium, early/late unwind, normal Drop, payload suppression and resource forms | 90 s; missing correspondence fails acceptance; ownership remains unproved |
| 6 | Archive full logs/output/hashes/config/certificates, upload receipt, independent verdict | 70 s reserved for packaging/upload; incomplete evidence INCONCLUSIVE |

Stages 1–5 sum to 1050 s; stage 6 uses the existing 70 s packaging/upload reserve. Inspected dispatcher computes work_seconds=timeout-70 and lane deadline roughly 15 s earlier, yielding 1115 s work allowance for timeout 1200. Thus 1050 s leaves 65 s internal margin and respects the wrapper; total stage caps 1120 s, with remaining 80 s conservatively left for wrapper overhead/margin. No retry allowance. Stage caps are scheduling proposals, not benchmarks. Future runner must preserve this reserve and collect failure artifacts before outer timeout; freeze matching watchdog values in infra review. Hard timeout 1200 s, reservation 1260 s (+60 s queue envelope). Actual charge ceil(createTime→finishTime) includes queue/setup/upload; execution duration separate. Queue/setup overrun requires reconciliation/checkpoint, no second build. Session/lane/deadline may impose stricter stop.

## Interpretation and closure

- **PASS admission:** intended controls, actual generic helper/guard/wrapper/glue bodies, exact source/callee/cleanup correspondence and complete evidence. Inventory shim/spec boundaries and unproved CURRENT/borrow/shape obligations. Verification accepted/full safety remain false/NOT_RUN.
- **INCONCLUSIVE:** environment/resources, missing artifact, unrelated registration/spec failure or blockage before observing selected target. Name first causal stage/symbol/span; distinguish unobserved from rejected. No unintended-negative credit.
- **STOP:** exact compiler/source incompatibility, unsupported selected operation, missing cleanup or need for semantic patch/generic restrictions. A missing selected ordinary callee binding is STOP / LIBRARY-SPEC, distinct from unsupported semantics. Preserve first failure and return decision to owner. No no-panic/purity/Copy/Freeze, assumed owner bridge, sysroot substitution or erased checks to obtain PASS.

After terminal API state download only own evidence to fresh directory, validate archive/inventory/receipt and ordered chunks, reconcile own ledger/token/slot using client; record actual charge. Prefix remains gs://smallsort-ci-evidence-504462351565/cloud-build/BUILD_ID/. Cloud SUCCESS is not admission PASS. Generated source/logs/output stay outside Git. Update own STATUS and future experiment record with exact identities/result; no peer/coordinator edits.

Minimal justified request: **one warm admission attempt, at most 1260 ledger seconds**, after environment freeze. With no confirmed image, **1800 s cold setup cap is a separate risk-limited proposal**, not a completion forecast. At most one cold and one warm, sequential; separate explicit budgets/session. OOM/timeout grants no enlargement/retry/G2. No build, proof, lane implementation/registration occurred in preparation.

After closure report evidence/verdict/blocker/spent-retired budget and potential next decision, then stop. G2, CI integration, migration and Tool Application remain outside scope.
