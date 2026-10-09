#!/usr/bin/env python3
"""Small synthetic classifier controls; this never runs compiler or VeriFast."""
import importlib.util
from pathlib import Path

path=Path(__file__).with_name('mdnew-upstream-pr-audit.py')
spec=importlib.util.spec_from_file_location('mdnew_upstream_pr_audit',path)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

commands=list(m.TRACES)
def line(command, body=''):
    return f'Starting process 1: purely_unsafe/manuallydrop_new_cfg$ {command}\n{body}' \
           f'PASS: purely_unsafe/manuallydrop_new_cfg$ {command} (0.01s)\n'
valid=''.join(line(c, ('[1]0 errors found (8 statements verified)\n' if c in commands[:2] else
                       '[1]false_normal_post.rs(12,1): error: Cannot prove false\n' if 'false_normal_post' in c else
                       '[1]shared_false_unwind.rs(17,1): error: Cannot prove false\n' if 'shared_false_unwind' in c else
                       '[1]dead_code_pre.rs(1,1-7,2): dead code\n' if 'dead_code_pre' in c else '')) for c in commands)
assert m.verify_trace(valid,0)['mysh_commands']==5
controls=(
    ('missing', valid.replace(line(commands[0],'[1]0 errors found (8 statements verified)\n'),''), 0, 'INCOMPLETE_EVIDENCE'),
    ('early diagnostic', valid.replace('[1]dead_code_pre.rs(1,1-7,2): dead code\n','')+
     '[9]dead_code_pre.rs(1,1-7,2): dead code\n', 0, 'EARLY_OR_WRONG_DIAGNOSTIC'),
    ('wrong diagnostic', valid.replace('dead_code_pre.rs(1,1-7,2): dead code',
                                        'dead_code_pre.rs(1,1): error: Cannot prove false'),
     0, 'EARLY_OR_WRONG_DIAGNOSTIC'),
    ('nonzero runner', valid, 1, 'EARLY_OR_WRONG_DIAGNOSTIC'),
    ('timeout', valid, 124, 'TIMEOUT'),
    ('disabled unwind', valid+'-ignore_unwind_paths\n', 0, 'EARLY_OR_WRONG_DIAGNOSTIC'),
)
for name,log,code,kind in controls:
    try: m.verify_trace(log,code)
    except m.AuditFailure as error: assert error.kind==kind,(name,error.kind)
    else: raise AssertionError(f'{name} control passed')
print({'synthetic_trace_controls':len(controls)+1,'compiler_or_verifier_execution':False,'passed':True})
