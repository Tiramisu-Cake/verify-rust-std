R14-01/P1: CLOSED by static source evidence. The only source delta imports the
original grandparent sort4_stable. Both calls at lines300/301 resolve to that exact
declaration. Frozen r4, removed/renamed/wrong-target/cfg-disabled imports reject;
the repaired source, legitimate qualification and alias pass. The copied bodies,
len>=8 branch, six assertions, domains, frames and initialization remain unchanged.

R14-02/P2: CLOSED by actual synthetic semantic gate checks. With imports at module
scope and original function attributes preserved, the exact ordinary1/ordinary2
chain rejects contracted swap_if_less in BOTH ordinary and combined gates. Safe
s2_swap_seam remains inventoried by full identity. Three-level/module aliases,
function-target/replacement chains and cycle/ambiguity/unresolved controls pass.
Only ordinary_contract_source_sha256 and cfg_pfc_source_sha256 are removed for
the independent alias discriminator; no byte-guard result substitutes for semantics.

New R14-03/P2: OPEN. Nested-parenthesized unbound static calls disappear from the
new lexical gate instead of rejecting. R14-03-DISCRIMINATOR.json and REPORT.md give
the exact reproduction and localized repair contract for original13. Therefore
the review verdict is CHANGES_REQUIRED even though both original findings close.

Closure is static/synthetic only. Native compile and causal repair NOT_RUN;
actual R3 failing unit/body UNKNOWN; independent proof credit NONE.
