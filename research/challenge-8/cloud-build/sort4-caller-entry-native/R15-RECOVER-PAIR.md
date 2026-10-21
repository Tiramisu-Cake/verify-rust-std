# R15 checked pair-recovery dependency

`a1-actual-recover-pair.rs` carries the existing `comparison_debt<T>` and
checked `recover_pair<T>` proof text from the callback recovery fixture. The
recovery closes both initialized-reference fractions, merges the reserved
lifetime token, ends that lifetime, consumes both borrow-end tokens, and opens
the current full-borrow contents. The posts return the current values at both
slots with one `T.own` per slot. `T` remains generic; no `Copy`, `Freeze`,
comparator law, pointer-address premise, or new axiom is added.

`join_four_owned_cells<T>` reverses the current four-cell capture split. Its
precondition contains the four current point-to-point values and exactly one
`own<T>` for each value. Its postcondition keeps those values in their original
order in the four-cell array and one `foreach` ownership sequence. It does not
copy values or create another owner.

The intended positive focused targets are the checked bodies of
`recover_pair` and `join_four_owned_cells`, plus exporter discovery through
`r15_recover_pair_type_anchor<T>`. The anchor has only generic pointer
arguments; it invokes no comparator and does not claim actual `sort4_stable`
runtime behavior. These are independent checked dependencies. The actual body
must not consume either as a presumed summary before the matching same-unit
focused checks pass.

The marked negative `recover_pair_missing_reserved_half_negative` supplies
`[1/4]lifetime_token(k)` where `recover_pair<T>` requires `[1/2]`. Its expected
failure location is the ghost `recover_pair::<T>(left, right)` call, at that
lemma's missing lifetime-token precondition. A setup/export failure or any
other rejection is not this negative's expected observation. This synthetic
negative is metadata for a later paired focused check, not a proof result.
