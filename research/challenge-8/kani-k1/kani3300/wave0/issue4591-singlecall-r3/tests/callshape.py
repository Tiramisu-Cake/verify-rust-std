"""Bounded source-call model for these fixtures; never a Rust/MIR interpreter.

Models straight-line calls and the pinned body-source mode selection. Branches,
loops and recursive paths are reported rather than assigned path feasibility.
Generated closure identity follows the source provider, not its copied target.
"""

import re


def mask(text):
    return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
                  lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), text)


def functions(text):
    clean = mask(text)
    pattern = re.compile(r'(?m)^(?P<attrs>(?:#\[[^\n]*\]\s*\n)*)'
                         r'fn\s+(?P<name>\w+)[^{]*\{')
    result = {}
    for match in pattern.finditer(clean):
        start, end, depth = match.end(), match.end(), 1
        while depth and end < len(clean):
            depth += (clean[end] == '{') - (clean[end] == '}')
            end += 1
        if depth:
            raise ValueError('unbalanced fixture function')
        name = match['name']
        if name in result:
            raise ValueError('duplicate fixture name')
        result[name] = {
            'attrs': text[match.start('attrs'):match.end('attrs')].strip().splitlines(),
            'body': text[start:end - 1],
            'line': text.count('\n', 0, match.start()) + 1,
            'end_line': text.count('\n', 0, end) + 1,
            'source': text[match.start():end],
        }
    return result


def local_calls(body, definitions):
    return [m[1] for m in re.finditer(r'\b([a-zA-Z_]\w*)\s*\(', mask(body))
            if m[1] in definitions]


def attr_args(function, attribute):
    return re.findall(r'#\[kani::' + attribute + r'\(([^\]]*)\)\]',
                      '\n'.join(function['attrs']))


def trace(text, harness):
    defs = functions(text)
    pfc = attr_args(defs[harness], 'proof_for_contract')
    if len(pfc) != 1:
        raise ValueError('one PFC target required')
    target = pfc[0]
    stubs = dict(tuple(s.strip() for s in pair.split(','))
                 for pair in attr_args(defs[harness], 'stub'))
    verified = set(attr_args(defs[harness], 'stub_verified'))
    events, unsupported = [], []

    def visit(requested, path):
        source, seen = requested, set()
        while source in stubs:
            if source in seen:
                raise ValueError('cyclic fixture stubs')
            seen.add(source)
            source = stubs[source]
        effective = requested if requested == target or requested in verified else source
        fn = defs[effective]
        contracted = any(re.search(r'kani::(?:requires|ensures|modifies)\(', a)
                         for a in fn['attrs'])
        mode = ('Check' if effective == target else
                'Replace' if effective in verified else
                'Original' if '--no-assert-contracts' in text else 'Assert') if contracted else 'Body'
        event = {'requested': requested, 'body_source': source,
                 'effective': effective, 'mode': mode, 'path': path + [requested]}
        events.append(event)
        if source != effective:
            unsupported.append('explicit-selected-target ordinary overlap: ' + requested)
            return
        if requested in path:
            unsupported.append('recursive source path: ' + requested)
            return
        if re.search(r'\b(if|match|while|loop|for)\b', mask(defs[source]['body'])):
            unsupported.append('branched source path: ' + requested)
        if mode != 'Replace':
            for called in local_calls(defs[source]['body'], defs):
                visit(called, path + [requested])

    for called in local_calls(defs[harness]['body'], defs):
        visit(called, [])
    checked = [event for event in events if event['effective'] == target and event['mode'] == 'Check']
    exact = any(event['requested'] == target for event in events)
    return {'harness': harness, 'selected_target': target, 'exact_target_reachable': exact,
            'effective_check_calls': len(checked), 'events': events,
            'unsupported': unsupported,
            'single_call_shape': exact and len(checked) == 1 and not unsupported}


def guard_model(completed_calls):
    """Sequential nonrecursive projection of dfcc_swap_and_wrap.cpp:175-212."""
    completed, outcomes = False, []
    for _ in range(completed_calls):
        outcomes.append(not completed)
        completed = True
    return outcomes
