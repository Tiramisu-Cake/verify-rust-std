# KANI3300 B2 independent static review

Reviewer: independent GPT-6 Luna, HIGH reasoning, separate context, no nested delegation.
Verdict: **PASS — static probe review**, no correctness blocker found.

- Baseline: `230fa9aa656dd90503390019a6c0d153ef93520b`.
- Reviewed candidate: `4770341265db9e8e5b3f4863705f3ae1e5a91703`.
- Reviewed tree: `ffeb23509e0294c4c722e8db2c9c14c8ca71f529`.
- Spec SHA256: `b101253b24546920fb993cecc8b67032835570241f73591a128b4696a3cac068`.
- Diff SHA256: `3ed46f58a3460918b8bd2e130aa172b126303776c35a00af0985fcd06c2467a0`.
- Packet SHA256: `206942e294cadb9a13b5c407faf6a7914b3b1b5bc20d28a88a201d10a89361e7`.
- Both declared dependency hashes match. `smallsort-session review check`: PACKET_VALID_NOT_REVIEWED;
  that structural status is separate from the independent reviewer verdict above.

## Reviewer findings

All 25 binaries have expectation entries. Ten restored cases' names, values, union representations and move forms
match the historical removal between Kani `5b2265c41` and `8639a651f`.
Source raw pointers precede transfer and read the original named local/field. Ordinary probes have initialized
four-byte payloads without padding; the MaybeUninit detector control is explicitly uninitialized.
No unrelated unsafe read or lifetime issue was found by static inspection. Reinit writes the named local before
reading through the old pointer; the source remains in scope. CI must still inspect storage lifetime and reallocation.

Call forecasts are conditional: a pre-call address does not prove MIR passes the original source rather than a temporary;
the callee parameter's address does not settle this. EXPECTATIONS.md correctly reserves this to actual CI MIR/Miri.

## Limits and publication delta

No compiler, MIR or Miri outcome was measured. No proof credit. Compiler/tool execution and CI are coordinator-only.
The publication commit adds only this review record, the exact review packet/spec and result bookkeeping;
`probes/`, `EXPECTATIONS.md` and `removed-cases.md` remain byte-identical to the reviewed candidate.

## Main-agent static checks

Python TOML parsing checked edition 2021, empty dependencies, workspace isolation and nightly pin.
All 25 main/bin names map exactly to the expectation table, use pre-transfer raw pointers and volatile u8 reads;
intrinsic binaries carry the feature gate. Document line limits and `git diff --check` pass.
These checks do not establish compilation or measured Miri outcomes.
