# Independent raw review: final composition Build `063d90bc`

**Composition result: PASS on the saved consumer proof. All six targeted
controls reach the consumer and produce their exact intended first VCs. The
overall Cloud lane remains incomplete because its later regression driver
raises a setup exception; this review does not convert that run-level failure
into acceptance.** Review used only the completed standard Cloud archive and
saved raw evidence. No compiler, verifier, extractor, or Cloud command was
run.

## Exact run and artifact pins

The verified archive SHA256 is
`8d543f47d80e535f876dfd63387d588d8278c6eed10ee6af32657e85a6458934`, Build
`063d90bc-572a-4182-bc04-9528b3a9eea3`, proof SHA
`9ffa34d2c35032cb3bd5c4172b40c95989eb3fa9`, and manifest SHA
`aed799ea2d20d2c9cf4367a2392327d1f5d7583b7f9a71511d10a0bd3b0ea694`. The
effective-hash record says `exact: true`; translator SHA256 is
`4450157b3137a58d46c4be52fd454695c1dcb2a123947df8b3d2ccfcc1e8f26f`.
Archive-index hashes for the producer artifact, composition log, composition
proof record, selector proof record, and final result record match the
provisionally extracted files. The producer artifact remains the reviewed
`48bbedb711fade25fde0622af0b56c6c17aab318ce0a94f1e517f9c153a81af9` seal.

## Producer, parent, and imported consumer

The fresh selector producer record reports exit 0, no errors or dead-code
diagnostics, `0 errors found`, return and leak checks observed. The C4 parent
record reports the same successful proof properties. The consumer record
reports exit 0, zero errors, no dead-code diagnostics, return and leak checks
observed, and 466 statements verified. The consumer's source pair is the
pinned C4 original/verified pair; the imported selector source is the pinned
selector source.

The raw consumer log contains this certificate:

```text
typed location-only certificate paths=3442 ordinary_strings=0 ref_sharing=none unsupported=none location_alias_partition=preserved raw_replacements=439
```

The following import record binds the same producer artifact, relocated
artifact, and reverse hash:

```text
importing nine definitions sha256=48bbedb711fade25fde0622af0b56c6c17aab318ce0a94f1e517f9c153a81af9 relocated_sha256=b4f4683d796137fcc55b51ff670caab538f5f56bf6f741cae2ca6af85a41380a reverse_sha256=48bbedb711fade25fde0622af0b56c6c17aab318ce0a94f1e517f9c153a81af9 location_occurrences=439
```

All nine imported selector body verification events occur before
`sort4_stable`; the filtered order matches the required seven helpers, nested
Drop body, and outer selector. The consumer reaches `sort4_stable`, completes
its original postconditions, return, and leak check, and ends with
`0 errors found (466 statements verified)`. This is fresh consumer evidence
for the sharing-preserving transport on the exact reviewed artifact.

## Six control VCs reviewed against raw source and trace

Each control keeps the pinned `verified/lib.rs` bytes and applies its
source-anchored translator control. Each raw log imports all nine selector
bodies, repeats the same typed-location/alias certificate (`3442` typed
endpoints, `439` raw replacements), verifies the selector bodies before the
consumer, reaches the `sort4_stable` target, and then reports exactly one
error with no dead-code entries. I checked each first error and source pattern
directly:

| Control | Exact first VC observed | Source/control correspondence |
| --- | --- | --- |
| `wrong-selected-original` | `verified/lib.rs(487,19-55): Assertion might not hold. (Cannot prove false.)` | The first-select negative asserts the opposite branch-selected element at the source-487 select site. |
| `normal-false-post` | `verified/lib.rs(315,21-24): Cannot prove condition. (Cannot prove false.)` | The translator substitutes `false` for the normal-return postcondition. |
| `c4-normal-omit-join` | `verified/lib.rs(317,5-12): No matching heap chunks: foreach<T>(...)` | The normal C4 join is omitted; the normal ownership postcondition fails at the source foreach. |
| `c4-unwind-missing-close` | `verified/lib.rs(68,29-30): No matching heap chunks: comparison_debt<T>(...)` | C4 unwind debt closure is omitted; the failure is at `recover_pair`'s source precondition. |
| `leak-thread-token` | `verified/lib.rs(315,5-17): No matching heap chunks: thread_token(t)` | The exact semantic control leaks the thread token after source-487 selection. |
| `leak-current-four-cell-frame` | `verified/lib.rs(316,17-20): No matching heap chunks: array<T>(v_base, 4, _)` | The exact semantic control leaks the current four-cell frame after source-487 selection. |

For every row, the raw error is the first error and appears after the
`sort4_stable` verification event. These are observed VCs, not runner-intended
labels. The wrong-selected case is an assertion failure rather than the
runner's narrower `Cannot prove condition` string pattern; its raw location,
message, and reversed selector assertion nevertheless match the intended
negative exactly.

## Run-level limitation

The top-level result remains `SETUP_OR_EXECUTION_FAILURE`, with
`diagnostic_complete: false` and `verification_accepted: false`. After the
consumer and all six controls, the regression runner fails at
`regressions.py:463` while looking for
`/workspace/infra/research/challenge-8/cloud-build/verifast-c4-select-integration/manifest.json`;
that path is absent in the staged layout. The outer-bound normal/readonly
capture and refinement stages themselves completed with exit 0. This is a
late runner path/setup failure, not a composition proof failure or a semantic
negative. The failed regression stage still needs an authorized repair and a
fresh run before the full lane can be marked complete.

## Classifier follow-up

**Static review: GO for the narrow `wrong-selected-original` classifier
correction.** The archived `row["errors"][0]` is exactly
`verified/lib.rs(487,19-55): error: Assertion might not hold. (Cannot prove
false.)`. Therefore a `re.fullmatch` for that literal, escaping punctuation,
correctly recognizes the observed assertion VC; the previous pattern
expecting `Cannot prove condition` cannot. Keep the existing permitted-exit,
target-before-error, nine-header, and AST-import requirements, and leave the
control classified `PENDING_INDEPENDENT_REVIEW` until this independent raw
review is attached. This classifier-only correction makes no proof or tool
claim and does not alter the six-control result reviewed above.
