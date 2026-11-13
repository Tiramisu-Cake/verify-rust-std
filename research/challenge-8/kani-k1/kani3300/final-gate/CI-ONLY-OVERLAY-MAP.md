# CI-only overlay map — preparation

Own clone `/root/kani-fix-3300-gate-w15`, branch
`ci/kani3300-fullgate-w15-prep`, based on exact C0. C0 remains read-only.
`CI-OVERLAY.json` and `ci-only-overlay.patch` bind the local preparation commit.
It must be rebased/recreated on accepted C1 and reviewed before coordinator
publication. A C0 overlay SHA is not a final export SHA.

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

Binding template is deliberately disabled: state NOT_RUN_C1_PENDING, null
SHA/tree, m3_accepted=false. Pre-setup guard rejects it. Future coordinator must
record C1_FROZEN, accepted M3, exact 40-character SHA/tree and all required source
hashes from EXPORT-MANIFEST plus final compiler/library/tests subtree hashes.
Workflow and observer must use the same binding; no latest/main alias.

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
