# Independent H_align gate: initial hosted result

2026-10-06 UTC (2026-10-07 Moscow). **CLOSED / INCONCLUSIVE — fixture annotation syntax failure before
proof obligations.** The one authorized NEW run is used; no active run. This
neither proves nor refutes H_align, and is not a new VeriFast semantic NO-GO.
[Phase/card](SORT4-ALIGNMENT-PHASE.md), [composition design](SORT4-COMPOSITION-ASSESSMENT.md).

## Run and frozen profile

[Run37529855468](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37529855468),
workflow_dispatch, verifast_sort4_alignment/budget90, exact source
`17ad1f48b1eb97f806e03a97b7bf64b24f8ac50b`. Clean fork/research heads matched
at entry and before dispatch; no other active experiment. Created20:53:28UTC,
verification job20:53:33–20:54:10UTC,37s, FAILURE; replay job SKIPPED.
One hosted ubuntu24.04/x86_64 runner. No rerun, alternate profile, patches or
local executable checks. Workflow remains manual-only.

Official VF26.09 archive checked against
`da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa` before
fresh extraction in RUNNER_TEMP; no cached/custom verifier substituted.
VeriFast source/schema809de4596839b739dd999f9e462242c835e3af46, schema SHA256
`7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9` checked.
Rust nightly-2026-02-05 / rustc1.95.0-nightly
`db3e99bbab28c6ca778b13222becdea54533d908`, LLVM22.1.0,
host x86_64-unknown-linux-gnu. Effective ldd resolves paired bin/libz3.so.

Recorded binary SHA256: verifast
`dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc`,
refinement-checker
`9f38829f30cb3295653ca111b53592946a97807eee54cba438fffed14c8c1ffe`,
exporter
`2b8ebb5373d0bdd82cc163f5a298a4291b89dcdb8630a01bf74149987f2d5e0c`.
All installed rsspec hashes retained; relevant prelude_core
`aba25fb4b0fc4aac2b26537b130c900697bf69933598878eed8e163f8aafa571`,
std/lib
`24c86cd57364d1962e13232bde46117f16b71dc4b8ba6264a4577903cfc53ecb`.
Target SmallSort blob e555fce440872898e47fd5114f32eb15401d07df actively checked,
SHA25632574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959.
No actual sort4 body/callee proof was run by these source-linked geometry fixtures.

## Six isolated cases

Every case has exporter0, Cap'n Proto decode0, refinement0 (No refinement errors
found), verifier1 and per-stage source hashes unchanged. Each original is the
exact ghost-stripped fixture; source/export/ghost boundaries and hashes are
archived. Five pointer cases preserve their actual .add in exported/decoded MIR:
generic const/mut T, concrete const Z, and source/destination byte .add(1) before
cast back to Z. The layout case preserves size_of/align_of calls. MIR includes
the emitted direct unwind-Continue edges; it is not a verified no-unwind result.

| Case | First actual VeriFast error in isolated verified/lib.rs | Intended proof stage reached? | Classification |
| --- | --- | --- | --- |
| positive_generic_const | line10, opening `{` of ghost lemma: Parse error | No helper or caller header/body; no .add proof record | INCONCLUSIVE |
| positive_generic_mut | line10, opening `{` of ghost lemma: Parse error | Same | INCONCLUSIVE |
| positive_zst_layout | line12, `ens`: Parse error | No layout/assertion proof | INCONCLUSIVE |
| positive_zst_add | line13, `ens`: Parse error | No .add/result proof | INCONCLUSIVE |
| negative_source_byte_offset | line14, `ens`: Parse error | Marked alignment assertion at line23 NOT REACHED | INCONCLUSIVE, not intended negative |
| negative_destination_byte_offset | line14, `ens`: Parse error | Marked alignment assertion at line23 NOT REACHED | INCONCLUSIVE, not intended negative |

Total caller headers0, helper headers0, helper-body records0, pointer-operation
records0. Hosted classifier rejects every case as INCONCLUSIVE, retaining raw
exits/errors; no unrelated parser failure counts as intended alignment detection.
No geometry, ZST-layout, full normal/unwind resource post, operation-level UB
coverage or generic-sort4 coverage has been established. No claim of a missed
alignment negative or unsupported repr(align8) follows from this parse failure.

## Cause and exact proposed formatting correction

This was an avoidable fixture-preparation error, not tool installation or a
failed mathematical/resource theorem. Both new ghost lemma signatures were
terminated by `;`, which declares a bodyless lemma, then followed by a body.
The Rust functions put `req`, `ens`, and `on_unwind_ens` in one annotation block;
the pinned frontend expects them as separate contract annotation ranges.
Existing checked recover_pair and natural-block callers show the supported
syntax. Successful Rust export/refinement does not parse/check those contracts
like VeriFast, so their success could not validate the proof annotation syntax.

A separately authorized syntax-only correction would change the two ghost
signatures to the following form, keeping their existing req/ens/body intact:

```text
lem aligned_step_const(address: usize, stride: usize, alignment: usize)
    req ...;
    ens ...;
{ ... }
```

Apply the same removal of the signature semicolon to aligned_step_mut. For all
six Rust functions, keep their exact predicates/assertions/operations but split
contract comments:

```text
/*@ req ...; @*/
/*@ ens ...; @*/
/*@ on_unwind_ens false; @*/
{ ... }
```

No runtime/type/algorithm/signature change, predicate weakening, added premise,
new trusted lemma, disabled check or verifier/parser/spec patch is proposed.
Driver case metadata is generated on the hosted runner and would track new
source lines; no classification relaxation is needed. The correction is described
only, **NOT APPLIED / NOT VERIFIED**. It requires a fresh source SHA and a NEW
hosted run, never rerunning37529855468. The original failing fixtures and evidence
stay intact. A new narrow decision could authorize that formatting correction
and one fresh90min diagnostic under the identical profile/cases/target posts;
it would not reopen any other tool phase.

## Evidence and cost

[Artifact11443817617](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37529855468/artifacts/11443817617),
159files,112183-byte zip; download SHA256 matches API/upload digest:
`f1ca30c7bc50125c09a901e9442ef2af8e596bc06e3dbd6c50bebb4e00ef663f`.
Aggregate JSON SHA256
`2e5d8fce61ee88fc0821139c20f2e9f0e8a6c35e21d0cca85164f1f47e8ea389`;
full Actions log SHA256
`490df197e2dbec659c5c64291d3a7d99582e01fed161479e8654f6fed8435e3c`.
Input fixture SHA256
`36fb4aaf8f070d0be22ff43578b8409d79e6b4fa4b4b8bb4c22e4f4c71547443`,
runner4712c5b8149a52e4f36b47596076eb7610d7b749c745720e7d171fce5ddb75d8,
driver8737ea905ea7472f559349586b5bd4ee2bc42de005ee7efeb6fda57594b59240.
Full per-case original/verified/MIR and stage hashes/resources remain in artifact.
Downloads/logs stayed outside the repository and were not committed.

Runner including verifier/toolchain/schema setup and all cases18.05s,
peak RSS622004KiB; each exporter~.02s, decode<.01s, verifier~.07s,
refinement~.07–.09s. No timeout/OOM. Compiler unused-variable warnings (size,
bad and the unused other pointer) are noncausal; full exporter logs retained.
Actions Node deprecation warnings are noncausal. Full six verifier/refinement
logs, exporter/decoded body/annotation locations, identities and artifact data
were inspected. No downloaded script/processor/verifier was executed locally.

## Remaining boundary and stop

Source-model audit remains: size_align plus valid-layout positivity can support
geometry; .add models provenance/limits separately. Typed copy/points_to do not
expose the needed alignment obligation in inspected pinned paths; byte-to-typed
conversion demands aligned input. No legitimate independent raw-copy detector
negative has been established. This is not repaired or measured by manual
alignment assertions. ZST layout calibration, geometry, caller/selected-pointer
routing, ownership and all five panic posts remain open.

**STOP at1/1 used; no active run.** Documentation closeout/commit/push only.
RAPx0.7.50 A/replay remain CLOSED / NO-GO, B/C NOT RUN, Kani results unchanged.
No full-sort4 proof, new trust extension, extra verification, external message or
publication is authorized. Proposed syntax correction needs a separate decision.
