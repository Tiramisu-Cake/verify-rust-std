# Independent review — initial finding
Reviewer /root/compact_review, GPT-6 Luna HIGH, fresh context, no nested delegation.
Initial candidate184b56181d6fb7db0f91076ade96114ace6e2cc0, baseline989f72351c2b5c5f3b5117315fc84f502e66d904.
Medium: Trace.body_hashes and Trace.last_writers had no per-unit entry cap; output caps did not bound diagnostic memory.
Resolved by64-entry/320-byte-key limits, unit resets and explicit PARTIAL snapshot_state_cap/writer_state_cap omission counters; existing keys can still update.
Same reviewer examined the delta; final exact decision and bindings in REVIEW.md/BINDING.json. Compilation NOT_RUN.
