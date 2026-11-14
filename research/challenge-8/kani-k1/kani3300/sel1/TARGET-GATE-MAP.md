# Target and regression gates — all NOT_RUN

Use the six exact selectors/argv in CI-REQUEST.json and immutable source/std bindings in INPUTS.json/STD-OVERLAY.json. The existing B′ CI recipe is a reference; it binds C1 and refuses this six-row request until the coordinator prepares a reviewed CI-only adaptation. No source/CI push, dispatch or runner execution was performed here.

| Row | Actual body/mode | Bound | Oracle |
| --- | --- | --- | --- |
| sort4-closure-on | helper_contracts::sort4_safety_u64; Check(sort4_stable) | src4 initialized, separate MU output4; unwind16 | SUCCESS,0 failed; comparator true/false and return covers, source frame/readbacks reached |
| swap-if-less-closure-on | helper_contracts::swap_safety_u64_backing4; Check(swap_if_less) | initialized backing4; nondet a,b<4 incl equal; unwind8 | SUCCESS,0 failed; frame and all comparator/position/return covers reached |
| raw-legal-on | replay_uninit_controls::sort4_raw_all_initialized_u64; Original(sort4_stable) | original raw src4/dst4; unwind16 | SUCCESS,0 failed; actual entered/returned covers |
| raw-negative-on | replay_uninit_controls::sort4_raw_hole_negative_u64; Original(sort4_stable) | same geometry, precisely source[1] unwritten; unwind16 | exactly intended uninitialized u64 source[1] read in smallsort.rs:751, no select/layout/frame refusal |
| merge-raw-closure-on | helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0; Check(bidirectional_merge) | unchanged B′ geometry; unwind34 | SUCCESS,0 failed, useful readbacks/frame/comparator/return reached |
| merge-profile-closure-on | replay_gateb_prime::merge_profile_closure_scratch48_u8_n9; Check(merge_profile_closure_u8) | unchanged B′ two backings; unwind34 | SUCCESS,0 failed, both backing covers and useful contract checks reached |

Original raw controls are copied byte-for-byte from the frozen final-gate test module. Their direct function-item comparator is an ordinary body path, not a PFC FnMut fn-item layout workaround. The selected source[1] read precedes later select calls; matching arbitrary failed property or failed exit is insufficient. Review source-stage/PFC/body/selected-byte correspondence and preserve complete failures.

The swap callback is test-only noncapturing `|a: &T,b: &T| arbitrary_less::<T>(a,b)`, with direct free-function call; no fn-pointer coercion. Production std helpers/contracts are byte-identical to frozen std. Nothing changes general fn-pointer/trait-object boundaries or grants FnDef layout support. Full original Gate B and further replay rows/caps are for a separate coordinator assignment.
