#!/usr/bin/env python3
"""Static/source + tiny Python fixture checks, never Rust/Kani qualification."""
from pathlib import Path
import collections
import hashlib
import itertools
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
WT = Path('/root/verify-rust-std-ch8-s1-w11')
V = WT / 'library/core/src/slice/sort/shared/smallsort/verify'
SOURCE = WT / 'library/core/src/slice/sort/shared/smallsort.rs'
BASE = '3f469d3ba2e94d7129e66e53ea76df883ff9c946'

def git(*args):
    return subprocess.check_output(['git', '-C', str(WT), *args], text=True).strip()

source = SOURCE.read_text()
assert git('hash-object', str(SOURCE)) == 'f8000328aae720a6ae7a6e81cd5d5816fd73df8c'
changed = git('diff', '--name-only', BASE).splitlines()
new = git('ls-files', '--others', '--exclude-standard').splitlines()
allowed = {str((V / n).relative_to(WT)) for n in (
    'sorting_leaf_swap.rs', 'sorting_leaf_probe.rs', 'sorting_leaf_controls.rs')}
assert set(changed + new) <= allowed, (changed, new)
networks = {}
for width in (9, 13):
    body = source.split(f'fn sort{width}_optimal<T, F>', 1)[1].split('\n}\n', 1)[0]
    edges = [(int(a), int(b)) for a, b in re.findall(
        r'swap_if_less\(v_base, (\d+), (\d+), is_less\)', body)]
    assert len(edges) == {9: 25, 13: 45}[width]
    assert all(0 <= a < b < width for a, b in edges)
    count = 0
    # Zero-one network sanity, not a Rust theorem or actual callee proof.
    for bits in itertools.product(range(2), repeat=width):
        out = list(bits)
        for a, b in edges:
            if out[b] < out[a]:
                out[a], out[b] = out[b], out[a]
        assert out == sorted(bits)
        count += 1
    networks[str(width)] = {'edges': edges, 'zero_one_fixtures': count}

# Ordered+full-multiset model differs from order alone or counts alone.
def post(pre, out):
    return len(pre) == len(out) and out == sorted(out) and collections.Counter(pre) == collections.Counter(out)
assert post([1, 2], [1, 2])
assert not post([1, 2], [2, 1])
assert not post([1, 2], [1, 1])
assert not post([1] * 13, [1] * 12 + [2])
assert not post(list(range(12, -1, -1)), list(range(12, -1, -1)))
for a in range(256):
    for b in range(256):
        lo, hi = (b, a) if b < a else (a, b)
        assert lo <= hi and collections.Counter((a, b)) == collections.Counter((lo, hi))

geometry = []
for n in range(16, 33):
    h = n // 2
    for src, dst, temp in ((0, 0, n), (h, h, n + 8)):
        assert src + 8 <= n <= 32
        assert dst + 8 <= temp and temp + 8 <= n + 16 <= 48
        geometry.append({'N': n, 'source_allocation': 'v32', 'source_offset': src,
                         'destination_allocation': 'scratch48', 'destination_offset': dst,
                         'temporary_allocation': 'scratch48', 'temporary_offset': temp,
                         'merge8_source_offset': temp, 'merge8_output_offset': dst})
assert len({(r['merge8_source_offset'], r['merge8_output_offset']) for r in geometry}) == 34

files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(V.glob('sorting_leaf*.rs'))}
roots = []
for p in sorted(V.glob('sorting_leaf*.rs')):
    text = p.read_text()
    assert 'panic_on_ord_violation' not in text and 'assume(false)' not in text
    roots.extend(re.findall(r'fn (s2_\w+)\(', text))
assert len(roots) == 11 and len(roots) == len(set(roots)), roots
manifest = json.loads((HERE/'CONTROL-MAP.json').read_text())
selectors = set()
for module in ('sorting_leaf_probe', 'sorting_leaf_controls'):
    text = (V/(module+'.rs')).read_text()
    selectors.update('core::slice::sort::shared::smallsort::verify::'+module+'::'+name
                     for name in re.findall(r'fn (s2_\w+)\(', text))
assert selectors == {r['selector'] for r in manifest['rows']}
assert len(manifest['rows']) == 11
assert sum(r['expect'].startswith('EXPECTED_') for r in manifest['rows']) == 8
for row in manifest['rows']:
    if row['expect'] == 'EXPECTED_NAMED_FAILURE':
        assert row['oracle'] in (V/'sorting_leaf_controls.rs').read_text()
(HERE/'geometry.json').write_text(json.dumps({'assurance': 'SOURCE_FORMULA_SYNTHETIC_ONLY', 'sort8': geometry}, indent=2)+'\n')
(HERE/'synthetic-result.json').write_text(json.dumps({
    'status': 'PASS_STATIC_AND_SYNTHETIC_ONLY', 'proof_credit': 'NONE',
    'rust_kani': 'NOT_RUN', 'source_base': BASE, 'source_head_observed': git('rev-parse','HEAD'),
    'source_blob': git('hash-object', str(SOURCE)), 'leaf_file_sha256': files,
    'networks': {k: {'edge_count':len(v['edges']), 'zero_one_fixtures':v['zero_one_fixtures']} for k,v in networks.items()},
    'pair_fixtures': 65536, 'sort8_topology_pairs': len(geometry), 'roots': roots,
}, indent=2)+'\n')
print('PASS: static scope/unchanged core; Python pair/network/checker/topology sanity only; Rust/Kani NOT_RUN')
