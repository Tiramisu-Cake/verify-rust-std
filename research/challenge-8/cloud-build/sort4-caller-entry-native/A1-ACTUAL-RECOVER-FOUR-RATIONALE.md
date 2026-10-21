# R15 four-source recovery dependency draft

`a1-actual-recover-four.rs` states a generic callback debt independently of any comparator argument address. The predicate carries the two fractional initialized-reference/close-borrow debts and one `borrow_end_token` for each source slot `base` through `base+3`. `recover_four_sources<T>` closes and merges the reference fractions, ends the shared lifetime, retrieves all four current cell owners, then invokes the copied `join_four_owned_cells<T>` helper to rebuild the array and its sole `foreach(own<T>)` sequence.

The helper has no premise relating either reference to the source array, no adjacency or pointer-equality premise, and no saved pre-callback source values. It is a resource recovery rule only: establishing that actual callback references and source cells satisfy this debt is a separate source-pair/proof obligation. It assumes neither callback purity nor ordering laws, `Copy`, `Freeze`, or a type-size bound.

The negative control provides the same reference debts and only three end tokens, then attempts to close the full four-token debt. Its expected rejection is that close, specifically for the missing `base+3` token. This is a source-only draft and is not an integrated callback summary or proof result. Only structural/static checks ran; no compiler, exporter, or verifier was invoked.
