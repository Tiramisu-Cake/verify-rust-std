# Nearest actual sort4 caller obligation — read-only mapping

Source `library/core/src/slice/sort/shared/smallsort.rs:606–656`, blob40939f922bcb6fdc7ee0d30427fa861827043827,
sha25685c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1.
Five unrestricted FnMut comparisons before any destination write; eight select
calls instantiate by-value selector with raw pointers `*const T`; four
copy_nonoverlapping calls. Pointer-select domain is relevant, but no unverified
selector summary is usable and no generic by-value select<T>/ZST theorem follows.

Nearest actual caller obligation after sufficient select is c1, `v_base.add(1)`
versus `v_base`: preserve/recover four readable current source cells and comparator
F.own on both normal and unwind; preserve four writable destination slots. No
purity/SWO/Freeze/Copy or no-panic premise for safety; ordering separate. There
are no writes before callback completion, but interior state may change; restore
current resources, never initial-value snapshots after callback.

Existing O24 review/capture `overnight-callback/ACTUAL-SORT4-FIRST-CALL-REVIEW.md`
verifiedfddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9,
ghost-stripped3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72,
normalMIR667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d,
readonly925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5.
It stops at reserved __vf_sort4_first_unwind (`No such function`); capture/calibration
only. join_four_owned_cells is an isolated positive-size lemma, not callback proof.
Design-only AST scope + strict CUT requires its reviewed raw-MIR/lifetime/storage,
normal/unwind and false controls; no accepted actual sort4 profile can be reused.
Full safety/four elements/comparisons/selects/copies and functional
permutation/ordering/stability remain open. No sort4 experiment dispatched here.
