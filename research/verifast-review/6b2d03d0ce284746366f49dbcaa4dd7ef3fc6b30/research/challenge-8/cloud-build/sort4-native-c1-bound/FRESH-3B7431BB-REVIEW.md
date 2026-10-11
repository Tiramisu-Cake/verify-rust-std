# Fresh corrected native C4 bound candidate review

Build `3b7431bb-4e18-4921-b690-307e4ba7f984` used proof/infra
`8de4cda418c4772009359fbb90e7e7f34836cca0`. It ran 465 seconds (created
`2026-10-11T10:26:03.935776892Z`, terminal
`2026-10-11T10:33:48.564284Z`), bringing charged time to 2526/3600 seconds
(1074 remaining). Collector completed with all evidence and text logs; its
verification-accepted flag is false. Archive SHA-256:
`4e9c337e98d403d5959d0581c8739b4510cb5b94b977fae2ce0a947b35e4f6e4`.
The full inventory has 1053 independently checked hashes. See
[FRESH-3B7431BB-INDEX.json](FRESH-3B7431BB-INDEX.json) and raw artifacts under
`allprooflogs/cases/sort4-c1-current-recovery/`.

All nine ZST model gates passed, including the ZST/non-ZST layout matrix,
nonvacuity, paired source/MIR checks, and intended assertion/resource
negatives. The retained native C1 prerequisite candidate/control results also
have the intended classifications: candidate binding passes; normal and
unwind false controls reach their assertions; admission controls refuse. In
the raw result also contains `native_c1_to_c4: NOT_RUN`, which refers to the
legacy separate C1-to-C4 driver path. It does not describe the current
`native_c4_bound` target: that target executed the four sequential native C1–C4
comparator expressions together in the guarded fragment and reached VF0. The
external SmallSort caller and callable summary remain `NOT_PROVED`.

C4 now reaches verification on the corrected inventory. Its exact-source
positive is a VF0 candidate: exit 0, `0 errors found (485 statements
verified)`, with the full normal cleanup including owned scratch, callback
resources, `CURRENT` restoration and leak check. The four actual direct-unwind
false controls and the normal false control each reach their intended false
assertion. The first-error locations are recorded in the index (normal 577,
unwinds 387, 442, 504 and 561). The source-hash, extra-body, malformed and
mixed-environment controls refuse at their intended admission checks. Default
off remains unadmitted and emits a parse error; it is not a semantic negative.

The raw positive control-flow audit records all 503 REGISTER IDs (0–502) in the
EXEC set, with no DEAD-code diagnostic. The zero-size dispatch at source line
322 takes the `sizeof(T)==0` route through labels 3/4 and returns through cleanup;
the `len < 8` route at line 330 is also executed and reaches cleanup. The four
source comparator operands are `(1,0)`, `(3,2)`, `(c,a)` and `(d,b)`, where the
last pair is derived from the preceding C1/C2 booleans. Each of the four actual
`FnMut::call_mut` sites preserves its direct-unwind edge and full unwind cleanup,
including native `v`, scratch `MaybeUninit` ownership, and callback resources.
The normal/unwind posts retain the thread resource and all three lifetime tokens.

The verified/original source hashes remain
`0f92a609c898df5271cbafd04cea688bf7b46c8b4786f8313b8ff99db995e9c4` and
`9628df15e3a42643d671bd1e9f5684e0bdd81162e26ab8233ce704a9657942df`.
Normal and readonly full-MIR hashes remain
`b0da712d2b16c76d1baac91ae69c591ddeab308a2242e196fe876fd27e35e24d` and
`79c16a30be7b2921ccdaa35c66aac496f236d900130fff72a36b81524e50ef86`; the
pre-transform AST is `65b9ddf282ab3b8d123bba3725600528936ff09e236c4261841d61f66cb5ae18`,
and the positive post-transform AST is
`759d08b814674869c26ec067c34c259d819cadbf7703ac76009b048e6bebf675`. Paired
normal/readonly support passed for `small_sort_general_with_scratch`. Effective
translator `66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124`,
verifast1 `bfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207`,
and kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`
match the corrected candidate.

This is raw-reviewed evidence for the isolated four-call native C4 fragment,
not an accepted verifier profile or a proof of the actual external caller,
complete `small_sort_general`, selector/C5/copy path, or unrestricted generic
`sort4_stable`. The exact target `small_sort_general_with_scratch` already has
`T: FreezeMarker` in its source signature (line 220 in the pinned source); this
is an existing source-domain restriction, not a new bound introduced by the
patch. The separate `sort4_stable` source at line 606 has no `T` bound, and this
fragment does not establish its unrestricted generic contract.
The driver reports `actual_caller_proved=false`, `callable_summary=false`, and
`proof_credit=false`; profile status remains
`SORT4_C1_CURRENT_RECOVERY_DIAGNOSTIC_ONLY_NOT_ACCEPTED`. Remaining trust
obligations include independent review/acceptance of the Rust ZST size-model
patch and source-specific C4 translator overlay, plus the separately excluded
caller and full algorithm obligations.
