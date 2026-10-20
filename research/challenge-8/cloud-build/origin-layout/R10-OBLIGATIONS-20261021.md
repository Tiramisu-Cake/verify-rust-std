# R10 final coverage / obligations — CLOSED_PARTIAL

| Obligation | Final scope / evidence |
| --- | --- |
| Actual normal backedge inventory | Build1:37/37 heap,41/41 env observed; current physical resources/values, not AST/parser-input binding |
| Native body/cycle source observation | Build5 insert_tail Runtime(PostCleanup), fingerprint e1f455a3ed9fb435, head97<-151/source275; reconstructed discovery, not execution proof |
| Initial invariant consumption | Build5 label path consumes invariant and passes observed leakcheck then produces body; limited observation only, complete entry routing OPEN |
| Continue/backedge preservation | OPEN; next refusal StorageDead276:44-45 before copy/body. No complete gate closed |
| Break/late-false/unwind CURRENT posts | OPEN in current profile. Historical R9 single cleanup result stays separate |
| Original tmp readonly return | Source hook retained; current same-Build complete theorem not re-established |
| Recovery5 negatives | Source repairs reviewed/service PASS; final Build5 all5 NOT_RUN prerequisite as reported |
| Allocation freshness8 | Build5 source2positive/6intendednegative, all8 current receipt identities claimed; physical per-case full audit/qualification OPEN |
| Prefix/caller | OPEN; erased coercion subtype and missing array/slice FBC, R10-PREFIX-BRIDGE-NOTE |
| Physical BeforeLive | OPEN; missing future live address cannot be substituted by lexical/unbound refusal, R10-BEFORELIVE-NOTE |
| Compatible complete matrix / generic T / arbitrary n | OPEN; no cross-Build PASS aggregation |
| Full target proof gates / B2 / accepted / independent credit | 0 / OPEN / false /0 |

Source/runtime annotations, diagnostics, exact lateNoop recognition, recovery
classifiers and run-bound freshness receipts are implementation/setup work.
They are not additional closed proof obligations. Compilation5PASS is separate
from actual bodyFAIL/sourceINC and the limited initial-path observation.
Reader coverage/identities: R10-BUILD1..5-RESULT and separate freshness records.
Next exact investigation: R10-LABEL-STORAGE-NOTE-20261021.md; retain real Live/Dead,
leakchecks, default-off and normal/unwind resources. No model fix inferred.
