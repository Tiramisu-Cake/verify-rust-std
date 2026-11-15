# Profiles qualification request — coordinator only

PREPARED / NOT_RESERVED / NOT_RUN. This is a request, not a workflow, reservation or dispatch GO.
The exact source commit/tree/patch and OFF tool identities are in CI-REQUEST.json. Independent
source review: REVIEW.json, GO_STATIC_REVIEW_ONLY; compiler/MIR/Kani/ON remain NOT_RUN.

Profiles-ON is one shared cap3 bucket in CH8-DISPATCH-LEDGER.md; no ledger edits by11.
Desired scheduling: one OFF qualification batch, later one ON batch owned by15, one conditional
addressed corrective/repro reserve. All accepted attempts (including failed setup) cost1;
no automatic retries or extra S credits. Coordinator freezes CI-control/workflow/runner SHAs,
reviews generated-property/root inventory, reconciles actual ledger use and obtains GO first.

OFF: exact stock0aac16ef62da9e9d5645782d458593e5d78143ba, tree9d8bc9312bf955ef126d32b819b3cd0ed105ed2b.
Use organizer vector in JSON: verify-std, exact roots, no-assert-contracts, object-bits12,
ordinary default checks, no disabled unwinding assertions, uninit/value-validity OFF. Export
JSON only collects evidence. One root invocation at a time. Honor source solver/unwind attrs;
no arbitrary lower unwind to fit a budget. Set RUSTFLAGS exactly empty for positive rows and
`--cfg kani_smallsort_controls` for negative rows; preserve tool-generated kani cfg. Do not
inherit S sorting cfg or substitute KeyLess. Base std's tool_config points at cd355b0b: use
an external CI-control KANI_TOML_FILE or exact separately built stock binary, not that default.

The fixed62 rows cover:

- 36 migrated PFC roots:14 swap,5 insert,2 sort4,12 merge,3 concrete forwarders.
- All11 closed-profile relation checks and5 matched Replace consumers.
- Eight semantic/payload negative roots (one forwarding root has three branch failures).
- Unchanged helper frame-negative PFC and its legal helper PFC companion.

Original arbitrary-bool helper summary consumers outside this migrated graph remain on their
existing direct FnDef types; no extra qualification is inferred or budget spent on them here.
No bad profile is a PFC/Replace admission domain. CONTROL-MAP.md explicitly replaces old identity
failures, names each oracle, and distinguishes the type guarantee from executed negative checks.

OFF ordering: all leaf PFCs and relation checks precede the five declared consumer rows. A
consumer is eligible only after its same-head P/T/geometry/closure leaf is independently accepted.
The wrapper owns the closure, hence leaf and consumer share the same helper F expression.
No safety-only arbitrary-F helper contract is used to assert ordered/full-value conclusions.
Full-value payload controls run real helpers/entries and keep their original independent probes.
Frame negative remains actual generated modifies evidence; its property ID is deliberately not
invented by static preparation.

Caps per planned run: ubuntu-24.04, jobs1/max-parallel1/concurrent-runs1; 180min total,
setup1800s, proof8400s, closeout600s; 600s/root; RSS6291456KiB=6GiB. Per-root stdout/stderr each
1MiB, JSON8MiB, total artifact256MiB. Estimated root time62min is unmeasured, not a completion
promise. A cap hit is PARTIAL/UNKNOWN; never raise caps or cut checks after observing failure.

ON is deferred, NOT_READY. Worker15 must freeze its safety tool pin/flags plus same source,
instance and geometry bindings separately. SEL1-C2 14bc57fdb99960240c4944845a3d985c8af4dcf7 is a
reference candidate, not admitted ON evidence here. Intended first ON is supported uninit-checks;
valid-value-checks require separate explicit qualification and are not claimed by uninit ON.
Unsupported ON row is STOP for its domain, never silent removal from a full qualification.
Neither historical FnPtr results nor this OFF batch transfer to ON.

Every positive needs complete zero-unexpected-failure output, every emitted cover SAT and exact
source/generated-instance binding. Every negative needs its named failure(s), preceding expected
successes, reachability and no unrelated failures. Bind property IDs/counts after actual lowering;
source root names/coordinates alone do not prove binding. Preserve original exit/signal/time,
raw RSS KiB/GiB, compiler/driver/backend/target/binary hashes and clean source identity. Missing,
partial, truncated, null/wrong-type exports, NOT_RUN and timeout remain distinct.

STOP immediately on unexpected indirect comparator edge, FnDef-shim/layout/codegen blocker,
property/frame weakening or bucket cap. No compiler patch/new callback model, source-property
weakening or switch to S KeyLess is authorized. Actual runner preparation must reuse the existing
preflight and cover success/error/timeout/partial/missing/null/wrong-type/explicit-NOT_RUN and
source-stage-target mismatch paths before a future dispatch.
