#!/usr/bin/env python3
"""Independent bounded path-parenthesis/guard checks; token strings only."""
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0,'/root/kani-ch8-s2-r14-03-gate-backlog-w13/ch8-s1-control')
import cfg_pfc as c
import lexical_bindings as l


def main():
    records = []
    for depth in (0,1,2,4,16,257,4096):
        for path,expected in [('callable',('callable',)),
                              ('super::super::sort4_stable',('super','super','sort4_stable')),
                              ('::core::mem::size_of::<u8>',('core','mem','size_of'))]:
            expression = '(' * depth + path + ')' * depth + '();'
            tokens = c.tokens(expression)
            actual = list(l.call_paths(tokens))
            assert len(actual) == 1 and actual[0][:3] == (expected,1,'STATIC')
            assert tokens[actual[0][3]][0] == expected[0]
            records.append({'depth':depth,'path':path,'status':'ONE_EXACT_STATIC_RECORD_WITH_ORIGINAL_TOKEN_OFFSET'})
    rejected = []
    for expression in ('((left,right))()', '((*pointer))()', '((obj.member))()',
                       '((factory))()()', '((factory(argument)))()',
                       '((callbacks[0]))()', '((|| {}))()',
                       '(({callback}))()', '((macro!()))()'):
        try:
            list(l.call_paths(c.tokens(expression)))
        except c.GateError as exc:
            assert 'unsupported' in str(exc) and 'call' in str(exc)
            rejected.append({'expression':expression,'status':'REJECT','diagnostic':str(exc)})
        else:
            raise AssertionError(expression)
    expression = '((callee))(((argument))(), ((receiver)).method());'
    actual = list(l.call_paths(c.tokens(expression)))
    assert [(x[0],x[2]) for x in actual] == [(('callee',),'STATIC'),(('argument',),'STATIC'),(('method',),'METHOD')]
    result = {'status':'PASS','scope':'bounded extractor/guard delta; no expression typing or syntax completeness claim',
              'path_cases':records,'unsupported_guard_cases':rejected,
              'nested_argument_and_method_case':{'source':expression,'records':actual},
              'native_compile':'NOT_RUN','proof_credit':'NONE'}
    (OUT/'EXTRACTOR-CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print('EXTRACTOR_CHECKS_PASS:21 supported path/depth cases through4096;9 unsupported nested forms reject; methods remain inventory-only')


if __name__ == '__main__':
    main()
