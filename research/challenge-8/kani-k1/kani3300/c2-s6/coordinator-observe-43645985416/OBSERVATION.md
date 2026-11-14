# C2-S6 coordinator observation — run 43645985416 (ubuntu-24.04)

Source: exact S5 8d67298c48eb7b2381f806a6353433d1440e3d94. CI-only commit 7615190ca2 (`uninit-ci/c2-s6-observe2`):
workflow `workflow.yml` + `.github/s6obs/*.rs` = worker repros from `../repro/`, except that the coordinator added the
missing `-Z unstable-options` to `ordinary-hook-return.rs`, `fn-item-plain.rs`, `fn-item-shadow-return.rs`
(without it Kani rejects `--cbmc-args`; nothing else changed). Each file run with
`RUSTFLAGS="<compile-flags> --emit mir" kani <file> --keep-temps <kani-flags>`. Bounded summaries: `*.summary.txt`.
Previous attempt 43645617823 is void (`--keep-temps` was placed after `--cbmc-args` → CBMC usage error).

| Input | Native outcome | Notes |
|---|---|---|
| companion-legal-ordinary (existing transfer-qualification/legal-ordinary.rs) | SUCCESS, 0 of 365 failed | matches its expected |
| companion-mu-argret (existing maybe-uninit-argument-return/main.rs) | FAILED, 1 of 176: uninit read of `u16` in transmute_neo | intended negative |
| fn-item-plain | SUCCESS, 0 of 20 | free FnDef through generic FnOnce, no shadow |
| fn-item-shadow-return | FAILED, 1 of 109: "Kani does not support shadow transfers without a paired argument/return protocol." at fn-item-shadow-return.rs:9 in `invoke::<fn() -> MaybeUninit<u16> {hole}>` | MIR: the call in `invoke` targets `<fn() -> MaybeUninit<u16> {hole} as FnOnce<()>>::call_once` (FnDef shim, not optimized to the Item `hole`); the refusal is emitted before that call; no earlier tuple/layout failure |
| generated-modifies-no-shadow | SUCCESS, 0 of 332 | hook return is a reference; no shadow carrier (confirms worker analysis) |
| generated-modifies-invalid-target | compile error E0277 `MaybeUninit<u16>: kani::internal::Pointer` not satisfied | setup failure, not semantic |
| ordinary-hook-return | FAILED, 1 of 121: "This is a placeholder message; Kani doesn't support message formatted at runtime" in `kani::mem_init::load_argument::<2, MaybeUninit<u16>>` | see below |

## ordinary-hook-return: fail-closed, but through an internal protocol assertion

MIR of the harness: `_6 = kani::internal::untracked_deref::<MaybeUninit<u16>>(_7)` followed (bb11) by the caller-side
return `load_argument(_17, 0, 5, 0, ..)`. `untracked_deref` is an `InstanceKind::Item` with a body (`todo!()` → panic_stub),
so `has_transfer_protocol` (uninit_visitor.rs:1233-1237) treats it as paired. Codegen intercepts the call through the
`UntrackedDerefHook` marker (hooks.rs), so the callee body — and its return `store_argument` — never runs; the caller's
load then trips a protocol assertion in `load_argument` (mem_init.rs:501-553). Result is FAILED (not a false SUCCESS),
but the description is an internal placeholder instead of the explicit Unsupported refusal used for shims.
The generated contract paths cannot produce such a call (reference return / E0277 above); only a direct call of the
`#[doc(hidden)]` internal function reaches it.
