# Independent C2 scope review before Cloud

Reviewer `/root/review_composition_design`, read-only GPT-6 Sol, reviewed the
semantic design and concrete delta independently of implementing worker.
Result: GO for diagnostic Cloud execution, not profile/theorem acceptance.

Localized findings were returned to worker and corrected: allow only the exact
original duplicate `bh0` pair; exclude the 18 future declarations from reachable
bounded output rather than executing them after the C2 join; label the two false
unwind assertions as branch reachability controls, not false-post controls.
Pinned full pre-AST still retains all declarations and full runtime inventory.
Revised translator `daf29b03fbb7aa10e6f580c70780a9fdc5a2eb6d3f4470e1c38673212ca3d9a3`,
patch `4851c87be76630a627ff04d351ba6146879568eb877a28235a95d4cbea913925`.

The concrete two sibling scopes, C1 direct-unwind exit before C2, both CURRENT
recoveries and two separate compiler-derived Output=bool registrations fit the
fixed source/MIR/pre-AST design. The original unbound scaffold must still refuse
before proof. Default-off C1 and full original bounded normal/unwind posts,
strict dead-code, return and leak remain gates. Main integration invokes this
only after the existing fresh C1 proof and refused unbound discovery; separate
profile inclusion enables this experimental route, never profile acceptance.

Admission remains PENDING until fresh raw post-AST and heap traces are reviewed.
`DeclStmt` may produce objects (`verifast.ml` declaration implementation), so
counts alone cannot certify placement. The first-textual-StorageLive test alone
is not a CFG proof; the revised driver also audits both exact complete graphs.
Review graph paths, retained declarations and produce/free on normal, C1 unwind
and C2 unwind after execution. Attribute each negative to its first intended VC
predicate/location; setup, frontend and unrelated helper failures do not count.
An experimental VF0 is not acceptance of a tool profile or whole-sort4 summary.

Main checked own files, Python AST syntax, patch SHA/profile match, exact sorted
recipe paths and `git diff --check`. These static checks run no compiler/proof.
Worker's saved-A5DE parser/CFG replay is isolated saved-input service testing;
fresh bound C2 is NOT_RUN at this checkpoint.
