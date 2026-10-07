#!/usr/bin/env python3
"""Hosted-only fail-closed acceptance of independent stock+CFG profile."""
import json, pathlib, re, sys
root=pathlib.Path(sys.argv[1])
stock=json.loads((root/'stock/cases/summary.json').read_text())
patched=json.loads((root/'cfg/cases/summary.json').read_text())
positive={'u32_positive','raw_positive','forget_positive','ordinary_unwind','shared_cleanup'}
negative={'u32_false_post','raw_false_post','forget_false_post','false_unwind'}
dead={'u32_contradictory_pre','forget_contradictory_pre'}
checks={}
checks['complete_cases']=set(stock)==set(patched)==positive|negative|dead
for name in sorted(patched):
 a,b=stock[name],patched[name]
 checks[name+'_frontend_integrity']=a['frontend_all_zero'] and b['frontend_all_zero'] and a['source_integrity'] and b['source_integrity']
 checks[name+'_verdict']=b['classification']==('POSITIVE' if name in positive else 'INTENDED_NEGATIVE' if name in negative else 'INTENDED_DEAD_CODE_REJECTION')
 for rel in ['original/lib.rs','verified/lib.rs','normal-mir.bin','readonly-mir.bin','normal-mir.txt','readonly-mir.txt']:
  checks[name+'_'+rel]=(root/'stock/cases'/name/rel).read_bytes()==(root/'cfg/cases'/name/rel).read_bytes()
 # Complete exported MIR equality independently protects all cleanup edges.
 if name in positive:
  strict=b['strict_original_classification']
  checks[name+'_whole_unit']=strict['accepted'] and strict['function_list_exact'] and not b['dead_code_diagnostics']
checks['stock_forget_causal_failure']=stock['forget_positive']['classification']=='INCONCLUSIVE' and stock['forget_positive']['stages']['full-verification']['exit']==1 and len(stock['forget_positive']['dead_code_diagnostics'])==1 and stock['forget_positive']['strict_original_classification']['error_count']==0
# Keep AST and console evidence for human binding of normal/unwind returns to actual functions.
for name in ['ordinary_unwind','shared_cleanup']:
 text=(root/'cfg/cases'/name/'verified-ast.txt').read_text()
 log=(root/'cfg/cases'/name/'full-verification.log').read_text()
 checks[name+'_unwind_return_in_ast']='ReturnStmt' in text and 'unwinding' in text
 checks[name+'_body_returns_leaks']=all(x['body_execution_seen'] and x['return_seen'] and x['leak_check_seen'] for x in patched[name]['strict_original_classification']['timed_functions'])
result={'profile':'stock-26.10+manuallydrop-new-cfg-v1','accepted':all(checks.values()),'checks':checks,'false_checks':[k for k,v in checks.items() if not v],'actual_helper_proved':False,'generic_safe_forget_proved':False}
(root/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['accepted'] else 1)
