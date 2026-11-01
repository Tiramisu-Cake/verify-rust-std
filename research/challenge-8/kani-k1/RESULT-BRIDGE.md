# RESULT BRIDGE — PRE-BUILD REVIEW / NOT_RUN

Task `TASK-BRIDGE.md`; branch `experiment/kani-k1-bridge-20261101`.
Library commit `b07dc219a27af35e9832335c129bb8759926b7ca`, tree
`f3bf04b5ccf83592e98c1d536d21713e7c01363a`; base `2dde801cf4` (library v4).
Pin Kani `9461e07af7`, nightly-2026-10-12; tools/flags unchanged; cap $88.96.
Stopped before build as requested; coordinator GO required. No UUID, spent/reserved $0/$0.

Adapter: raw `bidirectional_merge<T,F>` -> `adapter<T: FreezeMarker + MergeBridge<F>,F>` ->
sole u8/fn-pointer impl -> `merge_profile::<LtU8>(v,dst,*is_less)` verified replacement.
Unsupported T/F has no impl; no transmute/blanket fallback/specialization.
Leaf PFC and both A3 PFCs have no raw stub or verified replacement.

Caller <-> leaf: T=u8, F=`fn(&u8,&u8)->bool`, value=LtU8::CMP (key x>>1), exact N3,
halves 1+2, sorted right pair; separate initialized source `[u8;3]`, offset0, separate
`MaybeUninit<[u8;3]>` destination, offset0, dst-only frame. Same independent typed LtU8
probe set before call; key sortedness/full-value count, source/probe frame in caller oracle.
Wrong-F keeps sorted inputs/regions/type; unsorted uses right keys [1,0], no sortedness assume.
A3: separate initialized source3, initialized backing4, dst[0..3), sentinel[3], same fn/probe;
modifies only dst3; intentional sentinel write is inside target after its reachable cover.
A3 is separate frame calibration, not a leaf-domain extension or a claim for all profiles.

| # | Row (bridge:: suffix) | Expected | Status / VT / failed checks / covers |
|---|---|---|---|
| 1 | bridge_leaf_u8_n3 | SUCCESS | NOT_RUN / — / — / — |
| 2 | bridge_caller_positive_u8_n3 | SUCCESS | NOT_RUN / — / — / — |
| 3 | bridge_caller_wrong_f_u8_n3 | canonical requires FAILED | NOT_RUN / — / — / — |
| 4 | bridge_caller_unsorted_u8_n3 | sorted-halves requires FAILED | NOT_RUN / — / — / — |
| 5 | bridge_frame_positive_u8_n3 | SUCCESS | NOT_RUN / — / — / — |
| 6 | bridge_frame_negative_u8_n3 | sentinel assigns FAILED | NOT_RUN / — / — / — |

Substitution not yet established: require adapter cover and rows3–4 exact requires failures
under --no-assert-contracts; A3 requires assigns at bridge.rs:122, not OOB/precondition/unsupported.
Static checks 15/15, exact ordinary200 preserved, cfg-on forecast382->388; rustfmt/check clean.
No local compiler/proofs. G1 request `bridge-g1-20261101`: diagnostic, controls on, jobs1,
uninit off, 6x3min, reserve $0.648 <= $0.75. G2 only compile error + separate GO + full budget.
Monomorphization/bounds and indirect recursion remain unverified pin risks; pass order only
supports feasibility. No B2/N16 credit. Next after smoke: actual Stable u8 N9 A/B with matching leaves.
Artifacts: `bridge/PREBUILD.md`, request/args/runner, static gate/report, budget observation.
