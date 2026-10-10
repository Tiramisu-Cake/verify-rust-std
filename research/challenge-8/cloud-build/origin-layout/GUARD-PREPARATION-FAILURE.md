# Minimal guard preparation refusal — saved evidence

Build 282324ae-a918-4bc6-b73b-e2861f2596e5, proof=infra
a287a0f2d1b12e3a209b8d69cb66516acdd53f50; archive SHA256
c05f8fe9f1df66f5a276884e5121bf318071968d5a1f761d3c7e7e8847cbbc54.
This is a preparation failure before all nine guard controls, not an intended
semantic negative. No guard fixture was created or sent to the exporter.

`guard-storage-controls.py::run` injects POST after the FBC pointer-identity
ladder, then tries to remove baseline manifest ghost fragments first. Fragment
index4 includes that ladder, so POST splits its bytes and its count becomes0.
Saved-data replay confirmed all three baseline anchors count1, the fragment
count in baseline is1, and its count in the modified source is0. Fragment size
2867 bytes; SHA256 f5f0d175f1a138929c2725572b6d00b3db3c3a73630cf42e7bec21d4f996bf86.
The bare AssertionError is reduced to `hosted one-cell proof refused:` by the
outer handler; the metadata/logs retain the causal inputs.

Reproduction is pure saved-byte processing: read the original, verified and
metadata.json positive files under allprooflogs/checked-minimal-bridge/
concrete-u64 from the verified archive; apply the committed ALIGN, FACTS and
POST substitutions; check manifest ghost_fragments in their current order.
The first count!=1 is index4. Do not execute run() or execute_case locally.

Next repair: account for inserted ghost fragments before removing baseline
fragments (also check the full mutable FBC entry-false insertion), retain exact
once-only removal and final byte equality to original. Give failed anchors
explicit diagnostics. Replay all applicable fixture preparations against saved
source, then run fresh exact-SHA Cloud bridge-minimal. No supplied extent or
separation, semantic guard change, contract weakening, or proof credit follows
from this repair. No repair/Build was performed after the main deadline.
