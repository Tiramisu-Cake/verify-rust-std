# Address-taking after fraction merging

The source pin remains VeriFast 26.09,
`809de4596839b739dd999f9e462242c835e3af46`. The opt-in
`tuple_address_taken` profile inherits the tuple parser, HRTB and strict
lifetime-cut patches, then applies [verifast-address-taken.patch](verifast-address-taken.patch).
Its SHA-256 is `2c44ad1cdb218b82d8f82c714841fdeab2b76b356474ec146e2a780289acdf4a`;
the original `src/verify_expr.ml` SHA-256 is
`af5f7399d63e2ce2d5fc18291466b406c278f49d6bcb966ed49d644782958e2e`.

The patch adds `cont locals` to the `MergeFractionsStmt` arm of
`stmt_mark_addr_taken`. Without it, `stmts_mark_addr_taken` stops scanning
the remaining statements. The later address of the actual `ManuallyDrop<T>`
local in `insert_tail` is not marked, and its declaration stays a value
instead of using the verifier's existing addressable storage. Consequently,
the unchanged guard initializer fails with "Taking the address of this
expression is not supported" in run
[37414755368](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37414755368).

This is a traversal fix, not a new model for `ManuallyDrop`, allocation or
ownership. The pinned translator already erases its transparent wrapper and
uses identity operations for `new` and dereference. The patch enables the
existing local-storage path to see the later address expression; subsequent
reads must still possess their matching heap chunks.

Hosted acceptance runs the existing eight HRTB and twelve lifetime-scope
cases, followed by three physically isolated address tests. Two positive
functions read a scalar or a `ManuallyDrop<i32>` local through a pointer after
`merge_fractions`, with an exact result postcondition. The negative case
deliberately discards the read permission and must fail on the ensuing
dereference with the intended missing `points_to` error. Compiler export,
MIR decode and source hash roundtrip must pass for every case. No frontend
error qualifies as a successful negative test.

The actual unrestricted `T`/`F`, symbolic-length insertion probe then runs
with the same Rust bytes and ownership contract as `tuple_lft_cut`. Passing
the guard address expression is the next prefix milestone; guard ownership,
loop invariants, cleanup and the restored-range contract remain obligations.
All executable validation runs on hosted Actions. The prior profile remains
available to reproduce its address-taking failure.
