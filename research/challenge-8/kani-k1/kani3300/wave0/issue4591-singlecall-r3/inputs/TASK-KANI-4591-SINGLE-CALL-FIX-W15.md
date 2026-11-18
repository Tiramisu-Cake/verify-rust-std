# Fresh15 — #4591 native single-top-level-call diagnosis and offline repair

ISSUED owner01:00, /new15, currenthigh/FastOFF; no subagents/model changes.
Read kani3300/wave0/issue4591-singlecall-postrun/INPUTS.json and frozen authorad50,
review0f4, GO1a32. Native failure is authoritative; no static/mocked PASS overrides
it. STOP only a real blocker, not volume/context. Clean-room allows main plus
issue#4591/comments/reproducer; no unrelated third-party PR implementations.

Baseline PUBLISHED failed head6fca00af805b5c62b58e3e3f29eef183d6939907,
tree7a3d5c05b5d663d515c198b2bfa7c4926ae133ac, parentmain969f4648980a8e66cd0ca32fd3e714a55ac32cef.
All3CIterminal: Format/DenySUCCESS, KaniFAILURE (connectedmetadata). Coordinator
reports first kani suite658pass/1fail, replacement_contract_target in ordinary_stub.rs
hits single-top-level-call error for contracted_replacement::{closure}. Other
harnesses in file verified; expected/script-based-pre/ui suites NOT_RUN; remaining
regression matrix cancelled by fail-fast (reason coordinator-reported).

1. Focused bounded failure intake/provenance: native run/job/step metadata, exact
   supplied error/counts provenance, all12 jobs accounted with native outcomes.
   Connected summaries/explicitly allowed compact evidence only; no full/rawlogs,
   archives/GCS bypass or new native run. Missing exact detail UNKNOWN. Do not
   carry old F4 no-runner/advisory classification or claim complete green CI.
2. Trace exact diagnostic in pinned969f/tool+fix source: PFC generation, selected
   target reachability, top-level-call counter/guard, FnStubPass/body source and
   FunctionWithContractPass. Show effective checked calls for BOTH positive
   replacement_contract_target AND expected-suite replacement_provider_postcondition.
   Distinguish invalid fixture under existing PFC rules from a genuine routing
   regression; provide source citations and actual-vs-predicted boundaries.
3. Minimal supported repair. Respect exact-target reachability AND single legal
   top-level contract call; do not weaken/skip their guards or mask failure.
   Prior direct0+copied1 arrangement is not mandatory if source establishes it
   invalid. Preserve core ordinary-stub regression (safeu8f/g, requires/ensures/
   both) and meaningful same-function PFC/stub_verified controls plus safety and
   negative cases. If unsupported mixed PFC-provider+ordinary replacement case
   must be split/replaced, explain preserved goals and coverage limits; do not
   silently drop coverage or turn a supported semantic case into compile-error
   expectation. No unreachable/dummy-call tricks solely to bypass validation.
   Negative expected file shares the pattern and MUST be repaired/audited despite
   never running. Main#4591 issue i32 overflow remains a real caller-counterexample.
   Prefer fixture-only change if guard diagnoses fixture; compiler edits only
   with concrete source-established need and minimal reasoning. Broader design
   ambiguity ->root before expanding. Preserve already native-verified cases.
4. Regression validation: meaningful source-call-shape/guard/oracle checks which
   distinguish frozen6f defective fixture from repaired supported fixture, explicit
   limitations (not compiler/MIR/typecheck). Revisit all affected PFC harnesses and
   expected outputs, no guessed property quotas. Do not invent fixed nativePASS;
   nextCI is NOT_RUN. Preserve original/nativefailed/staticapproved history.

Create NEW isolated repair worktree based on exact published6f, local[skip ci]
repair candidate soleparent6f (future final nonskip SAME-TREE sibling sole6fparent
allows FAST-FORWARD remote branch;969f..future contains old6f+newnonskip, never
skipped candidate). No force/push. Recheck upstreammain read-only; report drift,
no automatic rebase/openPRbranch update. Own immutable
kani3300/wave0/issue4591-singlecall-r3/: DIAGNOSIS.md, nativeevidenceprojections,
source/base/tree/parent pins, patch/replay/invariance, tests/oracles/validation,
fullstandardpushCIrequest/finalheadgate/PRdraft/HANDOFF/manifest. All standard
workflow/scripts/actions/toolchain/dependency bytes match reviewedbase; no F4,
customCI/dispatch/cron/enable. Full futureKani all5OS/alljobs+Format/Deny, PR-only
scope deferred. Morning PR text STYLE, only actual current evidence/pending repair.

Current item1 31/31 EXHAUSTED; no automatic repeat/refund. Source offline work and
review authorized. After SAME11 exactAPPROVE root prepares GO-request HOLD FOR
OWNER_EXTRA_ITEM1_GRANT (potential +1 only owner morning). Never dispatch or mark
CIauthorized from static approval. Item2 12/17,total43/48 reference; S3independent.
No compiler/cargo/rustc/rustfmt/Kani/CBMC/expansion/verifier/fullrunner/CI/rerun/
cancel/push/PR/issues/comments/rawlogs/archives/GCS/ledger/reservation/budget.
Ownpaths --only [skip ci], Tiramisu-Cake <igkharin@gmail.com>. READY fullg0/source/
tree/parent/diagnosis/patch/test/CI pins ->SAME11delta, no publication.
