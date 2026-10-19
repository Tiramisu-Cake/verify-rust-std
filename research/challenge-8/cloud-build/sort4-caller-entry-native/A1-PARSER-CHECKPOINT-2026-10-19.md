# Select parser compatibility — итог D1/D2, 2026-10-19

**Цель частично достигнута:** установлен и исправлен конкретный quoted-string9362 defect; D2 доходит до следующего compiler ADT shape guard. P0a proof, полный P1 native-interface/equality и N-false31 lifecycle не закрыты. Нужен отдельный scope на MaybeUninit kind; активный guard не изменён.

## Кандидаты и Builds

| Цикл | Source/infra | Pre-submit publication | Build | Тип/гипотеза | Terminal | Charge |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | `189baef7ecb64fac969392a156ef72a9d5baf153` | `22cacac3044e010dbc23c2cbfba4298b87d81bbf` | `f8748a4d-c5f6-47fe-b157-4a9e60839d4e` | setup/parser diagnostic preflight; actual input binding, no proof attempt | FAILURE | 429s |
| D2 | `d246ccbcf7e851f1b3c471daf4ed7aa770e199ea` | `1c79c5035e1bbe6c192ba656e44d0b6c5628b4f2` | `3fc08bb1-07cb-4aed-906d-1c53df1846b5` | mixed parser compatibility + existing full26 route | FAILURE | 516s |

Both proof/infra SHAs and deterministic source payload hashes match coordinator ledger and published release manifests. D1 proof_attempted=false,source1INCONCLUSIVE/25NOT_RUN; that was a preflight, not the full matrix. D2 uses execution_mode=full-matrix and unchanged full26 inventory/lifecycle dependencies. Own fresh tools/reference receipts were reconstructed; no historical receipt substitution. No third Build, automatic retry or new lane.

## Диагноз и минимальное исправление

D1 [compact result](A1-PARSER-D1-RESULT-2026-10-19.json) records actual normal call, relative path focus/P0a/normal-mir.txt, original bytes SHA=parser input SHA `3bf1b47d7e28be437c7f5288c31ad930a1219018fa1cbd035706a94e9a2e6a01`, strictUTF8/universal-newline transforms. Exact targeted64charwindow9330..9394(requestb1be60e252963c00de7360c158b66dc48a7267ab0171d06e8f783ec8c91b2dac) establishes literal9362..9370 hex225c275f5f353322: region.id C escaped apostrophe __53; actual decoder error at9363. Generic service binding/causal flags are not upgraded; actual-call record+member SHA establish the requested input association. D1's normal member SHA also matches D2's verified catalogue.

D2 deterministically decodes only this C apostrophe escape token before strict JSON, preserves backslash pairs, exact identifier/Unicode values and original error offset mapping; malformed/unknown/unsupported forms still reject. No permissive fallback, eval, normalization, schema or non-string parser rewrite. [Rationale](A1-PARSER-D2-RATIONALE-2026-10-19.md) was written before implementation. Cloud D2's new error originates in `_ty` ADT validation after complete `_find_vfmir` parsing: this establishes advancement past the original string failure on the failing inventory path, not successful proof or blanket compatibility of every decoder form.

[New blocker proposal](A1-PARSER-MAYBEUNINIT-PROPOSAL-2026-10-19.md): current `_ty` demands structKind+void, while exact pinned Rust declares MaybeUninit as a union and pinned exporter maps compiler Union→unionKind. [Synthetic minimal counterexample](A1-PARSER-MAYBEUNINIT-SYNTHETIC-2026-10-19.json) rejects unionKind and accepts same recognized MaybeUninit/Self structure as structKind. Actual new failing serialized ADT name/kind/payload/call are not independently shown; the current predicate checks kind before name, so the error label alone is insufficient to assert actual name. Need that compact record before activating proposed strict unionKind expectation. [Two-line proposal](PROPOSED-maybeuninit-union-kind-2026-10-19.patch) applies statically with git apply --check but was NOT applied. The task freezes shape/identity/source-binding/admission predicates, so no semantic expansion was made.

## Review, source closure и identities

One independent GPT-6 Luna HIGH, fork none, no nested delegation: [D1 GO](A1-PARSER-D1-REVIEW-2026-10-19.md), [D2 GO](A1-PARSER-D2-REVIEW-2026-10-19.md). Source-only exact toolbase→43preR→fullR→C compositions/frozen maps PASS; committed closure33infra/107proof/160objects,170/171substitutions PASS. Local isolated service9groups,10valid/11rejected/10oldJSON values, Unicode/UTF8 offset tests and5portable [minimal tests](test_a1_parser_strings.py) PASS. Source checks/review do not establish Cloud compilation; no local actual extraction/fullrunner/compiler/refiner/verifier was executed.

| Identity | SHA-256 |
| --- | --- |
| Full R unchanged | `d99a5ed229533132b8292c5fc70ea93dbe261e9f76c2a0fcc6d6723e796454ca` |
| C unchanged | `e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e` |
| D2 profile | `084a0e7fb2e11511852066b9591df4377286debaa91c24c677ff4a5c89faf006` |
| D2 parser | `92d4e5b336b4e6409da814523500978b56c52218a6289434b526929ae1275b27` |
| R-after/C-before translator | `ffacadc74de9dded1e50e9b9a71f75a905cf97c7c823427cf7044494e87d052d` |
| C-after translator | `a11741f096eb2e1808cadcb8a49eeeb33117630ae6c141d0202af22b14a9b8c3` |
| Exporter source | `c29d0d4692eab84257fe61036d6e41dbc11ee3ad999005df4ffb157bb8b463ad` |

R-before/compiler/nightly commit/decoder generator/toolbase/kernel/refiner/prelude/domain/contracts/negative gates unchanged, per [D2 release](A1-PARSER-D2-RELEASE-2026-10-19.json). Fresh D2 R-only receipt SHAe17046850564f112336b9293eba9807098fa60d64d2420a343c82448ccf47ea0 has build_id3fc08bb1,build_exit0,c_patch_applied=false and matching R/translator/exporter identities; reconstruction receipt SHA466a27e5923f1691b63c534793c7262854cf4ba1eff4774d220c0706f9697633 has build_exit0,A1_TOOL_BUILT_UNRUN_PROOF and matching final-C source/binary identities. These are named own build/receipt facts, not inference from173zero exits and not P1 native equality acceptance. D1 Brief also explicitly names both R/C stages0. Prior compiler errors do not block these builds; absence of every warning not claimed.

## Все26 строки нового D2

[Machine observations/provenance](A1-PARSER-D2-RESULT-2026-10-19.json). All rows below are fresh source-reported statuses from D2 proof-audit.json, SHA `316dd1d30ddcde6c7569a96b5db1a172499fd2df88bab21975b113dbf60e3386`;20statuses via saved Reader observations, R2–R7 via6narrow targeted subtrees, every pointer below explicitly observed. No values copied from old Build/aggregate.

| Case | Source status | Source pointer |
| --- | --- | --- |
| `OFF` | INTENDED_CLASSIFIED | `/case_status/OFF/status` |
| `P0a` | INCONCLUSIVE | `/case_status/P0a/status` |
| `P0b` | NOT_RUN | `/case_status/P0b/status` |
| `P0c` | NOT_RUN | `/case_status/P0c/status` |
| `P-dispatch` | INCONCLUSIVE | `/case_status/P-dispatch/status` |
| `P1` | INCONCLUSIVE | `/case_status/P1/status` |
| `N-binder-collapse` | NOT_RUN | `/case_status/N-binder-collapse/status` |
| `N-alpha-valid` | NOT_RUN | `/case_status/N-alpha-valid/status` |
| `N-free-region` | NOT_RUN | `/case_status/N-free-region/status` |
| `N-region-swap` | NOT_RUN | `/case_status/N-region-swap/status` |
| `N-no-F` | NOT_RUN | `/case_status/N-no-F/status` |
| `N-clauses` | NOT_RUN | `/case_status/N-clauses/status` |
| `N-default-contract` | INCONCLUSIVE | `/case_status/N-default-contract/status` |
| `N-freeze-contract` | INCONCLUSIVE | `/case_status/N-freeze-contract/status` |
| `N-false31` | NOT_RUN | `/case_status/N-false31/status` |
| `N-source` | NOT_RUN | `/case_status/N-source/status` |
| `N-binding` | NOT_RUN | `/case_status/N-binding/status` |
| `N-clause-redirect` | NOT_RUN | `/case_status/N-clause-redirect/status` |
| `N-duplicate` | NOT_RUN | `/case_status/N-duplicate/status` |
| `R1` | INTENDED_CLASSIFIED | `/case_status/R1/status` |
| `R2` | INTENDED_CLASSIFIED | `/case_status/R2/status` |
| `R3` | INTENDED_CLASSIFIED | `/case_status/R3/status` |
| `R4` | INTENDED_CLASSIFIED | `/case_status/R4/status` |
| `R5` | INTENDED_CLASSIFIED | `/case_status/R5/status` |
| `R6` | INTENDED_CLASSIFIED | `/case_status/R6/status` |
| `R7` | INTENDED_CLASSIFIED | `/case_status/R7/status` |

R2/R3/R7 observed_outcome POSITIVE_INTENDED,stageNONE_OBSERVED; R4/R5/R6 NEGATIVE_INTENDED,stageverification; all6matrix_gate_passed=true,proof_credit=false,provenance=fresh-final-tool-regression. Eight source intended classifications do not mean8std theorems.

P1 source INCONCLUSIVE,reason current raw source observation missing,gate=false,credit=false. Targeted `/observation_details/P1` explicitly reports execution_started=true,not_run=false,adapter_error same MaybeUninit struct ADT kind; full equality/reference gate not established. Fresh R-only tool receipt does not replace its own P1 AST/native equality evidence.
N-false31 source NOT_RUN,gate=false,credit=false,reason/stage/outcome/provenance=null. Own pair body/conformance/receipt/admission/threshold32-len32 caller assertion lifecycle not separately established. A1/A2 OPEN/NOT_ACHIEVED; new independently established B1/B2 formal credit absent.

## Evidence boundaries и закрытие

D2 archive/inventory VERIFIED,source run_exit0/evidence_completeTrue,source verdict NOT_ACCEPTED_AS_REPORTED; these are separate from proof acceptance.181/181parsed stage records,8nonzero/173zero,stage orderNOT_ESTABLISHED,last completedUNKNOWN; overall causal_statusUNKNOWN. First reported runner blocker is P0a ADT predicate, not an inferred globally first causal stage. Reader incompleteness, missing actual ADT record and null lifecycle fields stay unknown; no missing result converted toNOT_RUN.

D1 targeted1position window after recorded input binding; D2 targeted7(6case subtrees+P1 observation), all bounded; no automatic pagination/adjacent-window scan/raw logs/archive/CloudLogging. D2 MaybeUninit search in retained normal projection yields NO_MATCH, member CONTENT_BUDGET_EXCEEDED; this does not establish raw absence. Administrative compact ADT record/coordinates needed before new scope activation; no extra Build merely to fill this reporting gap. download_verified not set; historical ledgers/evidence untouched.

2terminal Builds,945/3600Cloudseconds charged (D1429,D2516; execution428/514 separately);2655unused closed without carry. Owner request withdrawn, no own active/unresolved/reservation. T0 16:06:59Z; owner+90min extension main19:36:59Z/absolute20:06:59Z; closed at scope boundary before main. End time/wall-clock in current task/ledger. Setup/proof/reporting stage durations and dialogue-pause durations: no data; wall-clock is not active agent time. No tokens/money estimate. Further implementation/Cloud after close requires a new assignment with explicit MaybeUninit shape scope. This task's full proof objective is not declared achieved.
