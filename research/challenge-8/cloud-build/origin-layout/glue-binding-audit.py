#!/usr/bin/env python3
"""Read saved observer output only; never invokes compiler/extractor/verifier."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def classify(raw: bytes) -> dict:
    text = raw.decode('utf-8', errors='strict')
    edges = re.findall(r'^call_resolve block=(\S+) status=resolved instance=(.+)$', text, re.M)
    exact = re.findall(r'^call_expected_destructor_instance block=(\S+) expected=(.+) exact_instance_match=(true|false)$', text, re.M)
    matches = re.findall(r'^call_resolved_def_path block=(\S+) path=(.+) hash=(.+) selected_drop_match=(true|false)$', text, re.M)
    captures = re.findall(r'^selected_method_capture owner=(.+) source_instance=(.+) phase=(\S+) body_query=mir_drops_elaborated_and_const_checked instantiated=false concrete_args=(.+)$', text, re.M)
    capture_body = '--- resolved selected method exporter-owned MIR debug ---' in text
    bound = (len(edges) == len(exact) == len(matches) == len(captures) == 1 and
             edges[0][0] == exact[0][0] == matches[0][0] and exact[0][2] == matches[0][3] == 'true' and
             'Item(' in exact[0][1] and 'Item(' in edges[0][1] and capture_body)
    return {'classification': 'OBSERVED_EXACT_DESTRUCTOR_INSTANCE_AND_CAPTURE' if bound else 'INCONCLUSIVE_BINDING',
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
            'resolved_edges': edges, 'expected_instances': exact, 'destructor_defid_matches': matches,
            'captured_source_bodies': captures, 'captured_body_present': capture_body,
            'captured_body_instantiated': False, 'proof_credit': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('saved_observations', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise SystemExit('refusing to overwrite an evidence audit')
    rows = {str(f.relative_to(a.saved_observations)): classify(f.read_bytes())
            for f in sorted(a.saved_observations.rglob('drop-*.txt'))}
    partial = {str(f.relative_to(a.saved_observations)): hashlib.sha256(f.read_bytes()).hexdigest()
               for f in sorted(a.saved_observations.rglob('drop-*.partial'))}
    result = {'schema': 'merge-glue-binding-saved-audit-v1', 'accepted': False,
              'classification': 'OBSERVATION_COMPLETE' if rows and all(r['classification'] ==
                'OBSERVED_EXACT_DESTRUCTOR_INSTANCE_AND_CAPTURE' for r in rows.values()) else 'INCONCLUSIVE',
              'observations': rows, 'partial_diagnostic_sha256': partial,
              'compiler_invoked': False, 'extractor_invoked': False, 'verifier_invoked': False,
              'claims': 'Saved exact compiler Instance equality and owner MIR capture only; no generated-glue proof or monomorphized-method claim.'}
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'classification': result['classification'], 'complete_observations': len(rows), 'partials': len(partial)}))

if __name__ == '__main__':
    main()
