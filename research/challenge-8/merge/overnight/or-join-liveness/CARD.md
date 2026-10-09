# MIR-OR-JOIN-LIVENESS — experimental component, not an accepted profile

## Problem and observed basis

The actual `bidirectional_merge` diagnostic b34 verifies all visited body,
normal, unwind, return and leak obligations but exits 1 with six dead-code
records. Five are an impossible ghost case at source line 504 and are outside
this component. The sixth is source span
`verified/lib.rs(513,51-515,10)`, although the real call at line 514 executes
and its unwind cleanup and leak checks finish.

The pinned f760 frontend lowers the final
`left != left_end || right != right_end` to two true edges entering one panic
body. The normal-decode MIR used by the actual verifier has blocks 34 and
36, each with exactly two `StorageDead` statements followed by
`Goto 37`; block 37 contains the diverging
`panic_on_ord_violation` call with `UnwindAction::Continue`. In the b34
proof AST, the corresponding labels 34 and 36 each have one `Goto 37` with
the same printed body span, while label 37 has the one real panic call.
The separate `decode.out` snapshot numbers these blocks 28/30/31; it
does not match the actual VeriFast proof AST and is not the input pin for
this component. Fresh trial artifacts must establish their own matching
normal MIR/AST pair.
The first true edge executes; the second true edge is impossible after all
output slots have been filled. The frozen console's `LocHashtbl` compares
`loc0` by physical identity (`==`), so two separately decoded but
textually equal spans remain separate coverage entries.
The same pinned translator already gives the true/false Gotos inside each
single boolean `IfStmt` one shared location object. This component
extends that coverage convention only to the two operation-free entries
of one common source body.

## Rule and scope

`or-join-liveness.patch` applies **after** the six existing patches to
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` only. It is
inactive for every body except the exact `bidirectional_merge` name. For
that body it refuses unless all these conditions hold:

* Raw MIR blocks 34 and 36 are unique, have exactly two
  `StorageDead` statements each, and each has `Goto 37`.
* Their translated blocks have no statements or encoded terminator
  statements, and their two Goto spans are exactly
  verified/lib.rs(g,51-(g+2),10) for one positive guard line g.
* Block 33 compares `left != left_end`, taking true to 34 and false to
  35. Block 35 compares `right != right_end`, taking true to 36 and false
  to 38. The comparison AST spans are exact relative to g, and 34/36
  are the only predecessors of 37.
* Block 37 contains exactly one `panic_on_ord_violation` expression
  statement at line g+1 followed by the unwind return.
  Block 38 retains the normal return.
* After full body translation, there are exactly two Goto statements
  targeting AST label 37 at the admitted body span, exactly one panic call,
  and the two Gotos share the physical `loc0` object.

Only after the source/MIR checks does the patch replace the **location
object** of the second pure Goto terminator with the first one's location
object. Both edges, comparisons, target, panic call, return and unwind remain
in the proof AST and are verified normally. The existing console then
registers one coverage obligation for the two equivalent no-op entries to
the same source body. This is a trusted *coverage-origin* change. It neither
changes pointer/memory/lifetime semantics nor makes `GotoStmt` generally
transparent. No log filtering, `allow_dead_code`, assertion removal,
refinement change or runtime source rewrite is part of this component.

The source identity is an additional external admission gate. A separate
build recipe must compare the six-patch translator SHA-256 and patch
SHA-256 before application; the patched translator SHA-256 before build;
and the exact prepared `verified/lib.rs` SHA-256 before verification.
The original std blob, f760 source commit, exporter, decoder and refiner
pins must also match the explicit manifest for that one run.
The supplied `admit-source.py` checks its own recorded hash, the
source/profile hashes and exact signature/guard/body lines after source
preparation and before the experimental verifier is run. The build recipe
must itself pin this checker and the manifest, and preserve its exit log.
The b34 source SHA and guard line in `PINNED-INPUTS.json` are
**diagnostic evidence only**: the independent ghost restructuring changes
the SHA and likely shifts g. Both admitted source SHA and guard line must
be recorded from the newly prepared source before any Cloud trial.
An unset or different SHA
refuses the component; the existing six-patch profile is unaffected.
The manifest also requires the explicit
`EXPERIMENTAL_CLOUD_TRIAL` state; this never denotes theorem acceptance.
Proof-negative fixture sources require separate named entries in the
`control_sources` allowlist, each with its own SHA, source lines and
`DEAD_PROOF` expected gate. The checker refuses an unnamed or unpinned
fixture; a source-hash refusal cannot count as the intended dead-code
negative.

## Soundness boundary

The coverage grouping is justified only because these two MIR blocks carry
no translated operation and enter the *same* real source body. It does not
claim either edge is reachable, nor erase verification of either edge's
effect on control flow. `StorageDead` is already translated to no AST
statement by pinned f760; this card makes no new lifetime or cleanup
assumption about it. A changed MIR block with any other statement, changed
edge target, changed source span, altered comparison, or additional
predecessor must refuse before grouping. Real statements in either edge
must continue to receive independent coverage; all source break/continue
edges remain outside the admission pair.

The six-patch cleanup kernel and its captured-lifetime question remain
unaccepted. Passing this gate would settle only this one bounded coverage
artifact, not kernel soundness, caller ownership, arbitrary `n`,
callback frame or public SmallSort safety.

The patch has only static application review so far. No Cloud compiler,
frontend admission or proof has run. Its exact translated comparison and
panic patterns must be checked against fresh Cloud artifacts; in
particular, a new ghost helper may renumber basic blocks even when the
runtime code and relative source spans stay the same. Any resulting
refusal requires a newly pinned, reviewed component revision, rather
than relaxing the matcher in a running profile.

## Separate Cloud recipe and current refusal state

`build-seven.sh` copies the exact six-component source into a fresh
`RUNNER_TEMP` home, checks the baseline translator, full six-patch diff,
kernel, parser, prelude, stdlib, exporter, refiner and console hashes,
applies only this translator patch, and rebuilds `bin/verifast` in the
copy. It records the complete seven-component diff and new console hash;
the six-component home is rehashed after the build. The build is bounded
and runs only with the reviewed Cloud provider identity. The GNU make
target invokes Dune in the copied `src` directory; the separate console
must differ from the baseline binary. This recipe is not integrated into
the ordinary matrix.

`run-seven.sh` uses the unchanged retained `pointer-prove.py` harness
under an explicit experimental profile label. It checks an exact prepared
source before verification, preserves each stage exit and artifact, runs
the existing calibrated real dead-code negative and four new calibration-only
source liveness controls before the actual bounded case. Its global
`OR_JOIN_WORK_SECONDS` budget defaults to 900 seconds, accepts only 1..1000,
and reserves 10 seconds for child termination plus 30 seconds for the final
audit. Copy is limited to 90 seconds,
console build to 360 seconds, and each proof group to its remaining budget;
skipped groups are explicitly `NOT_RUN`. The actual group receives at most
680 seconds and its inner VeriFast cap never exceeds 600 seconds. A timeout
or depleted budget yields partial, unaccepted evidence.
`audit-seven.py`
keeps `accepted=false` and `component_gates_complete=false` in all cases.
It reports the actual full positive and calibrated proof negative only
when the retained harness's full gates and source/tool certificates match.
The four new controls cannot be counted as proof negatives until their
expected stage and location are registered from a separate Cloud run.

The current `PINNED-INPUTS.json` has null exact fixture/source/harness pins
and `admission_state=REFUSE_UNTIL_NEW_SOURCE_HASH_AND_CLOUD_CONTROLS`.
The baseline console pin is from b34 and must be compared with the fresh
six-component build; any difference requires a new reviewed pin. The
current scripts therefore refuse before any seventh-profile proof run.

## Cloud gates before any positive classification

1. Build the **separately named** seven-component experimental console
   from exact pinned f760 source and six-patch baseline; publish the
   original/modified translator, patch, all hashes and exact source
   admission result. Preserve the six-component binary/profile separately.
   Any compile, source, patch or admission failure is SETUP/INCONCLUSIVE.
2. Require a fresh same-source MIR and proof AST. Independently check the
   raw 33/34/35/36/37/38 CFG, `StorageDead` counts, distinct true edges,
   common target, exact spans, one real panic call, normal and unwind paths,
   and the post-translation physical grouping admission. Do not infer
   correspondence from equal printed spans alone.
3. Verify the full actual bounded `len ∈ {2,3}` positive with original
   target posts/resources and all helper bodies, source/refinement, normal
   and unwind, return/leak and **zero** dead-code records. The five ghost
   records formerly at line 504 require their separate equivalent proof
   restructuring. The panic call at g+1 must have an execution record and its unwind
   return/leak and posts must still be checked.
4. Register refusal controls with expected **frontend admission stage and
   exact error**: change either Goto target, insert a real statement in
   either join block, change `StorageDead` count/kind, add a predecessor
   to panic, change either comparison/branch order, change the source
   span, rename the panic callee, remove unwind, or change admitted source
   hash. A setup or parser failure is not a successful refusal.
5. Register proof-negative coverage controls, each with exact reachable
   setup and expected `dead code` location: make the real panic body
   unreachable while keeping the pure join shape; place a real statement
   in a genuinely dead source branch; and retain dead source
   `break`/`continue` lowered to Gotos outside the group. Verify that
   the six-patch baseline still reports the original synthetic-edge dead
   record and that this component does not suppress unrelated dead
   records. If a control is optimized away before frontend admission,
   classify it INCONCLUSIVE and replace it with a retained-MIR fixture.
   Each control source needs an independently pinned allowlist entry; no
   control source is currently admitted.

No positive result is accepted on this card alone. Full logs, separate
stage exits, proof/source/tool hashes and the exact controls are required.
