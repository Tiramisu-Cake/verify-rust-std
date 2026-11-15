"""Validate the offline result and presentation-name injection on actual inputs.
Python standard library only. Reads untrusted artifact files as data.
"""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path


def sha(data):return hashlib.sha256(data).hexdigest()


def validate(directory):
    result_path = directory/'RESULT-OFFLINE.json'
    result = json.loads(result_path.read_bytes())
    assert result['normalizer_sha256'] == sha((directory/'offline.py').read_bytes())
    assert result['hash_checked_raw_dump_files'] == 2358
    assert result['checked_dump_commands'] == 2358
    assert len(result['records']) == 393
    assert len({row['key'] for row in result['records']}) == 393
    assert result['control_symbol_gate_valid'] is True
    assert len(result['control']) == 3
    assert not result['normalization_errors']
    assert result['status'] == 'INCONCLUSIVE_AA'
    assert result['evidence_gaps'] == [{'code':'EMPTY_GOTO_FUNCTION_DUMPS','count':1179,'expected':1179,
        'reason':'exit 0 and empty bytes do not expose compiled GOTO bodies; symbol tables contain compiled markers'}]
    counts=collections.defaultdict(collections.Counter)
    ab_before_local=[]
    aa_after=[]
    controls_each_stage={}
    for row in result['records']:
        arms=row['arms']
        stages=set(arms['A1']['stage_sha256'])
        assert stages==set(arms['A2']['stage_sha256'])==set(arms['B1']['stage_sha256'])
        for stage in stages:
            counts[stage][row['kind']] += arms['A1']['stage_sha256'][stage]==arms['A2']['stage_sha256'][stage]
        if arms['A1']['stage_sha256']['initialize_order'] != arms['B1']['stage_sha256']['initialize_order'] and not row['is_control']:
            ab_before_local.append(row['key'])
        if not row['A1_A2_symbols_equal']:aa_after.append(row['key'])
        if row['is_control']:
            controls_each_stage[row['key']]={stage:arms['A1']['stage_sha256'][stage]==arms['A2']['stage_sha256'][stage]
                and arms['A1']['stage_sha256'][stage]!=arms['B1']['stage_sha256'][stage] for stage in stages}
            assert all(controls_each_stage[row['key']].values())
    assert {k:dict(v) for k,v in counts.items()}==result['AA_EQUAL_BY_CUMULATIVE_POLICY']
    # Independent corpus check for the reviewer's potential printed-name collision.
    # A symbol-name-only scan suffices: this map is the precise transformation
    # used before initializer RHS binding, without repeating normalization.
    root=Path(result['artifact_root']).resolve(strict=True)
    index=json.loads((root/'INDEX.json').read_bytes())
    seen={}
    compiled_total=collections.Counter()
    colliding=[]
    checked_names=0
    for key,entry in index.items():
        for arm,value in entry['arms'].items():
            spec=value['modes']['symbol-table'];digest=spec['raw_sha256']
            if digest not in seen:
                path=(root/spec['raw']).resolve(strict=True)
                assert path.is_relative_to(root)
                data=path.read_bytes();assert sha(data)==digest
                mapping={};markers=0
                for match in re.finditer(rb'^Symbol\.\.\.\.\.\.: (.*)$',data,re.M):
                    name=match[1].decode()
                    if 'AllocId(' in name and not name.startswith('tag-'):
                        printed=name.replace('.', '_').replace('::','$$')
                        if printed in mapping and mapping[printed]!=name:
                            colliding.append({'dump':spec['raw'],'printed':printed,'names':[mapping[printed],name]})
                        mapping[printed]=name;checked_names+=1
                markers=len(re.findall(rb'^Value\.\.\.\.\.\.\.: irep\([^\n]*compiled[^\n]*$',data,re.M))
                seen[digest]=markers
            compiled_total[entry['kind']]+=seen[digest]
    assert not colliding
    referenced={entry['diff'] for entry in result['residual_differences']}
    for entry in result['residual_differences']:
        assert sha((directory/entry['diff']).read_bytes())==entry['diff_sha256']
    report={'result_sha256':sha(result_path.read_bytes()),'normalizer_sha256':result['normalizer_sha256'],
        'validation_script_sha256':sha(Path(__file__).read_bytes()),'unique_symbol_dumps_scanned':len(seen),
        'allocation_definition_names_checked':checked_names,'printed_allocation_name_collisions':colliding,
        'compiled_Value_markers_by_kind_all_arms':dict(compiled_total),'AA_symbol_residual_keys':aa_after,
        'noncontrol_AB_before_local_alpha':ab_before_local,'control_AA_equal_AB_different_at_every_stage':controls_each_stage,
        'AA_cumulative':{k:dict(v) for k,v in counts.items()},'all_assertions_passed':True}
    (directory/'VALIDATION-OFFLINE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    validate(parser.parse_args().directory.resolve(strict=True))
