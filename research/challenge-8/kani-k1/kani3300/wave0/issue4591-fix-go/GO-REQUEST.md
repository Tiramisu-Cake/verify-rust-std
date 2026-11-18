# #4591 — согласие на один полный standard push-CI

**ROOT AGREE; READY_FOR_DELEGATED_COORDINATOR_GO.** W11 review `0f4e2830d9053cd3b031c36b9efd64a4c3a9160d` — APPROVE,
W11-01 CLOSED. Root rechecked27 author files/26 hashes and11 review files/10 hashes,
exact source/tree/sole parent, CI request and unchanged new-main protected bytes.
Connected upstream main is still `969f4648980a8e66cd0ca32fd3e714a55ac32cef`. Budget reference `243f3301a70047af08425d2ab25ce96dce82c6ae`:
current item1 30/31, item2 11/17,total41/48; prospective item1 31/31,total42/48.
No accounting, reservation, CI or publication action occurred here.

Package `ad50aaeaabe8b3a84dbf64a88d0214a16f4ee316`, source `3a770b5db51ba07acffce3483bde0901e6533f3a`, tree `7a3d5c05b5d663d515c198b2bfa7c4926ae133ac`. The local candidate has
[skip ci] and MUST NOT be pushed. User coordinator creates a new nonskip SAME-TREE
sibling with sole parent `969f4648980a8e66cd0ca32fd3e714a55ac32cef`;969f..final contains exactly that one commit.
Record actual final full SHA, branch and read-only gate result before push:

```text
python3 /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/wave0/issue4591-fix-main-r2/check_push_head.py /root/kani-issue4591-fix-main-r2-w15 FINAL_FULL_SHA
```

Require exit0/status MATCH/errors empty, unchanged main immediately before launch,
and a non-main future PR branch without an open PR. No force push or push to an
existing open PR branch is authorized. Final head/ref/run IDs are NOT_CREATED.

Launch once: unchanged `kani.yml` (all5 regression OS entries plus benchcomp,
perf,LLBC,docs), `format-check.yml` (both jobs), `deny.yml` (audit):12 native
instances. Keep native settings/retries; no extra workflow rerun, custom subset,
cron enablement or dispatch. Release/std/bench/metadata PR workflows remain
deferred to upstream PR under owner scope, never claimed PASS here.

Record all3 run IDs/attempts, every job/matrix result and exposed checkout/named
regression evidence. Missing/red/cancelled/skipped results retain native status;
new advisory/infrastructure/performance classifications need new evidence.
No old F4 outcome is transferred. All new current-main/fixed native results remain
NOT_RUN until this CI;407+237 static/mock checks are not typechecking/proof credit.
Explicit same-target PFC/verified/ordinary overlap retains prior behavior.

User coordinator launches after this consent under night delegation. PR/issue/
comments/public push to open PR branches still require owner approval. S3 remains
independent and blocked on its own controller repair. Exact machine-readable
bindings/conditions are in GO-REQUEST.json; root audit in ROOT-RECHECK.json.
