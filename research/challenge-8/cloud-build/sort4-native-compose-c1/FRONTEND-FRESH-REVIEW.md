# Fresh helper frontend review before semantic implementation

Verdict: **BLOCKED on the strict lifetime dependency**. This is a read-only
review of the Build4 capture and the proposed new helper-only callback overlay;
it grants no proof or tool-profile acceptance.

The captured original helper `Func` has SHA-256
`64c01593d890907756c2e707e09adb9da80c6a1d0967a6720d2200defacf8b06`
and immutable MD5 `f9e8dd5ea212287b36fa0beddd896528`. Its full normal and
unwind contracts are intact. It has one `FnMut::call_mut` switch at source line
199, with the original returning and direct-unwinding clauses. The source marker
block at lines 188–198 contains the debt close, pair recovery, four-cell join,
CURRENT full-array/owner join and T/F type leaks; the normal path contains its
separate source-written steps at lines 200 and 204–210. The paired full MIR
audit identifies the eight call temporaries as normal `_33`–`_40` and readonly
`_7`–`_14`, with ordered source operands 1 then 0, direct `Continue`, and no
cleanup/Drop. These pins support a narrowly scoped rewrite design, not proof.

The Build4 production translator SHA `4dc5f332d4c813fee966ef0724aa1f8ce0e6578ff1e15a0cb61bfb9719c6d14e`
and its corresponding `src/verifast.ml` have no operative strict lifetime cut.
The only occurrence of `SORT4_STRICT_LFT_CUT` in the current translator is the
capture instrumentation's environment check. The captured `'cmp` block still
closes at source line 203, after the `end_lft_binding::<'cmp>()` call at line
202. That call is not defined in the current tool/spec. The separately reviewed
`verifast-strict-lft-cut-26.10.patch` treats this source marker as a scoped cut
and adds verifier checks against lifetime-typed heap and outer-type escapes.
Stock `BlockStmt` handles lexical names and local frees, but has no equivalent
escape check. Replacing the marker with `Noop` and relying on the lexical close
would therefore delete the lifetime-end obligation; the absence of intervening
source statements does not make that substitution admissible.

Before implementation, pin and review the exact strict-cut dependency (or an
equivalent checked mechanism) in the isolated tool chain, then obtain a fresh
pre-overlay helper AST fingerprint under that exact chain. The new overlay must
still preserve the source debt close inside `'cmp`, leave the checked scope once
on both callback outcomes, execute the source CURRENT recovery/join/type-leak
steps outside it, retain the original normal clause and all full posts, and
reject additional control or callback shapes. Moving the eight uninitialized
callback declarations requires a path-level allocation/free audit: the tuple
declaration can produce an object, and its timing changes if relocated from
the function root. The existing pointer-add intrinsic lowering must be pinned
as stock behavior; the patch must not suppress a new edge. A positive VF0
cannot itself admit the revised tool semantics.
