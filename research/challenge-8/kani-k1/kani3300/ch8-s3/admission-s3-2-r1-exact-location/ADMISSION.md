# S3-2-r1: exact metadata admission and one bounded case

Coordinator + planner decision, 2026-11-19 05:54 request; independent review
`028531727fc48ef9f26f16dfb95c2b2666c96dd7` is APPROVE_INTAKE_WITH_PRESERVED_LIMITS,
zero blockers, RECOMMEND_EXACT_CASES. Intake `5d9439a7641c929838bf075c6aa6533a353ee92d`
remains immutable. This note changes admission only, without a native run or a
runtime/parser/policy patch.

Admit only the single system SUCCESS location record in each exact packet for
`m8_s32_d00_allinit`, `m8_s32_d00_partial_diag`, `m8_s40_d16_partial_diag` in
run44439462279/attempt1. Each full ID ends `.unreachable.1`, classunreachable,
statusSUCCESS, description`unreachable code`, file/line keys present-null and raw
lib.rs:0:0 in the exact harness. The full IDs, invocation/namespace, all source/
tool/control/head/request/workflow/schema/parser/member fingerprints, counts and
cardinality1 are mandatory in ADMISSION.json. All386 properties/380checks/
372SUCCESS/8separately assessed U/6SAT covers and all other positive locations
remain bound. These are SUCCESS checks, distinct from statusUNREACHABLE U.

**One case is QUALIFIED_BOUNDED_SOURCE_REPORTED: m8_s32_d00_allinit.** It executes
the actual bidirectional_merge<u8,KeyLess<u8>> body at source[32,40), destination
[0,8), backing[MaybeUninit<u8>;48], sorted source halves4+4 and full u8 values.
Initially known values occupy[8,48); destination is in the constructed uninitialized
complement. Five located SUCCESS roles, six SAT covers, eight source-local U
arguments, four visible SUCCESS unsupported guards and the exact PFC context are
retained at S1/Profilesv4 source-reported assurance. This is a bounded functional/
known-value-frame case for one original geometry pair, not a universal contract,
independent byte-state initialization theorem or provider summary.

**Both partial rows remain DIAGNOSTIC_ONLY_INITIALIZATION_OPEN.** Metadata admission
allows their exact observations to be described; it grants no qualified init leaf,
provider or summary. Actual mask/dstinit/store tracking remains OPEN. All34 sort8
init/caller contexts, generic/caller/type lifting and fullN16/N32 goals stay OPEN.
The two insertion roots remain RSS-censored UNKNOWN. Three fixed negative labels
are reviewed observations; this note makes no additional qualification decision
for those controls. Independent AST/MIR/B1/B2/init credit is NONE.

**General location rule remains PENDING.** Actual shared emitter/lowering cause and
positive source/MIR origin remain UNKNOWN. No lib.rs:0:0/suffix/class wildcard is
admitted. Oldf740 remains limited to its original run. Revoke these exact decisions
by append-only note if any fingerprint, identity, count, status or source-local
premise fails. All U/guard/role/cover/safety/partial-evidence gates remain strict.

Original workflowFAILURE, producer3OBSERVED/5UNKNOWN, strict0/8, U REJECT_ALL/
proposalDISABLED and null fields are unchanged; there is no evidence rewrite.
**Accounting unchanged: item1 31/31, item2 13/17, total44/48.** No charge, refund,
reservation, capacity grant, CI or publication is authorized. S3-3 remains PLANONLY
until a separate implementation/review/GO decision.
