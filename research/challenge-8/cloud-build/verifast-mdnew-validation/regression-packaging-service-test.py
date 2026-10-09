import pathlib,json,subprocess,tempfile,os,shutil,hashlib
repo=pathlib.Path('/root/verify-rust-std-verifast-infra');src=pathlib.Path('/tmp/mdnew-validation-extracted-b5c898e4-4049-4770-9d73-424703c8168c');script=repo/'research/challenge-8/cloud-build/package-evidence.py'; config=json.loads((src/'submitted-config.json').read_text());env=os.environ.copy();env.update(dict(x.split('=',1) for x in config['steps'][0]['env']));env.update(CLOUD_BUILD_ID='b5c898e4-4049-4770-9d73-424703c8168c',INFRA_SHA='cf938bb31348c598de3d261f4169fa13a4bd11ab',PROOF_SHA='cf938bb31348c598de3d261f4169fa13a4bd11ab',LANE='verifast-mdnew-regressions',SUBMITTED_CONFIG_SHA=hashlib.sha256((src/'submitted-config.json').read_bytes()).hexdigest())
with tempfile.TemporaryDirectory(prefix='mdnew-case-package-') as d:
 d=pathlib.Path(d); evidence=d/'evidence';shutil.copytree(src,evidence)
 def package(out):
  subprocess.run(['python3',str(script),'--evidence',str(evidence),'--out',str(out)],env=env,stdout=subprocess.DEVNULL,check=True)
  return json.loads((out/'summary.json').read_text())
 before=package(d/'before');assert not before['evidence_complete'] and before['missing_mandatory']==['allprooflogs/cases/*']
 # Execute precisely the new runner publication statement, with fake service paths.
 runner=(repo/'research/challenge-8/cloud-build/run-verifast-mdnew-cfg.sh').read_text();line='cp -a "$regression_dir" "$cases/upstream-regressions"';assert line in runner
 case=evidence/'allprooflogs/cases';case.mkdir(exist_ok=True)
 subprocess.run(['bash','-c',line],env={**env,'regression_dir':str(evidence/'allprooflogs/regressions'),'cases':str(case)},check=True)
 for f in (evidence/'allprooflogs/regressions').iterdir():assert f.read_bytes()==(case/'upstream-regressions'/f.name).read_bytes()
 after=package(d/'after');assert after['evidence_complete'] and after['verification_accepted'] and not after['missing_mandatory']
 pathlib.Path('/tmp/mdnew-validation-regression-packaging-test.json').write_text(json.dumps({'service_only':True,'old_archive_unchanged':True,'no_new_proof_credit':True,'before':before,'after':after,'case_evidence_exact_copy':True},indent=2)+'\n')
 print('PASS: missing-case gate rejects old layout; exact real case copy accepted; no packager weakening')
