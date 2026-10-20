# R9 candidate 3 independent review — GO for localized translator fix

Reviewed the current translator diff against tool commit
`899c9d7e4ef8370e53926ee6813baa97bb71d701`. The only change moves the
existing `translate_basic_block_id` helper from inside `TrBody` to the enclosing
`Make` module and adds a short scope comment. Its type and implementation are
identical. No call sites, control flow, resource rules, source marker handling,
or profile gates changed.

This is the required scope for the R9 admission code: it translates MIR block
IDs while building the body-level selected-Drop edge binding, outside the
nested `TrBody` module. The helper remains available to all existing
`TrBody` callers through the enclosing module and is now also in scope at the
body-level admission site. The prior compile failure was therefore a lexical
scope error; this move addresses that error without changing the translated
block-ID representation.

`git diff --check` against the candidate commit passed. No compiler, local
preparation, proof, or Cloud Build was run for this review. **GO for this
localized fix only.** This review provides no proof credit or profile
acceptance; normal source/profile closure and Cloud qualification remain
separate gates.
