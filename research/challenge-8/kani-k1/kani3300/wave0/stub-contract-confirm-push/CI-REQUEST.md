# Push-only stock-main stub/contract confirmation request

READY_FOR_SAME11_DELTA. Task `task54c3b8f7519cc4f73e6cf5dd348cfda6a0f8cdce` prepares a trigger repair. Confirmation remains NOT_RUN; this packet authorizes no publication, CI, workflow enabling, accounting or reservation. Owner reference: item1 29/30, item2 11/17, total40/47; S2 run44375519132 executing per owner. Fast OFF and current settings unchanged.

| Identity | Exact value |
| --- | --- |
| Stock HEAD | `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e` |
| Stock tree | `09b828b47c93e90e140e8c41f9048109a2f4a786` |
| Stock parent | `a3c8b8610739aab7d2c864bd4021086a5e7c0d94` |
| New control HEAD | `e9f0e9a38bf679fead630c44eec3bc08ebb9202b` |
| New control tree | `76ffe2048b88d45c759d0b297362c2c4981e7ad6` |
| New control sole parent | `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e` |
| Canonical request SHA256 for this candidate | `45b074506bd6e40e2f25bc1fc3603d1491bbbfda4c7a4295e40ec785cecb651c` |
| Profile SHA256 | `ceb930a5b7764799880ac48ad6318bbaf6e14d6af70ea98abbe9da82107af148` |
| Workflow SHA256 | `720cc99642dfdce815773145d0d37820c29cf1f8e85b4cec87e70247dfff8edd` |
| Full control patch SHA256 | `711ec08bea2995a438c12c717531f99a7eba9f54d6d580f8ccc40d7d6e858de9` |
| Trigger delta patch SHA256 | `bdfd63493519d96557c924aaef3b57eaf179cbf24489707f021d7d1c3fe4b1b8` |

`.github/workflows/stub-contract-confirm.yml` has exactly `on.push.branches: [stub-contract-confirm-ci/**]`. It has no manual/scheduled/other event. The obsolete slow-tests workflow is removed on this isolated control only; the other reviewed workflow suppressions remain. Fork slow-tests.yml is disabled_fork and has a cron per owner: it must remain disabled. Default branch and enabled states are unchanged.

The two depth2 checkouts, stock setup action, cargo build-dev, three separately selected native slots, environment/caps/oracles, service process handling, diagnostic/export completeness, compact schema and replay functions retain the reviewed behavior. `INVARIANCE.json` pins byte/AST/YAML equality. Source/compiler/fixture/service/classification changes are absent; the clear-error proposal and F4 fix stay excluded and unapproved.

Runtime requires the GitHub push context and payload and binds event after/ref/repository/head_commit to actual checkout HEAD/tree/soleparent. Missing context and legacy dispatch input sources are errors. The request uses the same canonical stub-contract-request-v1 scheme, computed from actual HEAD/tree/profile and frozen stock identities. The review packet and external final-head gate supply the expected reviewed identity; runtime records the actual push identity. There is no embedded self-hash or environment override for an expected head/tree/request.

Publication topology is specified in PUBLICATION.md and CI-REQUEST.json. The proposed exact ref is `refs/heads/stub-contract-confirm-ci/w15-push` in Tiramisu-Cake/kani. The unpublished candidate is a no-skip direct child of main. A same-tree direct sibling is possible only with the same stock parent/profile and an updated actual HEAD/request binding. `check_push_head.py` first derives that final request, then accepts only its exact expected digest. An unchanged candidate request cannot be reused for a sibling.

Sequence: READY → SAME11 narrow trigger/identity delta APPROVE → final-head/request gate and UPDATED GO-request for the actual non-skip head → separate coordinator/owner publication decision. The old dispatch GO is superseded; the old 5ba4 package, 125 control and 121893 review remain immutable prior-object evidence. There is no current attempt or budget mutation.
