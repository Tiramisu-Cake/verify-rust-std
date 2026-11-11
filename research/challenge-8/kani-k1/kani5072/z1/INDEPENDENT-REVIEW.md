# Independent static review — KANI5072 Z1

Reviewer: independent GPT-6 Luna HIGH, separate context; no nested delegation.
Final Kani candidate: `6fba5bf9254f4954dd6dbce6ece8ef159004e905`.
Baseline: `f046b70644e113be0df9c22c2e6ea44a65a57566`.
Candidate tree: `f3791c8eb38f92bc331bf8b8c63cda0bc22b9db4`.
Reviewed diff SHA-256: `aa0322469151cc7a7c86890b8d50e20b36e61b6d77c90f819e8b3c6ef5341aa3`.
Final spec SHA-256: `45bf9368f4d007cf7c9ca5043cf2cdfccb29bcfa33d7033e23fcc38e2bc8b46a`.
Final packet SHA-256: `0f5c6c7a29162573f59d1e54e4e8c187b84ed2a76a6ebd0b4abc9e1c06837f9b`.
Patch SHA-256: `380b22438bbdd115d98aacc81f97a49cce24e9abf77fa176c32067210e8ff238`.
Packet: `/tmp/kani5072-z1-review-packet-v3`; reproducible via committed `review-spec.json` and local Kani candidate.
`smallsort-session review check` passed with the expected candidate/spec/packet identities.

Initial finding: the uninhabited golden depended on whether MIR provided a return target.
Resolved: both returning and non-returning uninhabited-ZST paths now emit the same explicit SafetyCheck message.
Delta finding: the no-target guard needed to establish uninhabited layout rather than rely only on zero size.
Resolved: the guard requires both ZST and `layout.is_uninhabited()`.
Final reviewer verdict: no remaining static blockers found.
Alignment remains required; null inhabited ZST is allowed by the pinned contract; non-ZST lowering is preserved.
All native tests remain NOT_RUN pending exact-packet coordinator GO. Static review grants no proof credit.
