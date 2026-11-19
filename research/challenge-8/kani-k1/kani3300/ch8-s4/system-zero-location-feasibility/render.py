#!/usr/bin/env python3
"""Render the source-only investigation; no intake or native recomputation."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_bytes())
def write(n,s):
 if '--check' in sys.argv:assert (HERE/n).read_text()==s,n
 else:(HERE/n).write_text(s)
def main():
 cases=read('CASE-COMPARISON.json')['cases'];v=read('VALIDATION.json');pins=read('INPUTS.json')['pins'];neg=read('NEGATIVE-DISCRIMINATORS.json')
 table='| Exact case | Mode | Native properties | U | SUCCESS guards | Existing scope |\n|---|---|---:|---:|---:|---|\n'
 for c in cases:table+=f"| `{c['root']}` | {c['mode']} | {c['native_property_count']} | {c['U_count']} | {c['guard_count']} | {'DIAG_INIT_OPEN/nonprovider' if 'partial_diag' in c['root'] else 'Exact bounded SOURCE_REPORTED'} |\n"
 text=f'''# System zero-location investigation — READY

**COMMON_EMITTER_UNKNOWN.** A single generic Kani compiler template is the strongest verified candidate: `TerminatorKind::Unreachable` calls `codegen_assert_assume_false(PropertyClass::Unreachable, "unreachable code", loc)`, with `loc` from `term.source_info.span`. The pinned compiler/bindings/driver source has one exact literal occurrence and one `PropertyClass::Unreachable` use. This identifies a source routine capable of producing the records. It does not identify the same semantic check, the same inserted instruction, the same original source site or the same reason for the zero span in all five invocations.

Exactly five target packets are frozen, with full property/display IDs, null-key presence, class/status/description, cardinality, invocation, namespace, authenticated member identities, source/tool/control/request/workflow/cfg/argv and count/status partitions in CASE-COMPARISON.json. The optional old sort4same reference was not used or counted.

{table}
All five have one exact `unreachable` class, SUCCESS-status record displayed as `library/core/src/lib.rs:0:0 in function EXACT_HARNESS`, with both normalized file/line keys present-null. Their full IDs and invocation namespaces differ. The five inventories also contain {neg['located_other_class_unreachable_SUCCESS']} other positively located SUCCESS properties of the same `unreachable` class; total class count is {neg['total_class_unreachable_SUCCESS']}. Counterexamples with the same literal and `.unreachable.1` suffix, including core/std paths, are in NEGATIVE-DISCRIMINATORS.json. Class/status/text/suffix/std path cannot identify the actual check. StatusUNREACHABLE U is a separate partition and is never waived.

The three merge bodies are PFC u8/KeyLess fixtures that call bidirectional_merge at exact8 with disjoint geometries and then check full logical counts/known frames. Two remain partial-initialization diagnostics/nonproviders. The two fallback bodies are Original Cell<u8>/KeyLess<Cell<u8>> initialized V34/base1 with full independent logical bytes, symbolic N0..2 and3..4. They call small_sort_fallback, which returns below2 or calls insertion_sort_shift_left(offset1) -> insert_tail. These are source call paths, not a recovered dynamic path to the offending instruction. PFC-only, Cell-only or partial-initialization-only causes are not necessary conditions across the five. No valid harness/role/declaration line is substituted for a missing coordinate.

The exact static trace and its limits are recorded in TRACE.json. SOURCE-CITATIONS.json contains22 committed-file citations with file Git blob/SHA256 and exact inclusive source-range byte hashes/text. The relevant sequence is:

| Stage | What the pinned source establishes | What remains unbound |
|---|---|---|
| MIR/codegen (T01,T02,T14–T16) | A MIR Unreachable emits assert(false), then assume(false), with a supplied span. Several transforms can produce such terminators; the enum comment also mentions intrinsic versus compiler-assumed unreachability. | Actual historical body/block, transform route, span and original Rust expression for each check. |
| Location/Irep/GOTO (T03–T07) | Filename/coordinates/current function become a Property location and are serialized. Numeric0 is accepted and preserved on this route. Span-cache reuse resets current function/pragmas. | Which actual span produced lib.rs0, its expansion/inlining history, and whether later external transforms changed the instruction/location. |
| External processing/ID (T08–T10) | Kani specializes/instruments GOTO and invokes external CBMC; its consumer parses function.class.counter and demangles function names. | Raw successful property ID and final instruction map; `.1` is not a stable source identity. |
| Export/display (T10–T12) | Display prints supplied optional line/column strings including0. Stock export retains individual source fields for failures and unsupported constructs, while ordinary SUCCESS checks contribute counts. | The successful system property's original SourceLocation object, raw symbol and source/MIR origin. |
| Rich normalizer (T13) | Both controls have identical reader bytes. Authentic stored fields reproduce the exact0:0 display with present-null file/line. | Matching normalization does not supply missing emitter or source origin. |

The direct abort_immediate intrinsic emitter has classAssertion and a `reached intrinsic` message (T17), unlike the target. This excludes that direct emission as the literal/class match, but not an Unreachable terminator following a nonreturning call. `Location::None` also has a different direct serialized representation from a present0:0 location; external historical propagation remains unbound. `unreachable_unchecked` has a real must-never-be-reached safety precondition (S05), so classunreachable cannot be treated as harmless bookkeeping globally.

A synthetic normalizer discriminator found an additional grammar edge: `lib.rs:0:17` can become filename `lib.rs:0` and line17 because the regex can absorb a colon into the filename. The actual five0:0 records still become null and are unaffected. PARSER-EDGE-CASE.json records the exact pinned parser and synthetic outputs. This limits claims about all linezero/column forms and about positive syntactic coordinates; it is not native evidence or an applied parser repair.

A common rule cannot replace the five exact admissions on the available binding. RULE-PROPOSAL.json is NOT_APPLIED and recommends no general activation. It lists minimum future fingerprint requirements: pinned tool/parser/schema, an authenticated actual emitter/check-creation fingerprint, per-property MIR/GOTO identity and reason for unavailable location, exact invocation/protected/member bindings, justified cardinality and full unchanged partitions. Every other role/cover/U/guard remains strict; extra failures/gaps/unknown states reject. That emitter fingerprint is an explicitly unfilled gating field, and no matching rule is implemented.

UNKNOWN-GAPS.json specifies the missing discriminators: map each exact rendered ID to the raw property/instruction; map that instruction to MIR terminator/span/pass; trace why the coordinates became0; establish a narrow common semantic check kind across differing modes/types. These require authentic same-invocation origin evidence, not an inverse guess from the rendered text. Any future instrumentation or native evidence work needs separate authorization/review/GO. None is requested or performed here.

The existing merge review028531/admissionff193 and fallback review3c7bd65/admission9bb6 remain immutable. The script verifies every admission packet equals its exact independent review packet. Original producerUNKNOWN/strict rejection remains historical. Existing bounded admissions remain bounded; the two partial merge diagnostics remain DIAG_INIT_OPEN/nonproviders. This investigation grants no extra safety, functional, init/provider/summary/MIR/B1/B2/generic/fullN credit.

Validation passes: {v['checks_count']} targeted static/projection checks,22 source citations and25 pure normalizer checks (five authentic-field reconstructions and20 synthetic discriminators). No intake replay, artifact acquisition, raw/ZIP/GCS access, full suite, native/compiler/CI activity, source/control/tool/parser/policy/flags/runtime/ledger changes or publication. CurrentSolHigh/FastOFF preserved; no subagents/model changes. The investigation is complete with recorded UNKNOWNs, and does not delay or gate network plan/review/implementation.
'''
 write('TRACE.md',text)
 write('READY.md',f'''# READY — offline system zero-location feasibility

Result: **COMMON_EMITTER_UNKNOWN** across exactly5 merge/fallback packets. One static MIR-Unreachable codegen template is verified as the strongest candidate. The actual shared semantic check/site and the cause oflib.rs0 remain unbound. Both controls have the same normalizer bytes; five authentic-field0:0 reconstructions agree. A synthetic0:17 colon-ambiguity finding is recorded separately and affects none of the five exact packets.

Rule proposal NOT_APPLIED/no general activation. Five original exact admissions and producer history retained; partial merge diagnostics remain DIAG_INIT_OPEN/nonproviders. No new proof/admission credit and no network work gate.

{v['checks_count']} targeted checks PASS;22 exact committed source citations;25 pure normalization checks. See TRACE.md, CASE-COMPARISON.json, RULE-PROPOSAL.json, UNKNOWN-GAPS.json, NEGATIVE-DISCRIMINATORS.json, PARSER-EDGE-CASE.json and HANDOFF.md. MANIFEST.json covers the packet except itself; the containing immutable Git commit covers the manifest.
''')
 write('HANDOFF.md',f'''# W11 immutable READY handoff

Use the exact full40-character g0 commit returned with this packet. Task/input commit `{read('INPUTS.json')['task_commit']}`. Only `kani3300/ch8-s4/system-zero-location-feasibility/` is owned. Root should verify that exact commit and MANIFEST.json. Existing independent review/admission source blobs are pinned and hashed in PROVENANCE.json; tool `{pins['tool']}`, source `{pins['source']}`, fallback control `{pins['control']}`. The merger's source/control pins are separately frozen in CASE-COMPARISON.json.

Conclusion COMMON_EMITTER_UNKNOWN. Candidate static template is Kani MIR Unreachable -> assert-assume(false), classunreachable/messageunreachable code. Static uniqueness within inspected Kani source and shared normalization do not prove the same semantic check, per-invocation emission site, positive source coordinate or cause of0:0. The source trace, five full exact cases, negative discriminators and missing GOTO/MIR/span mapping are ready for root review.

General rule NOT_APPLIED and not recommended for activation until the missing emitter binding is established; proposed minimum fingerprint and failclosed adverse requirements are in RULE-PROPOSAL.json. Existing five exact original-run admissions remain unchanged:3 merge metadata cases (two partialDIAG_INIT_OPEN/nonproviders) and2 bounded Original Cell fallback cases. All U/roles/covers/guards remain strict. No retrospective producer/history edits or new credit.

PARSER-EDGE-CASE.json records a source-only synthetic0:17 grammar ambiguity; actual five0:0/null records are unaffected. No parser repair is applied or authorized here.

Reproduce read-only with `python3 build_packet.py --check`, `python3 render.py --check`, and `python3 seal.py --check` in this directory using pinned local Git objects. These commands do not recompute the intake, acquire evidence or invoke native tools. Before any future common rule: separate authorized evidence work if needed, independent review, and explicit root/coordinator decision. This investigation does not block network plan/review/implementation.

CurrentSolHigh/FastOFF preserved; no subagents/model changes, source/control/tool/parser/policy/flags/runtime/CI/native/acquisition/ledger/publication changes. Unrelated concurrent worktree output was preserved. Completion reason: authorized offline investigation is finished; uncertainty is an explicit result, not a blocker.
''')
 print(json.dumps({'render':'PASS','mode':'check' if '--check' in sys.argv else 'write'}))
if __name__=='__main__':main()
