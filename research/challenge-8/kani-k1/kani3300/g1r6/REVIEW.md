# G1R6 independent static review

- Baseline: `8639a651fd5fef812c711ebf62c7ff2bebd7f089`
- Candidate: `cac044742b19d098814d1b76fbe4a8df52d8a824`
- Candidate tree: `b778f2b5f7f28e3ce96ba417edae6c5fa276934a`
- Packet SHA256: `07a9cbf549b0b3e74b90933bcd1ab66829d664859b235c11659d2d5dc7c98ea2`
- Spec SHA256: `e981f1d80b62b65433cfe7a1a78e8a1f5416df4e08fc182bee5d22be9c3a5a41`
- Diff SHA256: `70bfe87243bee99d68deba9da004bc9e8e1bcb59c2f384bb630eaaee5115a830`

## Static result

No concrete static findings in the reviewed delta.

In `codegen_union` (`kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs:1313-1331`), only the storage payload inside the padded arm struct changes for a zero-sized arm; the `UnionField` retains the original logical `ty`, and the padding component still supplies `union_size - ty_size` bits. The GOTO serialization uses the padded storage type, while Kani field lookup/projection retains the logical union field type. This preserves the union extent and the existing logical projection contract. The changed closure uses the existing `codegen_ty_unit` API and introduces no apparent unused binding or new warning hazard by inspection.

The negative padding fixtures now use unions whose listed data arms do not cover the byte immediately before `Padded::word`; the prior four padding failure harnesses/reasons remain in the golden. The additional ZST-array negatives exercise the two codegen variants and expect the uncovered byte read to fail (62 failures total). The two positive `wide: u32` cases cover byte offset 3 and assert the copied padding byte remains `0x5a`, including after by-value identity return (65 successes total). I found no other changed negative expectation indicating a covered-padding read is still incorrectly expected to fail.

The forget fixture now materializes a `[U; 1]` source, performs `ptr::read` into a by-value local, and passes that local to `forget`; the expected golden is unchanged. This is a plausible static way to force the container value through the compiler path while leaving `forget` without an explicit storage effect.

## Limits

No build, compiler, Kani, CBMC, or runtime checks were run, as required. Therefore `-D warnings`, actual CBMC abort elimination, expected harness results, and whether the forget fixture reaches the intended instrumented path remain **NOT_RUN / runtime unknown**. This review grants no proof credit or GO decision.
