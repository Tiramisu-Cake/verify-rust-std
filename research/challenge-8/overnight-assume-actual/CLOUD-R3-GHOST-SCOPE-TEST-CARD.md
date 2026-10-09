# R3 ghost-scope routing TEST

The 03b Cloud run refused before any VeriFast proof header: both R3 lexical and
nested-order cases reported `actual outer/nested ghost scope inventory` at
`translate_body` line 6432. Exact R3 NORMAL and readonly captures export four
outer ghost annotations: two new saved-input `let` bindings at source line 155,
then the two existing nested `open` annotations at lines 167–168. The exact R3
owner admission already transfers the latter two into
`actual_nested_ghosts`, but the frozen outer routing branch compares that pair
against the first two outer annotations. The nested body's exported ghost list
is empty.

This standalone patch applies only after the R2 and immutable R3 patches to a
disposable Cloud tool copy. Base R3 translator SHA-256 is
`34a03879b45377570eab81ee384ade01ebea9d5d216eb6223c6c742c5819dc15`;
the new patch and statically applied translator hashes are in
`O26-R3-GHOST-SCOPE-TEST.json`. The additional exact-root
`SORT4_R3_GHOST_SCOPE_TEST_REPO_ROOT` and `SORT4_R3_GHOST_SCOPE_TEST=1`
are required alongside all R3 opt-ins. Missing or partial TEST opt-in retains
the frozen branch or refuses, respectively. The enabled branch requires exact
R3 nine-body admission, checks the two saved-input annotation strings and both
stored nested opens, retains the saved bindings in the outer body, and routes
only the two original opens into the qualified nested Drop body. Other bodies,
source, runtime, contracts, parser, kernel, memory model, exporter and refiner
are unchanged. The original routing remains the default.

A fresh Cloud build and full NORMAL/readonly, positive and negative evidence
are required. Controls must distinguish a wrong saved binding, missing or
reordered nested opens, partial opt-in, changed source or unit, and errors at
the exact routing gate. A green proof cannot establish soundness of this new
trusted translator branch without those independent controls and the full
normal/unwind/return/leak obligations. This is a diagnostic TEST only:
`mutation_controls_complete=false`, `actual_nested_drop_credit=false`, and
`verification_accepted=false`. The separate nested-before-outer scheduling
TEST, if layered, needs a fresh combined translator hash, build and certificate;
its old hash cannot be reused.
