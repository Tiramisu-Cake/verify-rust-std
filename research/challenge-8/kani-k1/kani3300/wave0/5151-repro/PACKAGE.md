# Kani #5151: initialized array element and drop

`RUSTFLAGS="--edition 2021" kani -Z uninit-checks --harness drop_initialized_slot --exact initialized-slot.rs`
checks dropping an initialized `D` in a two-element `MaybeUninit<D>` array whose
other element remains uninitialized. The prepared comparison uses stock Kani
`0aac16ef62da9e9d5645782d458593e5d78143ba` and prototype
`8e299aa6243bc5f06a29c51e98aafa9564478220` (tree
`9829702c1aa0ecb73c860fc0ad5451757917d6cb`).

The task specifies dropping element 0. The [issue reproducer](https://github.com/model-checking/kani/issues/5151)
drops element 1 after writing element 0. Both cases are retained, together with
a destructor that reads its byte to give a concrete uninitialized-read control.
The issue's code block, including its element-1 comment, is preserved in
`tests/expected/uninit/issue-5151/original-empty-drop.rs` after the test header.

## Expectations declared before execution

| Test | Stock | Prototype | Acceptance |
| --- | --- | --- | --- |
| `initialized-slot.rs` | Union/MaybeUninit unsupported check | Successful verification | Required |
| `original-empty-drop.rs` | Union/MaybeUninit unsupported check | Completed verification with supported checks | Diagnostic: retain successful result or actual uninitialized-read failure |
| `read-in-drop.rs` | Union/MaybeUninit unsupported check | Failure on reading uninitialized memory | Required negative control |

For the empty destructor, a successful result records which checks Kani
performed. Detection of the invalid drop remains open in that case. The
read-in-drop control performs an actual byte read and requires its memory
initialization failure. Unsupported checks, compilation errors, panics,
unrelated assertion failures, timeouts and incomplete output remain separate
outcomes. The prototype support comparison succeeds when the initialized test
passes, the byte-read control fails for the specified reason, and the original
case reaches completed verification without unsupported checks. A stronger
claim about the original invalid drop requires its own failing property.

Both tools pin `nightly-2026-10-23`, CBMC `6.11.0`, and Kissat `4.0.1`.
The comparison uses the standard library shipped with that nightly. Part 1
uses standalone files and requires no verify-rust-std checkout.

Each fixture declares `// compile-flags: --edition 2021`, as used by upstream
`tests/expected/panic/arg-error/test.rs`. Compiletest parses that directive in
`tools/compiletest/src/header.rs` and passes it through `RUSTFLAGS` in
`tools/compiletest/src/runtest.rs::run_kani`. The standalone driver forwards
`RUSTFLAGS` to rustc in `kani-driver/src/call_single_file.rs`. The regression
script supplies no default edition. The control runner applies the same
compiler flags to every standalone invocation and records them with each row.
The original issue body remains byte-identical after the test header.

For [run 43878900159](https://github.com/Tiramisu-Cake/kani/actions/runs/43878900159),
trigger `dbfb4d8bd8`, the owner reports six UNKNOWN rows caused by E0433 at the
`core` import under edition 2015. The corrected candidate remains unexecuted.
The added Python tests check the subprocess edition environment, matching
headers, rejection of a missing edition, and E0433 classification as UNKNOWN.

## Execution envelope and artifacts

The control workflow prepares two jobs in one serial matrix, on Ubuntu 24.04,
with three isolated exact-harness invocations per tool. Each job has a
55-minute envelope; its build cap is 1,800 seconds and each invocation has
60 seconds. The combined verifier allowance is six minutes across both tools;
the full reserved envelope is 110 runner-minutes. These are proposed caps;
runtime has not been measured. Setup, build or analysis can exhaust a cap.

Artifacts retain request and source identities, tool commit/tree before and
after execution, command and working directory, original process exit,
bounded output, structured results, and explicit incomplete/unstarted states.
The detailed file inventory and exact caps are in `CI-REQUEST.json`.

`CHALLENGE2.md` describes the separately gated #649 inventory and proposed
partitioning. Its historical 77 count comes from the maintainer's comment;
static candidates and measured failing harnesses have distinct status.

Runtime: **NOT_RUN**. This preparation has zero pushes, CI submissions,
publications, ledger writes and local Rust/Kani/CBMC invocations.
