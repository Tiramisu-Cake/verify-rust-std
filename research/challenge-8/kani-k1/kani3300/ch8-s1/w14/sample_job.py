#!/usr/bin/env python3
"""One explicit, bounded GitHub log range; retain projections, never raw logs."""
import argparse, hashlib, json, pathlib, re, subprocess
p=argparse.ArgumentParser()
p.add_argument('job',type=int)
p.add_argument('start',type=int)
p.add_argument('--size',type=int,default=16384)
a=p.parse_args()
assert a.start>=0 and 0<a.size<=65536
end=a.start+a.size-1
endpoint=f'repos/Tiramisu-Cake/verify-rust-std/actions/jobs/{a.job}/logs'
proc=subprocess.Popen(['gh','api','--include','-H',f'Range: bytes={a.start}-{end}',endpoint],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:
 headers=[]
 for _ in range(100):
  line=proc.stdout.readline(4096)
  headers.append(line)
  if not line.strip(): break
  if sum(map(len,headers))>16384: raise ValueError('header cap')
 h=b''.join(headers).decode(errors='replace')
 cr=re.search(r'(?im)^Content-Range: bytes (\d+)-(\d+)/(\d+)',h)
 if not headers[0].startswith(b'HTTP/1.1 206') or not cr: raise ValueError('refused body: no 206/Content-Range')
 lo,hi,total=map(int,cr.groups())
 if lo!=a.start or hi>end or hi-lo+1>a.size: raise ValueError('wrong range')
 # Bound cumulative coverage as well as each response; no automatic log traversal.
 prior=[]
 for saved in (pathlib.Path(__file__).parent/'samples').glob(f'{a.job}-*.json'):
  old=json.loads(saved.read_text())
  prior.append(old['content_range'][:2])
 merged=[]
 for x,y in sorted(prior+[[lo,hi]]):
  if merged and x<=merged[-1][1]+1: merged[-1][1]=max(y,merged[-1][1])
  else: merged.append([x,y])
 if sum(y-x+1 for x,y in merged)>min(262144,total//4): raise ValueError('cumulative sample cap; body refused')
 data=proc.stdout.read(a.size+1)
 if len(data)!=hi-lo+1: raise ValueError('wrong body size')
 text=data.decode('utf-8',errors='replace')
 # Drop the first/last partial line. Complete line coordinates stay within requested range.
 lines=text.split('\n')[1:-1]
 lines=[re.sub(r'^\ufeff?\d{4}-\d\d-\d\dT[^ ]+ ','',x).rstrip('\r') for x in lines]
 relevant=[x for x in lines if ('smallsort::verify::' in x or re.search(r'All harnesses:|Total number of harnesses:|Number of harnesses this worker|Start index into|Running verification for harnesses:|Running as parallel worker|KANI_JOBS:|WORKER_(INDEX|TOTAL):|Memory:|Processor|Model Name:|Chip:|Physical Memory:|macOS|Ubuntu|ARM64|X64|Image:|Version:|[Ii]ncluded [Ss]oftware:|timeout|Timeout|Maximum resident|Verification Time|VERIFICATION:-',x))]
 record={'job_id':a.job,'endpoint':endpoint,'requested':[a.start,end],'content_range':[lo,hi,total],'bytes':len(data),'range_sha256':hashlib.sha256(data).hexdigest(),'first_complete_line':lines[0] if lines else None,'last_complete_line':lines[-1] if lines else None,'selected_lines':relevant}
 out=pathlib.Path(__file__).parent/'samples';out.mkdir(exist_ok=True)
 target=out/f'{a.job}-{lo}-{hi}.json'
 target.write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({k:v for k,v in record.items() if k!='selected_lines'}))
 print('selected lines:',len(relevant));print('\n'.join(relevant[:4]));print('\n'.join(relevant[-4:]))
finally:
 if proc.poll() is None: proc.kill()
 proc.communicate()
