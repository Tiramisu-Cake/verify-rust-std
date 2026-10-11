#!/usr/bin/env python3
"""Explicit, locked v2-to-v3 coordinator migration. No Cloud API calls."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess

import coordination


CONTROL = 'research/challenge-8/cloud-build/control.py'
COORDINATION = 'research/challenge-8/cloud-build/coordination.py'
OWNERS = coordination.V3_OWNERS


def digest(data):
    return hashlib.sha256(data).hexdigest()


def mapping(values, label):
    result = {}
    for value in values:
        owner, separator, path = value.partition('=')
        if not separator or owner not in OWNERS or owner in result or not path:
            raise RuntimeError('Expected one ' + label + ' path for each stable owner')
        result[owner] = Path(path).resolve()
    if set(result) != OWNERS:
        raise RuntimeError('Expected ' + label + ' paths for all three stable owners')
    return result


def phase_projection(source):
    """Compare phase registrations and their named constants across adoption."""
    tree = ast.parse(source)
    selected = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            names = [target.id for target in getattr(node, 'targets', [getattr(node, 'target', None)])
                     if isinstance(target, ast.Name)]
            if any(any(part in name for part in ('PHASE', 'DEADLINE', 'LANES', 'START'))
                   for name in names):
                selected.append(ast.dump(node, include_attributes=False))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'authorized_phase':
            selected.append(ast.dump(node, include_attributes=False))
    if not any('authorized_phase' in item for item in selected):
        raise RuntimeError('Dispatcher has no authorized_phase registration')
    return selected


def check_dispatcher(source):
    tree = ast.parse(source)
    imports = any(isinstance(node, ast.Import) and
                  any(alias.name == 'coordination' for alias in node.names)
                  for node in tree.body)
    calls = {node.func.attr for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
             and isinstance(node.func.value, ast.Name) and node.func.value.id == 'coordination'}
    required = {'locked', 'reservations', 'require_capacity', 'reserve', 'update', 'clear'}
    if not imports or not required <= calls:
        raise RuntimeError('Dispatcher has not adopted the shared coordinator API')


def verify_clients(clients, acknowledgments):
    expected = digest(Path(coordination.__file__).read_bytes())
    for owner in sorted(OWNERS):
        root = clients[owner]
        ack = json.loads(acknowledgments[owner].read_text())
        source = (root / COORDINATION).read_bytes()
        control = (root / CONTROL).read_bytes()
        if (ack.get('owner') != owner or ack.get('coordination_sha256') != expected or
                digest(source) != expected or ack.get('control_sha256') != digest(control)):
            raise RuntimeError('Client acknowledgment or installed source differs: ' + owner)
        baseline = ack.get('baseline_control_commit')
        adopted = ack.get('infra_commit')
        for label, commit in (('baseline control', baseline), ('adopted infrastructure', adopted)):
            if not isinstance(commit, str) or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
                raise RuntimeError('Missing exact ' + label + ' commit: ' + owner)
        if baseline == adopted:
            raise RuntimeError('Phase baseline must precede dispatcher adoption: ' + owner)
        if subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor',
                           baseline, adopted], check=False).returncode != 0:
            raise RuntimeError('Phase baseline is not an ancestor of adoption: ' + owner)
        def committed(commit, relative):
            return subprocess.check_output(['git', '-C', str(root), 'show',
                                            commit + ':' + relative])
        if committed(adopted, COORDINATION) != source or committed(adopted, CONTROL) != control:
            raise RuntimeError('Installed dispatcher differs from adopted infrastructure commit: ' + owner)
        original = committed(baseline, CONTROL)
        if phase_projection(original) != phase_projection(control):
            raise RuntimeError('Phase registration changed during dispatcher adoption: ' + owner)
        check_dispatcher(control)
    return expected


def migrate(clients, acknowledgments):
    # The same flock spans validation and the atomic envelope replacement.
    with coordination.locked():
        source_hash = verify_clients(clients, acknowledgments)
        path = coordination.COORDINATION / 'active.json'
        if not path.exists():
            raise RuntimeError('No v2 envelope to migrate; initialize v2 first')
        version, capacity = coordination.protocol()
        if (version, capacity) != (2, 2) or 'schema_version' not in coordination.read(path):
            raise RuntimeError('Migration requires an existing v2 envelope')
        records = coordination.reservations()
        if any(record['owner'] not in OWNERS for record in records):
            raise RuntimeError('Active reservation has an unknown v3 owner')
        # Re-read immediately before the single atomic replacement; all token,
        # Build ID and receipt relationships remain the same records.
        coordination.write(path, {'schema_version': 3, 'max_active': 3,
                                  'reservations': records})
        if coordination.reservations() != records:
            raise RuntimeError('Migration readback differs from v2 records')
        return {'schema_version': 3, 'max_active': 3,
                'active_tokens': [r['dispatch_token'] for r in records],
                'coordination_sha256': source_hash}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', action='append', required=True, metavar='OWNER=CHECKOUT')
    parser.add_argument('--ack', action='append', required=True, metavar='OWNER=JSON')
    args = parser.parse_args()
    print(json.dumps(migrate(mapping(args.client, 'client'), mapping(args.ack, 'ack')), indent=2))


if __name__ == '__main__':
    main()
