# Review: intake fix w13

Reviewed `8860d38558651f7cf2e292d57b06b378c6ad3b94..b25dd39a46ba90b167500997d546a5f2f5bd8f3b` for the four requested files. No CI, compiler, or verifier was run, and this review makes no claim about a proof rerun.

## Result

No actionable finding from this bounded review. The earlier concern about the non-greedy description capture was a false positive: Python's `re.fullmatch` backtracks to the closing quote that satisfies the full record shape, including when the Location line is absent.

I ran a small synthetic decoder check with renderer-shaped stdout for `assertion "x" failed`, once with a Location line and once without. Both parsed without error, retained the exact description and location display, and yielded one property record.

The missing-site path is fail-closed by inspection: malformed, absent, and `Unknown file` locations are stored as `file: null` / `line: null` with `location_display` retained; parsing continues; `validate()` resets `complete` and rejects null metadata even for collector-rehydrated records. Stock inventory/ID/status reconciliation remains in place before completion. Runner failure output reports the terminal `stop_reason` (or terminal state), and failed groups retain `execution.original_exit_code` on per-row `group_original_exit` while converting observations to UNKNOWN.

The added synthetic tests cover absent/malformed locations and collector replay. The standalone check was limited to Python decoder behavior; no broader tests, CI, compiler, or verifier were run.
