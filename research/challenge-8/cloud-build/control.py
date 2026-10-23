#!/usr/bin/env python3
"""Lightweight VPS orchestration only. Never executes proof tools locally."""
import argparse,ast,base64,copy,datetime,gzip,hashlib,importlib.util,json,math,os,re,subprocess,sys,uuid
from pathlib import Path
import coordination

ROOT=Path(__file__).resolve().parents[3]
DIR=Path(__file__).resolve().parent
GCLOUD=['gcloud','--configuration=smallsort-ci','--account=smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com','--project=smallsort-ci']
BUCKET='gs://smallsort-ci-evidence-504462351565/cloud-build'
UBUNTU='ubuntu@sha256:5ec03bb3441e8b0bf3b4f9cd4629a1ae763010dc3035bb8da3ae6cf026486401'
SDK='gcr.io/google.com/cloudsdktool/google-cloud-cli@sha256:c631b05e8121048b29c9917bdc0a9fadd76d012f04f180a4409ec2ee534e832e'
ACCOUNT='smallsort-builder@smallsort-ci.iam.gserviceaccount.com'
SDK_PYTHON='/usr/lib/google-cloud-sdk/platform/bundledpythonunix/bin/python3'
R14_PHASE='MERGE-PUBLICATION-GATE-PROOF-R14-2026-10-21'
R14_PROBE_SOURCE='c9b5151735c352d212752c5fe644adcd3543b68d'
R14_GATE_PATH='research/challenge-8/cloud-build/origin-layout/R14-PUBLICATION-GATE-20261021.json'
R14_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R14-PROOF-RETRY-BUDGET-20261021.json'
R14_R13_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R13-UPLOAD-BUDGET-20261021.json'
R14_CLOSED_R13_CHECKPOINT='6ee5298e69dfe552487cd73cc7be04bae47dbf0f'
R14_GATE_IDENTITIES={
 'build_id':'331fba31-4548-40e7-bb6d-1d225f590602',
 'proof_source_sha':'c9b5151735c352d212752c5fe644adcd3543b68d',
 'submitted_config_sha256':'da5162520a5fa2b96611a56f06a21ad8ae91843e214257c27ebac41051391ea0',
 'archive_sha256':'8ecf904c01ef647009619d7d445e13cb258c18a656dc65bc873756c610183efb',
 'index_sha256':'ad0e439b6d42371ade0c1db672f0f675e0eb6e209ca643e04b5b079d9a5a428e'}
R14_POLICY_FILE_ID='0f66bbe9230a4472a9e913dca0daeb28ad99b4a96f7625f689ccb0c2b3561f97'
R14_POLICY_FILE_SHA256='9883177b74ed1ede34b6498f363ce689b82c1beaee9211810179253aee8cc659'
R14_UPLOAD_SHELL_SHA256='677740c98b0389c77c40804a825037b598c46c095fc0fecd9a30b80c5922ef64'
R14_BRIEF_REQUEST_ID='da464eaaf9a99cba220d2226f40eea07121267e0ca1f12ae0775b1b3ee4e6d38'
R15_PHASE='MERGE-SINGLETON-ARRAY-PROOF-R15-2026-10-21'
R15_PROBE_SOURCE='c4e989d7113f525244dfcd2a6e1689e4eda4c69d'
R15_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R15-BUDGET-20261021.json'
R15_PREFLIGHT_PATH='research/challenge-8/cloud-build/origin-layout/r15-source-preflight.py'
R16_PHASE='MERGE-CALLER-CURRENT-PROOF-R16-2026-10-21'
R16_PROBE_SOURCE='a89d091c95e50d3aab961654f54668e0f631e3be'
R16_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R16-BUDGET-20261021.json'
R16_PREFLIGHT_PATH='research/challenge-8/cloud-build/origin-layout/r16-source-preflight.py'
R17_PHASE='MERGE-CALLER-REFINEMENT-R17-2026-10-21'
R17_PROBE_SOURCE='137cbf8ed13653c83a56975449c544ed7b348365'
R17_STARTING_SOURCE_SHA='6fd50c699500cbac5c65912174d4aa49b49db19f'
R17_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R17-BUDGET-20261021.json'
R17_PROFILE_PATH='research/challenge-8/cloud-build/origin-layout/R17-BASELINE-PROFILE-20261021.json'
R17_CONTROLS_PATH='research/challenge-8/cloud-build/origin-layout/r17-rawptr-controls.py'
R17_PATCH_PATH='research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch'
R17_PROFILE_REGISTRATION='r17_registration'
R17_PROVIDER_OVERLAYS_PATH='research/challenge-8/merge/cloud-build/provider-overlays.py'
R17_PROVIDER_OLD_PROVE_SHA256='2739a58c55fa8b4b764b16b9df8dc40239c2f2a0335c134534e76c9559d81f27'
R17_PROVIDER_NEW_PROVE_SHA256='092669d3d8e619130c4afc36f8c3f73698f3d5f776ffbeb8fe1f566e313ec8aa'
R17_PROVIDER_COMPAT_PATH='research/challenge-8/cloud-build/origin-layout/generated-glue-compatibility-controls.py'
R17_PROVIDER_NEW_COMPAT_SHA256='2cedb29c2c0194e8e7f4eb254c9a5e27c8eb8b5faa864bc4bd60f3a37065b2c3'
R17_AUTHORIZATION=('CURRENT-TASK R17: actual Merge caller refinement/borrow and unsize; '
 'checked RawPtr matching with exact-origin controls; fresh3600/no carry; '
 'independent Luna HIGH review; Cloud-only preparation/compiler/proof.')
R17_CANDIDATE_TOOL_SHA='a66c1d30214e463a16a325cdef30b0ec8555e0af'
R17_REFINER_CORE_SOURCE_SHA256='48d02bf44f4a082709a427e3e0d78af5498c1f240082fb27c7891dc8a3a283b0'
R17_PATCH_SHA256='8d38122260e868351c8a245c5775d14d705a688cf5814512013ad9d33bb6e953'
R18_PHASE='MERGE-RAW-CALLER-R18-2026-10-22'
R18_PROBE_SOURCE='c99dfde0bbf2b926b351d29230bd338f032c4a14'
R18_BASELINE_SHA='83cca35d25b6b26cd698e78bb6c605716c96df89'
R18_STARTING_SOURCE_SHA='6fd50c699500cbac5c65912174d4aa49b49db19f'
R18_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R18-BUDGET-20261022.json'
R18_PROFILE_PATH='research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json'
R18_PROFILE_SHA256='947be6e0ed9aa0d2270a820dd72e5ff4c78e8d30af3e55d7228b477af700026d'
R18_START='2026-10-22T14:08:51Z'
R18_MAIN_DEADLINE='2026-10-22T16:08:51Z'
R18_DEADLINE='2026-10-22T16:38:51Z'
R18_AUTHORIZATION=('CURRENT-TASK R18: actual Merge raw caller frontier, RawPtr refinement and '
 'original borrow/unsize; fresh3600/no carry; independent review per runtime profile '
 '(claude-subagent:smallsort-reviewer); Cloud-only preparation/compiler/proof.')
R19_PHASE='MERGE-UNWIND-CLEANUP-R19-2026-10-22'
R19_PROBE_SOURCE='4af316937f71092896da013503f1d882c9280def'
R19_BASELINE_SHA='17fe08b5b4ed5b09c1d08bf56537c3d474c4ed05'
R19_STARTING_SOURCE_SHA=R18_STARTING_SOURCE_SHA
R19_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R19-BUDGET-20261022.json'
R19_ADDED_PATHS={R19_LEDGER_PATH,'research/challenge-8/cloud-build/origin-layout/r19-unwind-controls.py'}
R19_REMOVED_PATHS={'research/challenge-8/cloud-build/origin-layout/R11-RETRY-INPUTS-20261021.json','research/challenge-8/cloud-build/origin-layout/R11-RETRY-BUDGET-20261021.json'}
R19_PROFILE_PATH=R18_PROFILE_PATH
R19_BASELINE_PROFILE_SHA256=R18_PROFILE_SHA256
R19_PROFILE_SHA256='1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb'
R19_PATCH_SHA256='8b2cfaa4cf28e12bd4997cf0de131bb5e5cb424d393a2b4c315c829818b4c3a4'
R19_PROVIDER_OLD_PROVE_SHA256=R17_PROVIDER_NEW_PROVE_SHA256
R19_PROVIDER_NEW_PROVE_SHA256='8b708283a27f7bacbeb827e579203116ec942c4c06de438fde0a584d447e0749'
R19_START='2026-10-22T16:08:18Z'
R19_MAIN_DEADLINE='2026-10-22T18:08:18Z'
R19_DEADLINE='2026-10-22T18:38:18Z'
R19_AUTHORIZATION=('CURRENT-TASK R19: checked insert_tail unwind cleanup on the raw caller, then original '
 'borrow/unsize; fresh3600/no carry; independent review per runtime profile '
 '(claude-subagent:smallsort-reviewer); Cloud-only preparation/compiler/proof.')
R20_PHASE='MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23'
R20_PROBE_SOURCE='e278869253e5a1e553d0ac0c1bc7adb5221b681e'
R20_BASELINE_SHA=R20_PROBE_SOURCE
R20_STARTING_SOURCE_SHA='6fd50c699500cbac5c65912174d4aa49b49db19f'
R20_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R20-BUDGET-20261023.json'
R20_METADATA_TEST_PATH='research/challenge-8/cloud-build/origin-layout/r20-metadata-admission-service-test.py'
R20_ARRAY_SLICE_HELPER_PATH='research/challenge-8/cloud-build/origin-layout/r20-array-slice-content.rs'
R20_ADDED_PATHS={R20_LEDGER_PATH,R20_METADATA_TEST_PATH,R20_ARRAY_SLICE_HELPER_PATH}
R20_REMOVED_PATHS={
 'research/challenge-8/cloud-build/origin-layout/r9-guard-return-controls-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r5-emitter-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r9-phase-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r9-marker-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r10-invariant-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r10-phase-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r9-wiring-service-test.py',
 'research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/r11-native-receipt-service-test.py'}
R20_PROFILE_PATH=R19_PROFILE_PATH
R20_PROFILE_SHA256='1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb'
R20_STARTING_TOOL_COMMIT='39f6b0cacd00575c8ca2d39e9f15632723bf1227'
R20_PATCH_SHA256=R19_PATCH_SHA256
R20_PROVIDER_SHA256='2bed7d32a35ac10121820ffdf8a6dbcb645f5eefb838c9bb0d89915086a34ef3'
R20_PROVIDER_PROVE_SHA256=R19_PROVIDER_NEW_PROVE_SHA256
R20_METADATA_TOOL_COMMIT='578120769161e217e53bd569bafdccbd4b2e020e'
R20_METADATA_PROFILE_SHA256='949633103e909f27a721573ae88f4d3180278de5bcc2c60031239f93fe0b0301'
R20_METADATA_EXPORTER_SHA256='8bcb126ea684d1c671b96425940b0d24904fdaa3beb69a09316bd222316fca42'
R20_METADATA_SCHEMA_SHA256='a894cfc85246c0c33b239c0ee5b729762475f79f46931546937f082e1a6ad7c5'
R20_METADATA_PATCH_SHA256='3112458ee12910ea17f69465a271d2cda848c7e50223a4b0c2b30c5e892ea33b'
R20_METADATA_PROVIDER_SHA256='a119f26e3439e5e4ba5548c38abcbeced3b7eb17547098fc7185de2525b67043'
R20_METADATA_PROVIDER_PROVE_SHA256='c72b9a6eb235f1ec41eb305b4dd78a129e485733f655a569dd8c1c6bcde77a69'
R20_R19_EXPORTER_SHA256='d8bca867798fd93ececcb5fd8db330d6d23d2f7b815009437bf4961b9fcd2f51'
R20_R19_SCHEMA_SHA256='b6c63644e8926a207b4393b80bf27696838aa22fe9db33acecc9fefa68550750'
R20_R19_REFINER_CORE_SHA256='48d02bf44f4a082709a427e3e0d78af5498c1f240082fb27c7891dc8a3a283b0'
R20_METADATA_REFINER_CORE_SHA256='7be8a6f16ce45173866bddcc6b6d606ac4ef2a6748885eca1fc982611c753614'
R20_METADATA_REGISTRATION={
 'schema':'merge-r20-source-preserving-metadata-registration-v1',
 'phase_id':R20_PHASE,
 'baseline_profile_sha256':R20_PROFILE_SHA256,
 'starting_tool_commit':R20_STARTING_TOOL_COMMIT,
 'starting_source_sha':R20_STARTING_SOURCE_SHA,
 'owner':'merge','lane':'merge',
 'candidate_tool_commit':R20_METADATA_TOOL_COMMIT,
 'tool_source_paths':['src/refinement_checker/refinement_checker.ml',
                      'src/rust_frontend/vf_mir/vf_mir.capnp',
                      'src/rust_frontend/vf_mir_exporter/src/lib.rs'],
 'source_applicability':('source-preserving MIR metadata: real CastData.sourceTy is encoded as Some(exact operand type); the schema permits None, and synthetic built-in Cast fixtures explicitly use None. Pointer-coercion metadata remains exact when present. Inference-region identity remains body-scoped; synthetic fixture regions use identity None and empty region_scope_id, never an inferred identity. Retains diagnostic-only context for the existing unequal LocalAddressTaken refusal (function, paired block/command positions and full listings, same standalone fatal diagnostic) and the prior closed-usize Value/Leaf interpreter case (UIntPtrWidth outer/value type match, scalar size 1..8 and bits fit). Strict RawPtr projected-place classifier unchanged; other index cases unsupported/inconclusive; no pointer, resource, lifetime or memory-model rule.')}
R20_START='2026-10-22T20:08:00Z'
R20_MAIN_DEADLINE='2026-10-22T22:08:00Z'
R20_DEADLINE='2026-10-22T22:38:00Z'
R20_TASK_ID='merge-unwind-acceptance-autonomous-2026-10-23-r20'
R20_AUTHORIZATION=('CURRENT-TASK R20: accept checked raw caller unwind cleanup with normal/unwind controls, then '
 'original as_mut_ptr/unsize borrow lifecycle and CURRENT matrix; fresh3600/no carry; '
 'independent Codex Luna HIGH review; Cloud-only preparation/compiler/proof.')
R21_PHASE='MERGE-CALLER-ACCEPTANCE-R21-2026-10-23'
R21_PROBE_SOURCE='e819a3155c76499be35879697e4fe607528de3e3'
R21_BASELINE_SHA=R21_PROBE_SOURCE
R21_STARTING_SOURCE_SHA=R20_STARTING_SOURCE_SHA
R21_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R21-BUDGET-20261023.json'
R21_ADDED_PATHS={R21_LEDGER_PATH}
R21_REMOVED_PATHS={R20_METADATA_TEST_PATH}
R21_PROFILE_PATH=R20_PROFILE_PATH
R21_PROFILE_SHA256=R20_METADATA_PROFILE_SHA256
R21_STARTING_TOOL_COMMIT=R20_METADATA_TOOL_COMMIT
R21_PATCH_SHA256=R20_METADATA_PATCH_SHA256
R21_PROVIDER_SHA256=R20_METADATA_PROVIDER_SHA256
R21_PROVIDER_PROVE_SHA256=R20_METADATA_PROVIDER_PROVE_SHA256
R21_START='2026-10-22T22:25:31Z'
R21_MAIN_DEADLINE='2026-10-23T00:25:31Z'
R21_DEADLINE='2026-10-23T00:55:31Z'
R21_TASK_ID='merge-caller-acceptance-autonomous-2026-10-23-r21'
R21_AUTHORIZATION=('CURRENT-TASK R21: Cloud admission of reviewed HANDOFF tool578/profile9496, raw caller '
 'F5/state/index controls, then original as_mut_ptr/unsize borrow lifecycle and CURRENT matrix; '
 'fresh3600/no carry; independent review per runtime profile (claude-subagent:smallsort-reviewer); '
 'Cloud-only preparation/compiler/proof.')
R22_PHASE='MERGE-CALLER-ACCEPTANCE-R22-2026-10-23'
R22_PROBE_SOURCE='3fbbd0f6e6c4e48a00fe5a2ae4dc6197e299be84'
R22_BASELINE_SHA=R22_PROBE_SOURCE
R22_STARTING_SOURCE_SHA=R20_STARTING_SOURCE_SHA
R22_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R22-BUDGET-20261023.json'
R22_ADDED_PATHS={R22_LEDGER_PATH}
R22_REMOVED_PATHS={'research/challenge-8/cloud-build/origin-layout/R11-BUILD5-RESULT-20261021.json', 'research/challenge-8/cloud-build/origin-layout/R11-BUILD3-RESULT-20261021.json', 'research/challenge-8/cloud-build/origin-layout/R11-BUILD2-RESULT-20261021.json', 'research/challenge-8/cloud-build/origin-layout/R11-BUILD4-RESULT-20261021.json', 'research/challenge-8/cloud-build/origin-layout/R11-INPUTS-20261021.json', 'research/challenge-8/cloud-build/origin-layout/R11-BUILD1-RESULT-20261021.json'}
R22_PROFILE_PATH=R20_PROFILE_PATH
R22_PROFILE_SHA256=R20_METADATA_PROFILE_SHA256
R22_STARTING_TOOL_COMMIT=R20_METADATA_TOOL_COMMIT
R22_PATCH_SHA256=R20_METADATA_PATCH_SHA256
R22_PROVIDER_SHA256=R20_METADATA_PROVIDER_SHA256
R22_PROVIDER_PROVE_SHA256=R20_METADATA_PROVIDER_PROVE_SHA256
# R22 compile-only exporter/translator extension. The original tuple above remains a
# valid admission; these pins are populated only for the reviewed extension.
R22_COMPILE_FIX_TOOL_COMMIT='65f0bb35e4f188cf8ce405a67253127173c5c3a1'
R22_COMPILE_FIX_EXPORTER_SHA256='0b456d055d498429c3da5bd4b7a1eb455b1b691bb0133a5f61bb449aad4e4345'
R22_COMPILE_FIX_TRANSLATOR_SHA256='e5fe47a16b1a94dcfd07d7d7c0355d4e5acb999650f00498d11606909960dde2'
R22_COMPILE_FIX_PATCH_SHA256='6d76e07dec9b8d3e093e442d74ed9b930f6e9b85da3d0ea74e912a8a94b7f20d'
R22_COMPILE_FIX_PROFILE_SHA256='d2640ee7088ecfe61c8115bc27df81c45e77742ce990295c22cdf6de90eb7579'
R22_COMPILE_FIX_PROVIDER_SHA256='06c871818bad4a3e3538ff460d477d45845b8f276bbb9978b32b336eba5e65e9'
R22_COMPILE_FIX_PROVIDER_PROVE_SHA256='e7dae89d920535b60acae855232e6f200b19a97f7fdd7473585ea2f488520e71'
R22_OWNED_NLL_TOOL_COMMIT='fc0208d4f53583d458670cd07bd0370636d4b2eb'
R22_OWNED_NLL_EXPORTER_SHA256='7bdf554c34feaa15a96f0d652be272bddae2c915a0122e5af09adfe9acd4430d'
R22_OWNED_NLL_SCHEMA_SHA256='ed44ed45da772052e0b767beb47ef33af958ac6ee7bd03f3c100d9f906f6eb92'
R22_OWNED_NLL_REFINER_CORE_SHA256='11a0ff9057e6da92a684c20b1cda1e4825d986ea6d80980a7a967f236f0c9db8'
R22_OWNED_NLL_TRANSLATOR_SHA256='bc60d926e5b34aeaa5f18ca6b08d2f9c0e707bd2d537e9081ea762d5a41fcfb2'
R22_OWNED_NLL_PATCH_SHA256='097f1ea2caba540a6c2fbff51bcded4726f4fb73536dbc6e803423f70b9df9c5'
R22_OWNED_NLL_PROFILE_SHA256='3fec93b5237d534b69eb3be59d11ea4abde3588f07c6e9437b1c09bf8533ac88'
R22_OWNED_NLL_PROVIDER_SHA256='06c871818bad4a3e3538ff460d477d45845b8f276bbb9978b32b336eba5e65e9'
R22_OWNED_NLL_PROVIDER_PROVE_SHA256='e7dae89d920535b60acae855232e6f200b19a97f7fdd7473585ea2f488520e71'
R22_OWNED_NLL_REGISTRATION={
 'schema':'merge-r22-owned-nll-diagnostic-registration-v1',
 'phase_id':R22_PHASE,
 'baseline_profile_sha256':R22_COMPILE_FIX_PROFILE_SHA256,
 'starting_tool_commit':R22_COMPILE_FIX_TOOL_COMMIT,
 'candidate_tool_commit':R22_OWNED_NLL_TOOL_COMMIT,
 'tool_source_paths':['src/rust_frontend/vf_mir_exporter/src/lib.rs', 'src/rust_frontend/vf_mir/vf_mir.capnp', 'src/refinement_checker/refinement_checker.ml', 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'],
 'source_applicability':'diagnostic-only optional owned-NLL capture for exact registered source cases; identity=Nothing initializes all three synthetic Lifetime fixtures. Serialization retains captured facts but cross-stage mapping is UNESTABLISHED, derived origin stays unavailable, and no proof credit or ownership authority is granted. No runtime, model, CFG, normal-unwind, or source-control change.'}
R22_START='2026-10-23T07:44:00Z'
R22_MAIN_DEADLINE='2026-10-23T09:44:00Z'
R22_DEADLINE='2026-10-23T10:14:00Z'
R22_TASK_ID='merge-caller-acceptance-autonomous-2026-10-23-r22'
R22_AUTHORIZATION=('CURRENT-TASK R22: Cloud admission of reviewed HANDOFF tool578/profile9496, raw caller '
 'F5/state/index controls, then original as_mut_ptr/unsize borrow lifecycle and CURRENT matrix; '
 'fresh3600/no carry; independent Codex Luna HIGH delta review; '
 'Cloud-only preparation/compiler/proof.')
R23_PHASE='MERGE-CALLER-ACCEPTANCE-R23-2026-10-24'
R23_PROBE_SOURCE='733b6a7d68259787f1caf58177060589b6af779e'
R23_BASELINE_SHA=R23_PROBE_SOURCE
R23_STARTING_SOURCE_SHA=R20_STARTING_SOURCE_SHA
R23_LEDGER_PATH='research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R23-BUDGET-20261024.json'
R23_CAPTURE_POLICY_PATH='research/challenge-8/cloud-build/origin-layout/R23-CAPTURE-POLICY-20261024.json'
R23_CAPTURE_POLICY_SHA256='9618853a3290d2dffbbbc11fe2a4ea59ed25f8ecd0a8a3a21c84e7a01e9ce941'
R23_ADDED_PATHS={R23_LEDGER_PATH,R23_CAPTURE_POLICY_PATH}
R23_REMOVED_PATHS={'research/challenge-8/cloud-build/origin-layout/r10-source-preflight.py', 'research/challenge-8/cloud-build/origin-layout/r9-source-preflight.py', 'research/challenge-8/merge/cloud-build/test-provider-base-pins.py', 'research/challenge-8/cloud-build/origin-layout/r5-emitter-source-preflight.py', 'research/challenge-8/cloud-build/origin-layout/R10-START-20261021.json', 'research/challenge-8/cloud-build/origin-layout/LAYOUT-PINS.json', 'research/challenge-8/cloud-build/origin-layout/R5-EMITTER-PINS-20261020.json', 'research/challenge-8/merge/cloud-build/test-r11-provider-overlay-service.py'}
R23_PROFILE_PATH=R22_PROFILE_PATH
R23_PROFILE_SHA256=R22_OWNED_NLL_PROFILE_SHA256
R23_STARTING_TOOL_COMMIT=R22_OWNED_NLL_TOOL_COMMIT
R23_PATCH_SHA256=R22_OWNED_NLL_PATCH_SHA256
R23_SOURCE_PROFILE_SHA256='2119ad73877cfeac2158c20dbf03bf148236e4344f5ba2e60e8974a03d1626ba'
R23_SOURCE_PATCH_SHA256='1c8fc175b834ef1cf8c114b99bd1029e7a73dbc7f1317fb2fbd24b9c8536e596'
R23_SOURCE_REGISTRY_PATH='research/challenge-8/cloud-build/origin-layout/r23-source-profile.py'
R23_SOURCE_REGISTRY_SHA256='bfaaf9ab9b6100e2300f61887a5edbb3cb5ebcfa2ff52d4ba8131413efe57644'
R23_SOURCE_ADDED_PATHS={R23_SOURCE_REGISTRY_PATH,
 'research/challenge-8/cloud-build/origin-layout/R23-SOURCE-BORROW-TEMPLATE-20261024.rs',
 'research/challenge-8/cloud-build/origin-layout/r23-array3-borrow-content.rs',
 'research/challenge-8/cloud-build/origin-layout/r23-checked-slice-as-mut-ptr.rs'}
R23_ADDED_PATHS |= R23_SOURCE_ADDED_PATHS
R23_PROVIDER_SHA256='acad333bb74a416af8f5515d414740f7241358316d3cc6c1e417d85b7fccc20e'
R23_PLACEMENT_PATH='research/challenge-8/cloud-build/origin-layout/r11-storage-placement-controls.py'
R23_PLACEMENT_SHA256='801a711f6d4ebb1aba95e9f00d8e97a672e59742fc370493f9690077fb9f4faa'
R23_PROVE_SHA256='7c784fb1e00cf48e9b62c3978976e3fd33a91004be8d8e23e8599184181f92ef'
R23_COMPAT_PATH='research/challenge-8/cloud-build/origin-layout/generated-glue-compatibility-controls.py'
R23_COMPAT_SHA256='f710146680415de30b7e88d85a5112310ddc43b8aae9773a7c3f649bb27ad605'
R23_START='2026-10-23T10:45:00Z'
R23_MAIN_DEADLINE='2026-10-26T10:45:00Z'
R23_DEADLINE='2026-10-26T11:45:00Z'
R23_TASK_ID='merge-caller-acceptance-autonomous-2026-10-24-r23'
R23_AUTHORIZATION=('CURRENT-TASK R23 and R23-OWNER-DIRECTIONS: fix three NEEDS_FIX findings; '
 'early owned-NLL Build, maximum two capture cycles then source-level checked borrow route; '
 'raw caller F5/state/index and CURRENT normal/unwind matrix; fresh14400/no carry; '
 'one-time extended window; independent Codex Luna HIGH review; Cloud-only actual toolchain.')
R14_PREFLIGHT_PATH='research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py'
R11_SESSION_PATH='research/challenge-8/cloud-build/origin-layout/R11-SESSION-20261021.md'
R13_MODE_PATH='research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json'
R15_RECIPE_REMOVALS={R14_PREFLIGHT_PATH,'research/challenge-8/cloud-build/origin-layout/r13-source-preflight.py',
 R11_SESSION_PATH,'research/challenge-8/cloud-build/origin-layout/R11-CANDIDATE2-REVIEW-20261021.md',
 'research/challenge-8/cloud-build/origin-layout/R11-LABEL-STORAGE-DESIGN-20261021.md',
 'research/challenge-8/cloud-build/origin-layout/R11-PLACEMENT-DESIGN-20261021.md',
 'research/challenge-8/cloud-build/origin-layout/r11-phase-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r11-registration-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r11-retry-phase-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r11-source-preflight.py',
 'research/challenge-8/cloud-build/origin-layout/r11-storage-placement-controls-service-test.py',
 'research/challenge-8/cloud-build/origin-layout/r11-trace-service-test.py'}
TERMINAL={'SUCCESS','FAILURE','INTERNAL_ERROR','TIMEOUT','CANCELLED','EXPIRED'}
NIGHT_PHASE='NIGHT-SELECT-SORT4-CLOUD-2026-10-09'
NIGHT_DEADLINE='2026-10-09T08:00:00Z'
LANE_PATTERN=re.compile(r'[a-z][a-z0-9-]{0,63}\Z')
PHASE_PATTERN=re.compile(r'[A-Z][A-Z0-9-]{0,100}\Z')
OWNER_PATTERN=re.compile(r'[A-Za-z0-9._-]{1,80}\Z')

def read(p):return coordination.read(p)
def write(p,x):coordination.write(p,x)
def shquote(x):return "'"+x.replace("'","'\\''")+"'"
def digest(b):return hashlib.sha256(b).hexdigest()
def invoke(args):
 p=subprocess.run(GCLOUD+args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode:raise RuntimeError(p.stderr.strip())
 return json.loads(p.stdout) if p.stdout.strip() else None

def envs(infra,proof,lane,r13_required=False):return [f'INFRA_SHA={infra}',f'PROOF_SHA={proof}',f'LANE={lane}',f'PROOF_IMAGE={UBUNTU}',f'R13_UPLOAD_REQUIRED={"true" if r13_required else "false"}','CLOUD_BUILD_ID=${BUILD_ID}','CLOUD_BUILD_PROJECT_ID=${PROJECT_ID}','CLOUD_BUILD_REGION=global','SMALLSORT_EXECUTION_PROVIDER=cloud-build','SUBMITTED_CONFIG_SHA=${_CONFIG_SHA}',] + [f'CONFIG_PART_{i}=${{_CONFIG_{i}}}' for i in range(8)]

def required_upload_guard(phase):return phase in ('MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21','MERGE-PUBLICATION-GATE-PROOF-R14-2026-10-21','MERGE-SINGLETON-ARRAY-PROOF-R15-2026-10-21','MERGE-CALLER-CURRENT-PROOF-R16-2026-10-21','MERGE-CALLER-REFINEMENT-R17-2026-10-21','MERGE-RAW-CALLER-R18-2026-10-22','MERGE-UNWIND-CLEANUP-R19-2026-10-22','MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23','MERGE-CALLER-ACCEPTANCE-R21-2026-10-23','MERGE-CALLER-ACCEPTANCE-R22-2026-10-23',R23_PHASE)

def config(infra,proof,lane,seconds,token,source_payload=None,r13_required=False):
 if type(r13_required) is not bool:raise ValueError('R13 upload-required selection must be boolean')
 work_seconds=seconds-70
 work='''set -euo pipefail
 export DEBIAN_FRONTEND=noninteractive
 apt-get update
 apt-get install --yes --no-install-recommends ca-certificates curl git python3 time
 checkout() {
  local target=$1 revision=$2
  git init "$target"
  git -C "$target" remote add origin https://github.com/Tiramisu-Cake/verify-rust-std.git
  git -C "$target" config remote.origin.promisor true
  git -C "$target" config remote.origin.partialclonefilter blob:none
  git -C "$target" sparse-checkout set research/challenge-8 library/core
  git -C "$target" fetch --depth=1 --filter=blob:none origin "$revision"
  git -C "$target" checkout --detach FETCH_HEAD
  test "$(git -C "$target" rev-parse HEAD)" = "$revision"
 }
 checkout /workspace/infra "$INFRA_SHA"
 checkout /workspace/proof "$PROOF_SHA"
 export EVIDENCE_ROOT=/workspace/evidence
 bash /workspace/infra/research/challenge-8/cloud-build/run-proof.sh "$LANE"
'''
 source_parts=[]
 source_env=[]
 if source_payload is not None:
  encoded=base64.b64encode(source_payload).decode()
  # Nine config substitutions leave 191 of the documented 200 slots for source.
  # Keep each value ten bytes below the documented 4000-byte ceiling.
  source_parts=[encoded[i:i+3990] for i in range(0,len(encoded),3990)]
  if len(source_parts)>191:raise SystemExit('Pinned source payload exceeds bounded transport; no dispatch')
  groups=[source_parts[i:i+10] for i in range(0,len(source_parts),10)]
  restore=base64.b64encode(gzip.compress((DIR/'source-input.py').read_bytes(),mtime=0)).decode()
  replacement=("python3 -c "+shquote("import base64,os,pathlib; pathlib.Path('/workspace/source-inputs.json.gz').write_bytes(base64.b64decode(''.join(os.environ['SOURCE_GROUP_'+str(i)] for i in range("+str(len(groups))+"))))")+"\n"
   +" printf '%s  %s\\n' "+shquote(digest(source_payload))+" /workspace/source-inputs.json.gz | sha256sum -c -\n"
   +" printf '%s' \"$SOURCE_RESTORE_BYTES\" | base64 --decode | gzip --decompress > /workspace/source-input.py\n"
   +" python3 /workspace/source-input.py restore --archive /workspace/source-inputs.json.gz --evidence /workspace/evidence\n")
  start=work.index(' checkout() {')
  end=work.index(' export EVIDENCE_ROOT',start)
  work=work[:start]+replacement+work[end:]
  source_env=['SOURCE_GROUP_'+str(i)+'='+''.join('${_SOURCE_'+str(i*10+j)+'}' for j in range(len(group))) for i,group in enumerate(groups)]+[f'SOURCE_INPUT_SHA256={digest(source_payload)}','SOURCE_MODE=pinned-objects','SOURCE_RESTORE_BYTES='+restore]
 if lane=='smoke-success':work="printf 'SMALLSORT_BUCKET_WRITE_PROBE\\n'; printf 'cloud-build bucket probe\\n' > /workspace/evidence/probe.txt"
 elif lane=='smoke-error':work="printf 'CONTROLLED_ERROR_START\\n'; printf 'deliberate exit 42\\n' >&2; exit 42"
 elif lane=='smoke-timeout':work="printf 'INTERNAL_TIMEOUT_START\\n'; timeout --signal=TERM --kill-after=1s 2s bash -c 'sleep 30'"
 body='''set -euo pipefail
mkdir -p /workspace/evidence
printf '%s%s%s%s%s%s%s%s' "$CONFIG_PART_0" "$CONFIG_PART_1" "$CONFIG_PART_2" "$CONFIG_PART_3" "$CONFIG_PART_4" "$CONFIG_PART_5" "$CONFIG_PART_6" "$CONFIG_PART_7" | base64 --decode | gzip --decompress > /workspace/evidence/submitted-config.json
printf '%s  %s\\n' "$SUBMITTED_CONFIG_SHA" /workspace/evidence/submitted-config.json | sha256sum -c -
{ uname -a; nproc; cat /etc/os-release; cat /proc/meminfo; if test -f /sys/fs/cgroup/cpu.max; then cat /sys/fs/cgroup/cpu.max; fi; df -h /workspace; if test -f /sys/fs/cgroup/memory.max; then cat /sys/fs/cgroup/memory.max; fi; } > /workspace/evidence/environment.txt
export SMALLSORT_DEADLINE_EPOCH=$(( $(date +%s) + WORK_SECONDS - 15 ))
set +e
timeout --signal=TERM --kill-after=10s "${WORK_SECONDS}s" bash -ceu WORK_BODY > /workspace/evidence/full-stdout.log 2> /workspace/evidence/full-stderr.log
code=$?
set -e
printf '%s\\n' "$code" > /workspace/evidence/run-exit.txt
cat /workspace/evidence/full-stdout.log
cat /workspace/evidence/full-stderr.log >&2
exit 0
'''.replace(' + WORK_SECONDS - 15 ',f' + {work_seconds} - 15 ').replace('"${WORK_SECONDS}s"',f'"{work_seconds}s"').replace('WORK_BODY',shquote(work))
 # Shell dollar signs are escaped for Cloud Build substitutions; env builtins remain explicit.
 body=body.replace('$','$$')
 package=base64.b64encode(gzip.compress((DIR/'package-evidence.py').read_bytes(),mtime=0)).decode()
 upload='''set -euo pipefail
export CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False
r13_required="${R13_UPLOAD_REQUIRED:-false}"
r13_card=/workspace/proof/research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json
if [[ "$r13_required" != true && "$r13_required" != false ]]; then
 printf 'invalid R13 upload-required marker\\n' >&2
 exit 2
fi
if [[ "$r13_required" == true ]]; then
 [[ -f "$r13_card" && ! -L "$r13_card" ]] || {
  printf 'R13 upload is required but its selected mode card is missing or unsafe\\n' >&2
  exit 2
 }
fi
mkdir -p /workspace/cloudsdk/configurations
printf '[core]\\nproject = smallsort-ci\\naccount = ACCOUNT\\n' > /workspace/cloudsdk/configurations/config_smallsort-ci
export CLOUDSDK_CONFIG=/workspace/cloudsdk
SMALLSORT_UPLOAD_THRESHOLD="$(gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci config get-value storage/parallel_composite_upload_threshold)"
SMALLSORT_UPLOAD_COMPOSITE="$(gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci config get-value storage/parallel_composite_upload_enabled)"
export SMALLSORT_UPLOAD_THRESHOLD SMALLSORT_UPLOAD_COMPOSITE
SDK_PYTHON - <<'POLICY'
import json,os,pathlib
if os.environ['SMALLSORT_UPLOAD_COMPOSITE'].strip().lower()!='false':
 raise RuntimeError('SDK did not disable parallel composite upload')
p=pathlib.Path('/workspace/evidence/allprooflogs');p.mkdir(parents=True,exist_ok=True)
(p/'upload-policy.json').write_text(json.dumps({'schema':'smallsort-upload-policy-v1','sdk_image':'SDK_IMAGE','service_account':'ACCOUNT','bucket':'BUCKET','parallel_composite_upload_enabled_env':os.environ['CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED'],'parallel_composite_upload_enabled_effective':os.environ['SMALLSORT_UPLOAD_COMPOSITE'],'parallel_composite_upload_threshold':os.environ['SMALLSORT_UPLOAD_THRESHOLD'],'proof_sha':os.environ['PROOF_SHA'],'infra_sha':os.environ['INFRA_SHA'],'build_id':os.environ['CLOUD_BUILD_ID']},indent=2)+'\\n')
POLICY
printf '%s' PACKAGE_B64 | base64 --decode | gzip --decompress > /workspace/package-evidence.py
SDK_PYTHON /workspace/package-evidence.py --evidence /workspace/evidence --out /workspace/out
if [[ -e "$r13_card" || -L "$r13_card" ]]; then
 SDK_PYTHON /workspace/proof/research/challenge-8/cloud-build/origin-layout/r13-archive-size-guard.py --archive /workspace/out/evidence.tar.gz --mode-card "$r13_card" --policy /workspace/evidence/allprooflogs/upload-policy.json --diagnostic /workspace/out/archive-size-check.json
fi
prefix="BUCKET/$CLOUD_BUILD_ID"
export SMALLSORT_UPLOAD_STARTED_NS="$(date +%s%N)"
publication_files=(evidence.tar.gz archive.sha256 summary.json manifest.json files-sha256.json submitted-config.json text-logs-index.json)
if [[ -f /workspace/out/archive-size-check.json ]]; then publication_files+=(archive-size-check.json); fi
for file in "${publication_files[@]}"; do
 if [[ "$file" == evidence.tar.gz ]]; then export SMALLSORT_ARCHIVE_UPLOAD_STARTED_NS="$(date +%s%N)"; fi
 gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci storage cp --if-generation-match=0 "/workspace/out/$file" "$prefix/$file"
 if [[ "$file" == evidence.tar.gz ]]; then export SMALLSORT_ARCHIVE_UPLOAD_FINISHED_NS="$(date +%s%N)"; fi
done
gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci storage cp --recursive --if-generation-match=0 /workspace/out/text-logs "$prefix/"
SDK_PYTHON - <<'RECEIPT'
import json,os,pathlib,time
p=pathlib.Path('/workspace/out')
h=(p/'archive.sha256').read_text().split()[0]
size=(p/'evidence.tar.gz').stat().st_size
duration=(int(os.environ['SMALLSORT_ARCHIVE_UPLOAD_FINISHED_NS'])-int(os.environ['SMALLSORT_ARCHIVE_UPLOAD_STARTED_NS']))/1e9
guard_path=p/'archive-size-check.json'
guard=json.loads(guard_path.read_text()) if guard_path.is_file() else None
(p/'upload-complete.json').write_text(json.dumps({'build_id':os.environ['CLOUD_BUILD_ID'],'archive_sha256':h,'uploaded':True,'text_logs_index_sha256':__import__('hashlib').sha256((p/'text-logs-index.json').read_bytes()).hexdigest(),'archive_size_bytes':size,'archive_upload_seconds':duration,'archive_upload_bytes_per_second':size/duration if duration>0 else None,'pre_marker_upload_seconds':(time.time_ns()-int(os.environ['SMALLSORT_UPLOAD_STARTED_NS']))/1e9,'prerequisite_uploader_exit_code':0,'parallel_composite_upload_enabled':os.environ['CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED'],'archive_size_guard':guard,'archive_size_guard_sha256':__import__('hashlib').sha256(guard_path.read_bytes()).hexdigest() if guard_path.is_file() else None},indent=2)+'\\n')
RECEIPT
gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci storage cp --if-generation-match=0 /workspace/out/upload-complete.json "$prefix/upload-complete.json"
touch /workspace/upload.ok
'''.replace('ACCOUNT',ACCOUNT).replace('SDK_PYTHON',SDK_PYTHON).replace('SDK_IMAGE',SDK).replace('PACKAGE_B64','"$PACKAGER_BYTES"').replace('BUCKET',BUCKET).replace('$','$$')
 verdict='''import json,pathlib,sys
p=pathlib.Path('/workspace/out')
try:
 s=json.loads((p/'summary.json').read_text())
 ok=pathlib.Path('/workspace/upload.ok').is_file() and ((s.get('verification_accepted') is True) or (s.get('smoke_success') is True) or (s.get('diagnostic_complete') is True))
 print('SMALLSORT_FINAL_VERDICT',json.dumps(s,sort_keys=True),'upload_complete=',pathlib.Path('/workspace/upload.ok').is_file(),'verification_accepted=',s.get('verification_accepted'),'diagnostic_complete=',s.get('diagnostic_complete'))
 sys.exit(0 if ok else 1)
except Exception as e:
 print('INCOMPLETE_EVIDENCE',type(e).__name__,str(e));sys.exit(2)
'''
 return {'steps':[{'id':'execute','name':UBUNTU,'entrypoint':'bash','args':['-ceu',body],'env':envs(infra,proof,lane,r13_required)+source_env,'allowFailure':True},{'id':'package-upload','name':SDK,'entrypoint':'bash','args':['-ceu',upload],'env':envs(infra,proof,lane,r13_required)+['PACKAGER_BYTES='+package],'allowFailure':True},{'id':'verdict','name':SDK,'entrypoint':SDK_PYTHON,'args':['-c',verdict]}],'timeout':f'{seconds}s','queueTtl':'60s','options':{'machineType':'E2_STANDARD_2','logging':'CLOUD_LOGGING_ONLY'},'serviceAccount':f'projects/smallsort-ci/serviceAccounts/{ACCOUNT}','tags':['smallsort-cloud-migration',token],'substitutions':{'_CONFIG_SHA':'placeholder',**{f'_CONFIG_{i}':'placeholder' for i in range(8)},**{f'_SOURCE_{i}':part for i,part in enumerate(source_parts)}}}

def reconcile(state,ledger,ledger_path):
 for item in ledger['builds']:
  receipt_path=coordination.COORDINATION/'receipts'/(item['dispatch_token']+'.json')
  if not item.get('accounted') and receipt_path.is_file():
   receipt=read(receipt_path)
   if (receipt.get('status')=='NOT_CREATED_INVALID_ARGUMENT' and
       receipt.get('validation_rejection') is True and receipt.get('build_id') is None and
       receipt.get('owner')==item.get('owner') and
       receipt.get('phase_id')==ledger.get('phase')==item.get('phase_id') and
       receipt.get('ledger')==str(ledger_path) and
       receipt.get('dispatch_token')==item['dispatch_token']):
    item.update(status='NOT_CREATED_INVALID_ARGUMENT',accounted=True,build_seconds=0,
                reason=receipt.get('reason','API validation rejection'))
  if not item.get('build_id') and not item.get('accounted'):
   matches=invoke(['builds','list','--region=global','--filter=tags:'+item['dispatch_token'],'--format=json']) or []
   if len(matches)==1:item['build_id']=matches[0]['id']
   elif len(matches)>1:raise RuntimeError('Multiple builds for one dispatch token; no further dispatch')
  if item.get('build_id') and not item.get('accounted'):
   b=invoke(['builds','describe',item['build_id'],'--region=global','--format=json'])
   write(state/(item['build_id']+'.json'),b)
   item['status']=b.get('status');item['start_time']=b.get('startTime');item['finish_time']=b.get('finishTime');item['create_time']=b.get('createTime')
   if b.get('status') in TERMINAL:
    def t(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
    duration=math.ceil((t(b['finishTime'])-t(b['createTime'])).total_seconds()) if b.get('finishTime') and b.get('createTime') else item['reserved_seconds']
    item['build_seconds']=duration;item['accounted']=True
    if b.get('startTime') and b.get('finishTime'):item['execution_seconds']=math.ceil((t(b['finishTime'])-t(b['startTime'])).total_seconds())
 ledger['used_build_seconds']=sum(x.get('build_seconds',0) for x in ledger['builds'])
 ledger['remaining_build_seconds']=ledger['ceiling_build_seconds']-ledger['used_build_seconds']
 if ledger.get('phase') in (R17_PHASE,R18_PHASE,R19_PHASE,R20_PHASE,R21_PHASE,R22_PHASE,R23_PHASE):
  ledger['spent_build_seconds']=ledger['used_build_seconds']
 ledger['active_build']=next((x.get('build_id') or x['dispatch_token'] for x in ledger['builds'] if not x.get('accounted')),None)
 write(ledger_path,ledger)


def reconcile_global(caller_owner,caller_ledger):
 for record in coordination.reservations():
  reconcile_reservation(record,caller_owner,caller_ledger)


def reconcile_reservation(record,caller_owner,caller_ledger):
 token=record['dispatch_token']
 ledger_path=Path(record['ledger'])
 if not ledger_path.is_absolute():raise RuntimeError('Global reservation has a nonabsolute ledger path')
 own=(record.get('owner')==caller_owner and ledger_path==caller_ledger)
 ledger=read(ledger_path)
 if ledger.get('phase')!=record.get('phase_id'):raise RuntimeError('Global reservation phase/ledger mismatch')
 original=record.get('item')
 if not isinstance(original,dict) or any(original.get(key)!=record.get(key) for key in ('dispatch_token','owner','phase_id')):
  raise RuntimeError('Global reservation item identity mismatch')
 matches=[x for x in ledger['builds'] if x.get('dispatch_token')==token]
 if len(matches)>1:raise RuntimeError('Duplicate token in phase ledger')
 if not matches:
  if not own:raise RuntimeError('Foreign ledger lacks reserved token; global reservation retained')
  ledger['builds'].append(original.copy())
  write(ledger_path,ledger)
  matches=[ledger['builds'][-1]]
 item=matches[0]
 if item.get('owner')!=record['owner'] or item.get('phase_id')!=record['phase_id']:
  raise RuntimeError('Ledger token owner or phase mismatch')
 if item.get('build_id') and record.get('build_id') and item['build_id']!=record['build_id']:
  raise RuntimeError('Ledger and global Build IDs conflict')
 if record.get('validation_rejection'):
  if record.get('build_id') or item.get('build_id'):raise RuntimeError('Validation rejection conflicts with Build ID')
  possible=invoke(['builds','list','--region=global','--filter=tags:'+token,'--format=json']) or []
  if possible:raise RuntimeError('Build exists despite recorded validation rejection')
  receipt={'dispatch_token':token,'owner':record['owner'],'phase_id':record['phase_id'],
           'ledger':str(ledger_path),'build_id':None,'status':'NOT_CREATED_INVALID_ARGUMENT',
           'validation_rejection':True,'reason':record.get('rejection_reason','API validation rejection'),
           'build_seconds':0}
  write(coordination.COORDINATION/'receipts'/(token+'.json'),receipt)
  coordination.clear(token)
  return
 build_id=record.get('build_id') or item.get('build_id')
 if build_id is None:
  possible=invoke(['builds','list','--region=global','--filter=tags:'+token,'--format=json']) or []
  if len(possible)>1:raise RuntimeError('Multiple builds for one dispatch token; no further dispatch')
  if not possible:return  # Uncertain submission stays reserved, including a pre-submit crash.
  build_id=possible[0]['id']
 build=invoke(['builds','describe',build_id,'--region=global','--format=json'])
 if build.get('id')!=build_id:raise RuntimeError('Cloud API returned a different Build ID')
 if token not in build.get('tags',[]):raise RuntimeError('Build does not carry the reserved dispatch token')
 if record.get('build_id')!=build_id:
  record['build_id']=build_id
  coordination.update(record)
 coordination.submitted(record['owner'],token)
 if build.get('status') not in TERMINAL:return
 def t(value):return datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
 seconds=(math.ceil((t(build['finishTime'])-t(build['createTime'])).total_seconds())
          if build.get('finishTime') and build.get('createTime') else original['reserved_seconds'])
 receipt={'dispatch_token':token,'owner':record['owner'],'phase_id':record['phase_id'],
          'ledger':str(ledger_path),'build_id':build_id,'status':build['status'],
          'create_time':build.get('createTime'),'start_time':build.get('startTime'),
          'finish_time':build.get('finishTime'),'build_seconds':seconds,
          'validation_rejection':False}
 write(coordination.COORDINATION/'receipts'/(token+'.json'),receipt)
 coordination.clear(token)


def r12_upload_mode(proof_sha):
 if not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R12 requires a full selected proof source SHA')
 try:
  raw=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/origin-layout/R12-UPLOAD-MODE-20261021.json'],cwd=ROOT,stderr=subprocess.PIPE)
  card=json.loads(raw)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R12 selected committed source lacks a valid upload mode card')
 if not isinstance(card,dict) or card.get('schema')!='merge-r12-upload-mode-v1' or card.get('mode') not in ('synthetic-upload','proof-r11'):
  raise SystemExit('R12 selected source mode is not an authorized upload/proof mode')
 if card['mode']=='proof-r11' and set(card)!={'schema','mode'}:
  raise SystemExit('R12 proof mode card has unexpected fields')
 if card['mode']=='synthetic-upload' and (type(card.get('payload_bytes')) is not int or type(card.get('threshold_bytes')) is not int or card.get('proof_attempted') is not False or card!={'schema':'merge-r12-upload-mode-v1','mode':'synthetic-upload','payload_bytes':536870912,'threshold_bytes':157286400,'threshold_source':'https://docs.cloud.google.com/storage/docs/parallel-composite-uploads','proof_attempted':False}):
  raise SystemExit('R12 synthetic mode card differs from the reviewed large random payload')
 return card['mode']


def r12_runtime_inventory(commit,mutable_paths=None):
 spec=importlib.util.spec_from_file_location('r12_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
 recipe=source.committed_recipe(ROOT,commit,'merge')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 recipe_raw=subprocess.check_output(['git','show',commit+':'+recipe_path],cwd=ROOT)
 allowed_mutable={
  'research/challenge-8/cloud-build/origin-layout/R12-UPLOAD-MODE-20261021.json',
  'research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R12-UPLOAD-BUDGET-20261021.json'}
 if mutable_paths is not None:allowed_mutable=set(mutable_paths)
 proof_paths=[p for p in recipe['proof_paths'] if p not in allowed_mutable and not p.endswith('.md')]
 paths=sorted(set(proof_paths+recipe['infra_paths']+source.infra_paths(ROOT,commit)+[recipe_path]))
 raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*paths],cwd=ROOT)
 inventory={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':
   raise SystemExit('R12 runtime closure contains a non-regular source input')
  inventory[path.decode()]=(mode,kind,oid)
 if set(inventory)!=set(paths):raise SystemExit('R12 runtime closure is incomplete')
 return recipe_raw,inventory


def r12_validate_retry_sources(probe_sha,proof_sha):
 before_recipe,before=r12_runtime_inventory(probe_sha)
 after_recipe,after=r12_runtime_inventory(proof_sha)
 if before_recipe!=after_recipe or before!=after:
  raise SystemExit('R12 proof retry differs from the synthetic-gated runtime/publication source closure')


def r13_upload_mode(proof_sha):
 if not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R13 requires a full selected source SHA')
 try:
  raw=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json'],cwd=ROOT,stderr=subprocess.PIPE)
  card=json.loads(raw)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R13 selected source lacks a valid mode card')
 if not isinstance(card,dict) or card.get('schema')!='merge-r13-upload-mode-v1':
  raise SystemExit('R13 selected mode schema differs')
 if card.get('mode')=='proof-r11':
  if set(card)!={'schema','mode','archive_limit_bytes'} or type(card.get('archive_limit_bytes')) is not int or card['archive_limit_bytes']!=536870912:
   raise SystemExit('R13 proof mode must preserve the exact archive cap')
 elif card.get('mode')=='synthetic-upload':
  expected={'schema':'merge-r13-upload-mode-v1','mode':'synthetic-upload','payload_bytes':268435456,'threshold_bytes':157286400,'archive_limit_bytes':536870912,'threshold_source':'https://docs.cloud.google.com/storage/docs/parallel-composite-uploads','proof_attempted':False}
  if card!=expected or any(type(card.get(k)) is not int for k in ('payload_bytes','threshold_bytes','archive_limit_bytes')) or card.get('proof_attempted') is not False:
   raise SystemExit('R13 synthetic mode differs from reviewed 256MiB payload/512MiB archive contract')
 else:raise SystemExit('R13 selected mode is unknown')
 return card['mode']


def r13_runtime_inventory(commit):
 mutable={'research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json','research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R13-UPLOAD-BUDGET-20261021.json'}
 return r12_runtime_inventory(commit,mutable)


def r13_validate_retry_sources(probe_sha,proof_sha):
 before_recipe,before=r13_runtime_inventory(probe_sha)
 after_recipe,after=r13_runtime_inventory(proof_sha)
 if before_recipe!=after_recipe or before!=after:
  raise SystemExit('R13 proof retry differs from the gated runtime/publication closure')


def r14_validate_gate_record(gate):
 required={
  'schema':'merge-r14-publication-gate-v1',
  'status':'ACCEPTED',
  **R14_GATE_IDENTITIES,
  'brief_request_id':R14_BRIEF_REQUEST_ID,
  'archive_size_bytes':None,'exact_archive_size_observed':False,'sidecar_verified':False,
  'archive_limit_bytes':536870912,'threshold_bytes':157286400,
  'parallel_composite_upload_enabled':False,'proof_attempted':False,
  'verification_accepted':False,'archive_inventory_verified':True,
  'publication_verified':True,'independent_proof_credit':0,
  'mandatory_guard_path_verified':True,
  'size_bounds_basis':'EXACT_PINNED_FAIL_CLOSED_PATH_AND_SUCCESSFUL_CLOUD_STEPS'}
 if not isinstance(gate,dict) or not required.keys()<=gate.keys() or any(gate.get(key)!=value for key,value in required.items()):
  raise SystemExit('R14 G1 gate fields missing/mismatch')
 for key in ('exact_archive_size_observed','sidecar_verified','parallel_composite_upload_enabled',
             'proof_attempted','verification_accepted','archive_inventory_verified',
             'publication_verified','mandatory_guard_path_verified'):
  if type(gate.get(key)) is not bool:
   raise SystemExit('R14 G2 control flag type')
 if type(gate.get('archive_size_bytes')) is not type(None) or type(gate.get('independent_proof_credit')) is not int:
  raise SystemExit('R14 G3 size/credit type')
 if type(gate.get('archive_limit_bytes')) is not int or type(gate.get('threshold_bytes')) is not int:
  raise SystemExit('R14 G4 bound type')
 steps=gate.get('cloud_steps_success')
 if (not isinstance(steps,dict) or set(steps)!={'execute','package-upload','verdict'} or
     any(value is not True for value in steps.values())):
  raise SystemExit('R14 G5 Cloud step matrix')
 coverage=gate.get('coverage')
 expected_coverage={
  'fresh_brief':'VERIFIED_ARCHIVE_AND_INVENTORY','catalogue_complete':True,'catalogue_members':15,
  'policy_file_id':R14_POLICY_FILE_ID,'policy_file_sha256':R14_POLICY_FILE_SHA256,
  'policy_selector':'pointer root','policy_exact':True,'policy_complete':True,'policy_next_offset':None,
  'effective_enabled':'False','effective_threshold':'150M',
  'policy_source_and_build_match':True,'archived_submitted_config_sha256_matches':True,
  'submitted_config_file_id':'8a44769e28c1a68c618ab62b28eb20f29e1e29f8c2d06a136824a973717e1c9a',
  'submitted_config_catalogue_verification':'SHA256_VERIFIED_ARCHIVE_MEMBER',
  'actual_dispatch_config_audit':'R14-CONFIG-AUDIT-20261021.json',
  'upload_shell_sha256':R14_UPLOAD_SHELL_SHA256,
  'bounded_archive_statement':'157286400 < actual archive bytes <= 536870912 inferred from pinned mandatory guard + successful steps.',
  'sidecar_limitation':'External receipts unavailable via Reader; exact size/upload timing UNKNOWN. No raw read.',
  'historical_R13_records_modified':False,'old_probe_charged_to_R14':False}
 if not isinstance(coverage,dict) or not expected_coverage.keys()<=coverage.keys() or any(coverage.get(key)!=value for key,value in expected_coverage.items()):
  raise SystemExit('R14 G6 coverage identity')
 for key in ('catalogue_complete','policy_exact','policy_complete','policy_source_and_build_match',
             'archived_submitted_config_sha256_matches','historical_R13_records_modified','old_probe_charged_to_R14'):
  if type(coverage.get(key)) is not bool:
   raise SystemExit('R14 G7 coverage flag type')
 if type(coverage.get('catalogue_members')) is not int:
  raise SystemExit('R14 G8 catalogue count type')
 observed=coverage.get('observed_utc')
 try:
  observed_time=datetime.datetime.fromisoformat(observed.replace('Z','+00:00')) if isinstance(observed,str) else None
 except ValueError:
  observed_time=None
 if (observed_time is None or observed_time.tzinfo is None or
     observed_time<datetime.datetime.fromisoformat('2026-10-21T12:52:50+00:00') or
     observed_time>datetime.datetime.now(datetime.timezone.utc)):
  raise SystemExit('R14 G9 observation time')


def r14_read_selected_gate(proof_sha):
 if not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R14 S1 source SHA')
 try:
  selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  target=ROOT/R14_GATE_PATH
  if target.is_symlink() or not target.is_file():raise ValueError('publication gate is not a regular file')
  worktree=target.read_bytes()
  gate=json.loads(selected)
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R14 S2 selected gate unreadable')
 if selected!=worktree:
  raise SystemExit('R14 S3 gate differs from selected bytes')
 r14_validate_gate_record(gate)
 return gate


def r14_validate_runtime_maps(before,after,expected_additions):
 if set(expected_additions)!={R14_GATE_PATH,R14_LEDGER_PATH,
     'research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py'}:
  raise SystemExit('R14 C1 registration allowlist')
 ignore={R14_GATE_PATH,R14_LEDGER_PATH,
         'research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py',
         R14_R13_LEDGER_PATH,
         'research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json',
         'research/challenge-8/cloud-build/recipes/merge.json'}
 control_path='research/challenge-8/cloud-build/control.py'
 before_paths=set(before)-ignore;after_paths=set(after)-ignore
 if before_paths!=after_paths:
  raise SystemExit('R14 C2 runtime paths changed')
 for path in sorted(before_paths-{control_path}):
  if before[path]!=after[path]:raise SystemExit('R14 C3 changed input: '+path)
 if control_path not in before_paths:
  raise SystemExit('R14 C4 control.py absent')
 if before[control_path][:2]!=after[control_path][:2] or before[control_path][0] not in ('100644','100755'):
  raise SystemExit('R14 C5 control.py mode')


def r14_validate_historical_ledger(probe_entry,proof_entry,checkpoint_entry):
 if (not all(isinstance(item,tuple) and len(item)==3 for item in (probe_entry,proof_entry,checkpoint_entry)) or
     proof_entry!=checkpoint_entry or checkpoint_entry[:2]!=('100644','blob')):
  raise SystemExit('R14 C6 R13 account snapshot')


def r14_validate_recipe_delta(before_recipe,after_recipe,expected_additions):
 if not isinstance(before_recipe,dict) or not isinstance(after_recipe,dict):
  raise SystemExit('R14 C7 recipe object')
 before_paths=before_recipe.get('proof_paths');after_paths=after_recipe.get('proof_paths')
 if (not isinstance(before_paths,list) or not isinstance(after_paths,list) or
     before_paths!=sorted(set(before_paths)) or after_paths!=sorted(set(after_paths))):
  raise SystemExit('R14 C8 recipe paths noncanonical')
 before_body={key:value for key,value in before_recipe.items() if key!='proof_paths'}
 after_body={key:value for key,value in after_recipe.items() if key!='proof_paths'}
 if before_body!=after_body:
  raise SystemExit('R14 C9 recipe metadata changed')
 if set(after_paths)-set(before_paths)!=set(expected_additions) or set(before_paths)-set(after_paths):
  raise SystemExit('R14 C10 recipe path delta')


def r14_validate_mode_transition(before_card,after_card):
 expected_before={'schema':'merge-r13-upload-mode-v1','mode':'synthetic-upload',
  'payload_bytes':268435456,'threshold_bytes':157286400,'archive_limit_bytes':536870912,
  'threshold_source':'https://docs.cloud.google.com/storage/docs/parallel-composite-uploads',
  'proof_attempted':False}
 expected_after={'schema':'merge-r13-upload-mode-v1','mode':'proof-r11','archive_limit_bytes':536870912}
 if (not isinstance(before_card,dict) or not isinstance(after_card,dict) or
     before_card!=expected_before or after_card!=expected_after or
     any(type(before_card.get(k)) is not int for k in ('payload_bytes','threshold_bytes','archive_limit_bytes')) or
     type(before_card.get('proof_attempted')) is not bool or
     type(after_card.get('archive_limit_bytes')) is not int):
  raise SystemExit('R14 C11 mode transition')


def r14_validate_publisher_control(before_control,after_control):
 tree=ast.parse(after_control); baseline=ast.parse(before_control)
 def segment(parsed,text,name):
  node=next((n for n in parsed.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
  return ast.get_source_segment(text,node) if node else None
 if any(segment(baseline,before_control,n)!=segment(tree,after_control,n)
        for n in ('envs','config')):
  raise SystemExit('R14 C12 publisher config changed')
 expected="def required_upload_guard(phase):return phase in ('MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21','MERGE-PUBLICATION-GATE-PROOF-R14-2026-10-21','MERGE-SINGLETON-ARRAY-PROOF-R15-2026-10-21','MERGE-CALLER-CURRENT-PROOF-R16-2026-10-21','MERGE-CALLER-REFINEMENT-R17-2026-10-21','MERGE-RAW-CALLER-R18-2026-10-22','MERGE-UNWIND-CLEANUP-R19-2026-10-22','MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23','MERGE-CALLER-ACCEPTANCE-R21-2026-10-23','MERGE-CALLER-ACCEPTANCE-R22-2026-10-23',R23_PHASE)"
 if segment(tree,after_control,'required_upload_guard')!=expected:
  raise SystemExit('R14 C13 guard route')
 command=segment(tree,after_control,'run_command') or ''
 if 'r13_required=required_upload_guard(a.phase_id)' not in command:
  raise SystemExit('R14 C14 guard marker not routed')
 def assignments(parsed):
  return {t.id:ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign)
          for t in n.targets if isinstance(t,ast.Name) and t.id in {'BUCKET','UBUNTU','SDK','ACCOUNT','SDK_PYTHON'}}
 if assignments(baseline)!=assignments(tree) or len(assignments(baseline))!=5:
  raise SystemExit('R14 C15 publisher identity changed')


def r14_validate_retry_sources(probe_sha,proof_sha):
 expected_additions={R14_GATE_PATH,R14_LEDGER_PATH,
  'research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py'}
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 mode_path='research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json'
 try:
  before_recipe_raw=subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  after_recipe_raw=subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  before_recipe=json.loads(before_recipe_raw);after_recipe=json.loads(after_recipe_raw)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R14 R1 recipe unreadable')
 r14_validate_recipe_delta(before_recipe,after_recipe,expected_additions)
 try:
  before_card=json.loads(subprocess.check_output(['git','show',probe_sha+':'+mode_path],cwd=ROOT,stderr=subprocess.PIPE))
  after_card=json.loads(subprocess.check_output(['git','show',proof_sha+':'+mode_path],cwd=ROOT,stderr=subprocess.PIPE))
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R14 R2 mode card unreadable')
 r14_validate_mode_transition(before_card,after_card)

 def inventory(commit,recipe,recipe_raw):
  spec=importlib.util.spec_from_file_location('r14_pinned_source',DIR/'source-input.py')
  source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
  paths=sorted(set([p for p in recipe['proof_paths'] if not p.endswith('.md')]+
                   recipe['infra_paths']+source.infra_paths(ROOT,commit)+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if not record:continue
   meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
   if mode not in ('100644','100755') or kind!='blob':
    raise SystemExit('R14 R3 nonregular runtime input')
   found[path.decode()]=(mode,kind,oid)
  if set(found)!=set(paths):raise SystemExit('R14 R4 incomplete runtime closure')
  return found
 before=inventory(probe_sha,before_recipe,before_recipe_raw)
 after=inventory(proof_sha,after_recipe,after_recipe_raw)
 if before.get(mode_path,('',))[0:2]!=('100644','blob') or after.get(mode_path,('',))[0:2]!=('100644','blob'):
  raise SystemExit('R14 R5 mode card type')
 checkpoint_raw=subprocess.check_output(['git','ls-tree','-r','-z',R14_CLOSED_R13_CHECKPOINT,'--',R14_R13_LEDGER_PATH],cwd=ROOT,stderr=subprocess.PIPE)
 checkpoint_entries=[]
 for record in checkpoint_raw.split(b'\0'):
  if record:
   meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
   checkpoint_entries.append((path.decode(),(mode,kind,oid)))
 if len(checkpoint_entries)!=1 or checkpoint_entries[0][0]!=R14_R13_LEDGER_PATH:
  raise SystemExit('R14 R6 checkpoint ledger missing')
 r14_validate_historical_ledger(before.get(R14_R13_LEDGER_PATH),after.get(R14_R13_LEDGER_PATH),checkpoint_entries[0][1])
 try:
  current_historical=(ROOT/R14_R13_LEDGER_PATH).read_bytes()
  checkpoint_historical=subprocess.check_output(['git','show',R14_CLOSED_R13_CHECKPOINT+':'+R14_R13_LEDGER_PATH],cwd=ROOT,stderr=subprocess.PIPE)
 except (OSError,subprocess.CalledProcessError):
  raise SystemExit('R14 R7 checkpoint unreadable')
 if current_historical!=checkpoint_historical:
  raise SystemExit('R14 R8 working tree changed R13 ledger')
 ignore={recipe_path,mode_path}|expected_additions
 r14_validate_runtime_maps(before,after,expected_additions)
 control_path='research/challenge-8/cloud-build/control.py'
 def git_bytes(commit,path):
  return subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
 before_control=git_bytes(probe_sha,control_path).decode('utf-8')
 after_control=git_bytes(proof_sha,control_path).decode('utf-8')
 r14_validate_publisher_control(before_control,after_control)


def r15_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R15 S3 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 required_additions={R15_LEDGER_PATH}
 required_removals=R15_RECIPE_REMOVALS
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!=required_additions or
     set(old_paths)-set(new_paths)!=required_removals):
  raise SystemExit('R15 S4 recipe path closure/registration mismatch')


def r15_validate_transport_size(payload_bytes):
 if type(payload_bytes) is not int or payload_bytes<0:
  raise SystemExit('R15 S16 invalid source payload size')
 encoded_size=4*((payload_bytes+2)//3)
 if encoded_size>191*3990:raise SystemExit('R15 S16 source payload exceeds existing bounded transport')
 return encoded_size


def r15_set_execute_budget(cfg,timeout):
 if type(timeout) is not int or not 510<=timeout<=1200:
  raise SystemExit('R15 requires timeout510..1200 to reserve 420s for publication')
 steps=cfg.get('steps') if isinstance(cfg,dict) else None
 if not isinstance(steps,list) or not steps or not isinstance(steps[0],dict):
  raise SystemExit('R15 E1 generated execute step missing')
 args=steps[0].get('args')
 if not isinstance(args,list) or len(args)<2 or not isinstance(args[1],str):
  raise SystemExit('R15 E2 generated execute body missing')
 body=args[1];old=timeout-70;execute=timeout-420
 deadline=f' + {old} - 15 '
 timeout_arg=f'"{old}s" bash'
 if body.count(deadline)!=1 or body.count(timeout_arg)!=1:
  raise SystemExit('R15 E3 generated execute budget markers differ')
 body=body.replace(deadline,f' + {execute} - 15 ',1).replace(timeout_arg,f'"{execute}s" bash',1)
 args[1]=body
 return execute


def r15_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R15_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R15 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before_raw=subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  selected_raw=subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  before=json.loads(before_raw);selected=json.loads(selected_raw)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R15 S2 recipe unavailable')
 r15_validate_recipe_delta(before,selected)
 old_paths=before['proof_paths'];new_paths=selected['proof_paths']
 check_paths={path for path in old_paths
              if 'BUDGET' in path.rsplit('/',1)[-1].upper() and path!=R15_LEDGER_PATH}
 check_paths.update({R14_GATE_PATH,R13_MODE_PATH})
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R15 S5 historical tree unavailable')
 if (set(old_map)!=check_paths or new_map!=old_map or
     any(value[:2]!=('100644','blob') for value in new_map.values())):
  raise SystemExit('R15 S6 historical ledger or R14 gate changed')
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_probe=subprocess.check_output(['git','show',probe_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R15 S7 accepted R14 publication gate unavailable')
 if gate_selected!=gate_probe or gate_current!=gate_selected:
  raise SystemExit('R15 S8 R14 publication gate bytes changed')
 try:
  before_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R15 S9 publisher control unavailable')
 r14_validate_publisher_control(before_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r15_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha)
  paths=sorted(set(new_paths+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R15 S10 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R15 S11 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R15 S12 incomplete selected source closure')
 for path,(mode,kind,oid) in found.items():
  target=ROOT/path
  if target.is_symlink() or not target.is_file():raise SystemExit('R15 S13 source input missing: '+path)
  data=target.read_bytes()
  if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=oid:
   raise SystemExit('R15 S14 worktree bytes differ from selected source: '+path)
  executable=bool(target.stat().st_mode & 0o111)
  if executable!=(mode=='100755'):raise SystemExit('R15 S15 worktree mode differs from selected source: '+path)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r16_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R16 S2 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!={R16_LEDGER_PATH} or set(old_paths)-set(new_paths)):
  raise SystemExit('R16 S3 recipe path closure/registration mismatch')


def r16_validate_execute_budget(cfg,timeout):
 if type(timeout) is not int or not 510<=timeout<=1200:
  raise SystemExit('R16 requires timeout510..1200 with publication reserve')
 steps=cfg.get('steps') if isinstance(cfg,dict) else None
 if not isinstance(steps,list) or not steps or not isinstance(steps[0],dict):
  raise SystemExit('R16 E1 generated execute step missing')
 args=steps[0].get('args')
 if not isinstance(args,list) or len(args)<2 or not isinstance(args[1],str):
  raise SystemExit('R16 E2 generated execute body missing')
 body=args[1];old=timeout-70;execute=timeout-420
 if execute>780 or execute<90:
  raise SystemExit('R16 E3 execute budget outside authorized reserve')
 deadline=f' + {old} - 15 '
 timeout_arg=f'"{old}s" bash'
 if body.count(deadline)!=1 or body.count(timeout_arg)!=1:
  raise SystemExit('R16 E4 generated execute budget markers differ')
 body=body.replace(deadline,f' + {execute} - 15 ',1).replace(timeout_arg,f'"{execute}s" bash',1)
 args[1]=body
 return execute


def r16_validate_worktree_entry(path,mode,oid):
 target=ROOT/path
 if target.is_symlink() or not target.is_file():raise SystemExit('R16 S13 source input missing: '+path)
 data=target.read_bytes()
 if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=oid:
  raise SystemExit('R16 S14 worktree bytes differ from selected source: '+path)
 if bool(target.stat().st_mode & 0o111)!=(mode=='100755'):
  raise SystemExit('R16 S15 worktree mode differs from selected source: '+path)


def r16_validate_historical_closure(paths,before,selected):
 required={R13_MODE_PATH,R14_GATE_PATH}
 if (not required.issubset(paths) or set(before)!=set(paths) or set(selected)!=set(paths) or
     selected!=before or any(value[:2]!=('100644','blob') for value in selected.values())):
  raise SystemExit('R16 S6 historical ledger, R13 mode, or R14 gate changed')


def r16_final_deadline_check(a,ledger):
 checked_at=datetime.datetime.now(datetime.timezone.utc)
 main_deadline=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00'))
 cutoff=datetime.datetime.fromisoformat('2026-10-21T18:38:24+00:00')
 if checked_at>=main_deadline:
  raise SystemExit('R16 A6 main window expired during final source validation')
 if checked_at+datetime.timedelta(seconds=a.timeout+60)>cutoff:
  raise SystemExit('R16 A7 Build plus queue reserve exceeds absolute deadline after validation')


def r16_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R16_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R16 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before_raw=subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  selected_raw=subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  before=json.loads(before_raw);selected=json.loads(selected_raw)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R16 S4 recipe unavailable')
 r16_validate_recipe_delta(before,selected)
 check_paths={path for path in before['proof_paths']
              if 'BUDGET' in path.rsplit('/',1)[-1].upper()}
 check_paths.update({R13_MODE_PATH,R14_GATE_PATH})
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R16 S5 historical tree unavailable')
 r16_validate_historical_closure(check_paths,old_map,new_map)
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_probe=subprocess.check_output(['git','show',probe_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R16 S7 accepted R14 publication gate unavailable')
 if gate_selected!=gate_probe or gate_current!=gate_selected:
  raise SystemExit('R16 S8 R14 publication gate bytes changed')
 try:
  before_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R16 S9 publisher control unavailable')
 r14_validate_publisher_control(before_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r16_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha)
  paths=sorted(set(selected['proof_paths']+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R16 S10 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R16 S11 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R16 S12 incomplete selected source closure')
 for path,(mode,kind,oid) in found.items():
  r16_validate_worktree_entry(path,mode,oid)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r17_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R17 S2 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!={R17_LEDGER_PATH,R17_PROFILE_PATH,R17_CONTROLS_PATH} or
     set(old_paths)-set(new_paths)):
  raise SystemExit('R17 S3 recipe path closure/registration mismatch')


def r17_validate_execute_budget(cfg,timeout):
 if type(timeout) is not int or not 510<=timeout<=1200:
  raise SystemExit('R17 requires timeout510..1200 with publication reserve')
 steps=cfg.get('steps') if isinstance(cfg,dict) else None
 if not isinstance(steps,list) or not steps or not isinstance(steps[0],dict):
  raise SystemExit('R17 E1 generated execute step missing')
 args=steps[0].get('args')
 if not isinstance(args,list) or len(args)<2 or not isinstance(args[1],str):
  raise SystemExit('R17 E2 generated execute body missing')
 body=args[1];old=timeout-70;execute=timeout-420
 if execute>780 or execute<90:
  raise SystemExit('R17 E3 execute budget outside authorized reserve')
 if body.count(f' + {old} - 15 ')!=1 or body.count(f'"{old}s" bash')!=1:
  raise SystemExit('R17 E4 generated execute budget markers differ')
 args[1]=body.replace(f' + {old} - 15 ',f' + {execute} - 15 ',1).replace(f'"{old}s" bash',f'"{execute}s" bash',1)
 return execute


def r17_validate_profile_baseline(baseline,selected):
 if not isinstance(baseline,bytes) or not isinstance(selected,bytes) or baseline!=selected:
  raise SystemExit('R17 S6 baseline profile bytes differ from the selected starting profile')


def r17_validate_profile_delta(before,selected):
 try:
  old=json.loads(before);new=json.loads(selected)
 except (ValueError,TypeError,UnicodeDecodeError):
  raise SystemExit('R17 S7 profile JSON unavailable')
 if not isinstance(old,dict) or not isinstance(new,dict):
  raise SystemExit('R17 S7 profile JSON must be objects')
 allowed={'effective_tool_commit','refiner_core_source_sha256',
          'guard_return_trace_patch_sha256','ordered_patch_chain',R17_PROFILE_REGISTRATION}
 if set(old)-set(new) or set(new)-set(old)-{R17_PROFILE_REGISTRATION}:
  raise SystemExit('R17 S8 unrelated profile field added or removed')
 changed={key for key in set(old)|set(new) if old.get(key)!=new.get(key)}
 if not changed.issubset(allowed) or not allowed.issubset(changed|{key for key in allowed if old.get(key)==new.get(key)}):
  raise SystemExit('R17 S9 profile changed outside the reviewed pin/registration set')
 registration=new.get(R17_PROFILE_REGISTRATION)
 expected={'schema':'merge-r17-profile-registration-v1','phase_id':R17_PHASE,
  'baseline_profile_path':R17_PROFILE_PATH,'starting_tool_commit':'660b576b6b1608db913c51e0785b443a8733396f',
  'starting_source_sha':R17_STARTING_SOURCE_SHA,'owner':'merge','lane':'merge',
  'tool_source_paths':['src/refinement_checker/refinement_checker.ml'],
  'source_applicability':'paired RawPtr bare local only; exact mutability/full MIR and decoded local type/place; existing equal-state allocation reconciliation; no borrow or memory authority'}
 if (type(registration) is not dict or set(registration)!=(set(expected)|{'candidate_tool_commit'}) or
     any(registration.get(k)!=v for k,v in expected.items())):
  raise SystemExit('R17 S10 profile registration identity/scope mismatch')
 candidate=registration.get('candidate_tool_commit')
 source_hash=new.get('refiner_core_source_sha256')
 patch_hash=new.get('guard_return_trace_patch_sha256')
 old_chain=old.get('ordered_patch_chain')
 new_chain=new.get('ordered_patch_chain')
 if (not isinstance(candidate,str) or not re.fullmatch('[0-9a-f]{40}',candidate) or
     candidate!=R17_CANDIDATE_TOOL_SHA or source_hash!=R17_REFINER_CORE_SOURCE_SHA256 or
     patch_hash!=R17_PATCH_SHA256 or
     candidate!=new.get('effective_tool_commit') or
     not isinstance(source_hash,str) or not re.fullmatch('[0-9a-f]{64}',source_hash) or
     not isinstance(patch_hash,str) or not re.fullmatch('[0-9a-f]{64}',patch_hash) or
     not isinstance(old_chain,list) or len(old_chain)!=19 or
     not isinstance(new_chain,list) or len(new_chain)!=19 or
     new_chain[:-1]!=old_chain[:-1] or type(new_chain[-1]) is not dict or
     type(old_chain[-1]) is not dict or
     old_chain[-1].get('path')!=R17_PATCH_PATH or new_chain[-1].get('path')!=R17_PATCH_PATH or
     new_chain[-1].get('sha256')!=patch_hash):
  raise SystemExit('R17 S11 candidate tool/source/patch pins mismatch')


def r17_validate_worktree_entry(path,mode,oid):
 target=ROOT/path
 if target.is_symlink() or not target.is_file():raise SystemExit('R17 S13 source input missing: '+path)
 data=target.read_bytes()
 if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=oid:
  raise SystemExit('R17 S14 worktree bytes differ from selected source: '+path)
 if bool(target.stat().st_mode & 0o111)!=(mode=='100755'):
  raise SystemExit('R17 S15 worktree mode differs from selected source: '+path)


def r17_validate_historical_closure(paths,before,selected):
 required={R16_LEDGER_PATH,R13_MODE_PATH,R14_GATE_PATH}
 if (not required.issubset(paths) or set(before)!=set(paths) or set(selected)!=set(paths) or
     selected!=before or any(value[:2]!=('100644','blob') for value in selected.values())):
  raise SystemExit('R17 S7 historical ledger, R13 mode, or R14 gate changed')


def r17_parse_provider_pin_tables(source):
 try:
  if not isinstance(source,bytes):raise ValueError('not bytes')
  module=ast.parse(source.decode('utf-8'))
  tables={}
  for node in module.body:
   if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('FILES','R11_FILES'):
    name=node.targets[0].id
    if name in tables or not isinstance(node.value,ast.Dict):raise ValueError('duplicate or non-dict table')
    keys=[];values=[]
    for key,value in zip(node.value.keys,node.value.values):
     if (not isinstance(key,ast.Constant) or type(key.value) is not str or
         not isinstance(value,ast.Constant) or type(value.value) is not str):
      raise ValueError('nonliteral path or digest')
     keys.append(key.value);values.append(value.value)
    if len(keys)!=len(set(keys)):raise ValueError('duplicate path')
    table=ast.literal_eval(node.value)
    if type(table) is not dict or len(table)!=len(keys):raise ValueError('invalid table')
    if any(not re.fullmatch('[0-9a-f]{64}',digest) for digest in values):raise ValueError('invalid digest')
    tables[name]=table
  if set(tables)!= {'FILES','R11_FILES'} or len(tables['FILES'])!=18 or len(tables['R11_FILES']) not in (2,3):
   raise ValueError('wrong table schema/count')
  if set(tables['FILES']) & set(tables['R11_FILES']):raise ValueError('overlapping tables')
  return tables
 except (SyntaxError,UnicodeDecodeError,ValueError,TypeError,RecursionError):
  raise SystemExit('R17 S16 malformed provider pin tables')


def r22_parse_provider_pin_tables(source):
 try:
  if not isinstance(source,bytes):raise ValueError('not bytes')
  module=ast.parse(source.decode('utf-8'))
  tables={}
  for node in module.body:
   if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('FILES','R11_FILES','R22_FILES','R22_OWNED_NLL_FILES'):
    name=node.targets[0].id
    if name in tables or not isinstance(node.value,ast.Dict):raise ValueError('duplicate or non-dict table')
    keys=[];values=[]
    for key,value in zip(node.value.keys,node.value.values):
     if (not isinstance(key,ast.Constant) or type(key.value) is not str or
         not isinstance(value,ast.Constant) or type(value.value) is not str):
      raise ValueError('nonliteral path or digest')
     keys.append(key.value);values.append(value.value)
    if len(keys)!=len(set(keys)):raise ValueError('duplicate path')
    table=ast.literal_eval(node.value)
    if type(table) is not dict or len(table)!=len(keys):raise ValueError('invalid table')
    if any(not re.fullmatch('[0-9a-f]{64}',digest) for digest in values):raise ValueError('invalid digest')
    tables[name]=table
  if set(tables)!= {'FILES','R11_FILES','R22_FILES','R22_OWNED_NLL_FILES'} or len(tables['FILES'])!=18 or len(tables['R11_FILES']) not in (2,3) or len(tables['R22_FILES'])!=len(tables['R11_FILES']) or len(tables['R22_OWNED_NLL_FILES'])!=len(tables['R11_FILES']):
   raise ValueError('wrong table schema/count')
  if set(tables['FILES']) & (set(tables['R11_FILES'])|set(tables['R22_FILES'])|set(tables['R22_OWNED_NLL_FILES'])):
   raise ValueError('provider tables overlap common sources')
  proof_path='research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py'
  if set(tables['R11_FILES'])!=set(tables['R22_FILES']) or set(tables['R11_FILES'])!=set(tables['R22_OWNED_NLL_FILES']) or proof_path not in tables['R22_FILES']:
   raise ValueError('R22 provider path set differs from R11')
  if any(tables['R11_FILES'][path]!=tables['R22_FILES'][path] or tables['R11_FILES'][path]!=tables['R22_OWNED_NLL_FILES'][path]
         for path in set(tables['R11_FILES'])-{proof_path}):
   raise ValueError('R22 control pins differ from R11')
  if (tables['R11_FILES'][proof_path] in (tables['R22_FILES'][proof_path],tables['R22_OWNED_NLL_FILES'][proof_path]) or
      tables['R22_FILES']!=tables['R22_OWNED_NLL_FILES']):
   raise ValueError('R22 profile pin tables are not exact and distinct from historical R11')
  return tables
 except (SyntaxError,UnicodeDecodeError,ValueError,TypeError,RecursionError):
  raise SystemExit('R22 S16 malformed provider pin tables')


def r17_validate_provider_module_delta(baseline_source,selected_source):
 old_prove=R17_PROVIDER_OLD_PROVE_SHA256.encode()
 new_prove=R17_PROVIDER_NEW_PROVE_SHA256.encode()
 new_compat=R17_PROVIDER_NEW_COMPAT_SHA256.encode()
 compat_path=R17_PROVIDER_COMPAT_PATH.encode()
 old_anchor=(b'    "research/challenge-8/cloud-build/origin-layout/'
             b'r11-storage-placement-controls.py": "0bea1e5390aa6297975552a9f29d600c8e7f9f6ab30caf26b07d27979cddf100",\n}')
 new_anchor=old_anchor[:-2]+b'\n    "'+compat_path+b'": "'+new_compat+b'",\n}'
 if (not isinstance(baseline_source,bytes) or not isinstance(selected_source,bytes) or
     baseline_source.count(old_prove)!=1 or baseline_source.count(new_prove)!=0 or
     baseline_source.count(new_compat)!=0 or
     baseline_source.count(compat_path)!=0 or baseline_source.count(old_anchor)!=1):
  raise SystemExit('R17 S16 provider module baseline differs from the reviewed source')
 expected=baseline_source.replace(old_prove,new_prove,1).replace(old_anchor,new_anchor,1)
 if selected_source!=expected:
  raise SystemExit('R17 S16 provider module contains an unreviewed change')


def r17_validate_provider_pin_tables(baseline_source,selected_source,closure_paths,read_selected_source):
 r17_validate_provider_module_delta(baseline_source,selected_source)
 baseline=r17_parse_provider_pin_tables(baseline_source)
 selected=r17_parse_provider_pin_tables(selected_source)
 if (set(selected['FILES'])!=set(baseline['FILES']) or
     set(selected['R11_FILES'])!=set(baseline['R11_FILES'])|{R17_PROVIDER_COMPAT_PATH}):
  raise SystemExit('R17 S16 provider pin path set changed')
 all_paths=set(selected['FILES'])|set(selected['R11_FILES'])
 if R17_PROVIDER_OVERLAYS_PATH not in closure_paths or not all_paths.issubset(closure_paths):
  raise SystemExit('R17 S16 provider pins absent from selected source closure')
 for name in ('FILES','R11_FILES'):
  for path,digest in selected[name].items():
   try:data=read_selected_source(path)
   except (OSError,subprocess.CalledProcessError,KeyError):
    raise SystemExit('R17 S16 provider pin source unavailable: '+path)
   if not isinstance(data,bytes) or hashlib.sha256(data).hexdigest()!=digest:
    raise SystemExit('R17 S16 provider pin source mismatch: '+path)


def r17_final_deadline_check(a,ledger):
 checked_at=datetime.datetime.now(datetime.timezone.utc)
 main_deadline=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00'))
 cutoff=datetime.datetime.fromisoformat('2026-10-21T21:03:50+00:00')
 if checked_at>=main_deadline:
  raise SystemExit('R17 A6 main window expired during final source validation')
 if checked_at+datetime.timedelta(seconds=a.timeout+60)>cutoff:
  raise SystemExit('R17 A7 Build plus queue reserve exceeds absolute deadline after validation')


def r17_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R17_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R17 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before_raw=subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  selected_raw=subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  before=json.loads(before_raw);selected=json.loads(selected_raw)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R17 S4 recipe unavailable')
 r17_validate_recipe_delta(before,selected)
 check_paths={path for path in before['proof_paths']
              if 'BUDGET' in path.rsplit('/',1)[-1].upper()}
 check_paths.update({R13_MODE_PATH,R14_GATE_PATH})
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R17 S5 historical tree unavailable')
 r17_validate_historical_closure(check_paths,old_map,new_map)
 try:
  baseline_profile=subprocess.check_output(['git','show',proof_sha+':'+R17_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  starting_profile=subprocess.check_output(['git','show',probe_sha+':research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json'],cwd=ROOT,stderr=subprocess.PIPE)
  current_baseline=(ROOT/R17_PROFILE_PATH).read_bytes()
  selected_profile=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json'],cwd=ROOT,stderr=subprocess.PIPE)
  current_profile=(ROOT/'research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json').read_bytes()
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R17 S6 baseline profile unavailable')
 r17_validate_profile_baseline(baseline_profile,starting_profile)
 if current_baseline!=baseline_profile:
  raise SystemExit('R17 S6 worktree baseline profile differs from selected source')
 r17_validate_profile_delta(starting_profile,selected_profile)
 if current_profile!=selected_profile:
  raise SystemExit('R17 S12 worktree profile differs from selected source')
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_probe=subprocess.check_output(['git','show',probe_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R17 S8 accepted R14 publication gate unavailable')
 if gate_selected!=gate_probe or gate_current!=gate_selected:
  raise SystemExit('R17 S9 R14 publication gate bytes changed')
 try:
  before_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R17 S10 publisher control unavailable')
 r14_validate_publisher_control(before_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r17_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha)
  paths=sorted(set(selected['proof_paths']+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R17 S11 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R17 S12 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R17 S13 incomplete selected source closure')
 try:
  provider_baseline=subprocess.check_output(['git','show',probe_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  provider_selected=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  def read_pinned_source(path):
   return subprocess.check_output(['git','show',proof_sha+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
  r17_validate_provider_pin_tables(provider_baseline,provider_selected,set(paths),read_pinned_source)
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R17 S16 provider pin source unavailable')
 for path,(mode,kind,oid) in found.items():r17_validate_worktree_entry(path,mode,oid)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r18_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R18 S2 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!={R18_LEDGER_PATH} or
     set(old_paths)-set(new_paths)):
  raise SystemExit('R18 S3 recipe path closure/registration mismatch')


def r18_validate_historical_closure(paths,before,selected):
 required={R17_LEDGER_PATH,R16_LEDGER_PATH,R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R18_PROFILE_PATH}
 if (not required.issubset(paths) or set(before)!=set(paths) or set(selected)!=set(paths) or
     selected!=before or any(value[:2]!=('100644','blob') for value in selected.values())):
  raise SystemExit('R18 S7 historical ledger, profile, R13 mode, or R14 gate changed')


def r18_final_deadline_check(a,ledger):
 checked_at=datetime.datetime.now(datetime.timezone.utc)
 main_deadline=datetime.datetime.fromisoformat(R18_MAIN_DEADLINE.replace('Z','+00:00'))
 cutoff=datetime.datetime.fromisoformat(R18_DEADLINE.replace('Z','+00:00'))
 if ledger.get('main_deadline_utc')!=R18_MAIN_DEADLINE or checked_at>=main_deadline:
  raise SystemExit('R18 A6 main window expired during final source validation')
 if checked_at+datetime.timedelta(seconds=a.timeout+60)>cutoff:
  raise SystemExit('R18 A7 Build plus queue reserve exceeds absolute deadline after validation')


def r18_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R18_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R18 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before=json.loads(subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
  selected=json.loads(subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R18 S4 recipe unavailable')
 r18_validate_recipe_delta(before,selected)
 check_paths={path for path in before['proof_paths']
              if 'BUDGET' in path.rsplit('/',1)[-1].upper()}
 check_paths.update({R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R18_PROFILE_PATH,R17_PROVIDER_OVERLAYS_PATH})
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R18 S5 historical tree unavailable')
 r18_validate_historical_closure(check_paths,old_map,new_map)
 try:
  selected_profile=subprocess.check_output(['git','show',proof_sha+':'+R18_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_profile=(ROOT/R18_PROFILE_PATH).read_bytes()
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R18 S6 pinned profile unavailable')
 if hashlib.sha256(selected_profile).hexdigest()!=R18_PROFILE_SHA256 or current_profile!=selected_profile:
  raise SystemExit('R18 S6 pinned profile bytes differ from the R18 baseline')
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R18 S8 accepted R14 publication gate unavailable')
 if gate_current!=gate_selected:
  raise SystemExit('R18 S9 R14 publication gate bytes changed')
 try:
  before_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R18 S10 publisher control unavailable')
 r14_validate_publisher_control(before_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r18_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha)
  paths=sorted(set(selected['proof_paths']+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R18 S11 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R18 S12 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R18 S13 incomplete selected source closure')
 try:
  provider_selected=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  def read_pinned_source(path):
   return subprocess.check_output(['git','show',proof_sha+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
  pins=r17_parse_provider_pin_tables(provider_selected)
  pinned={**pins['FILES'],**pins['R11_FILES']}
  if R17_PROVIDER_OVERLAYS_PATH not in found or not set(pinned).issubset(found):
   raise SystemExit('R18 S16 provider pins absent from selected source closure')
  for path,expected in pinned.items():
   if hashlib.sha256(read_pinned_source(path)).hexdigest()!=expected:
    raise SystemExit('R18 S16 provider pin source mismatch: '+path)
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R18 S16 provider pin source unavailable')
 for path,(mode,kind,oid) in found.items():r17_validate_worktree_entry(path,mode,oid)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r18_authorize(a,ledger):
 expected_ledger=DIR/R18_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
 builds=ledger.get('builds')
 if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
     ledger.get('owner')!='merge' or ledger.get('phase')!=R18_PHASE or ledger.get('phase_id')!=R18_PHASE or
     ledger.get('status')!='AUTHORIZED' or ledger.get('authorization_model')!='bounded-cloud-budget' or
     ledger.get('authorization')!=R18_AUTHORIZATION or ledger.get('ceiling_build_seconds')!=3600 or
     ledger.get('allowed_lanes')!=['merge'] or ledger.get('start_utc')!=R18_START or
     ledger.get('main_deadline_utc')!=R18_MAIN_DEADLINE or ledger.get('deadline_utc')!=R18_DEADLINE or
     ledger.get('baseline_sha')!=R18_BASELINE_SHA or
     'max_builds' not in ledger or ledger.get('max_builds') is not None or
     type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
     type(ledger.get('report_reserve_seconds')) is not int or ledger.get('report_reserve_seconds')<420 or
     ledger.get('carryover_allowed') is not False or ledger.get('carry_seconds')!=0 or
     ledger.get('publication_gate_path')!=R14_GATE_PATH or ledger.get('profile_path')!=R18_PROFILE_PATH or
     ledger.get('baseline_profile_sha256')!=R18_PROFILE_SHA256 or
     ledger.get('starting_source_sha')!=R18_STARTING_SOURCE_SHA or
     ledger.get('starting_tool_commit')!=R17_CANDIDATE_TOOL_SHA or
     type(ledger.get('used_build_seconds')) is not int or
     type(ledger.get('remaining_build_seconds')) is not int or
     not 0<=ledger.get('used_build_seconds')<=3600 or
     ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
     type(builds) is not list or
     type(ledger.get('spent_build_seconds')) is not int or
     ledger.get('spent_build_seconds')!=ledger.get('used_build_seconds') or
     ledger.get('retired_seconds')!=0 or
     'active_build' not in ledger or
     any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R18_PHASE or
         item.get('status') not in TERMINAL or item.get('accounted') is not True or
         not isinstance(item.get('build_id'),str) or not item.get('build_id') or
         type(item.get('build_seconds')) is not int or item.get('build_seconds')<0
         for item in builds) or
     sum(item['build_seconds'] for item in builds if type(item) is dict and
         type(item.get('build_seconds')) is int and item.get('build_seconds')>=0)!=ledger.get('used_build_seconds') or
     ledger.get('active_build') is not None):
  raise SystemExit('R18 A1 account authorization mismatch')
 now=datetime.datetime.now(datetime.timezone.utc)
 cutoff=datetime.datetime.fromisoformat(R18_DEADLINE.replace('Z','+00:00'))
 if now<datetime.datetime.fromisoformat(R18_START.replace('Z','+00:00')):
  raise SystemExit('R18 A2 window not started')
 if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(R18_MAIN_DEADLINE.replace('Z','+00:00')):
  raise SystemExit('R18 A3 main window expired')
 if a.command=='submit':
  if (type(a.timeout) is not int or not 510<=a.timeout<=1200 or a.lane!='merge' or
      a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
   raise SystemExit('R18 A4 requires one exact pinned source, merge lane, timeout510..1200')
  if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
   raise SystemExit('R18 A5 Build plus queue reserve exceeds absolute deadline')
  r14_read_selected_gate(a.proof_sha)
  r18_validate_sources(R18_PROBE_SOURCE,a.proof_sha)
  r18_final_deadline_check(a,ledger)
 return cutoff


def r19_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R19 S2 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!=R19_ADDED_PATHS or
     set(old_paths)-set(new_paths)!=R19_REMOVED_PATHS):
  raise SystemExit('R19 S3 recipe path closure/registration mismatch')


def r19_validate_historical_closure(paths,before,selected):
 required={R18_LEDGER_PATH,R17_LEDGER_PATH,R16_LEDGER_PATH,R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH}
 if (not required.issubset(paths) or set(before)!=set(paths) or set(selected)!=set(paths) or
     selected!=before or any(value[:2]!=('100644','blob') for value in selected.values())):
  raise SystemExit('R19 S7 historical ledger, profile, R13 mode, or R14 gate changed')


def r19_final_deadline_check(a,ledger):
 checked_at=datetime.datetime.now(datetime.timezone.utc)
 main_deadline=datetime.datetime.fromisoformat(R19_MAIN_DEADLINE.replace('Z','+00:00'))
 cutoff=datetime.datetime.fromisoformat(R19_DEADLINE.replace('Z','+00:00'))
 if ledger.get('main_deadline_utc')!=R19_MAIN_DEADLINE or checked_at>=main_deadline:
  raise SystemExit('R19 A6 main window expired during final source validation')
 if checked_at+datetime.timedelta(seconds=a.timeout+60)>cutoff:
  raise SystemExit('R19 A7 Build plus queue reserve exceeds absolute deadline after validation')


def r19_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R19_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R19 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before=json.loads(subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
  selected=json.loads(subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R19 S4 recipe unavailable')
 r19_validate_recipe_delta(before,selected)
 check_paths={path for path in before['proof_paths']
              if 'BUDGET' in path.rsplit('/',1)[-1].upper()}-R19_REMOVED_PATHS
 check_paths.update({R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH})
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R19 S5 historical tree unavailable')
 r19_validate_historical_closure(check_paths,old_map,new_map)
 try:
  selected_profile=subprocess.check_output(['git','show',proof_sha+':'+R19_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  probe_profile=subprocess.check_output(['git','show',probe_sha+':'+R19_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  selected_patch=subprocess.check_output(['git','show',proof_sha+':'+R17_PATCH_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  probe_provider=subprocess.check_output(['git','show',probe_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  selected_provider=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_profile=(ROOT/R19_PROFILE_PATH).read_bytes()
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R19 S6 pinned profile unavailable')
 if (hashlib.sha256(probe_profile).hexdigest()!=R19_BASELINE_PROFILE_SHA256 or
     hashlib.sha256(selected_profile).hexdigest()!=R19_PROFILE_SHA256 or current_profile!=selected_profile or
     hashlib.sha256(selected_patch).hexdigest()!=R19_PATCH_SHA256):
  raise SystemExit('R19 S6 profile or cumulative patch bytes differ from the reviewed R19 pins')
 if (probe_provider.count(R19_PROVIDER_OLD_PROVE_SHA256.encode())!=1 or
     selected_provider!=probe_provider.replace(R19_PROVIDER_OLD_PROVE_SHA256.encode(),R19_PROVIDER_NEW_PROVE_SHA256.encode(),1)):
  raise SystemExit('R19 S6 provider module differs from its exact prove pin delta')
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R19 S8 accepted R14 publication gate unavailable')
 if gate_current!=gate_selected:
  raise SystemExit('R19 S9 R14 publication gate bytes changed')
 try:
  before_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R19 S10 publisher control unavailable')
 r14_validate_publisher_control(before_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r19_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha)
  paths=sorted(set(selected['proof_paths']+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R19 S11 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R19 S12 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R19 S13 incomplete selected source closure')
 try:
  provider_selected=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  def read_pinned_source(path):
   return subprocess.check_output(['git','show',proof_sha+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
  pins=r17_parse_provider_pin_tables(provider_selected)
  pinned={**pins['FILES'],**pins['R11_FILES']}
  if R17_PROVIDER_OVERLAYS_PATH not in found or not set(pinned).issubset(found):
   raise SystemExit('R19 S16 provider pins absent from selected source closure')
  for path,expected in pinned.items():
   if hashlib.sha256(read_pinned_source(path)).hexdigest()!=expected:
    raise SystemExit('R19 S16 provider pin source mismatch: '+path)
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R19 S16 provider pin source unavailable')
 for path,(mode,kind,oid) in found.items():r17_validate_worktree_entry(path,mode,oid)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r19_authorize(a,ledger):
 expected_ledger=DIR/R19_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
 builds=ledger.get('builds')
 if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
     ledger.get('owner')!='merge' or ledger.get('phase')!=R19_PHASE or ledger.get('phase_id')!=R19_PHASE or
     ledger.get('status')!='AUTHORIZED' or ledger.get('authorization_model')!='bounded-cloud-budget' or
     ledger.get('authorization')!=R19_AUTHORIZATION or ledger.get('ceiling_build_seconds')!=3600 or
     ledger.get('allowed_lanes')!=['merge'] or ledger.get('start_utc')!=R19_START or
     ledger.get('main_deadline_utc')!=R19_MAIN_DEADLINE or ledger.get('deadline_utc')!=R19_DEADLINE or
     ledger.get('baseline_sha')!=R19_BASELINE_SHA or
     'max_builds' not in ledger or ledger.get('max_builds') is not None or
     type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
     type(ledger.get('report_reserve_seconds')) is not int or ledger.get('report_reserve_seconds')<420 or
     ledger.get('carryover_allowed') is not False or ledger.get('carry_seconds')!=0 or
     ledger.get('publication_gate_path')!=R14_GATE_PATH or ledger.get('profile_path')!=R19_PROFILE_PATH or
     ledger.get('baseline_profile_sha256')!=R19_BASELINE_PROFILE_SHA256 or
     ledger.get('starting_source_sha')!=R19_STARTING_SOURCE_SHA or
     ledger.get('starting_tool_commit')!=R17_CANDIDATE_TOOL_SHA or
     type(ledger.get('used_build_seconds')) is not int or
     type(ledger.get('remaining_build_seconds')) is not int or
     not 0<=ledger.get('used_build_seconds')<=3600 or
     ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
     type(builds) is not list or
     type(ledger.get('spent_build_seconds')) is not int or
     ledger.get('spent_build_seconds')!=ledger.get('used_build_seconds') or
     ledger.get('retired_seconds')!=0 or
     'active_build' not in ledger or
     any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R19_PHASE or
         item.get('status') not in TERMINAL or item.get('accounted') is not True or
         not isinstance(item.get('build_id'),str) or not item.get('build_id') or
         type(item.get('build_seconds')) is not int or item.get('build_seconds')<0
         for item in builds) or
     sum(item['build_seconds'] for item in builds if type(item) is dict and
         type(item.get('build_seconds')) is int and item.get('build_seconds')>=0)!=ledger.get('used_build_seconds') or
     ledger.get('active_build') is not None):
  raise SystemExit('R19 A1 account authorization mismatch')
 now=datetime.datetime.now(datetime.timezone.utc)
 cutoff=datetime.datetime.fromisoformat(R19_DEADLINE.replace('Z','+00:00'))
 if now<datetime.datetime.fromisoformat(R19_START.replace('Z','+00:00')):
  raise SystemExit('R19 A2 window not started')
 if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(R19_MAIN_DEADLINE.replace('Z','+00:00')):
  raise SystemExit('R19 A3 main window expired')
 if a.command=='submit':
  if (type(a.timeout) is not int or not 510<=a.timeout<=1200 or a.lane!='merge' or
      a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
   raise SystemExit('R19 A4 requires one exact pinned source, merge lane, timeout510..1200')
  if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
   raise SystemExit('R19 A5 Build plus queue reserve exceeds absolute deadline')
  r14_read_selected_gate(a.proof_sha)
  r19_validate_sources(R19_PROBE_SOURCE,a.proof_sha)
  r19_final_deadline_check(a,ledger)
 return cutoff


def r20_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R20 S2 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!=R20_ADDED_PATHS or
     set(old_paths)-set(new_paths)!=R20_REMOVED_PATHS):
  raise SystemExit('R20 S3 recipe path closure/registration mismatch')


def r20_validate_historical_closure(paths,before,selected,metadata_extension=False):
 required={R19_LEDGER_PATH,R18_LEDGER_PATH,R17_LEDGER_PATH,R16_LEDGER_PATH,
           R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R20_PROFILE_PATH}
 if (not required.issubset(paths) or set(before)!=set(paths) or set(selected)!=set(paths) or
     any(value[:2]!=('100644','blob') for value in selected.values())):
  raise SystemExit('R20 S7 historical R19 closure, profile, mode, or gate changed')
 differences={path for path in paths if before[path]!=selected[path]}
 expected={R20_PROFILE_PATH} if metadata_extension else set()
 if differences!=expected:
  raise SystemExit('R20 S7 historical closure changed outside the checked metadata profile extension')


def r20_validate_metadata_profile_extension(baseline_profile,selected_profile):
 try:
  old=json.loads(baseline_profile);new=json.loads(selected_profile)
 except (ValueError,TypeError,UnicodeDecodeError):
  raise SystemExit('R20 S6 metadata profile JSON unavailable')
 if (type(old) is not dict or type(new) is not dict or
     hashlib.sha256(baseline_profile).hexdigest()!=R20_PROFILE_SHA256 or
     new.get('r20_metadata_registration')!=R20_METADATA_REGISTRATION):
  raise SystemExit('R20 S6 metadata profile registration/baseline mismatch')
 baseline=copy.deepcopy(new)
 baseline.pop('r20_metadata_registration',None)
 baseline['effective_tool_commit']=R20_STARTING_TOOL_COMMIT
 baseline['refiner_core_source_sha256']=R20_R19_REFINER_CORE_SHA256
 baseline['exporter_source_sha256']=R20_R19_EXPORTER_SHA256
 baseline['schema_sha256']=R20_R19_SCHEMA_SHA256
 baseline['guard_return_trace_patch_sha256']=R20_PATCH_SHA256
 chain=baseline.get('ordered_patch_chain')
 if type(chain) is not list or len(chain)!=19 or type(chain[-1]) is not dict:
  raise SystemExit('R20 S6 metadata profile cumulative chain malformed')
 chain[-1]['sha256']=R20_PATCH_SHA256
 reverted=(json.dumps(baseline,indent=2)+'\n').encode()
 if hashlib.sha256(reverted).hexdigest()!=R20_PROFILE_SHA256:
  raise SystemExit('R20 S6 metadata profile changes fields outside the exact core/exporter/schema/tool/patch delta')
 if (hashlib.sha256(selected_profile).hexdigest()!=R20_METADATA_PROFILE_SHA256 or
     new.get('effective_tool_commit')!=R20_METADATA_TOOL_COMMIT or
     new.get('refiner_core_source_sha256')!=R20_METADATA_REFINER_CORE_SHA256 or
     new.get('exporter_source_sha256')!=R20_METADATA_EXPORTER_SHA256 or
     new.get('schema_sha256')!=R20_METADATA_SCHEMA_SHA256 or
     new.get('guard_return_trace_patch_sha256')!=R20_METADATA_PATCH_SHA256 or
     new.get('ordered_patch_chain')[-1].get('sha256')!=R20_METADATA_PATCH_SHA256):
  raise SystemExit('R20 S6 metadata candidate pins differ')


def r20_validate_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                                baseline_provider,selected_provider,current_provider):
 if (hashlib.sha256(baseline_profile).hexdigest()!=R20_PROFILE_SHA256 or
     hashlib.sha256(baseline_provider).hexdigest()!=R20_PROVIDER_SHA256 or
     current_profile!=selected_profile or current_provider!=selected_provider):
  raise SystemExit('R20 S6 baseline/current profile or provider bytes differ')
 profile_sha=hashlib.sha256(selected_profile).hexdigest()
 patch_sha=hashlib.sha256(selected_patch).hexdigest()
 if profile_sha==R20_PROFILE_SHA256:
  if (patch_sha!=R20_PATCH_SHA256 or selected_provider!=baseline_provider or
      baseline_provider.count(R20_PROVIDER_PROVE_SHA256.encode())!=1):
   raise SystemExit('R20 S6 legacy R19 profile/provider/patch tuple differs')
  return False
 if profile_sha!=R20_METADATA_PROFILE_SHA256 or patch_sha!=R20_METADATA_PATCH_SHA256:
  raise SystemExit('R20 S6 selected profile or cumulative patch is unregistered')
 r20_validate_metadata_profile_extension(baseline_profile,selected_profile)
 if (hashlib.sha256(selected_provider).hexdigest()!=R20_METADATA_PROVIDER_SHA256 or
     selected_provider.count(R20_METADATA_PROVIDER_PROVE_SHA256.encode())!=1):
  raise SystemExit('R20 S6 metadata provider/prove pin differs')
 return True


def r20_final_deadline_check(a,ledger):
 checked_at=datetime.datetime.now(datetime.timezone.utc)
 main_deadline=datetime.datetime.fromisoformat(R20_MAIN_DEADLINE.replace('Z','+00:00'))
 cutoff=datetime.datetime.fromisoformat(R20_DEADLINE.replace('Z','+00:00'))
 if ledger.get('main_deadline_utc')!=R20_MAIN_DEADLINE or checked_at>=main_deadline:
  raise SystemExit('R20 A6 main window expired during final source validation')
 if checked_at+datetime.timedelta(seconds=a.timeout+60)>cutoff:
  raise SystemExit('R20 A7 Build plus queue reserve exceeds absolute deadline after validation')


def r20_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R20_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R20 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before=json.loads(subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
  selected=json.loads(subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R20 S4 recipe unavailable')
 r20_validate_recipe_delta(before,selected)
 check_paths={path for path in before['proof_paths']
              if 'BUDGET' in path.rsplit('/',1)[-1].upper()} | {R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R20_PROFILE_PATH}
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R20 S5 baseline/current historical tree unavailable')
 try:
  selected_profile=subprocess.check_output(['git','show',proof_sha+':'+R20_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  baseline_profile=subprocess.check_output(['git','show',probe_sha+':'+R20_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_profile=(ROOT/R20_PROFILE_PATH).read_bytes()
  selected_patch=subprocess.check_output(['git','show',proof_sha+':'+R17_PATCH_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  baseline_provider=subprocess.check_output(['git','show',probe_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  selected_provider=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_provider=(ROOT/R17_PROVIDER_OVERLAYS_PATH).read_bytes()
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R20 S6 pinned profile, patch, or provider unavailable')
 metadata_extension=r20_validate_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                                                baseline_provider,selected_provider,current_provider)
 r20_validate_historical_closure(check_paths,old_map,new_map,metadata_extension)
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R20 S8 accepted R14 publication gate unavailable')
 if gate_current!=gate_selected:raise SystemExit('R20 S9 R14 publication gate bytes changed')
 try:
  baseline_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R20 S10 publisher control unavailable')
 r14_validate_publisher_control(baseline_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r20_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha)
  paths=sorted(set(selected['proof_paths']+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R20 S11 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R20 S12 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R20 S13 incomplete selected source closure')
 try:
  provider_selected=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  pins=r17_parse_provider_pin_tables(provider_selected)
  pinned={**pins['FILES'],**pins['R11_FILES']}
  if R17_PROVIDER_OVERLAYS_PATH not in found or not set(pinned).issubset(found):
   raise SystemExit('R20 S16 provider pins absent from selected source closure')
  for path,expected in pinned.items():
   selected_bytes=subprocess.check_output(['git','show',proof_sha+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
   if hashlib.sha256(selected_bytes).hexdigest()!=expected:
    raise SystemExit('R20 S16 provider pin source mismatch: '+path)
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R20 S16 provider pin source unavailable')
 for path,(mode,kind,oid) in found.items():r17_validate_worktree_entry(path,mode,oid)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r20_authorize(a,ledger):
 expected_ledger=DIR/R20_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
 builds=ledger.get('builds')
 if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
     ledger.get('owner')!='merge' or ledger.get('phase')!=R20_PHASE or ledger.get('phase_id')!=R20_PHASE or
     ledger.get('status')!='AUTHORIZED' or ledger.get('authorization_model')!='bounded-cloud-budget' or
     ledger.get('authorization')!=R20_AUTHORIZATION or ledger.get('schema')!='smallsort-prepared-session-ledger-v1' or
     ledger.get('task_id')!=R20_TASK_ID or type(ledger.get('ceiling_build_seconds')) is not int or ledger.get('ceiling_build_seconds')!=3600 or
     ledger.get('allowed_lanes')!=['merge'] or ledger.get('start_utc')!=R20_START or
     ledger.get('main_deadline_utc')!=R20_MAIN_DEADLINE or ledger.get('deadline_utc')!=R20_DEADLINE or
     ledger.get('baseline_sha')!=R20_BASELINE_SHA or
     'max_builds' not in ledger or ledger.get('max_builds') is not None or
     'maximum_builds' not in ledger or ledger.get('maximum_builds') is not None or
     type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
     type(ledger.get('maximum_build_timeout_seconds')) is not int or ledger.get('maximum_build_timeout_seconds')!=1200 or
     type(ledger.get('report_reserve_seconds')) is not int or ledger.get('report_reserve_seconds')<420 or
     ledger.get('carryover_allowed') is not False or ledger.get('carry_seconds')!=0 or
     ledger.get('publication_gate_path')!=R14_GATE_PATH or ledger.get('profile_path')!=R20_PROFILE_PATH or
     ledger.get('baseline_profile_sha256')!=R20_PROFILE_SHA256 or
     ledger.get('starting_source_sha')!=R20_STARTING_SOURCE_SHA or
     ledger.get('starting_tool_commit')!=R20_STARTING_TOOL_COMMIT or
     type(ledger.get('used_build_seconds')) is not int or type(ledger.get('remaining_build_seconds')) is not int or
     not 0<=ledger.get('used_build_seconds')<=3600 or
     ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
     type(builds) is not list or type(ledger.get('spent_build_seconds')) is not int or
     ledger.get('spent_build_seconds')!=ledger.get('used_build_seconds') or
     type(ledger.get('retired_seconds')) is not int or ledger.get('retired_seconds')!=0 or
     'active_build' not in ledger or
     any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R20_PHASE or
         item.get('status') not in TERMINAL or item.get('accounted') is not True or
         not isinstance(item.get('build_id'),str) or not item.get('build_id') or
         type(item.get('build_seconds')) is not int or item.get('build_seconds')<0
         for item in builds) or
     sum(item['build_seconds'] for item in builds if type(item) is dict and
         type(item.get('build_seconds')) is int and item.get('build_seconds')>=0)!=ledger.get('used_build_seconds') or
     ledger.get('active_build') is not None):
  raise SystemExit('R20 A1 account authorization mismatch')
 now=datetime.datetime.now(datetime.timezone.utc)
 cutoff=datetime.datetime.fromisoformat(R20_DEADLINE.replace('Z','+00:00'))
 if now<datetime.datetime.fromisoformat(R20_START.replace('Z','+00:00')):
  raise SystemExit('R20 A2 window not started')
 if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(R20_MAIN_DEADLINE.replace('Z','+00:00')):
  raise SystemExit('R20 A3 main window expired')
 if a.command=='submit':
  if (type(a.timeout) is not int or not 510<=a.timeout<=1200 or a.lane!='merge' or
      a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
   raise SystemExit('R20 A4 requires one exact pinned source, merge lane, timeout510..1200')
  if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
   raise SystemExit('R20 A5 Build plus queue reserve exceeds absolute deadline')
  r14_read_selected_gate(a.proof_sha)
  r20_validate_sources(R20_PROBE_SOURCE,a.proof_sha)
  r20_final_deadline_check(a,ledger)
 return cutoff


def r21_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R21 S2 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!=R21_ADDED_PATHS or
     set(old_paths)-set(new_paths)!=R21_REMOVED_PATHS):
  raise SystemExit('R21 S3 recipe path closure/registration mismatch')


def r21_validate_historical_closure(paths,before,selected):
 required={R20_LEDGER_PATH,R19_LEDGER_PATH,R18_LEDGER_PATH,R17_LEDGER_PATH,R16_LEDGER_PATH,
           R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R21_PROFILE_PATH}
 if (not required.issubset(paths) or set(before)!=set(paths) or set(selected)!=set(paths) or
     selected!=before or any(value[:2]!=('100644','blob') for value in selected.values())):
  raise SystemExit('R21 S7 historical R20 closure, profile, mode, or gate changed')


def r21_validate_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                                baseline_provider,selected_provider,current_provider):
 if (hashlib.sha256(baseline_profile).hexdigest()!=R21_PROFILE_SHA256 or
     selected_profile!=baseline_profile or current_profile!=selected_profile or
     hashlib.sha256(selected_patch).hexdigest()!=R21_PATCH_SHA256):
  raise SystemExit('R21 S6 pinned profile or cumulative patch differs from reviewed tool578 HANDOFF')
 try:profile=json.loads(selected_profile)
 except (ValueError,UnicodeDecodeError):raise SystemExit('R21 S6 pinned profile JSON unavailable')
 if type(profile) is not dict or profile.get('effective_tool_commit')!=R21_STARTING_TOOL_COMMIT:
  raise SystemExit('R21 S6 pinned profile tool commit differs')
 if (hashlib.sha256(baseline_provider).hexdigest()!=R21_PROVIDER_SHA256 or
     selected_provider!=baseline_provider or current_provider!=selected_provider or
     baseline_provider.count(R21_PROVIDER_PROVE_SHA256.encode())!=1):
  raise SystemExit('R21 S6 provider module differs from exact published tool578 pin')


def r21_final_deadline_check(a,ledger):
 checked_at=datetime.datetime.now(datetime.timezone.utc)
 main_deadline=datetime.datetime.fromisoformat(R21_MAIN_DEADLINE.replace('Z','+00:00'))
 cutoff=datetime.datetime.fromisoformat(R21_DEADLINE.replace('Z','+00:00'))
 if ledger.get('main_deadline_utc')!=R21_MAIN_DEADLINE or checked_at>=main_deadline:
  raise SystemExit('R21 A6 main window expired during final source validation')
 if checked_at+datetime.timedelta(seconds=a.timeout+60)>cutoff:
  raise SystemExit('R21 A7 Build plus queue reserve exceeds absolute deadline after validation')


def r21_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R21_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R21 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before=json.loads(subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
  selected=json.loads(subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R21 S4 recipe unavailable')
 r21_validate_recipe_delta(before,selected)
 check_paths={path for path in before['proof_paths']
              if 'BUDGET' in path.rsplit('/',1)[-1].upper()} | {R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R21_PROFILE_PATH}
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R21 S5 baseline/current historical tree unavailable')
 try:
  selected_profile=subprocess.check_output(['git','show',proof_sha+':'+R21_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  baseline_profile=subprocess.check_output(['git','show',probe_sha+':'+R21_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_profile=(ROOT/R21_PROFILE_PATH).read_bytes()
  selected_patch=subprocess.check_output(['git','show',proof_sha+':'+R17_PATCH_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  baseline_provider=subprocess.check_output(['git','show',probe_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  selected_provider=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_provider=(ROOT/R17_PROVIDER_OVERLAYS_PATH).read_bytes()
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R21 S6 pinned profile, patch, or provider unavailable')
 r21_validate_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                             baseline_provider,selected_provider,current_provider)
 r21_validate_historical_closure(check_paths,old_map,new_map)
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R21 S8 accepted R14 publication gate unavailable')
 if gate_current!=gate_selected:raise SystemExit('R21 S9 R14 publication gate bytes changed')
 try:
  baseline_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R21 S10 publisher control unavailable')
 r14_validate_publisher_control(baseline_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r21_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha)
  paths=sorted(set(selected['proof_paths']+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R21 S11 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R21 S12 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R21 S13 incomplete selected source closure')
 try:
  provider_selected=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  pins=r17_parse_provider_pin_tables(provider_selected)
  pinned={**pins['FILES'],**pins['R11_FILES']}
  if R17_PROVIDER_OVERLAYS_PATH not in found or not set(pinned).issubset(found):
   raise SystemExit('R21 S16 provider pins absent from selected source closure')
  for path,expected in pinned.items():
   selected_bytes=subprocess.check_output(['git','show',proof_sha+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
   if hashlib.sha256(selected_bytes).hexdigest()!=expected:
    raise SystemExit('R21 S16 provider pin source mismatch: '+path)
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R21 S16 provider pin source unavailable')
 for path,(mode,kind,oid) in found.items():r17_validate_worktree_entry(path,mode,oid)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r21_authorize(a,ledger):
 expected_ledger=DIR/R21_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
 builds=ledger.get('builds')
 if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
     ledger.get('owner')!='merge' or ledger.get('phase')!=R21_PHASE or ledger.get('phase_id')!=R21_PHASE or
     ledger.get('status')!='AUTHORIZED' or ledger.get('authorization_model')!='bounded-cloud-budget' or
     ledger.get('authorization')!=R21_AUTHORIZATION or ledger.get('schema')!='smallsort-prepared-session-ledger-v1' or
     ledger.get('task_id')!=R21_TASK_ID or type(ledger.get('ceiling_build_seconds')) is not int or ledger.get('ceiling_build_seconds')!=3600 or
     ledger.get('allowed_lanes')!=['merge'] or ledger.get('start_utc')!=R21_START or
     ledger.get('main_deadline_utc')!=R21_MAIN_DEADLINE or ledger.get('deadline_utc')!=R21_DEADLINE or
     ledger.get('baseline_sha')!=R21_BASELINE_SHA or
     'max_builds' not in ledger or ledger.get('max_builds') is not None or
     'maximum_builds' not in ledger or ledger.get('maximum_builds') is not None or
     type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
     type(ledger.get('maximum_build_timeout_seconds')) is not int or ledger.get('maximum_build_timeout_seconds')!=1200 or
     type(ledger.get('report_reserve_seconds')) is not int or ledger.get('report_reserve_seconds')<420 or
     ledger.get('carryover_allowed') is not False or ledger.get('carry_seconds')!=0 or
     ledger.get('publication_gate_path')!=R14_GATE_PATH or ledger.get('profile_path')!=R21_PROFILE_PATH or
     ledger.get('baseline_profile_sha256')!=R21_PROFILE_SHA256 or
     ledger.get('starting_source_sha')!=R21_STARTING_SOURCE_SHA or
     ledger.get('starting_tool_commit')!=R21_STARTING_TOOL_COMMIT or
     type(ledger.get('used_build_seconds')) is not int or type(ledger.get('remaining_build_seconds')) is not int or
     not 0<=ledger.get('used_build_seconds')<=3600 or
     ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
     type(builds) is not list or type(ledger.get('spent_build_seconds')) is not int or
     ledger.get('spent_build_seconds')!=ledger.get('used_build_seconds') or
     type(ledger.get('retired_seconds')) is not int or ledger.get('retired_seconds')!=0 or
     'active_build' not in ledger or
     any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R21_PHASE or
         item.get('status') not in TERMINAL or item.get('accounted') is not True or
         not isinstance(item.get('build_id'),str) or not item.get('build_id') or
         type(item.get('build_seconds')) is not int or item.get('build_seconds')<0
         for item in builds) or
     sum(item['build_seconds'] for item in builds if type(item) is dict and
         type(item.get('build_seconds')) is int and item.get('build_seconds')>=0)!=ledger.get('used_build_seconds') or
     ledger.get('active_build') is not None):
  raise SystemExit('R21 A1 account authorization mismatch')
 now=datetime.datetime.now(datetime.timezone.utc)
 cutoff=datetime.datetime.fromisoformat(R21_DEADLINE.replace('Z','+00:00'))
 if now<datetime.datetime.fromisoformat(R21_START.replace('Z','+00:00')):
  raise SystemExit('R21 A2 window not started')
 if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(R21_MAIN_DEADLINE.replace('Z','+00:00')):
  raise SystemExit('R21 A3 main window expired')
 if a.command=='submit':
  if (type(a.timeout) is not int or not 510<=a.timeout<=1200 or a.lane!='merge' or
      a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
   raise SystemExit('R21 A4 requires one exact pinned source, merge lane, timeout510..1200')
  if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
   raise SystemExit('R21 A5 Build plus queue reserve exceeds absolute deadline')
  r14_read_selected_gate(a.proof_sha)
  r21_validate_sources(R21_PROBE_SOURCE,a.proof_sha)
  r21_final_deadline_check(a,ledger)
 return cutoff


def r22_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R22 S2 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!=R22_ADDED_PATHS or
     set(old_paths)-set(new_paths)!=R22_REMOVED_PATHS):
  raise SystemExit('R22 S3 recipe path closure/registration mismatch')


def r22_validate_historical_closure(paths,before,selected):
 required={R21_LEDGER_PATH,R20_LEDGER_PATH,R19_LEDGER_PATH,R18_LEDGER_PATH,R17_LEDGER_PATH,R16_LEDGER_PATH,
           R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R22_PROFILE_PATH}
 if (not required.issubset(paths) or set(before)!=set(paths) or set(selected)!=set(paths) or
     any(value[:2]!=('100644','blob') for value in selected.values())):
  raise SystemExit('R22 S7 historical R20 closure, profile, mode, or gate changed')
 differences={path for path in paths if before[path]!=selected[path]}
 if differences not in (set(),{R22_PROFILE_PATH}):
  raise SystemExit('R22 S7 historical closure changed outside the exact R22 profile extension')


def r22_validate_owned_nll_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                                         baseline_provider,selected_provider,current_provider):
 if any(type(value) is not bytes for value in (baseline_profile,selected_profile,current_profile,selected_patch,baseline_provider,selected_provider,current_provider)):
  raise SystemExit('R22 S6 owned-NLL profile/patch/provider pins must be exact byte strings')
 if hashlib.sha256(baseline_profile).hexdigest()!=R22_PROFILE_SHA256:
  raise SystemExit('R22 S6 owned-NLL immutable profile9496 baseline differs')
 try: profile=json.loads(selected_profile)
 except (ValueError,UnicodeDecodeError): raise SystemExit('R22 S6 owned-NLL profile JSON unavailable')
 chain=profile.get('ordered_patch_chain') if type(profile) is dict else None
 if (hashlib.sha256(selected_profile).hexdigest()!=R22_OWNED_NLL_PROFILE_SHA256 or current_profile!=selected_profile or
     profile.get('profile')!='experimental-merge-label-storage-r11-v1' or
     profile.get('r22_owned_nll_registration')!=R22_OWNED_NLL_REGISTRATION or
     profile.get('effective_tool_commit')!=R22_OWNED_NLL_TOOL_COMMIT or
     profile.get('exporter_source_sha256')!=R22_OWNED_NLL_EXPORTER_SHA256 or
     profile.get('schema_sha256')!=R22_OWNED_NLL_SCHEMA_SHA256 or
     profile.get('refiner_core_source_sha256')!=R22_OWNED_NLL_REFINER_CORE_SHA256 or
     profile.get('translator_sha256')!=R22_OWNED_NLL_TRANSLATOR_SHA256 or
     profile.get('guard_return_trace_patch_sha256')!=R22_OWNED_NLL_PATCH_SHA256 or
     type(chain) is not list or len(chain)!=19 or type(chain[-1]) is not dict or
     chain[-1].get('sha256')!=R22_OWNED_NLL_PATCH_SHA256 or
     hashlib.sha256(selected_patch).hexdigest()!=R22_OWNED_NLL_PATCH_SHA256):
  raise SystemExit('R22 S6 owned-NLL candidate is not the exact registered tool/source/patch profile')
 reversed_profile=dict(profile); reversed_profile.pop('r22_owned_nll_registration',None)
 reversed_profile['effective_tool_commit']=R22_COMPILE_FIX_TOOL_COMMIT
 reversed_profile['exporter_source_sha256']=R22_COMPILE_FIX_EXPORTER_SHA256
 reversed_profile['schema_sha256']=R20_METADATA_SCHEMA_SHA256
 reversed_profile['refiner_core_source_sha256']=R20_METADATA_REFINER_CORE_SHA256
 reversed_profile['translator_sha256']=R22_COMPILE_FIX_TRANSLATOR_SHA256
 reversed_profile['guard_return_trace_patch_sha256']=R22_COMPILE_FIX_PATCH_SHA256
 reversed_profile['ordered_patch_chain']=list(chain)
 reversed_profile['ordered_patch_chain'][-1]={'path':'research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch','sha256':R22_COMPILE_FIX_PATCH_SHA256}
 reversed_bytes=(json.dumps(reversed_profile,indent=2,ensure_ascii=False)+'\n').encode()
 if hashlib.sha256(reversed_bytes).hexdigest()!=R22_COMPILE_FIX_PROFILE_SHA256:
  raise SystemExit('R22 S6 owned-NLL profile does not reverse exactly to compile profile65f')
 if (hashlib.sha256(baseline_provider).hexdigest()!=R22_PROVIDER_SHA256 or
     hashlib.sha256(selected_provider).hexdigest()!=R22_OWNED_NLL_PROVIDER_SHA256 or
     current_provider!=selected_provider):
  raise SystemExit('R22 S6 owned-NLL provider module differs')
 tables=r22_parse_provider_pin_tables(selected_provider)
 prove_path='research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py'
 if tables['R22_OWNED_NLL_FILES'].get(prove_path)!=R22_OWNED_NLL_PROVIDER_PROVE_SHA256:
  raise SystemExit('R22 S6 owned-NLL prove.py source pin differs')
 return 'r22-owned-nll-diagnostic'


def r22_validate_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                                baseline_provider,selected_provider,current_provider):
 if any(type(value) is not bytes for value in
        (baseline_profile,selected_profile,current_profile,selected_patch,
         baseline_provider,selected_provider,current_provider)):
  raise SystemExit('R22 S6 profile/patch/provider pins must be exact byte strings')
 if hashlib.sha256(baseline_profile).hexdigest()!=R22_PROFILE_SHA256:
  raise SystemExit('R22 S6 immutable profile9496 baseline differs')
 try: selected_card=json.loads(selected_profile)
 except (ValueError,UnicodeDecodeError): raise SystemExit('R22 S6 pinned profile JSON unavailable')
 if isinstance(selected_card,dict) and 'r22_owned_nll_registration' in selected_card:
  return r22_validate_owned_nll_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                                               baseline_provider,selected_provider,current_provider)
 if selected_profile==baseline_profile:
  # Historical R22 admission remains available with the exact original tuple.
  try:profile=json.loads(selected_profile)
  except (ValueError,UnicodeDecodeError):raise SystemExit('R22 S6 pinned profile JSON unavailable')
  if (current_profile!=selected_profile or
      hashlib.sha256(selected_patch).hexdigest()!=R22_PATCH_SHA256 or
      type(profile) is not dict or profile.get('effective_tool_commit')!=R22_STARTING_TOOL_COMMIT):
   raise SystemExit('R22 S6 original tool578/profile9496 tuple differs')
  if (hashlib.sha256(baseline_provider).hexdigest()!=R22_PROVIDER_SHA256 or
      selected_provider!=baseline_provider or current_provider!=selected_provider or
      baseline_provider.count(R22_PROVIDER_PROVE_SHA256.encode())!=1):
   raise SystemExit('R22 S6 original provider module differs from exact tool578 pin')
  return 'tool578-profile9496'

 # The sole alternative is the narrow compile-fix profile.  Reversing its
 # four extension fields must recreate the immutable profile9496 bytes.
 try:profile=json.loads(selected_profile)
 except (ValueError,UnicodeDecodeError):raise SystemExit('R22 S6 compile-fix profile JSON unavailable')
 if (hashlib.sha256(selected_profile).hexdigest()!=R22_COMPILE_FIX_PROFILE_SHA256 or
     current_profile!=selected_profile or type(profile) is not dict or
     profile.get('profile')!='experimental-merge-label-storage-r11-v1' or
     type(profile.get('r22_compile_fix_registration')) is not dict or
     profile['r22_compile_fix_registration']!={
       'schema':'merge-r22-compile-fix-registration-v1',
       'phase_id':R22_PHASE,
       'baseline_profile_sha256':R22_PROFILE_SHA256,
       'starting_tool_commit':R22_STARTING_TOOL_COMMIT,
       'candidate_tool_commit':R22_COMPILE_FIX_TOOL_COMMIT,
       'tool_source_paths':['src/rust_frontend/vf_mir_exporter/src/lib.rs','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'],
       'source_applicability':('compile-only Rust fixes: reborrow the erased-region Cap’n Proto builder before initializing identity; import the generated pointer-coercion data module; initialize identity=Nothing on three synthetic Lifetime records. No emitted MIR, schema, refinement, proof, runtime, CFG, postcondition, or control change.')} or
     profile.get('effective_tool_commit')!=R22_COMPILE_FIX_TOOL_COMMIT or
     profile.get('exporter_source_sha256')!=R22_COMPILE_FIX_EXPORTER_SHA256 or
     profile.get('translator_sha256')!=R22_COMPILE_FIX_TRANSLATOR_SHA256 or
     profile.get('guard_return_trace_patch_sha256')!=R22_COMPILE_FIX_PATCH_SHA256):
  raise SystemExit('R22 S6 candidate is not the exact reversible compile-fix profile extension')
 reversed_profile=dict(profile)
 reversed_profile.pop('r22_compile_fix_registration',None)
 reversed_profile['profile']='experimental-merge-label-storage-r11-v1'
 reversed_profile['effective_tool_commit']=R22_STARTING_TOOL_COMMIT
 reversed_profile['exporter_source_sha256']=R20_METADATA_EXPORTER_SHA256
 reversed_profile['translator_sha256']='1cb46fbbf1aed7654766c820a33ef3651139efa877e1ef3b13a25b02d9897c8b'
 reversed_profile['guard_return_trace_patch_sha256']=R22_PATCH_SHA256
 reversed_profile['ordered_patch_chain']=list(reversed_profile.get('ordered_patch_chain',[]))
 if reversed_profile['ordered_patch_chain']:
  reversed_profile['ordered_patch_chain'][-1]={'path':'research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch','sha256':R22_PATCH_SHA256}
 reversed_bytes=(json.dumps(reversed_profile,indent=2,ensure_ascii=False)+'\n').encode()
 if reversed_bytes!=baseline_profile:
  raise SystemExit('R22 S6 compile-fix profile does not reverse byte-exactly to profile9496')
 chain=profile.get('ordered_patch_chain')
 if (type(chain) is not list or len(chain)!=19 or type(chain[-1]) is not dict or
     chain[-1].get('path')!='research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch' or
     chain[-1].get('sha256')!=R22_COMPILE_FIX_PATCH_SHA256 or
     hashlib.sha256(selected_patch).hexdigest()!=R22_COMPILE_FIX_PATCH_SHA256):
  raise SystemExit('R22 S6 candidate cumulative patch pin differs')
 if (hashlib.sha256(baseline_provider).hexdigest()!=R22_PROVIDER_SHA256 or
     hashlib.sha256(selected_provider).hexdigest()!=R22_COMPILE_FIX_PROVIDER_SHA256 or
     current_provider!=selected_provider or
     selected_provider.count(R22_COMPILE_FIX_PROVIDER_PROVE_SHA256.encode())<1):
  raise SystemExit('R22 S6 compile-fix provider module or prove.py pin differs')
 tables=r22_parse_provider_pin_tables(selected_provider)
 if tables['R22_FILES'].get('research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py')!=R22_COMPILE_FIX_PROVIDER_PROVE_SHA256:
  raise SystemExit('R22 S6 compile-fix prove.py source pin differs')
 return 'r22-compile-fix'


def r22_final_deadline_check(a,ledger):
 checked_at=datetime.datetime.now(datetime.timezone.utc)
 main_deadline=datetime.datetime.fromisoformat(R22_MAIN_DEADLINE.replace('Z','+00:00'))
 cutoff=datetime.datetime.fromisoformat(R22_DEADLINE.replace('Z','+00:00'))
 if ledger.get('main_deadline_utc')!=R22_MAIN_DEADLINE or checked_at>=main_deadline:
  raise SystemExit('R22 A6 main window expired during final source validation')
 if checked_at+datetime.timedelta(seconds=a.timeout+60)>main_deadline:
  raise SystemExit('R22 A7 Build plus queue reserve exceeds main deadline after validation')


def r22_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R22_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R22 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before=json.loads(subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
  selected=json.loads(subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R22 S4 recipe unavailable')
 r22_validate_recipe_delta(before,selected)
 check_paths={path for path in before['proof_paths']
              if 'BUDGET' in path.rsplit('/',1)[-1].upper()} | {R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R22_PROFILE_PATH}
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R22 S5 baseline/current historical tree unavailable')
 try:
  selected_profile=subprocess.check_output(['git','show',proof_sha+':'+R22_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  baseline_profile=subprocess.check_output(['git','show',probe_sha+':'+R22_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_profile=(ROOT/R22_PROFILE_PATH).read_bytes()
  selected_patch=subprocess.check_output(['git','show',proof_sha+':'+R17_PATCH_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  baseline_provider=subprocess.check_output(['git','show',probe_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  selected_provider=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_provider=(ROOT/R17_PROVIDER_OVERLAYS_PATH).read_bytes()
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R22 S6 pinned profile, patch, or provider unavailable')
 admission=r22_validate_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                                      baseline_provider,selected_provider,current_provider)
 r22_validate_historical_closure(check_paths,old_map,new_map)
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R22 S8 accepted R14 publication gate unavailable')
 if gate_current!=gate_selected:raise SystemExit('R22 S9 R14 publication gate bytes changed')
 try:
  baseline_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R22 S10 publisher control unavailable')
 r14_validate_publisher_control(baseline_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r22_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha)
  paths=sorted(set(selected['proof_paths']+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R22 S11 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R22 S12 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R22 S13 incomplete selected source closure')
 try:
  provider_selected=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  if selected_profile==baseline_profile:
   pins=r17_parse_provider_pin_tables(provider_selected)
   pinned={**pins['FILES'],**pins['R11_FILES']}
  else:
   pins=r22_parse_provider_pin_tables(provider_selected)
   extension=pins['R22_OWNED_NLL_FILES'] if admission=='r22-owned-nll-diagnostic' else pins['R22_FILES']
   pinned={**pins['FILES'],**extension}
  if R17_PROVIDER_OVERLAYS_PATH not in found or not set(pinned).issubset(found):
   raise SystemExit('R22 S16 provider pins absent from selected source closure')
  for path,expected in pinned.items():
   selected_bytes=subprocess.check_output(['git','show',proof_sha+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
   if hashlib.sha256(selected_bytes).hexdigest()!=expected:
    raise SystemExit('R22 S16 provider pin source mismatch: '+path)
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R22 S16 provider pin source unavailable')
 for path,(mode,kind,oid) in found.items():r17_validate_worktree_entry(path,mode,oid)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r22_authorize(a,ledger):
 expected_ledger=DIR/R22_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
 builds=ledger.get('builds')
 if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
     ledger.get('owner')!='merge' or ledger.get('phase')!=R22_PHASE or ledger.get('phase_id')!=R22_PHASE or
     ledger.get('status')!='AUTHORIZED' or ledger.get('authorization_model')!='bounded-cloud-budget' or
     ledger.get('authorization')!=R22_AUTHORIZATION or ledger.get('schema')!='smallsort-prepared-session-ledger-v1' or
     ledger.get('task_id')!=R22_TASK_ID or type(ledger.get('ceiling_build_seconds')) is not int or ledger.get('ceiling_build_seconds')!=3600 or
     ledger.get('allowed_lanes')!=['merge'] or ledger.get('start_utc')!=R22_START or
     ledger.get('main_deadline_utc')!=R22_MAIN_DEADLINE or ledger.get('deadline_utc')!=R22_DEADLINE or
     ledger.get('baseline_sha')!=R22_BASELINE_SHA or
     'max_builds' not in ledger or ledger.get('max_builds') is not None or
     'maximum_builds' not in ledger or ledger.get('maximum_builds') is not None or
     type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
     type(ledger.get('maximum_build_timeout_seconds')) is not int or ledger.get('maximum_build_timeout_seconds')!=1200 or
     type(ledger.get('report_reserve_seconds')) is not int or ledger.get('report_reserve_seconds')<420 or
     ledger.get('carryover_allowed') is not False or ledger.get('carry_seconds')!=0 or
     ledger.get('publication_gate_path')!=R14_GATE_PATH or ledger.get('profile_path')!=R22_PROFILE_PATH or
     ledger.get('baseline_profile_sha256')!=R22_PROFILE_SHA256 or
     ledger.get('starting_source_sha')!=R22_STARTING_SOURCE_SHA or
     ledger.get('starting_tool_commit')!=R22_STARTING_TOOL_COMMIT or
     type(ledger.get('used_build_seconds')) is not int or type(ledger.get('remaining_build_seconds')) is not int or
     not 0<=ledger.get('used_build_seconds')<=3600 or
     ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
     type(builds) is not list or type(ledger.get('spent_build_seconds')) is not int or
     ledger.get('spent_build_seconds')!=ledger.get('used_build_seconds') or
     type(ledger.get('retired_seconds')) is not int or ledger.get('retired_seconds')!=0 or
     'active_build' not in ledger or
     any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R22_PHASE or
         item.get('status') not in TERMINAL or item.get('accounted') is not True or
         not isinstance(item.get('build_id'),str) or not item.get('build_id') or
         type(item.get('build_seconds')) is not int or item.get('build_seconds')<0
         for item in builds) or
     sum(item['build_seconds'] for item in builds if type(item) is dict and
         type(item.get('build_seconds')) is int and item.get('build_seconds')>=0)!=ledger.get('used_build_seconds') or
     ledger.get('active_build') is not None):
  raise SystemExit('R22 A1 account authorization mismatch')
 now=datetime.datetime.now(datetime.timezone.utc)
 cutoff=datetime.datetime.fromisoformat(R22_DEADLINE.replace('Z','+00:00'))
 if now<datetime.datetime.fromisoformat(R22_START.replace('Z','+00:00')):
  raise SystemExit('R22 A2 window not started')
 if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(R22_MAIN_DEADLINE.replace('Z','+00:00')):
  raise SystemExit('R22 A3 main window expired')
 if a.command=='submit':
  if (type(a.timeout) is not int or not 510<=a.timeout<=1200 or a.lane!='merge' or
      a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
   raise SystemExit('R22 A4 requires one exact pinned source, merge lane, timeout510..1200')
  if now+datetime.timedelta(seconds=a.timeout+60)>datetime.datetime.fromisoformat(R22_MAIN_DEADLINE.replace('Z','+00:00')):
   raise SystemExit('R22 A5 Build plus queue reserve exceeds main deadline')
  r14_read_selected_gate(a.proof_sha)
  r22_validate_sources(R22_PROBE_SOURCE,a.proof_sha)
  r22_final_deadline_check(a,ledger)
 return cutoff


def r23_validate_recipe_delta(before,selected):
 if (not isinstance(before,dict) or not isinstance(selected,dict) or
     {key:value for key,value in before.items() if key!='proof_paths'} !=
     {key:value for key,value in selected.items() if key!='proof_paths'}):
  raise SystemExit('R23 S2 recipe metadata changed')
 old_paths=before.get('proof_paths');new_paths=selected.get('proof_paths')
 if (not isinstance(old_paths,list) or not isinstance(new_paths,list) or
     old_paths!=sorted(set(old_paths)) or new_paths!=sorted(set(new_paths)) or
     set(new_paths)-set(old_paths)!=R23_ADDED_PATHS or
     set(old_paths)-set(new_paths)!=R23_REMOVED_PATHS):
  raise SystemExit('R23 S3 recipe path closure/registration mismatch')


def r23_validate_historical_closure(paths,before,selected,*,profile_extension=False):
 required={R22_LEDGER_PATH,R21_LEDGER_PATH,R20_LEDGER_PATH,R19_LEDGER_PATH,R18_LEDGER_PATH,R17_LEDGER_PATH,R16_LEDGER_PATH,
           R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R23_PROFILE_PATH}
 if (not required.issubset(paths) or set(before)!=set(paths) or set(selected)!=set(paths) or
     any(value[:2]!=('100644','blob') for value in selected.values())):
  raise SystemExit('R23 S7 historical R20 closure, profile, mode, or gate changed')
 differences={path for path in paths if before[path]!=selected[path]}
 if differences-({R23_PROFILE_PATH} if profile_extension is True else set()):
  raise SystemExit('R23 S7 historical closure changed outside the exact R23 profile extension')


def r23_final_deadline_check(a,ledger):
 checked_at=datetime.datetime.now(datetime.timezone.utc)
 main_deadline=datetime.datetime.fromisoformat(R23_MAIN_DEADLINE.replace('Z','+00:00'))
 cutoff=datetime.datetime.fromisoformat(R23_DEADLINE.replace('Z','+00:00'))
 if ledger.get('main_deadline_utc')!=R23_MAIN_DEADLINE or checked_at>=main_deadline:
  raise SystemExit('R23 A6 main window expired during final source validation')
 if checked_at+datetime.timedelta(seconds=a.timeout+60)>main_deadline:
  raise SystemExit('R23 A7 Build plus queue reserve exceeds main deadline after validation')


def r23_parse_provider_pin_tables(source):
 try:
  if not isinstance(source,bytes):raise ValueError('not bytes')
  module=ast.parse(source.decode('utf-8'))
  tables={}
  for node in module.body:
   if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('FILES','R11_FILES','R22_FILES','R22_OWNED_NLL_FILES'):
    name=node.targets[0].id
    if name in tables or not isinstance(node.value,ast.Dict):raise ValueError('duplicate or non-dict table')
    keys=[];values=[]
    for key,value in zip(node.value.keys,node.value.values):
     if (not isinstance(key,ast.Constant) or type(key.value) is not str or
         not isinstance(value,ast.Constant) or type(value.value) is not str):
      raise ValueError('nonliteral path or digest')
     keys.append(key.value);values.append(value.value)
    if len(keys)!=len(set(keys)):raise ValueError('duplicate path')
    table=ast.literal_eval(node.value)
    if type(table) is not dict or len(table)!=len(keys):raise ValueError('invalid table')
    if any(not re.fullmatch('[0-9a-f]{64}',digest) for digest in values):raise ValueError('invalid digest')
    tables[name]=table
  if set(tables)!= {'FILES','R11_FILES','R22_FILES','R22_OWNED_NLL_FILES'} or len(tables['FILES'])!=18 or len(tables['R11_FILES']) not in (2,3) or len(tables['R22_FILES'])!=len(tables['R11_FILES']) or len(tables['R22_OWNED_NLL_FILES'])!=len(tables['R11_FILES']):
   raise ValueError('wrong table schema/count')
  if set(tables['FILES']) & (set(tables['R11_FILES'])|set(tables['R22_FILES'])|set(tables['R22_OWNED_NLL_FILES'])):
   raise ValueError('provider tables overlap common sources')
  proof_path='research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py'
  if set(tables['R11_FILES'])!=set(tables['R22_FILES']) or set(tables['R11_FILES'])!=set(tables['R22_OWNED_NLL_FILES']) or proof_path not in tables['R22_FILES']:
   raise ValueError('R22 provider path set differs from R11')
  if any(tables['R11_FILES'][path]!=tables['R22_FILES'][path] or tables['R11_FILES'][path]!=tables['R22_OWNED_NLL_FILES'][path]
         for path in set(tables['R11_FILES'])-{proof_path,R23_PLACEMENT_PATH,R23_COMPAT_PATH}):
   raise ValueError('R22 control pins differ from R11')
  if (tables['R11_FILES'][proof_path] in (tables['R22_FILES'][proof_path],tables['R22_OWNED_NLL_FILES'][proof_path]) or
      tables['R22_FILES']!=tables['R22_OWNED_NLL_FILES']):
   raise ValueError('R22 profile pin tables are not exact and distinct from historical R11')
  if (tables['R22_FILES'].get(proof_path)!=R23_PROVE_SHA256 or
      tables['R22_FILES'].get(R23_PLACEMENT_PATH)!=R23_PLACEMENT_SHA256 or
      tables['R22_FILES'].get(R23_COMPAT_PATH)!=R23_COMPAT_SHA256):
   raise ValueError('R23 exact runner source pins differ')
  return tables
 except (SyntaxError,UnicodeDecodeError,ValueError,TypeError,RecursionError):
  raise SystemExit('R23 S16 malformed provider pin tables')


def r23_validate_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                                baseline_provider,selected_provider,current_provider):
 if any(type(value) is not bytes for value in
        (baseline_profile,selected_profile,current_profile,selected_patch,
         baseline_provider,selected_provider,current_provider)):
  raise SystemExit('R23 S6 exact byte-string pins required')
 if (hashlib.sha256(baseline_profile).hexdigest()!=R23_PROFILE_SHA256 or
     current_profile!=selected_profile or
     hashlib.sha256(selected_profile).hexdigest() not in (R23_PROFILE_SHA256,R23_SOURCE_PROFILE_SHA256) or
     hashlib.sha256(selected_patch).hexdigest()!=(R23_PATCH_SHA256 if selected_profile==baseline_profile else R23_SOURCE_PATCH_SHA256) or
     hashlib.sha256(baseline_provider).hexdigest()!=R22_OWNED_NLL_PROVIDER_SHA256 or
     hashlib.sha256(selected_provider).hexdigest()!=R23_PROVIDER_SHA256 or
     current_provider!=selected_provider):
  raise SystemExit('R23 S6 exact diagnostic profile/patch/provider tuple differs')
 if selected_profile!=baseline_profile:
  try:
   registry_path=ROOT/R23_SOURCE_REGISTRY_PATH
   if hashlib.sha256(registry_path.read_bytes()).hexdigest()!=R23_SOURCE_REGISTRY_SHA256:
    raise ValueError('registry source differs')
   spec=importlib.util.spec_from_file_location('r23_source_registry_client',registry_path)
   registry=importlib.util.module_from_spec(spec);spec.loader.exec_module(registry)
   reversed_profile=registry.reverse_profile(json.loads(selected_profile))
   if registry.serialize(reversed_profile)!=baseline_profile:raise ValueError('reverse differs')
  except (OSError,ValueError,TypeError,AttributeError):
   raise SystemExit('R23 S6 checked source profile does not reverse exactly to diagnostic baseline')


def r23_validate_sources(probe_sha,proof_sha):
 if probe_sha!=R23_PROBE_SOURCE or not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R23 S1 source identity')
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 try:
  before=json.loads(subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
  selected=json.loads(subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE))
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R23 S4 recipe unavailable')
 r23_validate_recipe_delta(before,selected)
 check_paths={path for path in before['proof_paths']
              if 'BUDGET' in path.rsplit('/',1)[-1].upper()} | {R13_MODE_PATH,R14_GATE_PATH,R17_PROFILE_PATH,R23_PROFILE_PATH}
 def tree_map(commit,paths):
  raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',*sorted(paths)],cwd=ROOT,stderr=subprocess.PIPE)
  found={}
  for record in raw.split(b'\0'):
   if record:
    meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
    found[path.decode()]=(mode,kind,oid)
  return found
 try:
  old_map=tree_map(probe_sha,check_paths);new_map=tree_map(proof_sha,check_paths)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R23 S5 baseline/current historical tree unavailable')
 try:
  selected_profile=subprocess.check_output(['git','show',proof_sha+':'+R23_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  baseline_profile=subprocess.check_output(['git','show',probe_sha+':'+R23_PROFILE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_profile=(ROOT/R23_PROFILE_PATH).read_bytes()
  selected_patch=subprocess.check_output(['git','show',proof_sha+':'+R17_PATCH_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  baseline_provider=subprocess.check_output(['git','show',probe_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  selected_provider=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_provider=(ROOT/R17_PROVIDER_OVERLAYS_PATH).read_bytes()
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R23 S6 pinned profile, patch, or provider unavailable')
 r23_validate_candidate_pins(baseline_profile,selected_profile,current_profile,selected_patch,
                             baseline_provider,selected_provider,current_provider)
 try:
  registry_selected=subprocess.check_output(['git','show',proof_sha+':'+R23_SOURCE_REGISTRY_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  if (hashlib.sha256(registry_selected).hexdigest()!=R23_SOURCE_REGISTRY_SHA256 or
      (ROOT/R23_SOURCE_REGISTRY_PATH).read_bytes()!=registry_selected):
   raise SystemExit('R23 S6 exact source registry differs')
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R23 S6 source registry unavailable')
 try:
  capture_policy=subprocess.check_output(['git','show',proof_sha+':'+R23_CAPTURE_POLICY_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  current_capture_policy=(ROOT/R23_CAPTURE_POLICY_PATH).read_bytes()
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R23 S6 post-stop-loss capture policy unavailable')
 if (hashlib.sha256(capture_policy).hexdigest()!=R23_CAPTURE_POLICY_SHA256 or
     current_capture_policy!=capture_policy):
  raise SystemExit('R23 S6 exact capture-off policy differs')
 r23_validate_historical_closure(check_paths,old_map,new_map,profile_extension=selected_profile!=baseline_profile)
 try:
  gate_selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  gate_current=(ROOT/R14_GATE_PATH).read_bytes()
  r14_validate_gate_record(json.loads(gate_selected))
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R23 S8 accepted R14 publication gate unavailable')
 if gate_current!=gate_selected:raise SystemExit('R23 S9 R14 publication gate bytes changed')
 try:
  baseline_control=subprocess.check_output(['git','show',R14_PROBE_SOURCE+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
  selected_control=subprocess.check_output(['git','show',proof_sha+':research/challenge-8/cloud-build/control.py'],cwd=ROOT,stderr=subprocess.PIPE).decode()
 except (subprocess.CalledProcessError,UnicodeDecodeError):
  raise SystemExit('R23 S10 publisher control unavailable')
 if (ROOT/'research/challenge-8/cloud-build/control.py').read_text()!=selected_control:
  raise SystemExit('R23 S10 current client differs from selected committed control')
 r14_validate_publisher_control(baseline_control,selected_control)
 source_spec=importlib.util.spec_from_file_location('r23_pinned_source',DIR/'source-input.py')
 source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
 try:
  infra_paths=source.infra_paths(ROOT,proof_sha,lane="merge")
  paths=sorted(set(selected['proof_paths']+selected['infra_paths']+infra_paths+[recipe_path]))
  raw=subprocess.check_output(['git','ls-tree','-r','-z',proof_sha,'--',*paths],cwd=ROOT,stderr=subprocess.PIPE)
 except (subprocess.CalledProcessError,KeyError,TypeError,ValueError,UnicodeDecodeError,SystemExit):
  raise SystemExit('R23 S11 selected source closure unavailable')
 found={}
 for record in raw.split(b'\0'):
  if not record:continue
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if mode not in ('100644','100755') or kind!='blob':raise SystemExit('R23 S12 nonregular source input')
  found[path.decode()]=(mode,kind,oid)
 if set(found)!=set(paths):raise SystemExit('R23 S13 incomplete selected source closure')
 try:
  provider_selected=subprocess.check_output(['git','show',proof_sha+':'+R17_PROVIDER_OVERLAYS_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  pins=r23_parse_provider_pin_tables(provider_selected)
  pinned={**pins['FILES'],**pins['R22_OWNED_NLL_FILES']}
  if R17_PROVIDER_OVERLAYS_PATH not in found or not set(pinned).issubset(found):
   raise SystemExit('R23 S16 provider pins absent from selected source closure')
  for path,expected in pinned.items():
   selected_bytes=subprocess.check_output(['git','show',proof_sha+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
   if hashlib.sha256(selected_bytes).hexdigest()!=expected:
    raise SystemExit('R23 S16 provider pin source mismatch: '+path)
 except (subprocess.CalledProcessError,OSError):
  raise SystemExit('R23 S16 provider pin source unavailable')
 for path,(mode,kind,oid) in found.items():r17_validate_worktree_entry(path,mode,oid)
 payload=source.make_payload(ROOT,proof_sha,proof_sha,'merge')
 r15_validate_transport_size(len(payload))


def r23_authorize(a,ledger):
 expected_ledger=DIR/R23_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
 builds=ledger.get('builds')
 if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
     ledger.get('owner')!='merge' or ledger.get('phase')!=R23_PHASE or ledger.get('phase_id')!=R23_PHASE or
     ledger.get('status')!='AUTHORIZED' or ledger.get('authorization_model')!='bounded-cloud-budget' or
     ledger.get('authorization')!=R23_AUTHORIZATION or ledger.get('schema')!='smallsort-prepared-session-ledger-v1' or
     ledger.get('task_id')!=R23_TASK_ID or type(ledger.get('ceiling_build_seconds')) is not int or ledger.get('ceiling_build_seconds')!=14400 or
     ledger.get('allowed_lanes')!=['merge'] or ledger.get('start_utc')!=R23_START or
     ledger.get('main_deadline_utc')!=R23_MAIN_DEADLINE or ledger.get('deadline_utc')!=R23_DEADLINE or
     ledger.get('baseline_sha')!=R23_BASELINE_SHA or
     'max_builds' not in ledger or ledger.get('max_builds') is not None or
     'maximum_builds' not in ledger or ledger.get('maximum_builds') is not None or
     type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
     type(ledger.get('maximum_build_timeout_seconds')) is not int or ledger.get('maximum_build_timeout_seconds')!=1200 or
     type(ledger.get('report_reserve_seconds')) is not int or ledger.get('report_reserve_seconds')<420 or
     ledger.get('carryover_allowed') is not False or ledger.get('carry_seconds')!=0 or
     ledger.get('publication_gate_path')!=R14_GATE_PATH or ledger.get('profile_path')!=R23_PROFILE_PATH or
     ledger.get('baseline_profile_sha256')!=R23_PROFILE_SHA256 or
     ledger.get('starting_source_sha')!=R23_STARTING_SOURCE_SHA or
     ledger.get('starting_tool_commit')!=R23_STARTING_TOOL_COMMIT or
     type(ledger.get('used_build_seconds')) is not int or type(ledger.get('remaining_build_seconds')) is not int or
     not 0<=ledger.get('used_build_seconds')<=14400 or
     ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=14400 or
     type(builds) is not list or type(ledger.get('spent_build_seconds')) is not int or
     ledger.get('spent_build_seconds')!=ledger.get('used_build_seconds') or
     type(ledger.get('retired_seconds')) is not int or ledger.get('retired_seconds')!=0 or
     'active_build' not in ledger or
     any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R23_PHASE or
         item.get('status') not in TERMINAL or item.get('accounted') is not True or
         not isinstance(item.get('build_id'),str) or not item.get('build_id') or
         type(item.get('build_seconds')) is not int or item.get('build_seconds')<0
         for item in builds) or
     sum(item['build_seconds'] for item in builds if type(item) is dict and
         type(item.get('build_seconds')) is int and item.get('build_seconds')>=0)!=ledger.get('used_build_seconds') or
     ledger.get('active_build') is not None):
  raise SystemExit('R23 A1 account authorization mismatch')
 now=datetime.datetime.now(datetime.timezone.utc)
 cutoff=datetime.datetime.fromisoformat(R23_DEADLINE.replace('Z','+00:00'))
 if now<datetime.datetime.fromisoformat(R23_START.replace('Z','+00:00')):
  raise SystemExit('R23 A2 window not started')
 if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(R23_MAIN_DEADLINE.replace('Z','+00:00')):
  raise SystemExit('R23 A3 main window expired')
 if a.command=='submit':
  if (type(a.timeout) is not int or a.timeout!=1200 or a.lane!='merge' or
      a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
   raise SystemExit('R23 A4 requires one exact pinned source, merge lane, timeout1200')
  if now+datetime.timedelta(seconds=a.timeout+60)>datetime.datetime.fromisoformat(R23_MAIN_DEADLINE.replace('Z','+00:00')):
   raise SystemExit('R23 A5 Build plus queue reserve exceeds main deadline')
  r14_read_selected_gate(a.proof_sha)
  r23_validate_sources(R23_PROBE_SOURCE,a.proof_sha)
  r23_final_deadline_check(a,ledger)
 return cutoff


def authorized_phase(a,ledger):
 if not a.phase_id or not PHASE_PATTERN.fullmatch(a.phase_id) or ledger.get('phase')!=a.phase_id:raise SystemExit('Explicit phase ID must match the selected account')
 if a.phase_id=='CLOUD-BUILD-MIGRATION' or ledger.get('status')!='AUTHORIZED' or not isinstance(ledger.get('authorization'),str) or not ledger['authorization'].strip():raise SystemExit('Phase account is closed or has no explicit authorization')
 if not a.owner or not OWNER_PATTERN.fullmatch(a.owner):raise SystemExit('Explicit valid --owner is required')
 if not isinstance(ledger.get('ceiling_build_seconds'),int) or ledger['ceiling_build_seconds']<=0:raise SystemExit('Invalid phase ceiling')
 if a.phase_id==NIGHT_PHASE and ledger['ceiling_build_seconds']!=10800:raise SystemExit('Select phase requires its separate 10800-second ceiling')
 if not isinstance(ledger.get('allowed_lanes'),list):raise SystemExit('Phase account needs an explicit lane allowlist')
 try:deadline=datetime.datetime.fromisoformat(ledger['deadline_utc'].replace('Z','+00:00'))
 except (KeyError,AttributeError,ValueError) as error:raise SystemExit('Invalid phase deadline') from error
 cutoff=datetime.datetime.fromisoformat(NIGHT_DEADLINE.replace('Z','+00:00'))
 if a.phase_id==R18_PHASE:
  cutoff=r18_authorize(a,ledger)
 if a.phase_id==R19_PHASE:
  cutoff=r19_authorize(a,ledger)
 if a.phase_id==R20_PHASE:
  cutoff=r20_authorize(a,ledger)
 if a.phase_id==R21_PHASE:
  cutoff=r21_authorize(a,ledger)
 if a.phase_id==R22_PHASE:
  cutoff=r22_authorize(a,ledger)
 if a.phase_id==R23_PHASE:
  cutoff=r23_authorize(a,ledger)
 if a.phase_id==R17_PHASE:
  expected_ledger=DIR/R17_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
  expected_start='2026-10-21T18:33:50Z'
  expected_main='2026-10-21T20:33:50Z'
  expected_cutoff='2026-10-21T21:03:50Z'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('authorization')!=R17_AUTHORIZATION or ledger.get('ceiling_build_seconds')!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or ledger.get('start_utc')!=expected_start or
      ledger.get('main_deadline_utc')!=expected_main or ledger.get('deadline_utc')!=expected_cutoff or
      ledger.get('baseline_sha')!='137cbf8ed13653c83a56975449c544ed7b348365' or
      'max_builds' not in ledger or ledger.get('max_builds') is not None or
      type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
      type(ledger.get('report_reserve_seconds')) is not int or ledger.get('report_reserve_seconds')<420 or
      ledger.get('carryover_allowed') is not False or ledger.get('carry_seconds')!=0 or
      ledger.get('publication_gate_path')!=R14_GATE_PATH or ledger.get('profile_path')!=R17_PROFILE_PATH or
      ledger.get('baseline_profile_sha256')!='eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375' or
      ledger.get('starting_source_sha')!=R17_STARTING_SOURCE_SHA or
      ledger.get('starting_tool_commit')!='660b576b6b1608db913c51e0785b443a8733396f' or
      type(ledger.get('used_build_seconds')) is not int or
      type(ledger.get('remaining_build_seconds')) is not int or
      not 0<=ledger.get('used_build_seconds')<=3600 or
      ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
      type(ledger.get('builds')) is not list or
      type(ledger.get('spent_build_seconds')) is not int or
      ledger.get('spent_build_seconds')!=ledger.get('used_build_seconds') or
      ledger.get('retired_seconds')!=0 or
      'active_build' not in ledger or
      any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R17_PHASE or
          item.get('status') not in TERMINAL or item.get('accounted') is not True or
          not isinstance(item.get('build_id'),str) or not item.get('build_id') or
          type(item.get('build_seconds')) is not int or item.get('build_seconds')<0
          for item in ledger.get('builds')) or
      sum(item['build_seconds'] for item in ledger.get('builds') if type(item) is dict and
          type(item.get('build_seconds')) is int and item.get('build_seconds')>=0)!=ledger.get('used_build_seconds') or
      ledger.get('active_build') is not None):
   raise SystemExit('R17 A1 account authorization mismatch')
  cutoff=datetime.datetime.fromisoformat(expected_cutoff.replace('Z','+00:00'))
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(expected_start.replace('Z','+00:00')):
   raise SystemExit('R17 A2 window not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(expected_main.replace('Z','+00:00')):
   raise SystemExit('R17 A3 main window expired')
  if a.command=='submit':
   if (type(a.timeout) is not int or not 510<=a.timeout<=1200 or a.lane!='merge' or
       a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
    raise SystemExit('R17 A4 requires one exact pinned source, merge lane, timeout510..1200')
   if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
    raise SystemExit('R17 A5 Build plus queue reserve exceeds absolute deadline')
   r14_read_selected_gate(a.proof_sha)
   r17_validate_sources(R17_PROBE_SOURCE,a.proof_sha)
   r17_final_deadline_check(a,ledger)
 if a.phase_id==R16_PHASE:
  expected_ledger=DIR/R16_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-21T16:08:24Z' or
      ledger.get('main_deadline_utc')!='2026-10-21T18:08:24Z' or
      ledger.get('deadline_utc')!='2026-10-21T18:38:24Z' or
      'max_builds' not in ledger or ledger.get('max_builds') is not None or
      type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
      ledger.get('carryover_allowed') is not False or
      ledger.get('publication_gate_path')!=R14_GATE_PATH or
      type(ledger.get('used_build_seconds')) is not int or
      type(ledger.get('remaining_build_seconds')) is not int or
      not 0<=ledger.get('used_build_seconds')<=3600 or
      ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
      type(ledger.get('builds')) is not list or
      any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R16_PHASE
          for item in ledger.get('builds')) or
      'active_build' not in ledger or
      (ledger.get('active_build') is not None and
       (type(ledger.get('active_build')) is not str or not ledger.get('active_build')))):
   raise SystemExit('R16 A1 account authorization mismatch')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T18:38:24+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('R16 A2 window not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('R16 A3 main window expired')
  if a.command=='submit':
   if (type(a.timeout) is not int or not 510<=a.timeout<=1200 or a.lane!='merge' or
       a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
    raise SystemExit('R16 A4 requires one exact pinned source, merge lane, timeout510..1200')
   if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
    raise SystemExit('R16 A5 Build plus queue reserve exceeds absolute deadline')
   r14_read_selected_gate(a.proof_sha)
   r16_validate_sources(R16_PROBE_SOURCE,a.proof_sha)
   r16_final_deadline_check(a,ledger)
 if a.phase_id==R15_PHASE:
  expected_ledger=DIR/R15_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-21T14:12:12Z' or
      ledger.get('main_deadline_utc')!='2026-10-21T16:12:12Z' or
      ledger.get('deadline_utc')!='2026-10-21T16:42:12Z' or
      'max_builds' not in ledger or ledger.get('max_builds') is not None or
      type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
      ledger.get('carryover_allowed') is not False or
      ledger.get('publication_gate_path')!=R14_GATE_PATH or
      type(ledger.get('used_build_seconds')) is not int or
      type(ledger.get('remaining_build_seconds')) is not int or
      not 0<=ledger.get('used_build_seconds')<=3600 or
      ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
      type(ledger.get('builds')) is not list or
      any(type(item) is not dict or item.get('owner')!='merge' or item.get('phase_id')!=R15_PHASE
          for item in ledger.get('builds')) or
      'active_build' not in ledger or
      (ledger.get('active_build') is not None and
       (type(ledger.get('active_build')) is not str or not ledger.get('active_build')))):
   raise SystemExit('R15 A1 account authorization mismatch')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T16:42:12+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('R15 A2 window not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('R15 A3 main window expired')
  if a.command=='submit':
   if (type(a.timeout) is not int or not 510<=a.timeout<=1200 or a.lane!='merge' or
       a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
    raise SystemExit('R15 A4 requires one exact pinned source, merge lane, timeout510..1200')
   if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
    raise SystemExit('R15 A5 Build plus queue reserve exceeds absolute deadline')
   if r13_upload_mode(a.proof_sha)!='proof-r11':
    raise SystemExit('R15 A6 proof mode')
   r14_read_selected_gate(a.proof_sha)
   r15_validate_sources(R15_PROBE_SOURCE,a.proof_sha)
 if a.phase_id=='MERGE-FIRST-CALLBACK-CLOUD-2026-10-17':
  expected_ledger=DIR/'origin-layout'/'FIRST-CALLBACK-BUDGET-20261017.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or
      a.owner!='merge' or ledger.get('owner')!='merge' or
      ledger['ceiling_build_seconds']!=960 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-17T00:32:42Z' or
      ledger.get('main_deadline_utc')!='2026-10-17T02:32:42Z' or
      ledger.get('deadline_utc')!='2026-10-17T03:02:42Z'):
   raise SystemExit('First callback phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-17T03:02:42+00:00')
  if a.command=='submit':
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
    raise SystemExit('First callback main window passed; finishing only')
   if a.timeout>900 or a.lane!='merge' or ledger.get('builds') or ledger.get('active_build') is not None:
    raise SystemExit('First callback permits one merge Build, timeout at most900s; no automatic retry')
 if a.phase_id=='MERGE-FIRST-CALLBACK-PIN-FIX-2026-10-18':
  expected_ledger=DIR/'origin-layout'/'PIN-FIX-BUDGET-20261018.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or
      a.owner!='merge' or ledger.get('owner')!='merge' or
      ledger['ceiling_build_seconds']!=960 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('used_build_seconds')!=0 or ledger.get('remaining_build_seconds')!=960 or
      ledger.get('start_utc')!='2026-10-18T08:41:55Z' or
      ledger.get('main_deadline_utc')!='2026-10-18T10:41:55Z' or
      ledger.get('deadline_utc')!='2026-10-18T11:11:55Z' or
      ledger.get('max_builds')!=1 or ledger.get('max_timeout_seconds')!=900):
   raise SystemExit('Pin-fix phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-18T11:11:55+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Pin-fix session has not started')
  if a.command=='submit':
   if now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
    raise SystemExit('Pin-fix main window passed; finishing only')
   if (a.timeout!=900 or a.lane!='merge' or a.source_mode!='pinned-objects' or
       ledger.get('builds')!=[] or ledger.get('active_build') is not None):
    raise SystemExit('Pin-fix permits one pinned merge attempt, timeout900s; no retry')
 if a.phase_id=='MERGE-FIRST-CALLBACK-TYPE-FIX-2026-10-18':
  expected_ledger=DIR/'origin-layout'/'TYPE-FIX-BUDGET-20261018.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or
      a.owner!='merge' or ledger.get('owner')!='merge' or
      ledger['ceiling_build_seconds']!=960 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('used_build_seconds')!=0 or ledger.get('remaining_build_seconds')!=960 or
      ledger.get('start_utc')!='2026-10-18T14:13:12Z' or
      ledger.get('main_deadline_utc')!='2026-10-18T16:13:12Z' or
      ledger.get('deadline_utc')!='2026-10-18T16:43:12Z' or
      ledger.get('max_builds')!=1 or ledger.get('max_timeout_seconds')!=900):
   raise SystemExit('Type-fix phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-18T16:43:12+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Type-fix session has not started')
  if a.command=='submit':
   if now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
    raise SystemExit('Type-fix main window passed; finishing only')
   if (a.timeout!=900 or a.lane!='merge' or a.source_mode!='pinned-objects' or
       ledger.get('builds')!=[] or ledger.get('active_build') is not None):
    raise SystemExit('Type-fix permits one pinned merge attempt, timeout900s; no retry')
 if a.phase_id=='MERGE-FIRST-COMPARATOR-R1-2026-10-18':
  expected_ledger=DIR/'origin-layout'/'FIRST-COMPARATOR-R1-BUDGET-20261018.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='time-window' or
      ledger['ceiling_build_seconds']!=18960 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-18T19:04:30Z' or
      ledger.get('main_deadline_utc')!='2026-10-18T21:04:30Z' or
      ledger.get('deadline_utc')!='2026-10-18T21:34:30Z'):
   raise SystemExit('First-comparator R1 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-18T21:34:30+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('First-comparator R1 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('First-comparator R1 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=900 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('First-comparator R1 requires pinned merge Build timeout90..900s')
 if a.phase_id=='MERGE-FIRST-COMPARATOR-R2-2026-10-19':
  expected_ledger=DIR/'origin-layout'/'FIRST-COMPARATOR-R2-BUDGET-20261019.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='time-window' or
      ledger['ceiling_build_seconds']!=18960 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-19T11:57:00Z' or
      ledger.get('main_deadline_utc')!='2026-10-19T13:57:00Z' or
      ledger.get('deadline_utc')!='2026-10-19T14:27:00Z'):
   raise SystemExit('First-comparator R2 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-19T14:27:00+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('First-comparator R2 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('First-comparator R2 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=900 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('First-comparator R2 requires pinned merge Build timeout90..900s')
 if a.phase_id=='MERGE-FIRST-COMPARATOR-R3-2026-10-19':
  expected_ledger=DIR/'origin-layout'/'FIRST-COMPARATOR-R3-BUDGET-20261019.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger['ceiling_build_seconds']!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-19T16:09:27Z' or
      ledger.get('main_deadline_utc')!='2026-10-19T19:39:27Z' or
      ledger.get('deadline_utc')!='2026-10-19T20:09:27Z'):
   raise SystemExit('First-comparator R3 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-19T20:09:27+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('First-comparator R3 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('First-comparator R3 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=900 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('First-comparator R3 requires pinned merge Build timeout90..900s')
 if a.phase_id=='MERGE-GUARD-ADDRESSABILITY-R4-2026-10-20':
  expected_ledger=DIR/'origin-layout'/'GUARD-ADDRESSABILITY-R4-BUDGET-20261020.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger['ceiling_build_seconds']!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-19T21:24:56Z' or
      ledger.get('main_deadline_utc')!='2026-10-19T23:24:56Z' or
      ledger.get('deadline_utc')!='2026-10-19T23:54:56Z'):
   raise SystemExit('Guard-addressability R4 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-19T23:54:56+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Guard-addressability R4 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Guard-addressability R4 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=900 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('Guard-addressability R4 requires pinned merge Build timeout90..900s')
 if a.phase_id=='MERGE-CURRENT-OWNERSHIP-R5-2026-10-20':
  expected_ledger=DIR/'origin-layout'/'CURRENT-OWNERSHIP-R5-BUDGET-20261020.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-20T07:28:45Z' or
      ledger.get('main_deadline_utc')!='2026-10-20T09:28:45Z' or
      ledger.get('deadline_utc')!='2026-10-20T09:58:45Z' or
      ledger.get('max_timeout_seconds')!=900):
   raise SystemExit('Current-ownership R5 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-20T09:58:45+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Current-ownership R5 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Current-ownership R5 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=900 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('Current-ownership R5 requires pinned merge Build timeout90..900s')
 if a.phase_id=='MERGE-CANONICAL-SHARE-R6-2026-10-20':
  expected_ledger=DIR/'origin-layout'/'CANONICAL-SHARE-R6-BUDGET-20261020.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-20T11:56:46Z' or
      ledger.get('main_deadline_utc')!='2026-10-20T13:56:46Z' or
      ledger.get('deadline_utc')!='2026-10-20T14:26:46Z' or
      ledger.get('max_timeout_seconds')!=900):
   raise SystemExit('Canonical-share R6 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-20T14:26:46+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Canonical-share R6 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Canonical-share R6 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=900 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('Canonical-share R6 requires pinned merge Build timeout90..900s')
 if a.phase_id=='MERGE-POST-MIGRATION-CURRENT-RECOVERY-R7-2026-10-20':
  expected_ledger=DIR/'origin-layout'/'CURRENT-RECOVERY-R7-BUDGET-20261020.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-20T14:33:33Z' or
      ledger.get('main_deadline_utc')!='2026-10-20T16:33:33Z' or
      ledger.get('deadline_utc')!='2026-10-20T17:03:33Z' or
      ledger.get('max_timeout_seconds')!=900):
   raise SystemExit('Current-recovery R7 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-20T17:03:33+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Current-recovery R7 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Current-recovery R7 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=900 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('Current-recovery R7 requires pinned merge Build timeout90..900s')
 if a.phase_id=='MERGE-LATE-RECOVERY-REJOIN-R8-2026-10-20':
  expected_ledger=DIR/'origin-layout'/'CURRENT-RECOVERY-R8-BUDGET-20261020.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-20T17:11:30Z' or
      ledger.get('main_deadline_utc')!='2026-10-20T19:11:30Z' or
      ledger.get('deadline_utc')!='2026-10-20T19:41:30Z' or
      ledger.get('max_timeout_seconds')!=900):
   raise SystemExit('Late-recovery-rejoin R8 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-20T19:41:30+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Late-recovery-rejoin R8 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Late-recovery-rejoin R8 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=900 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('Late-recovery-rejoin R8 requires pinned merge Build timeout90..900s')
 if a.phase_id=='MERGE-GUARD-CURRENT-RETURN-R9-2026-10-20':
  expected_ledger=DIR/'origin-layout'/'CURRENT-RECOVERY-R9-BUDGET-20261020.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-20T19:30:15Z' or
      ledger.get('main_deadline_utc')!='2026-10-20T21:30:15Z' or
      ledger.get('deadline_utc')!='2026-10-20T22:00:15Z' or
      ledger.get('max_timeout_seconds')!=1200):
   raise SystemExit('Guard/CURRENT return R9 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-20T22:00:15+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Guard/CURRENT return R9 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Guard/CURRENT return R9 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=1200 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('Guard/CURRENT return R9 requires pinned merge Build timeout90..1200s')
 if a.phase_id=='MERGE-MOVING-GAP-INVARIANT-R10-2026-10-21':
  expected_ledger=DIR/'origin-layout'/'CURRENT-RECOVERY-R10-BUDGET-20261021.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-20T21:48:01Z' or
      ledger.get('main_deadline_utc')!='2026-10-20T23:48:01Z' or
      ledger.get('deadline_utc')!='2026-10-21T00:18:01Z' or
      ledger.get('max_timeout_seconds')!=1200):
   raise SystemExit('Moving-gap invariant R10 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T00:18:01+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Moving-gap invariant R10 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Moving-gap invariant R10 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=1200 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('Moving-gap invariant R10 requires pinned merge Build timeout90..1200s')
 if a.phase_id=='MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21':
  expected_ledger=DIR/'origin-layout'/'CURRENT-RECOVERY-R11-BUDGET-20261021.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-21T06:14:39Z' or
      ledger.get('main_deadline_utc')!='2026-10-21T08:14:39Z' or
      ledger.get('deadline_utc')!='2026-10-21T08:44:39Z' or
      ledger.get('max_timeout_seconds')!=1200):
   raise SystemExit('Label-storage invariant R11 differs from owner time-window authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T08:44:39+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('Label-storage invariant R11 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Label-storage invariant R11 main window passed; no new dispatch/request')
  if a.command=='submit' and (not 90<=a.timeout<=1200 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('Label-storage invariant R11 requires pinned merge Build timeout90..1200s')
 if a.phase_id=='MERGE-R11-EVIDENCE-RETRY-2026-10-21':
  expected_ledger=DIR/'origin-layout'/'R11-RETRY-BUDGET-20261021.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or
      a.owner!='merge' or ledger.get('owner')!='merge' or
      ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=1060 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-21T09:02:57Z' or
      ledger.get('main_deadline_utc')!='2026-10-21T09:32:57Z' or
      ledger.get('deadline_utc')!='2026-10-21T09:47:57Z' or
      type(ledger.get('max_builds')) is not int or ledger.get('max_builds')!=1 or
      type(ledger.get('max_timeout_seconds')) is not int or
      ledger.get('max_timeout_seconds')!=1000 or
      type(ledger.get('used_build_seconds')) is not int or
      not 0<=ledger.get('used_build_seconds')<=1060 or
      type(ledger.get('remaining_build_seconds')) is not int or
      ledger.get('remaining_build_seconds')!=1060-ledger.get('used_build_seconds') or
      type(ledger.get('builds')) is not list or len(ledger.get('builds'))>1 or
      'active_build' not in ledger or
      'authorized_source_sha' not in ledger or
      (ledger.get('authorized_source_sha') is not None and
       (not isinstance(ledger.get('authorized_source_sha'),str) or
        not re.fullmatch(r'[0-9a-f]{40}',ledger.get('authorized_source_sha')))) or
      ledger.get('carryover_allowed') is not False):
   raise SystemExit('R11 evidence retry differs from exact one-Build owner authorization')
  if a.command in ('submit','request') and (
      ledger.get('builds') or ledger.get('active_build') is not None or
      ledger.get('used_build_seconds')!=0 or ledger.get('remaining_build_seconds')!=1060):
   raise SystemExit('R11 evidence retry Build/request already used; one-shot phase cannot be reused')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T09:47:57+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('R11 evidence retry has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('R11 evidence retry main window passed; no new dispatch/request')
  if a.command=='submit' and (a.timeout!=1000 or a.lane!='merge' or a.source_mode!='pinned-objects'):
   raise SystemExit('R11 evidence retry permits only the pinned merge lane at timeout 1000s')
  if a.command=='submit' and now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
   raise SystemExit('R11 evidence retry Build plus queue reserve exceeds the absolute deadline')
  if a.command=='submit' and (
      not isinstance(ledger.get('authorized_source_sha'),str) or
      not re.fullmatch(r'[0-9a-f]{40}',ledger.get('authorized_source_sha')) or
      getattr(a,'infra_sha',None)!=ledger.get('authorized_source_sha') or
      getattr(a,'proof_sha',None)!=ledger.get('authorized_source_sha')):
   raise SystemExit('R11 evidence retry requires the single reviewed source SHA pinned in its fresh account')
 if a.phase_id=='MERGE-UPLOAD-NONCOMPOSITE-R12-2026-10-21':
  expected_ledger=DIR/'origin-layout'/'CURRENT-RECOVERY-R12-UPLOAD-BUDGET-20261021.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-21T10:53:30Z' or
      ledger.get('main_deadline_utc')!='2026-10-21T12:53:30Z' or
      ledger.get('deadline_utc')!='2026-10-21T13:23:30Z' or
      'max_builds' not in ledger or ledger.get('max_builds') is not None or
      type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
      ledger.get('carryover_allowed') is not False or
      'synthetic_upload_gate' not in ledger or
      type(ledger.get('used_build_seconds')) is not int or
      type(ledger.get('remaining_build_seconds')) is not int or
      not 0<=ledger.get('used_build_seconds')<=3600 or
      not 0<=ledger.get('remaining_build_seconds')<=3600 or
      ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
      type(ledger.get('builds')) is not list or
      any(type(item) is not dict for item in ledger.get('builds')) or
      'active_build' not in ledger or
      (ledger.get('active_build') is not None and
       (type(ledger.get('active_build')) is not str or not ledger.get('active_build')))):
   raise SystemExit('R12 differs from its fresh non-composite upload authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T13:23:30+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('R12 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('R12 main window passed; no new dispatch/request')
  if a.command=='submit':
   if (type(a.timeout) is not int or not 90<=a.timeout<=1200 or a.lane!='merge' or
       a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
    raise SystemExit('R12 requires one exact pinned infra/proof source, merge lane, timeout90..1200')
   if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
    raise SystemExit('R12 Build plus queue reserve exceeds the absolute deadline')
   mode=r12_upload_mode(a.proof_sha)
   if mode=='proof-r11':
    gate=ledger.get('synthetic_upload_gate')
    if (not isinstance(gate,dict) or gate.get('status')!='VERIFIED_SYNTHETIC_PUBLICATION' or
        gate.get('upload_complete') is not True or gate.get('archive_inventory_verified') is not True or
        gate.get('proof_attempted') is not False or gate.get('verification_accepted') is not False or
        gate.get('parallel_composite_upload_enabled') is not False or
        type(gate.get('archive_size_bytes')) is not int or
        type(gate.get('threshold_bytes')) is not int or gate.get('threshold_bytes')<=0 or
        gate.get('archive_size_bytes')<=gate.get('threshold_bytes') or
        not isinstance(gate.get('brief_request_id'),str) or not gate.get('brief_request_id') or
        not isinstance(gate.get('archive_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',gate.get('archive_sha256'))):
     raise SystemExit('R12 proof retry requires accessible verified synthetic publication gate')
    matching=[x for x in ledger['builds'] if x.get('build_id')==gate.get('build_id') and
              x.get('accounted') is True and x.get('status')=='SUCCESS' and
              x.get('proof_sha')==gate.get('proof_source_sha') and
              x.get('submitted_config_sha256')==gate.get('submitted_config_sha256')]
    if len(matching)!=1 or r12_upload_mode(matching[0]['proof_sha'])!='synthetic-upload':
     raise SystemExit('R12 synthetic gate does not bind its successful accounted Build/source/config')
    r12_validate_retry_sources(gate['proof_source_sha'],a.proof_sha)
 if a.phase_id=='MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21':
  expected_ledger=DIR/'origin-layout'/'CURRENT-RECOVERY-R13-UPLOAD-BUDGET-20261021.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-21T12:10:26Z' or
      ledger.get('main_deadline_utc')!='2026-10-21T14:10:26Z' or
      ledger.get('deadline_utc')!='2026-10-21T14:40:26Z' or
      'max_builds' not in ledger or ledger.get('max_builds') is not None or
      type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
      ledger.get('carryover_allowed') is not False or
      'synthetic_upload_gate' not in ledger or
      type(ledger.get('used_build_seconds')) is not int or
      type(ledger.get('remaining_build_seconds')) is not int or
      not 0<=ledger.get('used_build_seconds')<=3600 or
      not 0<=ledger.get('remaining_build_seconds')<=3600 or
      ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
      type(ledger.get('builds')) is not list or
      any(type(item) is not dict for item in ledger.get('builds')) or
      'active_build' not in ledger or
      (ledger.get('active_build') is not None and
       (type(ledger.get('active_build')) is not str or not ledger.get('active_build')))):
   raise SystemExit('R13 differs from its fresh non-composite upload authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T14:40:26+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('R13 has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('R13 main window passed; no new dispatch/request')
  if a.command=='submit':
   if (type(a.timeout) is not int or not 90<=a.timeout<=1200 or a.lane!='merge' or
       a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
    raise SystemExit('R13 requires one exact pinned infra/proof source, merge lane, timeout90..1200')
   if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
    raise SystemExit('R13 Build plus queue reserve exceeds the absolute deadline')
   mode=r13_upload_mode(a.proof_sha)
   if mode=='proof-r11':
    gate=ledger.get('synthetic_upload_gate')
    if (not isinstance(gate,dict) or gate.get('status')!='VERIFIED_SYNTHETIC_PUBLICATION' or
        gate.get('upload_complete') is not True or gate.get('archive_inventory_verified') is not True or
        gate.get('proof_attempted') is not False or gate.get('verification_accepted') is not False or
        gate.get('parallel_composite_upload_enabled') is not False or
        type(gate.get('archive_size_bytes')) is not int or
        type(gate.get('threshold_bytes')) is not int or gate.get('threshold_bytes')<=0 or
        gate.get('archive_size_bytes')<=gate.get('threshold_bytes') or
        type(gate.get('archive_limit_bytes')) is not int or gate.get('archive_limit_bytes')!=536870912 or
        gate.get('archive_size_bytes')>536870912 or
        not isinstance(gate.get('brief_request_id'),str) or not gate.get('brief_request_id') or
        not isinstance(gate.get('archive_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',gate.get('archive_sha256'))):
     raise SystemExit('R13 proof retry requires accessible verified synthetic publication gate')
    matching=[x for x in ledger['builds'] if x.get('build_id')==gate.get('build_id') and
              x.get('accounted') is True and x.get('status')=='SUCCESS' and
              x.get('proof_sha')==gate.get('proof_source_sha') and
              x.get('submitted_config_sha256')==gate.get('submitted_config_sha256')]
    if len(matching)!=1 or r13_upload_mode(matching[0]['proof_sha'])!='synthetic-upload':
     raise SystemExit('R13 synthetic gate does not bind its successful accounted Build/source/config')
    r13_validate_retry_sources(gate['proof_source_sha'],a.proof_sha)
 if a.phase_id==R14_PHASE:
  expected_ledger=DIR/R14_LEDGER_PATH.removeprefix('research/challenge-8/cloud-build/')
  if (a.ledger.resolve()!=expected_ledger.resolve() or a.owner!='merge' or
      ledger.get('owner')!='merge' or ledger.get('authorization_model')!='bounded-cloud-budget' or
      ledger.get('ceiling_build_seconds')!=3600 or ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-21T12:52:50Z' or
      ledger.get('main_deadline_utc')!='2026-10-21T14:52:50Z' or
      ledger.get('deadline_utc')!='2026-10-21T15:22:50Z' or
      'max_builds' not in ledger or ledger.get('max_builds') is not None or
      type(ledger.get('max_timeout_seconds')) is not int or ledger.get('max_timeout_seconds')!=1200 or
      ledger.get('carryover_allowed') is not False or
      ledger.get('publication_gate_path')!=R14_GATE_PATH or
      type(ledger.get('used_build_seconds')) is not int or
      type(ledger.get('remaining_build_seconds')) is not int or
      not 0<=ledger.get('used_build_seconds')<=3600 or
      ledger.get('used_build_seconds')+ledger.get('remaining_build_seconds')!=3600 or
      type(ledger.get('builds')) is not list or
      any(type(item) is not dict for item in ledger.get('builds')) or
      any(item.get('build_id')==R14_GATE_IDENTITIES['build_id'] or
          item.get('owner')!='merge' or item.get('phase_id')!=R14_PHASE
          for item in ledger.get('builds')) or
      'active_build' not in ledger or
      (ledger.get('active_build') is not None and
       (type(ledger.get('active_build')) is not str or not ledger.get('active_build')))):
   raise SystemExit('R14 A1 account authorization mismatch')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T15:22:50+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('R14 A2 window not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('R14 A3 main window expired')
  if a.command=='submit':
   if (type(a.timeout) is not int or not 90<=a.timeout<=1200 or a.lane!='merge' or
       a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
    raise SystemExit('R14 A4 submit pins/timeout')
   if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
    raise SystemExit('R14 A5 deadline reserve')
   if r13_upload_mode(a.proof_sha)!='proof-r11':
    raise SystemExit('R14 A6 proof mode')
   r14_read_selected_gate(a.proof_sha)
   r14_validate_retry_sources(R14_PROBE_SOURCE,a.proof_sha)
 if a.phase_id=='CI-IAM-E2E-ONCE-2026-10-17':
  expected_ledger=DIR/'ci-iam-e2e-once-20261017'/'BUDGET.json'
  if (a.ledger.resolve()!=expected_ledger.resolve() or
      a.owner!='merge' or ledger.get('owner')!='merge' or
      ledger['ceiling_build_seconds']!=360 or
      ledger.get('allowed_lanes')!=['coordination-regression']):
   raise SystemExit('IAM E2E phase requires its separate merge account and exact scope')
  try:start=datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00'))
  except (KeyError,AttributeError,ValueError) as error:raise SystemExit('Invalid IAM E2E start') from error
  if (start.tzinfo is None or deadline.tzinfo is None or
      deadline-start!=datetime.timedelta(minutes=30) or
      datetime.datetime.now(datetime.timezone.utc)<start):
   raise SystemExit('IAM E2E requires an active, explicit 30-minute window')
  cutoff=deadline
  if a.command=='submit':
   if (ledger.get('builds')!=[] or ledger.get('active_build') is not None or
       a.timeout!=300 or a.lane!='coordination-regression' or
       a.source_mode!='pinned-objects' or
       a.proof_sha!='e918eb875119d912b981da2bfec4e0406e06571e'):
    raise SystemExit('IAM E2E permits one pinned historical diagnostic attempt, timeout300s')
 if a.phase_id=='DAY-MERGE-CLOUD-2026-10-09':
  if (a.owner!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-09T08:46:19Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T10:46:19Z' or
      ledger.get('deadline_utc')!='2026-10-09T11:16:19Z'):
   raise SystemExit('DAY merge phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-09T11:16:19+00:00')
 if a.phase_id=='AFTERNOON-MERGE-GUARD-CLOUD-2026-10-09':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['coordination-regression','merge'] or
      ledger.get('start_utc')!='2026-10-09T11:15:53Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T13:15:53Z' or
      ledger.get('deadline_utc')!='2026-10-09T13:45:53Z'):
   raise SystemExit('AFTERNOON merge phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-09T13:45:53+00:00')
 if a.phase_id=='NEXT-MERGE-DROP-CALLER-CLOUD-2026-10-09':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-09T13:27:15Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T14:27:15Z' or
      ledger.get('deadline_utc')!='2026-10-09T14:57:15Z'):
   raise SystemExit('NEXT merge phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-09T14:57:15+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('NEXT merge main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-MD-AUTHORITY-CLOUD-2026-10-09':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-09T14:28:08Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T15:28:08Z' or
      ledger.get('deadline_utc')!='2026-10-09T15:58:08Z'):
   raise SystemExit('MD authority merge phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-09T15:58:08+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('MD authority main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-SRC-ALIGN-RECOVERY-CLOUD-2026-10-09':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-09T15:58:54Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T16:58:54Z' or
      ledger.get('deadline_utc')!='2026-10-09T17:28:54Z'):
   raise SystemExit('Source alignment/recovery phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-09T17:28:54+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Source alignment/recovery main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-ALLOCATION-SPAN-PATCH-CLOUD-2026-10-09':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-09T17:32:10Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T18:32:10Z' or
      ledger.get('deadline_utc')!='2026-10-09T19:02:10Z'):
   raise SystemExit('Allocation span phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-09T19:02:10+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Allocation span main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-INCOMING-SPAN-LIFETIME-CLOUD-2026-10-09':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-09T18:49:50Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T19:49:50Z' or
      ledger.get('deadline_utc')!='2026-10-09T20:19:50Z'):
   raise SystemExit('Incoming span/lifetime phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-09T20:19:50+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Incoming span main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-INCOMING-ORIGIN-CLOUD-2026-10-09':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-09T20:16:40Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T21:16:40Z' or
      ledger.get('deadline_utc')!='2026-10-09T21:46:40Z'):
   raise SystemExit('Incoming origin phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-09T21:46:40+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Incoming origin main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-ORIGIN-LAYOUT-CLOUD-2026-10-10':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-09T21:53:00Z' or
      ledger.get('main_deadline_utc')!='2026-10-09T23:53:00Z' or
      ledger.get('deadline_utc')!='2026-10-10T00:23:00Z'):
   raise SystemExit('Origin/layout phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-10T00:23:00+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Origin/layout main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-CURRENT-RECOVERY-CLOUD-2026-10-10':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-10T00:34:48Z' or
      ledger.get('main_deadline_utc')!='2026-10-10T02:34:48Z' or
      ledger.get('deadline_utc')!='2026-10-10T03:04:48Z'):
   raise SystemExit('CURRENT recovery phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-10T03:04:48+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('CURRENT recovery main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-GUARD-GLUE-CLOUD-2026-10-10':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-10T10:21:50Z' or
      ledger.get('main_deadline_utc')!='2026-10-10T12:21:50Z' or
      ledger.get('deadline_utc')!='2026-10-10T12:51:50Z'):
   raise SystemExit('Guard/glue phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-10T12:51:50+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Guard/glue main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-BRIDGE-COMPILE-CLOUD-2026-10-10':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-10T12:58:04Z' or
      ledger.get('main_deadline_utc')!='2026-10-10T14:58:04Z' or
      ledger.get('deadline_utc')!='2026-10-10T15:28:04Z'):
   raise SystemExit('Bridge compile phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-10T15:28:04+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Bridge compile main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-GUARD-LEN1-CLOUD-2026-10-10':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-10T19:26:15Z' or
      ledger.get('main_deadline_utc')!='2026-10-10T21:26:15Z' or
      ledger.get('deadline_utc')!='2026-10-10T21:56:15Z'):
   raise SystemExit('Guard/len1 phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-10T21:56:15+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Guard/len1 main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-LEN1-COMPOSITION-CLOUD-2026-10-11':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-10T22:36:57Z' or
      ledger.get('main_deadline_utc')!='2026-10-11T00:36:57Z' or
      ledger.get('deadline_utc')!='2026-10-11T01:06:57Z'):
   raise SystemExit('Len1 composition phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-11T01:06:57+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Len1 composition main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-RECEIVER-CLOUD-2026-10-11':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-11T08:17:34Z' or
      ledger.get('main_deadline_utc')!='2026-10-11T09:17:34Z' or
      ledger.get('deadline_utc')!='2026-10-11T09:47:34Z'):
   raise SystemExit('Receiver phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-11T09:47:34+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Receiver main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-SELECTED-DROP-CLOUD-2026-10-11':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-11T09:24:22Z' or
      ledger.get('main_deadline_utc')!='2026-10-11T11:24:22Z' or
      ledger.get('deadline_utc')!='2026-10-11T11:54:22Z'):
   raise SystemExit('Selected Drop phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-11T11:54:22+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Selected Drop main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-ACTUAL-GLUE-CLOUD-2026-10-11':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-11T14:03:11Z' or
      ledger.get('main_deadline_utc')!='2026-10-11T16:03:11Z' or
      ledger.get('deadline_utc')!='2026-10-11T16:33:11Z'):
   raise SystemExit('Actual glue phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-11T16:33:11+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Actual glue main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-GLUE-BINDING-CLOUD-2026-10-11':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-11T16:15:22Z' or
      ledger.get('main_deadline_utc')!='2026-10-11T19:15:22Z' or
      ledger.get('deadline_utc')!='2026-10-11T19:15:22Z'):
   raise SystemExit('Actual glue phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-11T19:15:22+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Actual glue main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-GLUE-BODY-CLOUD-2026-10-11':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-11T19:19:34Z' or
      ledger.get('main_deadline_utc')!='2026-10-11T21:19:34Z' or
      ledger.get('deadline_utc')!='2026-10-11T21:49:34Z'):
   raise SystemExit('Generated glue phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-11T21:49:34+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('Generated glue main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-B1-B2-CLOUD-2026-10-12':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=3600 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-11T21:36:26Z' or
      ledger.get('main_deadline_utc')!='2026-10-11T23:36:26Z' or
      ledger.get('deadline_utc')!='2026-10-12T00:06:26Z'):
   raise SystemExit('B1/B2 merge phase differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-12T00:06:26+00:00')
  if a.command=='submit' and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('B1/B2 main window passed; finishing/evidence/checkpoint only')
 if a.phase_id=='MERGE-SHARED-REF-SESSION3-CLOUD-2026-10-12':
  if (a.owner!='merge' or ledger.get('owner')!='merge' or ledger['ceiling_build_seconds']!=960 or
      ledger.get('allowed_lanes')!=['merge'] or
      ledger.get('start_utc')!='2026-10-12T00:19:22Z' or
      ledger.get('main_deadline_utc')!='2026-10-12T01:19:22Z' or
      ledger.get('deadline_utc')!='2026-10-12T01:49:22Z'):
   raise SystemExit('Shared-reference session3 differs from explicit owner authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-12T01:49:22+00:00')
  if a.command=='submit':
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
    raise SystemExit('Shared-reference main window passed; finishing/evidence/checkpoint only')
   if a.timeout>900 or a.lane!='merge' or ledger.get('builds'):
    raise SystemExit('Shared-reference session3 permits one new merge Build, timeout at most900s')
 if deadline.tzinfo is None or deadline>cutoff:raise SystemExit('Phase deadline exceeds authorized cutoff')
 if a.phase_id==NIGHT_PHASE and deadline!=cutoff:raise SystemExit('Select phase requires its exact 08:00 UTC deadline')
 if datetime.datetime.now(datetime.timezone.utc)>=deadline:raise SystemExit('Phase deadline has passed')
 return deadline


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--state-dir',type=Path);p.add_argument('--phase-id');p.add_argument('--ledger',type=Path);p.add_argument('--owner')
 sub=p.add_subparsers(dest='command',required=True)
 q=sub.add_parser('submit');q.add_argument('--infra-sha',required=True);q.add_argument('--proof-sha',required=True);q.add_argument('--lane',required=True);q.add_argument('--timeout',type=int,required=True);q.add_argument('--source-mode',choices=['public-git','pinned-objects'],default='pinned-objects')
 q=sub.add_parser('status');q.add_argument('build_id',nargs='?')
 q=sub.add_parser('download');q.add_argument('build_id');q.add_argument('--output',type=Path,required=True);q.add_argument('--text-logs',action='store_true')
 q=sub.add_parser('cancel');q.add_argument('build_id')
 sub.add_parser('request')
 sub.add_parser('withdraw-request')
 a=p.parse_args()
 if a.command in ('submit','request','withdraw-request') and (not a.phase_id or not a.ledger or not a.state_dir or not a.owner):raise SystemExit('phase operation requires explicit --phase-id, --ledger, --state-dir and --owner')
 ledger_path=(a.ledger or DIR/'BUDGET.json').resolve()
 state=(a.state_dir or Path('/tmp/smallsort-cloud-migration')).resolve()
 if a.ledger and not ledger_path.is_relative_to(ROOT):raise SystemExit('Selected writable ledger must belong to this worktree')
 if bool(a.owner)!=bool(a.ledger):raise SystemExit('Global reconciliation requires both explicit --owner and --ledger')
 if a.phase_id and a.phase_id!=read(ledger_path).get('phase'):raise SystemExit('Phase ID does not match the selected ledger')
 if a.command=='download':
  with coordination.locked():
   if a.owner:reconcile_global(a.owner,ledger_path)
   ledger=read(ledger_path)
   reconcile(state,ledger,ledger_path)
   item=next((x.copy() for x in ledger['builds'] if x.get('build_id')==a.build_id),None)
   if item is None:raise SystemExit('Not a recorded own build')
  download(a,item)
  with coordination.locked():
   ledger=read(ledger_path)
   current=next((x for x in ledger['builds'] if x.get('build_id')==a.build_id),None)
   if current is None or current.get('submitted_config_sha256')!=item['submitted_config_sha256']:raise RuntimeError('Ledger changed during evidence download')
   current['download_verified']=True;current['archive_sha256']=(a.output/'archive.sha256').read_text().split()[0]
   write(ledger_path,ledger)
  return
 with coordination.locked():
  if a.command in ('request','withdraw-request'):
   ledger=read(ledger_path)
   run_command(a,state,ledger,ledger_path)
   return
  if a.owner:reconcile_global(a.owner,ledger_path)
  state.mkdir(parents=True,exist_ok=True)
  ledger=read(ledger_path)
  reconcile(state,ledger,ledger_path)
  run_command(a,state,ledger,ledger_path)


def run_command(a,state,ledger,ledger_path):
 if a.command=='request':
  authorized_phase(a,ledger)
  coordination.request(a.owner,a.phase_id,ledger_path,ledger['deadline_utc'])
  print('Turn requested for',a.owner)
  return
 if a.command=='withdraw-request':
  if not a.owner or not OWNER_PATTERN.fullmatch(a.owner):raise SystemExit('Explicit valid --owner is required')
  request_path=coordination.COORDINATION/'requests'/(a.owner+'.json')
  if request_path.exists():
   request=read(request_path)
   if request.get('phase_id')!=a.phase_id or request.get('ledger')!=str(ledger_path):raise SystemExit('Request does not match the selected phase account')
  coordination.withdraw(a.owner)
  print('Turn request withdrawn for',a.owner)
  return
 if a.command=='submit':
  deadline=authorized_phase(a,ledger)
  if a.lane not in ledger.get('allowed_lanes',[]):raise SystemExit('Lane is not approved in the phase account')
  if not LANE_PATTERN.fullmatch(a.lane):raise SystemExit('Invalid lane name')
  if a.source_mode!='pinned-objects':raise SystemExit('New phase requires pinned Git objects')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now+datetime.timedelta(seconds=a.timeout+60)>deadline:raise SystemExit('Timeout plus queue reserve exceeds phase deadline')
  coordination.request(a.owner,a.phase_id,ledger_path,ledger['deadline_utc'])
  for sha in [a.infra_sha,a.proof_sha]:
   if not re.fullmatch('[0-9a-f]{40}',sha):raise SystemExit('Full published SHA required')
   subprocess.run(['git','cat-file','-e',sha+'^{commit}'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for name in ['control.py','coordination.py','package-evidence.py','source-input.py']:
   expected=subprocess.check_output(['git','show',a.infra_sha+':research/challenge-8/cloud-build/'+name],cwd=ROOT)
   if expected!=(DIR/name).read_bytes():raise SystemExit('Uncommitted/local '+name+' differs from infrastructure SHA; publish first')
  ongoing=invoke(['builds','list','--region=global','--ongoing','--format=json'])
  if ledger['active_build']:raise SystemExit('Own queued/active or unresolved build: monitor/reconcile first')
  coordination.require_capacity(a.owner,ledger_path,ongoing or [])
  if not 90<=a.timeout<=1740 or a.timeout+60>1800 or a.timeout+60>ledger['remaining_build_seconds']:raise SystemExit('Invalid timeout or insufficient phase budget (60s queue reserve included)')
  token='dispatch-'+uuid.uuid4().hex
  source_payload=None
  if a.source_mode=='pinned-objects':
   sys.dont_write_bytecode=True
   spec=importlib.util.spec_from_file_location('source_input',DIR/'source-input.py')
   module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
   source_payload=module.make_payload(ROOT,a.infra_sha,a.proof_sha,a.lane)
  cfg=config(a.infra_sha,a.proof_sha,a.lane,a.timeout,token,source_payload,
             r13_required=required_upload_guard(a.phase_id))
  if a.phase_id==R15_PHASE:r15_set_execute_budget(cfg,a.timeout)
  if a.phase_id==R16_PHASE:r16_validate_execute_budget(cfg,a.timeout)
  if a.phase_id==R17_PHASE:r17_validate_execute_budget(cfg,a.timeout)
  if a.phase_id==R18_PHASE:r17_validate_execute_budget(cfg,a.timeout)
  if a.phase_id==R19_PHASE:r17_validate_execute_budget(cfg,a.timeout)
  if a.phase_id==R20_PHASE:r17_validate_execute_budget(cfg,a.timeout)
  if a.phase_id==R21_PHASE:r17_validate_execute_budget(cfg,a.timeout)
  if a.phase_id==R22_PHASE:r17_validate_execute_budget(cfg,a.timeout)
  if a.phase_id==R23_PHASE:r17_validate_execute_budget(cfg,a.timeout)
  if any(len(arg.encode())>10000 for step in cfg['steps'] for arg in step.get('args',[])):raise SystemExit('Config argument exceeds Cloud Build 10000-byte limit; no dispatch')
  source_values={k:v for k,v in cfg['substitutions'].items() if k.startswith('_SOURCE_')}
  for key in source_values:cfg['substitutions'][key]='placeholder'
  raw=(json.dumps(cfg,indent=2)+'\n').encode();h=digest(raw);path=state/(token+'.json');coordination.write_bytes(path,raw)
  compressed=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
  if len(compressed)>8*3500:raise SystemExit('Submitted config exceeds evidence transport limit; no dispatch')
  item={'dispatch_token':token,'owner':a.owner,'phase_id':a.phase_id,'infra_sha':a.infra_sha,'proof_sha':a.proof_sha,'lane':a.lane,'submitted_config_sha256':h,'reserved_seconds':a.timeout+60,'timeout_seconds':a.timeout,'status':'DISPATCH_PENDING','publish_text_logs':True,'source_mode':a.source_mode,'source_input_sha256':digest(source_payload) if source_payload is not None else None}
  values={'_CONFIG_SHA':h,**{f'_CONFIG_{i}':compressed[i*3500:(i+1)*3500] for i in range(8)},**source_values}
  flags=state/(token+'-flags.json');write(flags,{'--substitutions':values})
  reservation={'dispatch_token':token,'owner':a.owner,'phase_id':a.phase_id,'ledger':str(ledger_path),'state_dir':str(state),'item':item,'build_id':None}
  if a.phase_id in ('MERGE-FIRST-COMPARATOR-R1-2026-10-18','MERGE-FIRST-COMPARATOR-R2-2026-10-19','MERGE-FIRST-COMPARATOR-R3-2026-10-19','MERGE-GUARD-ADDRESSABILITY-R4-2026-10-20','MERGE-CURRENT-OWNERSHIP-R5-2026-10-20','MERGE-CANONICAL-SHARE-R6-2026-10-20','MERGE-POST-MIGRATION-CURRENT-RECOVERY-R7-2026-10-20','MERGE-LATE-RECOVERY-REJOIN-R8-2026-10-20','MERGE-GUARD-CURRENT-RETURN-R9-2026-10-20','MERGE-MOVING-GAP-INVARIANT-R10-2026-10-21','MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21','MERGE-R11-EVIDENCE-RETRY-2026-10-21','MERGE-UPLOAD-NONCOMPOSITE-R12-2026-10-21',R14_PHASE,R15_PHASE,R16_PHASE,R17_PHASE,R18_PHASE,R19_PHASE,R20_PHASE,R21_PHASE,R22_PHASE,R23_PHASE,'MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21'):authorized_phase(a,ledger)
  coordination.reserve(reservation)
  ledger['builds'].append(item);ledger['active_build']=token;write(ledger_path,ledger)
  cmd=['builds','submit','--no-source','--async','--region=global','--config='+str(path),'--flags-file='+str(flags),'--format=json','--quiet']
  try:b=invoke(cmd)
  except Exception as e:
   print('Dispatch response uncertain/error:',str(e).split('substitution value')[0][:400],file=sys.stderr)
   matches=invoke(['builds','list','--region=global','--filter=tags:'+token,'--format=json']) or []
   if not matches and re.search(r'ERROR: \(gcloud\.builds\.submit\) INVALID_ARGUMENT\b',str(e)):
    reservation['validation_rejection']=True;reservation['rejection_reason']=str(e).split('substitution value')[0][:300];coordination.update(reservation)
    write(coordination.COORDINATION/'receipts'/(token+'.json'),
          {'dispatch_token':token,'owner':a.owner,'phase_id':a.phase_id,
           'ledger':str(ledger_path),'build_id':None,'status':'NOT_CREATED_INVALID_ARGUMENT',
           'validation_rejection':True,'reason':reservation['rejection_reason'],'build_seconds':0})
    item.update(status='NOT_CREATED_INVALID_ARGUMENT',accounted=True,build_seconds=0,reason=str(e).split('substitution value')[0][:300]);ledger['active_build']=None;write(ledger_path,ledger);coordination.clear(token);raise SystemExit('Definitive API validation rejection; no build found and no time charged')
   if len(matches)!=1:raise SystemExit('No unique build resolved. Pending dispatch retained; lookup token before any retry: '+token)
   b=matches[0]
  item['build_id']=b['id'];item['status']=b.get('status');ledger['active_build']=b['id'];write(ledger_path,ledger);reservation['build_id']=b['id'];coordination.update(reservation);write(state/(b['id']+'.json'),b)
  coordination.submitted(a.owner,token)
  print(json.dumps({'build_id':b['id'],'config_sha256':h,'dispatch_token':token,'bucket_prefix':BUCKET+'/'+b['id']},indent=2))
 elif a.command=='status':
  if a.build_id:
   b=invoke(['builds','describe',a.build_id,'--region=global','--format=json']);print(json.dumps({key:b.get(key) for key in ['id','status','createTime','startTime','finishTime','logUrl']},indent=2))
  else:print(json.dumps(ledger,indent=2))
 elif a.command=='cancel':
  active=coordination.active(a.owner)
  if not active or active.get('build_id')!=a.build_id or active.get('owner')!=a.owner or active.get('phase_id')!=a.phase_id or active.get('ledger')!=str(ledger_path):raise SystemExit('Only the explicitly selected owner may cancel its active build')
  if not any(x.get('build_id')==a.build_id and not x.get('accounted') for x in ledger['builds']):raise SystemExit('Only own active build may be cancelled')
  invoke(['builds','cancel',a.build_id,'--region=global','--format=json']);print('Cancellation requested; status remains authoritative')


def download(a,item):
 a.output.mkdir(parents=True,exist_ok=False)
 names=['evidence.tar.gz','archive.sha256','summary.json','manifest.json','files-sha256.json','submitted-config.json','upload-complete.json']
 if item.get('publish_text_logs'):names.append('text-logs-index.json')
 subprocess.run(GCLOUD+['storage','cp',*[BUCKET+'/'+a.build_id+'/'+filename for filename in names],str(a.output)+'/'],check=True)
 if a.text_logs:subprocess.run(GCLOUD+['storage','cp','--recursive',BUCKET+'/'+a.build_id+'/text-logs',str(a.output)+'/'],check=True)
 subprocess.run([sys.executable,str(DIR/'verify-evidence.py'),'--directory',str(a.output),'--expected-build-id',a.build_id,'--expected-infra-sha',item['infra_sha'],'--expected-proof-sha',item['proof_sha'],'--expected-config-sha',item['submitted_config_sha256']],check=True)

if __name__=='__main__':main()
