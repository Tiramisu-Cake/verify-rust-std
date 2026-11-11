# KANI3300 B3 static review

**Verdict: PASS for static review; coordinator CI remains required.** No blocking correctness or source-audit issue remains in the reviewed candidate. Compilation, clippy, Kani, and CBMC outcomes are **NOT_RUN**; this review grants no proof credit.

## Reviewed identities

- Baseline: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`
- Tests-only commit: `dc590936c56556ecfb20fc714da06fcb13e884db`
- Candidate: `9dddcb1134f8a55ee3a4451df9513941ca3c8fc3`; tree `91608f7fd254e5588f4f0543439b58fd114b9d40`
- Final packet inventory SHA256: `4c1ba516cb85af073516352c20e431bcc893feda27b6f50e399931a5446f3eb3`
- Spec SHA256: `7af5bc83fbbebd267afa8f755d8e6a286a171012f2592ab4137c1c04126f68ac`
- Diff SHA256: `7c4bd82927350f14bfb41703a83b922ccadd2b1eaf9326f41a5ce28d3034115f`

Packet candidate/tree/diff identities, changed-file hashes, all nine dependency hashes, and source parity were checked against the committed candidate and packet. The two test sources are identical apart from the `-Z uninit-checks` directive. `git diff --check` is clean.

## Findings

- Backend change in `codegen/typ.rs` exactly matches the `d760bad` transplant: only a zero-sized payload inside a nonzero padded wrapper is represented by the empty unit struct. The `UnionField` retains the original logical arm type; padding width, non-ZST payloads, and the all-ZST branch are unchanged. `cprover_bindings` has no candidate change and matches the referenced upstream baseline, so logical field and padded representation interfaces remain intact.
- Seven harnesses per mode cover byte-backed `[(); 2]`, padded C and Rust unions, `repr(align(8))` ZST, union at offset 8, all-ZST union, and nondeterministic in-bounds array indexing with read/write/reference. Both expected files assert seven successful harnesses and zero failures.
- Typed-copy cases initialize the complete source union with `write_bytes` before `ptr::write(&mut dst, ptr::read(&src))`. Assertions inspect covered bytes or initialized typed fields; they do not inspect padding. The all-ZST case uses a zero-length write on a valid aligned pointer.
- Initial source-only audit identified `AllZst.unit` as write-only. The revised candidate reads `dst.unit` via `size_of_val` after typed transfer, inside the unsafe block, without comparing unit values; this removes the dead-field warning risk. No other apparent dead fields, unused imports, unnecessary mutability, unit comparisons, or source-level clippy/`-D warnings` hazards were found. Unsafe operations are confined to the explicit blocks and have valid pointers/lengths by inspection.

No runtime result is inferred from these source expectations. Narrow CI on both commits must establish reproduction and fix behavior.
