# R11 explicit core consumer activation

T0 2026-10-20T21:41:43Z, main 23:41:43Z, absolute 2026-10-21T00:11:43Z.

Defect: existing bounded native-p1-target preflight, helper profile maps, and
lossless row-pointer serializer recognize R10 but not the newly authorized R11.
The old protocol ID is retained while authorization/profile/account are distinct.
Register only exact R11 phase/profile in each consumer. Keep all 26 planned rows,
partial target reporting, malformed/null/conflicting values, original exceptions,
source binding, deadlines, admission and proof-credit criteria unchanged.

Serializer applicability: JSON-derived observation/details duplicated at exact
same case ID within a single report. Replace only type-identical recursively
equal JSON values with escaped local JSON pointers. Every detail/source byte
remains present; disagreeing or malformed values remain inline. No evidence
verdict or receipt is invented. Historical R9/R10 behavior is retained.

Controls: R11 and historical supported positives; reject R9 bounded target,
wrong authorization/protocol/hash; all JSON scalars/arrays/maps/Unicode/escaped
case keys roundtrip through local pointers; bool vs int, null, missing,
wrong-type/conflict/duplicate rows remain inline. Actual Cloud is still required.


## Own false31 boundary scope defect

R10 S3 root INCONCLUSIVE reports global unique/ordered guard rejection.
Source `_compose` retains both a1_guard_observer and original quicksort caller;
both include the identical inclusive threshold guard. Scanning the entire
source incorrectly requires only one occurrence across two distinct functions.
Limit unique/strict ordering to the exact caller MIR Body.span already bound
by paired normal/readonly MIR and certified source hash. Require this span to
select exactly a1_guard_observer in the native AST; retain threshold call-line
join, checked native contract and own receipt/body prerequisites. Reject missing,
wrong-path/type/out-of-bounds spans and duplicates/reversal inside that caller.
This corrects the reporting gate without reclassifying historical observations
or weakening the intended assertion. Synthetic scope controls plus own actual
Cloud lifecycle remain required; no proof credit from this change alone.
