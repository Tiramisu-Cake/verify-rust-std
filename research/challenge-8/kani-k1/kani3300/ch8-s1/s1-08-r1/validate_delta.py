#!/usr/bin/env python3
"""Read-only validation of the concrete W14 coordinate repair and immutability."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import prepare_package as p

HERE=Path(__file__).resolve().parent
OLD_CONTROL='9ccd882ef2460fbc97400594e7e3dfc884a4a997'
OLD_PACKAGE='8ea1c1d370f4076eb6ed4aeaa0a96898499ce580'
CONTROL=Path('/root/kani-ch8-s1-08-fix-w13')
STD=Path('/root/verify-rust-std-ch8-s1-08-w13')


def sha(data):return hashlib.sha256(data).hexdigest()


def check():
    sys.path.insert(0,str(CONTROL/'ch8-s1-control'))
    import oracle_source
    git=p.git
    request=json.loads((CONTROL/'ch8-s1-control/CI-REQUEST.json').read_bytes())
    previous=json.loads(git(CONTROL,'show',OLD_CONTROL+':ch8-s1-control/CI-REQUEST.json'))
    fixed=git(CONTROL,'rev-parse','HEAD').strip()
    assert git(CONTROL,'rev-parse','HEAD^').strip()==p.CONTROL_BASE
    assert git(CONTROL,'rev-parse',OLD_CONTROL+'^').strip()==p.CONTROL_BASE
    assert git(CONTROL,'merge-base',fixed,OLD_CONTROL).strip()==p.CONTROL_BASE
    assert fixed!=OLD_CONTROL
    assert git(STD,'rev-parse','HEAD').strip()==p.STD
    assert not git(STD,'status','--porcelain') and not git(CONTROL,'status','--porcelain')
    old_tree=git(CONTROL,'rev-parse',OLD_CONTROL+'^{tree}').strip()
    assert old_tree=='499871749fe40d714dc70fbafb2fd00f37ed64dd'
    assert git(Path('/root/kani-ch8-s1-08-w13'),'rev-parse','HEAD').strip()==OLD_CONTROL
    assert not git(Path('/root/kani-ch8-s1-08-w13'),'status','--porcelain')
    old=HERE.parent/'s1-08';g0=HERE.parents[5]
    for line in (old/'MANIFEST.sha256').read_text().splitlines():
        digest,rel=line.split('  ',1);assert sha((old/rel).read_bytes())==digest
    assert not git(g0,'diff',OLD_PACKAGE,'--',str(old))
    assert (CONTROL/'ch8-s1-control/ROLE-MAP.json').read_bytes()==(old/'ROLE-MAP.json').read_bytes()
    changed=[];unchanged=[]
    repair=json.loads((HERE/'ORACLE-REPAIR.json').read_bytes())
    changes_by_id={x['row_id']:x for x in repair['changes']}
    for a,b in zip(previous['rows'],request['rows'],strict=True):
        if a.get('oracle'):
            o=a['oracle'];text=git(STD,'show',p.STD+':'+o['file'])
            # Nonproduction oracles have no closure coordinates; source isn't
            # overlaid here because their complete ID and oracle must be equal.
            expected=oracle_source.repair_id(o['property_id'],text,a['selector'].rsplit('::',1)[-1])
            if expected!=o['property_id']:
                assert b['oracle']['property_id']==expected
                normalized=json.loads(json.dumps(b));normalized['oracle']['property_id']=o['property_id']
                assert a==normalized, 'only coordinate substring may change'
                assert changes_by_id[a['id']]['old_id']==o['property_id']
                assert changes_by_id[a['id']]['new_id']==expected
                changed.append(a['id'])
            else:
                assert a==b;unchanged.append(a['id'])
        else:assert a==b
    assert changed==['activation_descending_rejected','activation_effectful_rejected']
    assert len(unchanged)==6
    allowed={'schema','rows','ci_payload_sha256','ci_changed_paths'}
    assert previous.keys()==request.keys()
    assert all(previous[k]==request[k] for k in previous.keys()-allowed)
    changed_paths=set(git(CONTROL,'diff','--name-only',OLD_CONTROL,fixed).splitlines())
    assert changed_paths=={'.github/workflows/ch8-s1.yml','ch8-s1-control/CI-REQUEST.json',
      'ch8-s1-control/ORACLE-SOURCES.json','ch8-s1-control/oracle_source.py',
      'ch8-s1-control/test_s108r1.py','ch8-s1-control/check_package.py',
      'ch8-s1-control/fixtures/s108r1-smallsort.rs.txt','ch8-s1-control/fixtures/s108r1-sorting_model_controls.rs.txt'}
    workflow=git(CONTROL,'show',OLD_CONTROL+':.github/workflows/ch8-s1.yml')
    assert workflow.replace('test_s107.py test_s108.py','test_s107.py test_s108.py test_s108r1.py')==(CONTROL/'.github/workflows/ch8-s1.yml').read_text()
    package=git(CONTROL,'show',OLD_CONTROL+':ch8-s1-control/check_package.py')
    assert package.replace("assert 'test_s108.py' in steps[2]['run']", "assert 'test_s108.py' in steps[2]['run']\n        assert 'test_s108r1.py' in steps[2]['run']")== (CONTROL/'ch8-s1-control/check_package.py').read_text()
    for item in json.loads((HERE/'PRODUCER-SOURCE.json').read_bytes())['files']:
        repo=STD if item['revision']==p.STD else CONTROL
        data=subprocess.check_output(['git','-C',str(repo),'show',item['revision']+':'+item['path']])
        assert sha(data)==item['sha256']
    return {'status':'PASS','source_sha':p.STD,'fixed_control_sha':fixed,'parent':p.CONTROL_BASE,
      'control_relationship':'SIBLINGS_SAME_PARENT_AND_DEPTH5','old_candidate_immutable':True,
      'old_package_manifest_sha256':sha((old/'MANIFEST.sha256').read_bytes()),
      'oracle_ids_repaired':changed,'other_six_oracles':'UNCHANGED_COMPLETE_ORACLES_AND_ROWS',
      'non_oracle_rows':'UNCHANGED','role_map':'BYTE_IDENTICAL_TO_PREVIOUS_127_BINDINGS',
      'runtime_admission_pipeline':'UNCHANGED_EXACT_MATCHER','ci_push':'NOT_RUN',
      'review':'PENDING_DELTA_W14','compiler_exporter_verifier':'NOT_RUN'}


if __name__=='__main__':
    report=check();p.write(HERE/'DELTA-VALIDATION.json',report);print(json.dumps(report))
