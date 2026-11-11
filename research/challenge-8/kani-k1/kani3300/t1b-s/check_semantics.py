"""Static token comparison after removing only the opt-in diagnostic statements.
This does not compile Rust or claim MIR/GOTO equivalence at runtime.
"""
import re
import subprocess
from pathlib import Path

KANI = Path('/root/kani-fix-3300-t1')
BASE = '989f72351c2b5c5f3b5117315fc84f502e66d904'
FILES = [
    'codegen_cprover_gotoc/codegen/function.rs',
    'codegen_cprover_gotoc/compiler_interface.rs',
    'kani_middle/transform/mod.rs',
    'kani_middle/transform/check_uninit/mod.rs',
    'kani_middle/transform/check_uninit/delayed_ub/mod.rs',
]


def mask(text):
    # Preserve offsets while hiding braces/semicolons in comments and Rust strings.
    return re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',
                  lambda m: ' ' * len(m[0]), text, flags=re.S)


def normalize(text):
    while True:
        hidden = mask(text)
        hit = re.search(r'\bif\s+(?:crate::kani_middle::trace::enabled\(\)|trace_enabled\b|traced\b|'
                        r'instance_name\.as_deref\(\)|let Some\((?:instance_name|name)\) = instance_name\.as_deref\(\))', hidden)
        if not hit:
            break
        opening = hidden.index('{', hit.start())
        depth, end = 1, opening + 1
        while depth:
            depth += (hidden[end] == '{') - (hidden[end] == '}')
            end += 1
        text = text[:hit.start()] + text[end:]
    while True:
        hidden = mask(text)
        hit = re.search(r'\blet (?:trace_enabled|name|traced|cache_hit|instance_name)\s*=', hidden)
        # Only remove declarations that initialize diagnostic values.
        hits = list(re.finditer(r'\blet (?:trace_enabled|name|traced|cache_hit|instance_name)\s*=', hidden))
        target = None
        for hit in hits:
            end = hidden.index(';', hit.end()) + 1
            value = text[hit.start():end]
            if any(key in value for key in ('trace::', 'trace_enabled', 'name.as_deref().is_some_and')):
                target = hit.start(), end
                break
        if target is None:
            break
        text = text[:target[0]] + text[target[1]:]
    # enumerate adds observation-only ordinals; underlying order/iteration is identical.
    text = text.replace('for (ordinal, harness) in ordered_harnesses.into_iter().enumerate()',
                        'for harness in ordered_harnesses')
    # Strip comments while preserving strings in the final token stream.
    text = re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',
                  lambda m: m[0] if m[0].startswith('"') else '', text, flags=re.S)
    return re.findall(r'"(?:\\.|[^"\\])*"|[A-Za-z_][A-Za-z_0-9]*|\d+|\S', text, flags=re.S)


def check():
    results = {}
    for relative in FILES:
        path = 'kani-compiler/src/' + relative
        old = subprocess.check_output(['git', '-C', str(KANI), 'show', BASE + ':' + path]).decode()
        new = (KANI / path).read_text()
        a, b = normalize(old), normalize(new)
        if a != b:
            import difflib
            print('\n'.join(difflib.unified_diff(a, b, n=5)))
            raise AssertionError('non-diagnostic token difference: ' + path)
        results[path] = 'IDENTICAL_AFTER_DIAGNOSTIC_REMOVAL'
    return results


if __name__ == '__main__':
    import json
    print(json.dumps(check(), indent=2))
