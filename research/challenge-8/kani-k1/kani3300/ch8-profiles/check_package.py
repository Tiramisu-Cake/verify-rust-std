#!/usr/bin/env python3
"""Check frozen source/package bindings without building or running Rust tools."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
request = json.loads((HERE/'CI-REQUEST.json').read_text())
review = json.loads((HERE/'REVIEW.json').read_text())
audit = json.loads((HERE/'static-audit.json').read_text())
assert review['decision'] == 'GO_STATIC_REVIEW_ONLY'
assert request['source']['commit'] == review['candidate_commit'] == audit['candidate']
assert request['source']['tree'] == review['candidate_tree'] == audit['tree']
assert hashlib.sha256((HERE/'source.patch').read_bytes()).hexdigest() == request['source']['patch_sha256']
assert request['off_tool']['commit'] == '0aac16ef62da9e9d5645782d458593e5d78143ba'
assert request['off_flags']['uninit'] is False and request['off_flags']['valid_value'] is False
assert request['dispatch_cap'] == 3 and request['dispatch_charged'] == 0
assert request['caps']['rss_kib']/1048576 == request['caps']['rss_gib'] == 6
assert sum(request['caps'][k] for k in ('setup_seconds','proof_phase_seconds','closeout_seconds')) == request['caps']['workflow_minutes']*60
rows = request['rows']
assert len(rows) == len({r['selector'] for r in rows}) == 62
by_id = {r['id']: r for r in rows}
order = {r['id']: i for i,r in enumerate(rows)}
for row in rows:
    assert row['state'] == 'NOT_RUN' and row['property_binding'] is None
    assert row['timeout_seconds'] == 600
    assert row['cfg'] == (['kani_smallsort_controls'] if row['expected'] == 'DETECTED' else [])
    if row['mode'].startswith('Replace'):
        leaf = by_id[row['leaf_companion']]
        assert order[leaf['id']] < order[row['id']]
        assert leaf['profile'] == row['profile']
        assert leaf['mode'].startswith('PFC') and leaf['expected'] == 'SUCCESS'
for name in ['profile_wrong_f_swap_rejected_u8','profile_wrong_f_sort4_rejected_u64',
             'profile_wrong_f_insert_rejected_u8','profile_wrong_f_merge_rejected_u8',
             'profile_bad_relation_rejected_u8','profile_full_value_checker_rejects_payload_change_u8',
             'rejects_always_true','rejects_payload_corruption',
             'rejects_swap_comparator_writing_outside_frame_u8']:
    assert by_id[name]['expected'] == 'DETECTED'
assert len(by_id['rejects_always_true']['allowed_failure_descriptions']) == 3
subprocess.run(['git','-C','/root/verify-rust-std-ch8-profiles-w11','apply','--reverse','--check',str(HERE/'source.patch')], check=True)
rerun = subprocess.check_output([sys.executable,str(HERE/'audit_static.py')])
assert json.loads(rerun) == audit
result = {'schema':'ch8-profiles-package-check-v1','state':'PASS_STATIC_ONLY','source':audit['candidate'],
          'rows':len(rows),'modes':dict(collections.Counter(r['mode'] for r in rows)),
          'checks':['request/source/review/patch identities','positive/negative row oracle completeness',
                    'leaf-before-consumer same-profile gates','caps and KiB/GiB arithmetic',
                    'reverse patch check against candidate','reproduced full source audit'],
          'ci_request_sha256':hashlib.sha256((HERE/'CI-REQUEST.json').read_bytes()).hexdigest(),
          'review_sha256':hashlib.sha256((HERE/'REVIEW.json').read_bytes()).hexdigest(),
          'Rust_compilation':'NOT_RUN','lowering':'NOT_RUN','Kani':'NOT_RUN','ON':'DEFERRED_NOT_RUN',
          'builds':0,'pushes':0,'dispatches':0,'proof_credit':'NONE'}
print(json.dumps(result,indent=2))
