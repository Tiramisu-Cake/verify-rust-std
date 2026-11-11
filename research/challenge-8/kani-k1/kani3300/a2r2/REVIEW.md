# KANI3300 A2R2 — independent static review

## Identities

- Baseline: `0b1d68ac691cac7e03dbe73f4aec139bb5389059`
- Candidate: `585c93b2ff366f5723611a7ca944328ef62f40b5`
- Candidate tree: `15315ec46854fcb639d8c823a026090ea84a843d`
- Diff SHA256: `0023717c03680a3b5a3c3954af59ea44c9ea6fa893f23fc9280ee0cff3255847`
- Spec SHA256: `512b9ac28c699cdd65b997fdf15d5f3b17986222edc186e39beb6286de724a5e`

## Findings and verdict

No actionable static findings. **Static review PASS** for the stated A2R2 scope.

`RawEq` still derives `[u8; size_of::<T>()]` from each argument's reference pointee layout and queues a `CheckAs` for each operand; this selects the complete extent, including padding and union/`MaybeUninit` storage. For reference `Copy`/`Move` places, `mk_cast` appends `Deref`, forms the pointee address with `AddressOf(Const, ...)`, and only then casts to the byte-array pointer. That follows the ordinary `CheckRef` address construction and avoids a typed read of the reference local. Reference constants have no place and retain the prior direct cast. Non-reference `CheckAs` operands are unchanged. The generated `CheckAs` pointee type is used for the diagnostic, so the uninitialized-byte check identifies `[u8; N]` rather than the outer pointer type.

The delayed-UB `InitialTargetVisitor` continues to seed both original `raw_eq` arguments, so earlier writes to the referenced objects remain in its target set. The new address formation uses `AddressOf`/`PtrToPtr`; the delayed instrumentation visitor skips `AddressOf`/`Ref` rvalues, avoiding an added check of reference storage. The byte-array cast preserves same-size pointee extent. Unknown layout continues to emit `Unsupported`.

The fixture and golden statically retain initialized direct arrays, a reference-parameter call, scalars, storage, and ZST success cases; left and right one-byte holes and struct padding expect uninitialized-read failures with byte-array diagnostics. Harness order/counts are internally consistent (5 expected successes, 3 expected failures). The three `MaybeUninit` fixtures/goldens are not in the candidate diff. Pat/enum logic, the A3 protocol, and raw-pointer-to-reference `CheckAs` call sites are untouched.

Source audit against the pinned `rustc_public` API confirms the used `Ty::is_ref`, `Ty::try_new_array`, `Place.projection`, `ProjectionElem::Deref`, `Rvalue::AddressOf`, and pointer cast forms are available with the required types. The conditional borrows and operand match are consistent with the API. No new import, exhaustive-match, unused-code, or obvious `-D warnings`/clippy issue was found.

## Limits

Static source review only. Compilation, clippy execution, test execution, runtime verification, Cloud/CI, and proof credit are **NOT_RUN / NONE**. Expected golden output is not execution evidence.
