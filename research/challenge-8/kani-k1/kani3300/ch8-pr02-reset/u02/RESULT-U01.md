# U-01 result retained from coordinator task

Source of facts: `TASK-CH8-PR02-RESET-FIX2-W15.md` at g0 input `e3fce08411b8a222fc7e7b6d7e9969df3cbae407`. This stage did not independently retrieve or audit CI evidence or raw logs.

Run `43777434715`, trigger `e4bf2df0ca`, package `b4edbb18bc8a490197420aac0964a7d55b284380`, original source `f695f653efaa1f7ac6774a079104de8cc0ff81fc`.

- B SUCCESS: SEL1 `14bc57fdb9` plus source fix; original #4854 autoharness `reassemble_ptr_fragments_in_static` completed SUCCESS, 154 properties, 0 failed (previously fatal `reset is absent`). Explicit companion `explicit_proof_observes_initialized_null` SUCCESS, 156 properties, 0 failed.
- Artifact `ch8-pr02-reset-b-43777434715-1`, ID `14187497167`. Export SHA256s were supplied only in abbreviated form: `ed9b4c86…a7e8` and `11933e0e…eca3`. Full digests are UNKNOWN here and have not been reconstructed.
- A FAILURE due to fixture packaging; no A upload step existed, so no artifact. The task reports bounded job-log facts: patched PR-02 and old PR-02 builds OK; compiler units 66/66; suites 56 passed/2 ignored and 134 passed/4 ignored, no failures.
- Compiletest then failed with `couldn't find config.yml file for exec test in .../tests/script-based-pre/autoharness_entry_reset`, exit 101. Exec discovery is nonrecursive and requires config.yml in every top-level test directory (`tools/compiletest/src/main.rs`, `collect_exec_tests_from_dir`).
- Seven new regressions and their matched old PR-02 controls: NOT_RUN in U-01.

U-02 changes fixture paths and CI receipt packaging. Compiler diff, 28 fixture file bytes/modes, B runner and B inputs remain identical (COMPATIBILITY.json). This justifies omitting the repeated B arm under the task's permission. U-01 results remain source-reported; no independent B1/B2 or emitted-model proof credit is established by this stage.
