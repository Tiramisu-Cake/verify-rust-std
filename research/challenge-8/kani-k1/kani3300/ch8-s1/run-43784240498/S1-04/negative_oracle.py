"""Exact assert detector, not a proof-admission classifier.

Call only after source/tool/config/harness binding. Unreachable/unsupported role
review is a separate gate. Descriptions never serve as property identity.
"""

def matches(harness, oracle):
    if not isinstance(harness, dict) or not isinstance(oracle, dict):
        return False
    if any(not isinstance(oracle.get(k), str) or not oracle[k] for k in ('selector', 'property_id', 'export_file')):
        return False
    if type(oracle.get('line')) is not int or oracle['line'] < 1 or oracle.get('class') != 'assertion':
        return False
    if harness.get('name') != oracle.get('selector'):
        return False
    if harness.get('outcome') != {'kind': 'COMPLETED', 'verdict': 'FAILURE'}:
        return False
    checks, covers = harness.get('checks'), harness.get('covers')
    named = harness.get('failed_properties')
    if not isinstance(checks, dict) or not isinstance(covers, dict):
        return False
    if not isinstance(named, list) or len(named) != 1 or not isinstance(named[0], dict):
        return False
    if type(harness.get('n_failed')) is not int or harness['n_failed'] != 1:
        return False
    for key in ('undetermined', 'error', 'unknown', 'other'):
        if checks.get(key) != []:
            return False
    unreachable = checks.get('unreachable')
    if not isinstance(unreachable, list) or any(not isinstance(x, str) for x in unreachable):
        return False
    if len(set(unreachable)) != len(unreachable):
        return False
    if checks.get('failure') != [oracle.get('property_id')]:
        return False
    if oracle.get('property_id') in unreachable:
        return False
    for key in ('total', 'success'):
        if type(checks.get(key)) is not int or checks[key] < 0:
            return False
    if checks['total'] != checks['success'] + len(unreachable) + 1:
        return False
    sat = covers.get('satisfied')
    if (not isinstance(sat, list) or any(not isinstance(x, str) for x in sat)
            or len(set(sat)) != len(sat) or type(covers.get('total')) is not int
            or covers['total'] != len(sat)):
        return False
    if any(covers.get(k) != [] for k in ('unsatisfiable', 'unreachable', 'undetermined', 'error', 'unknown', 'other')):
        return False
    if type(harness.get('n_properties')) is not int or harness['n_properties'] != checks['total'] + covers['total']:
        return False
    unsupported = harness.get('unsupported_constructs')
    if not isinstance(unsupported, list) or any(not isinstance(p, dict) or p.get('status') != 'SUCCESS' or p.get('class') != 'unsupported_construct' for p in unsupported):
        return False
    prop = named[0]
    return (prop.get('id') == oracle.get('property_id')
            and prop.get('file') == oracle.get('export_file')
            and prop.get('line') == str(oracle.get('line'))
            and prop.get('class') == oracle.get('class') == 'assertion'
            and prop.get('status') == 'FAILURE')
