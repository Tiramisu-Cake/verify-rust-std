# Entry observer — conditional diagnostic only

DRAFT / NOT_IMPLEMENTED / NOT_RUN. Use only if corrected prepared diagnostic
reaches the unchanged strict entry refusal. No semantic proof credit.
Base kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c;
frozen translator1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313,
HEADf76012fb518703b1d98e243ac4f487f16877cfcb; no strict draft or peer changes.

At src/verifast.ml2585 List.map(name,tp), immediately before unchanged
freeze_strict_type l "entry outer type" [] tp, an environment-gated stderr
observer prints name and string_of_type tp. It does not catch exceptions,
resolve inference, alter type/debt/owner/token/heap/bounds or substitute types.
The original strict refusal remains unchanged; last printed entry names the
first offending current type. Gate is default-off SORT4_STRICT_LFT_TRACE=1.
Malformed gate values must refuse, all exit/cut/conservation checks remain.

Input: exact corrected prepared positive/false-Args diagnostic. Expected:
original entry refusal at same source location with ordered local/type trace.
A parser/ref-own/Args failure earlier is not evidence for a general rule.
Decision: identify exact variable and evaluate source-specific scope from
pinned MIR; if it requires an unsupported general rule stop repeating proof
runs and publish minimal dependency. Fresh native C1 binding remains separate.

Required review: only observer/gate added, unchanged exception and predicate;
default-off byte/effective-profile review, saved classifier replay; one Cloud
run with both compatible diagnostics, no historical full matrix.
