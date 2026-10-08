# O23 actual owner: conserved ghost scope and prototype outcome

O22 exact five-body admission reached nested Drop translation and raised
Not_found: the exporter placed two source-written nested ghost annotations
in the outer select_unpredictable body's ghostStmts list, while their call
terminators were in the nested Drop body, whose ghostStmts list was empty.
Patch 15 reassigns these same two annotation records only after the complete
O21 source, ADT, typed MIR and annotation certificate. It changes neither
exported MIR nor ghost commands.

O23 (run 37756681437, proof 94d055d5) passed admission and no longer raised
Not_found. The NORMAL exporter still records exactly 12 ordered outer
annotations, with original raw bytes and spans:

| Outer index | Source lines | Meaning in translator |
| --- | ---: | --- |
| 0 | 95 | nested full-borrow open, moved to nested body |
| 1 | 96 | nested nominal-owner open, moved to nested body |
| 2–5 | 103–106 | outer wrapper opens and two cell assertions |
| 6 | 124–130 | outer conditional selected guard-owner close |
| 7 | 132–136 | outer conditional unselected wrapper close |
| 8–10 | 137–139 | outer owner open, cell assertion, raw-pointer-owner open |
| 11 | 141–145 | outer conditional selected wrapper close |

The nested NORMAL MIR has exactly two VeriFast_ghost_command terminators
at source lines 95 and 96, both with unwind Continue, then the unchanged
real pointer-drop call. After transfer, the translator sees ten outer and
two nested annotations. Every original raw string and source span occurs
once. Readonly preprocessing omits the ghost call terminators, so NORMAL
remains the control-flow certificate. O23's direct typed-MIR mutant changing
only the first nested ghost-call span was rejected by the full-unit SHA gate
before proof, alongside the Move/Copy and cleanup-edge mutants.

The new O23 first proof error is at verified/lib.rs:77:39-40. VeriFast gives
call() in the existing safety_proof type fn_outcome<*Element>, but the
raw_ptr_own opening expects *Element. This prototype implementation proof
type error occurs before actual helper body verification. It does not
establish the nominal owner, SAFE forget or assume_init.

The separate source-only outcome_result candidate changes only that ghost
proof to:

    safety_proof {
        let outcome = call();
        open raw_ptr_own::<Element>()(_t, fn_outcome_result(outcome));
    }

The pinned Rust prelude maps returning(v) to v; its unwinding arm returns
a default value. The actual implementation and prototype retain the full
pointer equality/resource normal post and on_unwind_ens false. The latter
must still make the unwind outcome impossible; projection alone does not
authorize ignoring unwind. The current raw_ptr_own predicate is
definitionally true, so opening it releases no Element pointee right or
cell. There is no assume, axiom or runtime edit.

The old O21 five-body source hash/admission remain historical. This variant
needs fresh exact source/MIR admission, including shifted line spans,
before a proof attempt can test the ghost step. Six/seven/nine-body source
capture selects it without activating a semantic overlay. Source, export,
refinement or certificate refusal cannot count as proof progress.
