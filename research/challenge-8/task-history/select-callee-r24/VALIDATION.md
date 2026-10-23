# R24 validation notes

T0 is 2026-10-23T10:48:18Z, derived from the first session metadata timestamp
10:48:18.874Z rounded down; preparation is included. Formal main/absolute
limits are 2026-10-26T10:48:18Z / 11:48:18Z. This is a fresh R24 account,
21600 seconds, no R23 carry or proof credit.

## Before first Build

- Worker candidate 538431e3d6463d177a693393dc20b36c1b29a314 adds exact R24
  admission only. Worker reports 9 isolated synthetic registration tests and
  py_compile passing; preparation bundle check passed. The draft ledger/profile
  remain PREPARED_NOT_REGISTERED pending independent review and explicit
  branch-client admission.
- The worker also tried historical R21/R23 registration suites. Their
  installed-ledger tests expect AUTHORIZED but those historical ledgers are
  CLOSED. Preserve that failure and the closed accounts; do not reopen or
  modify history. The R24 suite checks historical synthetic R23 admission.
- Main ran the five ghost-successor synthetic/static controls, four R23
  source/row/runner pin checks, and runner shell syntax: all passed.
- Main statically applied the 27 tool patches in order to committed upstream
  files, reproducing translator 103a34 and parser 6a866a. No actual toolchain
  or source preparation was run locally. TOOL-OVERLAYS.md lists full hashes.
- The existing a4737f9f independent review packet was reconstructed exactly:
  packet397fa4c8, spec3cefdbf0. Its recorded GO_WITH_NITS remains limited to
  that unbuilt semantic candidate; this is not a new review or proof credit.
- The recipe closure between a4737f9f and R24 startup f565e3ee is unchanged:
  84 entries, 1968359 bytes. FIRST-TRANSPORT-PREFLIGHT.json records the exact
  infrastructure/proof pair and bounded encoded configuration checks.

The optional target classifier remains NO_GO/unqualified; no target map is
passed for the first Build. Seven negative diagnostics cannot establish full
matrix acceptance until a clean positive and exact current identities are
observed. Mutable P2 stays NOT_PUBLISHED, and W4 stays gated.

Independent R24 admission review returned GO_WITH_NITS on exact538431e3, with
9 synthetic tests passing. Fresh ledger was activated from explicit owner R24
authorization after that review; draft profile remains unaccepted/inactive.
Actual branch-client request and first Build are still pending at this entry.

Exact R24 branch-client request succeeded, followed by first Build
`af904556-010f-4159-9e4d-573e06e43d17`, infra538431e3/proofa4737f9f,
timeout1200, reserved1260. Remote HEAD ca6cb6b19aa8ee9cf0ea4c0048e4578efe7a3d78
was verified before submit. Source payload SHA matched the static preflight.
Initial client status is WORKING; no verification evidence or acceptance yet.

First handoff view generation refused CURRENT-TASK output over6144 bytes.
Shortened only the checkpoint next-step prose, preserving all pins, gates and
assignment text; regenerated views before watcher arm.
