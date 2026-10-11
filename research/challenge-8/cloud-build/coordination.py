"""Cross-worktree Cloud Build reservation and atomic accounting (VPS only)."""

import contextlib
import fcntl
import json
import os
from pathlib import Path
import tempfile
import datetime


COORDINATION = Path('/root/smallsort-ci-coordination')
MAX_ACTIVE = 2
SCHEMA_VERSION = 2
PROTOCOLS = {2: 2, 3: 3}
V3_OWNERS = frozenset(('select-sort4', 'merge', 'verifast'))


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    write_bytes(path, (json.dumps(value, indent=2) + '\n').encode())


def write_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def locked():
    COORDINATION.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (COORDINATION / 'lock').open('a+b') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def protocol():
    """Return the active envelope version and capacity; caller holds locked().

    Absence and legacy single-record state remain v2 on their first mutation.
    Only the explicit migration helper may change an existing v2 envelope to v3.
    """
    path = COORDINATION / 'active.json'
    if not path.exists():
        return SCHEMA_VERSION, MAX_ACTIVE
    data = read(path)
    if not isinstance(data, dict):
        raise RuntimeError('Invalid Cloud Build coordination state')
    if 'schema_version' not in data:
        return SCHEMA_VERSION, MAX_ACTIVE
    version = data['schema_version']
    if type(version) is not int or version not in PROTOCOLS or data.get('max_active') != PROTOCOLS[version]:
        raise RuntimeError('Unsupported Cloud Build coordination protocol')
    return version, PROTOCOLS[version]


def ledger_key(value):
    if not isinstance(value, (str, Path)) or not Path(value).is_absolute():
        raise RuntimeError('Reservation ledger must be absolute')
    return str(Path(value).resolve())


def reservations():
    """Read legacy single-slot, v2 or v3 state; caller holds locked().

    Keep the same file and lock. A v1 client sees the v2 envelope as occupied
    and cannot reconcile its missing record fields, so it fails closed.
    Never unlink the envelope, even when the last slot is released.
    """
    path = COORDINATION / 'active.json'
    if not path.exists():
        return []
    data = read(path)
    if not isinstance(data, dict):
        raise RuntimeError('Invalid Cloud Build coordination state')
    version, capacity = protocol()
    if 'schema_version' in data:
        records = data.get('reservations')
    else:
        records = [data]
    if not isinstance(records, list) or len(records) > capacity:
        raise RuntimeError('Invalid Cloud Build reservation count')
    tokens, owners, ledgers = set(), set(), set()
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError('Invalid Cloud Build reservation')
        for key, seen in (('dispatch_token', tokens), ('owner', owners), ('ledger', ledgers)):
            value = record.get(key)
            if not isinstance(value, str) or not value:
                raise RuntimeError('Missing or duplicate reservation ' + key)
            if key == 'ledger':
                value = ledger_key(value)
            if value in seen:
                raise RuntimeError('Missing or duplicate reservation ' + key)
            seen.add(value)
        if version == 3 and record['owner'] not in V3_OWNERS:
            raise RuntimeError('Unsupported v3 Cloud Build owner')
    return records


def active(owner=None):
    records = reservations()
    if owner is not None:
        records = [record for record in records if record['owner'] == owner]
    if len(records) > 1:
        raise RuntimeError('Select an owner when multiple builds are active')
    return records[0] if records else None


def save_reservations(records):
    version, capacity = protocol()
    if len(records) > capacity:
        raise RuntimeError('Cloud Build reservation capacity exceeded')
    if version == 3 and any(r['owner'] not in V3_OWNERS for r in records):
        raise RuntimeError('Unsupported v3 Cloud Build owner')
    write(COORDINATION / 'active.json', {
        'schema_version': version, 'max_active': capacity,
        'reservations': records,
    })


def require_capacity(owner, ledger, ongoing=()):
    """Count reservations plus untracked API builds, without double counting.

    An unresolved submission consumes its slot. A build newly visible by its
    token is the same slot; multiple matches or conflicting IDs fail closed.
    All project builds count, including ones submitted outside this client.
    """
    records = reservations()
    requested_ledger = ledger_key(ledger)
    if any(r['owner'] == owner or ledger_key(r['ledger']) == requested_ledger for r in records):
        raise RuntimeError('Owner or ledger already has an active or unresolved build')
    ids, matched_tokens = set(), set()
    occupied = len(records)
    for build in ongoing:
        build_id = build.get('id')
        if not isinstance(build_id, str) or not build_id or build_id in ids:
            raise RuntimeError('Invalid or duplicate ongoing Build ID')
        ids.add(build_id)
        matches = [r for r in records if r.get('build_id') == build_id or
                   r['dispatch_token'] in build.get('tags', [])]
        if len(matches) > 1:
            raise RuntimeError('Ongoing build matches multiple reservations')
        if matches:
            record = matches[0]
            token = record['dispatch_token']
            if (token in matched_tokens or token not in build.get('tags', []) or
                    record.get('build_id') not in (None, build_id)):
                raise RuntimeError('Ongoing build conflicts with reserved token or Build ID')
            matched_tokens.add(token)
        else:
            occupied += 1
    _, capacity = protocol()
    if occupied >= capacity:
        raise RuntimeError(('Both' if capacity == 2 else 'All') +
                           ' Cloud Build slots are occupied; monitor/reconcile first')
    if capacity == 3 and owner not in V3_OWNERS:
        raise RuntimeError('Unsupported v3 Cloud Build owner')


def reserve(record):
    # The caller also checks live API inventory under this same lock.
    require_capacity(record['owner'], record['ledger'])
    records = reservations()
    if any(r['dispatch_token'] == record['dispatch_token'] for r in records):
        raise RuntimeError('Dispatch token is already reserved')
    save_reservations(records + [record])


def update(record):
    records = reservations()
    index = next((i for i, r in enumerate(records)
                  if r['dispatch_token'] == record['dispatch_token']), None)
    if index is None:
        raise RuntimeError('Global Cloud Build reservation disappeared')
    current = records[index]
    if any(current.get(k) != record.get(k) for k in ('owner', 'phase_id', 'ledger', 'state_dir')):
        raise RuntimeError('Global Cloud Build reservation identity changed')
    if current.get('build_id') is not None and current['build_id'] != record.get('build_id'):
        raise RuntimeError('Global Cloud Build reservation Build ID changed')
    records[index] = record
    save_reservations(records)


def clear(token):
    records = reservations()
    if not any(r['dispatch_token'] == token for r in records):
        raise RuntimeError('Global Cloud Build reservation changed; refusing to clear')
    save_reservations([r for r in records if r['dispatch_token'] != token])


def request(owner, phase_id, ledger, deadline_utc):
    """Register a persistent turn request; caller holds locked()."""
    write(COORDINATION / 'requests' / (owner + '.json'), {
        'owner': owner, 'phase_id': phase_id, 'ledger': str(ledger),
        'deadline_utc': deadline_utc,
        'requested_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })


def withdraw(owner):
    path = COORDINATION / 'requests' / (owner + '.json')
    if path.exists():
        path.unlink()


def pending_others(owner):
    now = datetime.datetime.now(datetime.timezone.utc)
    others = []
    for path in (COORDINATION / 'requests').glob('*.json'):
        data = read(path)
        if data.get('owner') == owner:
            continue
        deadline = datetime.datetime.fromisoformat(data['deadline_utc'].replace('Z', '+00:00'))
        if now < deadline:
            others.append(data)
    return others


def last_owner():
    path = COORDINATION / 'last-owner.json'
    return read(path).get('owner') if path.exists() else None


def submitted(owner, token):
    turn_path = COORDINATION / 'last-owner.json'
    previous = read(turn_path) if turn_path.exists() else None
    if previous is None or previous.get('dispatch_token') != token:
        previous = {
            'owner': owner, 'dispatch_token': token,
            'submitted_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        write(turn_path, previous)
    request_path = COORDINATION / 'requests' / (owner + '.json')
    if request_path.exists():
        requested = read(request_path)
        if requested.get('requested_utc', '') <= previous['submitted_utc']:
            withdraw(owner)
