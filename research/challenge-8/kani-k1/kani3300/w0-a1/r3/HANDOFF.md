# Worker15 — A1-R3 handoff

One preparation stage from g0 `2ff42c1c8349972ec7ad60a68bbfafd32f903612`.
See TRIAGE.md for the confirmed import defect and limits on the8652-error attribution;
CI-REQUEST.md/JSON for the last-reserve proposal; REVIEW.md for independent review;
PACKAGE.json and CONTROL-CHECKSUMS.json for exact identities; VALIDATION.json for checks.

Local CI package: `e3e9f138b77d81ae7f75d3a6ec910e9c27eb3a8e`
at `/root/kani-fix-ch8-w0-a1-r3-w15`, branch `work/ch8-w0-a1-r3-w15`.
Local std fix: `312ff625b9b3338281d899cca47d72c24d5a2539`
at `/root/verify-rust-std-ch8-w0-a1-r3-w15`, branch `work/ch8-w0-a1-r3-std-w15`.
Both commits use `[skip ci]` and `Tiramisu-Cake <igkharin@gmail.com>`.
G0 handoff identity is the commit containing this directory, printed in the final READY line.

Reconstruction: ci-delta-from-bf81.patch applies to the old CI package; std-fix.patch
applies to the old std A1 package6586; std-test-only.patch applies to frozen70ba and
reconstructs the exact new library tree. Historical R1/R2 artifacts and ledgers were
not modified. Existing unrelated `kani3300/ch8-c-ctl/` was left untouched; concurrent
g0 commits `169dcbf58f` and `45498717e2` arrived during preparation and are preserved.
The shared-index packet was included unchanged by concurrent coordinator commit
`e3fce08411b8a222fc7e7b6d7e9969df3cbae407`; its unrelated ledger/task edits belong
to that coordinator. This worker did not edit them. Final closeout uses a separate
path-limited commit and preserves this history.

Next authorized stage belongs to the coordinator: verify exact local package hashes,
review and current reserve/slot/budget, then choose whether to publish and dispatch
the one R3 request. This worker creates no trigger and makes no publication.
Read bounded diagnostics first; on compile failure the remaining std rows must be
NOT_RUN. If a further blocker appears, retain it and stop; there is no automatic retry.

Runtime compile/verifier status: **NOT_RUN**. Independent proof credit:
**NOT_ESTABLISHED**. Push/CI/publication/ledger changes: **NONE**.
