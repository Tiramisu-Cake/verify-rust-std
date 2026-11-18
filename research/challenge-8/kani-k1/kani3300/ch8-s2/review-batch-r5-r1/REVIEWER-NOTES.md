The initial targeted transcript and its nonzero exit are preserved unchanged.
The first diagnostic helper invocation used an incorrect expected exception
message literal (`unrequested_process_group_escape`); it stopped before saving
its report. That reviewer assertion was corrected to the inspected runtime
literal `unexpected_process_group_containment_gap`. Its unsaved attempts are
not counted as evidence. The saved diagnostic contains one exact-test repeat
and three instrumented cases, including synchronized and deliberately delayed
sampling. No candidate/test/runtime bytes were edited.

g0 HEAD advanced concurrently from the pinned reviewed package to unrelated
coordinator commits touching CH8-DISPATCH-LEDGER.md and a W15 task. Those changes
were not made or staged by this reviewer. Exact dc8d package and original
review/package paths remain pinned; the independent verifier checks the package
commit directly so unrelated later HEAD commits do not redefine its subject.
