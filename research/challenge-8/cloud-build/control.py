#!/usr/bin/env python3
"""Lightweight VPS orchestration only. Never executes proof tools locally."""
import argparse,base64,datetime,gzip,hashlib,importlib.util,json,math,os,re,subprocess,sys,uuid
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
TERMINAL={'SUCCESS','FAILURE','INTERNAL_ERROR','TIMEOUT','CANCELLED','EXPIRED'}
NIGHT_PHASE='NIGHT-SELECT-SORT4-CLOUD-2026-10-09'
NIGHT_DEADLINE='2026-10-09T08:00:00Z'
DAY_PHASE='DAY-SELECT-SORT4-CLOUD-2026-10-09'
DAY_DEADLINE='2026-10-09T11:15:54Z'
AFTERNOON_PHASE='AFTERNOON-SELECT-SORT4-CLOUD-2026-10-09'
AFTERNOON_DEADLINE='2026-10-09T13:50:06Z'
AFTERNOON_LANES=frozenset(('o26-input-relation-frame-shadow-test','o26-input-relation-frame-shadow-capture','o26-input-relation-frame-test','o26-input-relation-frame-capture','o26-r3-ghost-scope-test','o26-wrapper-r3-nested-diagnostics','o26-input-relation-shadow-capture','o26-generic-sort4-postmark-diagnostics','o26-strict-cut-reuse-false-posts'))
NEXT_SELECT_PHASE='NEXT-SELECT-FRAME-CALLER-CLOUD-2026-10-09'
NEXT_SELECT_START='2026-10-09T14:03:33Z'
NEXT_SELECT_MAIN_DEADLINE='2026-10-09T15:03:33Z'
NEXT_SELECT_DEADLINE='2026-10-09T15:33:33Z'
NEXT_SELECT_LANES=frozenset(('o26-input-relation-frame-shadow-test','o26-select-sort4-first-caller-test'))
C1_PHASE='SORT4-C1-CURRENT-RECOVERY-CLOUD-2026-10-09'
C1_START='2026-10-09T15:08:25Z'
C1_MAIN_DEADLINE='2026-10-09T16:08:25Z'
C1_DEADLINE='2026-10-09T16:38:25Z'
C1_LANES=frozenset(('o26-sort4-c1-current-recovery',))
C1_ACTUAL_PHASE='SORT4-C1-ACTUAL-EXECUTION-CLOUD-2026-10-09'
C1_ACTUAL_START='2026-10-09T16:52:10Z'
C1_ACTUAL_MAIN_DEADLINE='2026-10-09T17:52:10Z'
C1_ACTUAL_DEADLINE='2026-10-09T18:22:10Z'
C1_CALLER_ENTRY_PHASE='SORT4-C1-CALLER-ENTRY-CLOUD-2026-10-09'
C1_CALLER_ENTRY_START='2026-10-09T18:17:12Z'
C1_CALLER_ENTRY_MAIN_DEADLINE='2026-10-09T19:17:12Z'
C1_CALLER_ENTRY_DEADLINE='2026-10-09T19:47:12Z'
C1_CALLER_ENTRY_LANES=frozenset(('o26-sort4-caller-entry',))
C1_BRIDGE_PHASE='SORT4-C1-CALLER-BRIDGE-CLOUD-2026-10-09'
C1_BRIDGE_START='2026-10-09T19:43:08Z'
C1_BRIDGE_MAIN_DEADLINE='2026-10-09T20:43:08Z'
C1_BRIDGE_DEADLINE='2026-10-09T21:13:08Z'
MISSION_PHASE='SORT4-NATIVE-ENTRY-C1-CLOUD-2026-10-10'
MISSION_START='2026-10-09T21:52:33Z'
MISSION_MAIN_DEADLINE='2026-10-09T23:52:33Z'
MISSION_DEADLINE='2026-10-10T00:22:33Z'
MISSION_LANES=frozenset(('o26-sort4-caller-entry','o26-sort4-c1-current-recovery'))
COMPOSE_PHASE='SORT4-NATIVE-COMPOSE-C1-CLOUD-2026-10-10'
COMPOSE_START='2026-10-10T00:34:15Z'
COMPOSE_MAIN_DEADLINE='2026-10-10T02:34:15Z'
COMPOSE_DEADLINE='2026-10-10T03:04:15Z'
COMPOSE_LANES=MISSION_LANES
C3_PREFIX_PHASE='SORT4-C3-PREFIX-CLOUD-2026-10-10'
C3_PREFIX_START='2026-10-10T10:20:59Z'
C3_PREFIX_MAIN_DEADLINE='2026-10-10T12:20:59Z'
C3_PREFIX_DEADLINE='2026-10-10T12:50:59Z'
C3_PREFIX_LANES=frozenset(('o26-sort4-c1-current-recovery','o26-compatible-strict-cut-test'))
NATIVE_C4_PHASE='SORT4-NATIVE-C4-CLOUD-2026-10-10'
NATIVE_C4_START='2026-10-10T13:00:22Z'
NATIVE_C4_MAIN_DEADLINE='2026-10-10T15:00:22Z'
NATIVE_C4_DEADLINE='2026-10-10T15:30:22Z'
NATIVE_C4_LANES=frozenset(('o26-sort4-c1-current-recovery',))
NATIVE_OPAQUE_PHASE='SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10'
NATIVE_OPAQUE_START='2026-10-10T19:27:14Z'
NATIVE_OPAQUE_MAIN_DEADLINE='2026-10-10T21:27:14Z'
NATIVE_OPAQUE_DEADLINE='2026-10-10T21:57:14Z'
NATIVE_OPAQUE_LANES=frozenset(('o26-sort4-c1-current-recovery',))
NATIVE_C1_BOUND_PHASE='SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11'
NATIVE_C1_BOUND_START='2026-10-11T08:33:37Z'
NATIVE_C1_BOUND_MAIN_DEADLINE='2026-10-11T10:33:37Z'
NATIVE_C1_BOUND_DEADLINE='2026-10-11T11:03:37Z'
NATIVE_C1_BOUND_LANES=frozenset(('o26-sort4-c1-current-recovery',))
ACTUAL_CALLER_ENTRY_PHASE='SORT4-ACTUAL-CALLER-ENTRY-CLOUD-2026-10-11'
ACTUAL_CALLER_ENTRY_START='2026-10-11T13:54:02Z'
ACTUAL_CALLER_ENTRY_MAIN_DEADLINE='2026-10-11T15:54:02Z'
ACTUAL_CALLER_ENTRY_DEADLINE='2026-10-11T16:24:02Z'
ACTUAL_CALLER_ENTRY_LANES=frozenset(('o26-sort4-c1-current-recovery',))
CALLER_BOUND_PHASE='SORT4-CALLER-DERIVED-BOUND-CLOUD-2026-10-11'
CALLER_BOUND_START='2026-10-11T16:25:01Z'
CALLER_BOUND_MAIN_DEADLINE='2026-10-11T18:55:01Z'
CALLER_BOUND_DEADLINE='2026-10-11T19:25:01Z'
CALLER_BOUND_LANES=ACTUAL_CALLER_ENTRY_LANES
BINDING_PREFIX_PHASE='SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11'
BINDING_PREFIX_START='2026-10-11T19:22:51Z'
BINDING_PREFIX_MAIN_DEADLINE='2026-10-11T21:22:51Z'
BINDING_PREFIX_DEADLINE='2026-10-11T21:52:51Z'
BINDING_PREFIX_LANES=ACTUAL_CALLER_ENTRY_LANES
BINDING_SESSION2_PHASE='SORT4-COMPILER-BINDING-PREFIX-SESSION2-CLOUD-2026-10-12'
BINDING_SESSION2_START='2026-10-11T21:49:02Z'
BINDING_SESSION2_MAIN_DEADLINE='2026-10-11T23:49:02Z'
BINDING_SESSION2_DEADLINE='2026-10-12T00:19:02Z'
BINDING_SESSION2_LANES=ACTUAL_CALLER_ENTRY_LANES
A1_PHASE='SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17'
A1_START='2026-10-17T09:58:22Z'
A1_MAIN_DEADLINE='2026-10-17T11:58:22Z'
A1_DEADLINE='2026-10-17T12:28:22Z'
A1_LANES=ACTUAL_CALLER_ENTRY_LANES
A1_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-RCG-PROFILE-2026-10-17.json'
A1_FIX_PHASE='SORT4-A1-UNUSED-MUT-FIX-CLOUD-2026-10-18'
A1_FIX_START='2026-10-18T08:37:29Z'
A1_FIX_MAIN_DEADLINE='2026-10-18T10:37:29Z'
A1_FIX_DEADLINE='2026-10-18T11:07:29Z'
A1_FIX_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-RCG-UNUSED-MUT-PROFILE-2026-10-18.json'
A1_TYPE_PHASE='SORT4-A1-OCAML-TYPE-FIX-CLOUD-2026-10-18'
A1_TYPE_START='2026-10-18T14:31:11Z'
A1_TYPE_MAIN_DEADLINE='2026-10-18T16:31:11Z'
A1_TYPE_DEADLINE='2026-10-18T17:01:11Z'
A1_TYPE_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-RCG-OCAML-TYPE-PROFILE-2026-10-18.json'
A1_BUILD_PHASE='SORT4-A1-OCAML-BUILDABILITY-2026-10-18-R1'
A1_BUILD_START='2026-10-18T18:59:16Z'
A1_BUILD_MAIN_DEADLINE='2026-10-18T20:59:16Z'
A1_BUILD_DEADLINE='2026-10-18T21:29:16Z'
A1_BUILD_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-BUILDABILITY-R5-PROFILE-2026-10-18.json'
A1_BUILD_CEILING=18960
A1_PARSER_PHASE='SORT4-P0A-PARSER-COMPATIBILITY-2026-10-19-R2'
A1_UNION_PHASE='SORT4-MAYBEUNINIT-UNION-KIND-2026-10-20-R4'
A1_AUTO_PHASE='SORT4-NATIVE-INTERFACE-AUTONOMOUS-2026-10-20-R5'
A1_PARSER_START='2026-10-19T16:06:59Z'
A1_UNION_START='2026-10-19T21:15:52Z'
A1_AUTO_START='2026-10-19T22:34:09Z'
A1_PARSER_MAIN_DEADLINE='2026-10-19T19:36:59Z'
A1_UNION_MAIN_DEADLINE='2026-10-19T23:15:52Z'
A1_AUTO_MAIN_DEADLINE='2026-10-20T00:34:09Z'
A1_PARSER_DEADLINE='2026-10-19T20:06:59Z'
A1_UNION_DEADLINE='2026-10-19T23:45:52Z'
A1_AUTO_DEADLINE='2026-10-20T01:04:09Z'
A1_PARSER_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-PARSER-D2-PROFILE-2026-10-19.json'
A1_UNION_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-UNION-U2-PROFILE-2026-10-20.json'
A1_AUTO_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-AUTO-S6-PROFILE-2026-10-20.json'
A1_PARSER_CEILING=3600
A1_UNION_CEILING=3600
A1_AUTO_CEILING=3600
A1_SCOPE_PHASE='SORT4-PACKAGE-SCOPE-NATIVE-PROOF-2026-10-20-R6'
A1_SCOPE_START='2026-10-20T07:16:11Z'
A1_SCOPE_MAIN_DEADLINE='2026-10-20T09:16:11Z'
A1_SCOPE_DEADLINE='2026-10-20T09:46:11Z'
A1_SCOPE_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-SCOPE-S3-PROFILE-2026-10-20.json'
A1_SCOPE_CEILING=3600
A1_R7_PHASE='SORT4-PACKAGING-NATIVE-PROOF-2026-10-20-R7'
A1_R7_START='2026-10-20T11:16:28Z'
A1_R7_MAIN_DEADLINE='2026-10-20T13:16:28Z'
A1_R7_DEADLINE='2026-10-20T13:46:28Z'
A1_R7_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-PACKAGING-R7-PROFILE-2026-10-20.json'
A1_R7_CEILING=3600
A1_R8_PHASE='SORT4-POST-MIGRATION-NATIVE-PROOF-2026-10-20-R8'
A1_R8_START='2026-10-20T14:28:47Z'
A1_R8_MAIN_DEADLINE='2026-10-20T16:28:47Z'
A1_R8_DEADLINE='2026-10-20T16:58:47Z'
A1_R8_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-POST-MIGRATION-R8-PROFILE-2026-10-20.json'
A1_R8_CEILING=3600
A1_R9_PHASE='SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9'
A1_R9_START='2026-10-20T17:07:04Z'
A1_R9_MAIN_DEADLINE='2026-10-20T19:07:04Z'
A1_R9_DEADLINE='2026-10-20T19:37:04Z'
A1_R9_PROFILE='research/challenge-8/cloud-build/sort4-caller-entry-native/A1-NATIVE-INTERFACE-R9-PROFILE-2026-10-20.json'
A1_R9_CEILING=3600
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

def envs(infra,proof,lane,phase_id=None):
 phase_env=(['SORT4_NATIVE_C4_PHASE=1','SORT4_NATIVE_C4_PHASE_ID='+NATIVE_C4_PHASE]
            if phase_id==NATIVE_C4_PHASE else
            ['SORT4_NATIVE_OPAQUE_PHASE=1','SORT4_NATIVE_OPAQUE_PHASE_ID='+NATIVE_OPAQUE_PHASE]
            if phase_id==NATIVE_OPAQUE_PHASE else
            ['SORT4_NATIVE_C1_ZST_REPAIR_PHASE=1','SORT4_NATIVE_C1_ZST_REPAIR_PHASE_ID='+NATIVE_C1_BOUND_PHASE]
            if phase_id==NATIVE_C1_BOUND_PHASE else
            ['SORT4_ACTUAL_CALLER_ENTRY_PHASE=1','SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID='+ACTUAL_CALLER_ENTRY_PHASE]
            if phase_id==ACTUAL_CALLER_ENTRY_PHASE else
            ['SORT4_ACTUAL_CALLER_ENTRY_PHASE=1','SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID='+CALLER_BOUND_PHASE]
            if phase_id==CALLER_BOUND_PHASE else
            ['SORT4_ACTUAL_CALLER_ENTRY_PHASE=1','SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID='+BINDING_PREFIX_PHASE]
            if phase_id in (BINDING_PREFIX_PHASE,BINDING_SESSION2_PHASE) else [])
 if phase_id==A1_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_PROFILE],cwd=ROOT)
  phase_env=['SORT4_A1_PHASE_ID='+A1_PHASE,'SORT4_A1_CHECKED_TRAIT_CONTRACT=1',
             'SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_FIX_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_FIX_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_FIX_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 fix authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_FIX_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_TYPE_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_TYPE_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_TYPE_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 fix authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_TYPE_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_BUILD_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_BUILD_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_BUILD_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 fix authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_BUILD_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_PARSER_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_PARSER_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_PARSER_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 fix authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_PARSER_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_UNION_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_UNION_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_UNION_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 fix authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_UNION_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_AUTO_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_AUTO_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_AUTO_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 fix authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_AUTO_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_R7_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_R7_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_R7_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 R7 authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_R7_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_R8_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_R8_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_R8_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 R8 authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_R8_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_R9_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_R9_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_R9_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 R9 authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_R9_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 if phase_id==A1_SCOPE_PHASE:
  profile_bytes=subprocess.check_output(['git','show',proof+':'+A1_SCOPE_PROFILE],cwd=ROOT)
  profile=json.loads(profile_bytes)
  if profile.get('authorization_phase_id')!=A1_SCOPE_PHASE or profile.get('experiment_protocol_phase_id')!=A1_PHASE:raise SystemExit('A1 package-scope authorization/protocol profile binding differs')
  phase_env=['SORT4_A1_AUTHORIZATION_PHASE_ID='+A1_SCOPE_PHASE,'SORT4_A1_PHASE_ID='+A1_PHASE,
             'SORT4_A1_CHECKED_TRAIT_CONTRACT=1','SORT4_A1_PROFILE_SHA256='+digest(profile_bytes)]
 return [f'INFRA_SHA={infra}',f'PROOF_SHA={proof}',f'LANE={lane}',f'PROOF_IMAGE={UBUNTU}','CLOUD_BUILD_ID=${BUILD_ID}','CLOUD_BUILD_PROJECT_ID=${PROJECT_ID}','CLOUD_BUILD_REGION=global','SMALLSORT_EXECUTION_PROVIDER=cloud-build','SUBMITTED_CONFIG_SHA=${_CONFIG_SHA}',] + [f'CONFIG_PART_{i}=${{_CONFIG_{i}}}' for i in range(8)] + phase_env

def config(infra,proof,lane,seconds,token,source_payload=None,phase_id=None):
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
mkdir -p /workspace/cloudsdk/configurations
printf '[core]\\nproject = smallsort-ci\\naccount = ACCOUNT\\n' > /workspace/cloudsdk/configurations/config_smallsort-ci
export CLOUDSDK_CONFIG=/workspace/cloudsdk
printf '%s' PACKAGE_B64 | base64 --decode | gzip --decompress > /workspace/package-evidence.py
rm -f /workspace/upload.ok /workspace/package-upload-error.json
set +e
SDK_PYTHON /workspace/package-evidence.py --evidence /workspace/evidence --out /workspace/out 2> /workspace/packaging-stderr.log
packaging_status=$?
set -e
cat /workspace/packaging-stderr.log >&2
if [ "$packaging_status" -ne 0 ]; then
 SDK_PYTHON - "$packaging_status" <<'PACKAGING_FAILURE'
import json,pathlib,sys
root=pathlib.Path('/workspace')
record={'schema_version':1,'stage':'package-upload','operation':'package-evidence',
        'exit_code':int(sys.argv[1]),'failure_class':'packaging-failed',
        'primary_error':(root/'packaging-stderr.log').read_text(errors='replace'),
        'proof_status':'UNCHANGED'}
# Emit the primary failure even if the final verdict step cannot run. Do not
# follow evidence links or change the package failure / proof verdict.
import stat
sizes={}
for name in ('proof-audit.json','allprooflogs/cases/sort4-c1-current-recovery/diagnostic-audit.json'):
 path=root/'evidence'/name
 try:
  metadata=path.lstat()
  sizes[name]={'kind':'regular' if stat.S_ISREG(metadata.st_mode) else 'nonregular',
               'bytes':metadata.st_size if stat.S_ISREG(metadata.st_mode) else None}
 except FileNotFoundError:
  sizes[name]={'kind':'missing','bytes':None}
 except OSError as error:
  sizes[name]={'kind':'unavailable','bytes':None,'error':type(error).__name__}
view={key:record[key] for key in ('schema_version','stage','operation','exit_code','failure_class','proof_status')}
view.update(primary_error=record['primary_error'][:4096],
            primary_error_truncated=len(record['primary_error'])>4096,audit_sizes=sizes)
print('SMALLSORT_PACKAGING_FAILURE',json.dumps(view,sort_keys=True),file=sys.stderr,flush=True)
try:
 (root/'package-upload-error.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\\n')
except OSError as error:
 print('SMALLSORT_PACKAGING_DIAGNOSTIC_PERSIST_FAILED',type(error).__name__,file=sys.stderr,flush=True)
PACKAGING_FAILURE
 exit "$packaging_status"
fi
prefix="BUCKET/$CLOUD_BUILD_ID"
for file in evidence.tar.gz archive.sha256 summary.json manifest.json files-sha256.json submitted-config.json text-logs-index.json; do
 gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci storage cp --if-generation-match=0 "/workspace/out/$file" "$prefix/$file"
done
gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci storage cp --recursive --if-generation-match=0 /workspace/out/text-logs "$prefix/"
SDK_PYTHON - <<'RECEIPT'
import json,os,pathlib
p=pathlib.Path('/workspace/out')
h=(p/'archive.sha256').read_text().split()[0]
(p/'upload-complete.json').write_text(json.dumps({'build_id':os.environ['CLOUD_BUILD_ID'],'archive_sha256':h,'uploaded':True,'text_logs_index_sha256':__import__('hashlib').sha256((p/'text-logs-index.json').read_bytes()).hexdigest()},indent=2)+'\\n')
RECEIPT
gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci storage cp --if-generation-match=0 /workspace/out/upload-complete.json "$prefix/upload-complete.json"
touch /workspace/upload.ok
'''.replace('ACCOUNT',ACCOUNT).replace('SDK_PYTHON',SDK_PYTHON).replace('PACKAGE_B64','"$PACKAGER_BYTES"').replace('BUCKET',BUCKET).replace('$','$$')
 verdict='''import json,pathlib,sys
p=pathlib.Path('/workspace/out')
failure=pathlib.Path('/workspace/package-upload-error.json')
if failure.exists():
 try:
  record=json.loads(failure.read_text())
  if not isinstance(record,dict):raise ValueError('packaging failure record must be an object')
 except Exception as e:
  record={'stage':'package-upload','failure_class':'packaging-failed','proof_status':'UNCHANGED',
          'diagnostic_error':type(e).__name__+': '+str(e)}
 print('INCOMPLETE_EVIDENCE',json.dumps(record,sort_keys=True))
 sys.exit(2)
if not (p/'summary.json').is_file():
 print('INCOMPLETE_EVIDENCE',json.dumps({'stage':'package-upload','failure_class':'missing-packaging-output',
       'missing':['summary.json'],'proof_status':'UNCHANGED'},sort_keys=True))
 sys.exit(2)
try:
 s=json.loads((p/'summary.json').read_text())
 ok=pathlib.Path('/workspace/upload.ok').is_file() and ((s.get('verification_accepted') is True) or (s.get('smoke_success') is True) or (s.get('diagnostic_complete') is True))
 print('SMALLSORT_FINAL_VERDICT',json.dumps(s,sort_keys=True),'upload_complete=',pathlib.Path('/workspace/upload.ok').is_file(),'verification_accepted=',s.get('verification_accepted'),'diagnostic_complete=',s.get('diagnostic_complete'))
 sys.exit(0 if ok else 1)
except Exception as e:
 print('INCOMPLETE_EVIDENCE',type(e).__name__,str(e));sys.exit(2)
'''
 return {'steps':[{'id':'execute','name':UBUNTU,'entrypoint':'bash','args':['-ceu',body],'env':envs(infra,proof,lane,phase_id)+source_env,'allowFailure':True},{'id':'package-upload','name':SDK,'entrypoint':'bash','args':['-ceu',upload],'env':envs(infra,proof,lane,phase_id)+['PACKAGER_BYTES='+package],'allowFailure':True},{'id':'verdict','name':SDK,'entrypoint':SDK_PYTHON,'args':['-c',verdict]}],'timeout':f'{seconds}s','queueTtl':'60s','options':{'machineType':'E2_STANDARD_2','logging':'CLOUD_LOGGING_ONLY'},'serviceAccount':f'projects/smallsort-ci/serviceAccounts/{ACCOUNT}','tags':['smallsort-cloud-migration',token],'substitutions':{'_CONFIG_SHA':'placeholder',**{f'_CONFIG_{i}':'placeholder' for i in range(8)},**{f'_SOURCE_{i}':part for i,part in enumerate(source_parts)}}}

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
    # Conservative envelope includes queue/preparation/upload, rounded up.
    duration=math.ceil((t(b['finishTime'])-t(b['createTime'])).total_seconds()) if b.get('finishTime') and b.get('createTime') else item['reserved_seconds']
    item['build_seconds']=duration;item['accounted']=True
    if b.get('startTime') and b.get('finishTime'):item['execution_seconds']=math.ceil((t(b['finishTime'])-t(b['startTime'])).total_seconds())
 ledger['used_build_seconds']=sum(x.get('build_seconds',0) for x in ledger['builds'])
 ledger['remaining_build_seconds']=ledger['ceiling_build_seconds']-ledger['used_build_seconds']
 ledger['active_build']=next((x.get('build_id') or x['dispatch_token'] for x in ledger['builds'] if not x.get('accounted')),None)
 write(ledger_path,ledger)


def reconcile_global(caller_owner,caller_ledger):
 """Reconcile both slots without editing another owner's ledger or state."""
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

def status_summary(build):
 # Keep status diagnostics bounded to public Build metadata. In particular,
 # never print step args/env, commands, or log/archive payloads.
 if not isinstance(build,dict):build={}
 top=('id','status','createTime','startTime','finishTime','logUrl','failureInfo')
 out={key:build.get(key) for key in top}
 out['steps']=[]
 steps=build.get('steps')
 if isinstance(steps,list):
  fields=('id','status','exitCode','timing')
  out['steps']=[{key:step.get(key) for key in fields}
                for step in steps if isinstance(step,dict)]
 return out


def authorized_phase(a,ledger):
 if not a.phase_id or not PHASE_PATTERN.fullmatch(a.phase_id) or ledger.get('phase')!=a.phase_id:raise SystemExit('Explicit phase ID must match the selected account')
 if a.phase_id=='CLOUD-BUILD-MIGRATION' or ledger.get('status')!='AUTHORIZED' or not isinstance(ledger.get('authorization'),str) or not ledger['authorization'].strip():raise SystemExit('Phase account is closed or has no explicit authorization')
 if not a.owner or not OWNER_PATTERN.fullmatch(a.owner):raise SystemExit('Explicit valid --owner is required')
 if not isinstance(ledger.get('ceiling_build_seconds'),int) or ledger['ceiling_build_seconds']<=0:raise SystemExit('Invalid phase ceiling')
 if a.phase_id==A1_PHASE and (ledger['ceiling_build_seconds']!=960 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_START or ledger.get('main_deadline_utc')!=A1_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_DEADLINE or ledger.get('maximum_builds')!=1 or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 continuation requires exact new account, owner, window, one Build and lane')
 if a.phase_id==A1_FIX_PHASE and (ledger['ceiling_build_seconds']!=960 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_FIX_START or ledger.get('main_deadline_utc')!=A1_FIX_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_FIX_DEADLINE or ledger.get('maximum_builds')!=1 or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 unused-mut fix requires exact new account, owner, window, one Build and lane')
 if a.phase_id==A1_TYPE_PHASE and (ledger['ceiling_build_seconds']!=960 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_TYPE_START or ledger.get('main_deadline_utc')!=A1_TYPE_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_TYPE_DEADLINE or ledger.get('maximum_builds')!=1 or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 OCaml-type fix requires exact new account, owner, window, one Build and lane')
 if a.phase_id==A1_BUILD_PHASE and (ledger['ceiling_build_seconds']!=A1_BUILD_CEILING or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_BUILD_START or ledger.get('main_deadline_utc')!=A1_BUILD_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_BUILD_DEADLINE or ledger.get('maximum_builds') is not None or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 buildability session requires exact new account, owner, window, sequential Builds and lane')
 if a.phase_id==A1_PARSER_PHASE and (ledger['ceiling_build_seconds']!=A1_PARSER_CEILING or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_PARSER_START or ledger.get('main_deadline_utc')!=A1_PARSER_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_PARSER_DEADLINE or ledger.get('maximum_builds') is not None or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 parser compatibility session requires exact new account, owner, window, sequential Builds and lane')
 if a.phase_id==A1_UNION_PHASE and (ledger['ceiling_build_seconds']!=A1_UNION_CEILING or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_UNION_START or ledger.get('main_deadline_utc')!=A1_UNION_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_UNION_DEADLINE or ledger.get('maximum_builds') is not None or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 MaybeUninit union kind session requires exact new account, owner, window, sequential Builds and lane')
 if a.phase_id==A1_AUTO_PHASE and (ledger['ceiling_build_seconds']!=A1_AUTO_CEILING or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_AUTO_START or ledger.get('main_deadline_utc')!=A1_AUTO_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_AUTO_DEADLINE or ledger.get('maximum_builds') is not None or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 Autonomous native interface session requires exact new account, owner, window, sequential Builds and lane')
 if a.phase_id==A1_R7_PHASE and (ledger['ceiling_build_seconds']!=A1_R7_CEILING or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_R7_START or ledger.get('main_deadline_utc')!=A1_R7_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_R7_DEADLINE or ledger.get('maximum_builds') is not None or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 R7 packaging/native proof session requires exact new account, owner, window, sequential Builds and lane')
 if a.phase_id==A1_R8_PHASE and (ledger['ceiling_build_seconds']!=A1_R8_CEILING or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_R8_START or ledger.get('main_deadline_utc')!=A1_R8_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_R8_DEADLINE or ledger.get('maximum_builds') is not None or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 R8 post-migration native proof session requires exact new account, owner, window, sequential Builds and lane')
 if a.phase_id==A1_R9_PHASE and (ledger['ceiling_build_seconds']!=A1_R9_CEILING or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_R9_START or ledger.get('main_deadline_utc')!=A1_R9_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_R9_DEADLINE or ledger.get('maximum_builds') is not None or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 R9 native interface proof session requires exact new account, owner, window, sequential Builds and lane')
 if a.phase_id==A1_SCOPE_PHASE and (ledger['ceiling_build_seconds']!=A1_SCOPE_CEILING or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=A1_LANES or ledger.get('start_utc')!=A1_SCOPE_START or ledger.get('main_deadline_utc')!=A1_SCOPE_MAIN_DEADLINE or ledger.get('deadline_utc')!=A1_SCOPE_DEADLINE or ledger.get('maximum_builds') is not None or ledger.get('maximum_build_timeout_seconds')!=900):raise SystemExit('A1 package-scope native proof session requires exact new account, owner, window, sequential Builds and lane')
 if a.phase_id==MISSION_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=MISSION_LANES or ledger.get('start_utc')!=MISSION_START or ledger.get('main_deadline_utc')!=MISSION_MAIN_DEADLINE or ledger.get('deadline_utc')!=MISSION_DEADLINE):raise SystemExit('Mission phase requires its exact separate account, owner, window and lanes')
 if a.phase_id==COMPOSE_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=COMPOSE_LANES or ledger.get('start_utc')!=COMPOSE_START or ledger.get('main_deadline_utc')!=COMPOSE_MAIN_DEADLINE or ledger.get('deadline_utc')!=COMPOSE_DEADLINE):raise SystemExit('Composition phase requires its exact separate account, owner, window and lanes')
 if a.phase_id==NATIVE_C4_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=NATIVE_C4_LANES or ledger.get('start_utc')!=NATIVE_C4_START or ledger.get('main_deadline_utc')!=NATIVE_C4_MAIN_DEADLINE or ledger.get('deadline_utc')!=NATIVE_C4_DEADLINE):raise SystemExit('Native C4 phase requires exact separate account, owner, window and lane')
 if a.phase_id==NATIVE_OPAQUE_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=NATIVE_OPAQUE_LANES or ledger.get('start_utc')!=NATIVE_OPAQUE_START or ledger.get('main_deadline_utc')!=NATIVE_OPAQUE_MAIN_DEADLINE or ledger.get('deadline_utc')!=NATIVE_OPAQUE_DEADLINE):raise SystemExit('Native opaque phase requires exact separate account, owner, window and lane')
 if a.phase_id==NATIVE_C1_BOUND_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=NATIVE_C1_BOUND_LANES or ledger.get('start_utc')!=NATIVE_C1_BOUND_START or ledger.get('main_deadline_utc')!=NATIVE_C1_BOUND_MAIN_DEADLINE or ledger.get('deadline_utc')!=NATIVE_C1_BOUND_DEADLINE):raise SystemExit('Native C1 bound phase requires exact separate account, owner, window and lane')
 if a.phase_id==ACTUAL_CALLER_ENTRY_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=ACTUAL_CALLER_ENTRY_LANES or ledger.get('start_utc')!=ACTUAL_CALLER_ENTRY_START or ledger.get('main_deadline_utc')!=ACTUAL_CALLER_ENTRY_MAIN_DEADLINE or ledger.get('deadline_utc')!=ACTUAL_CALLER_ENTRY_DEADLINE):raise SystemExit('Actual caller entry phase requires exact separate account, owner, window and lane')
 if a.phase_id==CALLER_BOUND_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=CALLER_BOUND_LANES or ledger.get('start_utc')!=CALLER_BOUND_START or ledger.get('main_deadline_utc')!=CALLER_BOUND_MAIN_DEADLINE or ledger.get('deadline_utc')!=CALLER_BOUND_DEADLINE):raise SystemExit('Caller derived bound phase requires exact separate account, owner, window and lane')
 if a.phase_id==BINDING_PREFIX_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=BINDING_PREFIX_LANES or ledger.get('start_utc')!=BINDING_PREFIX_START or ledger.get('main_deadline_utc')!=BINDING_PREFIX_MAIN_DEADLINE or ledger.get('deadline_utc')!=BINDING_PREFIX_DEADLINE):raise SystemExit('Compiler binding prefix phase requires exact separate account, owner, window and lane')
 if a.phase_id==BINDING_SESSION2_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=BINDING_SESSION2_LANES or ledger.get('start_utc')!=BINDING_SESSION2_START or ledger.get('main_deadline_utc')!=BINDING_SESSION2_MAIN_DEADLINE or ledger.get('deadline_utc')!=BINDING_SESSION2_DEADLINE):raise SystemExit('Compiler binding session2 phase requires exact separate account, owner, window and lane')
 if a.phase_id==C3_PREFIX_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger.get('allowed_lanes',[]))!=C3_PREFIX_LANES or ledger.get('start_utc')!=C3_PREFIX_START or ledger.get('main_deadline_utc')!=C3_PREFIX_MAIN_DEADLINE or ledger.get('deadline_utc')!=C3_PREFIX_DEADLINE):raise SystemExit('C3 prefix phase requires its exact separate account, owner, window and lane')
 if a.phase_id==NIGHT_PHASE and ledger['ceiling_build_seconds']!=10800:raise SystemExit('Select phase requires its separate 10800-second ceiling')
 if a.phase_id==DAY_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4'):raise SystemExit('Day select phase requires its separate 3600-second account and owner')
 if not isinstance(ledger.get('allowed_lanes'),list):raise SystemExit('Phase account needs an explicit lane allowlist')
 if a.phase_id==C1_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger['allowed_lanes'])!=C1_LANES or ledger.get('start_utc')!=C1_START or ledger.get('main_deadline_utc')!=C1_MAIN_DEADLINE or ledger.get('deadline_utc')!=C1_DEADLINE):raise SystemExit('C1 phase requires its exact separate account, owner, window and lane')
 if a.phase_id==C1_ACTUAL_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger['allowed_lanes'])!=C1_LANES or ledger.get('start_utc')!=C1_ACTUAL_START or ledger.get('main_deadline_utc')!=C1_ACTUAL_MAIN_DEADLINE or ledger.get('deadline_utc')!=C1_ACTUAL_DEADLINE):raise SystemExit('Actual C1 phase requires its exact separate account, owner, window and lane')
 if a.phase_id==C1_CALLER_ENTRY_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger['allowed_lanes'])!=C1_CALLER_ENTRY_LANES or ledger.get('start_utc')!=C1_CALLER_ENTRY_START or ledger.get('main_deadline_utc')!=C1_CALLER_ENTRY_MAIN_DEADLINE or ledger.get('deadline_utc')!=C1_CALLER_ENTRY_DEADLINE):raise SystemExit('C1 caller-entry phase requires its exact separate account, owner, window and lane')
 if a.phase_id==C1_BRIDGE_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or set(ledger['allowed_lanes'])!=C1_CALLER_ENTRY_LANES or ledger.get('start_utc')!=C1_BRIDGE_START or ledger.get('main_deadline_utc')!=C1_BRIDGE_MAIN_DEADLINE or ledger.get('deadline_utc')!=C1_BRIDGE_DEADLINE):raise SystemExit('C1 caller-bridge phase requires its exact separate account, owner, window and lane')
 if a.phase_id==AFTERNOON_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or not set(ledger['allowed_lanes'])<=AFTERNOON_LANES):raise SystemExit('Afternoon select phase requires its separate 3600-second account, exact owner and approved lanes')
 if a.phase_id==NEXT_SELECT_PHASE and (ledger['ceiling_build_seconds']!=3600 or a.owner!='select-sort4' or ledger.get('owner')!='select-sort4' or not set(ledger['allowed_lanes'])<=NEXT_SELECT_LANES or ledger.get('start_utc')!=NEXT_SELECT_START or ledger.get('main_deadline_utc')!=NEXT_SELECT_MAIN_DEADLINE):raise SystemExit('Next select phase requires its exact separate account, owner, window and lanes')
 try:deadline=datetime.datetime.fromisoformat(ledger['deadline_utc'].replace('Z','+00:00'))
 except (KeyError,AttributeError,ValueError) as error:raise SystemExit('Invalid phase deadline') from error
 cutoff=datetime.datetime.fromisoformat((A1_R9_DEADLINE if a.phase_id==A1_R9_PHASE else A1_R8_DEADLINE if a.phase_id==A1_R8_PHASE else A1_R7_DEADLINE if a.phase_id==A1_R7_PHASE else A1_SCOPE_DEADLINE if a.phase_id==A1_SCOPE_PHASE else A1_AUTO_DEADLINE if a.phase_id==A1_AUTO_PHASE else A1_UNION_DEADLINE if a.phase_id==A1_UNION_PHASE else A1_PARSER_DEADLINE if a.phase_id==A1_PARSER_PHASE else A1_BUILD_DEADLINE if a.phase_id==A1_BUILD_PHASE else A1_TYPE_DEADLINE if a.phase_id==A1_TYPE_PHASE else A1_FIX_DEADLINE if a.phase_id==A1_FIX_PHASE else A1_DEADLINE if a.phase_id==A1_PHASE else BINDING_SESSION2_DEADLINE if a.phase_id==BINDING_SESSION2_PHASE else BINDING_PREFIX_DEADLINE if a.phase_id==BINDING_PREFIX_PHASE else CALLER_BOUND_DEADLINE if a.phase_id==CALLER_BOUND_PHASE else ACTUAL_CALLER_ENTRY_DEADLINE if a.phase_id==ACTUAL_CALLER_ENTRY_PHASE else NATIVE_C1_BOUND_DEADLINE if a.phase_id==NATIVE_C1_BOUND_PHASE else NATIVE_OPAQUE_DEADLINE if a.phase_id==NATIVE_OPAQUE_PHASE else NATIVE_C4_DEADLINE if a.phase_id==NATIVE_C4_PHASE else C3_PREFIX_DEADLINE if a.phase_id==C3_PREFIX_PHASE else COMPOSE_DEADLINE if a.phase_id==COMPOSE_PHASE else MISSION_DEADLINE if a.phase_id==MISSION_PHASE else C1_BRIDGE_DEADLINE if a.phase_id==C1_BRIDGE_PHASE else C1_CALLER_ENTRY_DEADLINE if a.phase_id==C1_CALLER_ENTRY_PHASE else C1_ACTUAL_DEADLINE if a.phase_id==C1_ACTUAL_PHASE else C1_DEADLINE if a.phase_id==C1_PHASE else NEXT_SELECT_DEADLINE if a.phase_id==NEXT_SELECT_PHASE else AFTERNOON_DEADLINE if a.phase_id==AFTERNOON_PHASE else DAY_DEADLINE if a.phase_id==DAY_PHASE else NIGHT_DEADLINE).replace('Z','+00:00'))
 if a.phase_id in (A1_PHASE,A1_FIX_PHASE,A1_TYPE_PHASE,A1_BUILD_PHASE,A1_PARSER_PHASE,A1_UNION_PHASE,A1_AUTO_PHASE,A1_SCOPE_PHASE,A1_R7_PHASE,A1_R8_PHASE,A1_R9_PHASE) and deadline!=cutoff:raise SystemExit('A1 requires exact absolute deadline')
 if deadline.tzinfo is None or deadline>cutoff:raise SystemExit('Phase deadline exceeds its authorized cutoff')
 if a.phase_id==DAY_PHASE and deadline!=cutoff:raise SystemExit('Day select phase requires its exact absolute deadline')
 if a.phase_id==AFTERNOON_PHASE and deadline!=cutoff:raise SystemExit('Afternoon select phase requires its exact absolute deadline')
 if a.phase_id==NEXT_SELECT_PHASE and deadline!=cutoff:raise SystemExit('Next select phase requires its exact absolute deadline')
 if a.phase_id==NATIVE_C4_PHASE and deadline!=cutoff:raise SystemExit('Native C4 phase requires exact absolute deadline')
 if a.phase_id==NATIVE_OPAQUE_PHASE and deadline!=cutoff:raise SystemExit('Native opaque phase requires exact absolute deadline')
 if a.phase_id==NATIVE_C1_BOUND_PHASE and deadline!=cutoff:raise SystemExit('Native C1 bound phase requires exact absolute deadline')
 if a.phase_id==ACTUAL_CALLER_ENTRY_PHASE and deadline!=cutoff:raise SystemExit('Actual caller entry phase requires exact absolute deadline')
 if a.phase_id==CALLER_BOUND_PHASE and deadline!=cutoff:raise SystemExit('Caller derived bound phase requires exact absolute deadline')
 if a.phase_id==BINDING_PREFIX_PHASE and deadline!=cutoff:raise SystemExit('Compiler binding prefix phase requires exact absolute deadline')
 if a.phase_id==BINDING_SESSION2_PHASE and deadline!=cutoff:raise SystemExit('Compiler binding session2 phase requires exact absolute deadline')
 if a.phase_id==C3_PREFIX_PHASE and deadline!=cutoff:raise SystemExit('C3 prefix phase requires its exact absolute deadline')
 if a.phase_id==C1_BRIDGE_PHASE and deadline!=cutoff:raise SystemExit('C1 caller-bridge phase requires exact absolute deadline')
 if a.phase_id==C1_CALLER_ENTRY_PHASE and deadline!=cutoff:raise SystemExit('C1 caller-entry phase requires its exact absolute deadline')
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
  if a.phase_id==A1_BUILD_PHASE:
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_BUILD_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Buildability main window ended; no new Build')
   if not 90<=a.timeout<=900:raise SystemExit('Buildability timeout must be90..900 seconds')
  if a.phase_id==A1_PARSER_PHASE:
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_PARSER_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Parser compatibility main window ended; no new Build')
   if not 90<=a.timeout<=900:raise SystemExit('Parser compatibility timeout must be90..900 seconds')
  if a.phase_id==A1_UNION_PHASE:
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_UNION_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('MaybeUninit union kind main window ended; no new Build')
   if not 90<=a.timeout<=900:raise SystemExit('MaybeUninit union kind timeout must be90..900 seconds')
  if a.phase_id==A1_AUTO_PHASE:
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_AUTO_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Autonomous native interface main window ended; no new Build')
   if not 90<=a.timeout<=900:raise SystemExit('Autonomous native interface timeout must be90..900 seconds')
  if a.phase_id in (A1_R7_PHASE,A1_R8_PHASE,A1_R9_PHASE):
   main_deadline=A1_R9_MAIN_DEADLINE if a.phase_id==A1_R9_PHASE else A1_R8_MAIN_DEADLINE if a.phase_id==A1_R8_PHASE else A1_R7_MAIN_DEADLINE
   label='R9' if a.phase_id==A1_R9_PHASE else 'R8' if a.phase_id==A1_R8_PHASE else 'R7'
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(main_deadline.replace('Z','+00:00')):raise SystemExit(f'A1 {label} main window ended; no new Build')
   if not 90<=a.timeout<=900:raise SystemExit(f'A1 {label} timeout must be90..900 seconds')
  if a.phase_id==A1_SCOPE_PHASE:
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_SCOPE_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Package-scope native proof main window ended; no new Build')
   if not 90<=a.timeout<=900:raise SystemExit('Package-scope native proof timeout must be90..900 seconds')
  if a.phase_id in (A1_PHASE,A1_FIX_PHASE,A1_TYPE_PHASE):
   phase_main=A1_TYPE_MAIN_DEADLINE if a.phase_id==A1_TYPE_PHASE else A1_FIX_MAIN_DEADLINE if a.phase_id==A1_FIX_PHASE else A1_MAIN_DEADLINE
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(phase_main.replace('Z','+00:00')):raise SystemExit('A1 main window ended; no new Build')
   if a.timeout!=900 or len(ledger.get('builds',[]))>=1:raise SystemExit('A1 allows one Build, timeout 900 seconds, no automatic retry')
  if a.lane not in ledger.get('allowed_lanes',[]):raise SystemExit('Lane is not approved in the phase account')
  if not LANE_PATTERN.fullmatch(a.lane):raise SystemExit('Invalid lane name')
  if a.source_mode!='pinned-objects':raise SystemExit('New phase requires pinned Git objects')
  now=datetime.datetime.now(datetime.timezone.utc)
  if a.phase_id==COMPOSE_PHASE and now>=datetime.datetime.fromisoformat(COMPOSE_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Composition main window ended; no new experiment')
  if a.phase_id==NATIVE_C4_PHASE and now>=datetime.datetime.fromisoformat(NATIVE_C4_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Native C4 main window ended; no new experiment')
  if a.phase_id==NATIVE_OPAQUE_PHASE and now>=datetime.datetime.fromisoformat(NATIVE_OPAQUE_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Native opaque main window ended; no new experiment')
  if a.phase_id==NATIVE_C1_BOUND_PHASE and now>=datetime.datetime.fromisoformat(NATIVE_C1_BOUND_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Native C1 bound main window ended; no new experiment')
  if a.phase_id==ACTUAL_CALLER_ENTRY_PHASE and now>=datetime.datetime.fromisoformat(ACTUAL_CALLER_ENTRY_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Actual caller entry main window ended; no new experiment')
  if a.phase_id==CALLER_BOUND_PHASE and now>=datetime.datetime.fromisoformat(CALLER_BOUND_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Caller derived bound main window ended; no new experiment')
  if a.phase_id==BINDING_PREFIX_PHASE and now>=datetime.datetime.fromisoformat(BINDING_PREFIX_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Compiler binding prefix main window ended; no new experiment')
  if a.phase_id==BINDING_SESSION2_PHASE and now>=datetime.datetime.fromisoformat(BINDING_SESSION2_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Compiler binding session2 main window ended; no new experiment')
  if a.phase_id==C3_PREFIX_PHASE and now>=datetime.datetime.fromisoformat(C3_PREFIX_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('C3 prefix main window ended; no new experiment')
  if a.phase_id==MISSION_PHASE and now>=datetime.datetime.fromisoformat(MISSION_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Mission main window ended; no new experiment')
  if a.phase_id==C1_ACTUAL_PHASE and now>=datetime.datetime.fromisoformat(C1_ACTUAL_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Actual C1 main window ended; no new experiment')
  if a.phase_id==C1_BRIDGE_PHASE and now>=datetime.datetime.fromisoformat(C1_BRIDGE_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('C1 caller-bridge main window ended; no new experiment')
  if a.phase_id==C1_CALLER_ENTRY_PHASE and now>=datetime.datetime.fromisoformat(C1_CALLER_ENTRY_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('C1 caller-entry main window ended; no new experiment')
  if now+datetime.timedelta(seconds=a.timeout+60)>deadline:raise SystemExit('Timeout plus queue reserve exceeds phase deadline')
  coordination.request(a.owner,a.phase_id,ledger_path,ledger['deadline_utc'])
  # Requests are informational. One slot per owner provides isolation without
  # making an idle/pending peer serialize the other owner's work.
  for sha in [a.infra_sha,a.proof_sha]:
   if not re.fullmatch('[0-9a-f]{40}',sha):raise SystemExit('Full published SHA required')
   subprocess.run(['git','cat-file','-e',sha+'^{commit}'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for name in ['control.py','coordination.py','package-evidence.py','source-input.py']:
   expected=subprocess.check_output(['git','show',a.infra_sha+':research/challenge-8/cloud-build/'+name],cwd=ROOT)
   if expected!=(DIR/name).read_bytes():raise SystemExit('Uncommitted/local '+name+' differs from infrastructure SHA; publish first')
  ongoing=invoke(['builds','list','--region=global','--ongoing','--format=json'])
  if ledger['active_build']:raise SystemExit('Own queued/active or unresolved build: monitor/reconcile first')
  coordination.require_capacity(a.owner,ledger_path,ongoing or [])
  if a.phase_id==A1_BUILD_PHASE:
   records=coordination.reservations()
   occupied=len(records)+sum(not any(x.get('build_id')==b['id'] or x['dispatch_token'] in b.get('tags',[]) for x in records) for b in ongoing or [])
   if occupied>=2:raise SystemExit('Buildability owner restriction: maximum2 occupied project slots')
  if a.phase_id==A1_PARSER_PHASE:
   records=coordination.reservations()
   occupied=len(records)+sum(not any(x.get('build_id')==b['id'] or x['dispatch_token'] in b.get('tags',[]) for x in records) for b in ongoing or [])
   if occupied>=2:raise SystemExit('Buildability owner restriction: maximum2 occupied project slots')
  if a.phase_id==A1_UNION_PHASE:
   records=coordination.reservations()
   occupied=len(records)+sum(not any(x.get('build_id')==b['id'] or x['dispatch_token'] in b.get('tags',[]) for x in records) for b in ongoing or [])
   if occupied>=2:raise SystemExit('Buildability owner restriction: maximum2 occupied project slots')
  if a.phase_id in (A1_AUTO_PHASE,A1_SCOPE_PHASE,A1_R7_PHASE,A1_R8_PHASE,A1_R9_PHASE):
   records=coordination.reservations()
   occupied=len(records)+sum(not any(x.get('build_id')==b['id'] or x['dispatch_token'] in b.get('tags',[]) for x in records) for b in ongoing or [])
   if occupied>=2:raise SystemExit('A1 owner restriction: maximum2 occupied project slots')
  # queue envelope is reserved too, respecting phase/per-build ceiling.
  if not 90<=a.timeout<=1740 or a.timeout+60>1800 or a.timeout+60>ledger['remaining_build_seconds']:raise SystemExit('Invalid timeout or insufficient phase budget (60s queue reserve included)')
  token='dispatch-'+uuid.uuid4().hex
  source_payload=None
  if a.source_mode=='pinned-objects':
   sys.dont_write_bytecode=True
   spec=importlib.util.spec_from_file_location('source_input',DIR/'source-input.py')
   module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
   source_payload=module.make_payload(ROOT,a.infra_sha,a.proof_sha,a.lane)
  cfg=config(a.infra_sha,a.proof_sha,a.lane,a.timeout,token,source_payload,a.phase_id)
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
  # Source transport can be slow on the shared VPS; never reserve/dispatch a
  # native-C4 experiment after its main window even if preflight began earlier.
  if a.phase_id==NATIVE_C4_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(NATIVE_C4_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Native C4 main window ended during preflight; no new Build')
  if a.phase_id==NATIVE_OPAQUE_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(NATIVE_OPAQUE_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Native opaque main window ended during preflight; no new Build')
  if a.phase_id==NATIVE_C1_BOUND_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(NATIVE_C1_BOUND_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Native C1 bound main window ended during preflight; no new Build')
  if a.phase_id==ACTUAL_CALLER_ENTRY_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(ACTUAL_CALLER_ENTRY_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Actual caller entry main window ended during preflight; no new Build')
  if a.phase_id==CALLER_BOUND_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(CALLER_BOUND_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Caller derived bound main window ended during preflight; no new Build')
  if a.phase_id==BINDING_PREFIX_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(BINDING_PREFIX_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Compiler binding prefix main window ended during preflight; no new Build')
  if a.phase_id==A1_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('A1 main window ended during preflight; no new Build')
  if a.phase_id==A1_FIX_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_FIX_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('A1 fix main window ended during preflight; no new Build')
  if a.phase_id==A1_TYPE_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_TYPE_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('A1 fix main window ended during preflight; no new Build')
  if a.phase_id==A1_BUILD_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_BUILD_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('A1 fix main window ended during preflight; no new Build')
  if a.phase_id==A1_PARSER_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_PARSER_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('A1 fix main window ended during preflight; no new Build')
  if a.phase_id==A1_UNION_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_UNION_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('A1 fix main window ended during preflight; no new Build')
  if a.phase_id==A1_AUTO_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_AUTO_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('A1 fix main window ended during preflight; no new Build')
  if a.phase_id in (A1_R7_PHASE,A1_R8_PHASE,A1_R9_PHASE):
   main_deadline=A1_R9_MAIN_DEADLINE if a.phase_id==A1_R9_PHASE else A1_R8_MAIN_DEADLINE if a.phase_id==A1_R8_PHASE else A1_R7_MAIN_DEADLINE
   label='R9' if a.phase_id==A1_R9_PHASE else 'R8' if a.phase_id==A1_R8_PHASE else 'R7'
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(main_deadline.replace('Z','+00:00')):raise SystemExit(f'A1 {label} main window ended during preflight; no new Build')
  if a.phase_id==A1_SCOPE_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(A1_SCOPE_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('A1 package-scope main window ended during preflight; no new Build')
  if a.phase_id==BINDING_SESSION2_PHASE and datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(BINDING_SESSION2_MAIN_DEADLINE.replace('Z','+00:00')):raise SystemExit('Compiler binding session2 main window ended during preflight; no new Build')
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
   b=invoke(['builds','describe',a.build_id,'--region=global','--format=json']);print(json.dumps(status_summary(b),indent=2))
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
