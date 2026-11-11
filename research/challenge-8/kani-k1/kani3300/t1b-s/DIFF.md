# Diagnostic delta
Single local Kani commit12b4137c42f3ee92f12476ea0771ea41a5cd1e8d, parent989f72351c2b5c5f3b5117315fc84f502e66d904; no Kani push.
Six compiler files, only opt-in observation changes; kani-compact.patch contains the complete minimal diagnostic diff.
trace.rs replaces textual MIR excerpts with streamed hashes and unchanged-hash deduplication; bounded writer state links a body hash/context to its GOTO consumer. Cap64 entries/320-byte keys, reset each unit.
UninitInstrumenter emits one zero_ops count per body/pass while selected nonzero op payloads, instrumenter order and operations stay intact.
BodyTransformation and DelayedUbPass record changed-body writer/hash; no cache key, mutation, traversal, transformation, analysis-target or semantic op change.
compiler_interface emits final presence after globals/optional second reachability and explicit actual codegen order. function.rs records the body passed to GOTO block emission.
Selected payload filters exclude calibration/adapter MIR/ops; bounded outside-filter cache/origin witnesses retain the existing policy. Calibration verdict controls remain in C.
Combined patch is f046b70644 → final candidate, including unchanged CMP2; applying in a temporary index gives exact expected tree; reversing only compact delta restores989f72351c tree.
No runner/reader/recipe/production repair, flags, checks, source library, controls or active inputs changed. Static invariance tests are not compilation or independent formal proof.
