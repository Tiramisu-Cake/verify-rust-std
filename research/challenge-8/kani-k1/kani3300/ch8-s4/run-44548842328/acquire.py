#!/usr/bin/env python3
"""One authorized compact acquisition, metadata/digest first; no archive retained.

Same bounded in-memory adapter as run-44505531344. Never call on replay.
"""
import base64, gzip, hashlib, io, json, subprocess, zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def write(n, v): (HERE/n).write_text(json.dumps(v, indent=2)+'\n')
def main():
    assert not (HERE/'group-evidence.json.gz').exists(), 'do not reacquire'
    meta=json.loads((HERE/'CONNECTED-METADATA.json').read_text())
    a,=meta['artifacts']['artifacts']
    assert a['id']==14542371938 and a['name']=='ch8-s3-2-44548842328-1'
    assert a['size_in_bytes']==448143 and a['digest']=='sha256:5faedd4231f8aae73aa47f6020665de24e153944d0f2436893e631c70bca913b'
    p=subprocess.Popen(['gh','api','repos/Tiramisu-Cake/kani/actions/artifacts/14542371938/zip'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    raw=p.stdout.read(8*1024*1024+1)
    if len(raw)>8*1024*1024: p.kill(); raise ValueError('transport bound exceeded')
    err=p.stderr.read(); assert p.wait(timeout=45)==0, err.decode()
    assert len(raw)==a['size_in_bytes'] and 'sha256:'+sha(raw)==a['digest']
    out={'metadata_first':True,'bytes':len(raw),'sha256':sha(raw),'digest_checked_before_zip_open':True,'transport_saved':False,'compact_acquisitions':1,'raw_full_GCS':False}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.namelist()==['group-evidence.json.gz']
        info=z.getinfo('group-evidence.json.gz')
        assert info.file_size<=8*1024*1024 and not info.flag_bits&1
        gz=z.read(info)
    with gzip.GzipFile(fileobj=io.BytesIO(gz)) as f: unpacked=f.read(32*1024*1024+1)
    assert len(unpacked)<=32*1024*1024
    doc=json.loads(unpacked)
    assert doc['schema']=='ch8-s1-05-artifact-v1' and doc['state']=='PACKAGED' and doc['error'] is None
    catalogue={}
    for n,e in doc['files'].items():
        path=Path(n)
        assert not path.is_absolute() and '..' not in path.parts and '\\' not in n and path.suffix=='.json'
        b=e['text'].encode() if e.get('encoding','utf-8')=='utf-8' else base64.b64decode(e['text'],validate=True)
        assert len(b)==e['bytes'] and sha(b)==e['sha256']
        v=json.loads(b)
        catalogue[n]={'bytes':len(b),'sha256':sha(b),'keys':list(v) if isinstance(v,dict) else None}
    out.update(payload_bytes=len(gz),payload_sha256=sha(gz),uncompressed_bytes=len(unpacked),uncompressed_sha256=sha(unpacked),members=catalogue)
    (HERE/'group-evidence.json.gz').write_bytes(gz)
    write('artifact-integrity.json',out)
    write('compact-metadata.json',{k:v for k,v in doc.items() if k!='files'})
    print(json.dumps({k:v for k,v in out.items() if k!='members'}))
    print(json.dumps({'structured_members':len(catalogue),'member_names':list(catalogue)}))
if __name__=='__main__': main()
