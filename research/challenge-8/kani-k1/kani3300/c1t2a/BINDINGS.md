# C1-T2-A source and evidence bindings

All CI facts here are coordinator reports from TASK-KANI3300-C1T2A/user, not independently inspected property reports. INPUTS records locally verified full Git identities, trees and 30 source/golden hashes. Git contents establish source availability, not actual selected CI input, MIR, executable identity or a reached check. OBSERVATIONS has 6 C1-T + 8 mixed + 2 D0 harness rows without attributing aggregate verdicts to unknown properties.

## Old inputs

Baseline 43225818126: expected 125/9; eight mixed plus known maybe-uninit-initialized fail. M1 43225812282: unit 5/0, expected 134/4; only four MU fail. Four u8 cases distinguish the reported models: raw-u8 fails in its harness and eq-u8 in SpecArrayEq<u8,3>::spec_eq at equality.rs:157, with `[u8; 3]` uninitialized-read descriptions; all four match legal SUCCESS goldens on M1. Exact property IDs, operand/witness, masks and extra baseline failures are unavailable. The reported specialization is stronger than syntax, but does not establish the full source-mask/reset/runtime bridge.

Both old lanes' four MU cases stop at the sole reported layout Unsupported for `MaybeUninit<[MaybeUninit<u8>;3]>`, maybe_uninit.rs:430, before intended raw_eq. Their intended P read and lawful S check are CHECK_NOT_REACHED (reported), not payload failures or mask measurements. Exact constructor call/MIR location remains unavailable. They do not qualify immutable None preservation.

Six old C1-T historically matched baseline/M1 goldens; their new-pair per-case reports are not supplied. SUCCESS does not explain origins or initialization. Actual Stack/Aggregate/GlobalAlloc::Memory/Static, retained CheckAs/get, relevance/phase/reset/setter/seed/copy remain UNKNOWN. A source reference/const or missing artifact cannot settle those questions. D0 [u8;4] is mandatory and unchanged; a containing-test aggregate does not bind either D0 harness/property.

## Repair source contract

In exactly four raw-mu sources, S is now a mutable `[MaybeUninit<u8>;3]` initialized as three valid uninitialized MU elements, followed by the same raw byte writes 7,0,9. Array `as_mut_ptr()` points to the first MU element; casting to u8 exposes its one-byte storage. All writes are in the three-byte extent, precede borrowing `&storage`, and finish before raw_eq. No outer MU as_mut_ptr/assume_init or moved assume_init temporary remains. The reference is to MU storage; no typed `[u8;3]` hole reference is constructed.

P const definitions and borrow construction, operand order, intrinsic, assertions/unused results and all goldens are byte-preserved. Legal requires S/P masks [true,true,true], both reached read checks SUCCESS and equality true. P-left hole remains offset0 ([false,true,true]); P-right remains offset2 ([true,true,false]); S must succeed and only the intended P byte read may fail. These are required masks, not measured masks. The ignored `_equal` in hole cases still needs retained-read binding; do not infer it survives optimization.

Source format and invariant checks do not establish compiler/layout support. If flat setup still encounters Unsupported, stop with its exact source/property binding; do not expand layout support or weaken payload requirements. Every repaired outcome is NOT_RUN pending coordinator rerun.

## Required targeted evidence

For EACH lane and EACH of the 16 harnesses, request selected input/root/hash, original and consumed MIR, retained raw_eq or actual SpecArrayEq route/extent/order, emitted and reached property IDs/descriptions/source sites and ALL extras; separate setup/compiler/solver/golden status. Bind BOTH carriers/provenance/addends/referent origins/AllocIds, ranges and canonical symbols; report lowering mismatch explicitly. Request InitialTargets/points-to/relevance/delayed phases and reason for any absence.

For M1, bind actual immutable referent Some/None before zero-fill, mutability/Freeze/layout, compatible emitted symbol, completed per-model reset then runtime object/offset mask seed before first user effect and the actual get. Some(0) stays true, None false; AllocId is not runtime object ID. Mutable S must get only tracked writes, no immutable seed; copied false must not be reinitialized. Incomplete/missing artifact means UNKNOWN, not absent instrumentation. Existing C1-T2 BINDING-QUESTIONS and M0/M1 contracts remain normative; no raw/full-log fallback, no new runner.
