#!/usr/bin/env python3
"""Light saved-byte fixture preparation replay. No extractor or proof execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA = 'c05f8fe9f1df66f5a276884e5121bf318071968d5a1f761d3c7e7e8847cbbc54'
PREFIX = 'allprooflogs/checked-minimal-bridge/concrete-u64/'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('fresh own replay output required')
    assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE_SHA
    spec = importlib.util.spec_from_file_location('guard_pure_preparation', HERE/'guard-storage-controls.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # imports inert stdlib only; run() is never called
    with tarfile.open(args.archive) as archive:
        original = archive.extractfile(PREFIX+'cases/positive/original/lib.rs').read()
        baseline = archive.extractfile(PREFIX+'cases/positive/verified/lib.rs').read()
        manifest = json.loads(archive.extractfile(PREFIX+'metadata.json').read())['positive']
    # Reproduce the precise old refusal before checking the repaired preparation.
    legacy = baseline.replace(module.SIGNATURE, module.ALIGN+module.SIGNATURE, 1)
    legacy = legacy.replace(module.GUARD_INIT, module.GUARD_INIT+module.FACTS, 1)
    legacy = legacy.replace(module.FBC_LADDER, module.FBC_LADDER+module.POST, 1)
    failed = None
    for index, item in enumerate(manifest['ghost_fragments']):
        ghost = item.encode()
        if legacy.count(ghost) != 1:
            failed = {'index': index, 'count': legacy.count(ghost), 'bytes': len(ghost),
                      'sha256': module.sha(ghost)}
            break
        legacy = legacy.replace(ghost, b'', 1)
    assert failed == {'index': 4, 'count': 0, 'bytes': 2867,
                      'sha256': 'f5f0d175f1a138929c2725572b6d00b3db3c3a73630cf42e7bec21d4f996bf86'}
    args.output.mkdir(parents=True)
    rows = {}
    prepared = []
    for name, extra in [('qualified_live_guard', b''),
                        ('guard_source_overlap_false', module.FALSE),
                        ('guard_zero_extent_false', module.ZERO)]:
        verified, lines, receipt = module.prepare_qualified(name, original, baseline, manifest, extra)
        assert verified.count(module.POST) == verified.count(module.FACTS) == verified.count(module.ALIGN) == 1
        assert lines['separation'] < lines['post_fbc']
        prepared.append((name, verified, receipt))
    verified, close_line, target_line, receipt = module.prepare_full_fbc(original, baseline, manifest)
    assert target_line == close_line+1 and verified.count(module.ENTRY_FALSE) == 1
    prepared.append(('full_mutable_canonical_fbc_entry_false', verified, receipt))
    for name, verified, receipt in prepared:
        case = args.output/name
        for tree, data in [('original', original), ('verified', verified)]:
            (case/tree).mkdir(parents=True)
            (case/tree/'lib.rs').write_bytes(data)
        (case/'preparation.json').write_text(json.dumps(receipt, indent=2)+'\n')
        rows[name] = {k: receipt[k] for k in ('original_sha256','verified_sha256','lines',
                                             'runtime_exact_after_ghost_strip')}
    mutations = {}
    name, verified, receipt = prepared[0]
    fragments = [item.encode() for item in receipt['ghost_fragments']]
    for label, changed, runtime in [
            ('missing_post', verified.replace(module.POST,b'',1), original),
            ('duplicate_facts', verified+module.FACTS, original),
            ('runtime_changed', verified, original+b'\n')]:
        try:
            module._check_prepared(label, runtime, changed, fragments)
        except ValueError:
            mutations[label] = True
        else:
            raise AssertionError('mutation incorrectly accepted: '+label)
    changed_manifest = dict(manifest, ghost_fragments=[x for x in manifest['ghost_fragments']
                                if module.FBC_LADDER not in x.encode()])
    try:
        module.prepare_qualified('missing_manifest_carrier', original, baseline, changed_manifest)
    except ValueError:
        mutations['missing_manifest_carrier'] = True
    else:
        raise AssertionError('missing manifest carrier accepted')
    report = {'schema':'guard-preparation-saved-replay-v1','classification':'PASS_PREPARATION_ONLY',
              'source_build_id':'282324ae-a918-4bc6-b73b-e2861f2596e5',
              'source_proof_sha':'a287a0f2d1b12e3a209b8d69cb66516acdd53f50',
              'source_archive_sha256':ARCHIVE_SHA, 'legacy_first_refusal':failed,
              'prepared_cases':rows,'rejected_mutations':mutations,
              'helper_sha256':hashlib.sha256((HERE/'guard-storage-controls.py').read_bytes()).hexdigest(),
              'compiler_attempted':False,'proof_attempted':False,'accepted':False}
    (args.output/'replay.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'classification':report['classification'],'prepared':len(rows),
                      'mutation_rejections':len(mutations),'legacy_refusal_index':failed['index']}))


if __name__ == '__main__':
    main()
