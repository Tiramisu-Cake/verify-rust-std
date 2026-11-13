# LAWFUL-ORACLES PREP — worker14, 2026-11-13

Source READY: `0beeb6b79efb72b88035e2b747aa889e9b1cb4d4`.
Clone `/root/kani-fix-3300-lawful-oracles`, branch `fix/kani-3300-lawful-oracles`.
Parent exactly `ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677`.
Research base be5bdb511676c0f441662528c0b88aab9c3fe007, pull --ff-only up-to-date.

Tests-only: lawful source/expected plus one json-handler exact-oracle scenario.
Original lawful SHA256 f629b795969f197ef289061c88ebc26e08c8fe969a6f82f643897451bfbdf90f matched.
Body/modifies/ensures unchanged; only explanatory per-test b12 flag comments added.
Candidate hashes and exact comment diff: INPUTS.json / LAWFUL-COMMENT-DELTA.patch.
No duplicate P1, production/schema/compiletest/solver/slicing/global default changes.

Strong gates: exact input/hash/root/selection; completed outcome; original exit;
full failure multiset/IDs/class/type/description/source; counter/status partitions;
complete regular inventory; selected useful SUCCESS assertions; reviewed GOTO binding.
Eight case definitions and source-operation maps: ORACLES.json / CONTROL-MAP.md.
P2 retains two obligations; postcondition-hole/clause inventories remain independent.
Frame must bind user *outside at line22, never an arbitrary historical var_N.
Unreachable service branches allowed; reached Unsupported/extra failures rejected.
Lawful reached closure-layout Unsupported causes STOP, without a model patch.

15 Python synthetic test methods PASS; AST/hash/body/Bash/whitespace/scope PASS.
Local fmt NOT_RUN (rustfmt unavailable); compiler/verifier/CI NOT_RUN.
All actual case outcomes NOT_RUN, all bindings BINDING_PENDING, independent credit0.
Exact generated failure IDs and useful-success/private/source/GOTO bindings pending.
CI request proposes eight singleton b12 roots,300s/6GiB; coordinator approves actual caps/budget.
Selected json-handler exec is mandatory; Quick alone leaves the strong gate NOT_RUN.
No worker15 integration, nested agents, push, CI dispatch or Cloud spend.
Static self-review recorded; independent acceptance belongs to coordinator.
Both author and committer Tiramisu-Cake <igkharin@gmail.com>, set via git -c.
