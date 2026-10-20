# Candidate4 diagnostic return-type repair

Independent /root/r10_review, explicit GPT-6 Luna HIGH, fork none, no delegation:
f9361c7c vsdde5d090 GO. Build3 exact combined-console error atverifast2229:
check_leaks returns symexec_result, not unit. Earlier static review incorrectly
assumed unit; that GO is not compilation evidence and failure is preserved.
Actual verify_expr180 and verifast0 type show SymExecSuccess constructor.
New let-pattern preserves original check result and returns it after unit log;
failed checks throw before receipt. No heap/env/rules/check changes. Existing
source grammar/order, invariant and freshness reviewed deltas unchanged.
Only Cloud compiler can establish compilation; actual target still OPEN.
