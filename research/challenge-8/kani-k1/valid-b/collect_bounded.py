"""Export only authorized bounded K-1 summary/inventory/peaks views for a finished VALID-B build."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
TOOL = ROOT/'research/challenge-8/kani-k1/tools/k1g.sh'

def capture(label, args):
    run = subprocess.run([str(TOOL), *map(str,args)], cwd=ROOT, text=True, capture_output=True,
                         timeout=300)
    path = BASE/'evidence'/label
    path.parent.mkdir(exist_ok=True)
    path.write_text(run.stdout)
    if run.stderr:
        path.with_suffix(path.suffix+'.stderr').write_text(run.stderr)
    if run.returncode:
        raise RuntimeError(f'{args[0]} failed {run.returncode}; see {path}')
    return run.stdout

def fields(text):
    return {k:v for line in text.splitlines() if '=' in line and '\t' not in line
            for k,v in [line.split('=',1)] if re.fullmatch('[a-z_0-9]+',k)}

def collect(label, processes):
    session = json.loads((BASE/'session.json').read_text())
    entry = next(e for e in session['builds'] if e['label']==label)
    build, sha = entry['build_id'], entry['sha']
    request_bytes = subprocess.check_output(['git','show',sha+':research/challenge-8/kani-k1/RUN-REQUEST.json'],cwd=ROOT)
    request = json.loads(request_bytes)
    expected = dict(build_id=build,head_sha=sha,request_id=request['request_id'],
                    request_sha256=hashlib.sha256(request_bytes).hexdigest())
    status=json.loads(capture(label+'.status.json',['status',build]))
    if status['id']!=build or status['source_sha']!=sha:raise ValueError('build metadata identity mismatch')
    if status['status'] not in ('SUCCESS','FAILURE','INTERNAL_ERROR','TIMEOUT','CANCELLED','EXPIRED'):raise ValueError('build not terminal')
    md = capture(label+'.summary.md',['summary',build])
    if sha not in md: raise ValueError('summary source identity missing')
    inventory = request.get('inventory',False) and not entry.get('setup_failed')
    for verb,suffix in [('summary','rows.tsv')]+([('inventory','inventory.page')] if inventory else []):
        offset = 0
        while True:
            output = capture(f'{label}.{offset:04d}.{suffix}',[verb,build,offset,80])
            meta = fields(output)
            for key,value in expected.items():
                if meta.get(key)!=value: raise ValueError(f'{verb}: {key} identity mismatch')
            if int(meta['offset'])!=offset: raise ValueError('page offset mismatch')
            following = meta['next_offset']
            if following=='done': break
            new_offset = int(following)
            if new_offset!=offset+int(meta['count']) or new_offset<=offset:
                raise ValueError('page continuation mismatch')
            offset = new_offset
    if request['kind'] != 'inventory' and not entry.get('setup_failed'):capture(label+'.peaks.txt',['peaks',build])
    if processes:
        offset=0
        while True:
            output=capture(f'{label}.process-{offset:04d}.txt',['peaks',build,offset,8])
            match=re.search(r'^process_records=(\d+) offset=(\d+) count=(\d+) next_offset=(\S+)$',output,re.M)
            if not match: raise ValueError('no process page metadata')
            total,here,count,following=match.groups()
            if int(here)!=offset:raise ValueError('process page offset mismatch')
            if following=='done':break
            if int(following)!=offset+int(count) or int(following)<=offset:raise ValueError('process continuation mismatch')
            offset=int(following)
    capture(label+'.tooling.txt',['check-tooling',build,entry['sha']])
    print(label,build,'bounded exports complete',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('--process-pages',action='store_true')
    a=p.parse_args();collect(a.label,a.process_pages)
