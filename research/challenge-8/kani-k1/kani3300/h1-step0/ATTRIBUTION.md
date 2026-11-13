# H1 STEP0 — attribution and handoff

2026-11-13; worker14. Local Python only; Cloud $0; verification NOT_RUN; proof credit 0.
Authority: `TASK-KANI3300-H1-STEP0.md`; R3 §2/4 at 88ca9d0294f5e6f631117aa68f56ee1e3464398d and `PLANNER-R3-H1-REVIEW.md`.
D1-A files equal 15276d57238f4a70b2ea5fca9141ef047cce120c (local Git comparison); historical files unchanged.

## Accepted scope and reproducibility

`INPUTS.json` records absolute paths, manifest/control/content SHA256 and byte counts, actual model metadata and complete capture receipts.
Only two explicit D1 roots are opened; identity and manifest hashes are checked before reading their permitted contents.
R1 actual model: `e8d4d3e82326663aa34f912b36535cd29088adaa4fc7d3c8afe403534adc28a2` (372228 bytes).
R6 actual model: `47eaccef418b63d26413c3a310804482ba00ecdacb6ec684abf1d392dff65e55` (378130 bytes).
Binary models were not read. Program-only streams: 1656636/1886396 bytes; dropped=0, truncated=false, stream_complete=true.
The two bounded actual-model function and symbol projections also have complete capture receipts; selected-JSON coverage is not substituted for these projections.
Capture completeness covers text, not GOTO/L2/converter completeness or the incomplete D1 diagnostic frontend (historical rc101).
CBMC binary SHA `a62af25d27425610608221d79c202f993efe1d5a85cece186119bec196382995`, version 6.11.0, actual argv object-bits16 + slice-formula + program-only.
Reproduce: `PYTHONDONTWRITEBYTECODE=1 python3 research/challenge-8/kani-k1/kani3300/h1-step0/analyze_offline.py`.
Tests: same directory `test_synthetic.py` (10 hand-authored tests; multiline, unknown kind, ambiguous index, duplicate prefix, missing definition, caps, wrong hash/pin, truncated receipt, key identity and distinct use kinds).
Budget: 60 CPU seconds (SIGXCPU -> INCOMPLETE, hard61), 60s wall check, 512MiB address space, 8MiB per input. No huge-expression fingerprint serialization.
On detected cap/identity error: INCOMPLETE marker and no completed JSON outputs. Analysis observed about 2s; no compiler/verifier/CI or evidence download was invoked; the requested initial git pull --ff-only was already up to date.

## Root, scope, type and definitions

Each pin independently binds the following roots by exact `owner#2..field..elems == dynamic_object$m`; matching numbers across pins are incidental.

| Write-set owner (full SSA) | contract_frees | allocated | deallocated |
|---|---|---|---|
| `__requires_write_set!0@1#2` | `$0` | `$2` | `$3` |
| `__ensures_write_set!0@1#2` | `$5` | `$7` | `$8` |
| `__contract_write_set!0@1#2` | `$10` | `$12` | `$13` |

`$m` abbreviates `dynamic_object$m` only in this table. Other dynamic objects (assigns ranges/append lists) are not promoted into DFCC indexed tables.
All nine roots per pin: explicit object_bits=16, nof_objects=65536, element pointer type, allocate(nof_objects*8), hence extent524288 bytes/capacity4194304 bits (TYPE_DERIVED).
Architecture symbol values confirm pointer_width64/char_width8: R1 value lines9988/9888, R6 lines10358/10258; coordinates are saved per table.
Actual converter operand allocation/flattened width remains UNKNOWN: source rules about flattening are not a measurement of this D1 run.
`TABLES.json` retains creation invocation (`object_bits!0@N#2`), full source/function/PC/byte coordinates, owner aliases, malloc aliases, SHARED_WRITE events and every table SSA definition.
SHARED_WRITE is a separate equation event, not an initialized definition. Printed SSA versions are scoped by exact model hash, not transferable across pins.
Roots other than $12 have only sliced #1=ARRAY_OF(NULL), with zero visible indexed reads. This is NEGATIVE_PROXY_RESULT/UNKNOWN_GOTO_COVERAGE for those tables, not absence of converter reads.
$12 has #1=ARRAY_OF(NULL), #2=ARRAY_OF(NULL) WITH address update, and #3..#17 chained WITH updates. No definition is missing for a visible read.
R1 #1..#17 definitions are sliced. R6 #2..#14 are retained, #1/#15..#17 sliced; no printed guards on these definitions.
Read versions are #5,#6,#7,#8,#11,#14. Retained WITH/address definitions are INITIALIZED_WITH_ADDRESS_OR_NULL_UPDATES; actual constant bitvectors are UNKNOWN.
R6 #2 contains ARRAY_OF directly, so its initialized chain does not syntactically depend on sliced #1. No visible unconstrained source definition is asserted.
R1 original definitions are initialized too; their sliced status only makes free-version conversion a candidate. Fresh full-width bits require converter evidence.
No arbitrary alias/field/offset collapse: canonical view changes whitespace only. A confirmed pinned source rule for PO(&x.field)=PO(&x) was not supplied, and is not assumed.

## Full printed census and selection

Counts include the final visible ASSERT in the first interval. After it, all records are ignored. ASSERT/ASSUME contain equality subexpressions and retain their own record kind.

| Kind/status | R1 through ASSERT | R1 after | R6 through ASSERT | R6 after |
|---|---:|---:|---:|---:|
| guard_assignment/ignored | 59 | 1 | 24 | 1 |
| guard_assignment/retained | 66 | 0 | 83 | 0 |
| assignment/ignored | 4097 | 52 | 4482 | 73 |
| assignment/retained | 430 | 0 | 560 | 0 |
| ASSUME/retained | 33 | 0 | 41 | 0 |
| ASSERT/retained | 96 | 0 | 115 | 0 |
| SHARED_WRITE/retained | 442 | 0 | 478 | 0 |
| SHARED_WRITE/ignored | 0 | 4 | 0 | 8 |

Unknown records=0; other visible categories=0; this does not inventory nonprinted GOTO categories.
Full totals R1=5280 (1067 retained/4213 ignored), R6=5865 (1277/4588); independently match D1-A, without its legacy prefix limits.
Guard lines are separate: R1 through=1579 ignored+456 retained, after=4 ignored (2039 total); R6 through=1394+563, after=4 ignored (1961 total).
Last ASSERT R1: stream line15922, byte1639681, length106, printed5223, PC161; R6 line17116, byte1862239, length106, printed5783, PC161.
Both source-bind to bless_by_id::<1>, library/kani/src/lib.rs:63; these are physical output coordinates, not execution order.
Candidate set: table index reads in all guard assignments (ignored and retained), plus retained other records through last ASSERT. No such candidate occurs after it.
R1: 57 ignored guard-read occurrences -> 6 raw/canonical keys. R6: 22 ignored+11 retained guard-read occurrences -> 12 keys.
All candidate reads are guard-assignment proxies at builtin library line814/check_assignment; there are zero direct table reads in retained non-guard assignments/ASSUME/ASSERT or guard-line expressions.
15 other ignored assignment reads per case (nof_elems accounting) are inventoried but excluded from candidate C/D/S.
WITH updates: global R1 85 ignored, R6 77 ignored+13 retained; table$12 has 16 WITH definitions per pin (R1 all ignored; R6 13 retained+3 ignored).
Byte operators: R1 4 extracts+1 update, R6 9 extracts+1 update, all ignored. These are operator occurrences, not indexed table reads. LHS indexed table stores=0.
Key = exact table SSA/version + index expression + type-derived 64-bit pointer result; PC/function remain provenance. Raw and whitespace-canonical counts coincide on real D1.

## Top candidate read keys (18, below top30 cap)

Index aliases below are display abbreviations, not equivalence rules: M=`_RNvNtCs86zjduzGLhS_4kani8mem_init14MEM_INIT_STATE`, B=`_RNvNtCs86zjduzGLhS_4kani8mem_init15ARGUMENT_BUFFER`.
Each key uses `(long int)__CPROVER_POINTER_OBJECT(&M)` on R1, `(signed long int)__CPROVER_POINTER_OBJECT(&M/&B)` on R6; result type const void*, width64 TYPE_DERIVED.
Only `$12` keys appear here; full expressions, definitions, all provenance coordinates and ignore status are in READ-CENSUS/TABLES.

| Pin | Version | Index | Occurrences ignored/retained | Definition | First stream line/byte |
|---|---|---|---:|---|---|
| r1-skip | `dynamic_object$12#11` | M | 18/0 | sliced | 6949/735627 |
| r1-skip | `dynamic_object$12#8` | M | 14/0 | sliced | 4852/529298 |
| r6b | `dynamic_object$12#11` | M | 11/0 | retained WITH; constant UNKNOWN | 6925/762697 |
| r1-skip | `dynamic_object$12#14` | M | 9/0 | sliced | 10891/1115336 |
| r1-skip | `dynamic_object$12#5` | M | 6/0 | sliced | 2159/258787 |
| r1-skip | `dynamic_object$12#7` | M | 6/0 | sliced | 3961/438713 |
| r1-skip | `dynamic_object$12#6` | M | 4/0 | sliced | 3050/348284 |
| r6b | `dynamic_object$12#11` | B | 0/3 | retained WITH; constant UNKNOWN | 7561/836989 |
| r6b | `dynamic_object$12#14` | M | 3/0 | retained WITH; constant UNKNOWN | 11349/1243619 |
| r6b | `dynamic_object$12#6` | M | 3/0 | retained WITH; constant UNKNOWN | 3094/360303 |
| r6b | `dynamic_object$12#8` | M | 3/0 | retained WITH; constant UNKNOWN | 4912/549686 |
| r6b | `dynamic_object$12#8` | B | 0/3 | retained WITH; constant UNKNOWN | 5491/607086 |
| r6b | `dynamic_object$12#14` | B | 0/2 | retained WITH; constant UNKNOWN | 11928/1301107 |
| r6b | `dynamic_object$12#5` | M | 1/0 | retained WITH; constant UNKNOWN | 2250/269686 |
| r6b | `dynamic_object$12#5` | B | 0/1 | retained WITH; constant UNKNOWN | 2491/296685 |
| r6b | `dynamic_object$12#6` | B | 0/1 | retained WITH; constant UNKNOWN | 3673/416530 |
| r6b | `dynamic_object$12#7` | M | 1/0 | retained WITH; constant UNKNOWN | 4068/457860 |
| r6b | `dynamic_object$12#7` | B | 0/1 | retained WITH; constant UNKNOWN | 4309/485279 |

## Proxy versus converter and pinned-source gap

R1 candidate C_retained=0,D_free=6,S_free=6; 6 first reads per free version, 0 extra distinct same-version reads, 51 repeated occurrences of those same keys.
R6 C_retained=12,D_free=0,S_free=0; 6 retained first-version reads+6 additional distinct same-version reads; 21 repeated occurrences. Of these, 16 repeats are ignored M and 5 retained B.
C_constant is UNKNOWN, not 12 established constant bitvectors. Zero directly confirmed ARRAY_OF-only candidate reads does not prove zero constant-converted reads.
Converter C/D/S and cache misses are UNKNOWN; the text cannot supply a finite upper bound on omitted GOTO reads or a positive lower bound on actual misses.
R6 prediction12 matches the independent proxy. R1 prediction~10 does not: it gives6; no field normalization was required. This is a finding, not parser failure or automatic refutation.
Possible static mirror: R1 GOTO projection line4293/PC1860 and R6 line4406/PC1902, source builtin library:814/check_assignment, allocated.elems[pointer_object(ptr)].
SSA mirror assignments use PC1915/R1 and1957/R6 at that same source/function. Those PCs do NOT equal the projection PCs; equal numeric PC would not establish binding either.
Source/function correspondence yields one candidate static rule for each of the 90 occurrences, but no per-invocation GOTO/L2 identity, polarity/guard completeness, or cache identity.
Pinned CBMC6.11 mechanisms are SOURCE-REPORTED in R3: show_program.cpp:60–90 omits GOTO; symex_goto.cpp:68–93 keeps L2 conditions; slice.cpp:34–121 skips GOTO dependencies; symex_target_equation.cpp:457–482 converts them.
R3 also cites boolbv_map.cpp:41–71 (fresh bits), boolbv_index.cpp:203–240 (finite indexing), cprover_contracts.c:251–278/447–481 (object-table creation).
Exact pinned upstream source contents are absent from the allowed saved D1 inputs; these code rules were not independently re-read or downloaded. Source rule -> actual converter workload remains a precise gap.
Neither zero direct retained-assert table reads nor sliced initialized definitions establish GOTO absence, fresh bits, cache misses or dominant memory.

## Independent arithmetic (R3 §2.2 source-reported counters)

For N=65536, qV=N+64=65600 and qC=65N+1=4259841; kV and kC are computed separately. Residual percentages use observed V/C as denominator.

| Run | kV | kC | V residual | V % | C residual | C % |
|---|---:|---:|---:|---:|---:|---:|
| upstream/43253856019 | 4 | 4 | 22483 | 7.892 | 33050 | 0.194 |
| V02/43258921276 | 12 | 12 | 56829 | 6.733 | 104684 | 0.204 |
| R5-01/43268005490 | 12 | 12 | 59280 | 7.003 | 100743 | 0.197 |
| R6b/43276309576 | 12 | 12 | 42758 | 5.152 | 55693 | 0.109 |

The two k floors agree but do not infer read counts. Clauses fit within0.11–0.21%; variables leave5.15–7.90%. Historical counters are not measurements of these D1 program-only captures.
Conditional 64-bit constant-index model: constant read V≈N+64,C≈65N+1; first free version V≈129N+64,C≈321N+1; extra free read of same version V≈65N+64.
For D free reads on S versions and C constant reads, slopesV=64S+65D+C and slopesC=321D+65C, plus per-read64 and other residuals. S=D is an input to a scenario, never inferred generally.
R1 proxy D=S=6,C=0 would yield50725248 variables/126222342 clauses; forecast~10 instead gives210370570 clauses. Neither is a measured lower bound without GOTO conversion/cache evidence.
R6 proxy IF all12 retained reads convert constant:787200 variables/51118092 clauses; historical residual42758/55693. IF all12 were free sharing6 versions:76284672 variables/252444684 clauses.
Mixed classes, symbolic converted indices, another width or cache reuse change the model. Gate arithmetic is not measured allocations/RSS and no universal2.5–5/<10 ratio is applied.
Optional legal_pfc_transfer/43232249168 counters: UNKNOWN; no exact curated local receipt was handed over, and no historical full log was sought.

## Saturating warning binding and STEP1 handoff

Warnings in exact streams: R1 lines38/42; R6 lines54/58; callsites lib.rs833/846 in both.
Actual GOTO calls: R1 lines4905/4945 (PC2143/2160), R6 lines5020/5060 (PC2186/2203); both pass self and rhs=1, with no write-set argument.
Actual symbol signatures have third __write_set_to_check: R1 symbol Type lines9010/9070; R6 9340/9400.
Exact actual bodies R1 add3895–3907/sub3911–3923, R6 add3990–4002/sub4006–4018; no reference to that parameter in either complete body. Body hashes and full bounds are in READ-CENSUS.
This establishes an unused extra parameter for those bodies statically, more than source-location coincidence. It does not prove general nondet-argument harmlessness, runtime feasibility, all R6 abort branches, or complete fidelity.
No STEP1 dispatch is authorized. Handoff: matched source/fixture/actual-model pins, then separately authorized object-bits12/10/14 with a third completed point and semantic property inventories.
Compare baseline slicing with --no-slice-formula at matched bits; simple tail slicing still applies. Separate initialized-definition effects from hidden GOTO workload/caching, rather than assuming no-slice always grows memory.
--arrays-uf-always is a separate discriminator; rejection/object exhaustion/early frameFAIL/Unsupported are inconclusive, not resource relief.
Ask STEP1 capture design for bounded GOTO/L2 steps with ignore flag, exact typed table/index keys, definition retention, converter cache hit/miss by key/version, actual clauses/variables and raw RSS KiB.
Save complete bounded tails and per-property P1/P2 oracle alongside exact source/fixture/tool/flags identities. Object-bits changes capacity/offset bounds; no proof transfer to16-bit follows.
If stock flags cannot expose those counters, keep them UNKNOWN and plan instrumentation separately; STEP0 does not authorize a converter patch or extra runs.
Final disposition: SUPPORTED_PROXY, converter causality PROVISIONAL; R1~10 has COUNTEREVIDENCE at proxy level. No B1/B2, semantic qualification or independent proof credit.

Validation receipt: 10 synthetic tests PASS; independent anchored marker/ASSERT/guard counts, all read/definition byte spans and input hashes PASS; generated JSON identical on rerun.
Final timed validation: 2.656s wall, process maxrss43084KiB (Python analysis plus coordinate checks, not verifier RSS); ATTRIBUTION151 lines, RESULT31 lines.
