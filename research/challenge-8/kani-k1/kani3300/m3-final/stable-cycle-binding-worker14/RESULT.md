# Worker14 — stable CC4 diagnostics and partial r3 binding

READY `3912b8e0319754f43bbcd7f2b363ad5cbf0a80c9` in `/root/kani-fix-3300-worker14`, two new commits directly on `ada5c7bd44ee33a9c9e229cc5c35bcd32464d0fb`:
`585768eb1` stabilizes the CC4 diagnostic/docs/oracles;
`3912b8e03` binds the six unaffected roots.

Cycle path frames now use `readable_name` (Instance::name with the local crate
prefix trimmed), explicit source/registration-override/discarded-closure-override
provenance, a readable registration origin, and call `file:line`. Internal Debug
Instance/AnalysisKey/DefId and mangled symbols are absent from user text. Exact
Instance/provenance equality still detects cycles; errors still latch and prevent
partial summary export. Bounds remain 12 frames and 4096 characters per frame,
with the existing omission/truncation markers. Frame numbers are path positions.
All five cycle `.expected` files and the mode-boundary oracle now check the new
format. The oracle rejects old Debug identity text; exact failure/Unsupported
comparison and the narrow T1b allowance are unchanged.

The nested aggregate limitation keeps its general explanation and false-positive
warning without test filenames or harness names.

`AUDIT-R3.py` revalidates all 11 explicitly supplied local invocations from capture
run `43504302188`: input/output/export/receipt hashes, schema/process/root metadata,
full isolated and mixed observations, and all recorded comparisons. It makes no
verifier calls and leaves original evidence untouched. Actual capture statistics:
18 comparisons, 17 accepted = **11 exact + 6 T1b**, one rejection
`cycle_root/all_A_then_B`. The prompt's 10 exact / 7 T1b split differs from the
saved capture. No cycle-description normalization or acceptance was introduced.

Six exact isolated inventories (including failure kind, complete failures,
Unsupported, check and cover inventories) are now `REGRESSION_BOUND` in
`roots.json`, with capture provenance/digest. `cycle_root` remains
`BINDING_PENDING`, its inventory fields null and its required new-text schema
recorded in `binding_pending_reason`. We do not invent a runtime inventory for
the new message. Ordinary regression remains blocked by that pending root;
the next authorized capture/review must supply its exact inventory. Producer
order remains `ORDER_UNCONTROLLED`, with no order or independent proof credit.

Validation: **87 Python synthetic tests pass** (19 mode boundary, 41 composition,
6 binding, 21 strong oracle); these include timeout/process/schema error paths,
exact failure and Unsupported drift, the pending cycle guard, stable message
recognition, and the T1b limit. Rustfmt parse/format check passes using the
pre-existing standalone rustfmt 1.11 nightly (2026-09-28); diff and frozen-input
checks pass. Added Rust unit coverage checks stable Display across opaque-ID
changes and keeps distinct exact keys separate; Rust unit tests/typechecking
were **NOT_RUN**. No cargo, Kani, CBMC, CI dispatch, amend or push performed.
The compiler diagnostic change still requires the next runtime capture.
