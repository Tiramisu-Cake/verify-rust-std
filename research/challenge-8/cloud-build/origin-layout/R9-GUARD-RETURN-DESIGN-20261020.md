# R9 first gate — native failed-return/resource binding

Defect: archived Build6 reports dummy return -> rootfree324 missinghalf tmp, but
records no executed MIR selectedDrop arm or target/Resume binding. Normal source
suffix effects and the exact failed path are therefore unresolved. Repeating the
same proof with a larger timeout alone would not distinguish the hypotheses.

Applicability: exact first+late callback actual insert_tail body, generated selected
CopyOnDrop Drop validated by existing key/path/hash/guard qualification. R8 narrow
StorageLive premise remains byte-for-byte unchanged. Prefix/other profiles/default
environment stay diagnostic-off; normal/unwind/abort/Resume and all posts remain.

First implementation is read-only diagnostics, not recovery/model extension:
translator emits parser-inexpressible native ghost events on each qualified Drop
returning/unwinding arm after unchanged receiver finish, and on actual Return and
Resume. Event metadata binds current MIR block/is_cleanup, normaltarget/unwind
kind/target, selected generated key/path/hash/guard and source span. A kernel-only
handler prints existing selected readonly-end/ref-initialized/points_to/array/Drop
resource chunks with coefficients/terms and tmp storage-live identity, and returns
exactly the input heap/env. Before freeing tmp a bounded native heap snapshot is
printed. No assertion, chunk, assumption, pointer equality or resource is added.
Source/AST/parser binding must be supported by the native construction plus exact
pinned component/source identities; coordinates alone are never called binding.

Distinguishing observations: cleanup=true + returning -> original cleanup target
vs cleanup=false returning vs Drop-own-unwinding; matching target block and Resume/
Return event; original readonly token/ref pointer/owner quarter/current value and
origin tmp half. Multiple events/hidden chunks/truncation remain explicit; no
absence-to-proof inference. This gate also executes the already reviewed fixed
freshness classifier at compatible final identities. Full mandatory suite retained.

Controls: native event off by default; first+late source qualification required;
AST event handler dialect/pure/name/shape guard; identical h/env continuation;
retained branch finish/target/unwindAction; bounded selected heap coverage counts;
CLI and parent env isolation on success/error; source hash and compiler/refiner
stage receipts remain strict. Independent Luna HIGH review before Cloud.

After observed path/resource binding, choose exact checked postDrop continuation
marker and run its source-supplied commands through ordinary resource verification.
Do not place recovery on Drop's own unwind action, retire tmp early, weaken posts,
or reclassify R8 controls. New semantic premise outside existingR8scope not allowed.
