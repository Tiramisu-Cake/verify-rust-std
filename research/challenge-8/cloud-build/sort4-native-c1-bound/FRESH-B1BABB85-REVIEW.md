# Fresh minimal Rust ZST size repair — model gates partial

Build b1babb85-c138-4b1f-abc6-b424051bbeb7, proof=infra
95f181fb0646bd678a09a6bbf6304157a8304257, new repair account.
Create08:46:36.740787288→finish08:52:15.144773 UTC; conservative339sec.
Cloud FAILURE because diagnostic_complete=false; run_exit0 is collector only.
Archive ed1a87f32d8059b84be0968ef37c7f71cbefbb3c0df96e2fe16156e868e51b34.
Download verifies archive/config/input/file inventory/receipt/text index/chunks.

Both callback-free sameguard bodies with/without unused native MU scratch VF0,
paired normal/readonly exports/decode/refinement0. Both preguard positive-size
queries fail on their exact first-body assertion: noMU3,41–42 /MU4,41–42,
Cannot prove0<sizeof(T_typeid). Both real nonzero-branch positive assertions VF0.
Concrete entry unit/MUunit reachable false rejects4,16–21 Cannot prove false.
Raw-pointer extra permission rejects4,19–22 No matching heap chunks points_to(unit).
C nonempty and C++ empty positive-size controls VF0. No check/resource deleted.

Matrix sizes pass for unit/MUunit/Empty/reprC Empty/u8/MUu8/empty arrays/ZSTarray3,
then fails14,43–44 on alignof(unit)>0. This is missing invocation of existing
std::alloc::is_valid_layout_size_of_align_of /size_align lemmas in fixture,
not evidence to change alignment model. Fresh followup adds existing proof lemma
calls, preserves every assertion and runtime source (no runtime branches).
Model patch unchanged:19ee0d684e972f164f16f21926bde7d5d1edc1f9224a880c20120f9cb62f1074;
verifast1 baseb1b0ae618bbce1a0bce9714ce10a47dbeb855e919b980b7ce6a70108ff9b91d7,
resultbfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207.
Exact new console and every source/layout/tool hash in ZST-REPAIR-BASE-RESULT-MANIFEST.

Native C1 SKIPPED_MODEL_GATES_FAILED; C4 NOT_RUN. Old native PASS not inherited.
No caller/generic actualsort4ZST theorem/profile qualification. All model gates
recorded fresh support identities; synthetic MIR is newly captured, not frozen.
Independent static review confirms causal classifier cannot pass earlier setup
or unrelated failures. Next permitted step: fixture-only lemma call correction,
fresh full gates then native consumer on exact published profile.
