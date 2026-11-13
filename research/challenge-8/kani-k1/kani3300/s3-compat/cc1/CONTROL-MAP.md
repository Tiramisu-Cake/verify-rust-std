# CC1 control map — all Rust execution NOT_RUN

| Obligation | Control / required observation |
| --- | --- |
| Self cycle | active_call_tests self-cycle; points-to-cycles/self-cycle.rs::self_cycle: targeted Unsupported, complete export, no abort |
| Mutual/original stack | active_call_tests mutual-cycle: root→A→B→A with repeated index1; mutual-cycle.rs::mutual_cycle: cycle Unsupported |
| Completed diamond/repeat | active_call_tests diamond; dag.rs::diamond_two_inputs: useful assertions17/29/17 SUCCESS, no reached Unsupported |
| Two initial graphs | dag.rs sends distinct a/b pointees through identical leaf monomorphization; repeated_callee_preserves_hole reads b hole after legal a, must retain actual read Check/CheckRef |
| Exact instance/body | active_call_tests exact_instance_and_body_selection: synthetic F<u8>/F<u16>/override keys; production Instance key audited, actual typecheck pending |
| Override vs discarded | active_call_tests discarded_override is synthetic empty-body control; existing ordinary/P1 and C03/S3 hole controls exercise actual registration/discarded selection, unchanged at C2 |
| Error unwinding | mutual-cycle unit checks every ancestor returns the same Err and stack becomes empty; callbacks must not join a failed child |
| Independent roots, both orders | active_call_tests independent_roots; roots-cycle-first.rs and roots-acyclic-first.rs pair self_cycle with independent_nonrecursive; each good root must succeed alone and mixed |
| Bounded diagnostic | unit diagnostic_is_bounded:100 active keys, bounded reason, all100 exits fail/pop; no depth truncation |
| Original regression | unchanged mode-boundaries/recursive.rs: recursive_check, recursive_ordinary, recursive_simple_check collected separately; complete failure inventories, never treat remaining bool/layout failures as PASS |
| Legal capture-free recursive mode | capture-free.rs::capture_free_recursive_check: no predicate/body upvars, legal total ensures(true), MU result not read; expected explicit cycle Unsupported |
| Nonrecursive P1 | unchanged closure-zst/scalar-pfc-legal.rs::postcondition_reads_initialized_return; exact existing p1 oracle, no additional failures |

Unit controls exercise the actual ActiveCalls helper with synthetic identities, not
rustc/MIR or actual override resolution. Python source checks are not Rust tests.
Mixed source declaration order alone does not prove starting_items traversal order;
coordinator must establish actual grouping/order from existing preparation artifacts,
or record that order coverage UNKNOWN. Unit order checks remain required separately.
New .expected files are proposed expected-suite substring expectations, not observed
inventories. They do not permit extra failure acceptance; coordinator uses complete
JSON/regular inventories and binds the actual root Unsupported/read operations.

All eight existing oracles and historical mode findings remain byte-for-byte intact.
Quick's old8-oracle PASS does not cover these new roots. Full common Quick/strong
suites remain a later coordinated gate on the reviewed composition.
