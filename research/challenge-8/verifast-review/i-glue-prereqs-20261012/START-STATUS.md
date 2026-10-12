# VeriFast maintainer — I / actual glue compatibility preflight

**BLOCKED: combined tool source candidate NOT_PREPARED / UNBUILT / NOT_RUN.**
Fixed I toolb6cb276a/package4214cbe0 vs glue a158398e/project6283377b:
необходимы новые compiler-qualified layout и StorageLive/live-origin/numeric-span
rules, отсутствующие в frozen I. Отдельный trust decision и receipt transport через
I strict freeze обязательны; whole merge chain также теряет I slice/pointer-drop/
FRAME/native/MDnew/strict/ZST paths. Семантика tool не менялась.

[Compatibility blocker](verifast-review/i-glue-compat-20261012/COMPATIBILITY.md),
[exact hashes/dependencies](verifast-review/i-glue-compat-20261012/INPUTS-AND-SOURCE-COMPARISON.json),
[conditional future gates](verifast-review/i-glue-compat-20261012/FUTURE-GATES.md),
[independent GO](verifast-review/i-glue-compat-20261012/INDEPENDENT-REVIEW.md),
[commands](verifast-review/i-glue-compat-20261012/REPRODUCE.md).
F1 остаётся CLOSED; опубликованный patch применён только к собственной runner628
copy. Service15 cases (1saved/14synthetic) +8False проходят; v8 proof/qualification
status не повышен. Separate v8 Builda9613c24 признан, moving merge head не читался.

Main6e1a8e59 и ACKea155143, I/ready upstream as_mut_ptr/ManuallyDrop::new и прежние
PASS сохранены. B1/B2/O23, receiver/end controls/actual panic cleanup остаются
отдельными obligations; v6 PASS не переносится наv8 или отсутствующий combined tool.
Cloud0/newproof0, no compiler/extraction/refiner/verifier execution, merge/upstream
PR/profile acceptance, active merge/coordinator/foreign worktree changes.

Сессия CLOSED в пределах60мин. Reviewed package fbac3cd7; remote/API tree/manifest
проверены. [Publication](verifast-review/i-glue-compat-20261012/PUBLICATION.json),
[cleanup](verifast-review/i-glue-compat-20261012/CLEANUP.json): temporary service
fixtures auto-removed, unused own persistent /tmp artifacts none, additional0bytes freed.
