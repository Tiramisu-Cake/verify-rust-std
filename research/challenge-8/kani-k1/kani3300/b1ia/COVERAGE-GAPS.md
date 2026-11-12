# Remaining coverage and compiler-input requirements

The four B1I `compiler_visitor_controls` are preserved verbatim in TEST-MANIFEST.json as **NONEXECUTED_COMPILER_INPUT_SPECIFICATION / NOT_RUN**. They are specifications, not executed tests or PASS. Their historical source-probe notes are superseded by the bindings below.

| Specification / remaining gap | Required minimal next compiler/MIR control |
|---|---|
| `fn-def-resolution-err-empty-entry` | Bodyful nonforeign Item caller, empty entry statements, direct MU formal plus pending pointer operand read. Bind actual FnDef with resolver returning Err (not FnPtr), one target, entry LoadArgument → operand Check → local could-not-resolve Unsupported. Preserve prior seed targets and points-to edges without unwrap. |
| `bodyless-shim-and-llvm` | Bind actual generated/bodyless Shim, LlvmIntrinsic, and bodyless nonforeign Item separately with body=None, pending reads and nonempty prior targets/edges. Confirm local exact kind diagnostic after reads, no body unwrap, retained prior graph/targets. Fn-trait-pointer source controls cover FnPtr only. |
| `bodyful-shim-direct-shadow-argument-only` | Bind actual Shim + Some(MIR), one direct MaybeUninit<u16> argument (not tuple), destination unit, shadow_args=true/shadow_return=false. Confirm exactly one paired-protocol Unsupported before transfer, no BeginArgumentTransfer/StoreArgument/LoadArgument/Move reset attributable to that call. Tuple negatives stop at layout and cannot close this gap. |
| `bodyful-shim-shadow-return-only` | Bind actual Shim + Some(MIR), ordinary nonshadow closure/empty tuple args, MU<u16> destination, shadow_args=false/shadow_return=true. Confirm paired-protocol Unsupported before return0 load and no transfers. Item-return sources do not establish this Shim branch. |

For all controls, capture caller/callee identity, actual kind/body, argument/destination types and ABI, exact source/terminator site and the named JSON properties with statuses. Entry LoadArgument binding must include signature/count/index/size and reached checks. Pending reads must remain present/reached and ordered before Unsupported; a generic FAILED outcome cannot establish this. Test both plain and ordinary-byte-copy seeded cases, measuring initial target set, seed collection, local visitor activation and relevance rather than inferring them from source helpers.

The source Item-return negatives preserve false and reached u16 assume_init failures; initialized companions expect true, reached read SUCCESS and scalar value 7 through the supported Item return0 protocol. All candidate kind/protocol/read bindings remain NOT_RUN. No shim ABI support is added. A further source FnOnce example without actual kind/ABI binding is not a solution to these gaps. Use a minimal coordinator compiler/visitor fixture with exact bindings; this stage builds no framework.

Known raw_eq legal failure and full flat-storage model remain D0/release dependencies under decision B. This package neither modifies that model nor closes Part 1. New unexpected FAIL/ICE or missing required read/load property stops acceptance and requires a separate production-repair task.
