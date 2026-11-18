# Final-head fork push CI intake

Disposition: **FORK_PUSH_CI_PARTIAL_INFRASTRUCTURE**. All three workflows are terminal, attempt 1, push, exact final head/ref MATCH. All 12 expected jobs are accounted for in RESULT.json and the complete bounded job/step summaries in PROVENANCE.json.

| Workflow | Native outcome | Intake disposition |
| --- | --- | --- |
| Kani CI 44274306776 | FAILURE | Eight jobs SUCCESS; regression (macos-15) CANCELLED, INFRASTRUCTURE_NO_RUNNER / NOT_RUN |
| Format 44274306711 | SUCCESS | Format and Clippy SUCCESS; C formatting has continue-on-error but itself succeeded |
| Deny 44274306733 | FAILURE | EXTERNAL_ADVISORY, f4_blocking=false by coordinator/owner decision |

Successful Kani jobs: regression on ubuntu-22.04, ubuntu-24.04, ubuntu-24.04-arm and macos-15-intel; benchcomp-tests, perf, LLBC and documentation. Documentation publication alone was correctly SKIPPED by its main-branch condition. macos-15 had runner_id=0, empty runner_name and zero steps. The coordinator supplies the hosted-runner non-acquisition message; the owner chose NO_RERUN and upstream PR coverage. Five-OS coverage remains incomplete.

The first failed step is Deny's Run EmbarkStudios/cargo-deny-action@v2 (step 4). The coordinator reports RUSTSEC-2026-0543, chrono unmaintained, and `advisories FAILED: 1 errors`, and accepts it as external. The reported last-green upstream-main timeline is coordinator provenance, without independent log/advisory-date validation. Parent/head Cargo.lock bytes independently match. This acceptance preserves native FAILURE.

The prior main confirmation observed the initialized harness succeeding alone and failing paired in both cfg variants. Frozen candidate source registers delayed-shared-body in the standard script-based-pre suite and checks initialized success, intended unsafe failures and singleton/paired signature equality in both feature call paths. All executed native regression steps succeeded. The coordinator reports ubuntu-24.04 script-based-pre **103/103**; this count is not independently exposed by the connected summaries. Named fixture runtime output, per-harness property inventories, measured checkout SHA, actual compilation order and cache causality remain UNKNOWN. Source expectations are kept separate from observed runtime results.

The full perf job/step succeeded; individual measurements, ratios and internal retries are UNKNOWN. Release bundle instances, std verification and labeled compiler/end-to-end comparisons remain DEFERRED_TO_UPSTREAM_PR; extra_jobs is PR metadata-only. No fork PR merge tree was used.

Draft ready for owner review; CI readiness is partial. No CI, push, PR, rerun, source or ledger action was taken. Missing details are enumerated in RESULT.json; no new run is requested.
