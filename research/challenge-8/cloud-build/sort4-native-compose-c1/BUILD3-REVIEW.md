# Build3 first frontend boundary and capture-only next step

Cloud Build `4a0b4f8b-2409-4133-a99d-aa2d783067cc` used immutable
proof/infra SHA `5dc32b471a3217fb193ebe75f1116e154012af96` and the
unchanged production translator SHA
`4d3a190fcec695415b41162ddf8d71aec6e2826d2b69e7692df306a568add98c`.
The verified archive is at
`/tmp/native-compose-4a0b4f8b-read/allprooflogs/cases/sort4-native-compose-c1`.
Original/verified source hashes are respectively
`e7b3211c2a81b779803db1416365fe857b6ba9e760c814e77d73db2a61d0175c`
and `28716b042293c4b5211d5696464696fa7da073ca15301a6002b62f3813d3497e`.

Normal and readonly export/decode and refinement all exited zero. Both full
helper MIR records contain exactly one `FnMut::call_mut`, ordered `v_base.add(1)`
then `v_base`, generic `F, (&T,&T)`, one normal target and direct Continue.
The native diagnostic full MIR contains one helper call with actual arguments
`v_base` (cast to const), `len`, and a mutable reborrow of `F`. The isolated
saved-MIR structural classifier passes in both modes, including eight callback
locals (receiver, tuple, four shared refs, two raw pointer temporaries),
one declaration/live/definition/dead occurrence each, no direct address-of,
cleanup or Drop. This is a structural diagnostic; it does not prove the helper,
native function or actual std caller CFG.

The complete helper record hashes are `0dc4d60b62343cb816326b4cf229581081f4e7ff906559cdc2448f14853be3b0`
(normal) and `362db0d6d413be96c526407fb6781498cdde8ff8a68b8d064eb3ec4a1a0cc720`
(readonly). The complete native record hashes are
`1163da55264497d8b57186aa3974a1ab2087e1439177e0aecc875b9c3479d674`
and `c87004838fcef0d3b575c57bb1758ca06a585df725733d584322e0de49e7d666`.
The helper callback ref/tuple/raw-temporary locals are `_33` through `_40`
in normal MIR and `_7` through `_14` in readonly MIR. These hashes bind the
saved Build3 compiler evidence; changing any verified source requires fresh
compiler and refinement stages even if the runtime body is the same.

With existing reviewed strict lifetime and HRTB options enabled, the full
verifier entered `c1_source_prefix` and first refused at
`verified/lib.rs(189,13-35): No such function: __vf_c1_compose_unwind`.
The native verifier entry was never reached. The stock whole-module
`-dump_ast_with_locs` exited 2 with `Failure("TODO")` in
`Ocaml_expr_of_ast.of_body_ss`, before yielding an AST file. Neither
outcome gives proof credit.

The independently reviewed response is an instrument-only target Func
capture under `SORT4_NATIVE_C1_AST_CAPTURE=1`. Its single-file patch is
`capture-overlay.patch`, applied to the exact production translator
SHA above; patched SHA is
`4dc5f332d4c813fee966ef0724aa1f8ce0e6578ff1e15a0cb61bfb9719c6d14e`.
The hook checks the exact Build3 verified source SHA, source signature line,
marker/call uniqueness, exact frozen strict/HRTB options and absent output;
serializes the original `c1_source_prefix` Func only, checks its immutable
fingerprint and returns the same object. Other bodies, including native,
pass unchanged. The full verifier stage runs with capture opt-in off and must
still refuse at the same marker. The AST diagnostic may still exit 2 at the
whole-module serializer after the target file has been emitted. If the target
file is absent, Build4 remains only a failed capture, with no semantic
overlay authorized.
