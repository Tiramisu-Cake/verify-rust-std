# Author static audit
Exact prototype: 12b4137c42f3ee92f12476ea0771ea41a5cd1e8d → 94467a24484f1d57315ebbcde7f024dd27576a00.
Only compiler_interface.rs behavior changes; codegen_order.rs changes documentation only. No function/type signature, import, visibility, flag or lint attribute changes.
-D warnings source audit: both introduced mutable locals are used by mutable reference; no new import, dead item, unused argument, lifetime/generic parameter, feature, allowance or warning suppression. This is source inspection, not a compiler -D warnings result.
BodyTransformation::new and its stub/inst pass ordering are unchanged; each constructor receives the same queries/tcx/unit. Both auxiliary maps and pass objects are owned by the new transformer.
GlobalPasses::run_global_passes writes only the supplied root transformer; cloned template passes retained. Reachability before/after globals and GotocCtx share that root transformer.
The root transformer remains in the loop scope until after codegen_items returns and results are consumed. codegen_items finishes synchronous body emission and gcx.split before handing owned FileDataToWrite to export workers.
The ordering transformer is scoped inside the has_workers branch and dropped before root emission; the same heuristic/rating/sort and no-workers path remain.
The unit-scoped trace maps are observers only; last_writer may be stale for unchanged fresh bodies. ACCEPTANCE.md preserves UNKNOWN for an unresolved literal foreign-label criterion.
rustfmt wrapper with --config-path rustfmt.toml and --check: PASS; Kani prototype git diff --check: PASS. Research metadata diff --check excludes exact generated *.patch envelopes (their blank context markers are patch data). Compilation/runtime checks NOT_RUN.
