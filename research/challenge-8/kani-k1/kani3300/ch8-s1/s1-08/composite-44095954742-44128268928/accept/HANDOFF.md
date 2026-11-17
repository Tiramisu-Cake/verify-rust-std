# W11 composite candidate handoff

READY_FOR_INDEPENDENT_REVIEW. Exact candidate is the g0 commit containing this
handoff, ACCEPT.json, INPUTS.json, ORIGIN-MAP.json, COMPATIBILITY.json, replay.py,
test_replay.py, MUTATIONS.json, VALIDATION.json and ACCEPTANCE.md. Resolve with
`git log -1 --format=%H -- <this accept directory>`; the full SHA is returned to
coordinator after the scoped local commit. No self-referential commit hash is
embedded in generated receipts.

35/35 rows QUALIFIED (33 original + 2 atomic retry), compatibility PASS;
127 roles =111 labels +16 fresh semantic bindings/sets, 54 supplemental sites,
113 required SAT covers, 439/439 U records allowed, 22/22 PFC chains,
8/8 exact negative oracles, 8/8 companions, 4/4 unions. 39 targeted mutations PASS.
Original431 U records include429 checks +2 covers; retry has8 checks.

Task dad394c5948af7dde9f6195b5e7d461f6b040a8d; original intake
6d300f3ab9801c808612b562588af06e0f7b4ff9; retry intake
0beb690dfa99e4524de71b2ffc311fe7d7556cc1. Pins are not replaced by current HEAD.
Full per-origin/evidence identities and immutable helper dependencies are in
INPUTS.json and ORIGIN-MAP.json. Historical inputs/receipts remain unchanged.

Run from any directory with Python3:
`python3 -I -B <this accept directory>/replay.py`
Default rehashes pinned inputs, separately replays exact original and retry
collectors, rebuilds all gates, and compares ACCEPT/ORIGIN-MAP/COMPATIBILITY bytes.
No compiler/verifier/network/full runner; no input writes. `--write` is explicitly
limited to those three outputs in this directory. The targeted test script writes
only its MUTATIONS.json receipt in this directory.

W14 must independently review the new adapter and receipt at the exact candidate
commit before final admission. Independent review: PENDING. No self-admission.
No new CI/rerun/push/source/control/ledger/budget authority.9/14,total35/40 retained.
Original run FAILED; no same-run14/14, uniform600, aggregate runtime, fit600 or
causality claim. Only bounded source-reported S1 observations; B1/B2/general credit NONE.
