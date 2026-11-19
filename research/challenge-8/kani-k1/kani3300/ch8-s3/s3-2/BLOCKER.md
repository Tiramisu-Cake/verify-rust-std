# S3-2 implementation gate — actual partial-MU mask binding

Task `be42098995b302cade928d8caf6135adf7a1cc0d` is issued by root03:27 despite
the prepared heading in its file. Starting plan86f5bcc, corrected intake31c1dbf,
short review657b1e0 APPROVE/both findings closed, admissionb4879b2: seven bounded
SOURCE_REPORTED cases. Those cases provide no universal provider contract or
independent initialization theorem. No original-run location exception applies
to a new root/run. Current high/FastOFF; no subagents/model changes.

**Concrete issue:** the task requires an actual-state relational init/MU-mask
oracle for the two partial fixtures, while preserving stock0aac and current
flags. Those flags do not enable uninitialized-memory instrumentation. The
available memory predicate cannot observe initialization under that setting.
Crate visibility is not a barrier for an in-core harness; disabled instrumentation
is the barrier.
An expected mask computed from fixture offsets is not the actual callee's
initialization state. The required binding is not established; all eight planned
rows and their obligations are retained, with no narrowed candidate substituted.

Pinned tool0aac source evidence (exact blobs/range hashes in SOURCE-CITATIONS.json):

- `library/kani_core/src/mem.rs:73–79`: public can_dereference checks alignment,
  bounds, assert_is_initialized and valid value. Lines245–259 show the underlying
  is_initialized hook is pub(crate); assert_is_initialized returns true after
  an internal check. These harnesses live inside core: lib.rs357–358 expands
  kani_core::kani_lib!(core), whose lib.rs42–65 generates core::kani::mem. Thus
  the crate-visible hook is reachable here; visibility is NOT the blocker.
  Negating can_dereference is not an uninitializedness query.
- `kani-compiler/src/kani_middle/transform/kani_intrinsics.rs:115–120`: enable_uninit
  is set only by ExtraChecks::Uninit. Lines213–234 replace is_initialized with
  constant true when disabled. `args.rs:104–105,150–157` declares the optional
  extra checks, including Uninit; the pinned request enables neither Uninit nor
  ghost-state. Mem-predicates alone does not activate this instrumentation.
- `library/kani_core/src/mem_init.rs:7–19,36–70`: actual tracking state is an
  internal compiler model, not an end-user oracle. An uninstrumented default
  table is not the memory state of actual production stores.
- `library/kani/src/shadow.rs:17–26,70–81`: ShadowMem requires manual set after
  stores. A harness-written mask cannot observe stores inside unchanged merge
  and would assume the missing relation. This also needs another unstable API.
- `kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs:186–233`: precise
  modifies creates bounded dst write targets. It is useful footprint evidence;
  its conclusion is not that each dst byte has been initialized or that typed
  loads verify actual initialization when the hook is constant true. The optional
  init-state model is itself added as an allowed assigns target at142–170.

For both partial fixtures slot8 must remain uninitialized before and after the
call. A direct in-core assertion `!crate::kani::mem::is_initialized(p.add(8))`
therefore expresses a necessary mask obligation, but lowers to `!true` under
the fixed flags. Positive initializedness assertions instead become vacuous.
This is a static reduction from pinned compiler source, not a native execution
or a proof about an executed fixture. It is the decisive observation gate.

Under source513, `ub_checks.rs:245–250` reexports Kani memory predicates.
The guarded merge contract's dst-only modifies and sorted/count ensures remain
necessary. A successful PFC footprint can support a source-level outside-frame
argument; it does not create a native initializedness oracle. No claim is made
that ordinary value/order checks are useless, or that another reviewed method
could never prove the mask. The missing link is specific to this task's required
actual-mask oracle under its fixed lane.

The required fixtures remain exact: MU48 L(src32,dst0), initially only[32,40)
initialized, requires mask after call[0,8) union[32,40); R(src40,dst16), initially
[0,8) union[32,48), requires after[0,8) union[16,24) union[32,48). Source halves
are sorted4+4, with independent full-byte values; every previously initialized
outside value must survive. No uninitialized byte may be spec-read. Address
disjointness and valid provenance remain separate preconditions. These sets
describe obligations, not assertions about an observed native mask.

**Bounded alternative for root decision, NOT_APPLIED:** retain the same eight
rows, exact values/offsets/order and current caps/flags; implement the two partial
fixtures with actual merge, existing full-byte sorted/count post, source/known-
initialized outside-value frame, dst-only checked PFC footprint, and exact
source-level store/loop coverage argument. Report mask/dst-init/no-MU-read claims
at their actual SOURCE_REPORTED scope and leave the missing independently checked
actual-state binding OPEN. Do not label an expected-mask assertion as a check.
This changes the required oracle/assurance boundary, so W13 has not applied it.
It gives no full sort8/caller/init theorem or assumed-summary credit.

If the exact actual-mask oracle is mandatory, a separately authorized design is
needed: an instrumentation-enabled lane plus a supported actual-state observation/
frame method, with unchanged full-byte/init/frame goals, appropriate adverse
controls and independent review. Merely adding uninit-checks is not established
as sufficient for querying negative initializedness or proving mask preservation.
No tool patch, new flag, trusted ghost relation or broader model is proposed as
already accepted. Raising a resource cap cannot fix the missing observation.

W13 reported this gate to root before narrowing, dropping or reordering any row.
No source/control worktrees or semantic candidate have been created at this gate;
there is no source/control commit, CI request, patched runtime or new workflow
ready for independent implementation review. Final Validate, service tests,
source gates and six patch replays are NOT_RUN because there is no candidate.
Only bounded source/flag/domain/document consistency is checked. No native
compiler/solver/runner/CI, artifact acquisition, publication or accounting action.
