# Typed hook dispatch boundary

Source audit; candidate native MIR/operation qualification PENDING.

GotocHooks::hook_applies: fn_marker → try_get_kani_function → Hook(hook) immediately
returns kani_lib_hooks[hook].clone(), never calls handler.hook_applies on that branch.
KaniFunction::try_from(Instance) uses the SAME fn_marker/parser. Predicate exclusion
is exact typed Hook(_), not a suffix classifier or second hardcoded list.

Enum ↔ fn_hooks exact equality: 18 unique variants/registrations. Pure unit
`typed_marker_categories_remain_distinct` audits every Hook/Model/Intrinsic and
unknown/loop marker without constructing an unsafe synthetic Instance.

| Canonical marker | Variant | Handler |
| --- | --- | --- |
| AnyRawHook | AnyRaw | Nondet |
| AssertHook | Assert | Assert |
| SliceValidityAssumeHook | SliceValidityAssume | SliceValidityAssume |
| AssumeHook | Assume | Assume |
| CheckHook | Check | Check |
| CoverHook | Cover | Cover |
| ExistsHook | Exists | Exists |
| ForallHook | Forall | Forall |
| FloatToIntInRangeHook | FloatToIntInRange | FloatToIntInRange |
| InitContractsHook | InitContracts | InitContracts |
| IsAllocatedHook | IsAllocated | IsAllocated |
| PanicHook | Panic | Panic |
| PointerObjectHook | PointerObject | PointerObject |
| PointerOffsetHook | PointerOffset | PointerOffset |
| SafetyCheckHook | SafetyCheck | SafetyCheck |
| SafetyCheckNoAssumeHook | SafetyCheckNoAssume | SafetyCheckNoAssume |
| UnsupportedCheckHook | UnsupportedCheck | UnsupportedCheck |
| UntrackedDerefHook | UntrackedDeref | UntrackedDeref |

Separate other_hooks, deliberately outside this correction:
Panic: PanicStub substring/panic lang/name conditions; RustAlloc: exchange_malloc;
MemCmp: core/std slice memcmp; LoopInvariantRegister: kani_register_loop_contract
and possible MIR expression use. PanicStub is a Model, not typed Hook. This fix
is NOT a complete backend interception classifier.

Operation audit: callee-entry loads, caller classification and Return stores all
use has_transfer_protocol. Item/nonforeign/has_body requirements remain. At Call,
super_terminator operand checks precede pairing Unsupported; break 'call skips
return LoadArgument, Begin/Store, snapshots and source deinit, while end-of-terminator
B1 flush remains. No shadow values means no pairing refusal. Ordinary Models,
Intrinsics and unknown markers retain the prior body-domain classification.
These source-derived expectations require bounded candidate MIR/operation confirmation.
