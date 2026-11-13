# CC2 ordinary argument storage

Candidate 9631aaf89e869624fbfc8cd22d327ce194eb779d on reviewed CC1 b2e1a392a.
SETTER-MAP was written before the patch. Only the delayed instrumentation visitor
and three new expected-suite fixtures/goldens changed. Source assurance only.

Ordinary arguments have a defining value at entry but no defining MIR assignment
in the callee. The visitor now supplies Before SetRef(true) at bb0 for argument
locals 1..=arg_count, restricted by the existing same-depth alias `needs_set`
criterion and an existing Sized PointeeInfo data mask. Return local 0 and other
locals are not initialized. Scalar false has the same initialized data mask as
scalar true. Pointer/ref arguments initialize representation bytes at &raw slot;
there is no traversal into the referent. Padding is false under the existing
MEM_INIT_STATE.set implementation, not initialized by the type's extent.

Top-level union/MU arguments are excluded. Arrays/aggregates containing MU/union
are not admitted when the recursive layout returns UnionAsField; other layout
errors are not replaced with all-true. A reference to such storage remains a
supported pointer representation. Existing MU/union copy/argument/return/Move
logic is untouched. No runtime, DFCC, private-assigns, marker, solver or check
policy change. The alias-ancestor walk was extracted unchanged in meaning and
retains cycle termination; both entry and existing destination writes use it.

Entry operations precede instruction reads. When bb0 contains only a terminator,
updating its source coordinate now preserves pending entry operations instead
of dropping them. For a nonempty block, visit_statement already flushes them.
Caller operand reads remain before the call; callee seeding touches a distinct
parameter allocation. Local raw-deref/source checks also remain unchanged.

No duplicate normal-return/copy setter was added: delayed mutating destinations
already use After SetRef, and MutableBody places call setters on the normal edge.
The same ordinary typed mask covers supported tuple/struct copies. By-value
nonzero closure storage is still a CC3 layout blocker; its existing copy setter
and future entry admission need the actual closure mask. We did not implement
upvar types/offsets, infer tuple layout, or claim captured ordinary roots PASS.

New controls read scalar/ref/wrapper arguments BEFORE their address is created;
otherwise the old local AddressOf setter could mask the entry defect. A matched
CC1-binary probe is requested to establish discrimination in selected MIR.
Capture-free ordinary/SimpleCheck paths have no source arguments/upvars and
perform the slot operations inside ordinary helpers. Actual generated layout,
Copy/Move shape, masks and reachability remain UNKNOWN until coordinator CI.
Full SCC, new transfer protocol and lifetime/Move redesign were not required.
