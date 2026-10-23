"""Cloud input verification only. Import is inert; no extraction or tool invocation."""
import hashlib
import os
import subprocess
from pathlib import Path


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def has_symlink_parent(repo, path):
    """Check path parents with lstat semantics; never traverse a parent link."""
    relative = path.relative_to(repo)
    parent = repo
    for part in relative.parts[:-1]:
        parent = parent / part
        if parent.is_symlink():
            return True
    return False


def symlink_target_is_checkout_relative(repo, path, target):
    """Validate a link lexically, without resolving or following its target."""
    if not target or os.path.isabs(target):
        return False
    parent = os.fsencode(path.parent.relative_to(repo))
    normalized = os.path.normpath(os.path.join(parent, target))
    return normalized not in (b'..', b'') and not normalized.startswith(b'../')


def verify_checkout(repo, pin):
    repo = repo.resolve(strict=True)
    if git(repo, 'rev-parse', 'HEAD').decode().strip() != pin['commit']:
        raise ValueError('checkout commit mismatch: ' + str(repo))
    # Reject tracked changes and unexpected Cargo config; no compilation here.
    if git(repo, 'status', '--porcelain', '--untracked-files=all').strip():
        raise ValueError('checkout is not pristine: ' + str(repo))
    for p, tree in pin.get('trees', {}).items():
        if git(repo, 'rev-parse', pin['commit'] + ':' + p).decode().strip() != tree:
            raise ValueError('source tree mismatch: ' + p)
    if 'tree' in pin and git(repo, 'rev-parse', 'HEAD:').decode().strip() != pin['tree']:
        raise ValueError('tool root tree mismatch')
    for rec in pin.get('files', []):
        p = repo / rec['path']
        if (has_symlink_parent(repo, p) or not p.is_file() or p.is_symlink() or
                not p.resolve().is_relative_to(repo)):
            raise ValueError('unsafe pinned source: ' + rec['path'])
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != rec['sha256'] or len(data) != rec['bytes']:
            raise ValueError('working input SHA256 mismatch: ' + rec['path'])
        meta = git(repo, 'ls-tree', 'HEAD', '--', rec['path']).decode().split()
        if meta[0] != rec['mode'] or meta[2] != rec['blob']:
            raise ValueError('input mode/blob mismatch: ' + rec['path'])
    # Verify physical bytes of the complete selected tracked closure, not only
    # git status (which can be fooled by assume-unchanged/index flags).
    byte_inventory = {}
    for prefix in pin.get('verify_paths', []):
        args = ['ls-tree', '-r', '-z', 'HEAD']
        if prefix:
            args.extend(['--', prefix])
        for raw in git(repo, *args).split(b'\0'):
            if not raw:
                continue
            metadata, raw_path = raw.split(b'\t', 1)
            mode, kind, blob = metadata.decode().split()
            name = raw_path.decode()
            p = repo / name
            if has_symlink_parent(repo, p):
                raise ValueError('tracked source has swapped symlink parent: ' + name)
            if mode == '160000':
                subpin = pin.get('gitlinks', {}).get(name)
                if subpin is None or blob != subpin['commit'] or p.is_symlink() or not p.is_dir():
                    raise ValueError('unfrozen/unmaterialized Gitlink: ' + name)
                byte_inventory[name] = {'gitlink': verify_checkout(p, subpin)}
                continue
            if mode == '120000':
                if kind != 'blob' or not p.is_symlink():
                    raise ValueError('missing or non-symlink tracked link: ' + name)
                target = os.readlink(os.fsencode(p))
                git_target = git(repo, 'cat-file', 'blob', blob)
                if target != git_target:
                    raise ValueError('tracked symlink target/blob mismatch: ' + name)
                if not symlink_target_is_checkout_relative(repo, p, target):
                    raise ValueError('tracked symlink escapes checkout: ' + name)
                byte_inventory[name] = {
                    'git_blob': blob,
                    'mode': mode,
                    'symlink_target_sha256': hashlib.sha256(target).hexdigest(),
                    'bytes': len(target),
                }
                continue
            if mode not in ('100644', '100755') or kind != 'blob' or p.is_symlink() or not p.is_file():
                raise ValueError('unsupported/missing tracked source mode: ' + name)
            if not p.resolve().is_relative_to(repo):
                raise ValueError('source path escapes checkout')
            size = p.stat().st_size
            sha1 = hashlib.sha1(('blob '+str(size)+'\0').encode())
            sha256 = hashlib.sha256()
            with p.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024*1024), b''):
                    sha1.update(chunk)
                    sha256.update(chunk)
            if sha1.hexdigest() != blob or bool(p.stat().st_mode & 0o111) != (mode == '100755'):
                raise ValueError('tracked source byte/mode mismatch: ' + name)
            byte_inventory[name] = {'git_blob': blob, 'mode': mode, 'sha256': sha256.hexdigest(), 'bytes': size}
    # Cargo reads ancestors; an unpinned enclosing config invalidates isolation.
    for parent in (repo, *repo.parents):
        for name in ('config', 'config.toml'):
            if (parent / '.cargo' / name).exists():
                raise ValueError('ambient Cargo config: ' + str(parent / '.cargo' / name))
    return {'ok': True, 'commit': pin['commit'], 'files': pin.get('files', []), 'byte_inventory': byte_inventory}
