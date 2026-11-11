# RESULT-KANI3300-CMP1 — PRE-BUILD
Status: PREPARED; native/core NOT_RUN; dispatch CLOSED pending accepted U3B/PFC boundary and exact coordinator GO.
Full Kani candidate `6ef9fd72066443f7f113440ba32f77f310520a93`; branch fix/kani-3300-cmp.
Full tree `97159e7c2d7ce369fb7cf7fee60c58002a7a2610`; all tests retained in clone and full patch.
Build subset commit `5bd2d2bf4b7702b9a6eac0051e705c01c0d4f609` (local derivation; published patch is canonical).
Build tree `a85582af9753e386075f3ee11d012b7777ac5d98`; production/selected fixtures equal full candidate.
Build patch SHA256 `c819f200d3f995811fe66589f8cbd0593fe05deb8a5231442efec4f87ef295ec`.
Request SHA256 `87e38d8430faa561cf7f3f22a5194346a4a128b5f28331a38588b13990e77b5a`; full patch SHA256 `481c01624dcc36d0820d8f66912c28e074f0feaa28e246a8976efec54aa12a1c`.
Pin f046b70644e113be0df9c22c2e6ea44a65a57566; tooling 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c unchanged.
Invariant: disjoint target R/S/P partition; typed R reads retained; complete S transfer; exact P clears; indirect whole assignment Unsupported.
Diffstat CMP1−v2 production: 4 files, +606/−15; ghost-state/SKIPPED_ITEMS unchanged.
Luna HIGH: no remaining identified production blocker after localized fixes; static only; see REVIEW-CMP1.md.
Static PASS: fresh exact-pin apply/tree, validate20, rustfmt, scope/blob/lane equality, tooling117; pinned diffstat3179<=4096.
U3B source-report9f964706: 7 PASS/2 ERROR (on-uninit PFC OOM); production=v2; acceptance/PFC boundary OPEN.
Budget CMP1: spent$0, reserved$0, proposed$0.540, cap$0.60; no Build submitted.

|offset|selector suffix|intended / actual|
|---:|---|---|
|0|maybe-uninit-wrap-u3-intoiter|SUCCESS / NOT_RUN|
|1|compound-cmp1-positive|SUCCESS / NOT_RUN|
|2|compound-cmp1-empty-negative|specific FAILURE / NOT_RUN|
|3|compound-cmp1-overwrite-negative|specific FAILURE / NOT_RUN|
|4|compound-cmp1-call-negative|specific FAILURE / NOT_RUN|
|5|compound-cmp1-projection-negative|one SUCCESS + four uninit FAILURE / NOT_RUN|
|6|compound-cmp1-padding-negative|specific FAILURE / NOT_RUN|
|7|compound-cmp1-layout-unsupported|union, enum, nested-MU, nested-union, indirect: each Unsupported / NOT_RUN|
|8|compound-cmp1-no-mir-unsupported|specific FAILURE / NOT_RUN|
|9|maybe-uninit-wrap-u3-positive|SUCCESS / NOT_RUN|
|10|maybe-uninit-wrap-u3-padding|specific FAILURE / NOT_RUN|
|11|maybe-uninit-wrap-u3-source-read|specific FAILURE / NOT_RUN|
|12|maybe-uninit-review-positive|SUCCESS / NOT_RUN|
|13|maybe-uninit-review-overwrite-copy|specific FAILURE / NOT_RUN|
|14|maybe-uninit-buffer-u3b-pfc-positive|SUCCESS / NOT_RUN|
|15|maybe-uninit-buffer-u3-frame-negative|specific FAILURE / NOT_RUN|
|16|maybe-uninit-buffer-u3-no-mir-unsupported|specific FAILURE / NOT_RUN|
|17|maybe-uninit-buffer-u3b-pfc-positive-no-uninit|SUCCESS / NOT_RUN|
|18|maybe-uninit-buffer-u3b-pfc-negative|specific FAILURE / NOT_RUN|
|19|maybe-uninit-buffer-u3b-pfc-negative-no-uninit|SUCCESS / NOT_RUN|
Core proposal after native+new GO: U8/U9 plus U1/U2,U6; preserve original assertions/covers/domain/flags; exact source paths still to bind.
