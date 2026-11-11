# KANI3300 G1R — PRE-BUILD REVIEW
PREPARED, NOT AUTHORIZED; Runtime Codex; one static stage; Cloud spent/reserved this stage $0/$0; no build/dispatch.
Kani candidate/production repair: `3d085249c9c6c49a9c2e5747e2167d629748fb70`; parent `45d0300e054345b4f6bdf89528195ee7c5dba8a5`; branch `fix/kani-3300-g1`; author Tiramisu-Cake; local only, no Kani push.
Delta: exactly two `.shape().size` → `.shape().size.bytes()` fixes in Repeat Move and intrinsic Forget; no semantic/test changes.
Sweep: entire production `657c2b245..HEAD`, five files, exact nightly API sources; see COMPILE-SWEEP.md and API-SOURCES.json. Compiler/native NOT_RUN; proof credit NONE.
Native pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; tooling KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` unchanged; slug kani3300, owner k1-merge, request kind kani-tests.
Both reduced patches contain complete P1 + G1 production against full f046; all seven production files equal candidate. Base657c production equals c39; no CMP2.
Each request preserves its original 20 selectors, flags, test timeout 150s, fixture/helper bytes and complete goldens. TEST-MANIFEST.json retains all expectations; current native outcomes NOT_RUN.
| Package | Request SHA-256 | Patch SHA-256 | Applied tree | Diffstat bytes |
|---|---|---|---|---|
| A | `996eaa06da3e57d4d44bcc962e9f3301265f4eb9301cd30b97489ce67a051bcd` | `47e625bab9d19dab22e4ec0682ecd4f561a180c022e7c09e29b205d7abcb7339` | `2fdd891e1c8e7d9fbaf51a6c7170d5dea6f127c5` | 3013 |
| B | `faefa40aa4777ecd13a9813f26bd91d7b44b75bf35195523da254674176f45a8` | `c9ddce47cae76e9b9f462e8bcac94c73f70c0e8c32438f35f9ff1d7539117767` | `8f152bac27f8ff1d7fba45f57dc6a0ebeb348867` | 2734 |
Artifacts: RUN-REQUEST.json / RUN-REQUEST-B.json; kani3300-g1r-a-build.patch / kani3300-g1r-b-build.patch (+ .sha256); APPLIED-INVENTORY-A/B.json; preflight-a/b.json.
Full source patch SHA-256 `5df3a2654846414b09f9fa3cd94b6defcd071f13374a0a0910a0ca8a4fde15b7`; build patch reduction affects test selection only.
Preflight: unchanged KT2 validate + prepare-kani PASS; explicit git apply --check --index on clean exact f046 PASS; all selected source/golden/helper hashes and production bytes match candidate.
Validation: permitted rustfmt wrapper --check --edition 2024, repository config, complete G1 changed Rust sources; git diff --check PASS; tests unchanged from 45d0300e05 and P1 regressions unchanged from 657c.
A: harness_timeout_minutes=24; reserve (24+30) × $0.0135 = $0.7290 ≤ $0.7325; prior G1A $0.0675 + reserve = $0.7965 ≤ cumulative cap $0.80. This is a proposal, no reservation made.
B: harness_timeout_minutes=29 unchanged; (29+30) × $0.0135 = $0.7965 unchanged proposal; separate owner GO still required. No B authorization inferred.
Independent review: REVIEW.md binds exact candidate, repair delta and full sweep; review packet/spec hashes are in review-packet/metadata.json.
No request installed, phase/slot/ledger opened, Cloud reservation/submission, Actions/PR/issue/comment, or Kani publication. Historical G1A failure/ledger left intact.
Open: actual compilation/-D warnings/native outcomes await separately authorized dispatch; inherited P1 limitations and full regressions retain prior status. Stop after PRE-BUILD REVIEW handoff.
