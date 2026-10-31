# WRAP-N2 source review

Main agent owns integration and validation. A bounded Luna High read-only reviewer checked
wrap.rs, registration, task constraints and relevant dispatch/runtime bodies; no nested agents.
No discovered correctness/dispatch issue. Review is source inspection, not Kani acceptance.

Confirmed: Cell selects stable blanket fallback; u8 selects Copy/Freeze network (N2 insertion);
NonCopyU8 selects default Freeze general. General scratch initializes its two live singleton
halves before merge reads, writes output into v and forgets the panic copy-back guard on success.
Full-value count uses independent shared byte witness, scalar old and typed projections; key is
>>1. XOR1 control preserves key but has a count counterexample. No summary/leaf/panic stub used.

Final Stable scratch delta rechecked: backing[2] is initialized/uninitialized, exposed len0..2.
Only initialized slot0 is read before/after; slot1 is passed as MaybeUninit and ignored by the
Cell stable fallback. Empty and uninit-tail covers added. No finding in the final delta.

Compilation, instrumentation, PFC acceptance, native covers, checks, VT/RSS and exact runtime
failure locations remain NOT_RUN until the coordinator authorizes G1.

Main-agent final adjustment: pair_region takes a shared slice and only queries read/write
predicates through raw pointers; it never writes or requires a mutable specification capture.

## G2 delta review after G1 COMPILE_ERROR

G1 supplied no compile/PFC credit: E0502 at all three scalar old-count clauses on &mut inputs.
The same Luna High reviewer separately inspected the G2 raw-pair transformation and exact
scratch nonoverlap arithmetic. No explicit safety, arithmetic, N2-domain, oracle or frame issue
was found. offset_from is reached only with live nonempty regions in the same allocation;
the negative-distance unsigned magnitude comparison preserves scratch-before-input geometry.
Each wrapper constructs exactly two initialized writable elements after its canonical guard,
and pair_count still captures a scalar through the same full-value checker. The PFC backing,
probe, comparator, controls, outside frame checks and covers retain their original domains.
Compile success, E0502 removal on the pin and all proofs/control outcomes remain NOT_RUN.
