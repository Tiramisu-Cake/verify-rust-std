#!/usr/bin/env python3
"""Same14 bounded gate-only delta review; no integration or executable CI package."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / 'r14-03-gate-backlog'
G0 = Path('/root/verify-rust-std-kani3300-g0')
PACKAGE_SHA = '4eccefc670602b58f25f9c55a27da2d844cdcf18'
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def committed_files(directory, commit):
    result = {}
    for path in sorted(directory.iterdir()):
        assert path.is_file()
        rel = str(path.relative_to(G0))
        data = path.read_bytes()
        assert data == git(G0, 'show', commit + ':' + rel), rel
        result[path.name] = sha(data)
    return result


def main():
    package_hashes = committed_files(PACKAGE, PACKAGE_SHA)
    manifest_names = set()
    for line in (PACKAGE / 'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        assert digest == package_hashes[name]
        manifest_names.add(name)
    assert manifest_names | {'MANIFEST.sha256'} == set(package_hashes)
    pins = json.loads((PACKAGE / 'PINS.json').read_text())
    assert pins['proposed_local_control']['sha'] == '0e97a487d8b7f8e8cbced5dbe2b6909c7150c695'
    assert pins['proposed_local_control']['tree'] == 'b980862474e3630c459ee147def4fa45f3ea42fd'
    assert pins['proposed_local_control']['parent'] == '0e8c836857344866564e1423ad5d8d28bbc4106b'
    assert pins['patch']['sha256'] == '1dfaf5a1fa2d748e81bea4093018eb65972d7cfc807e47c0d1f7ad39565f8cba'
    preservation = {}
    for name, revision in [('batch-r4-r1',pins['frozen_package']),
                           ('review-batch-r4-r1',pins['frozen_review']),
                           ('go-r4-r1',pins['entry_g0'])]:
        preservation[name] = {'commit':revision,'files':committed_files(OUT.parent / name, revision)}
    for key in ('proposed_local_control','frozen_control','frozen_source'):
        identity = pins[key]
        repo = Path(identity['worktree'])
        assert git(repo, 'rev-parse', 'HEAD').decode().strip() == identity['sha']
        assert git(repo, 'rev-parse', 'HEAD^{tree}').decode().strip() == identity['tree']
        assert git(repo, 'rev-list', '--parents', '-n', '1', identity['sha']).decode().split() == [identity['sha'],identity['parent']]
        assert not git(repo, 'status', '--porcelain=v1')
    control = Path(pins['proposed_local_control']['worktree'])
    frozen = Path(pins['frozen_control']['worktree'])
    source = Path(pins['frozen_source']['worktree'])
    q = control / 'ch8-s1-control'
    paths = git(control, 'diff', '--name-only', pins['frozen_control']['sha'], pins['proposed_local_control']['sha']).decode().splitlines()
    assert paths == pins['changed_paths'] == ['ch8-s1-control/lexical_bindings.py','ch8-s1-control/test_r1403_lexical.py']
    old_bytes = (frozen / paths[0]).read_bytes()
    new_bytes = (control / paths[0]).read_bytes()
    old_ast, new_ast = ast.parse(old_bytes), ast.parse(new_bytes)
    for module in (old_ast, new_ast):
        assert sum(isinstance(x,ast.FunctionDef) and x.name == 'call_paths' for x in module.body) == 1
        module.body = [x for x in module.body if not (isinstance(x,ast.FunctionDef) and x.name == 'call_paths')]
    assert ast.dump(old_ast, include_attributes=False) == ast.dump(new_ast, include_attributes=False)
    patch = (PACKAGE / 'PATCH.patch').read_bytes()
    assert sha(patch) == pins['patch']['sha256']
    assert patch == git(control, 'diff', '--binary', '--full-index', pins['frozen_control']['sha'], pins['proposed_local_control']['sha'])
    with tempfile.TemporaryDirectory(prefix='same14-gate-index-') as temp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp)/'index'))
        subprocess.run(['git','-C',str(control),'read-tree',pins['frozen_control']['sha']],env=env,check=True)
        subprocess.run(['git','-C',str(control),'apply','--cached',str(PACKAGE/'PATCH.patch')],env=env,check=True)
        assert git(control,'write-tree',env=env).decode().strip() == pins['proposed_local_control']['tree']
    task_documents = []
    for name in ('TASK-CH8-S2-R14-03-BACKLOG-REVIEW-W14.md','TASK-CH8-S2-R14-03-BACKLOG-W13.md'):
        path = G0 / 'research/challenge-8/kani-k1' / name
        assert path.read_bytes() == git(G0,'show',PACKAGE_SHA+':'+str(path.relative_to(G0)))
        task_documents.append({'path':str(path.relative_to(G0)),'sha256':sha(path.read_bytes())})
    dump('INPUTS.json',{'task_id':'task6db728b62b62d6d98d683f3d2cf6fb824dd6cc68',
                        'issued':'owner17:54 SAME14 gate-only delta', 'package_commit':PACKAGE_SHA,
                        'pins':pins,'package_files_sha256':package_hashes,'task_documents':task_documents,
                        'patch_replay':'EXACT_TREE_MATCH','AST_outside_call_paths':'IDENTICAL',
                        'checker_before_sha256':sha(old_bytes),'checker_after_sha256':sha(new_bytes)})
    # Verify preserved precursor failure and distinguish it from final acceptance.
    precursor = json.loads((PACKAGE/'PRECURSOR-NOTES.json').read_text())
    assert precursor['exit_code'] == 1 and precursor['tests'] == 23 and precursor['failures'] == 1
    assert precursor['acceptance_evidence'] is False
    assert b'FAILED (failures=1)' in (PACKAGE/'PRECURSOR-TESTS.txt').read_bytes()
    assert sha(git(control,'show',precursor['control']+':'+paths[0])) == sha(new_bytes) == precursor['checker_sha256_unchanged']
    # Independently rerun the exact 23 affected final-object tests.
    provenance = json.loads((PACKAGE/'TEST-PROVENANCE.json').read_text())
    assert sha((PACKAGE/'TESTS.txt').read_bytes()) == provenance['transcript_sha256']
    argv = [sys.executable] + provenance['argv'][1:]
    start = time.monotonic()
    with (OUT/'FINAL-TESTS.txt').open('w') as stream:
        test = subprocess.run(argv,cwd=q,env=os.environ.copy(),stdout=stream,stderr=subprocess.STDOUT)
    transcript = (OUT/'FINAL-TESTS.txt').read_bytes()
    assert test.returncode == 0 and b'Ran 23 tests in ' in transcript and transcript.endswith(b'\nOK\n')
    dump('TEST-PROVENANCE.json',{'control':pins['proposed_local_control'],'argv':argv,'cwd':str(q),
                                'count':23,'exit_code':test.returncode,'elapsed_seconds':round(time.monotonic()-start,3),
                                'transcript_sha256':sha(transcript),'execution':'ACTUAL_FINAL_COMMITTED_LOCAL_CONTROL',
                                'scope':'Affected targeted offline tests only; full96 not repeated'})
    print('23/23 independent final-object targeted tests PASS',flush=True)
    sys.path.insert(0,str(q))
    import cfg_pfc as c
    import lexical_bindings as l
    spec = importlib.util.spec_from_file_location('same14_frozen_gate', frozen/'ch8-s1-control/lexical_bindings.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    request_bytes = (q/'CI-REQUEST.json').read_bytes()
    assert request_bytes == (frozen/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    assert sha(request_bytes) == pins['unchanged_frozen_request_sha256']
    r = json.loads(request_bytes)
    baseline = l.check(source,r)
    assert baseline == old.check(source,r)
    assert baseline == json.loads((OUT.parent/'batch-r4-r1/NAME-RESOLUTION-MAP.json').read_text())
    assert len(baseline['functions']) == 8 and len(baseline['contexts']) == 11
    assert sum(len(x['static_calls']) for x in baseline['functions']) == 77
    # Repeat the frozen review's exact mutation, not a byte-guard rejection.
    frozen_case = json.loads((OUT.parent/'review-batch-r4-r1/R14-03-DISCRIMINATOR.json').read_text())
    sources = json.loads((q/'S2-SOURCE.json').read_text())
    semantic = copy.deepcopy(r)
    semantic.pop('lexical_source_sha256')
    outcomes = {}
    with tempfile.TemporaryDirectory(prefix='same14-r1403-review-') as temp:
        root = Path(temp)
        for rel,text in sources.items():
            path = root / rel
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
        mutation = sources[l.BATCH].replace(frozen_case['old'],frozen_case['new'],1)
        assert sha(mutation.encode()) == frozen_case['mutated_batch_sha256']
        (root/l.BATCH).write_text(mutation)
        for name,gate in [('frozen',old),('proposed',l)]:
            try:
                doc = gate.check(root,semantic)
                outcomes[name] = {'status':doc['status'],'static_calls':sum(len(x['static_calls']) for x in doc['functions'])}
            except c.GateError as exc:
                outcomes[name] = {'status':'REJECT','diagnostic':str(exc)}
        assert outcomes['frozen'] == {'status':'STATIC_PASS','static_calls':77}
        assert outcomes['proposed']['status'] == 'REJECT' and 'unresolved static path' in outcomes['proposed']['diagnostic']
        assert 'missing_static' in outcomes['proposed']['diagnostic']
    dump('DISCRIMINATOR.json',{'exact_frozen_mutation_sha256':frozen_case['mutated_batch_sha256'],
                              'only_removed_request_keys':['lexical_source_sha256'],
                              'other_request_fields':'EXACTLY_UNCHANGED','outcomes':outcomes,
                              'baseline':'EXACT_MAP_MATCH_FROZEN_PROPOSED_AND_PINNED_MAP;77calls8functions11contexts',
                              'native_compile':'NOT_RUN','proof_credit':'NONE'})
    assert package_hashes == committed_files(PACKAGE,PACKAGE_SHA)
    for name,record in preservation.items():
        assert record['files'] == committed_files(OUT.parent/name,record['commit'])
    for key in ('proposed_local_control','frozen_control','frozen_source'):
        repo = Path(pins[key]['worktree'])
        assert not git(repo,'status','--porcelain=v1')
        assert git(repo,'rev-parse','HEAD').decode().strip() == pins[key]['sha']
    dump('PRESERVATION.json',preservation)
    dump('CHECKS.json',{'status':'STATIC_PASS','manifest':'COMMITTED_MATCH_UNCHANGED',
                       'changed_paths':paths,'checker_delta':'call_paths ONLY; AST outside identical',
                       'patch_replay':'EXACT_TREE_MATCH','final_targeted_tests':23,
                       'precursor_failure':'PRESERVED; CHECKER_BYTES_IDENTICAL; NO_ACCEPTANCE_CREDIT',
                       'baseline_map':'EXACTLY_UNCHANGED77/8/11','exact_discriminator':'FROZEN_ACCEPTS_PROPOSED_REJECTS',
                       'frozen_package_review_GO_source_control':'UNCHANGED_BEFORE_AND_AFTER',
                       'integration':'NOT_PERFORMED','package_status':'NOT_AN_EXECUTABLE_CI_PACKAGE',
                       'native_compile':'NOT_RUN','CI':'NOT_RUN','proof_credit':'NONE'})
    print('REVIEW_CHECKS_COMPLETE: gate-only exact delta, patch replay, discriminator, baseline, preservation PASS',flush=True)


if __name__ == '__main__':
    main()
