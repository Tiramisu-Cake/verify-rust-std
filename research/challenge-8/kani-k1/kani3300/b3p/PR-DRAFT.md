# Avoid CBMC aborts when copying padded unions with zero-sized fields

Typed copies of padded unions with zero-sized array fields can abort CBMC 6.11.0 with status 134 under the default checks, without `-Z uninit-checks`. The matched base run reports `simplify_utils.cpp:345`, in `bits2expr`, at the positive element-width invariant `el_size_opt.has_value() && *el_size_opt > 0`.

Union code generation retains the positive-padding wrapper but replaces its zero-width **physical payload** with the existing empty-unit struct representation. The original **logical arm type** remains available for projections and indexing. Nonzero payloads and the no-padding path, including all-ZST unions, retain their existing behavior. This avoids reconstructing a zero-width-element array from the padded wrapper's bitvector.

The exact reproduced input is [the seven-harness default-check fixture](https://github.com/Tiramisu-Cake/kani/blob/dc590936c56556ecfb20fc714da06fcb13e884db/tests/expected/uninit/zst-union-arm-no-checks/main.rs) at `dc590936c56556ecfb20fc714da06fcb13e884db`. Its [executed `array_typed_copy` harness](https://github.com/Tiramisu-Cake/kani/blob/dc590936c56556ecfb20fc714da06fcb13e884db/tests/expected/uninit/zst-union-arm-no-checks/main.rs#L56-L67) includes the ZST projection after the typed copy. See the matched [base run](https://github.com/Tiramisu-Cake/kani/actions/runs/43115481098/job/130842240466) and [fix run](https://github.com/Tiramisu-Cake/kani/actions/runs/43115485052/job/130842254653). The final placement is [tests/expected/zst-union-arm/main.rs](https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/tests/expected/zst-union-arm/main.rs), with its [seven-success golden](https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/tests/expected/zst-union-arm/expected), at `6db3c4dabd4a368314eb8e2b71d21d1eee721593` in the general expected suite.

The regression scope is typed copies with a byte-array payload, a padded C-layout payload in C- and Rust-layout unions, a containing union at a nonzero offset, aligned ZST/all-ZST controls, and typing/in-bounds projection for nondeterministic indexing constrained to `index < 2`. Byte-array assertions read an initialized arm covering the full extent; padded-payload assertions read only the initialized `byte` and `word` fields. They do not establish reading or preservation of padding bytes, physical ZST writes, general ABI/noinline call-return coverage, or escaping-reference alignment.

## Testing

These are historical results on the exact revisions below, as recorded by the B1–B3 audit. No new compiler, verifier, or CI run was performed for this repackaging.

| Historical run | Source revision, actual CI checkout, and result |
| --- | --- |
| [43115481098](https://github.com/Tiramisu-Cake/kani/actions/runs/43115481098) | Base `bf9c58e662fd65c64381ef2ac97a6397ffc0693a` plus fixtures at `dc590936c56556ecfb20fc714da06fcb13e884db`; CI checkout `f304106019f81f09a1547a52808e3fd0c59556bb`. Default selector: 3 SUCCESS, 4 CBMC aborts with status 134. Overall quick workflow failed. |
| [43115485052](https://github.com/Tiramisu-Cake/kani/actions/runs/43115485052) | Backend fix `9dddcb1134f8a55ee3a4451df9513941ca3c8fc3`; CI checkout `9ce21fcdf5306707968357ee579a35d9d8a6973b`. Same default fixture and golden: 7/7 SUCCESS. Overall quick workflow failed. |
| [43117729467](https://github.com/Tiramisu-Cake/kani/actions/runs/43117729467) | Final placement at `6db3c4dabd4a368314eb8e2b71d21d1eee721593`: Ubuntu 22.04, Ubuntu 24.04, and Ubuntu 24.04 ARM64 regression PASS; expected suite in each: 548 passed, 13 ignored. Perf, LLBC, docs, and benchcomp PASS. Overall workflow **cancelled**. |
| [43117729474](https://github.com/Tiramisu-Cake/kani/actions/runs/43117729474) | Separate format/Clippy workflow at `6db3c4dabd4a368314eb8e2b71d21d1eee721593`: PASS. |
| [43117729608](https://github.com/Tiramisu-Cake/kani/actions/runs/43117729608) | Separate cargo-deny workflow at `6db3c4dabd4a368314eb8e2b71d21d1eee721593`: PASS. |

The four matched base aborts were `array_typed_copy`, `padded_typed_copy_c`, `padded_typed_copy_rust`, and `zst_arm_at_nonzero_offset`. The three already-passing controls were `aligned_zst_typed_copy`, `all_zst_union`, and `zst_array_indexing`. The [source-to-source change](https://github.com/Tiramisu-Cake/kani/compare/dc590936c56556ecfb20fc714da06fcb13e884db...9dddcb1134f8a55ee3a4451df9513941ca3c8fc3) is the backend fix; each quick CI checkout also contains workflow-only changes, so its complete tree is not asserted equal to the source revision's tree.

Both quick workflows failed the separate flag-on selector before CBMC on both matched trees. The default-selector success on the fixed tree is separate from the workflow result. In the full run, macOS 14 has no test steps; macOS 15 Intel reached setup. Neither has a completed regression result, and the available evidence does not establish the cancellation's cause. Linux final-placement coverage is confirmed; the full platform matrix remains unconfirmed.

The new local single-commit candidate `83a413f9be2d57389c991d9f5d1250b4e4386203` is **NOT_RUN; same tree as 6db3c4dab**. Its tree is `c9b9bafdeca616fac235574f33dad477c25ad90b`; the historical `6db3c4dabd4a368314eb8e2b71d21d1eee721593` tree is `c9b9bafdeca616fac235574f33dad477c25ad90b`. It has sole parent `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`. The historical runs above belong to their recorded SHAs, not to this new commit.

## Related issues and scope limits

Related to [#5085](https://github.com/model-checking/kani/issues/5085): it reports the analogous CBMC invariant on another lowering path involving nested zero-width arrays. Identity of the underlying mechanism has not been established.

The separate flag-on compiler panic at `relevant_instruction.rs:136:73` reproduced before CBMC on both matched trees. [#4854](https://github.com/model-checking/kani/issues/4854) is relevant for triage of a similar failure; the exact operation and operand are unknown from the backtrace. The [retained flag-on fixture](https://github.com/Tiramisu-Cake/kani/blob/dc590936c56556ecfb20fc714da06fcb13e884db/tests/expected/uninit/zst-union-arm-uninit-checks/main.rs) is the observed input; the reduced [PANIC-NOTE input](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b3r/PANIC-NOTE.md) is **NOT_RUN**, not a confirmed minimum. B3 does not fix this panic. The default-check backend fix does not establish support for union storage under `-Z uninit-checks`, G1, or MaybeUninit transfer.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with AI assistance.*
