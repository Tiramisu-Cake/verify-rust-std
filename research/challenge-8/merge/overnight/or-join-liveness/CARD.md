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

## Separate Cloud recipe and experimental trial state

`build-seven.sh` copies the exact six-component source into a fresh
`RUNNER_TEMP` home, checks the baseline translator, full six-patch diff,
kernel, parser, prelude, stdlib, exporter, refiner and console hashes,
applies only this translator patch, and rebuilds `bin/verifast` in the
copy. It checks the complete seven-component diff against the separately
recorded expected SHA before the expensive console build and records the new
console hash without assuming path-independent binary reproducibility;
the six-component home is rehashed after the build. The build is bounded
and runs only with the reviewed Cloud provider identity. The GNU make
target invokes Dune in the copied `src` directory; the separate console
must differ from the baseline binary. This recipe is not integrated into
the ordinary matrix.

`run-seven.sh` uses the unchanged retained `pointer-prove.py` harness
under an explicit experimental profile label. It checks an exact prepared
source before verification, preserves each stage exit and artifact, runs
the existing calibrated real dead-code negative and four new calibration-only
source liveness controls before the actual bounded case. It then runs the
separate admission controls and the unchanged six-component console on the
same exact fixture/source/posts. Its global
`OR_JOIN_WORK_SECONDS` budget defaults to 1300 seconds, accepts only 1..1300,
and reserves 10 seconds for child termination plus 30 seconds for the final
audit. Copy is limited to 90 seconds,
console build to 360 seconds, and each proof group to its remaining budget;
skipped groups are explicitly `NOT_RUN`. Both actual and six-comparison groups
receive at most 680 seconds each and their inner VeriFast caps never exceed
600 seconds. The admission controls receive at most 240 seconds. A timeout
or depleted budget yields partial, unaccepted evidence.
`audit-seven.py`
keeps `accepted=false` and `component_gates_complete=false` in all cases.
Its independent tool inventory requires the outer build-wrapper exit 0 and
rehashes the retained baseline/component translators, component patch,
six-component full diff, separately pinned expected seven-component full diff,
and installed seventh translator against the recorded manifests.
this audit does not establish component soundness.
It reports the actual full positive and calibrated proof negative only
when the retained harness's full gates and source/tool certificates match.
The four new controls cannot be counted as proof negatives until their
expected stage and location are registered from a separate Cloud run.

The current manifest pins the exact strengthened-helper source and unchanged
fresh six-component console from f0b1ff62 below. It permits only an explicitly
unaccepted experimental Cloud trial. `control-driver.py` may use at most 240s
of the same 1300s budget after the actual proof, in a third disposable tool home.
Its expanded shape matrix and separate source-hash refusal gate require their
own complete Cloud evidence; positive admission and exact frontend refusals
are diagnostics only.
Production six/seven binaries, exporter, refiner and source must remain unchanged.
See CONTROL-DRIVER-CARD.md. Budget exhaustion records NOT_RUN/INCONCLUSIVE.
The six-comparison is classified only on exact identical source and normal MIR,
all eleven verified bodies and return/leak records, full exporter/decode/refiner
stages, one verifier dead-code line at the pinned synthetic Goto span, no other
errors or dead records, and complete stack/panic certificates. Its VF exit 1
remains `INCONCLUSIVE` in the retained harness; the separate coverage-difference
label is neither an intended proof negative nor acceptance.

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


## Fresh pinned trial — f0b1ff62 source provenance only

The new helper preserves the exact selected current value. Build
f0b1ff62-bae7-4ac0-9c3e-dda341e6146a at694feb56 publishes its checked literal
fixture/source extraction and source-only audit. Its overall FAILURE is an
independent permutation artifact-audit defect, not a source preparation failure;
it proves no bounded body. The source pin is accepted only as provenance:
fixture804ca58912a35a4e34c3cac2dc563bcc154daed709477071217d90bd2de8fb47;
verified sourcee03a0398a590fb409d892f2cfad90d2d4b2c4c15949df6feda44852a21aa7d18;
overlaid retained harnessec82511289297f898c4b2442fbc5024c1f55ec919de6d9d5a59d1764615eb3d6;
signature398, guard551. Fresh baseline console is unchanged354436b9.
The manifest authorizes an EXPERIMENTAL_CLOUD_TRIAL at these exact pins.

## Fresh bounded diagnostic — fde74800

The fde74800 Cloud archive records the seventh console, exact source admission,
and the unchanged bounded actual body with all four stages zero, all eleven
bodies visited, 28 return and 31 leak records, 362 target execution records,
full stack/panic certificates, and zero error/dead records. This is a
conditional bounded body PASS under the unaccepted kernel/profile, not a
public-caller or unrestricted theorem. The outer collection was FAILURE: its
auditor treated successful empty stage logs as absent and never read the present
component report. The first admission driver recorded two exact frontend
shape refusals, while its positive AST classifier cut the target function at
its own indented `Func` line and reported INCONCLUSIVE despite the preserved
two Gotos and panic body. These are historical results; code repairs require
a fresh Cloud run. Same-source six comparison and the expanded admission matrix
have no fresh evidence yet. Kernel capture closure and caller/resource bridges
remain open.


## Fresh Cloud outcome — 9ad825fa

Build `9ad825fa-23f2-49f6-bc6c-db2052fe755c`, proof/infra
`96086b2b6c150346e9d3cd1dad30778845880011`, config
`c95985b0200b86222f489c32222e2bbf93bbf3c2812b8acd6fdaf79f88bb2cbd`, sourceinput
`45ddd6d31d5b03e491fbf65b7607a52735a03904161d40cc12e70aa96315219d`; archive SHA
`21fe558a9a30afd70f3f0f71a105a1ef4b5c10f206109bdd2f140fd1d2892577`. Actual
len2/3 is a bounded PASS under the unaccepted seven-component profile: 11/11
bodies, 28 returns, 31 leak checks, 362 target execution records, all stages zero,
no error/dead records. This is the positive-stride/FreezeMarker projection only.
The expanded shape matrix is incomplete: all 17 manual controls stopped at exporter
exit 2 with `normal MIR field is missing: goto`, so there are no matcher-negative
results. The separate source-hash control passed as an expected source-admission
refusal; this does not substitute for the shape controls. Profile acceptance remains
false. The same-source six result is recorded in
[SAME-SOURCE-COMPARISON-CARD.md](SAME-SOURCE-COMPARISON-CARD.md).
