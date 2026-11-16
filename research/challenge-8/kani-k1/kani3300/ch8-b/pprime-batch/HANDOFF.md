# B P-prime batch — preparation only

Input g0 `82cc48368e`, control `4d7e34383a`; exact candidate/tree/request identities in
`CI-REQUEST.json`. Runtime235 NOT_RUN; no proof credit. No push, CI, ledger or local
cargo/rustc/Kani/CBMC. Independent review: `REVIEW.md`; synthetic/static checks: `VALIDATION.json`.

All235 roots now share ONE verify-std invocation (identical flags/cfg/RUSTFLAGS),
with235 exact --harness selectors, --jobs=1, --harness-timeout600s, one export-json.
Historical shard183/52 fields, manifest bytes, oracles and classification/precedence
are unchanged. Std P-prime and pristine stock0aac compiler/model pins are unchanged.
No list, warmup or per-root invocation. `control-delta.patch` is against4d7e34383a.

Binding is per root in export harnesses[]: unique selector/core/manual identity,
contract structure retained, own outcome/verdict/checks/covers/failed_properties.
The entire group selection, target, features, checks and timeout are validated.
A PASS root can coexist with a failing/timeout neighbour and group exit1; missing
rows in a valid PARTIAL export stay incomplete. Every old classification remains;
unknown property buckets preserve diagnostic failures but cannot create complete PASS.
B has no expected contract-target oracle in its frozen manifest: the contract is
retained as source metadata, not claimed independent target binding.

Std compile/preparation runs once through the group invocation. A2100s cap ends
at the fresh export marker, written by pinned main.rs after project build/selection
and before check_all_harnesses. `std-compile.json` persists before spawn and at
that sampled boundary, with cap/time/status and bounded4096-byte head/tail.
This stage includes compilation/preparation; compiler-internal work is NOT_RUN.
Wrapper group cap=2100+235*600=143100s. The unchanged host job210min is an external
ceiling and may force PARTIAL before worst-case group completion. No worst-case
completion claim or shortened row timeout. Stock export is terminal: abrupt job
loss before terminal export leaves selected rows UNKNOWN/seeded NOT_RUN.

Group RSS<=min(12GiB,available−2GiB) via0.1s process-tree sampling; no start without
reserve. Exact per-harness attribution is unavailable, so per-root RSS is UNKNOWN
and only group peak is reported. No claimed6GiB/root measurement/enforcement.
Output64MiB total cap with bounded head/tail; export16MiB; curated artifacts<128MiB.
No raw logs/archives/targets uploaded. Source and binary snapshots before/after.

Coordinator must bind this reviewed candidate and g0 packet before any separately
authorized publication/reservation/trigger. This package does not authorize dispatch.
