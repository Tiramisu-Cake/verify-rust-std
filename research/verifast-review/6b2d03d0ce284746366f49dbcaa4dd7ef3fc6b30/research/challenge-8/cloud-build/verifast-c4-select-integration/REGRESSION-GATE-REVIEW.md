# Regression gate tightening — 2026-10-10

Read-only review findings were applied only to `driver.py` and
`regressions.py`; no translator, verifier, source fixture, or coordinator input
was changed.

The selector cleanup-off diagnostic now requires the pinned three dead-code
spans, expected exit 1, no verifier error, ordered seven-helper/nested/outer
proof evidence, complete helper/nested normal-unwind checks, and both outer
normal returns. Partial cleanup opt-in still requires the exact certificate
refusal marker and incomplete root/test pair before any function header.

ManuallyDrop pass fixtures now require target function headers, zero-error,
return, leak, and no-dead-code evidence. The contradictory-precondition case
requires all four archived dead-code spans: the full function, both line-6
expressions, and the closing brace at `dead_code_pre.rs(7,2)`. False-post
fixtures carry exactly one `//~should_fail` marker at the expected source
contract line (line 3 normal; line 14 unwind). Their gates require exit 0,
zero verifier errors, the target function header, return/leak completion, and
the exact assertion-plus-expression consumption events at that line. This is
successful `-allow_should_fail` harness behavior after consuming the annotated
false contract, not a printed verifier-error negative. Raw VC review remains
pending.

The wrong-selected-original control is recognized only for a single
`Cannot prove condition` at the injected line-487 assertion after all nine
selector definitions and C4 entry. Independent raw review remains pending.
Top-level `diagnostic_complete` now requires composition plus all completion
gates, including exact-reviewed controls; incomplete or missing evidence is
recorded as `INTEGRATION_DIAGNOSTIC_INCOMPLETE` and listed explicitly.

Still unresolved and intentionally blocking completion: same-source
source/contract/type/Move/edge/reachable-unwind admission mutants; strict
lifetime outer-type escape; frame and thread-resource controls; raw VC review
of the composition/C4 controls; and proof execution itself. The cleanup
projection has exact typed call/edge and full-unit hash guards, but the
reachable-unwind refusal mutation is not exercised by this runner. No compiler,
extractor, verifier, or proof runner was executed; only Python AST syntax
parsing was used.
