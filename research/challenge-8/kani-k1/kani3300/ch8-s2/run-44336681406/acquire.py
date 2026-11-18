#!/usr/bin/env python3
"""Read only the authorized compact artifact; no transport ZIP is saved."""
import sys,io,json,hashlib,zipfile,gzip,urllib.request,base64
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def write(n,v): (HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main(url):
 with urllib.request.urlopen(url,timeout=45) as f: raw=f.read(8*1024*1024+1)
 assert len(raw)==31442 and sha(raw)=='10cdd2d22173d8a15c6d05a1c89e4a323eb5633c3f82bb8d410e8a8135e67f9c'
 transport={'bytes':len(raw),'sha256':sha(raw),'digest_checked_before_zip_open':True,'transport_saved':False}
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  assert z.namelist()==['group-evidence.json.gz']
  info=z.getinfo('group-evidence.json.gz')
  assert info.file_size<=8*1024*1024 and not info.flag_bits&1
  gz=z.read(info)
 transport.update(payload_bytes=len(gz),payload_sha256=sha(gz))
 with gzip.GzipFile(fileobj=io.BytesIO(gz)) as f: unpacked=f.read(32*1024*1024+1)
 assert len(unpacked)<=32*1024*1024
 doc=json.loads(unpacked)
 assert doc['schema']=='ch8-s1-05-artifact-v1'
 decoded={}
 print(json.dumps({'namespace_inventory':list(doc['files'])}))
 for name,item in doc['files'].items():
  p=Path(name)
  assert not p.is_absolute() and '..' not in p.parts and '\\' not in name and name.endswith('.json')
  row_ids={'swap_pfc','summary_witness','merge32_real','sort13_assumed','general32_assumed','merge_order_corrupt','merge_count_corrupt','checker_count_corrupt','checker_order_corrupt','sort13_weak','general32_weak'}
  if not (name in {'receipt.json','job-status.json'} or name.startswith(('groups/s2-batch3probes-u34/','setup/')) or p.parts[0] in row_ids):
   raise ValueError('unexpected structured namespace: '+name)
  b=item['text'].encode() if item.get('encoding','utf-8')=='utf-8' else base64.b64decode(item['text'],validate=True)
  assert len(b)==item['bytes'] and sha(b)==item['sha256']
  decoded[name]=json.loads(b)
 transport.update(uncompressed_bytes=len(unpacked),uncompressed_sha256=sha(unpacked),members={k:{x:v[x] for x in ('bytes','sha256','encoding') if x in v} for k,v in doc['files'].items()})
 (HERE/'group-evidence.json.gz').write_bytes(gz)
 write('artifact-integrity.json',transport)
 write('compact-metadata.json',{k:v for k,v in doc.items() if k!='files'})
 # Structured projections only; no native raw/full log or transport archive.
 write('embedded-projection.json',decoded)
 print(json.dumps({'integrity':'PASS','members':{k:list(v) if isinstance(v,dict) else type(v).__name__ for k,v in decoded.items()},'metadata':{k:v for k,v in doc.items() if k!='files'}}))
if __name__=='__main__': main(sys.argv[1])
