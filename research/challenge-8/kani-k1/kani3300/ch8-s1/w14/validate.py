#!/usr/bin/env python3
"""Offline arithmetic/identity/coverage checks only. Never builds, verifies or dispatches."""
import collections,csv,hashlib,json,math,pathlib,re,subprocess
P=pathlib.Path(__file__).resolve().parent
BASE='872d5a43380752786415bc00d2a12ce0e930cb37'
def table(n):return list(csv.DictReader((P/n).open(),delimiter='\t'))
def check(x,message):
 if not x:raise ValueError(message)
def close(a,b):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=1e-6)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=table('published-timings.tsv');roots=table('baseline-roots.tsv');replace=table('replace-map.tsv');classes=table('coverage-classes.tsv')
names={r['harness'] for r in old}
for name,rows in [('published',old),('baseline',roots),('replace',replace)]:
 check(len(rows)==len({r['harness'] for r in rows})==235,f'{name}: unique235')
 check({r['harness'] for r in rows}==names,f'{name}: same inventory')
check(sum(r['panic_stub']=='yes' for r in old)==71,'panic stub count71')
check(sum(r['replacement_status']=='CONDITIONAL_CANDIDATE' for r in replace)==21,'candidates21')
check(all(r['replacement_approved']=='False' and r['ordinary_keep_now']=='True' for r in replace),'no removal approved')
check(all(not r['new_root'] and not r['new_source_sha'] and not r['new_contract_version'] for r in replace),'new identities absent')
check(all(not r['ubuntu_aggregate_rss_bytes'] and not r['macos_aggregate_rss_bytes'] and not r['ubuntu_root_wall_s'] and not r['macos_root_wall_s'] for r in roots),'unknown RSS/wall never zero')
for c in classes:
 rr=[r for r in replace if r['class']==c['class']]
 check(len(rr)==int(c['roots']),f'class {c["class"]}')
 check(sum(r['replacement_status']=='CONDITIONAL_CANDIDATE' for r in rr)==int(c['conditional_candidates']),'class candidate count')
 for os in ['ubuntu','macos']:check(close(sum(float(r[f'{os}_vt_s']) for r in rr),c[f'{os}_vt_s']),'class VT')
check(sum(int(c['roots']) for c in classes)==235 and sum(int(c['retain_without_primary_S_replacement']) for c in classes)==214,'class totals')
summary=json.loads((P/'api-summary.json').read_text());shards=json.loads((P/'baseline-shards.json').read_text())
check(summary['pr']['head']==summary['run']['head_sha']==BASE,'PR/run identity')
check(summary['run']['run_attempt']==1 and summary['run']['conclusion']=='success','run attempt1/success')
check(summary['total_count']==len(summary['jobs'])==16,'complete job metadata page')
check(all(j['conclusion']=='success' for j in summary['jobs']),'16/16 job metadata')
check(sum(s['job_elapsed_s'] for s in shards['shards'])==25116,'runner elapsed sum')
for os in ['ubuntu','macos']:
 a=set((P/f'shard-{os}-2-roots.txt').read_text().splitlines());b=set((P/f'shard-{os}-4-roots.txt').read_text().splitlines())
 check(len(a)==183 and len(b)==52 and not a&b and a|b==names,'shard partition235')
 for r in roots:check(int(r[f'{os}_partition'])==(4 if r['harness'] in b else 2),'root shard mapping')
 for i in [1,2,3,4]:
  s=next(s for s in shards['shards'] if s['os']==os and s['partition']==i)
  job=next(j for j in summary['jobs'] if j['id']==s['job_id'])
  check(job['conclusion']==s['conclusion']=='success','shard job identity')
  expected=(a if i==2 else b if i==4 else set())
  check(s['smallsort_roots']==len(expected),'per-shard SmallSort count')
  check(close(s['smallsort_autoharness_vt_projection_s'],sum(float(r[f'{os}_vt_s']) for r in old if r['harness'] in expected)),'VT projection')
 check(max((s for s in shards['shards'] if s['os']==os),key=lambda s:s['job_elapsed_s'])['partition']==4,'worst shard4')
 check(close(sum(float(r[f'{os}_vt_s']) for r in old),7801.879658047 if os=='ubuntu' else 10534.459671914),'total VT')
 check(all(r[f'{os}_status']=='SUCCESSFUL' for r in old),'source-reported statuses')
# source anchors are checked at pinned old SHA; no parsing/compiler execution.
source_cache={}
for r in replace:
 path,line=r['source'].rsplit(':',1)
 if path not in source_cache:
  source_cache[path]=subprocess.check_output(['git','show',f'{BASE}:{path}']).decode().splitlines()
 check(re.search(r'\b'+re.escape(r['harness'].split('::')[-1])+r'\b',source_cache[path][int(line)-1]) is not None,'exact source anchor')
# HTTP206 projections carry explicit ranges; verify membership from selected-list sections.
samples={f.name:json.loads(f.read_text()) for f in (P/'samples').glob('*.json')}
def selected(name):
 lines=samples[name]['selected_lines'];idx=lines.index('Running verification for harnesses:')
 return {s.split('verify::')[1] for s in lines[idx+1:] if s.startswith('slice::sort::shared::smallsort::verify::')}
check(selected('128376214074-460000-525535.json')|{s.split('verify::')[1] for s in samples['128376214074-525000-540999.json']['selected_lines'] if s.startswith('slice::sort::shared::smallsort::verify::')}==set((P/'shard-ubuntu-2-roots.txt').read_text().splitlines()),'ubuntu2 selection')
check(selected('128376214045-490000-555535.json')==set((P/'shard-macos-2-roots.txt').read_text().splitlines()),'macos2 selection')
check(selected('128376213966-500000-565535.json')==set((P/'shard-macos-4-roots.txt').read_text().splitlines()),'macos4 selection')
u4={s.split('verify::')[1] for s in samples['128376214108-500000-565535.json']['selected_lines'] if s.startswith('slice::sort::shared::smallsort::verify::')}
check(u4==set((P/'shard-ubuntu-4-roots.txt').read_text().splitlines()),'ubuntu4 selection')
for d in samples.values():
 lo,hi,total=d['content_range'];check(0<=lo<=hi<total and d['bytes']==hi-lo+1<=65536,'sample bounds')
 check(len(d['range_sha256'])==64,'sample digest')
template=json.loads((P/'cost-report.template.json').read_text())
check(template['status']=='NOT_RUN' and all(s=='UNKNOWN' for s in template['gates'].values()),'no future gate credit')
check(template['baseline']['roots']==template['new']['roots']==[],'empty roots are template only')
check(template['dispatch']['credit_consumed']==0,'zero dispatch')
for filename in ['README.md','COVERAGE.md','COST-REPORT-FORMAT.md']:
 for target in re.findall(r'\]\(([^)]+)\)',(P/filename).read_text()):
  if not re.match(r'https?://',target):check((P/target).exists(),f'local link {target}')
report={'status':'PASS','scope':'offline research consistency only; not compiler/proof/R8 acceptance','unique_old_roots':235,'standard_roots':183,'contract_roots':52,'classes':10,'conditional_candidates':21,'retain_without_primary_S_replacement':214,'currently_retained':235,'dispatches':0,'local_builds':0,'historical_rss':'UNKNOWN','R8':'UNKNOWN','input_sha256':{str(f.relative_to(P)):sha(f) for f in sorted(P.rglob('*')) if f.is_file() and f.name not in ('VALIDATION.json','CHECKPOINT.json') and '__pycache__' not in str(f)}}
(P/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='input_sha256'},indent=2))
