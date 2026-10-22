#!/usr/bin/env python3
"""Explicit, locked v3 -> v4 coordinator transition and its rollback.

v4 owners are select-sort4, merge and network (verifast refused), cap 3.
`audit` validates the three ACKs against the installed, committed and
published clients. `migrate` repeats the audit under the shared lock, requires
an idle coordinator (no reservation, no turn request, no ongoing project Build)
and atomically rewrites the envelope, reading it back by value. `rollback`
returns to v3 while no v4-only owner is recorded or requesting. The only Cloud
call is the read-only `builds list --ongoing` inventory inside `migrate`.
"""

import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import coordination

CONTROL = 'research/challenge-8/cloud-build/control.py'
COORDINATION = 'research/challenge-8/cloud-build/coordination.py'
# Network had no cloud-build client before adoption; its dispatcher baseline
# is the reviewed prepared client, installed byte-identically.
BASELINE_CONTROL = {'network': 'research/challenge-8/network/cloud-readiness/client/control.py'}
OWNERS = coordination.V4_OWNERS
GCLOUD = ['gcloud', '--configuration=smallsort-ci',
          '--account=smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com',
          '--project=smallsort-ci']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def mapping(values, label):
    result = {}
    for value in values:
        owner, separator, path = value.partition('=')
        if not separator or owner not in OWNERS or owner in result or not path:
            raise RuntimeError('Expected one ' + label + ' path for each v4 owner')
        result[owner] = Path(path).resolve()
    if set(result) != OWNERS:
        raise RuntimeError('Expected ' + label + ' paths for all three v4 owners')
    return result


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def full_sha(value):
    return isinstance(value, str) and len(value) == 40 and all(c in '0123456789abcdef' for c in value)


def check_dispatcher(source):
    tree = ast.parse(source)
    imports = any(isinstance(node, ast.Import) and
                  any(alias.name == 'coordination' for alias in node.names)
                  for node in tree.body)
    calls = {node.func.attr for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
             and isinstance(node.func.value, ast.Name) and node.func.value.id == 'coordination'}
    required = {'locked', 'reservations', 'require_capacity', 'reserve', 'update', 'clear', 'request'}
    if not imports or not required <= calls:
        raise RuntimeError('Dispatcher has not adopted the shared coordinator API')


def verify_clients(clients, acks):
    """Each owner: installed = adopted commit bytes, dispatcher unchanged, published."""
    if set(clients) != OWNERS or set(acks) != OWNERS:
        raise RuntimeError('Transition requires all three v4 owners')
    expected = digest((HERE / 'coordination.py').read_bytes())
    for owner in sorted(OWNERS):
        root = Path(clients[owner])
        ack = json.loads(Path(acks[owner]).read_text())
        source = (root / COORDINATION).read_bytes()
        control = (root / CONTROL).read_bytes()
        if (ack.get('owner') != owner or ack.get('coordination_sha256') != expected or
                digest(source) != expected or ack.get('control_sha256') != digest(control)):
            raise RuntimeError('Client acknowledgment or installed source differs: ' + owner)
        baseline, adopted, branch = ack.get('baseline_control_commit'), ack.get('infra_commit'), ack.get('branch')
        if not full_sha(baseline) or not full_sha(adopted) or baseline == adopted:
            raise RuntimeError('ACK needs distinct full baseline and infra commits: ' + owner)
        if not isinstance(branch, str) or not branch:
            raise RuntimeError('ACK needs the published branch: ' + owner)
        if git(root, 'symbolic-ref', '--short', 'HEAD').decode().strip() != branch:
            raise RuntimeError('Client worktree is not on the acknowledged branch: ' + owner)
        if subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', baseline, adopted],
                          check=False).returncode != 0:
            raise RuntimeError('Baseline is not an ancestor of adoption: ' + owner)
        changed = set(git(root, 'diff', '--name-only', baseline, adopted).decode().split())
        if not changed <= {COORDINATION, CONTROL}:
            raise RuntimeError('Adoption changed paths beyond the client: ' + owner)
        if (git(root, 'show', adopted + ':' + COORDINATION) != source or
                git(root, 'show', adopted + ':' + CONTROL) != control or
                git(root, 'show', baseline + ':' + BASELINE_CONTROL.get(owner, CONTROL)) != control):
            raise RuntimeError('Installed client differs from adoption or dispatcher changed: ' + owner)
        check_dispatcher(control)
        remote = git(root, 'ls-remote', 'origin', 'refs/heads/' + branch).decode().split()
        if (len(remote) != 2 or not full_sha(remote[0]) or
                subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', adopted, remote[0]],
                               check=False).returncode != 0):
            raise RuntimeError('Adoption commit is not published on the branch: ' + owner)
    return expected


def ongoing_builds():
    output = subprocess.check_output(GCLOUD + ['builds', 'list', '--region=global', '--ongoing', '--format=json'])
    builds = json.loads(output or b'[]')
    if not isinstance(builds, list):
        raise RuntimeError('Unexpected Cloud Build inventory')
    return builds


def require_idle(list_ongoing):
    """Caller holds locked(): no reservation, request or ongoing project Build."""
    if coordination.reservations():
        raise RuntimeError('Coordinator not idle: reservation or unresolved submit present')
    if any((coordination.COORDINATION / 'requests').glob('*.json')):
        raise RuntimeError('Coordinator not idle: turn request present')
    ongoing = list_ongoing()
    if ongoing:
        raise RuntimeError('Coordinator not idle: ongoing Cloud Build present')


def envelope_path():
    return coordination.COORDINATION / 'active.json'


def migrate(clients, acks, list_ongoing=ongoing_builds):
    # The same flock spans audit, idle check and the atomic envelope replacement.
    with coordination.locked():
        source_hash = verify_clients(clients, acks)
        path = envelope_path()
        if not path.exists() or 'schema_version' not in coordination.read(path):
            raise RuntimeError('Transition requires an existing v3 envelope')
        if coordination.protocol() != (3, 3):
            raise RuntimeError('Transition starts only from the v3 envelope')
        before = coordination.read(path)
        require_idle(list_ongoing)
        records = coordination.reservations()
        coordination.write(path, {'schema_version': 4, 'max_active': 3, 'reservations': records})
        if coordination.protocol() != (4, 3) or coordination.reservations() != records:
            raise RuntimeError('Transition read-back mismatch')
        return {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'coordination_sha256': source_hash, 'before': before,
                'after': coordination.read(path)}


def rollback():
    """v4 -> v3 with the same records; refused once a v4-only owner appears."""
    with coordination.locked():
        path = envelope_path()
        if coordination.protocol() != (4, 3):
            raise RuntimeError('Rollback starts only from the v4 envelope')
        before = coordination.read(path)
        records = coordination.reservations()
        if any(r['owner'] not in coordination.V3_OWNERS for r in records):
            raise RuntimeError('Rollback refused: v4-only owner reservation present')
        for request in (coordination.COORDINATION / 'requests').glob('*.json'):
            if coordination.read(request).get('owner') not in coordination.V3_OWNERS:
                raise RuntimeError('Rollback refused: v4-only owner request present')
        coordination.write(path, {'schema_version': 3, 'max_active': 3, 'reservations': records})
        if coordination.protocol() != (3, 3) or coordination.reservations() != records:
            raise RuntimeError('Rollback read-back mismatch')
        return {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'before': before, 'after': coordination.read(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('audit', 'migrate', 'rollback'))
    parser.add_argument('--client', action='append', default=[], metavar='OWNER=CHECKOUT')
    parser.add_argument('--ack', action='append', default=[], metavar='OWNER=JSON')
    args = parser.parse_args()
    if args.command == 'rollback':
        result = rollback()
    else:
        clients, acks = mapping(args.client, 'client'), mapping(args.ack, 'ack')
        if args.command == 'audit':
            result = {'coordination_sha256': verify_clients(clients, acks)}
        else:
            result = migrate(clients, acks)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
