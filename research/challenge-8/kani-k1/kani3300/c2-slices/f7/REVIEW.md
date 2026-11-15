# Independent worker14 review

Source: [f7-worker14.md](../reviews/f7-worker14.md), JSON sibling,
g0 commit `c04f1bdc728c1abc3826e7b1a7b3b5c5bddd242d`.
PASS_BOUNDED_STATIC_REVIEW, findings=[]; binds exact F7 source
`8e299aa6243bc5f06a29c51e98aafa9564478220` and its F tree.

CI: [f7-ci-worker14.md](../reviews/f7-ci-worker14.md), JSON sibling,
g0 commit `6ce83576451c28f4549561c0fa6448c6fceff365`.
PASS_BOUNDED_STATIC_CI_REVIEW, no open findings; binds final overlay
`8288537e7c57b04d2462ff0c5bf1af38ab9d4451`.
The reporting metadata finding was corrected to76/28/0/76 before final review.
Inherited20-unit manifest metadata describes prior groups; effective inputs add
F7 six+two and require28 targeted units/76 full compiler units.

Both are static reviews. All new native results, including default/LLBC
compilation and actual mixed-vs-isolated outcomes, remain NOT_RUN.
