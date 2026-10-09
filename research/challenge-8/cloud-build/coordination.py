"""Cross-worktree Cloud Build reservation and atomic accounting (VPS only)."""

import contextlib
import fcntl
import json
import os
from pathlib import Path
import tempfile
import datetime


COORDINATION = Path('/root/smallsort-ci-coordination')


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


def active():
    path = COORDINATION / 'active.json'
    return read(path) if path.exists() else None


def reserve(record):
    if active() is not None:
        raise RuntimeError('Global Cloud Build reservation already exists')
    write(COORDINATION / 'active.json', record)


def update(record):
    if active() is None:
        raise RuntimeError('Global Cloud Build reservation disappeared')
    write(COORDINATION / 'active.json', record)


def clear(token):
    path = COORDINATION / 'active.json'
    current = active()
    if current is None or current.get('dispatch_token') != token:
        raise RuntimeError('Global Cloud Build reservation changed; refusing to clear')
    path.unlink()
    directory = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


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
