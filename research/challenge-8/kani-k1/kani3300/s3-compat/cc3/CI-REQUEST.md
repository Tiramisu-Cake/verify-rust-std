# CC3 bounded coordinator request — no dispatch authorization

Source `76a706f8f8c5b0471bd5c8e6b48cdaf45bab9b66`, tree
`6730468d0cb9cf24752ad67ef6ebaab35be8e627`, parent accepted CC2
`9631aaf89e869624fbfc8cd22d327ce194eb779d`. INPUTS.json pins all changed files;
CI-ROOTS.json pins every invocation/input/root/flag/cap. Worker did not build,
push, execute CI or spend Cloud funds. Coordinator owns independent semantic
review, GO, source transport, budgets/caps and exact binary provenance.

1. Independently review the closure arm and unchanged CC1/CC2 dependencies.
2. Existing clean build/preflight/typecheck on nightly-2026-10-23, rustc
   7189d39d9, x86_64-unknown-linux-gnu, stock CBMC6.11.0/normal cadical.
   Compile the three new fixtures; build/typecheck cap600s. Preparation failure
   stops proof. No source/workflow overlay or worker rebuild is requested.
3. Run manifest invocations sequentially, one solver/job, fresh output directory
   each. Exact singleton argv is CHECKOUT/scripts/kani FILE + common_cli +
   --exact --harness ROOT + output_cli + tail_cli. Whole-input mixed argv omits
   --exact/--harness and requires precisely the listed roots. The wrapper must
   execute the matching driver with argv0 kani. Record compiler/driver/sysroot/
   CBMC/solver hashes and versions, actual backend argv and GOTO/model identity.
4. Original replace ordinary/SimpleCheck run first, independently of the legacy
   mode collector's early-stop behavior. Collect recursive roots separately and
   preserve every remaining failure, including ordinary cycle release blockers.
   Replace_transfer is observation only: preserve the historical five failures
   before comparing new results; never assume its two u8 havoc-domain checks
   are false or demand their removal as an ordinary-slot acceptance criterion.

Total35 invocations /40 harness results:8 new singleton roots,18 existing
closure controls,6 original mode roots,3 new-file mixed runs. Proposed caps:
120s/harness; outer60+120*root_count seconds (180/300/420); RSS12582912KiB;
whole request envelope7800s including600s preparation and300s capture reserve.
These are request ceilings, not authorization; coordinator fixes GO/caps before
submission. No H1 matrix, new profile, retries or budget extension is authorized.
Normal solver/slicing and memory/unwind/overflow/bool/receiver/undefined-function/
reachability checks stay enabled. Object-bits12 is per invocation, never global.

Require complete consistent JSON and regular property inventories, IDs/classes/
descriptions/locations/statuses, actual reached covers/useful assertions,
original exits/signals/timeouts/RSS KiB and source/binary binding. Crash, missing
or partial export, signal/cap or collection error is not expected-negative PASS.
Legal positives require zero failures and reached useful SUCCESS. Payload
negatives require exactly the local Check and delayed CheckRef bound to the
actual target u8 read, without slot/layout/invalid-value/frame/protocol failures.
Unsupported is not a substitute. Expected files express future requirements;
new property IDs/counts and actual outcomes remain UNKNOWN until execution.

Selected MIR/model fields through existing coordinator capture only:

- For original replace ordinary/SimpleCheck and new captured_contract: actual
  monomorphized ensures upvar type (&bool), size/offset/mask, caller aggregate
  construction and setter for that storage, wrapper/upvar Copy/Move operations,
  normal edges and both slot/referent CheckRefs. Check bool true/false branches
  and useful covers. Do not infer runtime last setter from a description.
- For every boundary: actual reached typed ptr::read<F>/closure layout request,
  actual F/upvar list and full rustc FieldsShape offsets/order/size, recursively
  composed data/padding mask and source→model binding. An earlier unrelated
  Unsupported or absent request is NONDISCRIMINATING. By-value MU/union must
  show recursive UnionAsField; by-reference masks must not initialize payload.
- For mixed/nested controls: actual logical and physical field permutations,
  nonzero Offset<F>.callback offset, nested current_offset composition and
  padded field mask. At least one field order must be nonidentity for order
  coverage; if rustc picks identity throughout, report missing discrimination.
- For holes: distinguish reference-slot object/extent from MU referent; reach
  the body/pre-read cover. Padding pointer must be bound to byte1 of the live
  copied closure's actual captured Padded field. Any lost copy/Move/order or
  preempted read remains UNKNOWN, not inferred coverage.
- For mixed/singletons: record actual starting_items grouping and both actual
  root orders through existing support; declaration order alone proves neither.
  No new tracing framework, source rewrites or re-learned oracle IDs.

After targeted evidence, one Quick and all8 strong JSON cases on the reviewed
common CC1–CC3 head remain required, with existing C03/S3 left/right-hole,
CC1/CC2/capture-free/legal-pair/P1/P2/frame/clause controls and both root orders.
CI-ROOTS.json pins the existing strong-oracle manifest and S3 control inputs.
Those final gates need separate coordinator authorization/caps, as do subsequent
M3/full/platform/SmallSort gates. This request does not qualify any general mode
or publish Part1. If an original legal companion needs wider aggregate/union
support, report that release blocker without changing predicate/captures.
Read resulting CI evidence through Evidence Brief only; no raw-download fallback
or historical evidence/ledger rewrites. Independent proof credit remains absent.
