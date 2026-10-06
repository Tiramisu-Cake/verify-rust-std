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

## Hosted source-build entrypoint

`verifast_insert_tail_tuple_parser` routes to `run-verifast-probe.sh BUDGET tuple_parser` on Ubuntu22.04. Its overall timeout includes extraction, pinned
release setup, `build-verifast-tuple-parser.sh`, verification and refinement.
The helper checks the exact source commit/parser/prelude before applying the
patch and retains both parser versions and the actual applied diff. It builds
only `make ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes`, the console
artifact target. `make verifast` additionally regenerates C manifests and
failed an unrelated bitops.c proof in run37405631794 after compiling the
console. Pinned vfconsole skips final manifest linking for all-.rs inputs;
Rust frontend loads the hash-checked adjacent prelude.rsspec. No C manifest is
reused/fabricated, and no library proof is represented as newly verified.

VFDeps25.01 archive `vfdeps-adf88dc-linux.txz` SHA256
`8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580` uses bzip2 despite its .txz suffix and is extracted
at its upstream root prefix with `/tmp/vfdeps-adf88dc` symlink, preserving
compiled-in OCaml paths. Decoder source is fixed to
`2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2` and installed with `--locked`.
The exact-release exporter/refiner are byte-compared after copying into source
bin; rebuilt console, paired Z3 and source resources remain together. Complete
stage logs/resources/exits, original model, tool paths/versions, parser/patch,
binary and resource hashes are uploaded, excluding the checkout/build tree.
A failed build means no target proof. A successful verifier exit additionally
requires one named insert_tail and actual body execution records; full logs
still need review for normal/unwind paths and remaining ownership obligations.
The common workflow checkout/runner-preparation step precedes the probe timeout;
all VeriFast tool setup, decoder/source build and proof are inside it.
No baseline tool configuration is changed by this experimental selection.

## Explicit comparison resources on exit

After run37406214235 reached FnMut preconditions and failed the default empty
unwind postcondition's leak check, tuple_parser now uses explicit transparent
normal and unwind assertions accounting for the exact remaining resources:
F ownership/points-to/thread token, type interpretations, prefix array/owners,
two borrowed-content end tokens, half lifetime token, both initialization
fractions and their close tokens, and the remaining foreach fragments. The
fresh lifetime/reference IDs/fractions are existential postcondition bindings,
not newly assumed resources. Original input preconditions and runtime bytes
are unchanged, with normal/unwind checks enabled and no heap wildcard/leak.

This is a **partial comparison-resource exit diagnostic**, not a restored
owned-range or final insertion contract. It intentionally does not describe a
completed shift: that path must eventually return a different restored range,
and no full-function green result is expected or claimed from this temporary
post. Ordinary early exits can return their real borrowing obligations for
future proved normalization; this does not itself normalize them or establish
panic restoration. The next run should expose the normal tail.read obligation
or a concrete failure to match the explicitly returned resources. Actual Z3
resolution is now captured/asserted with the same paired-library environment
used for verification, rather than metadata collected before the LD export.

Run37407173581 at ff413cfbee73e42c576eee96bdc461b80ca76255 consumes the explicit
exit resources and passes its leak check, then stops on the normal call's
associated Output type versus bool. The actual FnMut signature requires bool,
but that constraint is not yet connected to the annotated reference lifetimes.
This does not prove normalized panic ownership or the first normal read. The
new paired-Z3 resolution check passes; full ghost-byte/refinement audits pass.

The next observation invokes the unchanged pinned exporter with readonly
preprocessing on Actions, preserving raw compiler MIR and decoded Capnp text.
Both Rust input hashes are compared before/after; exporter/decode logs, statuses
and resources are separate. This captures the actual compiler-origin bound
regions and associated-output projection before any HRTB translation change.
The normal verifier and refiner still run independently with their usual flags.
