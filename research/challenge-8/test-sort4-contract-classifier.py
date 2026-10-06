#!/usr/bin/env python3
"""Hosted regression gate: malformed/unrelated logs must never be accepted."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('classifier', Path(__file__).with_name('classify-sort4-contract.py'))
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)
checks = 0
for case, (_, _, negative) in classifier.CASES.items():
    log = Path(f'research-results/{case}.log').read_text()
    code = int(Path(f'research-results/{case}-exit-code.txt').read_text())
    # Require genuine accepted input before testing malformed variations.
    assert classifier.classify(case, code, log)['accepted'], case
    variants = [
        (124, log), (2, log), (code, ''),
        (code, log.replace('VERIFICATION:-', 'TRUNCATED:')),
        (code, log.replace('Complete -', 'TRUNCATED -')),
        (code, log.replace('Checking harness ', 'Wrong harness ')),
        (code, log + '\nerror: synthetic frontend failure\n'),
        (code, log.replace('Status: SUCCESS', 'Status: UNKNOWN', 1)),
    ]
    if negative:
        description = 'memcpy src/dst overlap' if 'coincident' in case else 'original multiset preserved'
        variants += [
            (0, log),
            (code, log.replace(description, 'unrelated assertion')),
            (code, log.replace('Status: FAILURE', 'Status: SUCCESS')),
            (code, log.replace('in function ptr::copy_nonoverlapping::<i32>', 'in function unrelated'))
            if 'coincident' in case else
            (code, log.replace('smallsort.rs:', 'unrelated.rs:')),
        ]
    else:
        variants += [(1, log), (code, log.replace('Status: SATISFIED', 'Status: UNREACHABLE', 1))]
    for bad_code, bad_log in variants:
        assert not classifier.classify(case, bad_code, bad_log)['accepted'], case
        checks += 1
Path('research-results/classifier-regression.txt').write_text(
    f'PASS: 4 genuine accepted cases and {checks} malformed/nonmatching variants rejected\n')
print(f'Classifier rejection gate PASS ({checks} variants)')
