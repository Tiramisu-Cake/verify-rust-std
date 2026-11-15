"""R2 artifact reader for offline.py; standard library only, no backend execution.

Use the unchanged symbol policies in offline.py. Function content is compared
exactly, after independently splitting the single source-justified path banner.
No speculative location/label/order/identifier rewrite is applied to new bodies.
"""
import collections
import difflib
import json
from pathlib import Path
import runpy


def run_r2(root, output, normalizer):
    root = root.resolve(strict=True)
    output = output.resolve()
    if output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError('output must be disjoint from untrusted artifact')
    output.mkdir(parents=True, exist_ok=True)
    result_path = output / 'RESULT-OFFLINE-r2.json'
    result_path.write_text(json.dumps({'schema': 'b3-t1b-r2-offline-v1', 'status': 'INVALID',
                                     'stage': 'READ_VALIDATION_NOT_COMPLETED'}) + '\n')
    sha, safe_read = normalizer['sha'], normalizer['safe_read']
    def read(relative):
        # Match the CI validator: duplicate JSON members are never accepted.
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('duplicate JSON key')
                result[key] = value
            return result
        return json.loads(safe_read(root, relative), object_pairs_hook=unique)
    original, index = read('RESULT.json'), read('INDEX.json')
    if (original.get('schema') != 'b3-t1b-r2-capture-v1'
            or original.get('status') != 'CAPTURE_COMPLETE_OFFLINE_REQUIRED'
            or original.get('stage') != 'COMPLETE' or str(original.get('run_attempt')) != '1'
            or str(original.get('source_run')) != '43701550489'
            or original.get('source_artifact') != 'b3-t1-43701550489-1'):
        raise ValueError('wrong or incomplete r2 capture')
    expected_models = 393
    lineage = {'task_base': '43b065bb9d0fc78cb66aef81584a8241a85f461d',
               'ci_parent': '1a8faa3b60ee9a19534cdb57315e8887f5666301',
               'source_ci_sha': 'cfa4b0c5296b1f7735b0d4a138d339431dfbf93d'}
    if any(original.get(k) != v for k, v in lineage.items()):
        raise ValueError('capture CI/research lineage mismatch')
    if not isinstance(original.get('ci_sha'), str) or len(original['ci_sha']) != 40 or any(c not in '0123456789abcdef' for c in original['ci_sha']):
        raise ValueError('missing/invalid source-reported capture CI SHA')
    counts = collections.Counter(e['kind'] for e in index.values())
    expected = {kind: expected_models // 3 for kind in ('final', 'linked', 'symtab')}
    if len(index) != expected_models or counts != expected:
        raise ValueError('incomplete r2 model inventory')
    arms, modes = ('A1', 'A2', 'B1'), ('symbol-table', 'goto-functions')
    source = {}
    for arm in arms:
        path = f'input/{arm}/index.json'
        if sha(safe_read(root, path)) != original['input_indexes'][arm]:
            raise ValueError('source index digest mismatch')
        src = read(path)
        tool = read(f'input/{arm}/tools.json')['goto-instrument']['sha256']
        if (src.get('complete') is not True or tool != src['tools']['goto-instrument']
                or tool != original['tool']['sha256'] or tool != original['tool']['expected_sha256']):
            raise ValueError('source tool identity mismatch')
        source[arm] = src['records']
        if set(index) != {k for k, v in source[arm].items() if v['kind'] in expected}:
            raise ValueError('source/model inventory mismatch')
    extract = runpy.run_path(str(Path(__file__).with_name('function_dump_r2.py')))['extract_functions']
    commands = collections.defaultdict(list)
    for path in sorted((root / 'commands').glob('*.json')):
        cmd = read(str(path.relative_to(root)))
        commands[cmd['stdout']].append(cmd)
    def command_data(relative, mode, arm, key):
        entries = commands[relative]
        if len(entries) != 1 or entries[0].get('state') != 'EXIT' or entries[0].get('exit') != 0:
            raise ValueError('missing/failed dump command')
        cmd = entries[0]
        argv = cmd['argv']
        verbosity = '6' if mode == 'goto-functions' else '4'
        suffix = '/' + arm + '/' + source[arm][key]['path']
        if (len(argv) != 5 or argv[0] != original['tool']['path']
                or argv[1] != '--show-' + mode or not argv[2].endswith(suffix)
                or argv[3:] != ['--verbosity', verbosity]):
            raise ValueError('source/mode/tool/verbosity command mismatch')
        if safe_read(root, cmd['stderr']):
            raise ValueError('nonempty display stderr')
        data = safe_read(root, relative)
        if not data:
            raise ValueError('empty display stdout')
        return data, argv[2]
    output.mkdir(parents=True, exist_ok=True)
    cache, texts, records = {}, {}, []
    verified = total_bytes = 0
    for key, entry in sorted(index.items()):
        if set(entry['arms']) != set(arms):
            raise ValueError('arm inventory mismatch')
        texts[key] = {}
        row = {'key': key, 'kind': entry['kind'], 'arms': {}}
        for arm in arms:
            item = entry['arms'][arm]
            if (item['input_sha256'] != source[arm][key]['sha256']
                    or entry['kind'] != source[arm][key]['kind'] or set(item['modes']) != set(modes)):
                raise ValueError('source/kind/mode binding mismatch')
            values, hashes = [], {}
            for mode in modes:
                spec = item['modes'][mode]
                data, model = command_data(spec['raw'], mode, arm, key)
                if sha(data) != spec['raw_sha256']:
                    raise ValueError('raw dump digest mismatch')
                verified += 1
                total_bytes += len(data)
                if mode == 'symbol-table':
                    digest = sha(data)
                    if digest not in cache:
                        cache[digest] = normalizer['stages'](data.decode('utf-8', errors='strict'))
                    rendered, stages, stats = cache[digest]
                    hashes.update(symbol_stage_sha256=stages, symbol_policy_counts=stats)
                else:
                    body, banner, body_counts = extract(data, model)
                    for field, value in (('content', body), ('status', banner)):
                        if safe_read(root, spec[field]) != value or sha(value) != spec[field + '_sha256']:
                            raise ValueError('function content/status split mismatch')
                    if any(spec[k] != v for k, v in body_counts.items()):
                        raise ValueError('function/instruction census mismatch')
                    hashes.update(body_counts)
                    rendered = body.decode('utf-8', errors='strict')
                hashes[mode] = sha(rendered)
                values.append(rendered)
            row['arms'][arm] = hashes
            texts[key][arm] = values
        records.append(row)
        if len(records) % 25 == 0:
            print('r2 normalized ' + str(len(records)), flush=True)
    # Independently validate six raw determinism repeats and their commands.
    seen = set()
    for repeat in original['determinism']:
        key, arm, mode = repeat['key'], repeat['arm'], repeat['mode']
        identity = (key, arm, mode)
        if identity in seen:
            raise ValueError('duplicate repeat identity')
        seen.add(identity)
        spec = index[key]['arms'][arm]['modes'][mode]
        relative = spec['raw'].removesuffix('.txt') + '.repeat.txt'
        data, model = command_data(relative, mode, arm, key)
        if (repeat['equal'] is not True or sha(data) != spec['raw_sha256']
                or sha(data) != repeat['first_sha256'] or sha(data) != repeat['repeat_sha256']):
            raise ValueError('raw repeat mismatch')
        if mode == 'goto-functions':
            extract(data, model)
    samples = {(key, arm) for key, arm, mode in seen}
    if (len(seen) != 6 or len(samples) != 3 or {a for k, a in samples} != set(arms)
            or len({k for k, a in samples}) != 3 or any(not k.startswith('final/') for k, a in samples)):
        raise ValueError('missing three-arm, three-model, two-mode determinism samples')
    residual, aa_equal = [], set()
    def compare(key, left, right):
        paths = []
        for mode, a, b in zip(modes, texts[key][left], texts[key][right]):
            if a != b:
                name = sha(key)[:24] + f'.{left}-{right}.{mode}.diff'
                delta = ''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=left+'/'+key, tofile=right+'/'+key))
                (output / name).write_bytes(delta.encode('utf-8'))
                paths.append({'mode': mode, 'path': name, 'sha256': sha(delta)})
        if paths:
            residual.append({'key': key, 'pair': left+'-'+right, 'aa_equal': key in aa_equal,
                             'control': '/control/' in key, 'diffs': paths,
                             'class': 'FUNCTION_CHANGES' if any(p['mode'] == 'goto-functions' for p in paths) else 'SYMBOL_CHANGES'})
        return not paths
    # Finish the entire A/A census before inspecting any A/B differences.
    aa = collections.Counter()
    for key in sorted(texts):
        if compare(key, 'A1', 'A2'):
            aa_equal.add(key)
            aa[index[key]['kind']] += 1
    aa_diff = list(residual)
    controls = []
    for key in sorted(texts):
        for arm in ('A1', 'A2'):
            compare(key, arm, 'B1')
        if '/control/' in key:
            a, a2, b = (texts[key][arm] for arm in arms)
            gate = normalizer['check_control'](a[0], b[0])
            gate2 = normalizer['check_control'](a2[0], b[0])
            gate.update(key=key, aa_equal=key in aa_equal, a2b_valid=gate2['valid'],
                        function_text_equal=a[1] == a2[1] == b[1],
                        scope='exact wrapper symbol transition; all function content must match')
            controls.append(gate)
    expected_controls = {'final/control/array_typed_copy'} | {k for k in index if k.startswith(('linked/control/', 'symtab/control/'))}
    valid_control = (len(expected_controls) == 3 and {c['key'] for c in controls} == expected_controls
                     and all(c['valid'] and c['a2b_valid'] and c['aa_equal'] and c['function_text_equal'] for c in controls))
    perf = [r for r in residual if not r['control'] and r['pair'] != 'A1-A2']
    status = ('INVALID_CONTROL' if not valid_control else 'INCONCLUSIVE_AA' if aa_diff
              else 'OTHER_CHANGES' if perf else 'MODELS_EQUAL')
    result = {'schema': 'b3-t1b-r2-offline-v1', 'status': status, 'run_id': original['run_id'],
              'source_reported_lineage': {**lineage, 'ci_sha': original['ci_sha']},
              'artifact_index_sha256': sha(safe_read(root, 'INDEX.json')),
              'original_result_sha256': sha(safe_read(root, 'RESULT.json')),
              'normalizer_sha256': normalizer['SOURCE_SHA256'], 'driver_sha256': sha(Path(__file__).read_bytes()),
              'function_parser_sha256': sha(Path(__file__).with_name('function_dump_r2.py').read_bytes()),
              'source_reported_tool': original['tool'], 'symbol_policies': list(normalizer['POLICIES']),
              'function_policy': 'exact body text; only exact input-path status prefix split',
              'model_counts': dict(counts), 'AA_EQUAL': dict(aa), 'AA_DIFF': aa_diff,
              'B_PAIR_DIFFS': [r for r in residual if r['pair'] != 'A1-A2'],
              'B_DIFF': [r for r in residual if r['pair'] == 'A1-B1' and r['aa_equal']],
              'control': controls, 'control_valid': valid_control, 'records': records,
              'hash_checked_raw_dump_files': verified, 'hash_checked_raw_dump_bytes': total_bytes,
              'classification_order': 'all A1-A2, then A1-B1/A2-B1',
              'original_result_preserved': True, 'no_sat_or_formal_proof_or_harmlessness_credit': True}
    temporary = result_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    temporary.replace(result_path)
    print(json.dumps({'status': status, 'AA_EQUAL': dict(aa), 'control_valid': valid_control}), flush=True)
    return result
