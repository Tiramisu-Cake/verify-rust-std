# Opt-in evidence audit

Target library SHA: `9be5499c459e3157be0d86dc366b2eccd1e911c8`.
Evidence scope: 252 extended-positive harnesses; historical PASS 185, no exact PASS evidence 67.
Transfer result after per-harness source audit: PASS 184, NO_EVIDENCE 68.

This is a source-level transfer audit, not a new Kani run. Each harness source item and its identifier-resolved verification helper call closure are compared independently; this bounded Python analysis does not expand macros as rustc does. cfg attributes, comments, and import regrouping are normalized. Production/library files outside verify/ are also checked for changes.

Selected transferable PASS evidence source counts:
- P-6 Actions run 40748125754: 184

C3c is preferred only when that harness's own source and helper closure match the target; otherwise the audit tries earlier evidence such as P-6. Rows without a suitable matching PASS remain NO_EVIDENCE; timeout, missing result, neighboring length, and negative control are not PASS.

Reproduce with `python3 research/challenge-8/kani-k1/scope/audit_optin_evidence.py`.
