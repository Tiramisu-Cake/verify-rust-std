# CC4 coordinator request — no dispatch authorization

Source d7151a2202581cdafdab8354301aaee00ff57df7, tree
0e493cc99e769ff3124ed015bdab824137266ab6, exact parent CC3
76a706f8f8c5b0471bd5c8e6b48cdaf45bab9b66. INPUTS.json pins changed files.
CI-ROOTS.json pins23 invocations /29 root results, input hashes, selection,
flags/environment and proposed caps. Worker has not pushed, built, run CI or
spent Cloud funds. Coordinator owns independent review, GO, source transport,
submission, caps and binary/source provenance. This request is preparation only.

1. Review the bounded diagnostic/override-metadata diff and inherited CC1–CC3
   dependencies. Origin resolve uses the same RunContract model/args as the
   contracts pass; analyzed selected bodies and partial-graph rejection remain.
2. Existing clean build/preflight/typecheck on nightly-2026-10-23 / rustc7189d39d9,
   target x86_64-unknown-linux-gnu; include all3 new fixtures and8 active_call_tests
   Rust units. Proposed build600s/unit120s. Stop before proof on preparation
   failure; worker performed no local Rust compilation.
3. Use normal solver/cadical, slicing, checks and existing bounded capture.
   Exact singleton argv: CHECKOUT/scripts/kani FILE + common_cli + --exact
   --harness ROOT + output_cli + tail_cli. Whole-input omits --exact/--harness.
   Source unwind8 and per-invocation object-bits12 remain intact. One job/solver,
   fresh output per invocation, per-root120s, outer60+120*root_count seconds,
   RSS12582912KiB, proposed whole request6600s including preparation/300s capture
   reserve. These ceilings require coordinator GO and do not authorize dispatch.
4. First run original3 roots separately; no legacy collector early-stop. Compare
   isolated bounded SimpleCheck against original, then isolated recursive ordinary.
   Run original/reversed mixed inputs and reversed singletons; record actual
   codegen units, starting_items grouping/order, per-unit mode and body selection.
   A shared immutable map is not evidence of corruption. If orders coincide,
   order coverage stays UNKNOWN; inherited helper units cover fresh contexts in
   both orders but cannot substitute for actual integration order evidence.
5. Run remaining CC1 DAG/repeated-callee/hole/independent/order controls, original
   nonrecursive replace ordinary/SimpleCheck positives, P1 and2 corrected boundary
   fixtures. Required positives must have zero failures and reached useful
   assertions/covers. Preserve exact negative read checks and every extra failure.

Capture original exit/signal/cap/RSS, argv/environment, matching compiler/driver/
sysroot/CBMC/solver hashes and versions, model/GOTO identity. Complete consistent
regular and JSON inventories must include all property IDs/classes/descriptions/
locations/statuses, successful/unreachable/cover checks and Unsupported. Missing,
malformed/partial export, crash or cap never passes an expected negative. Existing
wrapper must exec the matching driver with argv0 kani; no source/CI overlay by
worker, new trace framework, public JSON schema or solver-policy change.

Exact missing fields are in CYCLE-MAP. Prefer existing typed selected/source MIR
windows from the same unit before delayed-UB instrumentation: full Instance or
compiler symbol, typed provenance/selected snapshot origin, caller bb/index/span,
call terminator and repeated active key for each cyclic root separately. The new
bounded reason supplies these where untruncated; omissions/truncation require
specific missing windows, not attribution from overridden=true or root names.
No source-panic registration retry. No recursive analysis of newly instrumented
runtime bodies, fallback, silent cutoff or optimistic summary.

Original saved SimpleCheck is SUCCESS with no failures, NOT cycle Unsupported.
Its collector cover gap requires generated-body↔source cover binding; do not waive
it or require unreachable wrapper covers without explaining selection. Bind both
bounded body branch covers and both outer return paths, including useful assertions.
If isolated passes while original fails, investigate per-unit mode/body selection.
If isolated cycles, obtain actual generated/helper edges. Any unexplained required
positive Unsupported, bad source selection, lost check or extra FAIL is BLOCKED.
A real necessary cycle needs sound summary/SCC or owner-agreed scope in another
reviewed stage. No wider ordinary-contract boundary is accepted by this doc.

The two expectation corrections require exactly one source/model-bound failure
of the specified class/reason and no extras; matching substrings alone is not
acceptance. These cases give no capture/PFC proof credit.

After targeted evidence, run one Quick and all8 existing strong JSON oracle cases
on the reviewed common CC1–CC4 composition, plus inherited CC2/CC3 slot/upvar,
A3/M1/S3/private-frame/C03 and left/right-hole controls. These final composition
runs need separate coordinator authorization/caps; M3/full/platform/SmallSort also
remain separate. No re-learned oracle IDs or relaxed exact failure gates.
Optional upstream flat-recursion probe is NOT_RUN and not included or authorized.
Use Evidence Brief for new CI evidence; allowed old CC3 files are identified in
CYCLE-MAP/EXPECTATION-BOUNDARIES. No raw artifact/log download or historical rewrite.
