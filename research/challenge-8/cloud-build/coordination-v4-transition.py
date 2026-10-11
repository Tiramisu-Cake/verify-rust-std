#!/usr/bin/env python3
"""Read-only client ACKs and explicit locked v3-to-v4 migration with API inventory."""

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

import coordination


CONTROL = 'research/challenge-8/cloud-build/control.py'
COORDINATION = 'research/challenge-8/cloud-build/coordination.py'
OWNERS = coordination.V4_OWNERS
PROC_ROOT = Path('/proc')
GIT_TIMEOUT_SECONDS = 5
API_TIMEOUT_SECONDS = 10
REVIEW_STATUS = 'OWNER_REVIEWED_BASELINE'
CLOUD_IDENTITY = ('smallsort-ci',
                  'smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com',
                  'smallsort-ci')


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
        raise RuntimeError('Expected ' + label + ' paths for all four stable owners')
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


def exact_commit(value, label):
    if not isinstance(value, str) or len(value) != 40 or any(c not in '0123456789abcdef' for c in value):
        raise RuntimeError('Missing exact ' + label + ' commit')
    return value


def project_origin(remote):
    path = 'Tiramisu-Cake/verify-rust-std'
    if remote in ('git@github.com:' + path, 'git@github.com:' + path + '.git'):
        return True
    try:
        parsed = urlsplit(remote)
        return (parsed.scheme in ('https', 'ssh') and parsed.hostname == 'github.com' and
                parsed.port is None and parsed.query == parsed.fragment == '' and
                parsed.path in ('/' + path, '/' + path + '.git') and
                parsed.username == ('git' if parsed.scheme == 'ssh' else None) and
                parsed.password is None)
    except ValueError:
        return False


def audit_dispatchers():
    """Fail closed if any project dispatcher could race adoption or migration.

    Scan all visible processes, including clients outside the four mappings.
    A vanished PID is harmless; inability to inspect a live PID is not.
    """
    try:
        processes = list(PROC_ROOT.iterdir())
    except OSError as error:
        raise RuntimeError('Cannot audit running dispatcher processes') from error
    for process in processes:
        if not process.name.isdecimal():
            continue
        try:
            raw = (process / 'cmdline').read_bytes()
        except FileNotFoundError as error:
            if not process.exists():
                continue
            raise RuntimeError('Cannot audit live process ' + process.name) from error
        except OSError as error:
            raise RuntimeError('Cannot audit live process ' + process.name) from error
        if not raw:
            continue  # Kernel task or a process that has already exited.
        args = [os.fsdecode(part) for part in raw.split(b'\0') if part]
        if any(re.search(r'(?<![A-Za-z0-9_.-])control\.py(?![A-Za-z0-9_.-])', arg)
               for arg in args):
            raise RuntimeError('Dispatcher command is running (PID ' + process.name + ')')


def check_client(owner, root, ack, expected, *, check_remote=True):
    """Read checkout and remote refs; never alter a client or issue an ACK for it."""
    if owner not in OWNERS or ack.get('owner') != owner:
        raise RuntimeError('Client acknowledgment has wrong owner: ' + owner)
    source = (root / COORDINATION).read_bytes()
    control = (root / CONTROL).read_bytes()
    if (ack.get('coordination_sha256') != expected or digest(source) != expected or
            ack.get('control_sha256') != digest(control)):
        raise RuntimeError('Client acknowledgment or installed source differs: ' + owner)
    baseline = exact_commit(ack.get('baseline_control_commit'), 'baseline control')
    adopted = exact_commit(ack.get('infra_commit'), 'adopted infrastructure')
    review = ack.get('review_receipt')
    if (not isinstance(review, dict) or review.get('owner') != owner or
            review.get('review_status') != REVIEW_STATUS or
            review.get('baseline_control_commit') != baseline or
            review.get('control_sha256') != digest(control)):
        raise RuntimeError('Missing matching owner-reviewed baseline receipt: ' + owner)
    if baseline == adopted:
        raise RuntimeError('Phase baseline must precede dispatcher adoption: ' + owner)
    if subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor',
                       baseline, adopted], check=False, timeout=GIT_TIMEOUT_SECONDS).returncode != 0:
        raise RuntimeError('Phase baseline is not an ancestor of adoption: ' + owner)
    def committed(commit, relative):
        return subprocess.check_output(['git', '-C', str(root), 'show', commit + ':' + relative],
                                       timeout=GIT_TIMEOUT_SECONDS)
    if committed(adopted, COORDINATION) != source or committed(adopted, CONTROL) != control:
        raise RuntimeError('Installed dispatcher differs from adopted infrastructure commit: ' + owner)
    if committed(baseline, CONTROL) != control:
        raise RuntimeError('Dispatcher differs from owner-reviewed baseline: ' + owner)
    phase_projection(control)  # Sanity check only; human baseline review is separate.
    check_dispatcher(control)
    published_ref = ack.get('published_ref')
    if not isinstance(published_ref, str) or not published_ref.startswith('refs/heads/') or any(
            c.isspace() for c in published_ref):
        raise RuntimeError('Missing exact published branch ref: ' + owner)
    if check_remote:
        remote = subprocess.check_output(['git', '-C', str(root), 'remote', 'get-url', 'origin'],
                                         text=True, timeout=GIT_TIMEOUT_SECONDS).strip()
        if not project_origin(remote):
            raise RuntimeError('Client origin is not the project fork: ' + owner)
        remote_line = subprocess.check_output(['git', '-C', str(root), 'ls-remote', '--exit-code',
                                               'origin', published_ref], text=True,
                                              timeout=GIT_TIMEOUT_SECONDS).strip()
        if remote_line != adopted + '\t' + published_ref:
            raise RuntimeError('Infrastructure commit is not the published branch tip: ' + owner)
    if (root / COORDINATION).read_bytes() != source or (root / CONTROL).read_bytes() != control:
        raise RuntimeError('Client source changed during acknowledgment: ' + owner)


def make_ack(owner, root, baseline, adopted, published_ref, review_receipt):
    """Return an ACK for the caller's own checkout; printing it is read-only."""
    audit_dispatchers()
    expected = digest(Path(coordination.__file__).read_bytes())
    ack = {'owner': owner, 'coordination_sha256': digest((root / COORDINATION).read_bytes()),
           'control_sha256': digest((root / CONTROL).read_bytes()),
           'infra_commit': adopted, 'baseline_control_commit': baseline,
           'published_ref': published_ref, 'review_receipt': review_receipt}
    check_client(owner, root, ack, expected)
    audit_dispatchers()
    if digest(Path(coordination.__file__).read_bytes()) != expected:
        raise RuntimeError('Coordinator source changed during acknowledgment')
    return ack


def verify_clients(clients, acknowledgments, *, check_remote=True, ack_bytes=None):
    source_path = Path(coordination.__file__)
    expected = digest(source_path.read_bytes())
    for owner in sorted(OWNERS):
        raw_ack = ack_bytes[owner] if ack_bytes is not None else acknowledgments[owner].read_bytes()
        check_client(owner, clients[owner], json.loads(raw_ack),
                     expected, check_remote=check_remote)
    if digest(source_path.read_bytes()) != expected:
        raise RuntimeError('Coordinator source changed during client validation')
    return expected


def read_ongoing(configuration, account, project):
    """Read current project Build inventory using explicit Cloud SDK identity."""
    validate_cloud_identity(configuration, account, project)
    command = ['gcloud', '--configuration=' + configuration, '--account=' + account,
               '--project=' + project, 'builds', 'list', '--ongoing', '--region=global',
               '--format=json']
    data = json.loads(subprocess.check_output(command, text=True, timeout=API_TIMEOUT_SECONDS))
    if not isinstance(data, list):
        raise RuntimeError('Invalid ongoing Cloud Build inventory')
    return data


def validate_cloud_identity(configuration, account, project):
    if (configuration, account, project) != CLOUD_IDENTITY:
        raise RuntimeError('Cloud inventory identity differs from canonical project account')


def migrate(clients, acknowledgments, *, configuration, account, project):
    validate_cloud_identity(configuration, account, project)
    audit_dispatchers()
    # Publication needs remote reads. Do those before taking the shared lock,
    # then revalidate all installed and committed bytes under the lock.
    preflight_acks = {owner: acknowledgments[owner].read_bytes() for owner in OWNERS}
    preflight_hash = verify_clients(clients, acknowledgments, ack_bytes=preflight_acks)
    with coordination.locked():
        audit_dispatchers()
        if any(acknowledgments[owner].read_bytes() != preflight_acks[owner] for owner in OWNERS):
            raise RuntimeError('Client acknowledgment changed after publication preflight')
        source_hash = verify_clients(clients, acknowledgments, check_remote=False,
                                     ack_bytes=preflight_acks)
        if source_hash != preflight_hash:
            raise RuntimeError('Coordinator source changed after publication preflight')
        path = coordination.COORDINATION / 'active.json'
        if not path.exists():
            raise RuntimeError('No v3 envelope to migrate')
        version, capacity = coordination.protocol()
        envelope = coordination.read(path)
        if (version, capacity) != (3, 3) or 'schema_version' not in envelope:
            raise RuntimeError('Migration requires an existing v3 envelope')
        records = coordination.reservations()
        coordination.validate_records(records, 4, require_full=True)
        ongoing = read_ongoing(configuration, account, project)
        occupied = coordination.occupied_slots(records, ongoing)
        if occupied > 4:
            raise RuntimeError('Cloud Build inventory exceeds v4 capacity')
        audit_dispatchers()
        if digest(Path(coordination.__file__).read_bytes()) != source_hash:
            raise RuntimeError('Coordinator source changed during migration')
        # Preserve every other top-level and reservation field, including
        # timestamps and receipts, in the one atomic replacement.
        updated = {**envelope, 'schema_version': 4, 'max_active': 4}
        coordination.write(path, updated)
        if coordination.read(path) != updated or coordination.reservations() != records:
            raise RuntimeError('Migration readback differs from v3 records')
        return {'schema_version': 4, 'max_active': 4,
                'active_tokens': [r['dispatch_token'] for r in records],
                'occupied_slots': occupied,
                'coordination_sha256': source_hash}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('audit', help='read-only check that no dispatcher command is running')
    ack = commands.add_parser('ack', help='print a verified ACK for one installed client')
    ack.add_argument('--owner', required=True, choices=sorted(OWNERS))
    ack.add_argument('--client', required=True, type=Path)
    ack.add_argument('--baseline-control-commit', required=True)
    ack.add_argument('--infra-commit', required=True)
    ack.add_argument('--published-ref', required=True)
    ack.add_argument('--review-receipt', required=True, type=Path,
                     help='separate owner-authored baseline review JSON')
    migration = commands.add_parser('migrate', help='validate four ACKs and atomically migrate v3 to v4')
    migration.add_argument('--client', action='append', required=True, metavar='OWNER=CHECKOUT')
    migration.add_argument('--ack', action='append', required=True, metavar='OWNER=JSON')
    migration.add_argument('--configuration', required=True)
    migration.add_argument('--account', required=True)
    migration.add_argument('--project', required=True)
    args = parser.parse_args()
    if args.command == 'audit':
        audit_dispatchers()
        result = {'dispatcher_commands': 'none'}
    elif args.command == 'ack':
        result = make_ack(args.owner, args.client.resolve(), args.baseline_control_commit,
                          args.infra_commit, args.published_ref,
                          json.loads(args.review_receipt.read_text()))
    else:
        result = migrate(mapping(args.client, 'client'), mapping(args.ack, 'ack'),
                         configuration=args.configuration, account=args.account, project=args.project)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
