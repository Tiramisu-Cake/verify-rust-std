# O22: accepted local unsafe adapter component

O22 hosted run [37754201983](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37754201983),
proof commit `02945280d4f335948c6edd60feb7ac62092a0256`, produced
`overnight-s6/forget-own-controls/summary.json` with all eight declared
variants executed. This result is **ACCEPTED_LOCAL_COMPONENT** for the
standalone, public generic `unsafe fn checked_forget_owned<T>(t:T)` in the
pinned 26.10 experimental profile. Its runtime body is byte-exactly the
extracted std `mem::forget` body, and its checked contract requires and
returns the same `thread_token(tid)` and `<T>.own(tid,t)`, with
`on_unwind_ens false`. The adapter is not the SAFE, const std function and
this run contains no call-site redirect or proof of SAFE correspondence.

The positive passed NORMAL and readonly MIR export/decode, the complete
one-call `ManuallyDrop::<T>::new`/Move(t)/cleanup graph inventory, source
identity, refinement, and full VeriFast verification: exit 0,
`0 errors found (52 statements verified)`. Its own return and leak checks
were reached. The complete positive function MIR SHA-256 is
`ec489d53f4dba5937576a03506f05d852c8cdd3f7c5197c0d698d6d8b18caf5b`
in both modes. The full original and verified source SHA-256 values are
`1e8d7157507da272f158ba317bc860fc9b87aee180ed4f53000c927709b02332`
and `cfac82c0362a4e18037fac59c94c18274c4699c6f2780b406fd1f80478c60a50`.
The source certificate separately pins the full std `mem/mod.rs` and
`manually_drop.rs` files and their exact extracted bodies.

| Control | Hosted first failure or admission result |
| --- | --- |
| `false_normal` | line 8, `Cannot prove false` in the extra normal post |
| `owner_duplicate` | line 8, missing second `own(T_typeid)(tid,t)` |
| `owner_wrong_value` | line 8, cannot prove `!(t = t)` for the demanded distinct value |
| `thread_duplicate` | line 8, missing second `thread_token(tid)` |
| `owner_loss` | line 15 leak of `own(T_typeid)(tid,t)` at return |
| `contradictory_pre` | mandatory dead code at the function header, line 3 |
| `weakened_unwind_admission` | rejected before verifier invocation because the target certificate requires false unwind |

Each proof negative had successful NORMAL/readonly export/decode and
refinement, exact source identity, the expected one-function verifier target,
and one error at its named obligation; the dead-code case had no unrelated
proof error. The unwind mutation is only an admission control: an exact
nonunwinding body does not provide a meaningful proof-negative for weakening
the unwind post.

The trust boundary for using this result elsewhere is still open. The
adapter's `unsafe` and non-const signature differs from the actual SAFE,
const `mem::forget`; its body-level result alone cannot upgrade the stock
SAFE summary. A future call-site use needs a separate exact source and typed
MIR certificate, nominal guard owner validity and resource transfer, cleanup
fidelity, and an explicit reviewed SAFE-to-adapter correspondence. No
additional `T.own`, pointee right or trusted ownership axiom follows from
this local proof.
