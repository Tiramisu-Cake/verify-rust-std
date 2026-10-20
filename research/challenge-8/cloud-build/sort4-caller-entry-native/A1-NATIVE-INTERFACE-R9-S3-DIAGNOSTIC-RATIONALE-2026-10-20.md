# R9 S3 rationale — diagnose duplicate compiler-bound function candidates

## Defect and applicability

The S2 Build `62675952-19c6-483b-8770-28992e68b640` again reported the same R-only diagnostic, at the same source range and with the same source error SHA as S1: `A1 small_sort implementation signature compiler item body is not unique`. This remains a source-reported translation failure, not a verifier result. S2's `body=Some _` filter removed prototypes but did not make the compiler-name candidate unique.

The pinned translator SOURCE scratch is SHA `9391bff0376ad008798a950d76dbaac095cacbe8fd5acf5b2ea4d336a759f33f`. The pinned exporter source (`f76012fb518703b1d98e243ac4f487f16877cfcb`) records trait implementation item paths as `def_path_str` strings and independently collects implementation function bodies. The translator forms `traits_and_body_decls` from all translated trait declarations and body declarations. The checked Rust source has two `StableSmallSortTypeImpl::small_sort` implementation bodies (the generic fallback and the `FreezeMarker` specialization). This source structure makes duplicate candidates plausible, but without the actual serialized candidate identities and spans it does not prove which pair caused the observed match or which one corresponds to the current trait-impl item. The available string identity is therefore insufficient evidence for a selector; no source candidate is dropped or preferred.

## Narrow diagnostic and preserved behavior

Keep the S2 exact translated compiler item-name comparison and `body=Some _` requirement unchanged. Construct diagnostics only on the missing-definition or multiple-definition error path. Count every exact-name `Ast.Func`, but format at most four candidate rows; cap each escaped name and file field at 160 input bytes, and include source line/column and `Some`/`None` body presence. Do not weaken uniqueness, infer the active specialization, change required/native signatures or posts, alter applicability, or change the C patch or proof semantics. The next S3 source report can identify the collision and support a later exact-identity/interface-gated fix if justified.

## Controls

Apply the patch only to a disposable copy of the pinned SOURCE scratch. Verify the patch applies, diagnostic formatting occurs only on missing/multiple-candidate failures, the output is bounded to four rows and capped fields, and the manifest records exact R and unchanged-C source hashes. Run the existing source-map static tests and patch/hash checks. No compiler, preparation, extraction, runner, verifier, or Cloud control is run locally.

## Static patch outputs

The bounded diagnostic patch applies to the exact `9391bff0376ad008798a950d76dbaac095cacbe8fd5acf5b2ea4d336a759f33f` translator scratch and yields R candidate SHA `ff9c4f7217bbca25975bb94a08df1ee705d506a248a06ad2da504adb25ff4889`; applying the unchanged C patch yields `dad5857cdc204cbd93e9311c0cea91b1016485194324dbe000c3f3bdd59f0848`. These are source/patch application pins only and do not establish translation or proof success.
