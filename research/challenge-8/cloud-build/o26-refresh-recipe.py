#!/usr/bin/env python3
"""Cloud-only fresh O26 source/certificate checks; frozen twenty are separate."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path('research/challenge-8')
SOURCE = '1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
ORIGINAL = '466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
UNIT = '10cf6e4d2a462082d456135078a77ea6670358f1ad15e0d81901104e8a102b43'
BODIES = (
 '8d95311e339f94caed26d93fd339e279e8b1df9a3b783f202e99359e60d101cc',
 '92bd8aea548575b4b5cd8bdb826f807937c219a6872bec2ade2bce3bf25fc562',
 '273813f669fe0e34b486287539580e3cb487185f0be3691a1151ebf227685182',
 'f21b9915065deb75ded03903fc1b2781b3a19ebbe1561d2a9ca692b31931f951',
 'ac51fb48e423d64c3f8a96054c166b959303617f4affbd6665e10fe75cf6d4ed',
 '1c8531225e562d2d6492e79e049101f5884c580762733080686737d1c3cd07f6',
 'e8dd503c0bf832081e71dcc9d115c2a07e9349ff746ec7e7cce132edf63f4137',
 '9577c64905c4a45eecc4aab506f6276fea076f8a7a18d2f7ca0304cf70205b86',
 'e0508d6cfb436bc1bcd04737ad74e37b357d17e9ec3c2a226ee961f7036eae9a',
)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def o26(cloud_dir: Path):
    path = cloud_dir / 'o26-recipe.py'
    spec = importlib.util.spec_from_file_location('o26_recipe_existing', path)
    if spec is None or spec.loader is None: raise ValueError('O26 recipe unavailable')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

def write(out: Path, data: dict):
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')

def preflight(repo: Path, ev: Path, cloud_dir: Path):
    cap = o26(cloud_dir).load_capture(repo, 'refresh_preflight')
    cap.clear_semantic_opt_ins()
    dest = ev / 'preflight' / 'candidate'
    dest.parent.mkdir(parents=True, exist_ok=False)
    source = cap.PREP.write_case(repo, dest)
    case = dest / cap.PREP.CASE_NAME
    actual = {k: digest(case / f'{k}/lib.rs') for k in ('original','verified')}
    if (source['verified_sha256'] != SOURCE or source['original_sha256'] != ORIGINAL or
        actual != {'verified':SOURCE,'original':ORIGINAL} or
        source['ghost_strip_identity'] is not True or len(source['source_order']) != 9):
        raise ValueError('fresh Cloud preflight source pair differs')
    write(ev / 'source-preflight.json', {'classification':'O26_REFRESH_SOURCE_ONLY_PREFLIGHT',
       'source':source, 'source_generation_complete':True,
       'compiler_or_verifier_invoked':False,
       'files':{k:str((case / f'{k}/lib.rs').relative_to(ev)) for k in actual}})

def compare(ev: Path):
    prior = json.loads((ev/'source-preflight.json').read_text())
    case = ev/'cases/candidate/capture/nine-body-a1-owned-forget'
    summary = json.loads((ev/'cases/candidate/capture/summary.json').read_text())
    source = summary['source']; snaps = summary['fingerprint']['snapshots']
    expected = {'unit':UNIT, **{f'body-{i}':h for i,h in enumerate(BODIES)}}
    assert set(snaps) == set(expected)
    snapshots_match = all(snaps[k]['sha256']==v and digest(case/snaps[k]['file'])==v
                          and (case/snaps[k]['file']).stat().st_size==snaps[k]['bytes']
                          for k,v in expected.items())
    pair_match = (source['verified_sha256']==SOURCE and source['original_sha256']==ORIGINAL
      and source['source_order']==prior['source']['source_order']
      and source['ghost_strip_identity'] is True
      and all((case/f'{k}/lib.rs').read_bytes()==(ev/prior['files'][k]).read_bytes()
              for k in ('original','verified')))
    full = summary['full_body_capture']
    modes_match = all(len(full[m]['bodies'])==9 and
       digest(case/full[m]['whole_decoded_mir_file'])==full[m]['whole_decoded_mir_sha256'] and
       all(b['index']==i and digest(case/b['file'])==b['sha256'] for i,b in enumerate(full[m]['bodies']))
       for m in ('normal','readonly'))
    complete = (snapshots_match and pair_match and modes_match and
       summary['frontend_refinement_and_full_body_capture'] is True and
       summary['fingerprint']['classification']=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE')
    record={'fresh_certificate_snapshots_match':snapshots_match,'source_pair_match':pair_match,
       'full_normal_readonly_mir_match':modes_match,'capture_complete':complete,
       'verified_sha256':SOURCE,'original_sha256':ORIGINAL,'unit_sha256':UNIT,
       'body_sha256':list(BODIES)}
    write(ev/'cases/candidate/capture-compare.json',record)
    if not complete: raise ValueError('fresh Cloud capture differs from pinned evidence')

def proof(repo: Path, ev: Path, cloud_dir: Path, tool_home: Path, schema: Path,
          sysroot: Path, deadline: int):
    mod=o26(cloud_dir)
    case=ev/'cases/candidate/capture/nine-body-a1-owned-forget'
    result=mod.proof_stage(repo,case,tool_home,schema,sysroot,deadline,
                           'refreshed-proof','refresh')
    write(ev/'cases/candidate/proof-stage.json', {'proof_sha':mod.git_sha(repo),
          'stage':result,'actual_verification_accepted':False})
    log=case/'refreshed-proof.log'
    if log.is_file():
        print(log.read_text(errors='replace'),flush=True)
    print(json.dumps({'proof_exit':result.get('exit'),
                      'source_unchanged':result.get('source_unchanged')}),flush=True)

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='mode',required=True)
    a=sub.add_parser('overlay')
    for n in ('repo','cloud-dir','evidence'): a.add_argument('--'+n,type=Path,required=True)
    a=sub.add_parser('preflight')
    for n in ('repo','cloud-dir','evidence'): a.add_argument('--'+n,type=Path,required=True)
    a=sub.add_parser('compare');a.add_argument('--evidence',type=Path,required=True)
    a=sub.add_parser('proof')
    for n in ('repo','cloud-dir','evidence','tool-home','schema','compiler-sysroot'):
        a.add_argument('--'+n,type=Path,required=True)
    a.add_argument('--deadline-epoch',type=int,required=True)
    x=p.parse_args()
    if x.mode=='overlay':
        mod=o26(x.cloud_dir)
        mod.overlay(x.repo,x.cloud_dir/'provider.py',x.evidence/'candidate-provider-overlay.json')
    elif x.mode=='preflight': preflight(x.repo,x.evidence,x.cloud_dir)
    elif x.mode=='compare': compare(x.evidence)
    else: proof(x.repo,x.evidence,x.cloud_dir,x.tool_home,x.schema,x.compiler_sysroot,x.deadline_epoch)
if __name__=='__main__':main()
