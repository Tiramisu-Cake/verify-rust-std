# Existing automatic GitHub Actions triggers

Cloud Build is the permanent execution provider for SmallSort CI and heavy
checks. GitHub remains the source, branch, pull-request and documentation host.
This inventory records the repository's current automatic Actions triggers;
it does not authorize a manual Actions dispatch, change any workflow file, or
claim these triggers have been disabled. Automatic runs can still occur when
their existing event and filters match.

The SmallSort research workflow, `.github/workflows/smallsort-research.yml`, has
only `workflow_dispatch`; it has no automatic push, pull-request, merge-group
or schedule trigger. Do not dispatch it without a direct owner instruction.

| Workflow | Existing automatic trigger and filter |
| --- | --- |
| `book.yml` | `merge_group`; pull requests targeting `main`; pushes matching `doc/**` or `.github/workflows/book.yml` (no branch filter specified). |
| `flux.yml` | pushes to `main`; pull requests targeting `main`. |
| `goto-transcoder.yml` | `merge_group`; pull requests targeting `main`; pushes matching `library/**`, `.github/workflows/goto-transcoder.yml`, `scripts/run-kani.sh`, or `scripts/run-goto-transcoder.sh` (no branch filter specified). |
| `kani-metrics.yml` | scheduled weekly at `00:00 UTC` Sunday. The job is additionally guarded by `github.repository == 'model-checking/verify-rust-std'`. |
| `kani.yml` | `merge_group`; pull requests targeting `main`; pushes matching `library/**`, `.github/workflows/kani.yml`, or `scripts/run-kani.sh` (no branch filter specified). |
| `kmir.yml` | `merge_group`; pull requests targeting `main`; pushes to `main` matching `.github/workflows/kmir.yml` or `kmir-proofs/**`. |
| `pr_approval.yml` | all `merge_group` events; `pull_request_review` events with type `submitted` or `dismissed` (no branch filter specified). |
| `rapx.yml` | pushes to `main`; pull requests targeting `main`. |
| `rustc.yml` | `merge_group`; pull requests targeting `main`; pushes matching `library/**`, `rust-toolchain.toml`, `.github/workflows/rustc.yml`, or `scripts/check_rustc.sh` (no branch filter specified). |
| `testable-simd-models.yml` | `merge_group`; pull requests targeting `main`; pushes matching `.github/workflows/testable-simd-models.yml` or `testable-simd-models/**` (no branch filter specified). |
| `update-subtree.yml` | scheduled daily at `14:00 UTC`. The job is additionally guarded by `github.repository == 'model-checking/verify-rust-std'`. |
| `verifast-negative.yml` | `merge_group`; pull requests targeting `main`; pushes matching `library/**`, `.github/workflows/verifast.yml`, or `verifast-proofs/**` (no branch filter specified). |
| `verifast.yml` | `merge_group`; pull requests targeting `main`; pushes matching `library/**`, `.github/workflows/verifast.yml`, or `verifast-proofs/**` (no branch filter specified). |

Manual `workflow_dispatch` entries are intentionally omitted from the table:
they are not automatic triggers and remain subject to direct owner authorization
under the permanent execution policy. Do not edit these filters as part of the
Cloud Build migration documentation.
