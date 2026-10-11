# Fresh native C4 bound inventory diagnostic review

Build `310f38b5-5f45-4d4c-bb72-cd3f48ed40c6` used proof/infra
`736691964dd733b67ded1a683efe5d586f5952f0`. It ran 430 seconds
(create `2026-10-11T10:14:49.688428244Z`, terminal
`2026-10-11T10:21:59.276092Z`), bringing the session total to 2061/3600
seconds (1539 remaining). The collector completed successfully with complete
evidence and text logs, but verification was not accepted. The downloaded
archive SHA-256 is
`e1d34905210b47f1d0fb1e7609b95112dca9ef7789fa5a53d05e23582609c9b8`;
1041 inventory hashes were independently checked. See
[FRESH-310F38B5-INDEX.json](FRESH-310F38B5-INDEX.json) and the raw archive
under `allprooflogs/cases/sort4-c1-current-recovery/`.

All nine fresh ZST model gates passed, including the paired source/MIR checks,
nonvacuity and missing-permission controls. Fresh C1 native binding passed;
its normal and direct-unwind false controls failed at their intended assertions,
and its source, extra-body, malformed and mixed-environment admission controls
were retained. These are diagnostic results only: no accepted tool profile,
callable summary or caller proof is established.

The C4 source/MIR/refinement and pre-transform AST identities match the pinned
candidate: verified source
`0f92a609c898df5271cbafd04cea688bf7b46c8b4786f8313b8ff99db995e9c4`, original
source `9628df15e3a42643d671bd1e9f5684e0bdd81162e26ab8233ce704a9657942df`,
normal full MIR `b0da712d2b16c76d1baac91ae69c591ddeab308a2242e196fe876fd27e35e24d`,
readonly full MIR `79c16a30be7b2921ccdaa35c66aac496f236d900130fff72a36b81524e50ef86`,
and pre-transform AST `65b9ddf282ab3b8d123bba3725600528936ff09e236c4261841d61f66cb5ae18`.
The paired support gate passed for `small_sort_general_with_scratch`.

This run gives useful inventory evidence: the C4 positive AST reports
`body=284 locals=239 projections=0 epilogue=0 hrtb=F:T`, while the then-active
root-count gate expected 282. The positive and all five semantic false controls
(normal and four direct unwinds) consequently stopped at
`Fatal error: exception Failure("NATIVE-C4-BOUND: complete native AST/HRTB inventory")`
before admission, post-transform AST and proof. Their classification is
INCONCLUSIVE, not proof negatives. Four admission controls refused as intended;
default-off remained unadmitted but ended in a parse error.

The effective translator was `a1be12ce7800222b25acd67e0766ee66d6290c6d9e451819fe27c51063093a06`.
That is the old-count diagnostic candidate from proof/infra 73669196, not the
corrected source candidate at `8de4cda418c4772009359fbb90e7e7f34836cca0` (expected
translator `66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124`).
The corrected candidate's fresh Cloud result is pending and is not represented
by this run. There is no C4 proof credit, accepted profile, external caller
proof or callable summary.
