import pathlib,sys,json,hashlib,subprocess
repo,inp,dest=map(pathlib.Path,sys.argv[1:]);m=json.loads((inp/'manifest').read_text())
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args]).decode().strip()
assert git('rev-parse','HEAD')==m['base']
assert hashlib.sha256((inp/'bundle').read_bytes()).hexdigest()==m['bundle_sha256']
assert git('bundle','list-heads',str(inp/'bundle'))==m['head']+' '+m['ref']
subprocess.run(['git','-C',str(repo),'bundle','verify',str(inp/'bundle')],check=True)
subprocess.run(['git','-C',str(repo),'fetch',str(inp/'bundle'),m['ref']],check=True)
assert git('rev-parse',m['head']+'^{tree}')==m['tree']
assert set(git('diff','--name-only',m['base'],m['head']).splitlines())==set(m['files'])
subprocess.run(['git','-C',str(repo),'worktree','add','--detach',str(dest),m['head']],check=True,stdout=sys.stderr)
for p,v in m['files'].items():
 assert hashlib.sha256((dest/p).read_bytes()).hexdigest()==v['sha256']
 assert git('rev-parse',m['head']+':'+p)==v['git_blob']
print(json.dumps(m,indent=2))
