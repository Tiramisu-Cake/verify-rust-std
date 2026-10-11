import pathlib,sys,json,re
root=pathlib.Path(sys.argv[1]);rc=int(sys.argv[2]);stage=sys.argv[3]
def read(n):
 p=root/n;return p.read_text(errors='replace') if p.is_file() else ''
def success(n):return read(n+'-exit-code.txt').strip()=='0' and '0 errors found' in read(n+'.stdout.log')
checks={'positive':success('positive'),'marked_negative':success('negative-marked'),'baseline_missing_binding':read('baseline-missing-binding-exit-code.txt').strip()=='1' and 'as_mut_ptr' in (read('baseline-missing-binding.stdout.log')+read('baseline-missing-binding.stderr.log')),'negative_diagnostic':read('negative-diagnostic-exit-code.txt').strip()=='1' and bool(re.search(r'slice_as_mut_ptr_no_init.rs\(\d+',read('negative-diagnostic.stdout.log')+read('negative-diagnostic.stderr.log'))),'make_test':read('make-test-exit-code.txt').strip()=='0'}
print(json.dumps({'schema':'slice-upstream-audit-v1','accepted':rc==0 and all(checks.values()),'runner_status':rc,'stage':stage,'checks':checks,'note':'Raw missing-binding and negative location/VC independently reviewed; no research profiles tested.'},indent=2))
