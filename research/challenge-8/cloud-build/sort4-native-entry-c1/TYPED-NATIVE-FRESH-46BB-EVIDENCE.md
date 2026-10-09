# Fresh typed-native entry evidence (46BB)

This note reviews only the saved Cloud evidence under `/tmp/native-46bb-read/allprooflogs`. It records a verified, source-linked native resource diagnostic and the exact one-producer-deleted controls. It does not claim a proof of `small_sort_general_with_scratch` as called by its parent, or of `sort4`.

## Positive result

`source-typed-frame-positive` reached verifier exit 0 with `0 errors found (82 statements verified)`. The exact original Rust caller was preserved at `fixture/actual-caller.rs`; the generated verified Rust source retained the actual function name and signature. In the actual diagnostic body, the ghost branch at `len >= 8` performs the stock calls `produce_type_interp::<T>()` and `produce_type_interp::<F>()` (verified source lines 32–33), checks the current thread, four source elements, their `own::<T>` facts, the comparator cell and `<F>.own`, splits the source array and owner facts, calls `c1_source_typed_identity`, rejoins the source resources, and explicitly leaks both logical type chunks (lines 40–52).

The checked identity lemma's pre- and postconditions are identical: `type_interp<T>()`, `type_interp<F>()`, `thread_token(t)`, `t == currentThread`, `v_base[..4] |-> source4`, `foreach(source4, own::<T>(t))`, `*is_less |-> less`, and `<F>.own(t, less)`. The lemma therefore demonstrates preservation of this four-element source/F/current-thread resource subset while the automatic native entry contract checks the full normal-return and unwind arms, frame restoration, and leak obligations. Both type-interp chunks are introduced by the explicit stock producers and explicitly leaked after the source frame is restored; they are not claimed to follow from the native heap.

The same-signature native entry contract admits every `v` length, every scratch length, and ZSTs. The typed source assertions and identity call are guarded by the diagnostic ghost condition `len >= 8`. This is a standalone resource lemma: the marker `FIRST_SORT4_CALLSITE_BOUNDARY` is artificial and sits within one ghost statement in both MIR views. The source-operation map confirms the exact read-only `len`, `v.as_mut_ptr()`, `len / 2`, and scratch-pointer statements, but has no source-line-to-basic-block mapping and makes no caller CFG projection. Thus this evidence does not prove the actual caller selected the `len >= 8` path, the scratch-success path, or the inline-const value path. It also does not prove sort4, the full caller, or a callable summary for either.

The positive raw record has `accepted: false`, `full_actual_caller_proved: false`, `actual_sort4_run: false`, and `bridge_actual_caller_applicability: NOT_PROVED`; those are the appropriate scope limits, not a failure of the native entry verification. The captured automatic post AST has normal-return and unwind arms and a matching automatic-contract certificate. This lemma invokes no comparator, so the captured unwind arm says nothing about callback panic behavior.

## Exact negative controls

Both negative cases retain a successful proof of `c1_source_typed_identity` before entering the native function (entry at verified line 20); each then reaches the identity-helper call at line 43. Each verification log contains exactly one verifier error, at the helper's matching precondition on line 16. The errors distinguish the omitted producer precisely, after the peer producer and all source/F/thread setup have been supplied:

| Case | Retained stock producer | First and only verifier error | Result |
| --- | --- | --- | --- |
| `source-typed-missing-F-negative` | `produce_type_interp::<T>()` | `verified/lib.rs(16,48-49): error: No matching heap chunks: type_interp<F>()` | Intended missing-`F`-producer control |
| `source-typed-missing-T-negative` | `produce_type_interp::<F>()` | `verified/lib.rs(16,25-26): error: No matching heap chunks: type_interp<T>()` | Intended missing-`T`-producer control |

In both controls, normal and readonly MIR export/decode and refinement complete; verification fails at the expected helper precondition. The helper's own proof and leak check complete before native entry. Therefore the recorded failures are attributable to the missing `type_interp` producer, not setup, parsing, helper verification, or an unrelated postcondition. They establish that each stock chunk is required by this checked helper contract; they do not establish that the actual caller provides either chunk.

## Evidence pins and profile caveat

Build46bb1257-eeb7-4fd6-b210-1c7f40a8c81c SUCCESS, create23:39:05.363527647, finish23:45:13.255746 UTC, charged368 seconds. Archive SHA256535cb3e3594b263303d5725abbcc13c07a6fec0542e2c81e0da89d4dc7f3f47c; archive and all text-log inventory verified by control download.

The extracted saved evidence is `/tmp/native-46bb-read/allprooflogs`; the archive manifest SHA-256 is `7ba4d2e58c0aa485a7434f47f93f2ec7a0e9db9286f65e5eb2e8875d25bba0ba`. The source/proof artifact hashes are:

| Artifact | SHA-256 |
| --- | --- |
| Original source pair `original/lib.rs` | `c7dcd0edef3255a1f3ec39a788bc99ff56e9eb1f322bc53a4f735827fb6a0bb6` |
| Actual caller source | `5204c0f7b6b8c5ab3480c154458569e3b0bd0603a8ac1803eecceb99ff83d5c7` |
| Positive `verified/lib.rs` | `5263b90d3e574549e147b71c09166eccc743abf192e29b589c760facdde318f3` |
| Missing-F `verified/lib.rs` | `7d0b1d8ebff155d2d6b74770c930e2626df1514decdb4392860e887f8b34b12c` |
| Missing-T `verified/lib.rs` | `b81bd66c27ef63ed67d23e6b437d01824476e8e13dd3f675211e10cb94566bde` |
| Positive verification log | `dd516a9b8e75a7ef9a06f6c7823165eb618bcbb9f2a4106e82582c4f58feef09` |
| Missing-F verification log | `21a5db7018fcaca2f9639ad73a5626b166d0f7ca5c8ad5ac4f12f95e9a9010ca` |
| Missing-T verification log | `f367ae5ebc8f16cd6d267bdc88255b59d184443b2d4c86fb4854ccacaf6ce634` |
| Positive captured proof AST | `7f01bee6a2265818548fda9eb23c9695a2f2e38197557c6b9ca7af90010fe803` |
| Positive automatic native-entry AST | `482cacd04a82a0d7804b75de8fb486f548dc9f6cb592de4940185f48c8945bd1` |
| Positive normal full-function MIR record | `191de81a6c6723324df1982ab414d4de2871a299fc768f605797788776061e12` |
| Positive readonly full-function MIR record | `c3e1c8e3e60d3a59ab15755020c141c8ff1e80902edbeb69572e9f86e0656235` |
| Cloud `tool-snapshot.json` | `a149b0e1c6526cd96d62a24116fc88dbe880df8ed3f763ea9effc89939ac1965` |
| `frozen-profile.json` | `142eedb67f6b95a379482677127c22b9054f0edd45bd9ebae6b5c847f3a20df5` |

The case pins both `proof_sha` and `infra_sha` to `ff5d4b85e89d5b1b35cd0bfbed6e70f76716e144`. The Cloud tool snapshot identifies base commit `f76012fb518703b1d98e243ac4f487f16877cfcb`, with C1 overlay inactive, and records Verifast `cb7d9ff0a1ba281310ea4cf5694a58b99f1ebad8136b16d3007c9402ece44817`, refinement checker `b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28`, and MIR exporter `b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796`. The snapshot records `new_semantic_patch: true`, variant `exact_slice_as_mut_ptr_value_projection_candidate`, and `profile_accepted: false`. The separate frozen-profile manifest also labels its profile `EXPERIMENTAL_O26_MAIN20_NOT_HELPER_ACCEPTANCE`, has `proof_sha` `c19e4c50470d32199178d5229a2819554fc6b2f1`, and pins a different Verifast/translator set. Consequently, report this as a fresh result under the exact captured `ff5d…` Cloud snapshot, not as acceptance of the frozen profile or independent validation of its semantic patch.

No compiler, verifier, extractor, or replay was run locally to prepare this note; the review uses only the saved Cloud files and their recorded hashes.
