# Fresh raw review: public-guard build `d352b4a6`

## Collector and artifact integrity

Reviewed Build `d352b4a6-d86d-48b4-86ca-cdccb0af4d89`, proof/infra revision
`3ed89d79a4d0c389607fac7eb0b3909d7e7d4b28`, lane
`o26-sort4-c1-current-recovery`. Raw summary: process exit 0,
`diagnostic_complete=true`, `evidence_complete=true`,
`verification_accepted=false`. Downloaded archive SHA-256
`ae39f373baf16748479cb05c0874e5c51536a8a692bfcfd63037778b6e1e9e75` matches
the upload receipt. I independently rehashed all 748 entries in
`files-sha256.json`: 748 match, no missing files or mismatches. All 478
indexed text chunks are present and the index SHA-256 is
`21f4e09e2ba3830acf7d190813fbb6cddc8d29c7053475518dc02452c8a19b18`.

## Tool and model profile

Tool pins remain the experimental, unaccepted profile: VeriFast HEAD
`f76012fb518703b1d98e243ac4f487f16877cfcb`, kernel
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`, pre-binding
translator `66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124`,
current translator `21ca026ae3279ef7da9a8a482b5355fab4c39250dec553854509b1f8923f52c4`,
parser `7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2`,
RSSpec `d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf`,
refiner `b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28`,
MIR exporter `b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796`,
and post-binding console `6d20c76fbd49c9ad2700ada5bf9e4ab5c218f82c5a32727daf2a3d3fb86b0ae9`.
Compiler commit is `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`, std base
`cd371e035c7e573760c43bf934d53e8118ee3e7d`, toolchain
`nightly-2026-09-25`. Source certificates retain slice SHA
`e3a45814fc07497d6e85d182d6b30782711e4b77752fa817988ec6da12e2cb6f`,
SmallSort SHA `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`,
stable public entry SHA
`3f2b2d8543a1cb91c9352e041bed49949a31cbd4b1030ec1a82cca1304cb22d3`, and
`SizedTypeProperties` source SHA
`b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2`.
The audit says no fresh ZST model or native C1/C4 gate was run in this Build.
This is not a profile acceptance or proof-model result.

## Eleven case outcomes

The two canonical native-reference cases pass paired normal/read-only MIR,
refinement, AST, and verification: each AST has one function root at
`verified/lib.rs(10,1-12,2)` and 4 distinct `VarPat` binders (5 occurrences);
each has source pair SHA `91d7d14cdf79fe2d33efc09013f20247a84a05f2f368927dc4ad84ae7b52edd3`
(generic) or `501623b02abcd6e2a6d72f2897d87b4ba7cd50c8a29d974e6a18ea3c39d427c6`
(MU). Each verifies 53 statements, all 55
registered physical IDs execute, and the generated posts, strict lifetime
checks, cleanup/free and leak checks pass. `consumer-positive` also passes
paired support, refinement, AST and verification (63 statements, all 65
registered IDs execute, complete normal/unwind posts and free/leak checks).
Its source pair is original `928e260c12be8b5fe05c230ebc8615fe6fbedc37290c90604a7dfccb1f9f2b30`
and verified `0ece00b2ceb995c9f5701abf7fdae2a62a96882639b17a52702e48ca698bf673`;
its AST root is `native_slice_pointer_consumer` at `verified/lib.rs(10,1-21,2)`
with 9 distinct `VarPat` binders (11 occurrences). These remain isolated
component/consumer results, not an actual caller proof.

All three consumer negatives reach their intended assertion with paired
support/refinement passed: wrong pointer at line 14
(`v_base != source_base`); missing raw rights at line 14
(`unrelated[..1]`); and a casted scratch pointer lacking initialized `T`
authority at line 17 (`array<T>(strip_pointer_metadata(scratch), 1, _)`).
They are intended assertion negatives; no setup/refinement failure substitutes
for them. Source-admission mutations and malformed phase admission are refused
before verifier execution; default-off refuses the exact method before the
binding. Those are admission controls, not proof negatives.

Both actual unfiltered caller-prefix variants pass normal/read-only export,
decode, paired full-MIR support and refinement, then fail at the same first
VC: `verified/lib.rs(20,24-32)`, mapped to
`shared/smallsort.rs:230`, `if scratch.len() < len + 16` after `len = v.len()`
at line 225. Source pair is original
`7a3124bfa59fd207a1c6b1a583b10c1e9b8828b2336338a9a65c8a80c17dd1a7` and
verified `f7bfcb41fa6fd5784649fab8d5ee06de890f019391e7f6b7ddd67887e713ee64`.
Error: `Potential arithmetic overflow. (Cannot prove
(ptr_len(fn_outcome_result(outcome)) + 16) <= 18446744073709551615.)` The
AST root is `small_sort_general_with_scratch<T,F>` at
`verified/lib.rs(10,1-57,2)`, with formals `v`, `scratch`, `is_less`, three
translated lifetime parameters and `fn_outcome<()>`. Each AST has one function
root and 14 distinct `VarPat` binders (17 occurrences); normal/read-only MIR
roots are `9929cb2bb0134d810828639594792696ecc21b6033c81d1a3062e3ac06ec132a` /
`27c206c36f0c5ff08c1d233b4eb54bb2d3a2a937126a7018c13cf39c28f67a54`. Each
verifier exits 1 before later caller operations; neither the abort branch nor
any pointer/alias obligation is proved.

The three new public-guard cases all fail before their target guard assertion.
They pass normal/read-only export and decode, paired MIR support, and
refinement; AST diagnostic and verifier both exit 1 at the same
`verified/lib.rs(6,8-27)` error:
`No such type parameter, inductive datatype, class, interface, or function
type: T`. The failing declaration is the generated `BufGuard::as_uninit_slice_mut`
trait method (source `BufGuard` returns `&mut [MaybeUninit<T>]`); its AST
generic list contains `Self` and a lifetime but not `T`, even though the
translated return type refers to `T`. It precedes the target root
`sort<T,F,BufT>` at `verified/lib.rs(9,1-25,2)` and public source guard
`stable/mod.rs:31–33`. Thus this is a fixture/exported-AST type-scope blocker,
not a semantic result for the public ZST guard and not either intended
negative. All three share original source digest
`e948ef52a22355109c74b6af6344b78dd2596431ebfcd247ebe91ae7cc3668d1`; their
verified digests are case-specific and listed below.

Per-case source/MIR/AST/log identities:

| Case | Verified source SHA | Normal / read-only full MIR SHA | Proof AST SHA | First verifier result |
| --- | --- | --- | --- | --- |
| `public-guard-positive` | `4af390bed43e889388893bff056e79bc10a16b353c0a847adb47ab739549cf08` | `663ce3a20c227205ed12ee76e6724b49a9e260187c645c94bfe991faa5c65c3e` / `da78ba2f929dab2d87bc89adc4f07447f00fe506aad333840ae557bcee87dc91` | `224d7e462cc916aa1c79f4d1e0867b28ceaca639b10acc71c90d3b9d20cba0b1` | T-scope error; log `837a729f6d38b6fb84c6036d26daf476b13b1e4d8408ccdfd9392e21b8b8381b` |
| `public-guard-false-positive-size` | `366dab1ea3a6fa5e1b27b61bc14a2cd499ec84d0900f8b93cac32e7e311ef737` | `b690987831286dfbd449bed901fecc6b7514292aa34f7b61fbdc5ae5d4c2fa15` / `b6dd4dc41138b73e49fa9955f6694a9c22ff943ed51c4be89000b0bf49c8e84d` | `8bac9948e456366c408280d3caca9fee2877c67de5a9d50b6cc29b867563382b` | T-scope error; log `fc90a81f2cbd3f50782408b23270a2618c9ba5cd24b13df80046cb94a24a333f` |
| `public-guard-zst-branch-false` | `24ec7f1c30cb70281e7a0c85769e8d93088390160f79dfbc3a683dbc45eae3b1` | `d8f3ef7356078fa755a0b7985a2e36b422957bfff1ba024b16f1ada3155856ec` / `a7ca5f95c4f875fce3d5db16f636926e44bf2227439b2cde068003a0fce53888` | `ac9b3fac49ab1e471d9023dbc38f082a33a6b027eda6d4e4461c931af5b2420d` | T-scope error; log `258c22752baf1683ebd45371c9d4de2441ea299e44a4f4d1738a87916b6623c3` |

Each public fixture AST has three function roots: `BufGuard::with_capacity`
at `(5,8-21)`, `BufGuard::as_uninit_slice_mut` at `(6,8-27)`, and `sort` at
`(9,1-25,2)`. Their saved ASTs contain respectively 11, 8 and 8 distinct
`VarPat` names; all three gates stop at the `BufGuard` method before the `sort`
root or guard predicate receives proof credit. Although 49 registered IDs
appear in execution accounting, that does not override the verifier's earlier
type-resolution error or turn these cases into semantic guard positives or
negatives.

## Current conclusion and open obligations

The candidate `[T]::as_mut_ptr` translator delta remains restricted to
projecting the receiver's pointer value; it does not supply pointer
permissions, ownership or lifetime authority. The pointer component/consumer
controls remain reviewable in this run, but neither actual caller prefix
passes `len + 16`, and the new public guard route did not compile into a
verifiable AST because of the `BufGuard` method type scope. The audit records
`public_guard_candidate_raw_review_required=false`,
`public_guard_transfer_to_helper_proved=false`,
`actual_caller_proved=false`, `actual_sort4_proved=false`,
`callable_summary=false`, and `profile_accepted=false`.

Even a future proof of the public guard's `IS_ZST` continuation would not
automatically transfer to the helper: caller dispatch, scratch creation and
the call edge remain unproved. `FreezeMarker` does not itself imply nonzero
size. `SizedTypeProperties::IS_ZST` is defined from `SIZE == 0`, and the pinned
RSSpec equates it with `size_of::<T>() == 0`; this source/spec fact must still
be established through the actual caller. The current helper's first open VC
is still the `len + 16` check before either pointer call. The second direct
sort4 call, its half-offset/disjointness/restoration, the sort8 route, full
five-comparison `sort4_stable`, tail/merge/panic paths and full SmallSort
contract are also open. This Build does not resolve the earlier trust review
of the entire experimental profile.
