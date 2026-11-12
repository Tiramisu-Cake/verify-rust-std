# M2-A coordinator request — six configurations maximum, not dispatch authorization

PREPARED / AWAITING_CI. Worker Cloud $0, no local compiler/verifier, no Actions/Cloud dispatch. Use existing authorized Quick/memprobe only. Exact source hashes, argv arrays and semantic oracles: TEST-MANIFEST.json. Exact M2 tool commit/tree and read-only CI recipe: INPUTS.json. Do not import C1-T2/B3R2 production or baseline commits.

## First inventory, then adaptive solver queue

| ID | Input/root | Mode/task | Semantic oracle |
| --- | --- | --- | --- |
| C01 | Original legal-pair.rs / legal_ordinary_transfer | Exact compiler filter, only-codegen + retained MIR; expected Assert | No semantic verdict; inventory only |
| C02 | Original legal-pair.rs / legal_pfc_transfer | Exact compiler filter, only-codegen + retained MIR; expected SimpleCheck | No semantic verdict; inventory only |
| C03 | cases/ordinary-singleton.rs / legal_ordinary_transfer | Solver, default Assert | All checks/assertions SUCCESS |
| C04 | Same bytes/root as C03 | Solver, no-assert-contracts → Original | All retained checks/assertions SUCCESS; removed clauses earn no credit |
| C05 | cases/undecorated-singleton.rs / legal_ordinary_transfer | Solver, uninit-only | All retained checks/assertions SUCCESS |
| C06 | Same bytes/root as C05 | Solver, uninit + function-contracts | Same expected SUCCESS; no decorated target |

C01/C02 preserve original input bytes; compiler filter must produce exactly one root each despite two attributes in source. Drafts each contain one root. Record both compiler-selected/compiled and solver-selected roots and actual transformed target mode. Stop on zero/multiple roots; `--only-codegen` returns before verify_project, so exit0 alone cannot validate selection. Source declaration order is not codegen order.

Inspect C01/C02 before admitting C03–C06. C03/C04 are the faithful singleton comparison: scalar true/false transfer, MU array3, three writes, body literal equality, out assignment and root equality remain. No semantic body operation was deleted just to obtain a smaller result. C04 isolates Assert wrappers/clauses; C05/C06 distinguish decorated Original from undecorated lowering and the flag alone. If inventories show the failing site cannot be investigated by this queue, mark remaining configurations DEFERRED and return the precise missing field; do not silently expand the matrix or substitute new jobs.

## Supported command surface at the pin

Manifest argv are direct standalone Kani commands for coordinator execution only. `RUSTFLAGS="--edition 2021 -D warnings"` is explicit for every solver invocation. C01/C02 additionally set `--emit=mir` in RUSTFLAGS. Direct CLI does not execute compiletest comments. Use one isolated existing work directory per configuration; no overlapping output/artifact directory or active suite replacement.

Driver args/mod.rs:258–260,284–320,338–341 supports `--harness NAME --exact`, `--no-assert-contracts`, `--only-codegen`; call_single_file.rs:180–186 passes root filter/exact to compiler. codegen_units.rs:88–99,375–395 filters before grouping/codegen. `--crate-name m2a` fixes crate identity. At this pin `kani_middle/mod.rs:36` readable_name strips the local crate prefix before metadata generation (metadata.rs:23), and kani_metadata/harness.rs:149–156 compares that pretty_name exactly. For these crate-root functions use bare `ROOT`, not `m2a::ROOT`; verify metadata against this exact crate-relative name rather than falling back to substring matching.

Omit `--jobs` entirely with output-format=regular: args/mod.rs:557–563 gives NoMultithreading. No autoharness, no parallel CBMC, no check-disabling flags. `--only-codegen --keep-temps` stops before verifier invocation (main.rs:169); it is different from no-codegen. `RUSTFLAGS --emit=mir` is read by call_single_file.rs:298 and DumpMirPass (transform/dump_mir_pass.rs:27–79); resulting `.kani.mir` is the transformed reachable-body view. It may contain dependency bodies; only curated target excerpts/inventories may be returned through the existing reporting interface. No full MIR/global/raw log upload to this worker.

The pin has no dedicated Kani `--show-properties` switch. `--cbmc-args` pass-through exists (args/mod.rs:225–236) but combining it with only-codegen executes no CBMC; do not invent such an inventory command or call it proof. C01/C02 request the existing coordinator non-solving property-inventory path over the emitted singleton model. If that path is unavailable, report PROPERTY_INVENTORY_UNKNOWN and give only the curated source/retained MIR inventory; do not launch a solver to fill the gap. Any backend/tool option beyond the manifest must be source/version-validated by coordinator and recorded in actual argv.

## Resource admission and result receipt

One compiler root and one solver at a time, configurations sequential, no full Quick/heavy-selector repeat. Proposed first solver batch cap: ≤180s elapsed and ≤6GiB RSS per process and runner; desired tiny semantic outcome about ≤60s/≤2GiB. These are proposals, not claimed enforcement. Existing memprobe uses external timeout1200 and job120min, no RSS cap. Coordinator must record an applicable existing enforcement before C03; if no compatible existing limit exists, return RESOURCE_GATE_UNRESOLVED and defer solver jobs. No new runner/watchdog/trace framework; RLIMIT_AS/ulimit virtual memory is not RSS. Inherited memprobe loop is not an approved cap. Preserve original exits through any output filtering; its grep pipeline status is not the Kani exit.

For each receipt preserve exact source/tool/tree/sysroot/compiler/CBMC identities, actual expanded argv/env (nonsecret fields only), cwd, stage exits/signals, root selection, actual mode/wrapper, selected solver (pin default CaDiCaL; installed identity UNKNOWN), bounds/defaults, all check settings, reachability, elapsed and raw RSS units/method. Distinguish per-process vs process-tree peak and concurrency. Report program/VCC sizes when available, otherwise UNKNOWN. A new matched input/model/config baseline is required before resource improvement claims; old combined-pair 15GB run is not a matched singleton baseline. A solver cutoff/OOM/timeout/killed runner is RESOURCE_INCOMPLETE, not semantic PASS/FAIL. Setup failure leaves solver NOT_RUN.

C01/C02 first return six site rows with BOTH operands as specified in SITE-MAP.md, actual CheckAs/property IDs/classes/locations and completeness/coverage. Request retained reset/seed/normal setters, generated copies and false source-following path only where available; runtime object/witness fields stay UNKNOWN without observed execution. A next diagnostic may target an established property with existing supported options, with no full-harness proof credit. Do not restart the original 15GB solver without a separate coordinator decision.

## Deferred, no automatic execution

`scalar-pfc-legal.rs` and `scalar-pfc-hole.rs` are genuine PFC calibration companions, with useful u8 ensures and unread valid MU in the root; no arrays/heap. Hole is byte-identical to original postcondition-hole: it is already scalar, so array removal cannot explain its reported OOM. They are DEFERRED, not seventh/eighth configurations. A later bounded legal/hole comparison requires its own admitted request after site/mode findings. Array-only/scalar-only/modifies-only ensures reductions, no-assert-contracts PFC and restored established array trigger are also DEFERRED. No broad Cartesian matrix.

Original out-pointer all-failure/endpoint/middle-hole binding and abort true/false CFG qualification need targeted existing curated observations, not additional jobs in this six-config queue. Missing exact IDs/traces/memory/receipt fields remain UNKNOWN. Use the authorized evidence interface; no raw archives/full logs/credentials, old D0 exception, workflow edits or deployment. M3 remains HELD until actual original legal/PFC/postcondition qualification and accepted resource decision.
