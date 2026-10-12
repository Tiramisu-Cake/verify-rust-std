# Internal I actual-glue prerequisites package

**NOT_QUALIFIED.** Narrow additive candidate, independent design/final review,
exact pinned Cloud build failures and complete NOT_RUN matrix; no adoption.

* [Semantic card](SEMANTIC-CARD.md), [design](DESIGN.md), [compiler source pins](COMPILER-SEMANTICS.json).
* [Independent design review](REVIEW-DESIGN.md), [tool review](TOOL-REVIEW.md), [runner review](RUNNER-REVIEW.md), [final review](FINAL-REVIEW.md).
* [Executed/NOT_RUN matrix](GATE-RESULTS.md), [results and durable evidence](RESULTS.json), [pins](PINS.json), [commands](COMMANDS.md).
* [Cloud manifest](../../cloud-build/verifast-i-glue-prereqs/manifest.json), [ledger](../../cloud-build/verifast-i-glue-prereqs/BUDGET.json), [fixtures and intended gates](../../cloud-build/verifast-i-glue-prereqs/C2-GATE-MATRIX.md).
* tool.bundle requires baseline I; additive/full-base compressed patches and exact source pairs are in the lane directory.

Historical PASS evidence and upstream candidates preserved at their old pins.
C3 deferred; B1/B2/O23 remain open. Merge agent's v8/actual cleanup untouched.
Publication is on own internal research branch, with no merge or upstream PR.

proof.bundle preserves the own prepared lane and execution commits, requiring the exact start. compiler-reference.tar.gz preserves the pinned compiler excerpts; package inventory binds both. Raw logs remain at verified durable GCS prefixes. An optional static-copy GCS upload was denied storage.objects.create; the source-reference copy is instead published with this internal Git package.
