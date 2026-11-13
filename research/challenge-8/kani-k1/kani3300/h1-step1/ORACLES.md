# H1 STEP1 oracles — source-bound, not accepted proof

Preparation only; every execution/semantic gate is NOT_RUN/UNKNOWN. No A3/Part1,
Replace, Recursive, M3, platform or SmallSort support is established by this package.

P1 is the exact scalar-pfc-legal.rs / postcondition_reads_initialized_return singleton.
All reached required properties must succeed, including private frame/model/protocol,
validity and uninitialized checks. The useful ensures at source line16 reads the
initialized returned MaybeUninit payload and compares it with17. Presence of a
SUCCESS/UNREACHABLE property is insufficient to establish that useful read.

P2 is the exact scalar-pfc-hole.rs / postcondition_reads_returned_hole singleton.
Its intended failure is the first payload read in the line16 ensures, after a lawful
MaybeUninit return. Require the actual property ID, class, description, source and
callsite/dataflow binding to that read. Preserve the entire bounded property inventory;
all other required obligations must succeed. A generated var_N, total FAILED count,
golden fragment or private assignable failure is not this oracle. Early Unsupported,
private frame, transfer/protocol, invalid-value or path-loss results are semantic gaps.

Match P1/P2 at12,10,14 bits on exact tool/source/input identities and default normal
checks, solver, target, unwind and property selection. P1-only arms retain the same
useful-read and absence-of-extra-failures gates but cannot independently substitute
for a matched negative at the same configuration. In particular16-bit UF/no-slice
resource relief is not by itself semantic qualification.

Source marker chain at4f64: library/kani_core/src/mem_init.rs tags MEM_INIT_STATE
with KaniMemoryInitializationState; codegen_cprover_gotoc/codegen/contract.rs searches
that marker, resolves the mangled static and attaches a whole-static assigns target.
The existing unwrap_or_default can silently produce no target: no fix is permitted.
Bind the actual emitted symbol, assigns target/extent and relevant reached state writes
from exact root metadata and the actual backend-spawn GOTO. The read-only GOTO/symbol
projections are bounded observations. Missing symbol/assigns/write binding stays
UNKNOWN/SEMANTIC_GAP, even if all properties report success. Do not borrow the R7/R8
carrier/ARGUMENT_BUFFER model or its expected assigns count for this4f64 experiment.

Resource and semantics are independent. A backend spawn receipt binds expanded argv,
stock binary hash and exact GOTO hash; source coordinates alone do not prove the path.
Object exhaustion, including E8, is OBJECT_CAPACITY_EXCEEDED/INCONCLUSIVE. UF rejection
is MODE_UNQUALIFIED/INCONCLUSIVE. A killed conversion has censored first-CNF counts,
never0 or a count copied from another arm. Setup/build failure is verification NOT_RUN.
Any unexpected semantic outcome is a blocker to report, never a reason to alter sources,
goldens, assumptions, checks, clause policy, carriers, solver or retry the arm.

After CI, analyze P1 and P2 separately against N=2^b. Use the same stage/first completed
conversion; enumerate later rounds separately. Two completed points always fit a line;
require a third completed point and independent read-class/coverage observations for
stronger attribution. Report slopes/intercepts/residuals/uncertainty and piecewise
workload if CFG, properties or read classes change. STEP0 R1/R6 S,D,C are not4f64 counts;
4f64 read counts remain UNKNOWN until separately bound. With free-version sharing,
conditional slopes are C≈(321D+65Cret)N and V≈(64S+65D+Cret)N plus residual terms.
Do not use universal C/V<10 or infer ownership from that fit. No-slice retains CBMC
simple_slice; reduced V supports the proposed mechanism without unique causal proof.
Decide SUPPORTED / COUNTEREVIDENCE / INCONCLUSIVE with conditions. Lower-bit outcomes
are not16-bit support; real SmallSort12-bit use needs its own capacity/semantic/replay gate.
