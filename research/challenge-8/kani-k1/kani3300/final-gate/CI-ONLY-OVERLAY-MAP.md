# CI-only overlays — frozen C1 / NOT_RUN

Gate A: `/root/kani-fix-3300-fullgate-c1-w15`,
`ci/kani3300-fullgate-c1-w15`; exact commit in CI-OVERLAY.json.
Gate B: separate C1 clone and commit in REPLAY-CI-OVERLAY.json.
Both direct-parent overlays target `1658f4cadfa83139e41180ce3865e23f79d889aa`;
all non-overlay tracked blobs remain identical to C1. Exact patches are retained.

Only new files `.github/workflows/kani3300-fullgate.yml` and
`scripts/kani3300-gate/{receipt.py,test_receipt.py,binding.json}` are added.
All 16 stock workflows are removed **in the overlay only**, to avoid automated
push jobs; its single workflow has workflow_dispatch only and a fork guard.
No source/compiler/runtime/tests or stock regression script changes.

The overlay is the control checkout. A second checkout uses frozen C1 SHA
directly, runs exact C1's own dependency setup, and remains free of overlay files.
Observer/artifacts stay outside that export. No added workflows or research
receipts enter the final tool source; ordinary upstream tracked workflows remain
in C1. `git status --porcelain --untracked-files=all` must be clean before/after
the script. Build outputs stay ignored; no cleanup/reset hides source changes.

Binding is C1_FROZEN with exact SHA/tree, owner-accepted M3 lineage,
and required compiler/library/tests/script subtree and file hashes. The frozen
composition manifest is included, with its R3/R4 inventory binding and T1b/
producer-order limits. Runtime binary/model hashes remain CI outputs.

The observer's BASH_ENV hook is restricted to the top-level original regression
script. DEBUG events record command/source/suite/mode; the next top-level event
or EXIT supplies the preceding command's exit. Event and child output use the
same stream, preserving ordering. Child shells are not instrumented. Counts
are bounded to 20 summary lines per stage; missing/extra/repeated stages,
nonzero/unknown exits, missing counts, failure counts or truncation reject
completeness. The parser cap is 256MiB; over-cap artifacts remain incomplete.
It does not rewrite failures, expected property inventories or regression lists.

Python synthetic tests cover success, original failure exit, missing/partial/
null/wrong-type data, timeout/signal, wrong-source attribution, repeated stages,
missing/failed counts and complete order. Shell trap behavior/setup/runtime
hash inventory is unexecuted until authorized CI. Coordinator must qualify the
observer there; `COMPLETE_EXIT_ZERO_REQUIRES_REVIEW` is reporting, not proof credit.

SmallSort test-only overlay, if feasible, is separately recorded in
`REPLAY-OVERLAY.json`/`replay-test-only.patch`; no production helper is changed.
It is not applied to C1 export, and cannot modify worker14-owned tests.
