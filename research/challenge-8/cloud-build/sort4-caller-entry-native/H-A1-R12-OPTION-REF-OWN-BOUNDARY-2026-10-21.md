# R12 Option reference-own boundary

## Observed S1 body result

S1 (`7bb78480-bd16-4d5a-85e2-82875fbad808`, candidate
`f274662fc8f45ae1455bac141c8236f322ca2269`) reached helper-body verification
and failed the leak check at `verified/lib.rs:12`. The exact BriefReader
positive-log record is file ID
`121a0129468674486eec98d3585083accd2bc4a732512857ab5cfc3406e9beec`,
SHA-256 `7f7ddeb7c4d908be0c7ebc410e30118f0b8d5f8f783f259b77beb5608c2a25b6`;
the bounded exact line response covers 1131–1142 (including diagnostic at
1135). It reports:

```text
Function leaks heap chunks: own(ref_typeid('a_typeid, T_typeid))(t, 0)
```

The dumped positive AST SHA-256 is (the S1 selector was not invoked after nonzero exit)
`1b567368fb4fe4c5cf47047418a8041f93ed0a3f8cc4a751701c3ef0df8686a5`.
The proof-audit record is file ID
`cc20cf422e3f3828330adb99a0a55222711961bbb855f3b12dfc360c537a3e96`,
SHA-256 `44117bd70d83c4438fb62b0e1134d2952f8c11b2058d3e9c3da77f248a40458f`.
Reader coverage was selected exact fields; the positive parent variant had
22 children and only its first 20 were read. This note relies on the exact
S1 evidence record and bounded Brief responses, not on a claim that the whole
proof-audit object was read. S1 closed no formal target gate or B1/B2 credit;
all 26 canonical rows were `NOT_RUN`.

## Static source boundary

The effective R11 parser is pinned by profile
`A1-CHECKED-CALLER-R11-PROFILE-2026-10-21.json`, SHA-256
`46047334a985ccc0f5b6833ca0ab4a67347e9b7782c7a489ffe6bb0e4aa8ce13`,
at tool commit `f76012fb518703b1d98e243ac4f487f16877cfcb`. The relevant
pinned-source chain is:

1. `src/rust_frontend/vf_mir_translator/rust_parser.ml`, blob
   `e27eee316f6ba809ca6fe2111e42f217745e45bf`, SHA-256
   `b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622`,
   lines 995–1017: generated enum ownership matches the constructor and emits
   a field `TypePredExpr(field_type, "own")` for each field. For
   `Option::Some(r)` that is `<&'a T>.own(t, r)`.
2. `src/verifast1.ml`, blob `e0bff63df9c0788ed89615efd784ff29e9136897`,
   SHA-256 `b1b0ae618bbce1a0bce9714ce10a47dbeb855e919b980b7ce6a70108ff9b91d7`,
   lines 5375–5408: a matching explicit type-predicate definition is selected;
   otherwise the evaluator node remains `WTypePredExpr`. Lines 8869–8871
   evaluate that node as the predicate symbol applied to the type ID. Lines
   599–604 and 6413–6416 construct shared-reference IDs as the uninterpreted
   `ref_typeid(lifetime_typeid, pointee_typeid)` term. Lines 7686–7711 install
   equalities only for explicit type-predicate definitions.
3. `bin/rust/rust_belt/general.rsspec`, blob
   `6c60c0e942b441901741889309858185a5572ebe`, SHA-256
   `ef2ff16dffd472bbc5fd7fa17e7f13a03d83919520da5ce7e2d7095194790d1d`,
   lines 145–153 and 190–196: the generic own predicate is declared, raw
   pointers have an explicit mapping, and `close_ref_own` has the direction
   shared-reference share → opaque reference-own. No shared-reference own
   mapping or reverse opening lemma appears in this pinned spec.
4. `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`, blob
   `4e237a61a7e4449735e53220114e57114b51e31a`, SHA-256
   `c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445`,
   lines 1541–1568 and 1623–1624: the RustBelt type interpreter separately
   gives a translated shared reference an `own` callback equal to
   `ptee_shr`. The inspected source does not connect this callback to the
   generic ghost `WTypePredExpr` emitted for an enum field.
5. `src/verify_expr.ml`, blob `b26182a08f6c4639e6e2520af18e1958d099fad7`,
   SHA-256 `f2a2a32c990219392cff3b1dbc13992567cf9cdc37d29ae3214e4353d81f8150`,
   lines 179–192: leak checking removes dummy-coefficient chunks and empty
   chunks, then rejects remaining chunks. The observed full-own chunk is not
   shown to be a dummy share.

Thus the observed resource has a source-level explanation: opening generic
`Option_own` exposes a shared-reference type-predicate symbol applied to
`ref_typeid`, and the checked body has no existing rule to consume it. The
existing `close_ref_own` lemma builds that opaque resource from a share; it
does not convert it back. This is a static irreducibility result for the
current representation, not a claim about Rust runtime leakage and not an
additional verifier run.

## Representation decision and next path

No axiom, assumed bridge, leak/forget, weakened postcondition, or runtime
standard-library change is authorized by this boundary. A future frontend
refinement could investigate normalizing generic enum field ownership through
the existing RustBelt type interpretation. It would need a separate
soundness argument that establishes representation preservation for generic
fields and shared-reference instantiations, plus discriminating controls for
both variants, arbitrary `None`/`Some`, required posts, and non-reference
fields. A source-preserving refinement established within the existing model remains
within Select’s authorized implementation scope. Introducing the missing equality
as an unproved bridge would require a separate trust decision and is prohibited
here; no such bridge is implemented. This is not a handoff of the current proof
blocker to the maintainer.

The independent canonical path remains available after the syntax preflight:
P0a/P0b may produce their own threshold/conformance observations, with the
exact canonical source pair and all existing checks preserved. The preflight
result and AST cannot satisfy a helper proof or caller receipt. Each canonical
caller pair still requires its own fresh same-Build checked-helper stage;
P0c then needs its own exact-pair receipt, and native P1 retains its helper
stage. The full 26-row admission remains a single same-Build run after these
prerequisites pass. Until a real helper body passes, helper-dependent caller
results remain blocked or not run, with no proof credit.
