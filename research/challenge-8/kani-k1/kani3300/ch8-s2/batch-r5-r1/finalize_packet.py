#!/usr/bin/env python3
"""Record final-object measurements and narrow finding closures; never runs tests."""
import hashlib,json,subprocess
from decimal import Decimal,ROUND_CEILING
from pathlib import Path
H=Path(__file__).resolve().parent;G=H.parents[6]
def load(n):return json.loads((H/n).read_text())
def dump(n,x):(H/n).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=load('PINS.json');c=p['control'];timing=load('COMBINED-FINAL-VALIDATE-TIMING.json');tests=load('COMBINED-TEST-PROVENANCE.json');source=load('COMBINED-CHECK-SOURCE-TIMING.json')
assert timing['status']=='PASS' and tests['test_count']==134 and timing['provenance']['control']['sha']==c['sha'] and source['status']=='PASS'
host=Decimal(timing['monotonic_end_ns']-timing['monotonic_start_ns'])/Decimal(10**9);assert host==Decimal(str(timing['elapsed_seconds']))
mins=int((host*Decimal('1.5')/60).to_integral_value(rounding=ROUND_CEILING));assert mins<=11
m=load('TIMEOUT-MARGIN.json');m.update(measurement_classification='ACTUAL_FINAL_OBJECT',actual_control=c,actual_host_seconds=str(host),actual_tests=134,minimum_seconds_exact=str(host*Decimal('1.5')),minimum_whole_minutes=mins,new_ratio=str(Decimal(660)/host),rounding='ceil(actual final Validate seconds *1.5/60)',targeted_tests='CAP-TESTS.json; plus four archive-only tests in actual final134',prior_measurement_classification='INHERITED_PRIOR_OBJECT4e97')
dump('TIMEOUT-MARGIN.json',m)
Q=Path(c['worktree'])/'ch8-s1-control'
case_names=['test_archive_only_prefix_exact_seal_and_collect_after_later_failure','test_missing_required_structured_member_rejects_archive','test_mutated_structured_member_with_updated_entry_hash_still_rejects','test_compact_cap_omission_is_explicit_and_never_qualified']
log=(H/'COMBINED-FINAL-VALIDATE.txt').read_text()
import re
for name in case_names:assert re.search(name+r'.* \.\.\. ok',log),name
dump('UPLOADED-PREFIX-REGRESSION.json',{'status':'PASS_ACTUAL_FINAL_OBJECT','control':c,'test_module_sha256':sha(Q/'test_r5.py'),'transcript_sha256':sha(H/'COMBINED-FINAL-VALIDATE.txt'),'measurement':'COMBINED-TEST-PROVENANCE.json','cases':{n:'PASS' for n in case_names},'old_exact_repro':load('PRIOR-4E97-UPLOADED-PREFIX-REPRO.json'),'positive_assertions':['real _run_group, root_outcome, finalize, fallback, packer and public collect','external native execution/source sampling fixtures only','two sequential singleton mock groups; first RECORDED, later UNKNOWN','copy only group-evidence.json.gz to clean directory and delete producer output','all required structured bytes hash-verified by sealed','byte-exact retained first row before and after fallback and archive replay','collect first RECORDED with expected_match true; later UNKNOWN; full inventory false','raw log payloads absent; local digest metadata nonrequired','proof_credit NONE'],'negative_assertions':['missing required export member rejected','tampered property member rejected even after updating entry hash/length','synthetic compact-cap omission publishes INCOMPLETE and never qualifies','production artifact caps unchanged'],'scope':'SYNTHETIC_SERVICE_REGRESSION; NOT_NATIVE_PROOF'})
inv=load('INVARIANCE.json');inv['portable_service_AST_except_sealed_root_outcome']='IDENTICAL';inv['existing_test_r5_AST_without_added_PortablePrefixTests']='IDENTICAL';dump('INVARIANCE.json',inv)

p.update(review14='SAME14_EXACT_COMBINED_DELTA_PENDING; prior022b CHANGES_REQUIRED',timing_classification='ACTUAL_FINAL_OBJECT',full_suite_new_head={'tests':134,'seconds':str(host),'execution_count':1,'receipt':'COMBINED-FINAL-VALIDATE-TIMING.json'},finding_author_status={'R14-R5-01':'FIXED_AWAITING_INDEPENDENT14_CLOSED','R14-R5-02':'FIXED_AWAITING_INDEPENDENT14_CLOSED'})
p['changed_test_pins'].update({'COMBINED-TEST-PROVENANCE.json':sha(H/'COMBINED-TEST-PROVENANCE.json'),'COMBINED-FINAL-VALIDATE.txt':sha(H/'COMBINED-FINAL-VALIDATE.txt')})
for n in ('PINS.json','IDENTITIES.json'):dump(n,p)
review=H.with_name('review-batch-r5');records=[]
for n in ('REPORT.md','reproduce_uploaded_prefix.py','UPLOADED-PREFIX-REPRO.json'):
 b=subprocess.check_output(['git','-C','/root/verify-rust-std-kani3300-g0','show','022b9893c693f5908d3c9fa2ffe22961bbf8d30b:research/challenge-8/kani-k1/kani3300/ch8-s2/review-batch-r5/'+n]);assert b==(review/n).read_bytes();records.append({'file':n,'sha256':sha(review/n)})
dump('REVIEW-INPUTS.json',{'review_commit':'022b9893c693f5908d3c9fa2ffe22961bbf8d30b','status':'CHANGES_REQUIRED','verified_inputs':records,'findings':['R14-R5-01','R14-R5-02'],'independent_closure':'PENDING_SAME14_EXACT_FINAL_DELTA'})
dump('AUDIT.json',{'control':c,'workflow_step_sum_minutes':187,'prior_step_sum_minutes':186,'setup_step_maxima_seconds':3180,'binding_setup_aggregate_seconds':1800,'job_minutes':180,'proof_step_seconds':7560,'campaign_seconds':6900,'validate_minutes':11,'local_sampled_PGID_RSS_GiB':6,'outer_sampled_PGID_RSS_GiB':12,'RSS_scope':'sampled PGID, not strict root/tree/kernel/cgroup','child_seconds':600,'compile_subcap_inside_child_seconds':180,'slot_seconds':720,'resources_schedule_source_tool':'UNCHANGED','extra_budget_grant':False,'current_budget_reference_only':'10/14 item2;39/43 total; extra3 NOT_APPROVED','dispatch':'NONE','proof_credit':'NONE'})
dump('CHECKPOINT.json',{'state':'READY_SAME14_DELTA_REVIEW','control':c,'source':p['source'],'tool':p['tool'],'tests':134,'Validate_seconds':str(host),'check_source_seconds':source['elapsed_seconds'],'margin':str(Decimal(660)/host),'independent14':'PENDING','native_r5':'NOT_RUN','CI':'NOT_RUN','ledger':'UNTOUCHED','dispatch_authority':'NONE'})
dump('PROVENANCE.json',{'task':'taska9cc91d717751d2047e13bc7570a95305f546fa7','margin_task':'taske333995f0089a629e0ccbaf1a477248ff5fc31e2','plan':'07d891b23ba65405920090de87ed7eec9730fec4','intake':'5ca0641af6c5b588ae2a4257ccc0fe52df6a827a','prior_package':p['frozen_package'],'prior_control':p['frozen_control'],'cap_only_control_precursor':'4f1271b72d266b1e5ff47132ce5c1bac0e55470c','final_control':c,'prior130':'INHERITED_PRIOR_OBJECT403.420022367s','new134':'ACTUAL_FINAL_OBJECT timed once','native_r5_r1':'NOT_RUN','source_tool_caps':'UNCHANGED','Fast':'OFF_NOT_TOGGLED','settings':'PRESERVED','subagents':0,'CI_push_issue_ledger_budget':'NONE'})
text=f'''Combined r5-r1 READY for SAME14 delta review; dispatch authority NONE.

Control {c['sha']}; tree {c['tree']}; parent {c['parent']}.
Request SHA256 {c['request_sha256']}; workflow SHA256 {c['workflow_sha256']}.
Source {p['source']['sha']}; tool {p['tool']['sha']}; checkout depths7/5/2.

R14-R5-01: R5 Validate11min, exact-cap assertions and maxima187 rebound; legacy10min/186 unchanged. Actual final Validate134 PASS {host}s, margin {Decimal(660)/host}x >=1.5. Check-source PASS {source['elapsed_seconds']}s. Prior130/403.420022367s stays INHERITED_PRIOR_OBJECT4e97. New timing was necessary because portable service/test behavior changed, with unchanged workflow command/module list.

R14-R5-02: portable seal schema ch8-s2-r5-portable-seal-v1 requires hashed structured JSON only. Raw captures stay local with explicitly nonrequired local-only digest metadata. Protected packer/decoder, source/tool/binary/compile/export/rich-property/diagnostic bindings remain unchanged. Path/schema/hash checks reject unavailable/mutated structured payloads. Old exact repro fails on stderr.log; fixed archive-only test deletes producer directory, preserves byte-exact completed prefix after later failure/fallback/pack, verifies seal AND public collect. Missing member, mutation with updated entry digest, and published compact-cap INCOMPLETE are rejected. No raw logs added to upload. Production compact caps unchanged; cap test uses synthetic padding/threshold.

Frozen530/4e97, review022b and cap-only4f evidence preserved. Delta contains only seven control paths; runtime delta only sealed/root_outcome, four tests added to existing explicit test_r5 module. Source/tool/order/campaign caps unchanged. Both general32 roots deferred;9/16/5 selected and full11/20/6 retained. No native compiler/verifier/full runner/CI/push/ledger/reservation. Extra3 budget NOT_APPROVED. Independent exact-final APPROVE and R14-R5-01+02 CLOSED required before separate GO request. This author fix does not claim independent closure or proof credit.
'''
for n in ('HANDOFF.md','REVIEW14-REQUEST.md'):(H/n).write_text(text)
(H/'TIMEOUT-MARGIN.md').write_text(f'''R5 Validate11 minutes (660s); legacy10 unchanged. Actual final134 PASS {host}s; ceil(1.5*{host}/60)={mins}min, ratio={Decimal(660)/host}. Prior130/403.420022367s is inherited4e97 only. See timing/provenance for exact object, command, environment and monotonic clocks. Future CI duration remains UNKNOWN. Setup aggregate1800, job180min, proofstep7560s, campaign6900s and resource caps unchanged; step sum187/setup maxima3180s do not grant more aggregate budget.\n''')
(H/'CURRENT-TASK.md').write_text('READY_SAME14_DELTA_REVIEW taska9cc91d717751d2047e13bc7570a95305f546fa7\nCombined R14-R5-01+02 repair; independent closure PENDING; no GO authority.\n')
(H/'DEVELOPMENT-NOTES.md').write_text('Cap-only4f and prior530/4e97 receipts retained as precursors. Targeted test threshold originally hit final hard cap ValueError; fixture corrected to force bounded INCOMPLETE artifact while leaving fallback envelope room, production caps unchanged. One precommit targeted invocation had wrong cwd/import failure; corrected transcript retained. Initial package enumeration included charon gitlink; narrowed file invariance traversal to ch8-s1-control plus exact whole-tree seven-path diff. No broader controller changes.\n')
(H/'BACKLOG.md').write_text('No additional controller improvements included. Optional broader controller work requires a separate task. Independent SAME14 exact-final delta review remains required.\n')
print('Final measurements bound; margin',Decimal(660)/host)
