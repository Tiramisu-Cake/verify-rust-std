# SEL1 quick CI run 43609527860 (b6f1b08eb5 + CI-only 483da65d23) — coordinator

- Format, build, clippy: PASS. kani 24/0; ui 17/0; script 2/0; json: oracles/mode ok, composition FAIL (S5 debt).
- expected: 228 passed / 5 failed (2 ignored). select-unpredictable controls: 24/29 ok.
- 4 negatives (padding/selected_{true,false}_padding_stays_uninitialized, pointer-hole-{true,false}): each run is
  `** 1 of N failed`, the single failure is `std::ptr::read_volatile::<u8>.safety_check.1` (core/src/ptr/mod.rs:2159)
  with description "Undefined Behavior: Reading from an uninitialized pointer of type `*const u8`".
  The goldens expect "... of type `u8`" — golden spelling bug (Kani names the pointer type), not a semantic miss.
- nested-unsupported/main.rs: compile error under `-D warnings`: "field `bytes` is never read" (main.rs:13) — test bug.
