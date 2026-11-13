# E1 prepared result — SOURCE-REPORTED / NOT_RUN

Source candidate: dc24745c68951effb702a4302e84481ca74bc51a.
Source tree: 4e17cba9a9ae0bbc625f5fc6c147ff1cca17dc04.
Base: 94c00a8859bc9e4f0f1b7db73a95dbee88f6213a.
Isolated clone /root/kani-fix-3300-e1, branch fix/kani-3300-e1.
Author/committer Tiramisu-Cake <igkharin@gmail.com>, set through git -c.

Prepared bounded constant ordinary-union mask materialization, exact projected raw-field setter,
and whole-call/callee-entry plus defensive unsized-transfer guards. Added 17 singleton controls
and one compiler-side unit. Production diff is limited to three check_uninit files; all other
source deltas are new part1-edges controls. Runtime/model policy and W15-owned files unchanged.

Static checks PASS: fixture/expected/root/hash/scope map, git diff --check, approved scratchpad
rustfmt --check; inherited strong-oracle Python tests 21/21 PASS. Independent read-only Luna HIGH
static review found no concrete issue; actual type/MIR/generated behavior remains unverified.
Compiler unit and all Kani fixtures NOT_RUN. No cargo/rustc/Kani/CBMC/Miri/build/push/CI/Cloud spend.

Release disposition: HELD / no final-export or M3 qualification yet. Whole immutable masks reuse
existing controls. Nonzero-offset/subrange and relocation-bearing immutable origins remain
outside M1 admission; unserved legal paths may falseFAIL. Shared named-static behavior requires
separate binding to its existing path, not blanket rejection. Their legal expectations stay
SUCCESS; initialized-byte failures are limitations, not a golden for UB. The paired hole is
unqualified until its legal companion and exact failure set pass. Coordinator must disposition
any confirmed limitation before release. No new domain/model/admission is implemented.

By-value DST reachability uses the inherited unsized_fn_params source pattern with actual
unsized self. Compiler validity and Slice/Move binding still require CI; Box/fat-pointer argument
or E0277 is not equivalent qualification. The explicit guard is a declared unsupported boundary,
not proof credit. Source package is READY for coordinator review and CI per CI-REQUEST.md;
this READY does not assert runtime correctness or final release readiness.
