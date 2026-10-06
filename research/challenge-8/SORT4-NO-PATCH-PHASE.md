# Sort4 no-patch feasibility phase

Owner-authorized on 2026-10-06 by the explicit continuation request, starting
from `11e8ead9389cc95fc7d13a24d0c28d7d2d6ba3c5` on
`Tiramisu-Cake/verify-rust-std`, `challenge-8/research`. Earlier phases remain
closed. The patched experiment in [the historical architecture proposal](SORT4-SAFETY-DECISION.md)
is **not authorized**. Current checkpoint: [STATUS](STATUS.md).

## Objective and allowed work

Assess an evidence-backed route to unrestricted safety of actual
`sort4_stable<T,F>` without custom verifier modifications. Target std blob
`e555fce440872898e47fd5114f32eb15401d07df`; full normal and all five unwind
resource obligations are in [SORT4-CONTRACT](SORT4-CONTRACT.md). Contract
clarification and general-rules admissibility remain explicit open questions.

Read prior evidence; compare alternative checked annotations/lemmas on unchanged
VeriFast 26.09 (`809de4596839b739dd999f9e462242c835e3af46`) and the actual official
26.10 release sources/artifact/toolchain. Compare at most one alternative already
approved and integrated tool in detail, using official sources and the repository
integration. That alternative may not be installed, integrated or run in this phase.

Own specifications, checked lemmas, minimal fixture/runner and necessary manual
workflow selection are allowed only if source review yields a concrete new
falsifiable hypothesis. No verifier patches (including historical ones), changes
to parser/translator/kernel/prelude/memory/refinement, assumed ownership bridge,
std runtime/generic-signature changes, Copy/Freeze/purity/nonpanic restrictions,
weakened posts or disabled required checks. No other functions, later phases,
external publication/contact or submission.

## Conditional experiment gate

Before any fixture implementation, record its hypothesis, exact isolated official
profile, obligations, full posts, controls and intended-negative stage/predicate/
location, and outcome-to-decision map in [EXPERIMENT-LOG](EXPERIMENT-LOG.md).
For 26.10 freeze release commit, artifact identity and Rust toolchain; retain the
main project pin. Check target-source and refinement-audit compatibility.

First substantive fixture must match actual c1 at smallsort.rs:626:
`let c1 = is_less(&*v_base.add(1), &*v_base);`, unrestricted T/F, four initialized
source cells, separate four-slot raw scratch and frame. It must prove both normal
return (including Boolean result) and direct panic return with full **current**
source storage/one ownership sequence, callback state, frame and scratch, retaining
legal callback effects. No borrow debt or duplicated independent ownership may
escape. Audit its correspondence to actual c1 and direct unwind; fixture success
would prove a prerequisite only, never whole sort4.

Use one active manual exact-SHA GitHub-hosted run, at most 90 minutes per run,
maximum two runs: primary and one technical correction within the same hypothesis.
Keep normal/unwind/leak/dead-code/refinement checks and required positive controls;
compiler/unsupported/unrelated failures never count as intended negatives.
Read full logs/artifacts. Follow [runbook](AGENT-RUNBOOK.md); server only edits and
orchestrates. If no new candidate emerges, dispatch no repeating diagnostic.

## Deliverables and stop

Write [SORT4-NO-PATCH-ASSESSMENT](SORT4-NO-PATCH-ASSESSMENT.md): compact obstacle
matrix with observed/inferred/unknown distinguished; immutable official sources,
versions and historical experiments; experiment result or reason for no run;
one recommended next task and owner decision. Align STATUS, PLAN, README,
architecture note, experiment log and coverage as claims change. Preserve all
historical results and patched proposal. Commit/push own work; default-main
workflow changes only if necessary through the runbook procedure. Stop at this
phase boundary without declaring all no-patch approaches impossible.

## Entry inspection

HEAD/local and remote research head both `11e8ead9389cc95fc7d13a24d0c28d7d2d6ba3c5`;
clean working tree, only origin pointing at the intended fork; remote main
`0b54bf8f1f2fc4f7d1a7acef4d428ffe34cd7447`. Recent Actions all completed; latest
research run37466906281 SUCCESS. No proof edit or run pending at entry.

## Closeout

CLOSED2026-10-06. [Assessment](SORT4-NO-PATCH-ASSESSMENT.md) records the completed
source comparison and obstacle matrix. No candidate met the conditional gate;
no proof fixture/runner/workflow changes, no dispatch (0/2 budget), no active run.
Official26.10 exact-source compatibility/refinement remains untested. Phase stops
at the single recommended owner contract/admissibility decision; historical
patched experiment and later phases remain unauthorized.
