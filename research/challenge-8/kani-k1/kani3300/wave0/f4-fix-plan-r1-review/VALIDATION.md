# PASS — static plan-delta review validation

Run from /root/verify-rust-std-kani3300-g0:

```sh
python3 research/challenge-8/kani-k1/kani3300/wave0/f4-fix-plan-r1-review/validate_review.py
```

The validator prints JSON and writes nothing. VALIDATION.json is the recorded
output. It checks nine exact committed input files and the exact nine-file added
metadata scope; historical old748/cbfd files; clean source HEAD/tree/parent;
source/test blob IDs and SHA256; all sixteen workflow identities and unchanged
.github/scripts trees. It derives seven applicable PR workflows/native events
from frozen YAML, checks actual bundle actions/platforms, both full five-OS test
matrices and their artifact/target routing, and expands matrix include rows.
Four builds plus two five-entry matrices equal fourteen required PR instances.
Only tag-release and dependent Docker publication intentionally skip.

Submitted validate_plan.py and --check-manifest both exit 0; replay JSON exactly
matches committed author VALIDATION.json, including 41 rejected negative cases.
The reviewer separately selects 21 independent omissions: seven individual
workflows, four individual build jobs, ten individual matrix OS entries. Each
starts from the complete request and is rejected by the submitted plan gate.
No native source test or old compiler review validator is invoked.

Operational prerequisites were manually reviewed in CI-REQUEST.md/json against
prior cbfd review and frozen native/reusable workflows/labeler; REVIEW.json records
the assessment. Static checks do not establish future labels, event delivery,
checkout identity, build success, runtime result or performance. Compiler/build/
new-test runtime/performance/full CI are NOT_RUN; proof credit NONE. No attempt,
reservation, ledger change, push, PR, publication, label/event action or CI occurred.
