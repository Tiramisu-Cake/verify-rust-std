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
PROTOCOLS = {2: 2, 3: 3, 4: 4}
V3_OWNERS = frozenset(('select-sort4', 'merge', 'verifast'))
V4_OWNERS = frozenset((*V3_OWNERS, 'refinedrust-feasibility'))


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
    Only an explicit migration helper may change an existing envelope version.
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
    if (type(version) is not int or version not in PROTOCOLS or
            type(data.get('max_active')) is not int or
            data['max_active'] != PROTOCOLS[version]):
        raise RuntimeError('Unsupported Cloud Build coordination protocol')
    return version, PROTOCOLS[version]


def ledger_key(value):
    if not isinstance(value, (str, Path)) or not Path(value).is_absolute():
        raise RuntimeError('Reservation ledger must be absolute')
    return str(Path(value).resolve())


def reservations():
    """Read legacy single-slot, v2, v3 or v4 state; caller holds locked().

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
    validate_records(records, version, require_full=(version == 4))
    return records


def validate_records(records, version, require_full=False):
    """Keep legacy reads compatible; require full reconciler records for v4."""
    if not isinstance(records, list):
        raise RuntimeError('Invalid Cloud Build reservation count')
    tokens, owners, ledgers, build_ids = set(), set(), set(), set()
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
        for key in ('phase_id', 'state_dir'):
            if require_full or key in record:
                if not isinstance(record.get(key), str) or not record[key]:
                    raise RuntimeError('Invalid reservation ' + key)
        if 'state_dir' in record and not Path(record['state_dir']).is_absolute():
            raise RuntimeError('Reservation state_dir must be absolute')
        if require_full and ('build_id' not in record or 'item' not in record):
            raise RuntimeError('Incomplete Cloud Build reservation')
        build_id = record.get('build_id')
        if 'build_id' in record and build_id is not None:
            if not isinstance(build_id, str) or not build_id:
                raise RuntimeError('Invalid reservation Build ID')
        item_build_id = None
        if 'item' in record:
            item = record['item']
            if not isinstance(item, dict):
                raise RuntimeError('Invalid reservation item')
            if require_full and any(key not in item for key in ('dispatch_token', 'owner', 'phase_id')):
                raise RuntimeError('Incomplete reservation item identity')
            for key in ('owner', 'phase_id', 'ledger', 'state_dir', 'dispatch_token', 'build_id'):
                if key == 'build_id':
                    # The ledger item and global record may acquire the same
                    # Build ID in separate reconciler steps; one can lag.
                    if key in item and item[key] is not None and (
                            not isinstance(item[key], str) or not item[key]):
                        raise RuntimeError('Invalid reservation item Build ID')
                    item_build_id = item.get(key)
                    if (item.get(key) and record.get(key) and item[key] != record[key]):
                        raise RuntimeError('Reservation item identity conflicts: ' + key)
                elif key in item and item[key] != record.get(key):
                    raise RuntimeError('Reservation item identity conflicts: ' + key)
        known_build_id = build_id or item_build_id
        if known_build_id:
            if known_build_id in build_ids:
                raise RuntimeError('Invalid or duplicate reservation Build ID')
            build_ids.add(known_build_id)
        if version == 3 and record['owner'] not in V3_OWNERS:
            raise RuntimeError('Unsupported v3 Cloud Build owner')
        if version == 4 and record['owner'] not in V4_OWNERS:
            raise RuntimeError('Unsupported v4 Cloud Build owner')


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
    validate_records(records, version, require_full=(version == 4))
    path = COORDINATION / 'active.json'
    previous = read(path) if path.exists() else {}
    # Envelope metadata (including future timestamps) belongs to the shared
    # coordinator. Replacing a reservation must not discard unrelated fields.
    envelope = previous.copy() if 'schema_version' in previous else {}
    envelope.update(schema_version=version, max_active=capacity, reservations=records)
    write(path, envelope)


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
    occupied = occupied_slots(records, ongoing)
    _, capacity = protocol()
    if occupied >= capacity:
        raise RuntimeError(('Both' if capacity == 2 else 'All') +
                           ' Cloud Build slots are occupied; monitor/reconcile first')
    if capacity == 3 and owner not in V3_OWNERS:
        raise RuntimeError('Unsupported v3 Cloud Build owner')
    if capacity == 4 and owner not in V4_OWNERS:
        raise RuntimeError('Unsupported v4 Cloud Build owner')


def occupied_slots(records, ongoing):
    """Validate current API inventory and count reservations plus unmatched Builds."""
    ids, matched_tokens = set(), set()
    occupied = len(records)
    for build in ongoing:
        if not isinstance(build, dict):
            raise RuntimeError('Invalid ongoing Build')
        build_id = build.get('id')
        if not isinstance(build_id, str) or not build_id or build_id in ids:
            raise RuntimeError('Invalid or duplicate ongoing Build ID')
        ids.add(build_id)
        tags = build.get('tags', [])
        if not isinstance(tags, list) or any(not isinstance(t, str) or not t for t in tags) or len(tags) != len(set(tags)):
            raise RuntimeError('Invalid or duplicate ongoing Build token')
        matches = [r for r in records if (r.get('build_id') or r.get('item', {}).get('build_id')) == build_id or
                   r['dispatch_token'] in tags]
        if len(matches) > 1:
            raise RuntimeError('Ongoing build matches multiple reservations')
        if matches:
            record = matches[0]
            token = record['dispatch_token']
            known_build_id = record.get('build_id') or record.get('item', {}).get('build_id')
            if (token in matched_tokens or token not in tags or
                    known_build_id not in (None, build_id)):
                raise RuntimeError('Ongoing build conflicts with reserved token or Build ID')
            matched_tokens.add(token)
        else:
            occupied += 1
    return occupied


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
    # A dispatcher may know only the fields it updates. Retain opaque receipt
    # and timing metadata already attached to this exact token.
    records[index] = {**current, **record}
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
