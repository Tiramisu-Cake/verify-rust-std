# Stock-main confirmation request — preparation only

Status: READY_FOR_REVIEW. Native/CI NOT_RUN. Independent review 14 or 11 and a separate coordinator/owner GO are required. This packet grants no publication, dispatch, accounting or reservation.

Compiler: stock upstream main `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`, tree `09b828b47c93e90e140e8c41f9048109a2f4a786`, parent `a3c8b8610739aab7d2c864bd4021086a5e7c0d94`. A separate stock checkout supplies the setup action, compiler build and scripts/cargo-kani. The dependency-free fixture and collector live in the control checkout. Its only changes are this fixture/profile/collector and isolated workflow control; compiler/driver/library/toolchain files are unchanged. `fix-clear-error.patch` remains outside both trees.

Control commit `1253186ae87e079758ab573f50ba305a028f8963`; tree `507f9a07bc6fb4eca26706ea0fde32612731fbe2`; sole parent `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`; local branch `w15/stub-contract-confirm`; unpublished. Canonical request SHA256 `21749d215a2851d971e58f16727d7589af3468adffe086afa4a558cf026841c4`; profile SHA256 `9f230f8fac56230a468f043e294bc77a745b50d5a16a47a7857eb0be4af5cae5`. `CI-REQUEST.json` provides exact inputs, planned argv, environment and bounds; runtime argv/cwd/env and invocation hashes are recorded independently in each process record.

After review and a separate GO, the operator can publish this exact control head and request one `workflow_dispatch` on `Tiramisu-Cake/kani`, `.github/workflows/slow-tests.yml`, ref `w15/stub-contract-confirm`, with inputs:

```json
{
  "control_head": "1253186ae87e079758ab573f50ba305a028f8963",
  "control_tree": "507f9a07bc6fb4eca26706ea0fde32612731fbe2",
  "request_sha256": "21749d215a2851d971e58f16727d7589af3468adffe086afa4a558cf026841c4"
}
```

The existing default-branch workflow file exposes workflow_dispatch (`DISPATCH-ENTRY.json`). The isolated branch replaces that path with the single confirmation job and removes its other workflow files. No default branch, workflow setting or Fast setting was changed. Workflow-registration/state access through the connector was unavailable (INVALID_ARGUMENT on its endpoint); the default-branch file was checked read-only instead. The future authorized operator must use the existing coordinator and verify the dispatch entry is enabled and the remote ref equals the reviewed commit. No alternate trigger, same-tree child, retries or accounting actions are included.

The workflow checks source and request identities, executes the Python service controls, uses stock setup (30-minute cap), builds stock Kani (`cargo build-dev`, 900 seconds), and runs provider, verified and ordinary commands in that order (120 seconds each). Each proof invocation has a separate temporary target and export path. All three are attempted after a successful build, including after a failed target invocation. Overall job cap is 60 minutes, with no automatic retries; native group RSS and per-process address space are capped at 8 GiB. Depth=2 is sufficient because both control and stock have one explicitly checked parent; missing ancestry fails the gate. Deeper checkout contents grant no looser binding.

One uploaded artifact contains only `result.json`, retained seven days. It records setup-action outcome, source/control head/tree/parent, profile/request/file identities, built compiler and resolved native-tool digests, build result, each harness/cfg/argv/cwd/environment, CLI exit/signal, stream and export inventory/digests, bounded diagnostics, per-slot outcomes, classification and canonical payload digest. Rustc error blocks are captured independently from head/tail previews, on both streams; caps/incomplete captures force INCONCLUSIVE. The recorded native exit/signal belongs to each invoked command; compiler-child process hints are retained as rendered data without inventing an unobserved child status. Temporary streams/exports are discarded; raw logs/archives are not uploaded or read through a bypass.

The producer gates successful exports on exact harness selection, target, enabled features and check flags; it cross-checks successful property identities/counts against regular native output and requires the fixture's semantic assertion/postcondition. The exact missing-closure error can be observed without RESULTS/export, but controls must independently verify. `ORACLES.md` distinguishes DEFECT_PRESENT, DEFECT_ABSENT and INCONCLUSIVE, including the separate explicit-unsupported behavior. A missing artifact/collector/setup is INCONCLUSIVE externally; the always-finish step can write a compact partial result when the control checkout and collector are available.

Accounting is reference only: item1 29/30, item2 10/17, total 39/47, including the owner's stated grants. The coordinator owns all records. Nothing was charged, edited, reserved, submitted, rerun or cancelled.
