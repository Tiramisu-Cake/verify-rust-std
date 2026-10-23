# Independent N4 admission and timing review

Reviewer: independent Codex review, no nested delegation.
Decision: scoped GO to publish this candidate and dispatch the authorized exact shape3 Build; no formal proof credit.
Baseline: `4837468689f52f464da86f5057efd70d9fa90d88`.
Candidate: `6ea689b7e479474f84d71c3a08a64cdfcd44bb6a` (tree `cbc51fda79cdb0599981dfec3dbbb1aae18c5baa`).
Spec SHA256: `8c977524cbb0c6f606dd08944d2e3b4235bda64180db26c1f1b18d681b3376cc`.
Packet SHA256: `2a2bd97df66af199e3c7019272e381214a4670c8491492bbaebfd3238e9828a0`.
`smallsort-session review check` passed for the exact candidate and spec identities.

No blocking finding. N4 phase, lane, phase dates, 3600-second ledger, report reserve, and profile SHA `72dba8447c2db3735df144b8f30ad07f4b2f453ea4c04e1019fc81dcb91f3890` agree. The recipe and runner select that N4 profile; source SHA/blob and call counts remain pinned, and the profile pins official stock VeriFast 26.09 with its existing archive and console hashes and no patches. N3 ledger/profile history and coordinator bytes are preserved.

The 600-second case limit is justified as a bounded next measurement after the prior final wrapper call at 389.097 seconds: it adds 210.903 seconds (about 54%); it does not claim 600 seconds suffices. The 975-second Build envelope equals 600 case + 120 setup + 15 margin + 240 report reserve. The submit gate also enforces a 60-second queue allowance against the main deadline. Controls retain the 600-second full exact prefix for membership/order, 180-second missing-law case, seven classifier controls, and the registered 780/600-second control cases. Required regressions remain registered. Existing preflight dependencies are unchanged, so no duplicate preflight is needed.

The candidate changes no SmallSort source, N13 proof generator/ranker, or coordinator implementation; the diff adds no mathematical, ownership, unwind, or trust changes. Shape3 exact acceptance, controls, compatible regressions, and all proof credit remain open pending Cloud evidence.

Validation: packet identity check passed; `git diff --check` passed; direct diff checks confirmed the source, proof generator/ranker, and coordinator are unchanged. The 23 tests in `test_network_n13_client.py` and `test_run_cloud.py` passed. No local generator, compiler, or verifier was run.
