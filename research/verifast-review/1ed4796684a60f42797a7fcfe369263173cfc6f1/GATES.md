# Focused gate results

Verdict **FOCUSED_VALIDATION_PASS**. Links are relative to the immutable packet root. Full focused source-built execution is Build 8dd10da5-8a6b-40d7-88e2-7f4271324f17 at infra/source cf938bb31348c598de3d261f4169fa13a4bd11ab and tool/tests 8f0b701e9f2a3da124372c5d37d4cda408d45001. Each baseline/candidate fixture has identical source bytes. Read [classifier](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/proof-audit.json) and [independent structural review](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/manual-structure-review.json).

| Gate | Result | Exact evidence |
| --- | --- | --- |
| Exact delivery / identities / component provenance | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/restore-receipt.json) |
| Both consoles compiled from exact restored inputs | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/runtime-components.json) |
| Baseline forget: normal return/leak then concrete orphan dead code | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/cases/baseline/forget/full-verification.log) |
| Candidate generic forget | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/cases/candidate/forget/full-verification.log) |
| Ordinary caller: function-specific Continue unwind and return | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/cases/captures/shared_cleanup/verified-ast.txt) |
| Shared cleanup: correct call, cleanup3, reachable unwind return | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/cases/captures/shared_cleanup/candidate-normal-mir.txt) |
| False-normal: exact false post line3, original should_fail completes | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/cases/candidate/false_normal_post/exit-status.txt) |
| False-unwind: exact on_unwind_ens false line14, originals complete both sides | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/cases/candidate/shared_false_unwind/exit-status.txt) |
| Contradictory precondition rejected by mandatory dead-code checker | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/cases/candidate/dead_code_pre/full-verification.log) |
| Tail control: function-bound bb4 Return, bb5 UnwindResume; no extra dead goto | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/manual-structure-review.json) |
| All MIR/decode/AST/refiner stage statuses and hashes | PASS | [file](evidence/8dd10da5-8a6b-40d7-88e2-7f4271324f17/selected/allprooflogs/cases/captures/shared_cleanup/capture-status.json) |
| Five existing native upstream regressions | PASS | [file](evidence/38b9ad73-55de-452e-9213-bbe4be886562/selected/proof-audit.json) |
| Full upstream suite | NOT_RUN | — |
| Consumer integration / pin acceptance | NOT_RUN / NOT_ACCEPTED | — |
| Upstream acceptance | NOT_ACCEPTED | — |

Baseline false-normal diagnostic rejects exactly at line3; baseline original allow is NOT_RUN as permitted by the original focused plan (it may hit the baseline orphan defect and would then carry no negative credit). Candidate false-normal original and both false-unwind originals are the acceptance gates and complete successfully.

Original and diagnostic source, stdout, stderr, exit receipts and detailed capture statuses are separately preserved alongside these files. Refiner unwind TODO remains: exit0 and equal MIR were supplemented by function-specific CFG/AST transitions and exact negative outcomes. Native upstream regression options include ignore_unwind_paths where upstream requires it; those lanes carry no focused unwind credit.
