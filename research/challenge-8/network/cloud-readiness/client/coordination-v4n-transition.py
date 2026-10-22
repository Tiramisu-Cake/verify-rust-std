#!/usr/bin/env python3
"""PREPARED_NOT_REGISTERED v3 -> v4 (four owners, cap 3) envelope transition.

Local file operations only; no Cloud calls. Not to be run without a separate
owner decision. `audit` checks that every stable owner's committed client uses
exactly this candidate coordinator; `migrate` rewrites the envelope version
under the shared lock while preserving every reservation byte-for-byte.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import coordination

OWNERS = coordination.V4_OWNERS
CLIENT_PATH = 'research/challenge-8/cloud-build/coordination.py'


def candidate_sha256():
    return hashlib.sha256((HERE / 'coordination.py').read_bytes()).hexdigest()


def audit(clients, acks):
    """clients/acks: owner -> worktree root / ACK JSON path, exactly V4_OWNERS."""
    if set(clients) != OWNERS or set(acks) != OWNERS:
        raise RuntimeError('Transition requires all four stable owners')
    expected = candidate_sha256()
    for owner in sorted(OWNERS):
        ack = json.loads(Path(acks[owner]).read_text())
        if ack.get('owner') != owner or ack.get('coordination_sha256') != expected:
            raise RuntimeError('ACK does not bind owner to the candidate coordinator: ' + owner)
        commit = ack.get('infra_commit')
        if not isinstance(commit, str) or len(commit) != 40:
            raise RuntimeError('ACK needs a full infra commit: ' + owner)
        committed = subprocess.check_output(
            ['git', '-C', str(clients[owner]), 'show', commit + ':' + CLIENT_PATH])
        local = (Path(clients[owner]) / CLIENT_PATH).read_bytes()
        if hashlib.sha256(committed).hexdigest() != expected or local != committed:
            raise RuntimeError('Client coordinator differs from the candidate: ' + owner)
    return expected


def migrate(clients, acks):
    expected = audit(clients, acks)
    with coordination.locked():
        if coordination.protocol() != (3, 3):
            raise RuntimeError('Transition starts only from the v3 envelope')
        records = coordination.reservations()
        for record in records:
            coordination.require_owner(4, record['owner'])
        coordination.write(coordination.COORDINATION / 'active.json',
                           {'schema_version': 4, 'max_active': 3, 'reservations': records})
        if coordination.protocol() != (4, 3) or coordination.reservations() != records:
            raise RuntimeError('Transition read-back mismatch')
    return {'coordination_sha256': expected,
            'active_tokens': [r['dispatch_token'] for r in records]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('audit',))
    p.add_argument('--client', action='append', default=[], help='owner=worktree')
    p.add_argument('--ack', action='append', default=[], help='owner=ack.json')
    a = p.parse_args()
    clients = dict(x.split('=', 1) for x in a.client)
    acks = dict(x.split('=', 1) for x in a.ack)
    # `migrate` is intentionally not exposed on the CLI in this prepared package.
    print(json.dumps({'coordination_sha256': audit(clients, acks)}))


if __name__ == '__main__':
    main()
