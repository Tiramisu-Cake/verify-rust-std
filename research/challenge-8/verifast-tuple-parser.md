# Experimental VeriFast tuple-2 ownership parser patch

This is a proposed **Actions-only verifier-source diagnostic**, not a verified
SmallSort proof or a change to the project's pinned production verifier. The
patch in `verifast-tuple-own.patch` targets VeriFast `26.09`, source commit
`809de4596839b739dd999f9e462242c835e3af46`, file
`src/rust_frontend/vf_mir_translator/rust_parser.ml` (pinned raw-file SHA-256
`f7f2c2bf573be09d8ce5dcd640ddca0e1437a8f18464facc9621ac287a5082e8`).
It has not been built or verified locally.

The actual `insert_tail` probe reached both `&*tail` and `&*sift` under its
generic initialized-range contract, then failed to produce the tuple-2
`Args.own` resource required by `FnMut::call_mut` in
[run 37400422055](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37400422055).
A ghost `close` found no tuple-2 predicate instance in
[run 37401357731](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401357731).
An inline wrapper definition collided with an existing name in
[run 37402093844](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37402093844),
and an explicit type-predicate alias in the bundled prelude duplicated the
tuple-2 `.own` definition in
[run 37402802085](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37402802085).
Those runs passed extraction and ghost-only refinement but did not prove the
comparator call.

The pinned [Rust spec parser](https://github.com/verifast/verifast/blob/26.09/src/rust_frontend/vf_mir_translator/rust_parser.ml)
expands `struct std_tuple_2_<T1, T2>(T1, T2)` into an opaque, bodyless
`std_tuple_2__own` fixpoint and a single `.own` alias to it. Appending another
definition cannot supply the missing field interpretation. The proposed
parser patch changes **only** that exact tuple name with type parameters
`T1, T2`: it emits a transparent `PredCtorDecl` with predicate arguments
`(thread_id_t, std_tuple_2_<T1, T2>)` and body
`<T1>.own(t, v.0) &*& <T2>.own(t, v.1)`. It retains the existing single
`.own` alias and leaves the generated handling of all other structs
unchanged. The body directly owns the two actual fields; it is not an opaque
lemma, assumed result, or comparator stub. The type-predicate checker in
[`verifast1.ml`](https://github.com/verifast/verifast/blob/26.09/src/verifast1.ml)
accepts predicate constructors as generic `.own` targets in principle; an
Actions build must test this exact AST and its type checking.

Any runner for this experiment should check out the pinned source commit,
fail closed if `rust_parser.ml` differs from the SHA-256 above, apply the
patch once, build **only on a GitHub-hosted Actions runner**, and record the
patch hash, resulting source and binary hashes, tool version, and complete
build and verification logs. It should use the unmodified bundled
`prelude.rsspec`: combining this source patch with the failed tuple spec
overlay would create the same duplicate definition. The original extracted
SmallSort Rust bodies, generic signatures, contract, normal/unwind checks,
and exact-byte refinement audit must remain unchanged. A derived binary
must be labeled as an experimental build from the pinned source, not as the
unchanged `26.09` release binary.

Useful regression evidence would include the actual `insert_tail` comparison
advancing past `FnMut` argument ownership; successful close/open of tuple-2
ownership for generic field types, including a non-`Copy` type; and unchanged
ownership behavior for tuple-1, tuple-3, tuple-4, and an unrelated struct.
The experiment must still inspect comparator normal and unwind paths, type
interpretation, and compatibility with the existing tuple-2 `.share`
definition. Passing the first call would leave early-return cleanup,
exclusive access before `tail.read()`, `CopyOnDrop` verification, and the
rest of Challenge 8 open.
