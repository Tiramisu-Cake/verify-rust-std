# CC2 bounded coordinator request — no dispatch authorization

Exact source/base/tree and hashes: INPUTS.json. Commands, roots, environment,
per-invocation object-bits12 and limits: CI-ROOTS.json. Worker did not push, run
CI or build. Coordinator owns independent semantic review, GO, source transport,
budget/caps and binary identities. Binary hashes remain UNKNOWN until captured.

1. Review the source diff/dependencies against accepted CC1 b2e1a392a.
2. Existing build/preflight/typecheck on nightly-2026-10-23; include compilation
   of all three new fixtures. Build cap600s; stop proof if preparation fails.
3. Run manifest candidate invocations sequentially,1 job, fresh directory each.
   Singleton argv: CHECKOUT/scripts/kani FILE + common_cli + --exact --harness
   ROOT + output_cli + tail_cli. Mixed argv omits --exact/--harness and requires
   precisely its listed roots. Wrapper must exec CHECKOUT/target/kani/bin/kani-driver
   with argv0 kani and the matching compiler/CBMC; record exact hashes and version.
4. Two baseline probes use the same hashed candidate positive.rs input but the
   accepted CC1 compiler/driver binary pair, without a source overlay or rebuild
   by worker. Capture their exact binary/source identities before comparison.
   If unavailable, mark baseline discrimination UNKNOWN; do not fabricate a
   baseline failure or call a non-discriminating test a reproduced entry defect.

Total19 invocations /25 harness results (17/23 candidate +2/2 baseline). Proposed
caps require coordinator GO:120s/harness,180s/invocation, RSS12582912KiB, complete
request envelope3600s including preparation. Individual caps are ceilings, not
permission to exceed the total envelope; an unfinished request is incomplete.
No H1 matrix, extra profile, retry, new tracing framework or new Cloud spend by
worker. Default solver, slicing, unwind/overflow/memory/receiver/bool/undefined
function/reachability checks remain enabled; object bits12 is per invocation.

Retain complete regular and JSON inventories for each harness, original exit,
signal, timeout and RSS KiB, argv/environment and source/binary binding. Missing,
malformed, partial or crashed collection is failure. No matched failure-string
alone accepts a negative. Bind exact read Check and CheckRef occurrences in the
selected model; require no extra slot/bool/ref/protocol/frame/Unsupported/invalid
value failures. Positive useful assertions must be reached SUCCESS and covers
satisfied. For payload negatives require the callee's cover before the actual
read to be reached; caller-negative must bind the read before entry. Padding
negative must bind byte1 of the actual repr(C) slot, not a different hole.

Selected field request through existing coordinator preparation/evidence only:

- For scalar_slot and reference_slot: actual monomorphized instance/body,
  arg_count/local numbers/types, first operand read before address creation,
  entry SetRef address and mask, caller source checks, normal return destination
  setter and consumer CheckRef. Establish candidate vs baseline difference.
- For move_wrapper: actual rustc offsets/order/size, data/padding mask, selected
  argument entry, aggregate/Use Copy-or-Move source checks and destination setter;
  actual normal-edge placement. If Move is optimized away, mark Move coverage
  UNKNOWN and use an existing coordinator-supported MIR selection, not a claim.
- For original captured cases: initialized bool parameter storage; creation and
  actual copying of the &bool capture field through registration; wrapper/upvar
  copy setter, current layout reason, and both capture-slot/referent CheckRefs.
  Do not infer last setter/witness from a property description. Nonzero layout
  Unsupported remains CC3 BLOCKED, never PASS bool initialization.
- For negative ref/raw/padding and caller roots: selected storage object/extent,
  typed mask, no pointer-referent initialization, actual reached read and complete
  failure set; selected trace fields/last-write evidence only if existing capture
  supplies them. Otherwise preserve UNKNOWN and request the concrete missing data.
- For mixed/singleton: actual starting_items grouping/order and full per-root
  comparison, not declaration-order inference. Both actual orders remain an open
  integration obligation unless established by the existing coordinator route.

Run original recursive_check/ordinary/SimpleCheck and original replace ordinary/
SimpleCheck separately, without the old collector's early stop. Preserve every
remaining failure. CC1 detected cycle must not crash; ordinary recursive
Unsupported remains release BLOCKED. Replace_transfer prior5-failure observation
is unchanged; no new demand to remove its two u8 havoc-domain checks.

After CC2 targeted evidence, common reviewed CC1–CC3 head still needs one Quick,
all8 strong JSON cases and C03/S3 left/right-hole controls, then separate full
gates. This request does not issue CC3 or publish Part1. Read resulting evidence
through Evidence Brief only; no raw logs/archives/downloads/historical rewrites.
