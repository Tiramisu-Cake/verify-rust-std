# R12 syntax preflight and helper-body evidence

The grammar preflight contains a positive Option-cleanup lemma and two
negative grammar controls. Its positive verifier invocation can reach the
lemma body and fail on the currently observed `Function leaks heap chunks:
own(ref_typeid(` diagnostic at the exact certified helper closing line (line
12 in the minimal fixture). Treating every nonzero positive exit as a grammar failure prevents
the canonical source cases from running, even when VeriFast emitted an AST
whose exact helper definition is selected.

R12 therefore records grammar and helper-body outcomes separately. The syntax
preflight passes only when the positive stage is terminal, its log and source
pair are intact, the exact manual helper AST is selected, and the positive
stage either exits zero or has exactly the known single body-leak diagnostic
at the certified helper closing line. The message immediately after
`: error: ` must be the complete observed `Function leaks heap chunks:
own(ref_typeid('a_typeid,T_typeid))(t,0)` form; a preceding unrelated error,
other verifier errors, wrong lines, multiple diagnostics, missing ASTs, and
partial/deadline stages remain
inconclusive or blocked. Both negative controls retain their exact expected
diagnostic checks.

Even when the known body leak is observed, the preflight sets
`body_verified=false`, `proof_credit=false`, and `caller_receipt=false`. It
does not create or satisfy the checked-helper prerequisite. The existing
canonical positive flow still runs P0a/P0b, then P0c's fresh same-Build helper
body stage before its caller stage. P1 likewise retains its own fresh
same-Build helper body stage before interface classification. No preflight
AST, stage, or error record is reused as a canonical caller receipt.
