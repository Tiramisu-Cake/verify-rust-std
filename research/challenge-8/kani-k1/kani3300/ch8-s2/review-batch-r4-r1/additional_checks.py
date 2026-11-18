#!/usr/bin/env python3
"""R14-03: required static path in nested parentheses disappears from name gate."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

OUT = Path(__file__).resolve().parent
PINS = json.loads((OUT.parent / 'batch-r4-r1/PINS.json').read_text())
Q = Path(PINS['control']['worktree']) / 'ch8-s1-control'
sys.dont_write_bytecode = True
sys.path.insert(0, str(Q))
import cfg_pfc as c
import lexical_bindings as l


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sources = json.loads((Q / 'S2-SOURCE.json').read_text())
    request = json.loads((Q / 'CI-REQUEST.json').read_text())
    assert sha((Q / 'CI-REQUEST.json').read_bytes()) == PINS['control']['request_sha256']
    original_request = copy.deepcopy(request)
    removed = request.pop('lexical_source_sha256')
    assert set(original_request) - set(request) == {'lexical_source_sha256'}
    expr = '((missing_static))();'
    scanner = []
    for sample in ('missing_static();', '(missing_static)();', expr,
                   '((super::super::sort4_stable))(a,b,c);'):
        scanner.append({'source':sample,'call_paths':list(l.call_paths(c.tokens(sample)))})
    assert len(scanner[0]['call_paths']) == len(scanner[1]['call_paths']) == 1
    assert scanner[2]['call_paths'] == scanner[3]['call_paths'] == []
    original = sources[l.BATCH]
    needle = 'fn sort13_weak() {'
    assert original.count(needle) == 1 and 'missing_static' not in original
    mutated = original.replace(needle, needle + ' ' + expr)
    with tempfile.TemporaryDirectory(prefix='same14-r14-03-') as temp:
        root = Path(temp)
        for rel, text in sources.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        (root / l.BATCH).write_text(mutated)
        result = l.check(root, request)
        record = next(x for x in result['functions'] if x['function'] == 'sort13_weak')
        assert result['status'] == 'STATIC_PASS'
        assert not any('missing_static' in json.dumps(x) for x in result['functions'])
        assert sum(len(x['static_calls']) for x in result['functions']) == 77
        failure = {'id':'R14-03', 'priority':'P2', 'status':'OPEN', 'owner':'original13',
                   'control':PINS['control'], 'source':PINS['source'],
                   'checker_path':'ch8-s1-control/lexical_bindings.py', 'checker_lines':[78,84],
                   'mutation_file':l.BATCH,'mutation_line':original[:original.index(needle)].count('\n')+1,
                   'old':needle,'new':needle + ' ' + expr,
                   'original_batch_sha256':sha(original.encode()),
                   'mutated_batch_sha256':sha(mutated.encode()),
                   'only_removed_request_keys':['lexical_source_sha256'],
                   'removed_hash_map_sha256':sha(json.dumps(removed,sort_keys=True).encode()),
                   'request_other_fields':'EXACTLY_UNCHANGED',
                   'scanner_controls':scanner,
                   'actual_full_name_gate':{'status':result['status'],'functions':len(result['functions']),
                                            'static_call_occurrences':77,'contexts':len(result['contexts']),
                                            'mutated_function_record':record,
                                            'missing_static_in_inventory':False},
                   'expected':'REJECT unresolved required static path, or explicitly reject unsupported callable parentheses',
                   'impact':'New bounded lexical gate silently omits a required static call instead of resolving or failing closed',
                   'independent_protection':'Exact immutable source/request hashes and correspondence independently reject changed bytes; no bypass claimed',
                   'actual_final_source':'No missing_static call in unchanged repaired source; this finding concerns the explicitly required new gate behavior',
                   'native_compile':'NOT_RUN','proof_credit':'NONE'}
    (OUT / 'R14-03-DISCRIMINATOR.json').write_text(json.dumps(failure,indent=2)+'\n')
    print('R14-03 REPRODUCED: nested-parenthesized unbound static call omitted; full name gate STATIC_PASS, 77 calls/8 functions/11 contexts')


if __name__ == '__main__':
    main()
