# R10 freshness run provenance design

The freshness-control aggregate currently records profile/tool binding and
classifications, while its stage gate checks stage names, exit codes, statuses,
and the two generated Rust input hashes. Those checks can classify a bounded
control run, but they do not distinguish a newly executed R10 case from an old
aggregate copied into a later Build's evidence tree. A byte-identical aggregate
is compatible with both a deterministic rerun and stale/copy provenance; it is
not execution evidence by itself.

For R10 only, the caller will pass the already validated parent run environment
as `validated_run`. The freshness runner will validate one canonical identity
tuple: Cloud Build UUID and provider identity, proof SHA, actual SmallSort
source SHA, selected profile name and profile SHA, effective tool commit, and
the exact exporter/VeriFast/refinement-checker binary SHA map. It will require
the selected profile binding to match the current profile file and tool commit.
R8/R9 behavior and historical evidence remain unchanged.

Each case receives that tuple plus its case name and prepared original/verified
source hashes. The hosted `execute_case` implementation attaches the identity
to each genuine stage receipt immediately after the stage returns. It preserves
the runner's status, exit code, argv, timing, and source-before/source-after
fields. It does not create absent receipts or stamp `NOT_RUN`, timeout, or
stage-start error receipts as executed. R10 admission requires the existing
stage/source/status/code checks and exact identity equality, while retaining
the existing target line, diagnostic predicate, source gate, and classification
criteria. The manifest, per-case result, and aggregate also carry the complete
eight-case identity map.

This provenance joins a source-reported control classification to one hosted
Build and its pinned inputs. It does not independently establish parser-input
binding, formal proof acceptance, or proof credit. A matching archive hash or
copied aggregate cannot substitute for per-case current-run stage receipts.
