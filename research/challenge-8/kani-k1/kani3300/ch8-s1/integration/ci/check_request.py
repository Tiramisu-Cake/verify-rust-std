#!/usr/bin/env python3
"""Source/manifest/overlay static binding checks; never invokes tools under test."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
STD=Path('/root/verify-rust-std-ch8-s1-w13')

def main():
    r=json.loads((HERE/'CI-REQUEST.json').read_text())
    assert r['std_sha']=='75a4d1ea6eb60c63c27c1b18e662740d93bafb08'
    assert r['std_tree']=='6d1b90bc11440762c9b65889fc538ba3071b0d9d'
    assert r['tool_sha']=='0aac16ef62da9e9d5645782d458593e5d78143ba'
    assert r['tool_tree']=='9d8bc9312bf955ef126d32b819b3cd0ed105ed2b'
    rows=r['rows'];assert len(rows)==23
    ids={x['id'] for x in rows};assert len(ids)==len(rows)
    assert all(x['state']=='NOT_RUN' and x['timeout_seconds']==600 for x in rows)
    assert all(x['selector'].startswith('slice::sort::shared::smallsort::verify::') for x in rows)
    assert all(x['source_qualified_selector']=='core::'+x['selector'] for x in rows)
    assert sum(x['mode']=='PFC' and x['variant']=='production' for x in rows)==8
    assert sum(x['expected']=='DETECTED' for x in rows)==8
    assert sum(x['variant']!='production' for x in rows)==2
    assert sum(x['id']=='ordinary-bridge' for x in rows)==1
    assert sum(x['planned_seconds'] for x in rows)==r['budgets']['planned_rows_seconds']
    assert r['budgets']['planned_rows_seconds']+r['budgets']['planned_list_seconds']<=r['budgets']['phase_seconds']
    assert r['budgets']['setup_seconds']+r['budgets']['phase_seconds']+r['budgets']['reserve_seconds']==7200
    assert r['flags']['uninit'] is False and r['flags']['valid_value'] is False
    assert r['flags']['no_assert_contracts'] and r['flags']['unwinding_assertions']
    for row in rows:
        if row['expected']=='DETECTED':
            assert row['failure_description']
            companion=row['companion'];assert companion in ids
            legal=next(x for x in rows if x['id']==companion)
            assert legal['expected']=='SUCCESS' and legal['variant']=='production'
    for rel,h in r['changed_file_sha256'].items():
        assert hashlib.sha256((STD/rel).read_bytes()).hexdigest()==h
    src=(STD/'library/core/src/slice/sort/shared/smallsort.rs').read_text()
    for name,variant in r['variants'].items():
        patch=HERE/variant['patch']
        assert hashlib.sha256(patch.read_bytes()).hexdigest()==variant['sha256']
        subprocess.run(['git','-C',str(STD),'apply','--check',str(patch)],check=True)
        changed=[x[1:] for x in patch.read_text().splitlines() if x.startswith(('+    #[cfg_attr','-    #[cfg_attr'))]
        assert len(changed)==2 and 'kani::ensures(' in changed[0] and 'kani::ensures(' in changed[1]
        assert variant['marker'] in patch.read_text() and variant['marker'] not in src
    print(json.dumps({'manifest':'PASS_STATIC_ONLY','rows':len(rows),'positive':15,'negative':8,
        'PFC_production':8,'activation_variants':2,'ordinary_bridge':1,'CLI_selectors':'crate-relative slice::; future actual-list reconciliation mandatory',
        'planned_seconds':3060,'hard_invocation_seconds':600,'phase_seconds':4500,'dispatch':'NOT_RUN','Cloud_dollars':0},indent=2))

if __name__=='__main__':main()
