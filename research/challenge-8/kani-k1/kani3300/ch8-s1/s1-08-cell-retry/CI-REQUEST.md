# S1-08 cell-only retry1200 — preparation

Status: READY_FOR_W14_REVIEW. Review pending; dispatch NOT_RUN, reservation NOT_RESERVED.
Task49f2363e09; baseline reviewed7c41333f9b/source99e8456d20/stock tool0aac16ef62.
Control candidate: `da8c766f957c576eafa44bccfba2c45490cef6d1`, sibling over9208; exact trees and hashes in IDENTITIES.json/PAYLOADS.json.

Executed scope, if separately authorized: one job/run, only `cell-u34`, exactly the
previous stable_default_cell + unstable_default_cell selectors, production/PFC,
Cell<u8>, symbolic N0..3, unwind34. Default invocation without --groups selects
only that pair; any other group or extra/missing/wrong selector is rejected.
Full35-row/14-group manifest and ROLE-MAP remain reference inventory. Other33
roots keep600s and cannot execute. No source publication or source change.

The only proof runtime delta is per-root600→1200s. Actual argv, compile marker,
export parser and row receipts agree. Compile900, RSS12GiB/headroom2GiB unchanged.
Group child900+2×1200=3300s; cleanup10 gives3310s. Phase8100 leaves4790s after
that envelope. Absolute setup1800 + phase8100 + fallback/upload reserve900 =
job10800s/180min. Existing caps suffice; phase/job are unchanged. Setup step
caps overlap the absolute setup budget; build wrapper keeps its remaining-time
check. `budgets.row_seconds=600` is the retained reference default;
`cell_row_seconds=1200` is the exact selected limit. See ENVELOPE.json.

No auto-rerun: existing run44095954742 is untouched. Coordinator may decide retry
only after that run is terminal and its intake is complete, then issue separate GO.
Item2 stays8/14 now; planned9/14 is conditional on a newly authorized accepted run.
Old incomplete cell group is not accepted. W14 review is not GO.

Even two successful1200s observations establish neither fit600s nor the ordinary
organizer cost budget, nor label causality. Keep new run/profile provenance;
results from two runs cannot be represented as same-run evidence. Future
composition/admission belongs to the coordinator under separate explicit rules.
No independent proof credit or acceptance is granted by this packet.
