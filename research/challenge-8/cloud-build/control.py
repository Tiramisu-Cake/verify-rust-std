#!/usr/bin/env python3
"""Lightweight VPS orchestration only. Never executes proof tools locally."""
import argparse,ast,base64,datetime,gzip,hashlib,importlib.util,json,math,os,re,subprocess,sys,uuid
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

def required_upload_guard(phase):return phase in ('MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21','MERGE-PUBLICATION-GATE-PROOF-R14-2026-10-21')

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
 # Resolve exactly the same closure as the pinned-object source transport.
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
 # The explicit mode card must change commits. Everything it can execute,
 # including the uploader and the recipe selection, must remain identical.
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
  raise SystemExit('R14 prior-publication gate has missing or mismatched required fields')
 for key in ('exact_archive_size_observed','sidecar_verified','parallel_composite_upload_enabled',
             'proof_attempted','verification_accepted','archive_inventory_verified',
             'publication_verified','mandatory_guard_path_verified'):
  if type(gate.get(key)) is not bool:
   raise SystemExit('R14 prior-publication gate has a non-boolean control field')
 if type(gate.get('archive_size_bytes')) is not type(None) or type(gate.get('independent_proof_credit')) is not int:
  raise SystemExit('R14 prior-publication gate has invalid unknown-size or credit typing')
 if type(gate.get('archive_limit_bytes')) is not int or type(gate.get('threshold_bytes')) is not int:
  raise SystemExit('R14 prior-publication gate has invalid size-bound typing')
 steps=gate.get('cloud_steps_success')
 if (not isinstance(steps,dict) or set(steps)!={'execute','package-upload','verdict'} or
     any(value is not True for value in steps.values())):
  raise SystemExit('R14 prior-publication gate does not bind success of all three Cloud steps')
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
  raise SystemExit('R14 gate lacks the exact fresh Brief/policy/config/coverage observations')
 for key in ('catalogue_complete','policy_exact','policy_complete','policy_source_and_build_match',
             'archived_submitted_config_sha256_matches','historical_R13_records_modified','old_probe_charged_to_R14'):
  if type(coverage.get(key)) is not bool:
   raise SystemExit('R14 gate coverage contains a non-boolean identity claim')
 if type(coverage.get('catalogue_members')) is not int:
  raise SystemExit('R14 gate catalogue member count has invalid typing')
 observed=coverage.get('observed_utc')
 try:
  observed_time=datetime.datetime.fromisoformat(observed.replace('Z','+00:00')) if isinstance(observed,str) else None
 except ValueError:
  observed_time=None
 if (observed_time is None or observed_time.tzinfo is None or
     observed_time<datetime.datetime.fromisoformat('2026-10-21T12:52:50+00:00') or
     observed_time>datetime.datetime.now(datetime.timezone.utc)):
  raise SystemExit('R14 gate coverage lacks a fresh post-T0 observation timestamp')


def r14_read_selected_gate(proof_sha):
 if not isinstance(proof_sha,str) or not re.fullmatch('[0-9a-f]{40}',proof_sha):
  raise SystemExit('R14 proof source must be a full selected commit SHA')
 try:
  selected=subprocess.check_output(['git','show',proof_sha+':'+R14_GATE_PATH],cwd=ROOT,stderr=subprocess.PIPE)
  target=ROOT/R14_GATE_PATH
  if target.is_symlink() or not target.is_file():raise ValueError('publication gate is not a regular file')
  worktree=target.read_bytes()
  gate=json.loads(selected)
 except (subprocess.CalledProcessError,OSError,ValueError,UnicodeDecodeError):
  raise SystemExit('R14 selected source lacks a readable publication gate')
 if selected!=worktree:
  raise SystemExit('R14 publication gate differs from its selected committed source')
 r14_validate_gate_record(gate)
 return gate


def r14_validate_runtime_maps(before,after,expected_additions):
 if set(expected_additions)!={R14_GATE_PATH,R14_LEDGER_PATH,
     'research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py'}:
  raise SystemExit('R14 registration allowlist differs from the reviewed path set')
 ignore={R14_GATE_PATH,R14_LEDGER_PATH,
         'research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py',
         R14_R13_LEDGER_PATH,
         'research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json',
         'research/challenge-8/cloud-build/recipes/merge.json'}
 control_path='research/challenge-8/cloud-build/control.py'
 before_paths=set(before)-ignore;after_paths=set(after)-ignore
 if before_paths!=after_paths:
  raise SystemExit('R14 changed or removed non-registration runtime closure paths')
 for path in sorted(before_paths-{control_path}):
  if before[path]!=after[path]:raise SystemExit('R14 changed a publisher/runtime input: '+path)
 if control_path not in before_paths:
  raise SystemExit('R14 source closure does not include control.py')
 if before[control_path][:2]!=after[control_path][:2] or before[control_path][0] not in ('100644','100755'):
  raise SystemExit('R14 control.py mode/kind changed outside the phase authorization delta')


def r14_validate_historical_ledger(probe_entry,proof_entry,checkpoint_entry):
 if (not all(isinstance(item,tuple) and len(item)==3 for item in (probe_entry,proof_entry,checkpoint_entry)) or
     proof_entry!=checkpoint_entry or checkpoint_entry[:2]!=('100644','blob')):
  raise SystemExit('R14 does not preserve the exact closed R13 account snapshot')


def r14_validate_recipe_delta(before_recipe,after_recipe,expected_additions):
 if not isinstance(before_recipe,dict) or not isinstance(after_recipe,dict):
  raise SystemExit('R14 recipes must be JSON objects')
 before_paths=before_recipe.get('proof_paths');after_paths=after_recipe.get('proof_paths')
 if (not isinstance(before_paths,list) or not isinstance(after_paths,list) or
     before_paths!=sorted(set(before_paths)) or after_paths!=sorted(set(after_paths))):
  raise SystemExit('R14 proof recipe paths are not canonical')
 before_body={key:value for key,value in before_recipe.items() if key!='proof_paths'}
 after_body={key:value for key,value in after_recipe.items() if key!='proof_paths'}
 if before_body!=after_body:
  raise SystemExit('R14 changed a source-input recipe field outside proof_paths')
 if set(after_paths)-set(before_paths)!=set(expected_additions) or set(before_paths)-set(after_paths):
  raise SystemExit('R14 recipe delta differs from the exact registration paths')


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
  raise SystemExit('R14 mode transition must preserve the synthetic probe and select the exact proof-r11 card')


def r14_validate_publisher_control(before_control,after_control):
 tree=ast.parse(after_control); baseline=ast.parse(before_control)
 def segment(parsed,text,name):
  node=next((n for n in parsed.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
  return ast.get_source_segment(text,node) if node else None
 # The probe commit is pinned; exact function-source equality preserves its
 # reviewed fail-closed guard, policy, upload order and marker-last behavior.
 if any(segment(baseline,before_control,n)!=segment(tree,after_control,n)
        for n in ('envs','config')):
  raise SystemExit('R14 changed the exact R13 Cloud config producer or upload command')
 expected="def required_upload_guard(phase):return phase in ('MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21','MERGE-PUBLICATION-GATE-PROOF-R14-2026-10-21')"
 if segment(tree,after_control,'required_upload_guard')!=expected:
  raise SystemExit('R14 does not enable the mandatory mode-card guard on exactly R13 and R14')
 command=segment(tree,after_control,'run_command') or ''
 if 'r13_required=required_upload_guard(a.phase_id)' not in command:
  raise SystemExit('R14 submit path does not pass the selected phase guard marker into config')
 def assignments(parsed):
  return {t.id:ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign)
          for t in n.targets if isinstance(t,ast.Name) and t.id in {'BUCKET','UBUNTU','SDK','ACCOUNT','SDK_PYTHON'}}
 if assignments(baseline)!=assignments(tree) or len(assignments(baseline))!=5:
  raise SystemExit('R14 changed a publisher image/account/bucket constant')


def r14_validate_retry_sources(probe_sha,proof_sha):
 """Require only the R14 registration delta around the exact R13 publisher."""
 expected_additions={R14_GATE_PATH,R14_LEDGER_PATH,
  'research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py'}
 recipe_path='research/challenge-8/cloud-build/recipes/merge.json'
 mode_path='research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json'
 try:
  before_recipe_raw=subprocess.check_output(['git','show',probe_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  after_recipe_raw=subprocess.check_output(['git','show',proof_sha+':'+recipe_path],cwd=ROOT,stderr=subprocess.PIPE)
  before_recipe=json.loads(before_recipe_raw);after_recipe=json.loads(after_recipe_raw)
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R14 could not read the exact probe and proof recipes')
 r14_validate_recipe_delta(before_recipe,after_recipe,expected_additions)
 try:
  before_card=json.loads(subprocess.check_output(['git','show',probe_sha+':'+mode_path],cwd=ROOT,stderr=subprocess.PIPE))
  after_card=json.loads(subprocess.check_output(['git','show',proof_sha+':'+mode_path],cwd=ROOT,stderr=subprocess.PIPE))
 except (subprocess.CalledProcessError,ValueError,UnicodeDecodeError):
  raise SystemExit('R14 source lacks a readable mode card')
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
    raise SystemExit('R14 runtime closure contains a non-regular source input')
   found[path.decode()]=(mode,kind,oid)
  if set(found)!=set(paths):raise SystemExit('R14 runtime source closure is incomplete')
  return found
 before=inventory(probe_sha,before_recipe,before_recipe_raw)
 after=inventory(proof_sha,after_recipe,after_recipe_raw)
 if before.get(mode_path,('',))[0:2]!=('100644','blob') or after.get(mode_path,('',))[0:2]!=('100644','blob'):
  raise SystemExit('R14 mode card must remain a regular non-executable source input')
 checkpoint_raw=subprocess.check_output(['git','ls-tree','-r','-z',R14_CLOSED_R13_CHECKPOINT,'--',R14_R13_LEDGER_PATH],cwd=ROOT,stderr=subprocess.PIPE)
 checkpoint_entries=[]
 for record in checkpoint_raw.split(b'\0'):
  if record:
   meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
   checkpoint_entries.append((path.decode(),(mode,kind,oid)))
 if len(checkpoint_entries)!=1 or checkpoint_entries[0][0]!=R14_R13_LEDGER_PATH:
  raise SystemExit('R14 closed R13 checkpoint does not contain the exact account file')
 r14_validate_historical_ledger(before.get(R14_R13_LEDGER_PATH),after.get(R14_R13_LEDGER_PATH),checkpoint_entries[0][1])
 try:
  current_historical=(ROOT/R14_R13_LEDGER_PATH).read_bytes()
  checkpoint_historical=subprocess.check_output(['git','show',R14_CLOSED_R13_CHECKPOINT+':'+R14_R13_LEDGER_PATH],cwd=ROOT,stderr=subprocess.PIPE)
 except (OSError,subprocess.CalledProcessError):
  raise SystemExit('R14 cannot verify the read-only closed R13 account snapshot')
 if current_historical!=checkpoint_historical:
  raise SystemExit('R14 working tree changed the closed R13 account snapshot')
 ignore={recipe_path,mode_path}|expected_additions
 r14_validate_runtime_maps(before,after,expected_additions)
 # The command generator is allowed to gain phase authorization, but the
 # emitted Cloud config and its identity-bearing constants must remain exact.
 control_path='research/challenge-8/cloud-build/control.py'
 def git_bytes(commit,path):
  return subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT,stderr=subprocess.PIPE)
 before_control=git_bytes(probe_sha,control_path).decode('utf-8')
 after_control=git_bytes(proof_sha,control_path).decode('utf-8')
 r14_validate_publisher_control(before_control,after_control)


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
   raise SystemExit('R14 differs from its exact publication-gate proof authorization')
  cutoff=datetime.datetime.fromisoformat('2026-10-21T15:22:50+00:00')
  now=datetime.datetime.now(datetime.timezone.utc)
  if now<datetime.datetime.fromisoformat(ledger['start_utc'].replace('Z','+00:00')):
   raise SystemExit('R14 proof window has not started')
  if a.command in ('submit','request') and now>=datetime.datetime.fromisoformat(ledger['main_deadline_utc'].replace('Z','+00:00')):
   raise SystemExit('R14 main window passed; no new dispatch/request')
  if a.command=='submit':
   if (type(a.timeout) is not int or not 90<=a.timeout<=1200 or a.lane!='merge' or
       a.source_mode!='pinned-objects' or a.infra_sha!=a.proof_sha):
    raise SystemExit('R14 requires one exact pinned infra/proof source, merge lane, timeout90..1200')
   if now+datetime.timedelta(seconds=a.timeout+60)>cutoff:
    raise SystemExit('R14 Build plus queue reserve exceeds the absolute deadline')
   if r13_upload_mode(a.proof_sha)!='proof-r11':
    raise SystemExit('R14 proof retry requires the exact R11 normal-proof mode')
   r14_read_selected_gate(a.proof_sha)
   r14_validate_retry_sources(R14_PROBE_SOURCE,a.proof_sha)
 if a.phase_id=='CI-IAM-E2E-ONCE-2026-10-17':
  # Separate, explicitly activated account; never reuse a historical ledger.
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
   # The dispatcher persists DISPATCH_PENDING before its only API submit call.
   # Even a definitive API rejection consumes this account's single attempt.
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
  # queue envelope is reserved too, respecting phase/per-build ceiling.
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
  # Recheck the time-window account after source/config preparation, before reserve.
  if a.phase_id in ('MERGE-FIRST-COMPARATOR-R1-2026-10-18','MERGE-FIRST-COMPARATOR-R2-2026-10-19','MERGE-FIRST-COMPARATOR-R3-2026-10-19','MERGE-GUARD-ADDRESSABILITY-R4-2026-10-20','MERGE-CURRENT-OWNERSHIP-R5-2026-10-20','MERGE-CANONICAL-SHARE-R6-2026-10-20','MERGE-POST-MIGRATION-CURRENT-RECOVERY-R7-2026-10-20','MERGE-LATE-RECOVERY-REJOIN-R8-2026-10-20','MERGE-GUARD-CURRENT-RETURN-R9-2026-10-20','MERGE-MOVING-GAP-INVARIANT-R10-2026-10-21','MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21','MERGE-R11-EVIDENCE-RETRY-2026-10-21','MERGE-UPLOAD-NONCOMPOSITE-R12-2026-10-21',R14_PHASE,'MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21'):authorized_phase(a,ledger)
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
