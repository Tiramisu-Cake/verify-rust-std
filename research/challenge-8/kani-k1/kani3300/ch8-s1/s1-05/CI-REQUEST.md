# S1-05 — preparation only

Control candidate `8860d38558651f7cf2e292d57b06b378c6ad3b94`, single parent
`40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`, local branch
`uninit-ci/ch8-s1-05-prep-w13`, worktree `/root/kani-ch8-s1-05-w13`.
Std `5be85699b8826e3286c0bf89efb9affefac0acb5`; stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`. No source/tool patch.
JSON request exactly mirrors the committed control request.

Same 35 selected roots, four fixed-N unions, 14 groups, unwind/timeout/checks,
patches, source geometry and flags as executed S1-04 control205b0e98c7.
Schedule remains light-model → light-corruption → light-controls → activation
(default/override) → Cell → eight heavy pairs; stage dependencies and
max-parallel1/fail-fastfalse unchanged. This is14 jobs in one prospective workflow.

Changes: stock regular output, streaming rich inventory with same-invocation
JSON reconciliation; record-only runner; macro declaration29 plus invocation
anchors66/67/68; prospective F7/F8 exact oracles from w11 ACCEPT.json, sole allowed
failure and same-pin unmutated companions requiring SATISFIED post-return covers.
F1–F6 oracles unchanged. Mutant return covers may be UNREACHABLE and give no
positive credit. Classification is offline under ACCEPTANCE-POLICY-BATCH/w11.

Each job uploads exactly one `group-evidence.json.gz`: original JSON bytes with
sizes/hashes, rich properties and bounded receipts/diagnostics. No raw stdout
file is uploaded. Caps:8,388,608 compressed and33,554,432 uncompressed bytes/job;
14-file compressed reservation117,440,512 bytes. Actual future lengths UNKNOWN;
ARTIFACT-SIZE.json distinguishes measured S1-04 projection from planning assumptions.

S1-04 grouped driver wall2082.381s, plus repeated setup/upload/queue. New regular
rendering/packing overhead is unmeasured; conservative inherited complete serial
envelope71,540s (19h52m20s), excluding queue. Each job remains capped180min;
this is not a180min workflow allocation. No budget/window/reservation is opened.

Preflight retains attempt1, exact single-parent graph/changed paths/payload
hashes, native typed YAML and control fetch-depth3 (std/tool2). Local validation
uses synthetic GitHub environment only. Future publication/dispatch requires
separate authorization and existing coordinator controls. All proof NOT_RUN,
qualified acceptance PENDING, proof credit NONE.
