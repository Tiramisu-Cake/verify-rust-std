# SEL1 fixture followup43609527860

READY ec85b782a1b7156ad434cfac25403acd4e326dc1 + e59c3527a852d805a4d1317a400a3229b398eead

Source changes exactly five test files. Four goldens now expect the observed `*const u8` diagnostic; all exact one-failure summaries, intended failure descriptions, useful SUCCESS assertions and FAILED verdicts remain. Pointer-hole sources select between allocated MU<u8> hole/legal slots, then call read_volatile::<u8> on the selected pointer; padding sources read byte1 of repr(C) Padded (u8/u32), with typed fields checked first. In all four cases this is the intended byte read, not a pointer payload load: the source intrinsic is volatile_load(src) for T=u8. The uninit visitor maps VolatileLoad to Check(args[0]), and build_get_and_check formats the pointer operand's type (`*const u8`) while checking the u8 pointee layout. The coordinator summary confirms the only failure is read_volatile::<u8>.safety_check.1; no alternate failure is blessed.

Nested.bytes keeps the same [MaybeUninit<u8>;2] field/type/construction and select/refusal path. A field-local allow(dead_code) documents its intentional absence of reads; -D warnings is retained. Adding a payload read would change the refusal control, so none was added. Production compiler/driver/library diff againstb6f1b08eb5 is empty. Owner rustfmt wrapper and --check passed.

Replay bound to ec85b782a1b7156ad434cfac25403acd4e326dc1, std6075e7ce17 and same six ON rows. Runner function AST, workflow, tests and std patch unchanged.29 service and7 packaging Python tests pass; exact0c1 delta generation/--check and candidate reverse-check pass. Delta ../ci/ci-overlay-delta.patch, SHA256d563532e1315780fefdd53fa471b30a60e9d2bf1b5f146f4605153c3865e9409.

Prior quick43609527860: owner reports fmt/build/clippy PASS,24/29 select controls ok,5 fixture failures; other suites intact and composition known S5 debt. New native/replay outcomes NOT_RUN. No local builds/push/CI. Both clones clean; source and overlay author/committer Tiramisu-Cake <igkharin@gmail.com> via git -c. Research uncommitted.
