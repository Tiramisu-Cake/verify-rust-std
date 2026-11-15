# W11 opt-in control oracles

Machine-readable selectors, exact assertion messages/covers, unwind values and
companions: CONTROL-MAP.json (12 roots:6 positive,6 intentional negatives).
Root namespace is prospective until compiler list confirms it; W13 must reconcile
exact --harness/--exact selection and actual inventory/property IDs. No invented
IDs or numeric property counts, no substring-only SUCCESS oracle.

All roots require cfg(all(kani,kani_smallsort_sorting,kani_smallsort_controls)).
Model module needs only kani+sorting. W13 registers both; no failing roots enter
ordinary inventory. The six actual PFC roots and two actual ensures-attachment
variants are worker13's separate rows, in the SAME bounded combined S1 batch.
There is no worker11-only dispatch/budget; all outcomes and timing are NOT_RUN.

The three model positives each select arbitrary initialized bytes and symbolic
len0..3, check active=true, identity iff already ordered, constructed sorted output
with the same multiset, both actual FnMut and FnOnce two-projection calls, layout,
ZST/no Drop and useful N/duplicate/unsorted covers. The constructor is a tiny
independent insertion fixture, not an actual std-sort proof or a trusted summary.

Inactive positive: descending closure, effectful captured closure (must not be
invoked), and unsupported MaybeUninit<u8>/KeyLess<MaybeUninit<u8>>. Valid references
to MaybeUninit wrappers are legal; payloads are never read. This is a source
read-free-path check and a future default-check CI control, not uninit-ON proof.
Three activation negatives demand enabled=true for exactly these unsupported
pairs; their named failure means model rejection, not sorting under arbitrary F.

Order fixture snapshots [a,b] with arbitrary bytes a<b and checks [b,a], whose
counts are unchanged. Only order is false. Count fixture checks [a,a], asserts it
is ordered, and intentionally demands post=true; only counts are false. Companion
uses the same snapshot/checker to accept [a,b] and reject both corruptions. The
strict-pair assumption is satisfiable (e.g.0,1); companion return cover required.

Invalid negative obtains an invalid token from safe inactive snapshot and demands
active post on empty output, so validity is the only false condition. Guard
companion rejects it, accepts fixed CAP32 identity, rejects changed length and
CAP33 input/output, and checks that later Cell mutation cannot alter pre-state.

Accept only source/tool/mode/cfg-bound complete inventories: positives have zero
unexpected failures and every listed cover reachable; negatives have their named
assertion failure, no unrelated safety/unwinding/frontend/setup failure. Preserve
all failed properties and original exits, even if CI infrastructure itself exits
successfully for an expected failure. Missing/unsupported/timeout => UNKNOWN,
never detected/accepted. Actual property IDs/counts follow CI receipts.

Cost binding: no timing data exists.600s/invocation is the shared hard cap, not an
estimate; root total worst-case exceeds the common75min phase when combined.
W13/coordinator must budget/order the fixed batch with a whole-phase watchdog;
remaining rows at cap are NOT_RUN/UNKNOWN, not silently skipped. This manifest
does not authorize additional jobs, dispatch, retries, tool changes or Cloud use.
