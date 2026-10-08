# G2 trace auxiliary admission — design before implementation

## Finding and exact scope

Run 37715432190, proof input at repository `6ddfd1999991478bdc511546afe5b21e4997e878`, generated a complete G2 trace adapter. The hosted decoded proof AST contains a 12-field local `G2PointerTrace<T>` declaration at `verified/lib.rs(9,1-22,2)`. Stock VeriFast 26.10 (`f76012fb518703b1d98e243ac4f487f16877cfcb`) emits nine generated auxiliary lemma functions at that same source location. The AST confirms that each has a body consisting of `#assume(false)`:

* `is_Send_G2PointerTrace_lemma`, `is_Send_G2PointerTrace_def`;
* `is_Sync_G2PointerTrace_lemma`, `is_Sync_G2PointerTrace_def`;
* `open_ref_init_perm_G2PointerTrace`, `init_ref_padding_G2PointerTrace`;
* `close_ref_initialized_G2PointerTrace`, `open_ref_initialized_G2PointerTrace`,
  `end_ref_padding_G2PointerTrace`.

They are emitted by the pinned translator's struct generation path in
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` (blob
`4e237a61a7e4449735e53220114e57114b51e31a`; relevant generator spans include
the Send/Sync lemma creation around 6750-6790, reference/padding lemma builders
around 7050-7365, and generated declaration assembly around 7490). These are
stock translator output, not hand-authored fixture bodies. Run classification
currently includes them in `visited_bodies`, records zero execution/return/leak
for all nine, and rejects the otherwise checked profile because observed
headers exceed `expected_bodies`. The 13 named trace lemmas have execution, return, and leak records; the
main has execution records but has not yet reached a successful return. The first current proof
failure is later in the main obligation (`verified/lib.rs(452,18-19)`, unbound
`k`); auxiliary admission work must not misclassify or hide it.

This adapter proves only the G2 pointer/index projection. It does not establish
actual SmallSort source correspondence, data-value reads/copies, permissions,
ownership, callback behavior, or unwind safety.

## Implemented adapter direction: remove the local ADT

The adapter now uses a type alias for a nested balanced tree of stock
two-tuples; there is no `struct G2PointerTrace<T>`. The exact tree is
`(( (left,right), (dst,left_rev) ), ( (right_rev,dst_rev),
(left_end,right_end) )), ( (forward_count,reverse_count), (odd,guard) )`.
The 12 projection paths in the result postcondition are respectively
`0.0.0.0`, `0.0.0.1`, `0.0.1.0`, `0.0.1.1`, `0.1.0.0`, `0.1.0.1`,
`0.1.1.0`, `0.1.1.1`, `1.0.0`, `1.0.1`, `1.1.0`, and `1.1.1`. The returned
tuple literal uses that same order.

This avoids local nominal-struct auto-trait/padding helper generation. No
existential return-address chunks cross the loop; the loop invariant keeps its
cursor geometry and the two decision-buffer fractions, while the final tuple
is constructed from the terminal locals. Use the already-profiled stock
tuple-2 representation rule recursively wherever ownership must be opened or
closed; add no generic helper summary or translator exception. Hosted AST
admission must confirm that the alias did not create a nominal ADT and that no
`*G2PointerTrace*` struct helpers were emitted. The 12 leaf types/order and
all terminal associations still require the ordinary main-body proof.

This route has no new trust assumption and no auxiliary allowlist. Its cost is
more tuple projection/product obligations and less readable terminal posts.
It keeps acceptance on checked bodies and existing tuple support, with no
special exemption for `#assume(false)` function bodies. Do not alter actual
merge source: this changes only the isolated proof adapter. It is not yet
hosted-accepted; the next run must establish tuple return handling and all
existing proof gates.

The latest hosted artifact (run 37717433930) parsed the adapter and reached
the main postcondition, then stopped at `result.1.0.0` in
`verified/lib.rs(381,12-15)`. In the pinned lexer, an integer token consumes a
following dot and digits, so adjacent numeric tuple selectors can be
tokenized as a decimal rather than successive `.field` selectors. The fixture
now parenthesizes each intermediate tuple projection, for example
`((result.1).0).0`, while retaining the same 12 paths, leaf ordering, and
postcondition equations. Parser source inspection supports this diagnosis;
the syntax correction still needs a hosted parser/proof result.

## Fallback: narrowly certified stock-generated declarations

If the tuple tree prevents the trace post from being expressed or makes the
checked proof intractable, an explicit stock-auxiliary certificate is a
bounded fallback, not a classifier-wide whitelist. The certificate must bind
all of the following together:

1. the pinned VeriFast commit and generator-source blob above, plus an exact
   hash of the unchanged generator section that emits these nine declarations;
2. the exact 12-field struct AST: generic parameter `T`, ordered field names,
   pointer/counter/bool types, one declaration at the admitted source span;
3. the exact nine qualified names, cardinality, signatures/contracts, AST
   locations, and `#assume(false)` bodies, structurally extracted from the
   hosted `proof-ast.ml` (never recognized from function-name prefixes alone);
4. a verifier-log condition that these nine helpers have no body-execution,
   return, or leak records. If any auxiliary executes, the case is
   INCONCLUSIVE/rejected pending a body proof; the certificate must not turn
   an executed `assume(false)` into a successful summary;
5. independent exact accounting for the main projection plus all 13
   hand-authored lemmas: each expected body appears exactly once, is visited
   and executed, has return and leak records, and has no error/dead-code
   finding; exporter, decoder, refinement, and unchanged-source gates all
   pass.

This fallback explicitly trusts the stock generator's inert declaration
surface for this exact struct and tool pin. It grants no lemma result, no
Send/Sync fact, no padding initialization permission, no resource conversion,
and no claim about another local struct or another generator version. The
trust ledger must call this a trusted stock auxiliary admission, not a proved
body. It has higher review and maintenance cost than the tuple route; any
generator/AST/location/name/cardinality change invalidates it.

## Fail-closed matrix

| Control | Required result |
|---|---|
| Exact 12-leaf tuple alias with no local struct helpers; main plus 13 lemmas satisfy all body gates | Admit only if AST confirms alias/product type and all main/lemma gates independently pass. Certificate fallback admits only exact auxiliary surface. |
| Change one field name, order, count, type, or generic arity | Reject certificate; tuple profile requires exact leaf order/type proof and fails at its type/association obligation. |
| Rename/add/remove/duplicate an auxiliary, move its source location, alter contract/body, or change generator blob | Reject certificate at admission. No wildcard/prefix matching. |
| One generated auxiliary has an execution record, return, or leak record | Reject/inconclusive; require proof of that exact helper body. No successful bodyless summary. |
| Add a user `#assume(false)` helper or a new auxiliary outside the nine | Reject as unlisted body/assumption; never globally allow generated-looking names. |
| Remove/duplicate any of the main body or 13 checked lemma headers, execution records, return/leak records; inject error/dead record or fail any stage/source hash | Must not classify as positive. Mutate each signal independently to test the fail-closed classifier. |
| Alter G2 body or pointer trace logic while keeping helper evidence | Reject unchanged-source/hash admission; auxiliary certificate does not admit adapter behavior. |

The hosted artifact itself is the evidence input; no local AST extractor,
runner, or verifier is used. A future extractor must parse proof AST with
explicit constructors/locations, pin the schema and source hash, reject
unknown shapes, and record the certificate beside ordinary proof results.

## Decision and next action

The nested stock-tuple adapter has been implemented in the assigned fixture;
the next step is its hosted full-trace matrix. Do not modify `pointer-prove.py`
to whitelist the nine names. Preserve the preceding run's terminal aggregate
error as historical evidence; the tuple representation is intended to remove
the actual-return-address mismatch rather than assume address identity. If
tuple encoding blocks checked ownership/postconditions, review and enable the
separate certificate fallback only after exact AST matcher and trust-entry
review. Either route still leaves actual bidirectional proof and full source
caller bridge as separate obligations.
