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

def envs(infra,proof,lane):return [f'INFRA_SHA={infra}',f'PROOF_SHA={proof}',f'LANE={lane}',f'PROOF_IMAGE={UBUNTU}','CLOUD_BUILD_ID=${BUILD_ID}','CLOUD_BUILD_PROJECT_ID=${PROJECT_ID}','CLOUD_BUILD_REGION=global','SMALLSORT_EXECUTION_PROVIDER=cloud-build','SUBMITTED_CONFIG_SHA=${_CONFIG_SHA}',] + [f'CONFIG_PART_{i}=${{_CONFIG_{i}}}' for i in range(8)]

def config(infra,proof,lane,seconds,token,source_payload=None):
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
SDK_PYTHON /workspace/package-evidence.py --evidence /workspace/evidence --out /workspace/out
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
try:
 s=json.loads((p/'summary.json').read_text())
 ok=pathlib.Path('/workspace/upload.ok').is_file() and ((s.get('verification_accepted') is True) or (s.get('smoke_success') is True) or (s.get('diagnostic_complete') is True))
 print('SMALLSORT_FINAL_VERDICT',json.dumps(s,sort_keys=True),'upload_complete=',pathlib.Path('/workspace/upload.ok').is_file(),'verification_accepted=',s.get('verification_accepted'),'diagnostic_complete=',s.get('diagnostic_complete'))
 sys.exit(0 if ok else 1)
except Exception as e:
 print('INCOMPLETE_EVIDENCE',type(e).__name__,str(e));sys.exit(2)
'''
 return {'steps':[{'id':'execute','name':UBUNTU,'entrypoint':'bash','args':['-ceu',body],'env':envs(infra,proof,lane)+source_env,'allowFailure':True},{'id':'package-upload','name':SDK,'entrypoint':'bash','args':['-ceu',upload],'env':envs(infra,proof,lane)+['PACKAGER_BYTES='+package],'allowFailure':True},{'id':'verdict','name':SDK,'entrypoint':SDK_PYTHON,'args':['-c',verdict]}],'timeout':f'{seconds}s','queueTtl':'60s','options':{'machineType':'E2_STANDARD_2','logging':'CLOUD_LOGGING_ONLY'},'serviceAccount':f'projects/smallsort-ci/serviceAccounts/{ACCOUNT}','tags':['smallsort-cloud-migration',token],'substitutions':{'_CONFIG_SHA':'placeholder',**{f'_CONFIG_{i}':'placeholder' for i in range(8)},**{f'_SOURCE_{i}':part for i,part in enumerate(source_parts)}}}

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
 """Observe another owner's reservation without editing its ledger or state."""
 record=coordination.active()
 if record is None:return
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
 if deadline.tzinfo is None or deadline>cutoff:raise SystemExit('Phase deadline exceeds authorized 08:00 UTC cutoff')
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
  if coordination.last_owner()==a.owner and coordination.pending_others(a.owner):raise SystemExit('Another owner has a pending turn; wait for its submit or withdrawal')
  for sha in [a.infra_sha,a.proof_sha]:
   if not re.fullmatch('[0-9a-f]{40}',sha):raise SystemExit('Full published SHA required')
   subprocess.run(['git','cat-file','-e',sha+'^{commit}'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for name in ['control.py','coordination.py','package-evidence.py','source-input.py']:
   expected=subprocess.check_output(['git','show',a.infra_sha+':research/challenge-8/cloud-build/'+name],cwd=ROOT)
   if expected!=(DIR/name).read_bytes():raise SystemExit('Uncommitted/local '+name+' differs from infrastructure SHA; publish first')
  ongoing=invoke(['builds','list','--region=global','--ongoing','--format=json'])
  if ongoing or ledger['active_build'] or coordination.active():raise SystemExit('Queued/active or unresolved build: monitor/reconcile first')
  # queue envelope is reserved too, respecting phase/per-build ceiling.
  if not 90<=a.timeout<=1740 or a.timeout+60>1800 or a.timeout+60>ledger['remaining_build_seconds']:raise SystemExit('Invalid timeout or insufficient phase budget (60s queue reserve included)')
  token='dispatch-'+uuid.uuid4().hex
  source_payload=None
  if a.source_mode=='pinned-objects':
   sys.dont_write_bytecode=True
   spec=importlib.util.spec_from_file_location('source_input',DIR/'source-input.py')
   module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
   source_payload=module.make_payload(ROOT,a.infra_sha,a.proof_sha,a.lane)
  cfg=config(a.infra_sha,a.proof_sha,a.lane,a.timeout,token,source_payload)
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
  active=coordination.active()
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
