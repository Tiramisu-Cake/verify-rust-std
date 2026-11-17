# Intake13 handoff

READY for coordinator-issued offline acceptance, not acceptance itself.13 complete groups/33 rows plus2
explicit UNKNOWN cell observations; no14/14 COMPLETE claim. RESULT.md explains findings and limits.
No dependency on retry/review; source99e/tool0aac/run44095954742/attempt1/request77ae…1431c7e are frozen.

Inputs for the next offline stage:

- INPUTS.json, CI-REQUEST.json and ROLE-MAP.json: exact pins and fresh expectations; parent pins hash included.
- collected.json:35 declared rows, source outcomes, full complete-group stock partitions, rich/native refs,
  binary snapshots, original exits/exceptions, group metrics and explicit per-root UNKNOWNs.
- runner-collected.json: unchanged21592884db collector result before adding the two read-only diagnostics.
  missing_groups=[cell-u34] means no admitted complete cell payload; its diagnostic refs do not fill that gap.
- evidence/<group>/{export,properties,binding-metadata,receipt}.json and compile/receipt.json:13 full
  structured groups. Export/rich/native metadata bytes are exact; receipt projections omit bounded stdout/stderr previews.
  Compact envelopes retain original embedded identities; no raw logs or ZIP transport files are retained.
- artifacts-metadata.json/jobs-metadata.json/run-identity.json, artifacts/*/zip-integrity.json,
  PROVENANCE.json and MANIFEST.sha256: GitHub ZIP/member/native identities, hashes and integrity attestations.
- LABEL-COVERAGE.json:111 fresh diagnostic labels (106 found,5 partial UNKNOWN) and16 semantic candidates,
  including all multi-instance candidates. Qualification remains PENDING; do not reuse historical IDs.
- LOCATION-EXCEPTIONS.json and COMPARISON-S1-07.json: exact approved-tuple comparison, source/config deltas,
  all fresh inventory/status changes. Use the existing exact tuple/U/PFC/role policy unchanged.
- TIMING-COMPARISON.json/md:35 exact common logical pairs, completed cohorts and one censored timeout;
  exact input hashes, joins, configs, raw durations, limits/deltas/ratios. No future retry evidence included.
- cell-diagnostic/:immutable commit929f21bb1f, hashes pinned in PROVENANCE.json. Source TIMEOUT and source
  SUCCESS are diagnostic observations within a FAILED group, both collector statuses UNKNOWN. Stable inventory
  is unavailable; unstable full rich301-record inventory is not retained by the diagnostic projection.
  Do not infer zero properties, regenerate RESULTS, promote either row, or block the13-group acceptance input.

Replay from this directory (Python only; no compiler/verifier or network):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 intake.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_intake.py
sha256sum -c MANIFEST.sha256
```

intake.py reuses collect.py and dependencies byte-pinned to executed trigger21592884db under replay-control/;
its wrapper supports13 complete groups plus immutable partial references. Replay requires existing local Git
objects in /root/kani-ch8-s1-08-w13 and /root/verify-rust-std-ch8-s1-08-w13 for static pin checks; no HEAD
mutation or full runner is involved. MANIFEST excludes itself and immutable cell-diagnostic/, whose own
manifest/commit and complete read-only hash map are checked separately. Running the replay reproduces
machine projections; RESULT/HANDOFF and replay test receipt are fixed reviewable reports.

Validation: VALIDATION.json and ADAPTER-TESTS.json.8 focused synthetic tests cover timeout censoring,
null/missing/wrong-type/NOT_RUN duration inputs, zero baseline, incompatible domain, cohort isolation,
reviewed label metadata, exact inventory old/new naming and partial-group status/identity preservation.
All checks PASS. Offline admission PENDING_OFFLINE; proof credit NONE. No ledger or external writes.
