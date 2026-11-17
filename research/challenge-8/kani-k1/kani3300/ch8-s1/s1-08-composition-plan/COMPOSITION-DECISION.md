# S1-08: conditional composition of two evidence origins

PREPARED_NOT_ISSUED. Coordinator decision under the owner's request after retry GO,
2026-11-17. No retry result or qualification is asserted by this preparation.

## Decision

Allow a **separate origin-partitioned composite receipt** for the existing bounded,
source-reported S1 policy, conditional on the gates below and independent review of
the resulting adapter/receipt. This is an explicit extension of the former
single-run task; it does not redefine either historical run or relax a proof gate.

Selection is fixed before reading retry outcomes:

- Run44095954742/attempt1, intake6d300f3ab9801c808612b562588af06e0f7b4ff9:
  only its13 complete groups/33 rows, excluding cell-u34.
- Run44128268928/attempt1: the **entire** cell-u34 group, exactly
  stable_default_cell and unstable_default_cell, after committed terminal intake.
  Both must come from this complete group; do not substitute the older unstable
  source SUCCESS or select individual properties across attempts.

The old two UNKNOWN cell observations remain in their immutable intake/diagnostic.
If retry is incomplete, its rows remain UNKNOWN/PENDING; the33 original rows may
still be assessed. No invented RESULTS or promotion through a healthy row in an
incomplete group. No other run/attempt or best-of-result selection is authorized.

## What this does and does not establish

Composition loses a single successful workflow/14-of-14 same-run matrix, one
request/control/invocation identity, a uniform600s profile, and any measured full
matrix wall/phase/ordinary-CI-fit claim. Original run remains FAILED. Cell retry
uses1200s and child3300s; its success does not prove the600s profile. There is no
measured composite invocation, simultaneous binary snapshot or aggregate runtime;
do not sum overlapping jobs into one run time. No causal claim about kani::assert.

Per-root bounded proof observations can be combined only after establishing the
same semantic verification inputs and unchanged producer semantics across these
two reviewed profiles. Time limits and selection are resource/scheduling deltas;
no assumption, expression, geometry, checks, solver or evidence decoder may drift.
Maintain separate raw request/control hashes and invocation IDs, never rewrite
them to a synthetic common hash. Source-reported producer trust stays explicit;
independent AST/MIR/compiler correctness and B1/B2/general proof credit stay NONE.

## Required gates

1. Replay each origin separately with its own exact executed collector/request.
   Validate terminal attempt/head/tree/parent, source99e/tool0aac, original group
   identities, artifacts/digests, full stock/rich/native reconciliation, protected
   binary before/after snapshots, original exits/exceptions and completeness.
   Original collector's missing cell and retry collector's13 unselected missing
   reference groups are retained. Never feed mixed raw roots to one collector:
   their request hashes differ and its exact hash checks must keep rejecting that.
2. Verify the two requests/control trees against the exact reviewed delta from
   7c to e27. Compare full row/domain/type/N/threshold/unwind/mode/variant bindings,
   source and variant file hashes, model/contract/ROLE-MAP, flags/cfg/solver/checks,
   tool identities and measured protected binaries. Across origins require the
   same protected binary digest/version identities as well as intact snapshots
   within each; transport paths/timestamps are not binary identity or proof input.
   Only reviewed cell timeout600→1200, derived/scheduling/profile metadata,
   preflight/tests and their payload hashes may differ. Unknown/mismatch is a
   specific composition gate, not a guessed equivalence or a new compiler audit.
3. The composite adapter selects only the fixed13+1 partition, checks exactly35
   unique declared row keys, and preserves each group's full origin tuple:
   repository/run/attempt/trigger/control-tree/request/group/invocation/artifact
   and member evidence hashes. Raw receipts stay immutable and are referenced.
   Each U/PFC/role/cover/oracle component is keyed to its **own** row origin and
   source/tool/request identity; never transplant old components by property ID.
4. Preserve all existing local gates:111 fresh exact role labels and16 fresh
   semantic bindings/sets, actual required113 SAT covers,8 predeclared sole FAILURE
   negatives including spans95/101, U per-site premises, Profiles-v4 full concrete
   PFC chains. Counts of all exported properties/U are measured, not quotas.
   Mandatory post/frame/relation UNREACHABLE still blocks. No S1-07 qualification
   totals or old cell diagnostic IDs/labels are imported as proof observations.
5. Re-derive the dependency graph from current specs. The reviewed reference has
   8 companion edges and4 N0..3 unions, none touching the cell pair: therefore all
   stay entirely in44095954742. Preserve exact same-run companion pins, qualified
   targets and transitive/least-fixed-point rules; union membership/domain/covers
   and all qualified members stay mandatory. Any unexpected cross-origin edge
   remains PENDING and is reported; this decision grants no companion waiver.
6. New adapter tests must discriminate origin/request substitution, duplicate or
   foreign rows, incomplete cell/one-row splice, wrong timeout/config/source/tool
   or binaries, missing mandatory role/U/PFC/negative/cover, companion and union
   corruption. Reuse reviewed rules, not a new broad classifier. Independent
   review of the new adapter and receipt is required before final admission.

Reference dependency graph was checked in
s1-07/run-43923266772/accept-v3/ACCEPT.json: its8 companions and4 unions involve
no stable_default_cell/unstable_default_cell. Current specs must confirm this.
The former TASK-CH8-S1-08-ACCEPT-W11.md describes a single-run stage and is not the
issuance contract for this composition. New task and INPUTS.json are authoritative.

## Activation and limits

Only after terminal retry44128268928/attempt1 may the coordinator issue retry
intake. Only after its exact committed handoff may the coordinator issue composite
acceptance; failed retry still permits a truthful partial assessment. Fresh pane
sessions, existing pane models, no nested delegation; compact reuse of reviewed
helpers. This preparation does not issue either task or authorize another run.
Current ledger bfccbbfd5d: item2 9/14, total35/40. No further CI/rerun/cancel/push,
reservation/budget/ledger/source/control/policy expansion is authorized.
