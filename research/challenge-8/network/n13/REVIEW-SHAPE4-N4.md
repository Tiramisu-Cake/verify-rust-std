# Independent shape4 generator delta review

Reviewer: independent GPT-6 Luna HIGH, no nested delegation.
Decision: scoped GO for this shape4 candidate and the authorized Cloud experiment; no proof credit.
Baseline: `fb0fec4ebabea55c85e2e9e76e4812de50863279`.
Candidate: `04f7ea1d14bd2ab5b66338cbc24631dd2f4fd82f` (tree `31ed263ed07c4582c602480b5512acb1ad119047`).
Spec SHA256: `a17f1137330fc8f99e8bcc78e03f44d5e2cbd17a42ba9293e092120ed12e9e09`.
Packet SHA256: `e58fab4bcad49e51df66f29af865e36ca8b6bc7b62e60d39c28e5c6934237691`.
`smallsort-session review check` passed for these exact candidate and spec identities.

No blocking finding in the scoped delta. The only changed file is `prove-ranks.py` (13 additions, one replacement). For exact N13, `network13_exact_result(rel, q)` is defined with precisely `full_post(exact_domain)`: 13 output-membership posts, 12 adjacent-order posts, and the full arbitrary-`q` occurrence-count equality. Its checked producer calls the unchanged `network13_finite_swo_export_packed`, then closes that result predicate. The public `network13_finite_swo_order` signature and pre/post remain unchanged; its body now calls the producer and opens the predicate before returning. No postcondition is assumed or dropped, and the exporter, composition proof, source schedule, negative controls, classifier controls, profile, runner, client, and coordinator are unchanged. No axiom or bodyless bridge is added.

This is a proof-structure experiment, not evidence that verification completes: the 600-second shape4 case may stall at the helper call, predicate close/open, or final post. Timeout remains inconclusive. The stock VeriFast 26.09 and pinned source/profile remain unchanged; no local generation, compiler, or verifier was run. `git diff --check` passed. The packet records the 15 runner/admission and 11 client synthetic checks as passed.
