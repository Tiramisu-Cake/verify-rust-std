Target: comment on model-checking/kani#3762 (open; no comments as of 2026-11-16).
Evidence: run 43830763471 (clean upstream 0aac16ef62), rows copy_integer / raw_bool_overwrite / raw_bool_read.

---

A data point on how this currently affects plain integer copies: with `-Z valid-value-checks`, `copy_nonoverlapping` is reported as unsupported even for `u8`, which has no invalid bit patterns.

```rust
#[kani::proof]
fn copy_integer() {
    let src = kani::any::<u8>();
    let mut dst = 0u8;
    unsafe { core::ptr::copy_nonoverlapping(&src, &mut dst, 1) };
    assert_eq!(dst, src);
}
```

```sh
kani -Z valid-value-checks copy_integer.rs --harness copy_integer --exact
```

Kani 0.68.0 at `0aac16ef62da9e9d5645782d458593e5d78143ba`, CBMC 6.11.0, x86_64 Linux. Result: VERIFICATION FAILED with exactly one failed check:

```text
std::ptr::copy_nonoverlapping::<u8>.unsupported_construct.1
Kani currently doesn't support checking validity of `copy_nonoverlapping` for `*const u8`
```

The assertion itself passes. This comes from the unconditional branch in [check_values.rs:491–497](https://github.com/model-checking/kani/blob/0aac16ef62da9e9d5645782d458593e5d78143ba/kani-compiler/src/kani_middle/transform/check_values.rs#L491-L497). Since most code that copies memory does so for types without validity requirements, any harness that reaches such a copy cannot pass with this flag, which makes the flag hard to use on larger code bases.

A narrower first step could be to treat copies whose pointee type has no validity requirement (integers, raw pointers, and aggregates made only of them) as needing no check, and keep the unsupported check for everything else. Types with restricted bit patterns, such as the `char` example in the description, would keep stopping at the unsupported check until full support exists.

*Disclosure: this comment was prepared with the help of AI assistants.*
