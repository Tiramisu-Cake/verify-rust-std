# O26 guard shadow: source-only repair before O27 capture

O26 full nine-body profile passed the source/complete MIR admission,
the checked generic pointer-drop body on both outcomes, the checked
A1 pair and owner-preserving forget callee, and the actual safe
prototype proof. It entered the actual helper body. Its first error
at verified/lib.rs:198 is a type mismatch while closing the nominal
guard owner: the ghost token guard denotes the first Rust guard
binding (a pointer, shown by VeriFast as **Element), whereas the
predicate requires a DropOnPanic<*Element> struct value.

The actual Rust source has two shadowed guard bindings. O24 NORMAL
MIR varDebugInfo records the first at line 188 as local _16 and the
second at line 195 as local _24. The latter is an aggregate assignment
of select_unpredictable::DropOnPanic with one inner field, initialized
from the first pointer binding. The current ghost owner-close line
appears immediately after that runtime aggregate. This error
precedes any resource post or cleanup proof and does not invalidate
the checked callees.

The proposed narrow source-only repair changes the two conditional
owner-close arguments from the shadowed bare guard identifier to
the explicit logical aggregate value

    select_unpredictable::DropOnPanic::<*Element> { inner: guard }

where guard inside the field expression is the first, pointer-valued
binding. The expression has the same nominal type, generic argument
and field value as the O24 runtime aggregate assigned to _24. This
does not invent GuardOwn: closing it must still consume exactly the
selected initialized cell and raw-pointer value right already
available in each branch. The unselected cell, real Drop, saved
logical owner across forget, normal/cleanup paths, full actual
post and false unwind remain as before. There is no runtime edit or
new frontend rule.

The old five-body source candidate and accepted admission hash remain
unchanged. Only the six/seven/nine source preparer opts into this
literal-owner variant. It must be re-exported in NORMAL and readonly
modes, refined against its exact original twin, and captured under
the diagnostic whole-unit dumper. The old nine-body source SHA and
every body/unit fingerprint are invalid for the new source; patch17
must receive freshly reviewed exact constants and source/ghost
reconstruction before a new proof attempt. Source or parser failure
is inconclusive. The expected next useful result is either a type
check of the logical aggregate and the real owner-close resource
obligation, or the next actual-body ownership obligation.
