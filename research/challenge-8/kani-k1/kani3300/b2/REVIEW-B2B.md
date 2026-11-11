# Independent static review — KANI3300 B2b

**Verdict: static review passes; no source-level blocker found.** This is a review of candidate `8f09ae8085e6d2884ecee1402019491038288bc7` (tree `97879d30bdcddde37d84ad400b17e84b3b72f708`) against baseline `50fa409e4dffe4fb3bd1a33b67197d3a63aa77d1`, using packet `/tmp/kani3300-b2b-review-packet`. `smallsort-session review check` validated the packet: SHA256 `b77bd7cff950073d2c9f6ff7a7dac9c3ee9187265ce71cc2b325b8438b761de7`, spec SHA256 `b088690eae6bd53bde3b1ac7c5ddd57effd065923bd3de1c35c4019c680042cc`, state `PACKET_VALID_NOT_REVIEWED`. Candidate tree identity matched; `git diff --check` was clean.

## Findings

- Each of the four added probes initializes `src: u8` to `0x51`, takes `p = addr_of!(src)`, passes that same local directly to `consume` with explicit `Move(src)` or implicit-place `Copy(src)`, then uses the saved `p` after return to read the byte. There is no transfer temporary, source reinitialization, or `StorageDead` in the custom MIR body. The pointer is formed from the local itself and `probe` has not returned at the read, so the intended source allocation remains in scope. (`custom_call_{move,copy}_{read,write}.rs`.)
- The API forms used are documented by the pinned `core::intrinsics::mir` source: locals/places and implicit Copy plus `Move` are at `mir.rs:211–225`; `addr_of!` at `:234–238`; `Call` form at `:245–252`; tuple `RET` fields and runtime/optimized mode are illustrated at `:135–145`. The direct call to `consume` and `read_volatile` uses that documented call form. This confirms source-level syntax against the supplied source copy; it does not substitute for compiler confirmation of generated MIR.
- The write callee only receives its by-value `u8` parameter. It creates a raw pointer to that parameter, volatile-writes `0xA7`, and volatile-reads it back. The caller source pointer is not passed to the callee. Accordingly, the Copy-write control checks callee `0xA7` while source remains `0x51`; the Move-write probe checks the callee value if execution reaches the return, while the later source read is expected to diagnose the moved-from state. Read-only variants likewise use a volatile read of the initialized parameter. No unrelated uninitialized value, invalid `u8`, padding, or pointer cast is apparent.
- The forecast follows the supplied pinned interpreter code. `step.rs:408–432` maps Copy to `FnArg::Copy` and a memory-backed Move to `FnArg::InPlace` (both branches for `move_definitely_disjoint` do so when a place is in memory). `call.rs:421–445` copies the argument into callee storage before protecting the in-place source. `machine.rs:1857–1875` documents protection and writes `uninit` to the source, including the no-borrow-tracker branch. Thus the static forecast of a failing post-call source read for Move and preserved `0x51` for Copy is justified by this interpreter path. The callee's write affects its own parameter, not the caller source.
- `EXPECTATIONS.md` distinguishes the coordinator-reported earlier B2 CI from B2b forecasts and marks B2b outcomes `NOT_RUN`; it also explicitly avoids language guarantees and proof credit. The source links cite the relevant pinned files and line spans. README instructions require coordinator CI to inspect MIR for exact source identity and callee operations.

## Limits / follow-up

No Cargo, rustc, Kani, CBMC, Miri, build, dispatch, network write, or external action was run. Therefore this review does not establish that the four files compile, that emitted MIR preserves the intended operands and pointer, that Miri reaches the expected source-read diagnostic, or that the audit source SHA matches the named nightly. Coordinator CI should confirm those facts and distinguish uninitialized-read UB from alias/protection diagnostics. No proof credit is granted.

## Publication notes — main agent

Reviewer: independent GPT-6 Luna, HIGH reasoning, separate context, no nested delegation.
The published `b2b-review-packet/` is byte-identical to the reviewed `/tmp` packet.
The publication adds review/spec/packet/result only; the six reviewed B2b candidate files remain byte-identical.
Static Python checks passed: isolated edition-2021/no-dependency manifest and nightly pin, total 29 binaries,
four-case Move/Copy read/write matrix, initialization/address/transfer/read ordering, matching callees,
expectation coverage. No execution outcome is inferred from these checks.

Source-only audit downloads came from `raw.githubusercontent.com/rust-lang/rust/7189d39d9ce936881b8132c6addeaf3e295cd455/`:

| Upstream path | SHA256 |
| --- | --- |
| `compiler/rustc_const_eval/src/interpret/call.rs` | `5a0599ddfacf984856704f319ec1eb0438de172d499150c94e6575d9e88a85cd` |
| `compiler/rustc_const_eval/src/interpret/step.rs` | `670ae45119b9dd184b4ae0cbe7f4ccb079440dac4ab8e5515c2821264fff204c` |
| `library/core/src/intrinsics/mir.rs` | `929437ae1ab07fb008b2bbf3a00f30a1c4c1c8a2eded81c04184633cd3b95821` |
| `src/tools/miri/src/machine.rs` | `74a73ede337dadc6ac4d81538f5e22bce29c326881099b03027d01d6e758ebd4` |

The exact review `diff.patch` contains single-space empty context lines by patch design;
publication whitespace checking excludes that immutable packet member. Candidate source/docs and
publication metadata pass `git diff --check`; packet bytes were preserved, not whitespace-normalized.
