# Kani3300 B1I final semantic review

Reviewed candidate source commit `dc5f5a406749a73f1c3192e0b5338441e79508bb` (tree `085bea5cda2df66a5cb4f72410fe124aa816c90b`), parent production commit `cdb439b0a4c36e9e595019895ab803230f332941`, based on `a0a2386001a15fecfe2facc2f6cd87f3dee13b60`. Worktree was clean at review. Review remained read-only. No cargo/rustc/Kani/CBMC/build/Actions/Cloud commands were run.

## Production verdict

**Scoped semantic review: no production blocker found.** The production diff preserves one `super_terminator` traversal and one final target push for all call paths; the order remains entry LoadArgument, operand reads, then local Unsupported. The local visitor owns rejected-call diagnostics independently of delayed seeds; points-to and local visitor use the shared call resolver; seed resolution is fallible. Bodyless nonforeign Item/Shim calls are rejected locally before points-to body use, and bodyful Shim analysis does not grant the unchanged Item-only A3 transfer predicate. Existing A3 caller/callee predicate remains `Item && !foreign && has_body()`. No ABI/layout/Move/raw_eq scope change was found.

The initial foreign-effects concern was withdrawn after source-path verification: foreign calls are handled by a separate branch in points-to, not by the new regular-call body `let-else`; base already accepted foreign FnDef calls and the diff does not broaden those models. Opaque non-shadow foreign effects remain an explicit pre-existing adjacent B4/realloc limitation outside this task; do not make a full foreign-domain fail-closed claim.

Static checks: `git diff --check` clean; all 11 pinned rustc_public source hashes match `API-SOURCES.json`. The reviewed `Instance::body() -> Option<Body>` API eagerly builds MIR; for newly rejected bodyless nonforeign Item/Shim cases, the same resolver result causes the local visitor to emit Unsupported while points-to returns before body conversion, preserving its prior graph.

## Fixture and manifest review

- The candidate contains 24 source/golden pairs; integrated manifest v1 lists 33 unchanged existing controls and four `NONEXECUTED_COMPILER_INPUT_SPECIFICATION`s. Every fixture state remains NOT_RUN. At final hash verification, all 24 source/golden pairs matched manifest SHA256 values, all 12 seeded source variants contained the ordinary-byte `copy_nonoverlapping` seed helper and invocation, and the six custom-MIR fixtures used bound argument names. The earlier `_value`/`value` mismatch in the four entry fixtures was corrected before this final review.
- The four entry fixtures keep the custom-MIR `bb0` empty and now use a runtime union argument. The partial case selects one byte before a `u32` read. These avoid the known ordinary-union constant path. Actual aggregate/Move lowering, entry LoadArgument emission, Check status, target count, and operation execution order remain NOT_RUN; output substrings alone do not prove them.
- The FnOnce shadow-argument-only source pair is explicitly `SOURCE_LOWERING_PROBE_ONLY`; its golden is provisional. A tuple-wrapped argument may not reach the visitor's direct `transfers_shadow` test. It is not coverage of that guard. The separate synthetic direct-argument compiler specification is still required before claiming this acceptance case complete. The return-only and plain/seeded Shim source controls likewise need actual Shim kind/body confirmation.
- FnDef resolver `Err` distinct from FnPtr remains only a compiler-level input specification; source FnPtr fixtures do not cover it. Bodyless Shim/LlvmIntrinsic and bodyless Item code paths also have input specifications, not executed controls. These are explicit remaining review/CI obligations, not PASS evidence.
- No legacy A3 coverage loss was identified statically: ordinary bodyful Item calls keep the same pairing predicate; existing shadow-argument/return rejection for foreign and FnOnce/shim paths remains. Existing outcomes still require coordinator Quick.

## Remaining limitation and handoff

The manifest currently reports `candidate_commit: PENDING_TEST_COMMIT`; update it to the exact candidate SHA after the hash-only research commit. The static candidate can be handed to the coordinator, but it is not runtime- or lowering-validated and does not complete the direct-shadow-argument synthetic control, the FnDef resolution-Err control, or the Shim lowering confirmations. Keep these marked NOT_RUN and do not report test coverage/pass until the authorized coordinator Quick and required MIR/property inspection.

Reviewer: independent GPT-6 Luna, HIGH reasoning, `/root/semantic_review`; no nested delegation.

Main-agent metadata finalization: manifest `source.candidate_commit` is now `dc5f5a406749a73f1c3192e0b5338441e79508bb`, with exact tree and production parent recorded. This changes research identity metadata only; reviewed source/golden hashes are unchanged. No compiler/control execution was added.
