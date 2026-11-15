#!/usr/bin/env python3
"""Source-only dispatch audit. Never invokes a Rust tool or verifier."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = '872d5a43380752786415bc00d2a12ce0e930cb37'
ROOT = Path('/root/verify-rust-std-ch8-profiles-w11')
PREFIX = 'library/core/src/slice/sort/shared/smallsort/'
ALLOWED = {PREFIX + x for x in ('verify.rs', 'verify/merge/profiles.rs', 'verify/network.rs',
                               'verify/merge.rs', 'verify/forwarding_contracts.rs')}

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()

def blob(rev, path):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{rev}:{path}'])

candidate = git('rev-parse', 'HEAD')
changed = git('diff', '--name-only', BASE, candidate).splitlines()
assert set(changed) == ALLOWED, changed
assert not git('status', '--porcelain'), 'Source worktree must be clean'
helper = PREFIX[:-1] + '.rs'
assert blob(BASE, helper) == blob(candidate, helper), 'Actual algorithm changed'
texts = {p: blob(candidate, p).decode() for p in ALLOWED}
# Scan the entire verification subtree, not just changed lines.
scan_paths = sorted((ROOT / PREFIX / 'verify').rglob('*.rs')) + [ROOT / helper, ROOT / PREFIX / 'verify.rs']
for path in scan_paths:
    source = path.read_text()
    assert not re.search(r'::CMP\b|const\s+CMP\b|profile_canonical_comparator|fn_addr_eq|\bFnPtr\b|\bdyn\s+Fn|\bas\s+(?:unsafe\s+)?fn\s*\(|(?:=|->)\s*(?:unsafe\s+)?fn\s*\(|\bas\s+\*const\s*\(\s*\)|:\s*(?:unsafe\s+)?fn\s*\(', source), path
profiles = texts[PREFIX + 'verify/merge/profiles.rs']
assert profiles.count('let mut is_less = |a: &P::Elem, b: &P::Elem| P::cmp(a, b);') == 4
assert 'fn cmp(a: &Self::Elem, b: &Self::Elem) -> bool;' in profiles
# Strip exactly the superseded comparator-identity requires; all other wrapper contracts
# must be byte-identical. Extract contiguous kani attrs immediately preceding each wrapper.
def contract(text, name):
    pos = text.index('unsafe fn ' + name)
    start = text.rfind('\n}\n', 0, pos) + 3
    attrs = text[start:pos]
    attrs = attrs[attrs.index('#[kani::'):]
    return attrs
for rel, names in [('verify/merge/profiles.rs', ['swap_profile', 'sort4_profile', 'insert_tail_profile', 'merge_profile']),
                   ('verify/forwarding_contracts.rs', ['stable_cell', 'unstable_byte', 'freeze_noncopy'])]:
    path = PREFIX + rel
    before = blob(BASE, path).decode()
    after = texts[path]
    for name in names:
        old = contract(before, name)
        old = re.sub(r'#\[kani::requires\((?:profile_canonical_comparator::<P>\(cmp\)|canonical\(cmp, \w+\))\)\]\n', '', old)
        assert old == contract(after, name), f'Contract changed: {name}'
# Ensure no old root disappears and no existing assertion or cover literal disappears,
# except the obsolete guard and explicitly mapped forwarding reachability labels.
removed_literals = []
for path, after in texts.items():
    before = blob(BASE, path).decode()
    pattern = r'kani::(?:assert|cover)\([\s\S]*?"([^"\n]+)"\s*\)'
    old = set(re.findall(pattern, before))
    new = set(re.findall(pattern, after))
    for literal in sorted(old - new):
        removed_literals.append({'path': path, 'literal': literal})
    old_functions = set(re.findall(r'\bfn\s+(\w+)\s*(?:<|\()', before))
    new_functions = set(re.findall(r'\bfn\s+(\w+)\s*(?:<|\()', after))
    assert old_functions - new_functions <= {'canonical', 'canonical_guard', 'profile_canonical_comparator'}, (path, old_functions - new_functions)
allowed_literals = {'canonical comparator required', 'invalid stable comparator reaches guard',
                    'invalid unstable comparator reaches guard', 'invalid Freeze comparator reaches guard'}
assert {x['literal'] for x in removed_literals} <= allowed_literals, removed_literals
report = {
    'schema': 'ch8-profiles-source-audit-v1', 'candidate': candidate,
    'tree': git('rev-parse', 'HEAD^{tree}'), 'baseline': BASE,
    'checks': ['exact five-file scope', 'clean source worktree', 'smallsort.rs byte-identical',
               'verification subtree + actual smallsort.rs: no explicit FnPtr/function-pointer type, function-address or as-fn coercion',
               'four typed direct profile closures', 'seven contract attribute sets preserved except identity requires',
               'old roots retained', 'removed literal allowlist checked'],
    'removed_literals_mapped_in': 'CONTROL-MAP.md', 'removed_literals': removed_literals,
    'source_sha256': {p: hashlib.sha256(blob(candidate, p)).hexdigest() for p in sorted(ALLOWED)},
    'actual_helper_sha256': hashlib.sha256(blob(candidate, helper)).hexdigest(),
    'assurance': 'STATIC_SOURCE_ONLY', 'compiler_mir_layout_dispatch': 'NOT_RUN',
    'proof_credit': 'NONE',
}
print(json.dumps(report, indent=2))
