# Future pilot acceptance (not run)
- Exactly the C2 trio in one invocation,1m per root/jobs1, original SUCCESS expectations; same library, filters, flags and ordering algorithm. Observe actual compilation order next → manual → index; request enumeration is not evidence of order.
- cmp3_into_iter_next retains its own necessary CheckRefs, including the IndexRange header checks where observed. PASS with instrumentation disappearing everywhere is rejected.
- cmp3_index_range_len becomes SUCCESS; cmp3_manually_drop_unsized_len and cmp3_into_iter_next remain SUCCESS.
- After each root's own analysis compare local/caller MIR snapshots and actual IndexRange::len goto_body_consumed hash, symbol, dump_ok and last_writer against C2. index/manual must not consume a body written by another root.
- Unchanged trace last_writers is unit-scoped (trace.rs::unit clears it, context does not). Fresh unmodified bodies may retain an old diagnostic label. A foreign label with a mismatched body hash does not establish transfer; preserve the strict no-foreign-last_writer criterion as UNKNOWN unless its actual provenance is independently resolved. Do not silently count it as PASS or change diagnostics in P.
- Missing/partial witnesses, hashes, CheckRefs or order leave the corresponding criterion UNKNOWN. Hashes are noncryptographic observations, not binding or proof credit.
- If index still FAILs, distinguish incomplete isolation from a residual within-root defect without changing ordinary/constant transfer in this pilot.
- Causal pilot only: fresh uninit-positive/negative calibration and native IntoIter/compound/padding regressions are separately required before production acceptance; no such verdict is claimed here.
