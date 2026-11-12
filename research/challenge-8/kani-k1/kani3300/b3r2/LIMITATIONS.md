# Limits and follow-up boundary

- All new A/B/C setup, compiler, CBMC, verdict, cover, exit and exception observations
  are NOT_RUN. Static review and formatting are not runtime or proof evidence.
- A's Node-first source shape does not establish retained MIR/GOTO root order or
  an actual v2 ICE. Coordinator must identify the retained graph and original
  failing stage/source if present; no reproduction means UNKNOWN until explained.
- The rustc layout equality changes only whole-ZST padded payload selection.
  Nonzero nested-ZST payloads and no-padding arms keep the prior representation.
  B may reveal remaining limitations or new regressions; no result is guessed.
- B inputs are research probes with semantic expected SUCCESS, not active ignored,
  crash/Unsupported goldens or known PASS tests. Source shapes, writes, reads and
  layout assertions are recorded in ASSESSMENT-B.md and the manifest.
- Base PASS -> v3 FAIL/ICE is a blocker/new regression. Base and v3 failure does
  not justify claiming repair; request a separate bounded repair or document the
  measured limitation. v3 PASS permits a later decision on active-suite promotion
  with observed goldens. B follow-up is a new session after coordinator results.
- New A/C expected files use existing cover-success patterns as desired output;
  compilation, warning-free status and actual golden compatibility are NOT_RUN.
  Each isolated harness needs its own cover description/status and assertion
  verdict. One global SAT line cannot establish all-harness non-vacuity.
- Covers establish reachability only, not correctness or representation/type binding.
- C full-extent byte writes precede typed copies; reads use initialized data arms
  plus logical ZST projections. ZSTs carry no physical writes. The aligned-array
  fixture checks Rust type alignment and takes logical element references through
  size_of_val; it does not measure or assert an address modulo that alignment.
- Old seven controls are preserved byte-for-byte, without new cover goldens.
  Preserve their individual outcomes; do not attribute new cover evidence to them.
- No claim of default success extends to the separate uninit-checks panic track.
- No global struct lowering, ABI, offsets, memory model or recursive representation
  rewrite is included. No CBMC minimum, issue closure, or independent B1/B2 credit.
- Kani candidate remains local, unpublished. Only the coordinator may push/run CI.
  No PR draft was changed and no issue, PR or external comment was published.
