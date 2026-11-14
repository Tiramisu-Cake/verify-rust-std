# S2 formatting and source-coalescing follow-up

READY `bf8170b28afb682f8dd55a94199caa247736d8fa`

Tree `9ff24911693123853c88cca21a0baf764b63b2bf`; branch fix/kani-3300-c2-s2. Separate format commit `3c2af5d5e54ebd15784e34b46e53fd54d7090c4e`, followed by tests-only commit `bf8170b28afb682f8dd55a94199caa247736d8fa`. Author/committer Tiramisu-Cake <igkharin@gmail.com> through git -c. Source clean; research uncommitted; no push/CI/builds. Authorized rustfmt ran and is idempotent on all affected files.

Old four source controls are NONDISCRIMINATING: candidate and old baseline both pass. Summary lacks numeric AllocIds/symbol maps; PASS does not establish absence of coalescing. Static reconstruction identifies the overlooked qualification route through T's original initializer MIR, which can qualify its inner &5 too. This is a source explanation/inference, not an observed trace of that CI.

Equal Allocation contents do not imply one AllocId. Added two source candidates using an aggregate const initializer and a CTFE-only const-fn initializer to avoid that extra typed-origin route. Old expectations are unchanged. Both new cases and exact mixed-qualification symbol binding are NOT_RUN/UNKNOWN; F5 is not yet reproduced on source. Its source unreachability is not established. The register repair is currently supported by the executed unit matrix, with genuine conflict guards retained.

Coordinator-reported f96 CI: build/clippy PASS, unit9/0, four controls PASS, kani24/0, expected208/0 (2 ignored), ui17/0, script2/0, contract oracles/modes PASS; format FAIL repaired locally here. Composition FAIL at the prior isolated-ordinary_ensures_legal stop remains narrowly S5-deferred, not all-PASS. No final-head CI or full C2 gate claim. Next: bounded baseline/candidate new controls and binding trace per CI-REQUEST.md.
