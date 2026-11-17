# S1-08 cell-only retry1200 r1 — fallback controls repair

READY_FOR_W14_REVIEW. Finding W14-CELL-RETRY-01: fix prepared, closure pending W14.
Task193b377c5cc092f1032741dbb854b0d1f77505d6; exact reviewec48e6d59b552da2a9aa8d985478bf259c950073.
New control `e27ec119eeac798d43d6bc056a449fa7576a5e94`, sibling over9208.
Old package9f4c37c894e7fecee0f59321ba66b65309a87606/control da8c766f957c576eafa44bccfba2c45490cef6d1 immutable.

Only tests and their two payload hashes change relative to da8. The two former
fallback controls are adapted to the exact cell pair and executed through the
existing test_cell_retry workflow preflight. The added in-memory overwrite
mutation is rejected by both controls at original_exit null versus42, below
payload hash gates. Runtime/fallback/workflow/decoder/native capture/source/tool
are byte-identical to da8. All timing/resource/proof settings are unchanged.
Exact patches/maps/hashes are in PATCHES.json, REPAIR-DIFF.json, SEMANTIC-DIFF.json
and PAYLOADS.json; test and mutation receipts in TEST-RESULT.json/MUTATION.json.

Scope remains one job/run, only cell-u34 with the two previous stable_default_cell
and unstable_default_cell selectors: production/PFC/Cell<u8>/symbolicN0..3/unwind34.
Other33 roots are reference-only and cannot execute, even with omitted --groups.
Two roots1200s, compile900s =>3300s child +10s cleanup; unchanged phase8100s,
setup1800s, job180min/10800s, fallback/upload reserve900s, RSS12GiB/headroom2GiB.
No source change or republish. Missing RESULTS/TIMEOUT remain UNKNOWN.

Dispatch NOT_RUN, reservation NOT_RESERVED, item2 charge8/14 unchanged.
Future9/14 is not authorized. No CI/rerun/cancel/push/ledger/publication.
Intake11 proceeds independently and was neither waited for nor changed.
Reviewer14 decides CLOSED/APPROVE; review is not GO. Only the coordinator may
consider retry after terminal S1-08 and committed intake.

Two1200s proofs do not establish fit600s, ordinary organizer cost qualification
or label causality. Preserve run/profile origin; two runs cannot be same-run
evidence. Composition/admission is a separate explicit coordinator decision.
