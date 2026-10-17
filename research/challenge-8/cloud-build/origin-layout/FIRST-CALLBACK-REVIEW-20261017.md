# Independent first-callback candidate review — 2026-10-17

Scope: readiness for ONE authorized Cloud experiment, not tool qualification,
proof acceptance or integration. No local compilation/extraction/verifier.

Semantic card was written before implementation. Root retained architecture
and scope decisions. Built-in independent agents reviewed separate ownership:

- worker_refiner reviewed explorer_hrtb's HRTB and worker_recovery's local
  recovery change. Its final scoped three-file diff is SHA256
  b7bf867409fbf6fc6c0a9dcc25d3b286a94365380c30e4b3081dbd3f5708929d.
  GO for candidate freeze; no remaining concrete issue in that scope.
- worker_recovery reviewed worker_refiner's official first-edge checker and
  root's runner/integration plus explorer_hrtb's admission harness. Final
  localized helper re-review restored GO after fixing undefined `streams`.
- Root independently reviewed the source/edge/lifetime architecture and all
  integration changes, without treating registration/shape receipts as proofs.

Concrete fixes from review: preserve compiler Trait binders; verify erased source
region/synthesized method-lifetime form; comments between comparator and `(`;
load source from actual spans rather than smallsort.rs basename; accept root
DefPaths; move whitespace helper before use; reject projected receiver/tuple/
result locals; preserve relevant implicit input lifetime; clone mutable ghost
BlockStmt address refs per CFG insertion; fix source-helper path and unique
negative locations; require prefix positive plus exact first-error location for
negatives; fix replay metadata's undefined variable. Physical singleton cell
ownership is tested rather than relying on u64's possibly empty logical own.

Existing v8 profile bytes preserved as GLUE-PROFILE-V8-20261012.json; hash
0e67b038f940a9892dcb840747fbcc340532a31649979601af545acc41a0c68b.
New tool commit d928cb1d7ac60c257daa537fa65577f41135f832 descends from a158398e.
Exporter/schema/kernel/parser/memory model/prelude/runtime std unchanged.
The new patch is appended after the frozen thirteen-patch chain. Compiler remains
nightly-2026-09-25 / f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f, x86_64.

Controls prepared: partial source-linked prefix before tail.read with CURRENT
normal/unwind posts; unchanged full-body diagnostic; four calibrated resource
losses; paired clause/binder/type/ghost mismatches, eight retained generic HRTB
cases; official first-Continue mutant; explicit late Cleanup marker refusal.
Prefix failure skips dependent negatives rather than granting false credit.
Fresh same-campaign B1/helper/normal-unwind/receiver/end/retirement/default-off
checks precede first-callback cases. All execution results are NOT_RUN here.

Remaining empirical risks: compiler build, exact exporter marker spans, parsed
annotation shape, reconstructed strict scope and actual resource closure. These
are the intended Cloud questions. Early refusal is INCONCLUSIVE; official exit0
without its affirmative first-edge receipt is not qualification. No late cleanup
or B2 proof is claimed. After terminal Build use only smallsort-brief UUID.

Exact reviewed inputs:
- `first-callback.patch` SHA256 `b7bf867409fbf6fc6c0a9dcc25d3b286a94365380c30e4b3081dbd3f5708929d`
- `first-callback.py` SHA256 `c88c2427bb0b3731083b89317a12666619c19b42c4e852bc5a3d2d9c786670a7`
- `first-callback-admission-controls.py` SHA256 `d728189e6746fec15b7f127645c30978502c96aa7c903b667f415df9b2815a4f`
- `GLUE-PROFILE.json` SHA256 `300fd8a7172c1644552b43c5bfda51a7c8a620f505012abd3760772df55102e3`
