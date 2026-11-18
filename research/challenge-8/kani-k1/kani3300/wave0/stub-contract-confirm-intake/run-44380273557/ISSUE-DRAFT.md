# Ordinary stubbing of a contracted function fails with a missing contract closure error

Kani fails to compile `#[kani::stub(f, g)]` when `f` has `requires` and `ensures` attributes, reporting a missing generated contract closure.

Reproduced with Kani built from upstream main on November 18, 2026: Kani 0.68.0, Rust toolchain `nightly-2026-11-12`, CBMC 6.11.0, on Linux x86_64.

Create a dependency-free library crate with these files.

`Cargo.toml`:

```toml
[package]
name = "stub-contract-confirm"
version = "0.1.0"
edition = "2021"
publish = false

[features]
provider = []
verified = []
ordinary = []

[workspace]
```

`src/lib.rs`:

```rust
#![cfg(kani)]

#[kani::requires(x < 8)]
#[kani::ensures(|result| *result == x + 1)]
fn f(x: u8) -> u8 {
    x + 1
}

fn g(x: u8) -> u8 {
    x + 2
}

#[kani::proof_for_contract(f)]
fn provider() {
    f(kani::any());
}

#[cfg(feature = "verified")]
#[kani::proof]
#[kani::stub_verified(f)]
fn verified_control() {
    let x: u8 = kani::any();
    kani::assume(x < 8);
    assert!(f(x) == x + 1);
}

#[cfg(feature = "ordinary")]
#[kani::proof]
#[kani::stub(f, g)]
fn ordinary_stub() {
    let x: u8 = kani::any();
    kani::assume(x < 8);
    assert!(f(x) == x + 2);
}
```

From the crate directory, use the `scripts/cargo-kani` executable from the main checkout where Kani was built. Each invocation selects one harness and uses a fresh target directory:

```bash
KANI=/path/to/kani/scripts/cargo-kani
run_case() {
    env -u CARGO_ENCODED_RUSTFLAGS -u CARGO_TARGET_DIR \
        -u CARGO_BUILD_TARGET -u FLAMEGRAPH \
        RUSTUP_TOOLCHAIN=nightly-2026-11-12 RUSTFLAGS= KANIFLAGS= KANI_LOG= \
        RUST_BACKTRACE=0 NO_COLOR=1 KANI_FAIL_ON_UNEXPECTED_DESCRIPTION=true \
        "$KANI" kani --manifest-path "$PWD/Cargo.toml" --lib \
        --no-default-features --features "$1" --exact --harness "$2" -j1 \
        -Z function-contracts -Z stubbing -Z export-json \
        --export-json "$PWD/$1.json" --output-format=regular \
        --target-dir "$PWD/target-$1"
}
run_case provider provider
run_case verified verified_control
run_case ordinary ordinary_stub
```

The provider and verified-stub harness each independently exit 0 and report `VERIFICATION:- SUCCESSFUL`. The ordinary-stub invocation exits 1 with:

```text
error: Failed to find contract closure `__kani_recursion_check_f` in function `stub_contract_confirm::f`

error: Failed to execute cargo (exit status: 101). Found 1 compilation errors.
```

Cargo also reports that the library could not compile due to one previous error.

Expected behavior: support ordinary replacement of the contracted function, allowing the `x + 2` assertion to verify, or emit a clear user diagnostic explaining that ordinary stubbing of a function with contract attributes is unsupported and identifying the supported alternative. The generated closure error does not explain the attribute combination or how to resolve it.

*Disclosure: this issue and reproducer were prepared with the help of AI assistants.*
