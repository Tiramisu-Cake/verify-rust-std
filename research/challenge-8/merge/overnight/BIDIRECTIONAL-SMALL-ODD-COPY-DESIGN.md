# Length-three odd-copy source association

Run 37762243525 reached the unchanged `bidirectional_merge` odd branch after
both actual merge calls and the real `is_multiple_of(2)` check. The failing
obligation was the source `points_to<T>` chunk of the checked C1
`ptr::copy_nonoverlapping(last_src, dst, 1)` contract at `verified/lib.rs:492`.
The recorded path selected `right` for `last_src`; the verifier's missing
address was the second field of the forward merge's tuple result. This is an
address-to-resource association obligation, after the earlier numeric copy
preconditions, rather than evidence that the source cell may be unowned.

The bounded profile has `len == 2 || len == 3`. The odd branch makes `len ==
3` by the checked `usize::is_multiple_of` remainder post. The sole forward
merge returns `left == src || left == src + 1` and `right == src + 1 || right
== src + 2`, through its checked result relation. The loop frame and actual
callee posts retain `points_to<T>` chunks and `<T>.own` for all three source
cells. The chosen `last_src` is therefore one of those existing cells, with
the exact choice governed by `left_nonempty` and the cursor values.

`bidirectional-small-prepare.py` now adds one ghost-only case split after the
unchanged `let last_src` statement. Each branch checks the cursor equality and
asserts the existing `*last_src |->` chunk at that concrete source cell. This
does not create a chunk, change a runtime statement, restrict the comparator,
or alter normal/unwind posts. A failed branch assertion is a new diagnostic
about the precise address relation or resource. The generated fixture must
still pass exact ghost stripping and fresh normal-MIR/proof-AST stack-role
linkage; previous SHA and role certificates cannot be reused for the edited
annotation. No local verifier or generator run was made.
