# Coordinator proposal: targeted closure-ZST probe (NOT_RUN)

No dispatch authorized by this request. Source 0ad35c0a9345d6dc460ef0f2ed2adea7b76d235b, tree 9863eb935446f0f9423d57daa3d8cbe0d11bf3b1,
parent4f64cc617c, isolated branch fix/kani-3300-closure-zst. Coordinator performs
independent review, final GO/caps/root selection, publication and CI. No worker
push, overlay, build or run. Historical H1 <=10 run grant is exhausted.

Build the exact source in a clean checkout with H1's normal pinned toolchain
nightly-2026-10-23 / x86_64-unknown-linux-gnu, stock CBMC6.11.0 and normal cadical.
Preserve all normal slicing/checks/unwind and property selection; no no-slice,
UF, lower-bits substitution or global-default change. Use existing quick capture;
no new tracing framework or source instrumentation is supplied.

First propose2 singleton roots: exact original research P1 then P2 from manifest,
not annotated suite copies. Match frozen bytes/hashes before each invocation.

```sh
RUSTFLAGS='--edition 2021 -D warnings' kani-driver INPUT --harness ROOT --exact --keep-temps \
  -Z uninit-checks -Z function-contracts -Z unstable-options --output-format=regular --verbose \
  --cbmc-args --object-bits 12
```

`--object-bits` and `12` are separate backend tokens. Every Kani option precedes
consuming --cbmc-args. ROOT/INPUT come from exact_replays, not inferred names.
Then propose16 boundary singleton roots, suite_fixtures excluding the two PFC
copies: unit/align64 legal/hole, scalar/padded, reference/raw legal/hole,
MU value/reference new/uninit, union value/reference. For these ordinary callbacks
omit `-Z function-contracts`; other normal options unchanged. Coordinator fixes
exact list/count before dispatch. No matrix/resource replays or adaptive retries.

Proposed normal per-case caps300s /6291456KiB (6GiB), one solver/process group
at once; initial2 <=600s, optional boundary16 <=4800s, total proposal18 <=5400s
normal case watchdog time. These are proposed caps, not an approved budget or
build/setup/queue allowance. Coordinator separately fixes build/setup/wall caps.
Do not project failing4f64's13s/1.8GiB onto the useful callback/outer assertion
workload: new fit/performance UNKNOWN. Capacity/timeout => inconclusive.

Mandatory bounded receipts, using existing H1/quick interfaces:

- Build source/tree→built Kani compiler/driver/sysroot hashes, actual toolchain,
  CBMC version/hash/solver and final CI identity. Constant source fields alone
  do not establish source→binary binding; never reuse H1's missing build receipt.
- Exact input bytes/root, actual expanded Kani/backend argv and actual spawn GOTO
  hash; retain original Kani/CBMC exits/signals and RSS KiB with watchdog vs
  kernel termination distinguished. Setup/build error means proof NOT_RUN.
- Full bounded inventory (all IDs/classes/descriptions/source/callsites/statuses)
  and completeness flags. H1's316 counts are historical, not a predicted count
  for this head. Preserve local Check and delayed CheckRef separately; STOP for
  count/class drift with exact MIR/source mapping, no oracle deduplication.
- Useful callback read reachability and outer assertion reached/status separately.
  P1 requires useful outer SUCCESS and no unrelated failure. P2 must fail both
  source/read-bound uninit obligations and nothing else; outer may be UNREACHABLE.
- For each boundary root, bounded operation/type/layout evidence for the typed
  `copy_and_call`→ptr::read of closure F. Record full sizedness/size and zero mask
  instantiation (`is_ptr_initialized::<0,F>` or the existing corresponding MIR
  operation if optimized away) versus nonzero closure-specific Unsupported.
  Source syntax/size assertion is insufficient. Earlier aggregate/Cell/union
  failure or absent query => NONDISCRIMINATING, not confirmation of the guard.

Reuse bounded H1 streams (prefix4MiB + final tail1MiB with total count/hash),
property cap20000 and bounded goto/symbol contexts<=200, line<=2048 bytes where
available. Cap/truncation forces UNKNOWN; never accept a partial inventory as
complete. If existing quick cannot expose zero-mask/MIR binding or both checks,
request exactly that missing operation/type/mask/source window and STOP the
qualification. No new unbounded tracing/framework/raw download is authorized.
Apply Evidence Brief restrictions to later reads; preserve unknown admission and
independent proof credit0. No G-SC, source-policy change or full H1 matrix.

New expected Unsupported boundary is not capture functionality. Keep all existing
frame/clause/transfer/false and other controls unchanged. Subsequent general gate
still needs legal-pair/postcondition-hole and R7-C lawful-modifies on compatible
identities; `out` capture may require separate upvar offsets/recursive-mask work.
This handoff does not issue or authorize that next stage.
