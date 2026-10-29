# Opt-in evidence audit

Target library SHA: `9be5499c459e3157be0d86dc366b2eccd1e911c8`.
Evidence scope: 252 extended-positive harnesses; historical PASS 185, no exact PASS evidence 67.
Transfer result after per-harness source audit: PASS 184, NO_EVIDENCE 68.

This is a source-level transfer audit, not a new Kani run. Each harness source item and its identifier-resolved verification helper call closure are compared independently; this bounded Python analysis does not expand macros as rustc does. cfg attributes, comments, and import regrouping are normalized. Production/library files outside verify/ are also checked for changes.

Selected transferable PASS evidence source counts:
- P-6 Actions run 40748125754: 182
- GCB C3c baseline-memory: 2

Latest historical PASS source counts:
- GCB C3c autoharness: 96
- P-6 Actions run 40748125754: 86
- GCB C3c controls: 1
- GCB C3c baseline-memory: 1
- RESULT-C3A: 1

All bounded GCB `*.rows.tsv` fragments were reconciled with their matching `*.status.json` source SHA, finish time, and build ID; rows are considered newest-first. GCB evidence is selected only when that harness's source and helper closure match the target; otherwise the audit falls back to an earlier suitable PASS such as P-6. Rows without a suitable matching PASS remain NO_EVIDENCE; timeout, missing result, neighboring length, and negative control are not PASS.

Reproduce with `python3 research/challenge-8/kani-k1/scope/audit_optin_evidence.py`.
