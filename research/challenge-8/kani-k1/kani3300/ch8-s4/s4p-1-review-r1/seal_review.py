#!/usr/bin/env python3
"""Seal only this new independent review directory; no candidate/ledger edits."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
G0 = Path('/root/verify-rust-std-kani3300-g0')
PACKET = HERE.parent / 's4p-1-r1'
read = lambda p: json.loads(p.read_text())
D = lambda raw: hashlib.sha256(raw).hexdigest()

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    assert not (HERE / 'MANIFEST.sha256').exists(), 'Review already sealed'
    audit = read(HERE / 'AUDIT.json')
    replay = read(HERE / 'REPLAY.json')
    tests = read(HERE / 'TARGETED-TESTS.json')
    authorpins = read(PACKET / 'PINS.json')
    final = read(PACKET / 'FINAL-VALIDATE.json')
    assert audit['status'] == replay['status'] == tests['status'] == 'PASS'
    assert len(audit['invariants']) == 14 and tests['tests'] == 6 and tests['errors'] == tests['failures'] == 0
    assert not (HERE / 'REPLAY.stderr').read_bytes() and not (HERE / 'AUDIT.stderr').read_bytes()
    assert replay['malformed_rejected_before_collection'] == 78 and replay['genuine_accepted'] == 6
    assert all(x['status'] == 'PASS' for x in audit['invariants'])
    identities = {}
    for name in ('source', 'control', 'tool'):
        item = authorpins[name]
        git = lambda *args: subprocess.check_output(['git','-C',item['repo'],*args], text=True).strip()
        assert git('rev-parse','HEAD') == item['sha'] and git('rev-parse','HEAD^{tree}') == item['tree']
        assert not git('status','--porcelain=v1')
        identities[name] = {'sha':item['sha'],'tree':item['tree'],'parents':item['parents'],'clean_after':True}
    assert subprocess.check_output(['git','-C',str(G0),'rev-parse','HEAD'],text=True).strip() == audit['author_commit']
    for line in (PACKET / 'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert D((PACKET / name).read_bytes()) == digest
    pins = {'schema':'ch8-s4p-1-independent14-delta-pins-v1',
            'task_commit':audit['task_commit'], 'owner_issue':'Owner10:13 /new14 overrides prepared reuse; execute exact W14 delta',
            'repair_author_commit':audit['author_commit'], 'frozen_author':'590dd6360f5b4c92eab9fff30aa0d2e7d8d942ce',
            'frozen_full_review':audit['frozen_review'], 'old_control':'e941155517a02f67ea9bac1adb81c1d5f6f85638',
            **identities, 'request':authorpins['request'],
            'repair_manifest_sha256':audit['packets']['repair']['manifest_sha256'],
            'frozen_review_manifest_sha256':audit['packets']['frozen_review']['manifest_sha256'],
            'final_validate_receipt_sha256':D((PACKET / 'FINAL-VALIDATE.json').read_bytes()),
            'final_validate':final, 'future_head_ref_run':'UNKNOWN',
            'delivery_commit':'REPORTED_EXTERNALLY_NO_SELFHASH_LOOP'}
    save('PINS.json', pins)
    closures = [
        {'id':'R14-01','priority':'P2','status':'CLOSED','blocking_exact_approval':False,
         'file':'ch8-s1-control/s4p_contract_stacks.py','line':110,
         'basis':'Actual prebuild gate:32 unique powerset contexts,16 sorting and4 ACTIVE. Every ACTIVE comparison exercises safety-wrapper to direct-Kani normalization with unchanged op/predicate tokens. Fresh actual four reports match committed JSON; source/hash/required-path checks retained. Meaningful regression is CI-selected and passed.',
         'evidence':['PREFLIGHT.json','TARGETED-TESTS.json','AUDIT.json']},
        {'id':'R14-02','priority':'P2','status':'CLOSED','blocking_exact_approval':False,
         'file':'ch8-s1-control/s4p_campaign.py','line':342,
         'basis':'Trusted exact string schema check before legacy collection. Real public LOCAL/UPLOAD_ONLY paths reject78 malformed cases including all original24 with zero legacy collection calls and only terminal read;6 genuine controls accept. Genuine prefixes0..8 and selected_roots int8 pass both routes.',
         'evidence':['TERMINAL-SCHEMA-MATRIX.json','PREFIXES.json','TARGETED-TESTS.json']}
    ]
    save('FINDINGS.json', {'schema':'ch8-s4p-1-independent14-delta-findings-v1','verdict':'APPROVE',
                          'repair_author_commit':audit['author_commit'],'control_sha':identities['control']['sha'],
                          'findings':closures,'new_findings':[],'blockers':[],'exact_candidate_approval':True,
                          'frozen_review_unchanged':'REQUEST_CHANGES on590/E941 remains historical; this is new delta closure',
                          'GO':'NOT_AUTHORIZED','proof_credit':'NONE'})
    save('HARNESS-NOTES.json', {'initial_replay_exit':1, 'initial_replay_stage':'Report comparison during source preflight; no service tests had run',
                               'cause':'Reviewer compared Python lexical report tuples directly against serialized JSON arrays at four required_production_fragments fields.',
                               'preserved':['replay-01.py','REPLAY-01.stdout','REPLAY-01.stderr','PREFLIGHT-REPRESENTATION.json'],
                               'correction':'Compare actual report through its JSON data model, matching the committed JSON report. No source/control/map/terminal schema was changed.',
                               'corrected_replay_exit':0,'corrected_replay_seconds':replay['seconds'],
                               'full_validate_executions_by_reviewer':0})
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    checkpoint = {'schema':'ch8-s4p-1-independent14-delta-checkpoint-v1','completed_utc':now,
                  'status':'READY_EXACT_APPROVE_NO_BLOCKERS','verdict':'APPROVE',
                  'task_commit':audit['task_commit'],'repair_author_commit':audit['author_commit'],
                  'control_sha':identities['control']['sha'],'closed':['R14-01','R14-02'],'new_findings':[], 'blockers':[],
                  'exact_candidate_approval':True,
                  'inheritance':'Frozen4856 unaffected conclusions inherited only through exact source/tool/request-semantics/runtime/profile/domain/mode/caps byte invariance and limited five-file control delta.',
                  'assurance':'INDEPENDENT_STATIC_AND_BOUNDED_SYNTHETIC_SERVICE_REVIEW; retained author full Validate receipt checked, not re-executed',
                  'checks':{'invariants':14,'repair_packet_files':62,'repair_packet_hashes':61,'author_readonly_checks':820,
                            'patch_trees':6,'shallow_depths':{'control':7,'source':5,'tool':2},'cfg_projections':32,'sorting_enabled':16,'ACTIVE_contexts':4,
                            'malformed_rejected_before_collection':78,'original24_rejected':24,'genuine_accepted':6,'prefixes':list(range(9)),'targeted_tests':6},
                  'retained_author_final_validate':{'tests':305,'seconds':final['elapsed_seconds'],'limit_seconds':1080,'margin':final['margin_at_18_minutes'],'exit_code':0,'execution_count':1,'reviewer_repeated':False},
                  'GO':'NOT_AUTHORIZED','proof_credit':'NONE','native_compile_proof_cost_fit':'NOT_RUN','future_head_ref_run':'UNKNOWN',
                  'accounting':'TRACKING_ONLY_UNCHANGED; no ledger/reservation/admission writes',
                  'next':'Root recheck exact repair/review full pins and manifests, then GO-request ch8-s4/s4p-1-go/ for ONE8 root attempt only; no automatic dispatch.',
                  'future_trigger':'User coordinator only: NONSKIP same-tree sibling of final control with sole9e14, exact source985 and stock0aac, unchanged workflow/request and shallow7/5/2; actual head/ref/run UNKNOWN.',
                  'open':['Root recheck and separate GO decision','Native compile/proof/exhaustion/cost/fit and compiler/MIR/B1/B2 UNKNOWN/NOT_RUN',
                          'Fallback5..16/network5..32/general/type/caller/init/ownership/panic/provider obligations OPEN'],
                  'constraints':'Only own new review paths written; no candidate edits/subagents/model changes/fullValidate/compiler/native/CI/fullrunner/raw/GCS/ledger/push/publication.',
                  'closure_reason':'Requested independent delta review complete; both localized blockers closed and exact candidate approved. Further GO/publication/dispatch belongs to root/user coordinator.'}
    save('CHECKPOINT.json', checkpoint)
    (HERE / 'CURRENT-TASK.md').write_text('''# W14 — exact S4P1 repair delta review

Runtime: Codex. Owner10:13 /new14 overrides prepared reuse and issues task989b0dbd020bc9bb500c0a18f3220d21537fbc44 on repair5b0ed64d86c6cd7ac18bb3c7b7b7fd124dcb504c.
High/FastOFF requested; no subagents/model changes performed.

Result: READY_EXACT_APPROVE_NO_BLOCKERS / APPROVE. Independently R14-01 CLOSED and R14-02 CLOSED. Six targeted tests PASS,32/16/4 actual gate,78 bad rejects before collection/6 genuine accepts,all prefixes0..8 on both public routes. Exact source/tool/runtime/profile/caps invariance supports inherited unaffected review4856 conclusions only. Full Validate retained305 PASS/550.637729s/1.961362x, not repeated.

See REVIEW.md, FINDINGS.json, PINS.json and CHECKPOINT.json. Root exact recheck precedes a separate GO request. GO NOT_AUTHORIZED; native/proof/CI/head/ref/run UNKNOWN/NOT_RUN; proof credit NONE. Only this new immutable output is written.
''')
    (HERE / 'REVIEW.md').write_text('''# Independent W14 delta review — APPROVE

READY_EXACT_APPROVE_NO_BLOCKERS. R14-01 CLOSED; R14-02 CLOSED. No new findings or blockers. Exact approval applies to repair author `5b0ed64d86c6cd7ac18bb3c7b7b7fd124dcb504c` under issued task `989b0dbd020bc9bb500c0a18f3220d21537fbc44`.

Reviewed control `2db5d2c08804036d283cb36450647cd584ee9e10`, tree `96b03b52cdd121965690544945c17b175253c6cd`, sole parent `9e14e033f9ee31522b571c127609dcdff76d230b`. It is an E941 sibling, not its child. Source `985062ebad90cee1e2846b1648cd6a8624d146f6` and stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba` retain exact frozen trees/parents and clean worktrees. Request SHA256 is `3d135ebabd0793681a5b8a2fdb2414324c7021c5d8791e700fc713b633ddd149`; workflow SHA256 remains `a56791ab37df944d65131c0a7a612a5245d3c8a0275ff8810fb44fa6a7af061a`. Full identities are in PINS.json.

**R14-01 — CLOSED.** At `ch8-s1-control/s4p_contract_stacks.py:110`, enumeration now derives from all five independent keys. Independent execution used the actual `runner.verify_source(..., prebuild=True)` against the exact source/tool checkouts, wrapping and calling the real policy/declaration functions. The actual gate produced the complete unique32-element powerset,16 sorting-enabled contexts and4 ACTIVE contexts. All four fresh gate reports match the committed JSON maps. Every ACTIVE context contains nonempty wrapper-to-direct-Kani comparisons with identical operations and predicate tokens; function availability/signatures/bodies remain checked by the real gate. No fabricated report or disabled comparison substitutes for those calls. PREFLIGHT.json records the compared functions/wrappers/source hashes. The new CI-selected regression passed, as did targeted required-path, Cell-anchor, missing-module and wrong-contract-target rejection tests. Old gate modules and fixture coverage are byte-invariant.

**R14-02 — CLOSED.** At `ch8-s1-control/s4p_campaign.py:342`, the reader requires a real string equal to trusted literal `ch8-s4p-1-campaign-v1` before reaching `legacy_collect` at line349. Both public LOCAL and compact-only UPLOAD_ONLY routes dispatch through this check. Expected schema is not derived from terminal data. Real current writer/finalizer, public collector and compact packer were exercised with synthetic native/Git/telemetry inputs. Only the terminal schema changed; all other structured evidence bytes were checked unchanged. Across full8, STOPPED0 and PARTIAL0, all78 missing/null/int/bool/float/list/object/empty/unknown/old-schema mutations rejected with the exact schema error, zero legacy-collection calls, and only the terminal receipt read before rejection. All original24 cases are included. All6 genuine state/route controls accepted; full cases retain8 RECORDED observations and genuine LOCAL/upload results agree. See TERMINAL-SCHEMA-MATRIX.json.

Independent public-reader replays also accepted every authentic prefix0..8 with genuine schema and selected_roots of exact int8 on both routes; unfinished rows retain existing semantics. PREFIXES.json records these controls. All three new actual CI-selected regressions and three retained source/legacy controls passed:6 tests,0 errors/failures (TARGETED-TESTS.*). Legacy7/8/9 schemas/counts, their actual runtime paths and their Validate selections are unchanged, with their retained successful suites bound to the final candidate. No malformed schema was normalized, rebaselined or collected by this replay.

**Exact invariance and retained validation.** Independently checked the repair packet's62 files/61 manifest hashes against the exact author commit, all118 request payload hashes, the frozen review's18 files/17 hashes, and the frozen author's54 files/53 hashes. Whole-tree mode/object comparison against E941 yields exactly five paths: CI-REQUEST.json, s4p_campaign.py, s4p_contract_stacks.py, s4p_validate.py and the new test_s4p_gate_repair.py. CI request fields differ only in payload inventory/hashes. The full Validate script changes only by adding this test module to NEW. All other control tree entries remain identical, including shared runtime/snapshots/ownership/reap/cleanup/deadlines/portable seals/caps, old profile gates, fixtures, lexer cache and workflow. Eight Original/null rows, full34u8/base1/Cell and four length-block candidates,21 literal assertions/30 covers, modes/domains/roles/locations/unwind/waivers are unchanged. Frozen full review4856's unaffected conclusions inherit solely by these exact invariances; its historical REQUEST_CHANGES on590/E941 remains untouched.

All six full patches were independently replayed with disposable indexes and temporary object directories to exact complete trees. Local shallow fetches independently confirmed required control7/source5/tool2 commits/trees. Fourteen review invariants pass (AUDIT.json); the read-only author checker also independently executed with820 checks PASS. Historical590/E941/review4856/old302PASS and all recorded precursor failures remain separate and byte-preserved. See PATCH-REPLAY.json, SHALLOW.json and AUDIT.json.

The retained exact final workflow Validate receipt, script/command/workflow/request/control identities and transcript hashes agree. Five suites report136+56+35+40+38=305 PASS, exit0,550.637729009s with1.961362150x margin at unchanged18min, exceeding1.5. Each new regression appears as executed and successful in the retained transcript. This is checked retained author local execution evidence, not independently measured timing or a CI run. No concrete concern warranted repeating full Validate, and none was repeated.

The review harness's initial preflight comparison stopped on Python tuples versus serialized JSON arrays at four lexical report fields. The original script and failed transcript are retained. Comparing the actual report through its JSON data model yields exact equality; source/control/committed maps were untouched. Corrected distinguishing replay passed. See HARNESS-NOTES.json and PREFLIGHT-REPRESENTATION.json.

**Handoff boundary.** This review grants exact implementation approval only. Root must recheck full new pins/manifests before a separate `ch8-s4/s4p-1-go/` GO request for ONE8 root attempt. Future actual head/ref/run remain UNKNOWN. The authorized future trigger must be a NONSKIP same-tree sibling of final control with sole9e14, exact source985/coordinator publication and stock0aac, unchanged request/workflow and shallow7/5/2. No automatic CI, rerun, publication, admission or accounting follows from APPROVE.

No candidate edits, compiler/rustfmt/native proof/full runner, CI, raw/full/GCS, ledger changes, push/publication, subagent or model change occurred. Only this new review directory was written. GO NOT_AUTHORIZED; new proof credit NONE. Native compile/proof/exhaustion/cost/fit, compiler/MIR binding and B1/B2 remain UNKNOWN/NOT_RUN. Even a future completed/reviewed/admitted union is limited to the exact finite families/lengths0..4; fallback5..16/network5..32/general/type/caller/init/ownership/panic/provider obligations remain OPEN.
''')
    (HERE / 'READY.md').write_text('''# READY — independent exact APPROVE

R14-01 CLOSED. R14-02 CLOSED. No blockers or new findings.
Exact repair5b0ed64d86c6cd7ac18bb3c7b7b7fd124dcb504c/control2db5d2c08804036d283cb36450647cd584ee9e10 approved.
14 invariants PASS; real32/16/4 gate;78 malformed rejects before collection/6 genuine accepts;prefix0..8/int8 both routes;6 targeted tests PASS.
Retained exact305PASS/550.637729s/1.961362x; full Validate not repeated.
Root recheck -> separate GO request only. GO NOT_AUTHORIZED; proof credit NONE; future head/ref/run UNKNOWN.
Manifest/delivery digest reported externally; no self-hash loop.
''')
    (HERE / 'HANDOFF.md').write_text('''# W14 delta handoff

APPROVE, R14-01 CLOSED, R14-02 CLOSED, no blockers. Exact identities and retained validation are in PINS.json; independent closure evidence is in REVIEW.md/FINDINGS.json/AUDIT.json/REPLAY.json.

Root rechecks exact repair5b0ed64d86c6cd7ac18bb3c7b7b7fd124dcb504c, new review delivery commit and both manifests before preparing ch8-s4/s4p-1-go/ for ONE8 root attempt only. Actual future source/head/ref/run remain UNKNOWN until the separately authorized user coordinator action. A future NONSKIP trigger must preserve final control tree96b03b52cdd121965690544945c17b175253c6cd and sole9e14e033f9ee31522b571c127609dcdff76d230b as a sibling, exact source985/tool0aac, request3d135/workflowa567 and shallow7/5/2. Review is not GO, dispatch, admission or proof credit.

Original frozen review4856 remains historical REQUEST_CHANGES; author590/E941/old302PASS and precursors are preserved. All proof/native/MIR/B1/B2 and broader family obligations remain open. Original13 CURRENT295 retains ownership of any later localized repair; none is requested by this approved delta.
''')
    files = sorted(p for p in HERE.rglob('*') if p.is_file() and p.name != 'MANIFEST.sha256')
    manifest = ''.join(D(p.read_bytes()) + '  ' + str(p.relative_to(HERE)) + '\n' for p in files)
    (HERE / 'MANIFEST.sha256').write_text(manifest)
    print(json.dumps({'verdict':'APPROVE','closed':['R14-01','R14-02'],'blockers':[], 'files':len(files)+1,'hashes':len(files),'manifest_sha256':D(manifest.encode()),'GO':'NOT_AUTHORIZED'}), flush=True)

if __name__ == '__main__':
    main()
