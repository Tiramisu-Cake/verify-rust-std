# Actual c1 missing-debt controls — preimplementation card

2026-10-09 after Builda80d95f6: exact c1 equality emitted once; full preAST and
source/MIR preserved. Direct unwind executes close186/recover187/join188/
original return190/leak226. Normal executes close191/strict exit192/recover193/
join194 then c2 preparation195 fails ref_precreated_token<T>(v_base+3,_).
Do not fix or implement c2. Normal full-function return/leak remains NOT_RUN.
The collector rejects library-origin diagnostic location; this is audit-only,
not an admission/resource verdict. Retain original Cloud FAILURE and raw data.

One final affected control step, within main window: keep positive rewritten
AST exact c4f0fdd1 and posts23b6309a. In isolated exact translator add default-OFF
negative-only selectors normal-missing-close/unwind-missing-close. Each replaces
only the selected source ghost debt close by Noop/omission AFTER original AST,
source/MIR/c1 hashes; other edge, original callback/assignment, strict scope,
recover_pair/join, full posts and remaining runtime operations stay unchanged.

Falsifiable expectation: absent comparison_debt<T> at ordinary recover_pair call
source193 normal /187 unwind, No matching heap chunks: comparison_debt<T>.
A strict exit/type/setup/frontend failure at an earlier obligation is
INCONCLUSIVE for this intended resource negative, never count it as success.
This changes neither normal case semantics nor memory model/kernel. Negative
removal intentionally tests the recovery premise; no supplied permission or
summary is created. Default case must retain exactly the prior c4f0fdd1 postAST.
Same-unit helpers and fresh affected strict/false-post gates under new console
remain required. Positive normal/join and unwind post/leak tracked separately.
Each mutant's raw log/status/case result persists before aggregate.

Additional verbose=2 same positive invocation is diagnostic logging only, to
retain detailed proof state if supported by the frozen console. No local proof.
No general alias mechanism; broader alias/storage/false actual-normal return
mutants and profile qualification remain OPEN. Caller resource derivation and
legal shared-entry/generic/ZST applicability still supplied/open. No c2/selector.
