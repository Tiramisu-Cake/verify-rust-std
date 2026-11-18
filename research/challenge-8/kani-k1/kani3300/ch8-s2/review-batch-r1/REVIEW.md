# S2 cfg/PFC r1 independent delta review — APPROVE

Exact preparation package `0a4cef493f858d0e91d3ebccfbbab0b8d32d0119`,
task `task7b829344c9cdd8c25ec59294bb9015201638a879`, `ch8-s2/batch-r1/`.
All 28 package files match committed blobs. Source
`9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6`, tree
`64d96010b0b4b896322e26d700c253f834ba9fd6`; control
`2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8`, tree
`b04ce6fd7a2c937bf72fcda7a262eef65a9f45bb`, direct parent
`9e14e033f9ee31522b571c127609dcdff76d230b`. Request SHA256
`779126ddc8aa3e5cabd9b9968f0e1cd853c4e1b60a95a21ff4eb42d5a0c7ca74`.
Stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba` is unchanged.

No blocking or new nonblocking finding. Approval covers this exact static
diagnostic preparation package. Actual r1 compilation remains NOT_RUN.

## Source and all cfg contexts

The source delta from old97ac appends 13 lines to sorting_s2_batch.rs and removes
nothing. Every original byte, source location, runtime body, contract expression,
semantic summary, precondition, frame, probe, type/comparator/domain and geometry
is unchanged. The added sort8 PFC calls the real helper on initialized u8[8]
source and separate writable destination/scratch[8] using KeyLess<u8>. Its
registration is visible in the same opt-in module as both general32 consumers.
It is absent from all 11 exact requested selectors and grants no qualification.

All rows request the same compilation context: kani,
kani_smallsort_sorting, kani_smallsort_controls, kani_smallsort_s2_assumed.
The checker traverses the actual core/module ancestors and active target
declarations. Its conservative provider slice is helper_contracts plus
sorting_s2_batch; other providers are not used to obtain acceptance.

| Root | Active stub_verified targets, in core::slice::sort::shared::smallsort |
| --- | --- |
| swap_pfc | none |
| summary_witness | none |
| merge32_real | none |
| sort13_assumed | swap_if_less |
| general32_assumed | sort8_stable, insert_tail, bidirectional_merge |
| merge_order_corrupt | none |
| merge_count_corrupt | none |
| checker_count_corrupt | none |
| checker_order_corrupt | none |
| sort13_weak | none; ordinary swap_if_less → weak_swap |
| general32_weak | sort8_stable, insert_tail; ordinary merge → weak_merge |

Each of the six active uses has an active matching full-target PFC. Sort8 resolves
to the appended registration; insert_tail and merge resolve to existing helper
PFCs; swap resolves to existing helper PFCs and swap_pfc. The map also checks five
additional active helper_contracts uses. The remaining two helper_contracts_wide
uses and four profile controls, their providers and module declarations are
byte invariant; their full-target registrations remain present in helper/network/
merge modules. No new whole-source/compiler audit is inferred from this delta.
All six requested negatives and the positive general32 root are retained.

Aliases/full paths and nested cfg/cfg_attr all/any/not are evaluated in the bounded
syntax. Inactive functions/modules, unknown relevant cfgs, globs, ambiguous paths
and opaque registrations fail closed. Independent mutations start with exact Git
source bytes and reseal hashes, so matching failures are not hash-drift failures.
Missing PFC, wrong cfg, inactive cfg_attr, disabled target/root/provider and a
visible foreign same-basename target via module alias are rejected. Active
aliased/full-path cfg_attr registrations are accepted. Ordinary stubs require no
PFC; this parser-only control does not qualify a replacement body or summary.

Old97ac is independently rejected at general32_assumed:54 for missing sort8 PFC.
The owner-reported failed run44264952389 named general32_weak:155; both uses share
the missing target and are repaired by this one registration. Static acceptance
does not establish successful Rust/Kani compilation or execution.

## Control, request and validation

The complete oldfc→r1 control delta has ten paths. Runner changes only its source
SHA/tree; policy adds the mandatory cfg/PFC check. check-source → verify_source →
s2_policy.validate_source → cfg_pfc.check executes after pinned source checkout
and before setup/build/verification, with no skip or continue-on-error. Local
package validation executes the same checker. Independent YAML mutations reject
late, skipped or ignored preflight and removed cfg tests.

Twenty-one other control payload files are byte invariant, including decoder,
source-location/negative oracles, packer, snapshot/finalization and service tests.
All 11 row objects differ only in the six negative whole-source SHA fields;
assertion lines/IDs/anchors are unchanged. Three primary probes, 20 required
covers, six exact negatives, flags/solver/checks, runtime and execution groups
are retained. S2-W14-N1 is resolved by deriving metadata6600/1, with no runtime
cap change. MEASUREMENTS is unchanged; qualification assumptions add only the
explicit nonexecuted registration and new source identity.

The mandatory 58 service/error/parser/synthetic tests pass. Fourteen independent
cfg/target fixtures and four workflow mutations pass. Five patch replays produce
the exact source/control trees. Real shallow metadata fixtures retain required
endpoints at control7/source5/tool2; control parent/payload/trigger/rerun guards
pass. Source and stock tool identities are clean and exact.

The unchanged envelope is stock600s/root, one serial 11-root group capped at
900+11*600=7500s, phase8100s, workflow step7560s, job10800s; literal step caps sum
10620s/177min. Group RSS/capture/artifact/compact caps and fallback are unchanged.
Per-root full wall/RSS and R8 remain UNKNOWN. Missing/partial/null/wrong-type/
timeout/NOT_RUN or source-stage-target mismatch remain fail-closed observations.

Old review0468 and old batch/GO/postrun history are immutable and unchanged.
Its guarantees are carried only across proven invariant bytes; its old approval
does not establish that the failed candidate compiled. Pilot/F4 are outside this
delta. No author source/control, pre-existing evidence or ledger was changed.

Registration is lookup presence, not proof. sort13/general32 remain
DIAGNOSTIC_ASSUMED; compile/proof/witness/covers/negative results/cost are NOT_RUN,
B1/B2/independent proof credit NONE, zero closed proof obligations. Native
compiler-instance/contract/property-origin edges remain UNKNOWN. APPROVE is not
GO or permission to repeat. Owner alone decides retry and accounting at10/14;
no charge, refund, reservation, CI, push or ledger action occurred.
