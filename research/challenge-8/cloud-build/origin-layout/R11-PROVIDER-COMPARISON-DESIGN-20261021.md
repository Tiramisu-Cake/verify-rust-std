# R11 hosted-provider comparison

The parent-validated R11 tuple stores a canonical provider identity with the
required keys `provider`, `build_id`, `project`, and `region`. The hosted proof
helper may return the same required identity plus additional metadata. Whole-
dictionary equality rejects that valid superset and caused the placement
campaign to stop before replay.

Compare only the four required fields, while requiring their exact types and
nonempty values, then compare proof SHA exactly. Missing, null, wrong-typed, or
mismatched required provider fields still fail closed. Additional provider
metadata is ignored; it never replaces the exact run identity or any native
source/artifact receipt gate.

Independent GPT-6 Luna HIGH reviewer r10_review GO: extra metadata allowed but four identity fields remain exact nonempty strings plus proof SHA; current env/run and native artifact gates unchanged. Provider synthetic positives/errors PASS, placement service11PASS.
