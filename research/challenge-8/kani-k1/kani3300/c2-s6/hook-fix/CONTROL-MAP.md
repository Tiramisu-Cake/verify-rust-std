# Hook continuation control map

Candidate native execution NOT_RUN. Goldens prescribe intended outcomes; not observations.
Baseline source-reported run43645985416 at exact8d is input; run43645617823 is VOID.
All selectors below are under tests/expected/uninit, one selected oracle root each.

| Selectors | Intended outcome / discriminator |
| --- | --- |
| marker-hook-calls/ordinary-hook-return | N1 explicit pairing Unsupported in actual UntrackedDerefHook MU-return caller, initialized low-byte own SUCCESS. No load_argument placeholder/payload UB substitutes. |
| marker-hook-calls/ordinary-hook-scalar | SAME actual hook, u16 return, N0 useful postcall destination37/source37 assertions SUCCESS. |
| marker-hook-calls/fn-item-plain | Generic FnOnce FnDef path, N0 invoke(answer)==42 SUCCESS; not coercion/optimized alternative. |
| marker-hook-calls/fn-item-shadow-return | Actual call_once FnDef shim in invoke, N1 explicit pairing Unsupported before call, initialized17 SUCCESS; no early tuple/layout refusal. |
| marker-hook-calls/generated-modifies-no-shadow | Legal PFC modifies(out), N0 payload7 SUCCESS. Hook returns reference: NONCARRIER. |
| marker-hook-calls/marked-body-{initialized,hole} | Real inline-never MU argument/return identity with unrelated unknown marker. N0 initialized29; N1 u16 hole plus initialized29 SUCCESS. |
| marker-hook-calls/marked-model-{initialized,hole} | Actual inline-never NondetFn1Model receives MU source11, returns ordinary Byte union via AnyModel/Arbitrary. N0 byte41; N1 empty-union byte read; source11 postcall SUCCESS in both. Typed model stays paired. |
| copy-source-arguments/arg{0,1}-{initialized,hole} | Explicit same-place Copy(source),Copy(source) to two argument indices. Each selected hole N1 u32 read; initialized N0 plus original-source preservation. |
| padded-slice-extents/{borrowed,raw}-{initialized,hole} | Actual repr(C) stride/offset assertions; MU slices, prefix crosses slot0 and ends before slot1 final u32 DATA byte. N1 hole u8 read vs N0 initialized, useful data SUCCESS. |

Reuse unchanged forced FnPtr controls, S2 immutable-descriptor-coalescing/registration9,
S3 nested-aggregate-reset and S4 delayed_cache6/delayed_scope2, existing paired MU
argument/return/Copy/Move/known-false witnesses. No mixed JSON or SEL1 import. F11 optional.
Generated modifies(*out) stays E0277 INVALID_TARGET, not semantic refusal. Do not claim
generated PFC shadow transfer or baseline false SUCCESS. Original REPRO/observation
remain immutable. Only missing-hook prerequisite is superseded by HOOK authorization.

Both refusal fixtures add useful initialized assertions to historical sources. Require
matched baseline8d/candidate observations of these SAME exported files and flags,
with exact hook/shim binding. Historical N1 placeholder → intended N1 Unsupported
is a differentiating basis, not qualification of altered sources.
