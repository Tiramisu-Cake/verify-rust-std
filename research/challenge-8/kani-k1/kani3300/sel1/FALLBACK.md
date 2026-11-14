# Fallback selection

`kani_middle::has_intrinsic_fallback` is the shared existing predicate `!must_be_overridden && instance.has_body()`. Codegen statement dispatch and reachability use it with their existing intrinsic-instance guards. No new backend result model or intrinsic enum case exists.

`select_unpredictable_fallback` additionally requires InstanceKind::Intrinsic, intrinsic name select_unpredictable, exact definition core::intrinsics::select_unpredictable, monomorphized `(bool,T,T)->T`, non-variadic signature, and actual `checked_body` availability. This preserves #5152 tail-call diagnostics. No other bodyful intrinsic or shim gets a new shadow protocol.

Points-to takes the existing regular-call path on that classifier. It reads selected analysis-body overrides or checked source body through the unchanged B1 mechanism. Source fallback, ordinary alias propagation and local instrumentation must bind the same instance/body at CI; report instance/body/provenance and selected PFC mode. If runtime artifacts establish a mismatch, STOP rather than credit a backend-only model. No measured MIR/body/binary binding has been claimed locally.

Local layout admission additionally requires sized payload and the existing PointeeInfo mask: for_typed_storage for MaybeUninit/flat supported storage, otherwise from_ty, with a sized argument mask. Nested/unsized layouts outside existing masks reject with operator/type-specific Unsupported before protocol effects. Generic unsupported intrinsic paths and can_skip_intrinsic are unchanged.
