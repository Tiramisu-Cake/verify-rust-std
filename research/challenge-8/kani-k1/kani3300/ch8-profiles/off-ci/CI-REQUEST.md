# Profiles OFF CI-only request

Preparation only; dispatches0, proof credit NONE. Exact identities and SHA256: CI-REQUEST.json.
The control commit has exactly one parent, upstream stock Kani0aac16ef62, and changes only
.github/workflows and ch8-prof-off-control. All stock workflows are deleted in control only.
The source and tool are separate sibling checkouts; production source/tool bodies are unchanged.

The manifest preserves all62 original rows, ordering, selectors, cfg, source unwind and negative
oracles. Two inventory listings cover empty RUSTFLAGS and exactly --cfg kani_smallsort_controls;
no S sorting cfg. Consumers require a matching earlier EXPECTED leaf observation. This gate
is operational scheduling only: generated wrapper/instance, success-property and cover bindings
still require independent result review; no CI observation automatically grants proof credit.

Caps: ubuntu24.04, jobs1, one lane/run; total180min, setup1800s, proof8400s, closeout600s;
row600s,6GiB RSS, stdout/stderr1MiB each, export8MiB, artifact256MiB. Caps stop execution and
materialize NOT_RUN, preserving original exit/signal/exception and existing row receipts.
Every emitted cover must be SAT with complete counts; every declared negative failure must
appear exactly once with no unrelated failures. The three forwarding branch failures are
required together. The final frame-negative remains UNKNOWN pending binding of the generated
modifies property ID; the runner never invents that ID. Any failed/incomplete row stops later
rows. Compilation targets are disposable build output, removed before evidence upload.

S1 runner adaptations are shown in runner-vs-s1.patch; process-group execution, caps, source
receipts and export checks are reused. No local compiler/verifier, push, CI, publication or
ledger action was performed. ON is outside this package.

Validation: all26 synthetic tests, YAML/actionlint1.7.7 and static identities PASS.
Independent Luna HIGH review: GO_STATIC_REVIEW_ONLY (REVIEW.json); initial finding retained
in REVIEW-initial.json and resolved by mandatory hashing of the actual pinned rustc binary.
Export target and harness timeout plus default-check/coverage configuration are checked.
