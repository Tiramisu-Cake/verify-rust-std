# U-02 result retained for U-03

Source: task TASK-CH8-PR02-RESET-U03.md at g0 input f3658d28cd. These are
coordinator/task-reported bounded artifact facts; this preparation did not
read raw logs or independently audit native results.

- Run `43780092728`, trigger prefix `235b30ffb8`, package
  `952ea771be3827a495a9c9f29ad6a015bd796fc7`; artifact bounded.
- PR02 `932fb8395a` plus U-02 fix, patch SHA256
  `d43f251e5694c9ca5f15ee20134f5035009223bdd1d50b9b79c1d0b30093e0cd`:
  old-build, fmt, build, clippy, compiler units 66/66, compiletest-build,
  expected uninit 56 passed/2 ignored and expected function-contract
  134 passed/4 ignored all exited 0.
- `script-based-pre autoharness_entry_reset_*`: 5 passed, 2 failed.
  Failed fixtures: `autoharness_entry_reset_initialized_read` and
  `autoharness_entry_reset_uninit_read`. The reported sole failed check was
  `Interaction between raw pointers and unions is not yet supported`
  (`main.rs:14`, `initialized_read`). This identifies the fixture problem;
  it does not establish either requested read outcome.
- The runner stopped there. `script-based-pre-autoharness` and `old-controls`
  were **NOT_RUN**. No matched-old-control acceptance is claimed for U-02.

U-03 changes only the two fixture bodies and CI gate orchestration/static
checks. Compiler diff identity is recorded in COMPATIBILITY.json. Native U-03
outcomes remain NOT_RUN; no new proof credit.
