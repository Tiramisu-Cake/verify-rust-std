# SEL1-C2 transfer ownership

Source `14bc57fdb99960240c4944845a3d985c8af4dcf7`, parent exact final C2 `8e299aa624`.
Static source review only; new runtime outcomes NOT_RUN.

| Operation / source | Owner and invariant |
| --- | --- |
| Codegen statement:928 / reachability:285 | Shared `has_intrinsic_fallback`: no required override and actual fallback body. Select classification additionally requires Intrinsic kind, exact core::intrinsics definition path, name, checked body, nonvariadic `(bool,T,T)->T`. |
| Visitor call:617–646 | `super_terminator` runs first; resolution and select validation precede call-specific Begin/Store/Load/deinit. Type/count/result mismatch produces Unsupported, retaining B1 pending operations and final flush. |
| Visitor validation:185–208 | Sized layout, existing typed storage mask (including false padding) or ordinary PointeeInfo, and complete `argument_size` required before select transfer. No new layout model. |
| Caller helper:210–241 | Begin with actual monomorphized `instance.ty()`. Both shadow arms get snapshots at original indices 2 and 3, count2; bool never transfers shadow. All Stores precede ANY Move SetRef(false), including the unselected arm. Copy remains live. |
| Callee entry:68–111 | Same real instance signature/count/indices. Entry exception allows only validated select. Existing sized/paired refusal remains for other domains. |
| Fallback assignments | Existing AssignUnion/typed-storage operations carry the chosen arm's true/false payload mask; padding uses C2 masks. This body is the only owner of selected shadow state, no initializedness union or extra backend copy/bless. |
| Callee normal Return:921–940 | Existing mandatory StoreArgument index0 for shadow results, extended only to valid select; same function Ty identity. |
| Caller normal continuation:676–682 | Existing index0 LoadArgument After replaces destination state. After a Call is its normal edge; unwind/abort gets no load. Current insertion machinery is byte-identical to C2. |
| Points-to intrinsic arm:373–384 | Follow the real regular fallback through current selected-body/active-call machinery. No separate select alias summary. |
| Points-to regular-call helper:620–731 | Formal slots point to caller operand referents via successors_for_operand. Fallback assignments join both arm referents, return0 successors connect to destination. Bool has no referent edge; caller-slot addresses are not substituted. Selecting a pointer reads/blesses no pointee. |
| C2 F6 reset | Both reset helpers unchanged; ordinary/foreign/shim/BlackBox paths retain their existing calls. Paired argument snapshots precede nested Move reset. Valid select nested layouts are rejected before this protocol. |
| Hooks / foreign / shims / other intrinsics | C2 Item predicate retains nonforeign/body/!Hook conjunction. Select's exact intrinsic classifier is the only added disjunct. Nonselect intrinsic Unsupported, bodyless and B1 boundaries remain. |
| DelayedUbPass / F7 | No diff in the pass or cache/scope files. Instrumented bodies and failed-root diagnostics both use `replace_delayed_body`; existing journal/restore boundaries retained. |

All runtime buffers, DFCC/private assigns, typed-mask implementations, immutable/F5
registry and closure-layout implementation remain byte-identical to C2. The original
S3/CC, mode/Replace/Recursive/hook/mixed-root tests are unchanged. New controls and
their intended outcomes are in `CONTROL-MAP.{md,json}`. Absent/overridden fallback
and unsized T have static guards only; the Nested fixture stops at an earlier
general UnionAsField check and gives no select-specific refusal execution credit.
