# RESULT BRIDGENINE — PRE-BUILD REVIEW / NOT_RUN

State: WAITING_FOR_COORDINATOR_GO; no build submitted, all four rows NOT_RUN.
Branch `experiment/kani-k1-bridgenine-20261101`; task base `2d1d17ca773d97f899006a4c5f84d120e63d4af3`.
Library `77cb4c97733d24c1f03f11dc803a2a7676bfc4d5`, tree `b903aba7c37e6956dc7b2643b4da79695d54fe4c`.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12, cap $88.96.

A/B share actual Stable u8 small_sort N9, explicitly typed fn-pointer F=LtU8::CMP, one independent
LtU8 probe set before input, pure key(x>>1)/full-u8-count oracle, no panic-cut or caller assumes.
B only: raw merge -> unchanged B1 adapter -> verified merge_profile<LtU8>; sort4/insertion real.
Gate A2: source compatibility satisfied; dynamic preconditions/substitution/oracle NOT_RUN.
Caller/leaf M03: `[MaybeUninit<u8>;48]`, src+0 prefix9 initialized/tail39 uninit, split4+5;
separate initialized `[u8;9]` dst+0; same fn-pointer/probe/model, destination9-only frame.
Actual sort4 writes [0..4)/[4..8), insertion extends second run to [4..9); no sortedness assume.
Leaf `merge_scratch48_contract_u8_n9` includes stable=true M03 and general=false M04;
no substitutions in leaf; full leaf cost charged to B. M02/exact N3 proof is not transferred.

| Row (verify:: suffix) | Status | VT / CBMC RSS | Covers expected | Failed checks |
|---|---|---|---|---|
| bridge::bridgenine_direct_u8_n9 (A) | NOT_RUN | UNKNOWN | 2/2 | UNKNOWN |
| bridge::bridgenine_caller_u8_n9 (B) | NOT_RUN | UNKNOWN | 3/3 | UNKNOWN |
| merge::merge_scratch48_contract_u8_n9 | NOT_RUN | UNKNOWN | 2/2 | UNKNOWN |
| bridge::bridgenine_payload_flip_u8_n9 | NOT_RUN | UNKNOWN | 3/3 | count only expected |

Control: [p;9], probe=p; caller v[0]^=1 after return at bridge.rs:171 preserves keys;
expected sole failed literal `bridgenine output preserves full-value probe count` (:176–179), 9->8.
A vs B: NOT_MEASURED; compare VT(B)+VT(leaf) vs VT(A), memory max(B,leaf) vs A, not sum.
Compiler RSS, whole-build wall and build cost separately UNKNOWN. Old v4 F-item is not baseline.
W1/N16/macOS: no new proof or feasibility conclusion before G1; scope is this u8 N9 instance.
Static17/17, ordinary exact200 preserved, cfg-on388->391; request and rustfmt checks pass.
G1 `bridgenine-g1-20261101`: measurement, controls=true, jobs1, uninit=false, 4x10min +30min.
Own UUIDs none; spent $0/reserved $0; prospective G1 full reserve $0.945, task <=2 builds/$1.50.
G2 only compile-error/new-leaf condition, separate GO, spent+new reserve <=$1.50.
Review packet: `bridgenine/PREBUILD.md`; request/args/static/budget in `bridgenine/`.
REVIEW REQUEST SHA is supplied in the coordinator handoff after publishing this packet.
BRIDGENINE is not complete; stopped at the mandatory PRE-BUILD REVIEW boundary.
