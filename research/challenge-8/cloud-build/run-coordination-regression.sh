#!/usr/bin/env bash
# Cloud-only coordinator tests with synthetic APIs; no compiler or verifier.
set -euo pipefail
[[ "${1:-}" == coordination-regression ]] || exit 2
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
[[ "$evidence_root" == /workspace/evidence ]] || exit 2
python3 "$cloud_dir/provider.py" > "$evidence_root/coordination-provider.json"
mkdir -p "$evidence_root/allprooflogs"
code=0
/usr/bin/time -v -o "$evidence_root/allprooflogs/coordination-resources.txt" \
  python3 "$cloud_dir/coordination-regression.py" \
  --cloud-dir "$cloud_dir" \
  --work-root /workspace/smallsort-work/coordination-regression \
  --output /workspace/evidence/allprooflogs/cases/coordination-regression \
  > "$evidence_root/allprooflogs/coordination.log" 2>&1 || code=$?
printf '%s\n' "$code" > "$evidence_root/allprooflogs/coordination-exit-code.txt"
cat "$evidence_root/allprooflogs/coordination.log"
python3 - "$evidence_root" "$code" <<'AUDIT'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
result = root / 'allprooflogs/cases/coordination-regression/summary.json'
summary = json.loads(result.read_text()) if result.exists() else {}
complete = (sys.argv[2] == '0' and summary.get('diagnostic_complete') is True
            and summary.get('case_count', 0) > 0
            and summary.get('passed_count') == summary.get('case_count'))
(root / 'proof-audit.json').write_text(json.dumps({
    'accepted': False, 'verification_accepted': False,
    'diagnostic_complete': complete, 'lane': 'coordination-regression',
    'classification': 'COORDINATION_REGRESSION_COMPLETE' if complete else 'INCONCLUSIVE',
    'case_count': summary.get('case_count'), 'passed_count': summary.get('passed_count'),
    'limits': 'Synthetic API and disposable coordinator only; no live dispatch or std proof.'
}, indent=2) + '\n')
AUDIT
exit "$code"
