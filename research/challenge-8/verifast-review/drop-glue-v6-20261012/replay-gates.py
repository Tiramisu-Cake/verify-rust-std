#!/usr/bin/env python3
"""Saved-data negative-gate replay only. Never prepare or execute proof tools.
Full prior source/MIR/body admissions are reused from hash-bound raw receipts;
this is not a full fresh auditor, verifier, or changed-profile result.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]); evidence = Path(sys.argv[2])
path = root / 'research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py'
spec = importlib.util.spec_from_file_location('review_saved_negative_gate', path)
r = importlib.util.module_from_spec(spec); sys.modules[spec.name] = r; spec.loader.exec_module(r)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
extraction = json.loads((evidence / 'extraction.json').read_text())
result = {'kind': 'SAVED_NEGATIVE_GATE_REPLAY_NO_FRESH_PROOF',
          'build_id': '34485da0-911b-4c1e-9d8d-32922f154f82',
          'auditor_commit': '420188dd1732d53f3f515690ed2ff6f53a9026ab',
          'auditor_source_sha256': sha(path), 'cases': {}}
for name, row in extraction['cases'].items():
    case = evidence / 'cases' / name
    raw = json.loads((case / 'classification.json').read_text())
    assert sha(case / 'original/lib.rs') == row['original_sha256']
    assert sha(case / 'verified/lib.rs') == row['verified_sha256']
    stages = raw['stages']
    for stage in ('exporter','decode','refinement','verifast'):
        assert int((case / (stage+'-exit-code.txt')).read_text()) == stages[stage]
        receipt = json.loads((case / (stage+'-stage.json')).read_text())
        # Record all receipts; their source immutability is also retained below.
        assert receipt['exit_code'] == stages[stage]
    setup = (all(stages[s] == 0 for s in ('exporter','decode','refinement')) and
             raw['source_unchanged_at_every_stage'] and
             all(raw[k]['admitted'] for k in ('source_gate','mir_gate','caller_ast_evidence',
                 'drop_body_effect_ast_gate','generated_glue_refinement_gate')))
    assert setup
    log = (case / 'verifast.log').read_text()
    errors = [line for line in log.splitlines() if re.search(r'\berror:',line,re.I)]
    dead = [line for line in log.splitlines() if re.search('dead code',line,re.I)]
    glue_gate = r._generated_glue_proof_gate(log, raw['caller_ast_evidence']['body_glue_evidence'])
    assert glue_gate['admitted']
    negative = r._body_glue_negative_gate(name, case, row, log, errors, dead,
        raw['caller_ast_evidence'], glue_gate, setup,
        raw['natural_scope_end_executed'], raw['caller_return'], raw['caller_leak_check'])
    if name == 'positive':
        verdict = raw['classification']; assert stages['verifast'] == 0 and not errors and not dead
    else:
        assert stages['verifast'] == 1 and negative['admitted'], (name, negative)
        verdict = 'CALLER_READY_ENTRY_EXPECTED_REJECTION' if name == 'caller_ready_entry_false' else 'EXPECTED_REJECTION'
    result['cases'][name] = {'old_verdict': raw['classification'], 'replay_verdict': verdict,
        'negative_gate': negative, 'stages': stages, 'source_unchanged_at_every_stage': True,
        'sha256': {f:sha(case/f) for f in ('classification.json','proof-ast.ml','decode.out',
            'original-decode.out','verifast.log','refinement.out','original/lib.rs','verified/lib.rs',
            'exporter-stage.json','decode-stage.json','refinement-stage.json','verifast-stage.json')},
        'errors':errors, 'dead':dead}
print(json.dumps(result,ensure_ascii=False,indent=2))
