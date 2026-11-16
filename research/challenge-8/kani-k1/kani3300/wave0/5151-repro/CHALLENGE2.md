# Challenge 2: source inventory and future measurement

The [maintainer's comment](https://github.com/model-checking/kani/issues/5151#issuecomment-6844432557)
reports 394 `intrinsics::verify` harnesses at Kani `c5e65fd`, with 91 unsupported
results: 58 array buffers, 19 `PointerGenerator` buffers, and 14 trait-object
pointers. It supplies aggregate counts and example diagnostics. The names of
the historical 77 failing harnesses require a source/result mapping.

## Version compatibility

The pinned [PR #649 source](https://github.com/model-checking/verify-rust-std/tree/ee550687f489ee864e27c107c5b4b101df3e2a85)
has head `ee550687f489ee864e27c107c5b4b101df3e2a85`. Its
`tool_config/kani-version.toml` selects
`c5e65fdfc3e15ec32293f2a4c07509aebec033c9`; its `rust-toolchain.toml` selects
`nightly-2026-10-23`. That Kani commit is an ancestor of stock `0aac16ef62`.
Stock and the prototype use the same nightly. The standard library source for
this part is the #649 tree, while the standalone part uses the tool's nightly
sysroot. Source compatibility has passed the version-pin check; compilation
and complete API compatibility remain untested.

## Static candidates

`challenge2-candidates.csv` identifies 56 source-inferred candidates: 37 with
explicit array buffers and 19 with direct or transitive `PointerGenerator`
use. Each row names the fully qualified harness, family and absolute source
line. All 56 name anchors were checked against the pinned source. The
PointerGenerator count matches the comment's 19; that numerical match leaves
the historical result-to-name binding unconfirmed. The 21 remaining array
cases in the reported 58 are unresolved.

`challenge2-static-harnesses.csv` contains a best-effort expansion of 393 source
IDs. This is one short of the reported 394. Conditional compilation, macro
expansion and runtime selection require compiler-backed inventory before
using this as an execution list. `CHALLENGE2-SOURCES.json` records exact
source and inventory hashes, pins and assurance.

The pinned `scripts/run-kani.sh` obtains canonical names with
`kani list $unstable_args ./library --std --format json`, combining standard
and contract harnesses. It runs selected names using
`kani verify-std -Z unstable-options ./library --no-assert-contracts --harness <id> --exact`
with the same project feature flags. The runner's `--kani-args` option adds
`-Z uninit-checks`. Its project flags are `function-contracts`, `mem-predicates`,
`float-lib`, `c-ffi`, `loop-contracts`, `quantifiers` and `stubbing`, each enabled
with `-Z`. These are future commands; they were read as source data.

## Proposed sequence and budget

1. Preserve the #649 source and compile/list all `core::intrinsics::verify`
   analysis targets with the pinned tool and required project flags. Store
   exact fully qualified names, source locations and inventory hashes.
2. Reconcile the static candidates against that inventory. Historical failing
   names become confirmed only with corresponding original per-harness results
   or a new baseline classification. Keep original and newly measured counts
   in separate fields.
3. Run a calibration of eight candidates, covering both buffer families and
   several intrinsics. Record setup/compile time, individual verification time,
   peak process-group RSS and completion status. Preserve failures and
   unsupported checks as diagnostic outcomes.
4. If 77 candidates are confirmed, partition stable sorted names as
   20/20/20/17, serially at first. Use a reusable compiled target only when
   source/tool/config identities match. Retain every selected harness.

Runtime and RSS for these 77 cases are **UNKNOWN**. A proposed 300-second
per-harness cap gives 23,100 seconds (6 h 25 min) of verifier allowance before
compilation and upload. This is an envelope, not an elapsed-time estimate.
Each 20-case partition can require 100 minutes of verifier allowance. A single
55-minute part-1 job cannot reserve that full envelope. Calibration should
determine whether smaller caps or more partitions are appropriate.

Part 2 is an inventory and execution proposal in this package. The workflow
executes part 1. Enabling #649 verification requires a separately authorized
stage with a confirmed target inventory and measured compilation envelope.
The current task's prohibition on local Rust/Kani/CBMC and CI execution leaves
these runtime measurements pending. An incompatibility STOP has not been
established by the source checks.
