# Validation

PASS — static and isolated Python fixtures only. Replay:

```sh
python3 research/challenge-8/kani-k1/kani3300/wave0/f4-fix/validate.py /root/kani-f4-fix-w15
```

The script checks Python AST/guarded entry point, shell syntax and executable entry point;
replays the new oracle on observed compact main results; checks parser compatibility using
explicitly reconstructed export envelopes; accepts a labelled synthetic expected-fixed result;
rejects semantic composition changes and lost unsafe controls; checks parser and mocked probe
success/error/timeout/signal/spawn/missing/null/wrong-type/NOT_RUN/partial/mismatch cases;
checks exact fixture identity, source lifetime wiring, preserved workflows/checks/scripts,
clean direct-parent source identity and nine-file scope; and replays the patch through a
separate Git index to reproduce the committed source tree.

Details: `VALIDATION.json`. Generated result data carries no proof credit. The malformed-result
cases invoke Python functions with fixtures; the probe tests mock `subprocess.run`, invoking no
native compiler or runner. Existing historical intake/ledgers are read-only.

Compiler build, cargo/rustc/Kani/CBMC/rustfmt, complete regression runner and CI: **NOT_RUN**.
Independent review14: **PENDING**. Fixed runtime PASS and performance/RSS: **UNKNOWN / NOT_RUN**.
No subagents, model changes, publication, messages, reservations or ledger edits occurred.
