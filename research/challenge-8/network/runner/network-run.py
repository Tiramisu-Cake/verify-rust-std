#!/usr/bin/env python3
"""Network control-matrix runner core (Cloud only; PREPARED, not wired to a lane).

Runs every control crate written by r4/swap-if-less-body.py or
w7/network-body.py (OUT_DIR with meta.json + <label>.rs) with a built VeriFast
under the P1 opt-in, and records raw observations. It never classifies a
proof result: every row is OBSERVED_UNCLASSIFIED or an explicit NOT_RUN/ERROR/TIMEOUT,
with the original exit code, timeout flag and output digests preserved.
Classification by message/location happens later through the Evidence Brief.
"""
import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

SCHEMA = 'network-run-v1'
NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def need(ok, why):
    if not ok:
        raise SystemExit('NETWORK RUN REFUSED: ' + why)


def provider_ok(environ):
    return (environ.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
            bool(environ.get('CLOUD_BUILD_ID')) and not environ.get('GITHUB_ACTIONS'))


def load_matrix(controls):
    """meta.json of one generator run -> (list of (label, path, crate_sha256, call_line), meta SHA256)."""
    raw = (controls / 'meta.json').read_bytes()
    meta = json.loads(raw)
    need(isinstance(meta, dict), 'meta.json must be an object')
    rows = []
    # R4 meta has 'controls' at top level; W7 meta has one entry per network.
    groups = {'': meta} if 'controls' in meta else meta
    for prefix, group in sorted(groups.items()):
        need(isinstance(group, dict) and isinstance(group.get('controls'), dict) and group['controls'],
             'meta group without controls: ' + (prefix or '<r4>'))
        default_line = group.get('crate_call_line')
        for label, row in sorted(group['controls'].items()):
            need(isinstance(row, dict) and isinstance(row.get('crate_sha256'), str) and
                 len(row['crate_sha256']) == 64, 'control row malformed: ' + label)
            line = row.get('crate_call_line', default_line)
            need(type(line) is int and line > 0, 'control call line missing: ' + label)
            name = f'{prefix}-{label}' if prefix else label
            need(NAME.fullmatch(name) is not None, 'control name is not a safe label: ' + repr(name))
            rows.append((name, controls / (name + '.rs'), row['crate_sha256'], line))
    need(len({r[0] for r in rows}) == len(rows), 'duplicate control names')
    return rows, sha(raw)  # identity of exactly the bytes parsed


def run_one(tool, name, path, crate_sha, call_line, work, evidence, timeout, base_env):
    row = {'control': name, 'expected_crate_sha256': crate_sha, 'call_line': call_line,
           'classification': 'NOT_RUN', 'exit': None, 'timed_out': False}
    if not path.is_file():
        row['reason'] = 'control crate missing'
        return row
    data = path.read_bytes()
    row['crate_sha256'] = sha(data)
    if row['crate_sha256'] != crate_sha:
        row['reason'] = 'control crate SHA256 differs from meta'
        return row
    fixture = work / name
    (fixture / 'verified').mkdir(parents=True)
    (fixture / 'verified' / 'lib.rs').write_bytes(data)
    env = dict(base_env, NETWORK_SWAP_IF_LESS_CALLBACK='1', NETWORK_SWAP_IF_LESS_CALL_LINE=str(call_line),
               NETWORK_SWAP_IF_LESS_SOURCE_SHA256=crate_sha)
    for key in ('SORT4_ACTUAL_BODY_C1_RECOVERY', 'SORT4_ACTUAL_BODY_C2_RECOVERY'):
        env.pop(key, None)
    argv = [str(tool / 'bin' / 'verifast'), '-rustc_args', '--edition 2021', '-verbose', '6', 'verified/lib.rs']
    row['argv'] = argv
    out_path, err_path = evidence / (name + '.stdout'), evidence / (name + '.stderr')
    with out_path.open('wb') as out, err_path.open('wb') as err:
        try:
            proc = subprocess.Popen(argv, cwd=fixture, env=env, stdout=out, stderr=err,
                                    start_new_session=True)
        except OSError as exc:
            row.update(classification='ERROR', reason=f'{type(exc).__name__}: {exc}')
            proc = None
        if proc is not None:
            try:
                row.update(exit=proc.wait(timeout=timeout), classification='OBSERVED_UNCLASSIFIED')
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)  # verifast and any rustc/exporter children
                except ProcessLookupError:
                    pass
                proc.wait()
                row.update(timed_out=True, classification='TIMEOUT', reason='timeout')
    row.update(stdout_sha256=sha(out_path.read_bytes()), stderr_sha256=sha(err_path.read_bytes()))
    return row


def main(argv=None, environ=None):
    environ = dict(os.environ if environ is None else environ)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool', type=Path, required=True)
    p.add_argument('--controls', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=180)
    a = p.parse_args(argv)
    need(provider_ok(environ), 'Cloud Build provider required')
    need(30 <= a.timeout <= 900, 'timeout must be 30..900 seconds')
    need(not a.work.exists() and not a.evidence.exists(), 'work/evidence directories must not exist')
    rows, meta_sha256 = load_matrix(a.controls)
    a.work.mkdir(parents=True)
    a.evidence.mkdir(parents=True)
    summary = {'schema': SCHEMA, 'proof_credit': False, 'complete': False,
               'meta_sha256': meta_sha256,
               'labels': [r[0] for r in rows], 'controls': []}

    def save():
        counts = {}
        for r in summary['controls']:
            counts[r['classification']] = counts.get(r['classification'], 0) + 1
        summary['counts'] = counts
        (a.evidence / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')

    save()  # an interrupted run leaves complete: false
    for r in rows:
        summary['controls'].append(run_one(a.tool, *r, a.work, a.evidence, a.timeout, environ))
        save()
    summary['complete'] = (len(summary['controls']) == len(rows) and
                           all(r['classification'] == 'OBSERVED_UNCLASSIFIED' and not r['timed_out']
                               for r in summary['controls']))
    save()
    print('NETWORK_RUN_SUMMARY', json.dumps({'controls': len(rows), 'complete': summary['complete'],
                                             'counts': summary['counts']}))
    return 0 if summary['complete'] else 2


if __name__ == '__main__':
    sys.exit(main())
