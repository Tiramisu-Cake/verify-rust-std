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
 assert len(raw)==481904 and sha(raw)=='885fa419e00f4ad83d427d2d03c8c38fd51291dea0f9d04ee5c6e71030e904c0'
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
 # Inventory retained in artifact-integrity.json; no verbose dump.
 for name,item in doc['files'].items():
  p=Path(name)
  assert not p.is_absolute() and '..' not in p.parts and '\\' not in name and name.endswith('.json')
  assert name.endswith('.json')
  b=item['text'].encode() if item.get('encoding','utf-8')=='utf-8' else base64.b64decode(item['text'],validate=True)
  assert len(b)==item['bytes'] and sha(b)==item['sha256']
  decoded[name]=json.loads(b)
 transport.update(uncompressed_bytes=len(unpacked),uncompressed_sha256=sha(unpacked),members={k:{x:v[x] for x in ('bytes','sha256','encoding') if x in v} for k,v in doc['files'].items()})
 (HERE/'group-evidence.json.gz').write_bytes(gz)
 write('artifact-integrity.json',transport)
 write('compact-metadata.json',{k:v for k,v in doc.items() if k!='files'})
 # Structured projections only; no native raw/full log or transport archive.
 write('member-catalogue.json',{k: {'keys':list(v) if isinstance(v,dict) else None} for k,v in decoded.items()})
 print(json.dumps({'integrity':'PASS','structured_members':len(decoded),'payload_bytes':len(gz),'metadata_keys':list(doc)}))
if __name__=='__main__': main(sys.argv[1])
