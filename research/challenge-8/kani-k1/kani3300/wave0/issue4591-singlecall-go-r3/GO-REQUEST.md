# #4591 r3 — reviewed GO-request, HOLD for owner budget

**HOLD_FOR_OWNER_EXTRA_ITEM1_GRANT.** Independent review
19079d13154e3b814a3abeca9d9b38f0188b731d APPROVE, zero blockers. Root conditionally
agrees to ONE complete standard push-CI after explicit owner+1 and final gates.
Current31/31 item1 is EXHAUSTED; morning+1 NOT_GRANTED. This HOLD grants no CI,
rerun, push or publication and changes no ledger/reservation. Current reference
31/31 +11/17=42/48; recompute from latest owner ledger at actual launch.

Exact author package5162af47e12611de4102ba20b0135b17c1d79d7d,
sourcef82934ca97caaa1270d5279054aa950173868be5,
tree2ff34bc99ec3fe63579202c196f0ca288e318919,
soleparent published6fca00af805b5c62b58e3e3f29eef183d6939907.
Root author38files/37hashes and review17files/16hashes match; compiler and standard
workflows remain base bytes.330 independent static checks/141 author replay
checks and three patch replays passed. All repaired native outcomes NOT_RUN.

Both fixtures now perform one selected caller-PFC Check with nested provider
Assert. Separate provider Check/verified controls remain. This preserves core
ordinary-stub behavior but establishes no general mixed provider-PFC alias
support. Original failedCI and all static approval history remain unchanged.

After owner grant, create a NONSKIP SAME-TREE sibling with sole6fparent;
969f..final must contain exactly old nonskip6f followed by new nonskip repair,
excluding skippedf829. Actual final head NOT_CREATED. Branch
fix/stub-contracted-function advances fast-forward, no force. Connected current
main969f and remote6f MATCH at root finalization; recheck immediately before
launch, return drift to root. Run author check_push_head.py against actual fullSHA
and require exit0/MATCH/errors[] before separately authorized coordinator push.

One full native bundle: kani.yml all5 regression OSes/all other jobs,
format-check.yml bothjobs, deny.yml audit,12instances; retain native settings.
PR-only release/std/bench remains deferred. No customworkflow/dispatch/cron/
subset/automatic rerun. Owner publishes PR/issues/comments; root performs no
compiler/Kani/CBMC/fullrunner/CI/push/accounting. Exact machine bindings and
remaining gates are in GO-REQUEST.json; source/coverage/native limits remain.
