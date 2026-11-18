"""Bounded synthetic reproduction; no native tool, compiler, CI or raw evidence."""
import gzip
import hashlib
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

CONTROL = Path('/root/kani-ch8-s2-r5-package-w13')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(CONTROL / 'ch8-s1-control'))
import runner as r
import r5_campaign as c
import r5_profile as p
import pack_evidence
from test_r5 import synthetic_supervision
import test_runner as fixtures

assert r.git(CONTROL, 'rev-parse', 'HEAD') == '4e97d370aba4adc480fcc3701b111d02658aa94d'
request = r.load_request()
with tempfile.TemporaryDirectory(prefix='review14-prefix-') as temp:
    root = Path(temp) / 'worker'
    uploaded = Path(temp) / 'uploaded'
    rid = p.ORDER[0]
    row = c.group(request, rid)['rows'][0]
    std, tool = Path(temp) / 'std', Path(temp) / 'tool'
    fingerprints = {'required_hashes_present': True, 'binaries': {
        name: {'path': '/' + name, 'sha256': 'a' * 64}
        for name in ('kani_driver', 'kani_compiler', 'cbmc')}}
    source = {**c.identity(request), 'changed_file_sha256': request['changed_file_sha256']}

    def synthetic_execute(argv, cwd, out, timeout, **kw):
        stock = fixtures.batch_export([row], request['source_bindings'])
        kw['export_path'].write_text(json.dumps(stock))
        kw['compile_monitor'].poll(1, {})
        fixtures.feed_regular(kw['rich_parser'], stock)
        target = Path(kw['env']['CARGO_TARGET_DIR'])
        (target / 'core.kani-metadata.json').write_text(json.dumps({
            'proof_harnesses': [{'pretty_name': row['selector'], 'crate_name': 'core'}]}))
        return {'original_exit_code': 1, 'elapsed_seconds': 2,
                'stdout_bytes': 1, 'stderr_bytes': 0, 'child_shutdown_verified': True,
                'process_identity': {'pid': 2, 'pgid': 2, 'start_ticks': 22}}

    # Real control pipeline with the external native execution replaced by a
    # bounded synthetic export. In particular, _run_group itself creates logs.
    with mock.patch.object(r, 'verify_source', return_value=source), \
            mock.patch.object(r, 'binary_fingerprints', return_value=fingerprints), \
            mock.patch.object(r, 'group_memory_budget', return_value={'group_cap_kib': 12 * 1024 * 1024}), \
            mock.patch.object(r, 'execute', side_effect=synthetic_execute):
        _, fatal = r._run_group(std, tool, root, request, c.group(request, rid),
                               time.monotonic() + 720, isolated_limits={
                                   'stdout_bytes': 10000, 'stderr_bytes': 1000, 'export_bytes': 100000})
    assert fatal is None
    c.root_outcome(root, request, rid, synthetic_supervision())
    c.finalize(root, request, 'synthetic later global failure')
    local = c.collect([root], request)
    local_row = next(row for row in local['rows'] if row['id'] == rid)
    assert local_row['outcome'] == 'RECORDED'
    before = c.sealed(root)
    local_receipt_hash = r.sha256(root / rid / 'receipt.json')
    packed = pack_evidence.pack(root)
    # Inspect only this locally generated synthetic structured test artifact.
    artifact = json.loads(gzip.decompress((root / pack_evidence.NAME).read_bytes()))
    sealed_paths = list(before[rid]['files'])
    omitted = [name for name in sealed_paths if name not in artifact['files']]
    uploaded.mkdir()
    shutil.copyfile(root / pack_evidence.NAME, uploaded / pack_evidence.NAME)
    import collect
    failure = None
    try:
        c.sealed(uploaded, collect.read_bytes, [rid])
    except Exception as exc:
        failure = {'type': type(exc).__name__, 'message': str(exc)}
    collector_failure = None
    try:
        c.collect([uploaded], request)
    except Exception as exc:
        collector_failure = {'type': type(exc).__name__, 'message': str(exc)}
    assert packed['state'] == 'PACKAGED'
    assert artifact['files'][rid + '/receipt.json']['sha256'] == local_receipt_hash
    assert 'groups/r5-' + rid + '/stderr.log' in omitted
    assert 'groups/r5-' + rid + '/stdout.log' in omitted
    assert failure and failure['type'] == 'KeyError'
    assert collector_failure and collector_failure['type'] == 'KeyError'
    result = {
        'state': 'REPRODUCED',
        'control_sha': r.git(CONTROL, 'rev-parse', 'HEAD'),
        'case': 'completed prefix sealed locally, later failure, uploaded artifact only',
        'root': rid,
        'local_seal_verified': True,
        'local_collector_outcome': local_row['outcome'],
        'local_expected_match': c.read(root / rid / 'receipt.json')['r5_expected_match'],
        'packed_state': packed['state'],
        'original_receipt_retained_exactly': True,
        'sealed_paths_missing_from_uploaded_artifact': omitted,
        'archive_only_seal_verification': failure,
        'archive_only_r5_collect': collector_failure,
        'scope': 'synthetic fixture; not native outcome or proof evidence',
        'compiler_CI_external_actions': 0,
    }
    (OUT / 'PRIOR-4E97-UPLOADED-PREFIX-REPRO.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
