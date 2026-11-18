# Review validation

Run `python3 validate_review.py` from this directory. Result: PASS.

The exact author validator replay passes 15 static/synthetic groups and 14
mocked mode/cfg/selection calls. Its sole packet write is intercepted and the
report reproduces the recorded author VALIDATION.json exactly; the original
pending-review14 field remains author data. REVIEW.json records independent11
approval. Native probes remain mocked; actual subprocesses are Git and bash -n.
Patch replay uses temporary isolated indexes. The real source index is unchanged.

Additional independent checks bind all 17 package files to the package commit,
task issuance, manifest, committed source hashes, prior review commits and
reference hashes, main/workflow invariance and exact source/tree/direct parent.
A mocked valid final-head sibling passes; 15 invalid candidate/tree/parent/range/
skip variants reject. No final commit, trigger or publication is created.

VALIDATION.json records checks, hashes and counters; AUTHOR-REPLAY.json preserves
the reconstructed author report. All author package bytes, clean source/HEAD and
real index hash are checked again after validation. Runtime/compiler/performance/
new CI remain NOT_RUN; future actual final-head identity gate remains pending.
