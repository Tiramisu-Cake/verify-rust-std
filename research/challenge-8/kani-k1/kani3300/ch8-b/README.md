# B-01 valid-value census package

CI commit: `5ee153ec2b22f1f7a0e174a985369b2280d8d296`; tree: `f9d2bfdc79fc9651332d618d5cfdca06e7ef8e7e`.
Worktree: `/root/kani-ch8-b-census-w14`, branch `work/ch8-b-census-w14`.
All package commits and the research commit use `[skip ci]`. No push or CI launch.
No ledger reservation/write. Trigger belongs to the coordinator.

Request: [CI-REQUEST.json](CI-REQUEST.json), exact235 manifest [roots.json](roots.json),
full CI-only delta [ci-control.patch](ci-control.patch).
Inventory source is g0 `904bc1e4583800a8152cbe5296bfc48c56b8643e`,
`kani3300/ch8-s1/w14/`; original inventory/ledger/history are untouched.
Source std872d5a43380752786415bc00d2a12ce0e930cb37, clean Kani0aac16ef62da9e9d5645782d458593e5d78143ba.
No compiler WIP is included. Challenge8 item1 plan§8 item1 only; STOP B unchanged.

The packet retains183 roots in shard2 and52 in shard4, omitting empty1/3.
Ubuntu24.04 diagnostic only. Organizer semantic flags + valid-value-checks;
stock export-json is report transport. No autoharness std, cfg-on controls,
uninit-checks, default-unwind override, check suppression, source or model changes.
Per-root invocations use2 outer slots, each jobs1 with separate target caches;
this preserves shard membership/concurrency upper bound, not historic timing comparability.

Limits: root600s and6GiB sampled process-tree RSS; aggregate<=min(12GiB,
available minus2GiB); verifier stage120min/shard, build35min, setup25min,
job210min, max-parallel shards1, total420 runner-min. Output2MiB/invocation,
export256KiB/root, diagnostic tail4096bytes; curated artifacts<128MiB/shard.
No raw logs/targets/archives are uploaded. A cap/runner loss is PARTIAL.
Checks/covers/failures from bound exports and actual exits/signals are retained.

Classes: PASS, copy Unsupported, casts, other Unsupported, intended invalid-value
failure, compile-resource-not-run. Mixed families retain all observed classes;
catchall includes unexpected scientific failures with explicit reason, not a fabricated
compile-error verdict. No ordinary root is prequalified as an intended invalid-value
failure. UNKNOWN never means NoConstraints or PASS. Full census requires both
complete shard summaries and235 unique bound receipts; missing rows remain NOT_RUN.
Source-reported diagnostic classes are not independent B1/B2 proof credit.

The control checkout and clean export/std are siblings. Checkout depth2+, runner.*
only step env, cwd/prefix/trigger checks and Python AST/YAML validation are present.
The exact branch `uninit-ci/ch8-b-census-*` triggers only the census workflow;
three stock push workflows have a narrow negative filter in control only.
The exporter Kani checkout remains pristine upstream. Require attempt1 and a
same-tree child of this `[skip ci]` package; coordinator alone creates that trigger.

[VALIDATION.json](VALIDATION.json) records12 synthetic service tests and static checks.
Review packets: [original](review-original/reviewer.md), [final](review-final/reviewer.md).
Final independent Luna HIGH decision: READY_WITH_LIMITATIONS, see [REVIEW.json](REVIEW.json).
Both concrete findings were fixed and rechecked on the final candidate. Packaging and
review confer no coordinator GO or proof credit.

Coordinator: reconcile B ledger/slot; bind the CI commit/tree, containing g0 SHA,
request SHA256, manifest SHA256 and final review; reserve exactly one B dispatch,
publish the package, then create the same-tree trigger. No auto-rerun. After execution,
aggregate both curated shard reports and preserve PARTIAL/unknown distinctions.
Do not import these outcomes into historical ledgers or set download_verified.
