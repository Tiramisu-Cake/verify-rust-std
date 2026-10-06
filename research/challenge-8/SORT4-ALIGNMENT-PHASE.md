# Independent sort4 alignment geometry gate

## Current syntax-only continuation — authorized 2026-10-07

**IN PROGRESS / preparation,0/1 additional NEW runs used.** Owner explicitly
permits the correction described in SORT4-ALIGNMENT-RESULTS.md at b1ae937 and
exactly one additional GitHub-hosted manual H_align run,90min including runner
preparation. Entry clean matching local/remote
b1ae937f901ad34aeef8bcdbd98997abd1fd1969; correct fork/research branch, no active
experiment. Initial37529855468/source17ad1f4 remains historical INCONCLUSIVE.

Allowlist: remove the signature semicolon from aligned_step_const/mut and split
req/ens/on_unwind_ens into separate supported annotation blocks in all six Rust
functions. Statically compare checked examples, unchanged ghost payloads and
Rust after ghost stripping before dispatch. No predicate, lemma body, assertion,
case, hypothesis, domain, post, classification, runner/workflow, flag, tool/spec,
trusted premise or runtime-source change. Official unchanged VF26.09 /
nightly-2026-02-05 and all original pins/checks below remain frozen.
Commit/push correction, ONE new manual dispatch at the corrected SHA, match
head_sha, monitor and inspect full logs/artifacts, then document/commit/push.
No Re-run37529855468. Stop after this run regardless of outcome; no further
proof corrections/runs without a new decision. RAPx CLOSED / NO-GO, B/C NOT RUN.
No local compilation/verifier/research-runner execution or external message.

## Historical initial authorization — CLOSED / INCONCLUSIVE

Budget1/1 initial runs used. Run37529855468/source17ad1f4 passes six exports /
decodes / refinements but fails all VF annotation parses before proof obligations;
no geometry/layout/negative proof result. [Initial closeout](SORT4-ALIGNMENT-RESULTS.md).
The original scope/card below stays unchanged; its no-second-run limit governs
that historical budget. The current owner instruction grants a separate one-run
syntax-only continuation above.

Owner authorized on 2026-10-06 by “Давай запустим предлагаемую тобой проверку”,
from clean matching local/remote research HEAD
98c0f4f53eca6467a1e0ead8f0260f96b7d53dbc. Fork/branch correct, no active/queued
Actions at entry. This opens only the H_align gate proposed in
[SORT4-COMPOSITION-ASSESSMENT](SORT4-COMPOSITION-ASSESSMENT.md#one-next-bounded-check--proposed-not-run).

## Scope and budget

One NEW GitHub-hosted manual diagnostic, at most90min including runner preparation,
official unchanged VeriFast26.09/nightly-2026-02-05. Prepare handwritten isolated
fixtures/runner under research/challenge-8 and a minimal workflow_dispatch
selection; commit/push, dispatch exact SHA, inspect full logs/MIR/refinement and
artifacts, document/commit/push closeout. No second run granted by this budget.
No local compiler/verifier/executable tests/extractor, verifier/spec/kernel patches,
new trusted axioms, actual std runtime/signature changes, callback/copy full proof,
RAPx/Kani reruns, B/C, other targets or external messages. Stop after result,
inconclusive setup/domain failure or exhausted budget; semantic changes require
a separate decision. Ordinary preparation is performed before the one run.

## Experiment card

Target obligation: actual sort4_stable source and dst .add offsets0..3 preserve
alignment of valid Storage bases, including ZST. Std blob
 e555fce440872898e47fd5114f32eb15401d07df unchanged. H_align: existing pinned
size_align, valid-layout, division facts and actual typed pointer-add representation
suffice to prove that property without Copy/Freeze or semantic extensions.

Eventual target is the adopted contract's full current SrcOwn(s,V5), Shadow(dst,
pi(V5)), storages, F/frame normal post and all five current SrcOwn + RawDst + F/
frame panic posts, exactly one owner/no local debt. This diagnostic deliberately
proves only pointer geometry, with untouched raw storage permissions/frame,
normal aligned result and no applicable unwind. It has no comparator or copy,
creates no owner, reads no T or padding, and proves no caller/selection theorem.

Domain: arbitrary valid sized T, aligned nonnull bases with four logical legal
positions, raw byte permissions/bounds corresponding to four T slots, i0..3.
Base alignment is the adopted Storage premise, not an inferred fact from generic
points_to or RAPx. Source/reference initialization and ownership are not consumed
by a pointer-only operation; no functional/purity premise is introduced. Require
no independent result alignment. Positivity must derive from existing valid
layout; legal limits/offsets from byte storage and the existing pointer model.
ZST empty byte regions retain separately stated nonnull/aligned base/provenance
facts; the fixture does not invent four same-address T.own chunks.

Cases are isolated at export/verify/refinement:

- Generic const/source and mut/destination actual .add(i), i0..3: expected checked
  alignment result and preserved byte resources. Checked arithmetic helper body,
  no bodyless bridge or new automatic lemma. Source-linked operation, not a whole
  actual sort4 extraction.
- Concrete #[repr(align(8))] ZST model/layout calibration and aligned .add control:
  must establish size0/align8 from model/exported source, not an assumption.
- Two byte-offset1 false source/destination alignment conclusions from aligned
  bases with live raw-byte backing: expected failure at marked alignment assertion,
  no impossible typed cell premise. Fixed modulus8 states the actual Rust layout
  fact independently of whether the VF layout control succeeds. They check the
  arithmetic/post protocol, not automatic UB detection.

Frozen VF source809de4596839b739dd999f9e462242c835e3af46; official Linux release
SHA256 da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa,
nightly-2026-02-05. Record archive/executable/prelude/schema hashes, effective flags,
compiler target, exact fixture/runner/std/run source, per-case MIR/export/refinement,
full verbose proof and resource statistics. No skip_specless flag, no changed
unwind/leak/refinement policy; ghost-strip exact original/annotated byte audit.

## Operation-enforcement audit and decision map

Read-only pinned-source audit: size_align proves divisibility, valid layout plus
is_power_of_2_pos establishes positive alignment. Typed pointer addition preserves
provenance but must check legal limits. Typed points_to/array resources and the
copy_nonoverlapping summary omit an alignment clause; byte-to-typed conversion
requires it. No legitimate misaligned typed-cell copy pair has been found without
assuming the contested resource. Report this source-model boundary, not a counted
intended negative or a new runtime detector. No rewrite/manual assertion can
repair that boundary under this phase. repr(align8) model support is unconfirmed
and tested separately rather than encoded as a trusted alignment axiom.

Classify generic geometry, concrete layout and false-post controls separately.
Geometry PASS requires actual operation reached, both generic proofs/helper bodies,
full normal/no-unwind/resource post, export/decode/refinement and no skipped errors.
Negatives count only at their own marked alignment assertion after the operation,
with source/export/refinement intact; frontend/helper/resource failures are
INCONCLUSIVE. Layout-control failure means align8/ZST calibration unestablished;
never promote negative results under an unmatched layout to target detection.
A false conclusion proved in the corresponding valid domain is a scoped NO-GO
for that model/route. No automatic copy alignment coverage follows even if geometry
passes. Need source/selected-pointer/caller/operation/resource integration later,
not an automatically approved phase. Any missing support or semantic extension
triggers STOP without patches; RAPx0.7.50 A remains NO-GO and B/C NOT RUN.
