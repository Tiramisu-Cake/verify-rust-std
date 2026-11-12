# Initializer bootstrap diagnostic: committed source bindings

Scope: M2-B/R6b only, worker15, Cloud$0. SOURCE_READY/NOT_COMPILED; NOT_RELEASE_CANDIDATE. Full identities and SHA256 values are in DIAGNOSTIC-MANIFEST.json; historical R6 package is bound at 54252f16e48bf5e08f4eaad2fc36ee07a75c4325 in INPUTS.json and remains unchanged.

| Configuration | Exact parent | Local candidate | Candidate tree |
| --- | --- | --- | --- |
| R6-02b | 258d6af1ea44411ec3f3aa0a4921c05c3700d6f9 | 405c1f059264d8f7cedeeaa01c6d4ad6867a419e | 162e8ad1e76e842b18c24a4ac2986335902834d7 |
| R1+skip | 1cd96e354ec45346b61c245554a50a8af8cb5ce7 | 56cbc5c4a479bc3fb25310b14fcf279d90581a02 | a97ec3d06efd827829f550f1e7a98f29538758fe |

Both patches are identical, SHA256 0688e33906f4489a4dc310384cfad0417a9dec4ba103da020eda82eea2afae78. Only `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` changes: five added lines, constant plus one slice entry plus rationale. Compiler file SHA256 e59ab3679603c16881c76701d6dfe46112e9174794a62417c0bae70a1c88f75c and compiler subtree b2644584ad2fa76535d29c1b8c479ec6b8829ec1 match between candidates. No runtime byte changes relative to each parent.

## Exact identity and reachability of the source call

- `kani_functions.rs:146–147`: existing KaniModel::InitializeMemoryInitializationState serializes as InitializeMemoryInitializationStateModel. TryFrom<Instance>:340–345 reads attributes::fn_marker(instance.def) and uses try_get_kani_function/FromStr, rather than pretty-name or module matching.
- `library/kani_core/src/mem_init.rs`: existing private initializer carries that marker at R6-02b:220 / R1+skip:233; signature remains zero arguments/generics and unit return. `library/kani/src/lib.rs:63` expands kani_core::kani_lib!, explaining the reported macro location without establishing emitted property causality.
- `ptr_uninit/mod.rs:57–65,101–138`: harness detection still injects the exact model call before the first harness instruction, with empty generics/arguments and unit return place. This source path is unchanged for both configurations. The initializer is not a harness itself.
- Candidate `check_uninit/mod.rs:60–61,90,134–139`: exactly that KaniFunction::Model value joins SKIPPED_ITEMS. The existing guard returns `(false, body)` before target_finder.find_all. It preserves the incoming body, its runtime assignments and calls.
- `ptr_uninit/mod.rs:67` and `delayed_ub/mod.rs:132` both call UninitInstrumenter::run. Both therefore skip initializer body instrumentation. Global initial-target collection, points-to analysis, instance reachability and provider construction still execute unchanged; this is not a new global exclusion.

## Whole-body trust boundary

At this pin the entire initializer has four assignments within the existing unsafe block: two `super::any()` values into tracked_object_id/offset, value=false, then epoch reset. Its only writes target verifier-owned MEM_INIT_STATE and, in R6-02b, the separate verifier-owned ARGUMENT_BUFFER. It takes no input, performs no user-memory read/dereference and contains no user callback. The Option reset is a direct None assignment, with no payload consumption or Drop callback (ArgumentBuffer and Option are Copy). R1+skip instead resets argument_buffer_active=false.

`kani_core/src/lib.rs:295–297` dispatches any<T:Arbitrary> to T::any. Both target fields are usize, fixing T=usize; `arbitrary.rs:33–45,70` uses trivial_arbitrary!(usize) and the original any_raw_internal::<usize>, then AnyRawHook (`lib.rs:526–545`). No generic user implementation is selected by this initializer. The callees are not newly skipped: their separately transformed bodies/hooks and caller call instructions remain under the existing rules.

The excluded scope is deliberately the whole bootstrap body, not only the Option write. The pointer visitor's ordinary assignment path (`ptr_uninit/uninit_visitor.rs:305–346`) can add initialization Set operations for raw address temporaries and raw-pointer writes, and Check operations for additional dereferences. Delayed UB's place visitor (`delayed_ub/instrumentation_visitor.rs:165–207`) can add SetRef/CheckRef for overlapping analysis targets, or Unsupported when their layout cannot be modeled. None of these two providers' checks, setters, copy/transfer instrumentation or Unsupported injections will be added inside this initializer after the guard. This includes instrumentation around the original scalar writes and any-call plumbing, not only the reported Enum reset. Exact previous emitted sites/counts are UNKNOWN without coordinator receipts; these are source rules, not a reconstructed failure inventory.

This private bootstrap must establish the shadow state before that state can describe user memory. Self-instrumenting its writes can mutate the same state or reject its representation before useful analysis. Its fixed source closure supports a diagnostic exemption. The exemption still changes private instrumentation and potentially paths, which is why R1+same-skip is mandatory and no production soundness acceptance is claimed.

All original reset statements execute if the original initializer path executes. The patch adds no assume, early return, branch, active flag, marker, layout support, ABI change, sentinel or rewritten model. User bodies and normal call sites have no source edits; their uninit providers still run, and pointer/valid-value checks and all other passes retain their existing policy. This does not assert identical generated user obligations or feasible paths: removed bootstrap shadow effects may change them.

## Runtime and frame invariants

R6-02b runtime SHA256 725522c2c896b338a737119a352a8ac5abae6fc898f1eee426c0e17e9b9df549 equals R6-02 byte-for-byte: separate unmarked Option pointer buffer, mandatory index0 store selection, real initialize Option=None, matched-load clear, exact R1 Hcopy/GLUE. R1+skip runtime SHA256 d565a600e34ef6199f4c6e0a799a5eb9a224ec0ed9a563ef47da2cbbe908cc06 equals R1 byte-for-byte: marked scalar payload and active=false epoch reset. No demonic return or payload substitution.

`codegen/contract.rs:142–170` still discovers only the KaniMemoryInitializationState-marked static for shadow assigns. ARGUMENT_BUFFER remains unmarked and does not become frame-private because its initializer is skipped. Store/reset/clear frame effects, expired saved pointer/invalid-source and other early failures remain possible. No assigns extension is requested to hide them.

## Assurance and matched-control decision

Reported by coordinator, not independently observed here: R6-01 run43271948094 hit >6.46GiB cutoff (11167steps,563→162VCC); R6-02 run43271955539 stopped at initializer Option/Enum Unsupported (1049steps,28→19VCC,0.8s). The latter is NON_COMPARABLE, not resource relief or Hrepr evidence. Historical reports are not rewritten.

Observed locally: committed source/hash/tree equality, exact patch reconstruction, signatures/markers, pinned formatting and diff checks (STATIC-CHECKS.json). Source-predicted: the shared guard prevents both providers from inserting that initializer-body Unsupported, retaining its reset source. Observed new build/path/feasibility/property/solver bindings: NONE/UNKNOWN; compilation and solver NOT_RUN; proof credit0.

The repaired P1 must first pass the emitted-path gate in CI-REQUEST. If R6-02b converts and R1+skip remains heavy under comparable paths, the distinguishing Hrepr experiment is restored, without isolating pointer lifetime/private membership. If both convert, initializer self-instrumentation is substantial or changes paths and previous Hrepr attribution must be reconsidered. If repair stops early, examine the new boundary in a separate handoff. Mere property presence or low counts do not establish feasibility or comparability. M3/integration/heavy M2/P2 remain HELD.
