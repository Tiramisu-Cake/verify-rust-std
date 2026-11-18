# Reviewer validation

- `python3 -B tests/review_checks.py`:330 PASS, recorded in REVIEW-CHECKS.json.
  Independent package/frozen-history pins, compiler/full workflow invariance,
  source excerpts, declaration/oracle inventory, private-index patch replay,
  fresh YAML projection and actual invalid-final-head rejection checks.
- Exact delivered author `validate.py` rerun against the pinned clean source:
  141 PASS, recorded in AUTHOR-VALIDATION-REPLAY.json. Its bounded source-call,
  guard, arithmetic, mode/postcondition and reachability mutations distinguish
  published6f's defective fixtures from both repairs.
- Three actual independent patch replays reproduce
  2ff34bc99ec3fe63579202c196f0ca288e318919. Replay index and newly written objects
  live in a private temporary Git repository; the source repository is read-only.
- Source diff whitespace checks pass; all38 delivery bytes and37 manifest seals
  match; all44 frozen references match; source worktree stays clean.

Initial reviewer-checker development found only a representation mismatch:
SOURCE-EXCERPTS stores joined lines without the range's final LF and omits
redundant blob fields on four fixture entries. The final checker compares that
exact line representation and derives each actual Git blob, checking any
declared blob. No delivered data was changed.

These checks do not run Rust syntax/type/name analysis, expansion, MIR,
compiler, rustfmt, Kani/CBMC, verifier or full runner. Python source models
cannot establish actual FnDef/closure binding. The configured CBMC excerpt is
source evidence, not an attestation of the failing native executable.
Native metadata is the committed compact connected projection, without a new
service query. No raw/full log, archive or GCS object was read.

Final-head metadata mocks and actual rejected heads do not establish a valid
future final head or authorize CI. All repair native results remain NOT_RUN;
the old6f native failure and unrun negative suite retain their original status.
