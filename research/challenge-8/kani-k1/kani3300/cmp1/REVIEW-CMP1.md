# CMP1 independent production review — static only

Reviewer: GPT-6 Luna HIGH, `semantic_review`, independent context, no nested delegation or builds.
Initial packet: candidate `03f9a43a4001605b5367fa62a6ff910e389c003b`, spec `ee587de5dae4e26c23a4b15aa06785ad3de1beca968219a99c136a7995afad7a`, packet `325cef9342b0bb898d93921c8839c334d8e4185f9802f0c2c33fd8d2a37c855b`.
Final reviewed semantic candidate: `bb767b96ed5d39c57c5a790c4098d0367c7400ed`, tree `8efbe6822044d7964c7bcddf25b99719c0930334`, baseline `81dd85bfce67226e283fdd9a156932e32ece080b`.
Final spec `525c089ef9402973e79981b0a70697c446219c99165f8f6794a5366f87d0ae0c`; packet `9dce317bfb543084e7716cfc1aa8fffef0f949879900c367c2308a95a082d802`.

Reviewer findings and disposition:

- A type-kind temporary borrowed through let-else could expire before field traversal. Fixed by binding `ty_kind` locally; reviewer accepted the localized fix.
- Newly supported whole-product `Use` assignment accepted a destination containing `Deref` without establishing the final address operand's shadow initialization. No reachable source-level counterexample was independently established. The candidate conservatively rejects every indirect whole-product assignment before transfer; a dedicated initialized-pointer Unsupported control exercises this boundary. Reviewer confirmed the identified blocker removed.
- An alleged ordinary-R aggregate counterexample was explicitly retracted as unestablished: examined typed MU reads/transmutes and raw deinitializing writes retained source/delayed checks. A separate negative fixture now poisons an ordinary `Pad` operand via raw padding copy before product aggregation. Its native result is NOT_RUN.

Witness assessment: reviewer found no multiple-argument witness counterexample. For a chosen live byte, select its argument in Store, avoid later Store overrides, and follow it in the matching Load. Mismatching loads bless only distinct callee allocations; return index0 is captured separately. Whole-product transfer uses the complete product size; generic product SetRef preserves R/S and clears only exact P intervals.

Final reviewer statement: “The prior static review applies to this exact candidate. Its indirect-destination guard rejects any whole-product assignment containing `Deref` before shadow mutation; I found no remaining identified production blockers.”

The final full candidate `6ef9fd72066443f7f113440ba32f77f310520a93` differs only in tests. `REVIEW-CARRYFORWARD.json` checks all production blobs equal the reviewed candidate; no control was removed from the full candidate. The test delta isolates layout diagnostics from bodyless black_box arguments and adds ordinary aggregate-source and initialized-slot reset controls.
No native/compile result, formal proof credit, accepted U3B base, or dispatch authorization follows from this review. U3B subsequently source-reported two PFC/uninit OOM outcomes; that is an admission boundary, not a changed production dependency.
