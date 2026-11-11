# KANI3300 T1b — compile-time diagnostic delta
Base CMP2 `b1f0105c0390fb55081e3d186fa286d23867b585`; diagnostic commit `51848f3fc7c432ae334aa4aa1c0bd607dedbcfc0` (local only, no Kani push).
Production patch bytes unchanged: SHA256 `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`.
Diagnostic patch SHA256 `211a036bc685ef2df5ef1d37b9f25d43d7d48595d08c9e3783d032718bb6dc14`; combined `8bfd47ae78d0ff8a1a9a0b9879719400b15cc463bef11e1fe03e340b6bc55545`.
Static applied tree `a88f60c9559879ed29443d52d8a8013da7bee9c5`; reversing delta restores `d356238999ab436ddc1dd7ffa845b0db214aa53e`.
Nine compiler files: collector, compiler interface/codegen order, transformer cache, initial/delayed targets/relevance, instrumenter.
Opt-in env: KANI3300_TRACE_DIR/FILTER plus request-bound TRACE_ID and fixed TRACE_STAGE.
Opt-out emits no sidecars, performs no diagnostic body queries or additional transformations.
Common unit/root/stub records; actual warmup/codegen chronology precedes cache events.
Separate16-event outside-filter cache witness cap with bounded root/stage/unit context; cache hit/miss, local-pass/DelayedUb writers and streamed body/stage fingerprints from already available bodies.
Instance name + mangled symbol; absent actual IndexRange::len is explicit (inlining/const-fold only possible, cause UNKNOWN).
Initial target location/cast-or-copy reason; resolved get/common-ancestor witnesses; selected, zero and skipped MemoryInitOps.
Op selection order/position/ordinal differs from execution order; selection_only records do not claim executed operations.
MIR: bounded prefix/suffix/selected lines before local passes, after passes, cache return and before/after delayed UB.
Body fingerprint is std-default-hasher-64 over Body::dump, not a cryptographic evidence identity.
Filter literals cover step1/step4, kani_cmp3 adapters, PolymorphicIter and IndexRange len/zero_to; generic Poly filter includes related methods.
Producer <=512 records including header/footer, <=250KiB invocation (task cap256KiB), <=2048B record.
Four lazily claimed slots + singleton overflow marker stay below1MiB/run; no-harness invocations claim none.
Record omissions and payload omission_counts have separate units; PARTIAL/OVERSIZED and incomplete footer are explicit.
Names/arrays bound before JSON values; RecordSink caps streamed serialization before allocation growth; Debug/MIR sinks bounded. IO errors never replace compiler verdict/exits/checks.
Intentionally omitted MIR excerpt bytes/lines are disclosed and can make the trace PARTIAL; no complete CFG claim.
No runtime CBMC projection, symbol/object mapping, new solver/slicing flags, extra transformations or production repair.
Pinned API hashes: API-SOURCES.json; Body::dump/Instance APIs and AsRefStr inspected; MachineSize APIs not added.
Allowed rustfmt wrapper (--edition2024), diff --check and source/license inspection PASS; actual compilation/-D warnings NOT_RUN.
Independent review: REVIEW-KANI.md PASS. Emitted MIR/GOTO equivalence experiment NOT_RUN.
Concrete object/offset/R/runtime causality UNKNOWN; independent B1/B2 proof credit NONE; Cloud $0.
