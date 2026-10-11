# Compiler-selected Drop receiver ledger (candidate)

Owner merge; policy c7ca8c467aecf10a4b53039372ee97714f854ee3. Domain concrete-u64/x86_64, len==1. Experimental profile `experimental-merge-selected-drop-receiver-v1`, SHA256 `7ac3e5e425899e100138b392ec552dab817c4da722067a588c86659dbc3a7fef`; NOT_ACCEPTED / NOT_FOR_INTEGRATION. Candidate tool73ef2980515203c480a324177ce5268fc40ac66f, basef76012fb plus preserved ten patches and selected-drop.patch. Kernel/model/verify_expr/parser/prelude/stdlib hashes unchanged from0b8cf55b.

The physical guard address g and created mutable receiver r are different symbolic pointers. No numerical address equation grants permissions; neither `ref_origin(g)==g` nor `ref_origin(r)==r` is asserted or supplied.

| Consumer / step | Required resources | Actual producer / returned resources |
| --- | --- | --- |
| Canonical generated trait prototype | thread/currentThread, full CopyOnDrop FBC(t,self), origin fixedpoint; guard type has no own lifetime parameters | Independent body safety_proof starts with this canonical contract; it does not prove caller applicability |
| Checked implementation strong contract | full three receiver fields/padding; source quarter singleton, destination full gap, CURRENT owner/type_interp, len==1 and copy geometry | Existing full caller entry follows actual tail.read/constructor and readonly half-FBC recombination; no receiver premises added |
| close_points_to(g) | full fields/padding at physical live guard | Existing structural rule packs typed guard storage *g|->v; external payload remains separate |
| create_ref_mut(g) | *g|->v | Existing unchanged aliasing spec returns *r|->v and exact linear ref_mut_end_token(r,g); no origin fixedpoint guarantee |
| open_points_to(r), selected actual method call | receiver typed storage; strong method contract | Same-unit checked actual Drop body bound to compiler-selected DefPathHash and qualified guard. Existing function map uses implementation pre/post and separately checks canonical prototype compatibility |
| Normal method return | returned full receiver fields/padding plus conserved source quarter and CURRENT destination/owner | Actual dynamic self.len copy verified against strong contract; len one is derived from caller constructor |
| close_points_to(r), end_ref_mut(r), open_points_to(g) | exact end token and full returned receiver typed storage | Existing end_ref_mut restores physical guard storage with returned value; open exposes physical frame for StorageDead/free checks |
| Normal recovery | source quarter + copied destination and owner, retained readonly end/lifetime resources | Caller packages CURRENT effect, then existing readonly borrow-end/merge/lifetime-end recovers full original tail post; no runtime second destructor |

`create_ref_mut` is applicable only after packing full physical storage. `end_ref_mut` requires precisely its created token and full receiver storage. `reborrow_ref_mut` is not used: it consumes full_borrow and lifetime token, returns canonical receiver FBC, but gap-own cannot be reclosed after destination initialization while also retaining the full effect. This candidate does not construct canonical full_borrow/lifetime/end resources for r. It proves a direct checked implementation route if its Cloud gates pass, not trait-prototype applicability.

Controls withhold the full guard len field, or both source-quarter representations, inside an existing full_borrow with no reopening. This is missing usable permission at the intended bridge/call, not omission of array packaging. A simultaneous two-full-effects assertion uses one initial payload. Before/after false establish nonvacuity. MIR must contain one guard Drop and no runtime destructor call; AST must contain one selected checked method, one reference creation, and one exact reference-end per outcome. Caller return/free/leak and unchanged full posts are mandatory.

Fresh evidence: Build8ba8161e on051bd424 compiled this exact candidate and passed both mandatory smoke groups/helper4. Actual natural fixture refused preparation before proof; receiver/method/recovery controls remain NOT_RUN. First Build2a462d72 refused preparation before candidate compilation/proof; original FAILURE preserved. Compiler-generated drop_in_place glue MIR and reachable caller panic cleanup remain NOT_RUN.
