`kani -Z uninit-checks tests/expected/uninit/unresolved-calls/fn-pointer-plain.rs` reports an unsupported function-pointer call; this regression covers an initialization check omitted on main and preserved by this PR.
This follow-up uses `checked_body` during call resolution and clarifies comments and diagnostics, with matching expected text; validation of this follow-up was limited to static checks.
*Disclosure: this change and this comment were prepared with the help of AI assistants.*
