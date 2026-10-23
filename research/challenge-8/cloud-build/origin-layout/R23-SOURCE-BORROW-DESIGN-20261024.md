# R23 checked source borrow candidate — preparation, no proof credit

Defect/applicability: after two owned-NLL cycles, capture is present but the
actual b2 caller still fails at array-to-slice placeholder lowering. Capture
Analysis(Initial) and emitted Runtime(PostCleanup) have different fingerprints;
no checked map exists. Do not send a third capture cycle. Source-level work
uses a separate tool worktree at fc0208d4 and keeps capture off in its new
exact opt-in profile.

Candidate: retain the canonical initialized [10,20,5] u64 caller runtime,
`values.as_mut_ptr()` and actual insert_tail call. Add only checked source
annotations/helpers. An explicit source logical lifetime must bind one unique
mutable Ref -> exact Unsize -> slice as_mut_ptr receiver chain. No general
inferred-lifetime exemption, RawPtr/Ref matching, address-only resource bridge,
NLL-derived death assumption, or escaped reference is admitted. The existing
strict lifetime no-escape/exception checks remain required.

Narrow representation choice: ordinary source predicate
r23_u64_array3_own(t,a) unfolds to foreach(Array_elems(a),own<u64>(t));
r23_u64_array3_fbc(t,p) contains *p|->a plus that same element ownership.
Only exact [u64;3] under the source adapter plan may use this representation;
other array interpretation/share cases remain unsupported. Its conversions
use checked Array_to_array/array_to_Array and the existing r20 element-array
content/slice borrow implications. Reverse conversion rebuilds trivial u64
owners with existing checked r9 helpers; it does not assume abstract array
value equality. No generic Copy/Freeze/purity or trusted premise is added.

The real array initialized by the caller is the sole authority. Checked
begin_lifetime/borrow consumes that content; checked end_lifetime/borrow_end
must restore it. Native as_mut_ptr extraction supplies data only, not memory
rights. Use one RustBelt protocol consistently; do not mix an unproved
TreeBorrows end-token bridge. Keep the possibly unwinding insert_tail outside
the short lifetime scope or provide checked original-edge recovery. The R19
normal/unwind resource epilogue and actual callee posts stay unchanged.

Controls required before credit: absent/multiple/displaced markers, wrong
array place/type/count/mutability, ArrayToPointer vs Unsize, missing/mismatched
source lifetime or receiver chain, escaping ref temps, absent physical array
or element owners, helper/source-stage-target mismatch, and all normal/unwind/
panic/Drop/Resume and existing raw controls. Outcomes before intended gates are
INCONCLUSIVE. Tool/source changes require exact published pins and independent
Luna HIGH semantic review before Cloud. All new source bodies/lemmas remain
Cloud-UNVERIFIED; this design grants no B1/B2 or independent credit.

Actual callee boundary found during implementation: the current std spec has
no slice as_mut_ptr body/contract. Regular-call resolution alone is not proof;
adding an external assumed contract or assuming unwind false is rejected.
The source route now adds a default-off read-only descriptor of the actual
compiler-resolved standard callee MIR to the call record, with full typed
steps/counts/signature/identity. It never uses a success flag or a hash as proof.
A paired, unused runtime helper definition has the actual two-cast projection
body and a checked resource-preserving contract. The adapter may redirect the
proof call only after complete typed runtime MIR of actual callee and helper
normalize to the same pure projection under actual T=u64, with no memory
accesses/calls/branches/Ref creation or hidden commands. The helper body must
then actually verify in this same source unit/version; require helper,
insert_tail and caller targets plus all source/stage gates. Its no-unwind post
is proved from the actual pure body, not an axiom. Original caller and std
algorithm runtime statements/signatures remain unchanged; the helper runtime
definition is present identically in both source units, without a Rust call
being added to the canonical caller. Scope is an exact checked body
representation/refinement, not a new alias/lifetime/memory premise.
